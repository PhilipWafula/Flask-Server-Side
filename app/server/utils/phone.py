import phonenumbers

from flask import current_app


def process_phone_number(phone_number, region=None, ignore_region=False):
    """
    Parse any given phone number.
    :param phone_number: int
    :param region: ISO 3166-1 alpha-2 codes
    :param ignore_region: Boolean. True returns original phone
    :return:
    """
    if phone_number is None:
        return None

    if ignore_region:
        return phone_number

    if region is None:
        region = current_app.config["DEFAULT_COUNTRY"]

    if not isinstance(phone_number, str):
        try:
            phone_number = str(int(phone_number))

        except ValueError:
            pass

    phone_number_object = phonenumbers.parse(phone_number, region)

    parsed_phone_number = phonenumbers.format_number(
        phone_number_object, phonenumbers.PhoneNumberFormat.E164
    )

    return parsed_phone_number
