from flask import current_app

from app.server import app_logger
from app.server import ContextEnvironment
from app.server import sms
from app.server.models.user import User


def send_sms(message: str, phone_number: str):
    response = sms.send(message=message,
                        recipients=[phone_number])

    return response


def send_one_time_pin(user: User, phone_number: str):

    otp = user.set_otp_secret()
    message = "Hello {}, your activation code is: {}".format(user.given_names,
                                                             otp)

    context_env = ContextEnvironment(current_app)
    if context_env.is_development or context_env.is_testing:

        app_logger.info(
            "IS NOT PRODUCTION NOT ACTUALLY SENDING:\n"
            "Recipient: {}\n"
            "Message: {}".format(phone_number, message))
    else:
        send_sms(message=message, phone_number=phone_number)
