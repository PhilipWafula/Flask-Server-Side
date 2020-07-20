# system imports
import requests
from typing import Optional, Dict

# third party imports
from celery.utils.log import get_task_logger
from flask_mail import Message

# application imports
from app.server import config, mailer
from worker import celery

task_logger = get_task_logger(__name__)


@celery.task
def send_email(mail_sender: str, email_recipients: list, subject: str, html_body=None):
    """

    :param email_recipients: a list of email address that will receive an email.
    :param mail_sender: the email that the organization uses to send out emails.
    :param subject: email subject
    :param html_body: html version constituting email body
    :return:
    """

    if not mail_sender:
        raise ValueError("Mail sender cannot be empty")

    try:
        # build mail message
        message = Message(
            subject=subject, recipients=email_recipients, sender=mail_sender
        )

        # get html body if present
        message.html = html_body

        mailer.send(message)

    except Exception as exception:
        task_logger.error(f"An error occurred sending email: {exception}")


@celery.task
def initiate_africas_talking_mobile_checkout_transaction(api_key: str,
                                                         mobile_checkout_transaction: Optional[Dict] = None):
    """Mobile checkout post request task.

    :param api_key: Africa's Talking access token
    :param mobile_checkout_transaction: The transaction json body
    :return: null
    """
    # send payments
    try:
        result = requests.post(
            url=config.AFRICASTALKING_MOBILE_CHECKOUT_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=mobile_checkout_transaction,
        )

        if result.status_code != 201:
            message = result.text
            response = {
                'error': {
                    'message': message,
                    'status': 'Fail'
                }
            }
            return response, result.status_code
        else:
            return result.json(), result.status_code
    except Exception as exception:
        response = {
            'error': {
                'message': f'{exception}',
                'status': 'Fail'
            }
        }
        task_logger.error(
            f"An error occurred initiating a mobile checkout transaction with AfricasTalking: {exception}"
        )
        return response, 500


@celery.task
def initiate_africas_talking_business_to_business_transaction(api_key: str,
                                                              business_to_business_transaction: Optional[Dict] = None):
    """B2B post request task.

    :param api_key: Africa's Talking access token
    :param business_to_business_transaction: The transaction json body
    :return: null
    """

    try:
        # send payments
        result = requests.post(
            url=config.AFRICASTALKING_MOBILE_B2B_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=business_to_business_transaction,
        )
        if result.status_code != 201:
            message = result.text
            response = {
                'error': {
                    'message': message,
                    'status': 'Fail'
                }
            }
            return response, result.status_code
        else:
            return result.json(), result.status_code
    except Exception as exception:
        response = {
            'error': {
                'message': f'{exception}',
                'status': 'Fail'
            }
        }
        task_logger.error(
            f"An error occurred initiating a business to business transaction with AfricasTalking: {exception}"
        )
        return response, 500


@celery.task
def initiate_africas_talking_business_to_consumer_transaction(api_key: str,
                                                              business_to_consumer_transaction: Optional[Dict] = None):
    """B2C post request task.

    :param api_key: Africa's Talking access token
    :param business_to_consumer_transaction: The transaction json body
    :return: null
    """

    try:
        # send payments
        result = requests.post(
            url=config.AFRICASTALKING_MOBILE_B2C_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=business_to_consumer_transaction,
        )

        if result.status_code != 201:
            message = result.text
            response = {
                'error': {
                    'message': message,
                    'status': 'Fail'
                }
            }
            return response, result.status_code
        else:
            return result.json(), result.status_code
    except Exception as exception:
        response = {
            'error': {
                'message': f'{exception}',
                'status': 'Fail'
            }
        }
        task_logger.error(
            f"An error occurred initiating a business to consumer transaction with AfricasTalking: {exception}"
        )
        return response, 500


@celery.task
def initiate_africas_talking_wallet_balance_request(api_key: str, username: str):
    """Wallet balance get request task.

    :param api_key: Africa's Talking access token
    :param username: Africa's Talking username
    :return: null
    """

    try:
        # send query
        result = requests.get(
            url=config.AFRICAS_TALKING_WALLET_BALANCE,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            params={"username": username},
            timeout=5,
        )
        # check result
        if result.status_code != 200:
            message = result.text
            response = {
                'error': {
                    'message': message,
                    'status': 'Fail'
                }
            }
            return response, result.status_code
        else:
            return result.json(), result.status_code

    except Exception as exception:
        response = {
            'error': {
                'message': f'{exception}',
                'status': 'Fail'
            }
        }
        task_logger.error(
            f"An error occurred initiating a wallet balance request with AfricasTalking: {exception}"
        )
        return response, 500
