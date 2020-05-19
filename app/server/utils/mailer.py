import jinja2
import os

from datetime import datetime
from flask import current_app

from app.server import config
from app.server import app_logger
from app.server import ContextEnvironment
from app.server.models.organization import Organization
from app.server.templates.mail_messages import MailMessage
from worker import tasks


def check_mailer_configured(organization: Organization):
    settings = organization
    # check that mailing sender is configured
    mailer_setting_missing = True
    if settings:
        # get mailer settings
        mailer_settings = [config.MAILER_SERVER,
                           config.MAILER_PORT,
                           config.MAILER_USERNAME,
                           config.MAILER_PASSWORD,
                           config.MAILER_DEFAULT_SENDER,
                           config.MAILER_USE_SSL,
                           config.MAILER_USE_TSL]
        # check if any is None
        mailer_setting_missing = any(setting is None for setting in mailer_settings)

    if mailer_setting_missing:
        return False
    else:
        return True


def _get_email_template(template_file):
    """
    Returns an email template file
    :param template_file: name of the template file.
    :return: email template file.
    """
    search_path = os.path.join(current_app.config['BASEDIR'], 'templates')

    template_loader = jinja2.FileSystemLoader(searchpath=search_path)
    template_environment = jinja2.Environment(loader=template_loader)

    return template_environment.get_template(template_file)


def _get_mail_body(action: str,
                   action_tag: str,
                   action_url: str,
                   copyright_year: int,
                   file_name: str,
                   given_names: str,
                   mail_message: str,
                   organization_address: str,
                   organization_name: str):
    """
    This method builds a mail body as per the flask_mail mailer object requirements. It takes the arguments below
    and leverages the provided email template files to render the respective html or text body files.

    :param action: Describes what action the email offers instructions for.
    :param action_tag: Identifies the organization that has sent the email by appending the organization name to
    the action parameter above. eg: Sample Organization: Reset your password.
    :param action_url: Provides a url which when appropriately accessed accomplishes the action described.
    :param copyright_year: Defines the year of the copyright for the software.
    :param file_name: Describes the email template file to use.
    :param given_names: The recipient's given names for mail personalization.
    :param mail_message: The instructions contained in the email.
    :param organization_address: A physical address for the organization
    :param organization_name: The organization's name
    :return:
    """
    template_file = file_name
    template = _get_email_template(template_file)
    mail_body = template.render(action=action,
                                action_tag=action_tag,
                                action_url=action_url,
                                copyright_year=copyright_year,
                                given_names=given_names,
                                mail_message=mail_message,
                                organization_address=organization_address,
                                organization_name=organization_name)
    return mail_body


def _mail_handler(email_recipients: list,
                  mail_sender: str,
                  subject: str,
                  text_body,
                  html_body=None):
    context_env = ContextEnvironment(current_app)
    if context_env.is_development or context_env.is_testing:
        recipients_logging_format = ', '.join(email_recipients)
        app_logger.info(
            "IS NOT PRODUCTION NOT ACTUALLY SENDING:\n"
            "From: {}\n"
            "To: {}\n"
            "{}".format(mail_sender, recipients_logging_format, text_body)
        )

    else:
        tasks.send_email.delay(mail_sender, email_recipients, subject, html_body)


class Mailer:
    def __init__(self, organization: Organization):
        self.organization = organization
        self.organization_name = organization.name
        self.mail_message = MailMessage(self.organization_name)
        self.mail_sender = config.MAILER_DEFAULT_SENDER
        self.organization_address = organization.address
        self.organization_domain = config.APP_DOMAIN

    def send_user_activation_email(self,
                                   activation_token: str,
                                   email: str,
                                   given_names: str):
        action_tag, mail_message = self.mail_message.activate_user_mail_message()
        action_url = self.organization_domain + '/login?activation_token={}'.format(activation_token)
        copyright_year = datetime.now().year
        action = action_tag.strip('{}: '.format(self.organization_name))

        html_body = _get_mail_body(action=action,
                                   action_tag=action_tag,
                                   action_url=action_url,
                                   copyright_year=copyright_year,
                                   file_name='action_email.html',
                                   given_names=given_names,
                                   mail_message=mail_message,
                                   organization_address=self.organization_address,
                                   organization_name=self.organization_name)

        text_body = _get_mail_body(action=action,
                                   action_tag=action_tag,
                                   action_url=action_url,
                                   copyright_year=copyright_year,
                                   file_name='action_email.txt',
                                   given_names=given_names,
                                   mail_message=mail_message,
                                   organization_address=self.organization_address,
                                   organization_name=self.organization_name)

        _mail_handler(email_recipients=[email],
                      html_body=html_body,
                      mail_sender=self.mail_sender,
                      subject=action_tag,
                      text_body=text_body)

    def send_reset_password_email(self,
                                  email: str,
                                  given_names: str,
                                  password_reset_token: str, ):
        action_tag, mail_message = self.mail_message.reset_user_password_mail_message()
        action_url = self.organization_domain + '/reset-password?token={}'.format(password_reset_token)
        copyright_year = datetime.now().year
        action = action_tag.strip('{}: '.format(self.organization_name))

        html_body = _get_mail_body(action=action,
                                   action_tag=action_tag,
                                   action_url=action_url,
                                   copyright_year=copyright_year,
                                   file_name='action_email.html',
                                   given_names=given_names,
                                   mail_message=mail_message,
                                   organization_address=self.organization_address,
                                   organization_name=self.organization_name)

        text_body = _get_mail_body(action=action,
                                   action_tag=action_tag,
                                   action_url=action_url,
                                   copyright_year=copyright_year,
                                   file_name='action_email.txt',
                                   given_names=given_names,
                                   mail_message=mail_message,
                                   organization_address=self.organization_address,
                                   organization_name=self.organization_name)

        _mail_handler(email_recipients=[email],
                      html_body=html_body,
                      mail_sender=self.mail_sender,
                      subject=action_tag,
                      text_body=text_body)
