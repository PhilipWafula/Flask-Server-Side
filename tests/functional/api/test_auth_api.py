import pytest
import pyotp
from tests.helpers.factories import UserFactory
from app.server.models.user import SignupMethod
from app.server.utils.messaging import send_one_time_pin

client_user = {
    "given_names": "Jon Snow",
    "surname": "Stark",
    "phone": "0711223344",
    "password": "password-123",
    "id_type": "NATIONAL_ID",
    "id_value": "12345678",
    "signup_method": "MOBILE",
    "role": "CLIENT",
}

admin_user = {
    "given_names": "John Doe",
    "surname": "Jane",
    "email": "admin-1@localhost.com",
    "password": "password-123",
    "signup_method": "WEB",
    "role": "ADMIN",
}


@pytest.mark.parametrize(
    "user_json, status_code", [(admin_user, 201), (client_user, 201)]
)
def test_register_api(
    test_client,
    initialize_database,
    create_master_organization,
    seed_system_data,
    user_json,
    status_code,
):
    """
    GIVEN a flask application
    WHEN a POST request is sent to the '/api/v1/auth/register/' with valid user data
    THEN check status code value
    """
    # add public identifier to json
    user_json["public_identifier"] = create_master_organization.public_identifier
    response = test_client.post(
        "/api/v1/auth/register/",
        headers={"Accept": "application/json"},
        json=user_json,
        content_type="application/json",
    )
    assert response.status_code == status_code


@pytest.mark.parametrize("activation_token", ["alsdfjkadsljflk", None])
def test_invalid_user_activation(test_client, create_admin_user, activation_token):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/auth/activate_user/' with an invalid activation_token is incorrect or None
    THEN check the response is invalid
    """
    assert not create_admin_user.is_activated
    response = test_client.post(
        "/api/v1/auth/activate_user/",
        headers={"Accept": "application/json"},
        json={"activation_token": activation_token},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert not create_admin_user.is_activated


def test_valid_user_activation(test_client, create_admin_user):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/auth/activate_user/' with the correct activation_token is provided
    THEN check the response is valid
    """
    assert not create_admin_user.is_activated
    activation_token = create_admin_user.encode_single_use_jws("user_activation")
    response = test_client.post(
        "/api/v1/auth/activate_user/",
        headers={"Accept": "application/json"},
        json={"activation_token": activation_token},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert create_admin_user.is_activated


otp_json_with_missing_value = {"phone": "+254712345678", "otp": "654871"}
malformed_otp_json = {
    "phone": "+254712345678",
    "otp": 654871,
    "otp_expiry_interval": 3600,
}


@pytest.mark.parametrize(
    "otp_json, status_code",
    [(otp_json_with_missing_value, 400), (malformed_otp_json, 400)],
)
def test_invalid_verify_otp(test_client, create_client_user, otp_json, status_code):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/v1/auth/verify_otp/' with an invalid json
    THEN check that that the response is invalid.
    """
    assert not create_client_user.is_activated
    response = test_client.post(
        "/api/v1/auth/verify_otp/",
        headers={"Accept": "application/json"},
        json=otp_json,
        content_type="application/json",
    )
    assert response.status_code == status_code


def test_valid_verify_otp(test_client, create_client_user):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/v1/auth/verify_otp/' with a valid OTP json
    THEN check that that the response is valid.
    """
    assert not create_client_user.is_activated
    otp = create_client_user.set_otp_secret()
    response = test_client.post(
        "/api/v1/auth/verify_otp/",
        headers={"Accept": "application/json"},
        json={"phone": "+254712345678", "otp": otp, "otp_expiry_interval": 3600},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert create_client_user.is_activated
    if response.status_code == 200:
        assert isinstance(response.json["authentication_token"], str)


def test_resend_otp(
    test_client, initialize_database, seed_system_data, mock_sms_client
):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/v1/auth/resend_otp/'
    THEN send back current OTP.
    """
    user = UserFactory(
        given_names="Arya Faceless",
        surname="Stark",
        phone="+254787654123",
        signup_method=SignupMethod.MOBILE_SIGNUP,
        role_id=2,
    )
    user.set_identification_details(id_type="NATIONAL_ID", id_value="88776655")
    user.hash_password("password-123")
    assert not user.is_activated
    send_one_time_pin(user=user)
    messages = mock_sms_client
    response = test_client.post(
        "/api/v1/auth/resend_otp/",
        headers={"Accept": "application/json"},
        json={"phone": "+254787654123"},
        content_type="application/json",
    )
    assert response.status_code == 200
    otp_secret = user.get_otp_secret()
    otp = pyotp.TOTP(otp_secret, interval=3600).now()
    assert len(messages) == 1
    assert messages == [
        {
            "phone": f"{user.phone}",
            "message": f"Hello {user.given_names}, your activation code is: {otp}",
        }
    ]


def test_login(test_client, activated_admin_user, activated_client_user):
    """
    GIVEN a flask application
    WHEN an activated user sends a POST request to '/api/v1/auth/login/'
    THEN status code is 200.
    """
    response = test_client.post(
        "/api/v1/auth/login/",
        headers={"Accept": "application/json"},
        json={"email": activated_admin_user.email, "password": "password-123"},
        content_type="application/json",
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert isinstance(response.json["authentication_token"], str)

    response = test_client.post(
        "/api/v1/auth/login/",
        headers={"Accept": "application/json"},
        json={"phone": activated_client_user.phone, "password": "password-123"},
        content_type="application/json",
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert isinstance(response.json["authentication_token"], str)


def test_logout(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/v1/auth/logout/' with a valid authentication token and valid logout action.
    THEN check response is 200 and auth_token is added to blacklist
    """
    from app.server.models.blacklisted_token import BlacklistedToken

    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.post(
        "/api/v1/auth/logout/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        json={"action": "logout"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert BlacklistedToken.check_if_blacklisted(authentication_token) is True


def test_request_password_reset_email(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a POST request is sent to '/api/v1/auth/request_password_reset_email/' for an activated user.
    THEN check that password reset token is not None.
    """
    response = test_client.post(
        "/api/v1/auth/request_password_reset_email/",
        headers={"Accept": "application/json"},
        json={"email": activated_admin_user.email},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert len(activated_admin_user.password_reset_tokens) == 1


def test_password_reset(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a post request with a valid password reset token and new password is sent to '/api/v1/auth/reset_password/'.
    THEN check that new password is set and valid.
    """
    password_reset_token = activated_admin_user.encode_single_use_jws(
        token_type="reset_password"
    )
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.post(
        "/api/v1/auth/reset_password/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        json={
            "new_password": "new-password-123",
            "password_reset_token": password_reset_token,
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    assert activated_admin_user.verify_password("new-password-123")
