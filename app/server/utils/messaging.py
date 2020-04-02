from flask import current_app

from app.server import sms


def send_sms(message, phone_number):
    response = sms.send(message=message,
                        recipients=[phone_number])

    return response


def send_one_time_pin(user, phone_number):
    # avoid actually sending the OTP in development environment
    is_development = current_app.config['DEPLOYMENT_NAME'] == 'development'
    message = user.set_otp_secret()
    if is_development:
        print('OTP is: {}'.format(message))
    send_sms(message=message, phone_number=phone_number)
