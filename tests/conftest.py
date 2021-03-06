import pytest
from flask import current_app

from app.server import create_app, db, app_logger
from app.server.data.seed_system_data import system_seed
from app.server.models.organization import Organization
from app.server.models.user import User, SignupMethod


@pytest.fixture(autouse=True)
def mock_sms_client(mocker):
    messages = []

    def mock_sms_api(phone_number, message):
        messages.append({"phone": phone_number, "message": message})

    mocker.patch("app.server.utils.messaging.send_sms", mock_sms_api)
    return messages


@pytest.fixture(autouse=True)
def mock_mailing_client(mocker):
    mails = []

    def mock_mail_api(
        email_recipients: list,
        mail_sender: str,
        subject: str,
        text_body,
        html_body=None,
    ):
        mails.append(
            {
                "recipients": email_recipients,
                "sender": mail_sender,
                "subject": subject,
                "text_body": text_body,
                "html_body": html_body,
            }
        )

    mocker.patch("app.server.utils.mailer.mail_handler", mock_mail_api)
    return mails


@pytest.fixture(scope="function")
def requires_auth(test_client):
    from app.server.utils.auth import requires_auth

    return requires_auth


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    test_client = app.test_client()
    context = app.app_context()
    context.push()

    yield test_client

    context.pop()


@pytest.fixture(scope="module")
def initialize_database():
    with current_app.app_context():
        db.create_all()
    yield db
    with current_app.app_context():
        try:
            db.session.commit()
        except Exception as exception:
            app_logger.warning(f"Exception occurred: {exception}")
            pass
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="module")
def seed_system_data(test_client, initialize_database):
    system_seed()


@pytest.fixture(scope="module")
def create_master_organization(test_client, initialize_database):
    organization = Organization(
        address="P.O.Box 112233", is_master=True, name="Test Master Organization"
    )
    db.session.add(organization)
    db.session.commit()
    return organization


@pytest.fixture(scope="module")
def create_standard_organization(test_client, initialize_database):
    organization = Organization(
        address="P.O.Box 332211", is_master=False, name="Test Standard Organization"
    )
    db.session.add(organization)
    db.session.commit()
    return organization


@pytest.fixture(scope="module")
def create_admin_user(
    test_client, initialize_database, seed_system_data, create_master_organization
):
    organization = create_master_organization
    user = User(
        given_names="John Doe",
        surname="Jane",
        email="admin@localhost.com",
        signup_method=SignupMethod.WEB_SIGNUP,
        role_id=1,
    )
    user.hash_password("password-123")
    user.bind_user_to_organization(organization)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="module")
def activated_admin_user(test_client, initialize_database, create_admin_user):
    user = create_admin_user
    user.is_activated = True
    return user


@pytest.fixture(scope="module")
def create_client_user(
    test_client, initialize_database, seed_system_data, create_master_organization
):
    organization = create_master_organization
    user = User(
        given_names="Jon Snow",
        surname="Stark",
        phone="+254712345678",
        signup_method=SignupMethod.MOBILE_SIGNUP,
        role_id=2,
    )
    user.set_identification_details(id_type="NATIONAL_ID", id_value="12345678")
    user.hash_password("password-123")
    db.session.add(user)
    user.bind_user_to_organization(organization)
    db.session.commit()
    return user


@pytest.fixture(scope="module")
def activated_client_user(test_client, initialize_database, create_client_user):
    user = create_client_user
    user.is_activated = True
    return user


@pytest.fixture(scope="function")
def create_blacklisted_token(activated_admin_user):
    from app.server.models.blacklisted_token import BlacklistedToken

    auth_token = activated_admin_user.encode_auth_token().decode()
    blacklisted_token = BlacklistedToken(token=auth_token)
    db.session.add(blacklisted_token)
    db.session.commit()
    return blacklisted_token
