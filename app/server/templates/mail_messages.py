"""
This module is responsible for definition of mail template messages.
"""


class MailMessage:
    def __init__(self, organization_name: str):
        self.organization_name = organization_name

    def activate_user_mail_message(self):
        action_tag = f"{self.organization_name}: Activate my account."
        mail_message = (
            f"Thank you for registering an admin account with {self.organization_name}."
            f"Use the button below to activate it."
            "If you did not mean to register, please ignore this ."
        )

        return action_tag, mail_message

    def reset_user_password_mail_message(self):
        action_tag = f"{self.organization_name}: Reset my password."
        mail_message = (
            f"You requested to reset the password for your {self.organization_name} account."
            "Use the button below reset it."
            "If you did not request a password reset, please ignore this email."
        )
        return action_tag, mail_message
