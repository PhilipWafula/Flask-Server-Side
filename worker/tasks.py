from celery.utils.log import get_task_logger
from flask_mail import Message

from app.server import mailer
from worker import celery

task_logger = get_task_logger(__name__)


@celery.task
def send_email(mail_sender: str,
               email_recipients: list,
               subject: str,
               html_body=None):
    """

    :param email_recipients: a list of email address that will receive an email.
    :param mail_sender: the email that the organization uses to send out emails.
    :param subject: email subject
    :param html_body: html version constituting email body
    :return:
    """

    if not mail_sender:
        raise ValueError('Mail sender cannot be empty')

    try:
        # build mail message
        message = Message(subject=subject,
                          recipients=email_recipients,
                          sender=mail_sender)

        # get html body if present
        message.html = html_body

        mailer.send(message)

    except Exception as exception:
        task_logger.error('An error occurred: {}'.format(exception))
