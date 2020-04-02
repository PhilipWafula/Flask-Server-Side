import jinja2
import os
from flask import current_app
from flask import request

from app.server.models.organization import Organization
from worker import tasks


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


def _get_organization_name_and_mailer_settings(organization: Organization):
    if organization:
        # get organization name
        organization_name = organization.name

        # get organization configuration
        organization_configuration = organization.configuration

        # get mailer settings
        organization_mailer_settings = organization_configuration.mailer_settings

        return organization_name, organization_mailer_settings

    raise ValueError('No organization was provided.')


def _mail_handler(mail_sender: str,
                  email_recipients: list,
                  subject: str,
                  html_body=None):
    is_development = current_app.config['DEPLOYMENT_NAME'] == 'development'
    is_production = current_app.config['DEPLOYMENT_NAME'] == 'production'
    is_testing = current_app.config['DEPLOYMENT_NAME'] == 'testing'

    if is_development or is_testing:
        print('Subject: {} \n From: {}  \n Recipient: {} \n Message: {}'.format(subject,
                                                                                mail_sender,
                                                                                email_recipients,
                                                                                html_body))

    if is_production:
        # send email
        tasks.send_email.delay(mail_sender, email_recipients, subject, html_body)


def send_user_activation_email(activation_token: str,
                               email: str,
                               given_names: str,
                               organization: Organization):
    """
    Sends token to activate user's account.
    :param given_names:
    :param organization:
    :param activation_token: account activation token.
    :param email: email address of recipient.
    """
    organization_name, mailer_settings = _get_organization_name_and_mailer_settings(organization)

    html_template_file = 'user_activation_email.html'
    html_template = _get_email_template(html_template_file)
    html_body = html_template.render(activation_token=activation_token,
                                     giver_names=given_names,
                                     host=request.url_root,
                                     organization_name=organization_name)

    mail_sender = mailer_settings.get('DEFAULT_SENDER', None)

    _mail_handler(email_recipients=[email],
                  subject='{}: Activate your account.'.format(organization_name),
                  html_body=html_body,
                  mail_sender=mail_sender)


def send_reset_password_email(password_reset_token: str,
                              email: str,
                              given_names: str,
                              organization: Organization):
    """
    Sends email with rest password token token
    :param given_names:
    :param organization:
    :param password_reset_token: password reset token.
    :param email: email address of recipient.
    """
    organization_name, mailer_settings = _get_organization_name_and_mailer_settings(organization)

    html_template_file = 'user_password_reset_email.html'
    html_template = _get_email_template(html_template_file)
    html_body = html_template.render(password_reset_token=password_reset_token,
                                     giver_names=given_names,
                                     host=request.url_root,
                                     organization_name=organization_name)

    mail_sender = mailer_settings.get('mail_sender', None)

    _mail_handler(email_recipients=[email],
                  subject='{}: Reset password.'.format(organization_name),
                  html_body=html_body,
                  mail_sender=mail_sender)
