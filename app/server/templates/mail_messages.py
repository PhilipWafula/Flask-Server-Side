"""
This module is responsible for definition of mail template messages.
"""


class MailMessage:

    def __init__(self, organization_name: str):
        self.organization_name = organization_name

    def activate_user_mail_message(self):
        action_tag = '{}: Activate my account.'.format(self.organization_name)
        mail_message = 'Thank you for registering an admin account with {}. Use the button below to activate it.' \
                       'If you did not mean to register, please ignore this .'.format(self.organization_name)

        return action_tag, mail_message

    def reset_user_password_mail_message(self):
        action_tag = '{}: Reset my password.'.format(self.organization_name)
        mail_message = 'You requested to reset the password for your {} account.' \
                       'Use the button below reset it.' \
                       'If you did not request a password reset, please ignore this email.'\
            .format(self.organization_name)
        return action_tag, mail_message
