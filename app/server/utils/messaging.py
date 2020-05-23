from flask import current_app

from app.server import app_logger
from app.server import ContextEnvironment
from app.server import sms
from app.server.models.user import User


def send_sms(message: str, phone_number: str):
    context_env = ContextEnvironment(current_app)
    if context_env.is_development or context_env.is_testing:
        app_logger.info(
            'IS NOT PRODUCTION NOT ACTUALLY SENDING:\n'
            f'Recipient: {phone_number}\n'
            f'Message: {message}')
    else:
        # TODO: [Philip] Make SMS asynchronous
        response = sms.send(message=message,
                            recipients=[phone_number])

        return response


def send_one_time_pin(user: User):
    otp = user.set_otp_secret()
    message = f'Hello {user.given_names}, your activation code is: {otp}'
    send_sms(message=message, phone_number=user.phone)
