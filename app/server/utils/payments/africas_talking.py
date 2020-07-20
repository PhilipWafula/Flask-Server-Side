# system imports
from typing import Dict, Optional

# third party import
from flask import jsonify, make_response

# application imports
from app.server import constants
from app.server.templates import responses
from app.server.utils.phone import process_phone_number
from worker import tasks


class AfricasTalking:
    """This class creates an Africa's Talking payment object with product username and api key."""

    def __init__(self, api_key: str, username: str):
        self.api_key = api_key
        self.username = username

    def create_mobile_checkout_transaction(
        self,
        amount: float,
        phone_number: str,
        product_name: str,
        currency_code: str = "KES",
        metadata: Optional[Dict] = None,
        provider_channel: Optional[str] = None,
    ):
        """This function creates a checkout transaction JSON object with the attributes provided.

        :param amount: The amount to be transacted
        :param phone_number: The target phone number to complete the transaction
        :param product_name: The product name initiating the transaction
        :param currency_code: The currency to be used
        :param metadata: Additional data
        :param provider_channel: The channel through which the payment has been initiated from
        :return: The transaction object
        """
        # ensure that phone number is in correct MSISDN format
        phone_number = process_phone_number(phone_number, 'KE')

        # check that amount is of type float
        if not isinstance(amount, float):
            try:
                amount = float(amount)
            except ValueError:
                response, status_code = responses.invalid_amount_type(amount)
                return response, status_code

        # check that currency is in supported currency codes
        if currency_code not in constants.AFRICAS_TALKING_CURRENCY_CODES:
            response, status_code = responses.unsupported_currency_code(currency_code)
            return response, status_code

        mobile_checkout_transaction = {
            "amount": amount,
            "phoneNumber": phone_number,
            "productName": product_name,
            "username": self.username,
            "currencyCode": currency_code
        }

        if metadata:
            mobile_checkout_transaction["metadata"] = metadata

        if provider_channel:
            mobile_checkout_transaction["providerChannel"] = provider_channel

        return mobile_checkout_transaction, 201

    def create_business_to_business_transaction(
        self,
        amount: float,
        destination_account: str,
        destination_channel: str,
        product_name: str,
        provider: str,
        transfer_type: str,
        currency_code: str = "KES",
        metadata: Optional[Dict] = None,
    ):
        """This function creates a B2B transaction JSON object with the parameters provided.

        :param amount: The amount to be transacted
        :param destination_account: The account name that will receive the payment
        :param destination_channel: The channel that will receive the payment
        :param product_name: The product name initiating the transaction
        :param provider: The provider used to process the request
        :param transfer_type: The transfer type of the payment
        :param currency_code: The currency to be used
        :param metadata: Additional data
        :return: The transaction object
        """
        # check that amount is of type float
        if not isinstance(amount, float):
            try:
                amount = float(amount)
            except ValueError:
                response, status_code = responses.invalid_amount_type(amount)
                return response, status_code

        # check that provider channel is in supported providers
        if provider not in constants.AFRICAS_TALKING_PROVIDERS:
            response, status_code = responses.unsupported_provider(provider)
            return response, status_code

        # check that transfer type is in supported transfer types
        if transfer_type not in constants.AFRICAS_TALKING_TRANSFER_TYPES:
            response, status_code = responses.unsupported_transfer_type(transfer_type)
            return response, status_code

        # check that currency is in supported currency codes
        if currency_code not in constants.AFRICAS_TALKING_CURRENCY_CODES:
            response, status_code = responses.unsupported_currency_code(currency_code)
            return response, status_code

        business_to_business_transaction = {
            "amount": amount,
            "destinationAccount": destination_account,
            "destinationChannel": destination_channel,
            "productName": product_name,
            "provider": provider,
            "transferType": transfer_type,
            "username": self.username,
            "currencyCode": currency_code,
        }

        if metadata:
            business_to_business_transaction["metadata"] = metadata

        return business_to_business_transaction, 201

    def create_business_to_consumer_transaction(
        self,
        amount: float,
        phone_number: str,
        product_name: str,
        currency_code: str = "KES",
        metadata: Optional[Dict] = None,
        name: Optional[str] = None,
        provider_channel: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """This function creates a B2C transaction JSON object from the parameters provided.

        :param amount: The amount to be transacted
        :param phone_number: The phone number of the recipient
        :param product_name: The product name initiating the transaction
        :param currency_code: The currency to be used
        :param metadata: Additional data
        :param name: The name of the recipient
        :param provider_channel: The channel through which the payment has been initiated from
        :param reason: The purpose of the payment
        :return: The transaction object
        """
        # ensure that phone number is in correct MSISDN format
        phone_number = process_phone_number(phone_number, 'KE')

        # check that amount is of type float
        if not isinstance(amount, float):
            try:
                amount = float(amount)
            except ValueError:
                response, status_code = responses.invalid_amount_type(amount)
                return response, status_code

        # check that currency is in supported currency codes
        if currency_code not in constants.AFRICAS_TALKING_CURRENCY_CODES:
            response, status_code = responses.unsupported_currency_code(currency_code)
            return response, status_code

        # check that reason is in supported reasons
        if reason and reason not in constants.AFRICAS_TALKING_REASONS:
            response, status_code = responses.unsupported_reason(reason)
            return response, status_code

        recipient = {
            "amount": amount,
            "phoneNumber": phone_number,
            "currencyCode": currency_code,
        }

        if metadata:
            recipient["metadata"] = metadata

        if name:
            recipient["name"] = name

        if provider_channel:
            recipient["providerChannel"] = provider_channel

        if reason:
            recipient["reason"] = reason

        recipients = [recipient]

        business_to_consumer_transaction = {
            "productName": product_name,
            "username": self.username,
            "recipients": recipients,
        }

        return business_to_consumer_transaction, 201

    def initiate_mobile_checkout_transaction(self, mobile_checkout_transaction: Optional[Dict] = None):
        """This functions calls the task necessary to perform a checkout transaction.

        :param mobile_checkout_transaction: checkout transaction object
        :return: null
        """
        kwargs = {
            'api_key': self.api_key,
            'mobile_checkout_transaction': mobile_checkout_transaction
        }
        result = tasks.initiate_africas_talking_mobile_checkout_transaction.apply_async(kwargs=kwargs,
                                                                                        ignore_result=False)

        return result.get()

    def initiate_business_to_business_transaction(self, business_to_business_transaction: Optional[Dict] = None):
        """This function calls the task necessary to perform a business to business transaction.

        :param business_to_business_transaction: B2B transaction object
        :return: null
        """
        kwargs = {
            'api_key': self.api_key,
            'business_to_business_transaction': business_to_business_transaction,
        }
        result = tasks.initiate_africas_talking_business_to_business_transaction.apply_async(kwargs=kwargs,
                                                                                             ignore_result=False)
        return result.get()

    def initiate_business_to_consumer_transaction(self, business_to_consumer_transaction: Optional[Dict] = None):
        """This function calls the task necessary to perform a business to consumer transaction.

        :param business_to_consumer_transaction: B2C transaction object
        :return: null
        """
        kwargs = {
            'api_key': self.api_key,
            'business_to_consumer_transaction': business_to_consumer_transaction
        }
        result = tasks.initiate_africas_talking_business_to_consumer_transaction.apply_async(kwargs=kwargs,
                                                                                             ignore_result=False)
        return result.get()

    def initiate_wallet_balance_request(self):
        """This function creates a task for sending a wallet balance query."""
        kwargs = {
            'api_key': self.api_key,
            'username': self.username,
        }
        result = tasks.initiate_africas_talking_wallet_balance_request.apply_async(kwargs=kwargs, ignore_result=False)
        return result.get()
