from app.server import sms


def send_sms(message, phone_number):
    response = sms.send(message=message,
                        recipients=[phone_number])

    return response


def send_one_time_pin(user, phone_number):
    message = user.set_otp_secret()
    send_sms(message=message, phone_number=phone_number)
