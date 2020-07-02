# third party imports
import pytest

# platform imports
from app.server.templates.responses import organization_not_found, \
    organization_id_not_provided, \
    user_not_found, \
    user_id_not_provided, \
    invalid_request_on_validation, \
    mailer_not_configured, \
    otp_resent_successfully, \
    invalid_amount_type, \
    unsupported_currency_code, \
    unsupported_provider,\
    unsupported_transfer_type, \
    unsupported_reason


def test_organization_not_found():
    response, status_code = organization_not_found(organization_id=1)
    assert response['error'].get('message') == 'Organization with id 1 not found.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 404


def test_organization_id_not_provided():
    response, status_code = organization_id_not_provided()
    assert response['error'].get('message') == 'Please provide a valid organization id.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_user_not_found():
    response, status_code = user_not_found(user_id=1)
    assert response['error'].get('message') == 'User with id 1 not found.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 404


def test_user_id_not_provided():
    response, status_code = user_id_not_provided()
    assert response['error'].get('message') == 'Please provide a valid user id.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_invalid_request_on_validation():
    response, status_code = invalid_request_on_validation(message='Sample message.')
    assert response['error'].get('message') == 'Invalid request: Sample message.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 400


def test_mailer_not_configured():
    response, status_code = mailer_not_configured()
    assert response['error'].get('message') == 'Please configure your mailer, to facilitate admin registration.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 403


def test_otp_resent_successfully():
    response, status_code = otp_resent_successfully()
    assert response.get('message') == 'Pin resent successfully.'
    assert response.get('status') == 'Success'
    assert status_code == 200


@pytest.mark.parametrize('amount',
                         [
                             '200.0',
                             60,
                             {'some_value': 60}
                         ])
def test_invalid_amount_type(amount):
    response, status_code = invalid_amount_type(amount=amount)
    assert response['error'].get('message') == f'Incorrect amount type: {type(amount)}.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_unsupported_currency_code():
    response, status_code = unsupported_currency_code(currency_code='YEN')
    assert response['error'].get('message') == f'Unsupported currency code: YEN.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_unsupported_provider():
    response, status_code = unsupported_provider(provider='Airtel')
    assert response['error'].get('message') == f'Unsupported provider: Airtel.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_unsupported_transfer_type():
    response, status_code = unsupported_transfer_type(transfer_type='RandomTransferType')
    assert response['error'].get('message') == f'Unsupported transfer type: RandomTransferType.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422


def test_unsupported_reason():
    response, status_code = unsupported_reason(reason='RandomReason')
    assert response['error'].get('message') == f'Unsupported reason: RandomReason.'
    assert response['error'].get('status') == 'Fail'
    assert status_code == 422

