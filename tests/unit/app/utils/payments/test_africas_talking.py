# system imports

# third-party imports
import pytest
import requests_mock

# application imports
from app import config
from app.server.utils.payments.africas_talking import AfricasTalking

# initiate africas talking util
africas_talking_utility = AfricasTalking(api_key=config.AFRICASTALKING_API_KEY,
                                         username=config.AFRICASTALKING_USERNAME)


@pytest.mark.parametrize("amount,"
                         "phone_number,"
                         "product_name,"
                         "currency_code,"
                         "metadata,"
                         "provider_channel",
                         [
                             (986.0, "+25487654321", "Sera", "UGX", None, None),
                             (124.75, "+25487654321", "Sera", "KES", {'OrderID': '321654987'}, None),
                             (168.75, "+25487654321", "Sera", "UGX", None, "123456"),
                             (10.0, "+254712345678", "Sera", "KES", {'OrderID': '321654987'}, "654321")
                         ])
def test_create_mobile_checkout_transaction(test_client,
                                            amount,
                                            phone_number,
                                            product_name,
                                            currency_code,
                                            metadata,
                                            provider_channel):
    mobile_checkout_transaction = africas_talking_utility.create_mobile_checkout_transaction(
        amount=amount,
        phone_number=phone_number,
        product_name=product_name,
        currency_code=currency_code,
        metadata=metadata,
        provider_channel=provider_channel
    )
    # add metadata and provider channel data if present in checkout transaction attrs
    if metadata and not provider_channel:
        assert mobile_checkout_transaction == {
            "amount": amount,
            "phoneNumber": phone_number,
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code,
            "metadata": metadata
        }
    elif provider_channel and not metadata:
        assert mobile_checkout_transaction == {
            "amount": amount,
            "phoneNumber": phone_number,
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code,
            "providerChannel": provider_channel
        }
    elif metadata and provider_channel:
        assert mobile_checkout_transaction == {
            "amount": amount,
            "phoneNumber": phone_number,
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code,
            "metadata": metadata,
            "providerChannel": provider_channel
        }
    else:
        assert mobile_checkout_transaction == {
            "amount": amount,
            "phoneNumber": phone_number,
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code
        }


@pytest.mark.parametrize("amount,"
                         "destination_account,"
                         "destination_channel,"
                         "product_name,"
                         "provider,"
                         "transfer_type,"
                         "currency_code,"
                         "metadata",
                         [
                             (358.0, "9865471", "7845215", "Sera", "Mpesa", "BusinessPayBill", "UGX", None),
                             (256.5, "7845215", "9865471", "Miradi", "Mpesa", "BusinessBuyGoods", "KES",
                              {'OrderID': '321654987'})
                         ])
def test_create_business_to_business_transaction(test_client,
                                                 amount,
                                                 destination_account,
                                                 destination_channel,
                                                 product_name,
                                                 provider,
                                                 transfer_type,
                                                 currency_code,
                                                 metadata):
    business_to_business_transaction = africas_talking_utility.create_business_to_business_transaction(
        amount=amount,
        destination_account=destination_account,
        destination_channel=destination_channel,
        product_name=product_name,
        provider=provider,
        transfer_type=transfer_type,
        currency_code=currency_code,
        metadata=metadata
    )
    if metadata:
        assert business_to_business_transaction == {
            "amount": amount,
            "destinationAccount": destination_account,
            "destinationChannel": destination_channel,
            "productName": product_name,
            "provider": provider,
            "transferType": transfer_type,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code,
            "metadata": metadata
        }
    else:
        assert business_to_business_transaction == {
            "amount": amount,
            "destinationAccount": destination_account,
            "destinationChannel": destination_channel,
            "productName": product_name,
            "provider": provider,
            "transferType": transfer_type,
            "username": config.AFRICASTALKING_USERNAME,
            "currencyCode": currency_code
        }


@pytest.mark.parametrize("amount,"
                         "phone_number,"
                         "product_name,"
                         "currency_code,"
                         "metadata,"
                         "name,"
                         "provider_channel,"
                         "reason",
                         [
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, None, None,
                              None),
                             (75.0, "+254712345678", "Sera", "KES", None, 'Jon Snow', None, None),
                             (98.0, "+254712345678", "Sera", "KES", None, None, "654321", None),
                             (365.0, "+254712345678", "Sera", "KES", None, None, None, "SalaryPayment"),
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, "Sansa Stark",
                              None, None),
                             (650.0, "+254712345678", "Sera", "KES", None, "Sansa Stark", "123456", None),
                             (650.0, "+254712345678", "Sera", "KES", None, None, "123456", "PromotionPayment"),
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, "Sansa Stark",
                              "123456", None),
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, "Sansa Stark",
                              None, "PromotionPayment"),
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, None, "123456",
                              "PromotionPayment"),
                             (650.0, "+254712345678", "Sera", "KES", None, "Sansa Stark", "123456", "PromotionPayment"),
                             (650.0, "+254712345678", "Sera", "KES", {'TransactionID': 'KLHSN7845120'}, "Sansa Stark",
                              "123456", "PromotionPayment"),
                             (650.0, "+254712345678", "Sera", "KES", None, None, None, None),
                         ])
def test_create_business_to_consumer_transaction(test_client,
                                                 amount,
                                                 phone_number,
                                                 product_name,
                                                 currency_code,
                                                 metadata,
                                                 name,
                                                 provider_channel,
                                                 reason):
    business_to_consumer_transaction = africas_talking_utility.create_business_to_consumer_transaction(
        amount=amount,
        phone_number=phone_number,
        product_name=product_name,
        currency_code=currency_code,
        metadata=metadata,
        name=name,
        provider_channel=provider_channel,
        reason=reason
    )

    if metadata and not name and not provider_channel and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata
            }]
        }
    elif name and not metadata and not provider_channel and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "name": name
            }]
        }
    elif provider_channel and not metadata and not name and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "providerChannel": provider_channel
            }]
        }
    elif reason and not metadata and not name and not provider_channel:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "reason": reason
            }]
        }
    elif metadata and name and not provider_channel and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata,
                "name": name,
            }]
        }
    elif name and provider_channel and not metadata and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "name": name,
                "providerChannel": provider_channel,
            }]
        }
    elif provider_channel and reason and not metadata and not name:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "providerChannel": provider_channel,
                "reason": reason
            }]
        }
    elif metadata and name and provider_channel and not reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata,
                "name": name,
                "providerChannel": provider_channel,
            }]
        }
    elif metadata and name and reason and not provider_channel:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata,
                "name": name,
                "reason": reason
            }]
        }
    elif metadata and provider_channel and reason and not name:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata,
                "providerChannel": provider_channel,
                "reason": reason
            }]
        }
    elif name and provider_channel and reason and not metadata:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "name": name,
                "providerChannel": provider_channel,
                "reason": reason
            }]
        }
    elif metadata and name and provider_channel and reason:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code,
                "metadata": metadata,
                "name": name,
                "providerChannel": provider_channel,
                "reason": reason
            }]
        }
    else:
        assert business_to_consumer_transaction == {
            "productName": product_name,
            "username": config.AFRICASTALKING_USERNAME,
            "recipients": [{
                "amount": amount,
                "phoneNumber": phone_number,
                "currencyCode": currency_code
            }]
        }


def test_initiate_mobile_checkout_transaction(mock_initiate_mobile_checkout_transaction, mobile_checkout_transaction):
    africas_talking_utility.initiate_mobile_checkout_transaction(mobile_checkout_transaction)
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'mobile_checkout_transaction': mobile_checkout_transaction
    }
    mock_initiate_mobile_checkout_transaction.assert_called_with(kwargs=kwargs)


def test_initiate_business_to_business_transaction(mock_initiate_business_to_business_transaction,
                                                   business_to_business_transaction):
    africas_talking_utility.initiate_business_to_business_transaction(business_to_business_transaction)
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'business_to_business_transaction': business_to_business_transaction
    }
    mock_initiate_business_to_business_transaction.assert_called_with(kwargs=kwargs)


def test_initiate_business_to_consumer_transaction(mock_initiate_business_to_consumer_transaction,
                                                   business_to_consumer_transaction):
    africas_talking_utility.initiate_business_to_consumer_transaction(business_to_consumer_transaction)
    kwargs = {
        'api_key': config.AFRICASTALKING_API_KEY,
        'business_to_consumer_transaction': business_to_consumer_transaction
    }
    mock_initiate_business_to_consumer_transaction.assert_called_with(kwargs=kwargs)


def test_get_wallet_balance_request():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.get(config.AFRICAS_TALKING_WALLET_BALANCE,
                            json={
                                "balance": "KES 600.0000",
                                "status": "Success"
                            })
        response, status_code = africas_talking_utility.get_wallet_balance_request()
        assert response == {
            "balance": "KES 600.0000",
            "status": "Success"
        }
        assert status_code == 200
