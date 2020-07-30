# application imports
from app.server.models.mpesa_transaction import MPesaTransaction
from app.server.utils.enums.transaction_enums import MpesaTransactionStatus


def test_payment_validation_api(test_client,
                                initialize_database,
                                create_initiated_mpesa_transaction,
                                create_successful_africas_talking_mobile_checkout_validation_callback):

    # simulate validation POST request from AfricasTalking
    response = test_client.post(
        '/api/v1/africas_talking/validate_payment/',
        headers={
            'Accept': 'application/json'
        },
        content_type='application/json',
        json=create_successful_africas_talking_mobile_checkout_validation_callback
    )

    # check that transaction is validated
    assert response.json == {
        'status': 'Validated'
    }


def test_payment_notifications_api(test_client,
                                   initialize_database,
                                   create_initiated_mpesa_transaction,
                                   create_successful_africas_talking_mobile_checkout_confirmation_callback):

    # get test transaction
    mpesa_transaction_id = create_successful_africas_talking_mobile_checkout_confirmation_callback.get(
        'transactionId'
    )
    mpesa_transaction = MPesaTransaction.query.filter_by(service_provider_transaction_id=mpesa_transaction_id).first()

    # check that statuses match yet to be validated transactions
    assert mpesa_transaction.status == MpesaTransactionStatus.INITIATED
    assert mpesa_transaction.status_description == 'Mobile checkout queued successfully.'

    # simulate validation POST request from AfricasTalking
    test_client.post(
        '/api/v1/africas_talking/confirm_payment/',
        headers={
            'Accept': 'application/json'
        },
        content_type='application/json',
        json=create_successful_africas_talking_mobile_checkout_confirmation_callback
    )

    assert mpesa_transaction.status == MpesaTransactionStatus.COMPLETE
    assert mpesa_transaction.status_description == 'Received Mobile Checkout funds from +254712345678'
