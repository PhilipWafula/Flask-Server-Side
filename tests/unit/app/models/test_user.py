def test_new_admin_user(test_client, initialize_database, create_admin_user):
    """
    GIVEN a user model
    WHEN a new admin user is created
    THEN check that the admin has an email, has a hashed password, role is set to admin and the admin is not activated
    """
    new_admin_user = create_admin_user
    assert new_admin_user.email == "admin@localhost.com"
    assert new_admin_user.password_hash is not None
    assert new_admin_user.password_hash != "password-123"
    assert new_admin_user.role.name == "ADMIN"
    assert not new_admin_user.is_activated


def test_new_client_user(test_client, initialize_database, create_client_user):
    """
    GIVEN a user model
    When a new client user is created
    THEN check that the client has a phone, hashed password, role set to client and the client is not activated
    """
    new_client_user = create_client_user
    assert new_client_user.phone == "+254712345678"
    assert new_client_user.password_hash is not None
    assert new_client_user.password_hash != "password-123"
    assert new_client_user.role.name == "CLIENT"
    assert not new_client_user.is_activated


def test_user_password_change(
    test_client, initialize_database, create_admin_user, create_client_user
):
    """
    GIVEN a user model
    WHEN a password change is made
    THEN check that the old password is invalidated and the new password hash is set
    """
    admin_user = create_admin_user
    client_user = create_client_user

    # verify current passwords are valid
    assert admin_user.verify_password("password-123")
    assert client_user.verify_password("password-123")

    # change user passwords
    admin_user.hash_password("new-password-123")
    client_user.hash_password("new-password-123")

    # verify old passwords invalidated
    assert not admin_user.verify_password("password-123")
    assert not client_user.verify_password("password-123")

    # verify new passwords are valid
    assert admin_user.verify_password("new-password-123")
    assert client_user.verify_password("new-password-123")


def test_valid_activation_token(create_admin_user):
    """
    GIVEN a User model
    WHEN a activation token is created
    THEN check token is valid
    """
    activation_token = create_admin_user.encode_single_use_jws(
        token_type="user_activation"
    )
    assert activation_token is not None
    validity_check = create_admin_user.decode_single_use_jws(
        token=activation_token, required_token_type="user_activation"
    )
    assert validity_check.get("status") == "Success"


def test_valid_authentication_token(activated_admin_user):
    """
    GIVEN A User Model
    WHEN a auth token is created
    THEN check it is a valid authentication token
    """
    authentication_token = activated_admin_user.encode_auth_token()
    assert authentication_token is not None
    resp = activated_admin_user.decode_auth_token(authentication_token.decode())
    assert not isinstance(authentication_token, str)
    assert (
        activated_admin_user.query.execution_options(show_all=True)
        .filter_by(id=resp["id"])
        .first()
        is not None
    )
