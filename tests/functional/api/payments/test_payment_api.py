# application imports
from app import config

# third party imports
import requests
import requests_mock


# TODO: [Philip] Find a way to test the get wallet api call.


def test_make_business_to_business_transaction(test_client,
                                               activated_admin_user,
                                               business_to_business_transaction,
                                               mock_initiate_business_to_business_transaction):
    """
    GIVEN a flask application
    WHEN a POST request is sent to /api/v1/payments/ with a valid auth token and payment type of business_to_business
    THEN check that a business_to_business transaction task is initiated successfully
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.post(
        '/api/v1/payments/',
        headers={
            'Authorization': f'Bearer {authentication_token}',
            'Accept': 'application/json'
        },
        content_type='application/json',
        json={
            "amount": 10.00,
            "currency_code": "KES",
            "destination_account": "Account",
            "destination_channel": "635214",
            "payment_type": "business_to_business",
            "product_name": "flask-server-side",
            "provider": "Mpesa",
            "transfer_type": "BusinessPayBill",
            "payments_service_provider": "africas_talking",
            "username": config.AFRICASTALKING_USERNAME,
            "metadata": {
                "recipient": "Some description",
                "mapping_id": "Some ID"
            }
        }
    )
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'business_to_business_transaction': business_to_business_transaction
    }
    mock_initiate_business_to_business_transaction.assert_called_with(kwargs=kwargs)
    assert response.json == {
        'message': 'Business to business transaction initiated successfully.',
        'status': 'Success'
    }
    assert response.status_code == 200


def test_make_business_to_consumer_transaction(test_client,
                                               activated_admin_user,
                                               business_to_consumer_transaction,
                                               mock_initiate_business_to_consumer_transaction):
    """
    GIVEN a flask application
    WHEN a POST request is sent to /api/v1/payments/ with a valid auth token and payment type of business_to_consumer
    THEN check that a business_to_consumer transaction task is initiated successfully
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.post(
        '/api/v1/payments/',
        headers={
            'Authorization': f'Bearer {authentication_token}',
            'Accept': 'application/json'
        },
        content_type='application/json',
        json={
            "payment_type": "business_to_consumer",
            "amount": 50.00,
            "phone_number": "+254700000000",
            "currency_code": "KES",
            "product_name": "flask-server-side",
            "payments_service_provider": "africas_talking",
            "provider_channel": "000000",
            "name": "Turing"
        }
    )
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'idempotency_key': None,
        'business_to_consumer_transaction': business_to_consumer_transaction
    }
    mock_initiate_business_to_consumer_transaction.assert_called_with(kwargs=kwargs)
    assert response.json == {
        'message': 'Business to consumer transaction initiated successfully.',
        'status': 'Success'
    }
    assert response.status_code == 200


def test_make_mobile_checkout_transaction(test_client,
                                          activated_admin_user,
                                          mobile_checkout_transaction,
                                          mock_initiate_mobile_checkout_transaction):
    """
    GIVEN a flask application
    WHEN a POST request is sent to /api/v1/payments/ with a valid auth token and payment type of business_to_consumer
    THEN check that a business_to_consumer transaction task is initiated successfully
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.post(
        '/api/v1/payments/',
        headers={
            'Authorization': f'Bearer {authentication_token}',
            'Accept': 'application/json'
        },
        content_type='application/json',
        json={
            "amount": 2500.00,
            "phone_number": "+254700000000",
            "product_name": "flask-server-side",
            "currency_code": "KES",
            "metadata": {
                "item": "Vanilla Latte"
            },
            "provider_channel": "ATHENA",
            "payments_service_provider": "africas_talking",
            "payment_type": "mobile_checkout"
        }
    )
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'idempotency_key': None,
        'mobile_checkout_transaction': mobile_checkout_transaction
    }
    mock_initiate_mobile_checkout_transaction.assert_called_with(kwargs=kwargs)
    assert response.json == {
        'message': 'Mobile checkout transaction initiated successfully.',
        'status': 'Success'
    }
    assert response.status_code == 200


def test_retry_payments_api(test_client,
                            activated_admin_user,
                            mobile_checkout_transaction,
                            create_failed_mpesa_transaction,
                            mock_initiate_mobile_checkout_transaction,
                            create_successful_africas_talking_transaction_query_result):

    authentication_token = activated_admin_user.encode_auth_token().decode()

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(config.AFRICAS_TALKING_FIND_TRANSACTION,
                            json=create_successful_africas_talking_transaction_query_result
                            )
        response = test_client.post(
            '/api/v1/payments/retry/',
            headers={
                'Authorization': f'Bearer {authentication_token}',
                'Accept': 'application/json'
            },
            content_type='application/json',
            json={
                'service_provider_transaction_id': create_failed_mpesa_transaction.service_provider_transaction_id
            }
        )

        assert response.json == {
            'message': 'Mobile checkout transaction retrial initiated successfully.',
            'status': 'Success'
        }
        assert response.status_code == 200

        kwargs = {
            'api_key': config.AFRICASTALKING_API_KEY,
            'idempotency_key': create_failed_mpesa_transaction.idempotency_key,
            'mobile_checkout_transaction': mobile_checkout_transaction
        }

        mock_initiate_mobile_checkout_transaction.assert_called_with(kwargs=kwargs)
