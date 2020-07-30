"""project-wide test fixtures."""
import pytest
from flask import current_app

from app import config
from app.server import create_app, db, app_logger
from app.server.data.seed_system_data import system_seed
from app.server.models.mpesa_transaction import MpesaTransaction
from app.server.models.organization import Organization
from app.server.models.user import User, SignupMethod
from app.server.utils.enums.transaction_enums import MpesaTransactionServiceProvider,\
    MpesaTransactionStatus,\
    MpesaTransactionType


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


@pytest.fixture(scope="module")
def create_initiated_mpesa_transaction(test_client, initialize_database):
    mpesa_transaction = MpesaTransaction(
        destination_account='+254712345678',
        amount=375.00,
        product_name='flask-server-side',
        provider='MPESA',
        service_provider_transaction_id='ATPid_SampleTxnId123',
        idempotency_key='186f90f3-1897-41af-8f86-fe4e7128526f',
        status=MpesaTransactionStatus.INITIATED,
        status_description='Mobile checkout queued successfully.',
        type=MpesaTransactionType.MOBILE_CHECKOUT,
        service_provider=MpesaTransactionServiceProvider.AFRICAS_TALKING
    )
    db.session.add(mpesa_transaction)
    db.session.commit()


@pytest.fixture(scope="module")
def create_failed_mpesa_transaction(test_client, initialize_database):
    mpesa_transaction = MpesaTransaction(
        destination_account='+254712345678',
        amount=375.00,
        product_name='flask-server-side',
        provider='MPESA',
        service_provider_transaction_id='ATPid_SampleTxnId456',
        idempotency_key='987r98e3-1998-41lm-8f86-jh4e0006526z',
        status=MpesaTransactionStatus.FAILED,
        status_description='The user is not within network coverage.',
        type=MpesaTransactionType.MOBILE_CHECKOUT,
        service_provider=MpesaTransactionServiceProvider.AFRICAS_TALKING
    )
    db.session.add(mpesa_transaction)
    db.session.commit()

    return mpesa_transaction


@pytest.fixture(scope="module")
def create_successful_africas_talking_mobile_checkout_validation_callback():
    return {
        "amount": 375,
        "category": "MobileB2C",
        "currencyCode": "KES",
        "metadata": {
            "mapping_id": "Some ID",
            "recipient": "Some description"
        },
        "phoneNumber": "+254712345678",
        "sourceIpAddress": "154.78.47.41",
        "transactionId": "ATPid_SampleTxnId123"
    }


@pytest.fixture(scope="module")
def create_successful_africas_talking_mobile_checkout_confirmation_callback():
    return {
        "requestMetadata": {
            "item": "Vanilla Latte"
        },
        "sourceType": "PhoneNumber",
        "source": "+254712345678",
        "provider": "Athena",
        "destinationType": "Wallet",
        "description": "Received Mobile Checkout funds from +254712345678",
        "providerChannel": "ATHENA",
        "direction": "Inbound",
        "transactionFee": "KES 1.0000",
        "providerRefId": "dc9f551c-197b-404e-ba28-09a7b023c6dc",
        "providerMetadata": {
            "KYCInfo1": "Sample KYCInfo1",
            "KYCInfo2": "Sample KYCInfo2"
        },
        "providerFee": "KES 25.0000",
        "origin": "ApiRequest",
        "status": "Success",
        "productName": "flask-server-side",
        "category": "MobileCheckout",
        "transactionDate": "2020-07-29 08:22:54",
        "destination": "PaymentWallet",
        "value": "KES 375.0000",
        "transactionId": "ATPid_SampleTxnId123"
    }


@pytest.fixture(scope='module')
def create_successful_africas_talking_transaction_query_result():
    return {
        "status": "Success",
        "data": {
            "requestMetadata": {
                "item": "Vanilla Latte"
            },
            "sourceType": "PhoneNumber",
            "source": "+254700000000",
            "provider": "Athena",
            "destinationType": "Wallet",
            "description": "The user is not within network coverage.",
            "providerChannel": "ATHENA",
            "transactionFee": "KES 0.0000",
            "providerRefId": "N/A",
            "providerMetadata": {
                "item": "Vanilla Latte"
            },
            "status": "Failed",
            "productName": "flask-server-side",
            "category": "MobileCheckout",
            "transactionDate": "2020-07-29 08:22:54",
            "destination": "PaymentWallet",
            "value": "KES 2500.0000",
            "transactionId": "ATPid_SampleTxnId123",
            "creationTime": "2020-07-29 08:22:54"
        }
    }


@pytest.fixture(autouse=True)
def business_to_business_transaction():
    """Fixture for mocking b2b transaction data."""
    return {
        "amount": 10.00,
        "currencyCode": "KES",
        "destinationAccount": "Account",
        "destinationChannel": "635214",
        "productName": "flask-server-side",
        "provider": "Mpesa",
        "transferType": "BusinessPayBill",
        "username": config.AFRICASTALKING_USERNAME,
        "metadata": {
            "recipient": "Some description",
            "mapping_id": "Some ID"
        }
    }


@pytest.fixture(autouse=True)
def business_to_consumer_transaction():
    """Fixture for mocking b2c transaction data."""
    return {
        "productName": "flask-server-side",
        "username": config.AFRICASTALKING_USERNAME,
        "recipients": [
            {
                "amount": 50.00,
                "phoneNumber": "+254700000000",
                "currencyCode": "KES",
                "name": "Turing",
                "providerChannel": "000000"
            }
        ]
    }


@pytest.fixture(autouse=True)
def mobile_checkout_transaction():
    """Fixture for mocking checkout transaction data."""
    return {
        "amount": 2500.00,
        "phoneNumber": "+254700000000",
        "productName": "flask-server-side",
        "username": config.AFRICASTALKING_USERNAME,
        "currencyCode": "KES",
        "metadata": {
            "item": "Vanilla Latte"
        },
        "providerChannel": "ATHENA"
    }


@pytest.fixture(autouse=True)
def mock_initiate_business_to_business_transaction(mocker):
    initiate_business_to_business_transaction = mocker.MagicMock()
    mocker.patch('worker.tasks.initiate_africas_talking_business_to_business_transaction.apply_async',
                 initiate_business_to_business_transaction)
    return initiate_business_to_business_transaction


@pytest.fixture(autouse=True)
def mock_initiate_business_to_consumer_transaction(mocker):
    initiate_business_to_consumer_transaction = mocker.MagicMock()
    mocker.patch('worker.tasks.initiate_africas_talking_business_to_consumer_transaction.apply_async',
                 initiate_business_to_consumer_transaction)
    return initiate_business_to_consumer_transaction


@pytest.fixture(autouse=True)
def mock_initiate_mobile_checkout_transaction(mocker):
    initiate_mobile_checkout_transaction = mocker.MagicMock()
    mocker.patch(
        'worker.tasks.initiate_africas_talking_mobile_checkout_transaction.apply_async',
        initiate_mobile_checkout_transaction)
    return initiate_mobile_checkout_transaction
