# system imports
import requests
from typing import Optional, Dict

# third party imports
from celery.utils.log import get_task_logger
from flask_mail import Message

# application imports
from app.server import config, db, mailer
from app.server.models.mpesa_transaction import MPesaTransaction
from app.server.utils.enums.transaction_enums import MpesaTransactionServiceProvider,\
    MpesaTransactionStatus,\
    MpesaTransactionType
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
        response = requests.post(
            url=config.AFRICASTALKING_MOBILE_CHECKOUT_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=mobile_checkout_transaction,
        )
        # get status code and status
        status_code = response.status_code
        response_body = response.json()

        # process response data
        if response_body.get('status') == 'PendingConfirmation':
            status = MpesaTransactionStatus.INITIATED
        else:
            status = MpesaTransactionStatus.FAILED

        # define transaction status description
        if status == 'Failed':
            status_description = response_body.get('errorMessage')
        else:
            status_description = 'Mobile checkout queued successfully.'

        # if transaction successfully initiated, create transaction on local table
        if status_code == 201 and status == 'PendingConfirmation':
            transaction = MPesaTransaction(
                destination_account=mobile_checkout_transaction.get('phoneNumber'),
                amount=mobile_checkout_transaction.get('amount'),
                product_name=mobile_checkout_transaction.get('productName'),
                provider='MPESA',
                service_provider_transaction_id=response.json().get('transactionId'),
                status=status,
                status_description=status_description,
                type=MpesaTransactionType.MOBILE_CHECKOUT,
                service_provider=MpesaTransactionServiceProvider.AFRICAS_TALKING
            )
            db.session.add(transaction)
            db.session.commit()

    except Exception as exception:
        task_logger.error(
            f"An error occurred initiating a mobile checkout transaction with AfricasTalking: {exception}"
        )


@celery.task
def initiate_africas_talking_business_to_business_transaction(api_key: str,
                                                              business_to_business_transaction: Optional[Dict] = None):
    """B2B post request task.

    :param api_key: Africa's Talking access token
    :param business_to_business_transaction: The transaction json body
    :return: null
    """

    try:
        response = requests.post(
            url=config.AFRICASTALKING_MOBILE_B2B_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=business_to_business_transaction,
        )

        # get status code and status
        status_code = response.status_code
        response_body = response.json()

        # process response data
        if response_body.get('status') == 'Queued':
            status = MpesaTransactionStatus.INITIATED
        else:
            status = MpesaTransactionStatus.FAILED

        # define transaction status description
        if status == 'Failed':
            status_description = response_body.get('errorMessage')
        else:
            status_description = 'Mobile business to business transaction queued successfully.'

        # if transaction successfully initiated, create transaction on local table
        if status_code == 201 and response_body.get('status') == 'Queued':
            transaction = MPesaTransaction(
                destination_account=business_to_business_transaction.get('destinationChannel'),
                amount=business_to_business_transaction.get('amount'),
                product_name=business_to_business_transaction.get('productName'),
                provider='MPESA',
                service_provider_transaction_id=response.json().get('transactionId'),
                status=status,
                status_description=status_description,
                type=MpesaTransactionType.MOBILE_BUSINESS_TO_BUSINESS,
                service_provider=MpesaTransactionServiceProvider.AFRICAS_TALKING
            )
            db.session.add(transaction)
            db.session.commit()

    except Exception as exception:
        task_logger.error(
            f"An error occurred initiating a business to business transaction with AfricasTalking: {exception}"
        )


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
        response = requests.post(
            url=config.AFRICASTALKING_MOBILE_B2C_URL,
            headers={
                "Accept": "application/json",
                "ApiKey": api_key,
                "Content-Type": "application/json",
            },
            timeout=5,
            json=business_to_consumer_transaction,
        )

        # get status code
        status_code = response.status_code
        # get all entries
        entries = response.json().get('entries')
        if status_code == 201 and entries:
            for entry in entries:
                # process amount
                amount = float(entry.get('value').lstrip("KES "))

                # define transaction status
                if entry.get('status') == 'Queued':
                    status = MpesaTransactionStatus.INITIATED
                else:
                    status = MpesaTransactionStatus.FAILED

                # define transaction status description
                if status == 'Failed':
                    status_description = entry.get('errorMessage')
                else:
                    status_description = 'Mobile Business to consumer transaction queued successfully.'

                transaction = MPesaTransaction(
                    destination_account=entry.get('phoneNumber'),
                    amount=amount,
                    product_name=business_to_consumer_transaction.get('productName'),
                    provider='MPESA',
                    service_provider_transaction_id=entry.get('transactionId'),
                    status=status,
                    status_description=status_description,
                    type=MpesaTransactionType.MOBILE_BUSINESS_TO_CONSUMER,
                    service_provider=MpesaTransactionServiceProvider.AFRICAS_TALKING
                )
                db.session.add(transaction)
                db.session.commit()

    except Exception as exception:
        task_logger.error(
            f"An error occurred initiating a business to consumer transaction with AfricasTalking: {exception}"
        )
