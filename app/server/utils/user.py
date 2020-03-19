from enum import Enum
from phonenumbers import NumberParseException

from app.server import db
from app.server.constants import IDENTIFICATION_TYPES
from app.server.models import user as user_model
from app.server.schemas.user import user_schema
from app.server.utils.messaging import send_one_time_pin
from app.server.utils.phone import process_phone_number


class SignupMethod(Enum):
    WEB_SIGNUP = 'WEB_SIGNUP',
    MOBILE_SIGNUP = 'MOBILE_SIGNUP'


def create_loan_account_user(given_names=None,
                             surname=None,
                             email=None,
                             msisdn=None,
                             address=None,
                             date_of_birth=None,
                             id_type=None,
                             id_value=None,
                             password=None,
                             signup_method=SignupMethod.MOBILE_SIGNUP):
    """
    :param signup_method:
    :param given_names:
    :param surname:
    :param email:
    :param msisdn:
    :param address:
    :param date_of_birth:
    :param id_type:
    :param id_value:
    :param password:
    :return:
    """

    # create user
    user = user_model.User(given_names=given_names,
                           surname=surname,
                           email=email,
                           msisdn=msisdn,
                           date_of_birth=date_of_birth,
                           address=address,
                           signup_method=signup_method)

    user.is_activated = False

    # set identification information
    if id_value:
        user.set_identification_details(id_type=id_type,
                                        id_value=id_value)

    # hash password
    if password:
        user.hash_password(password=password)

    db.session.add(user)

    return user


def update_loan_account_user(user,
                             given_names=None,
                             surname=None,
                             address=None,
                             date_of_birth=None):
    """
    :param user:
    :param given_names:
    :param surname:
    :param address:
    :param date_of_birth:
    :return:
    """

    if given_names:
        user.given_names = given_names

    if surname:
        user.surname = surname

    if address:
        user.address = address

    if date_of_birth:
        user.date_of_birth = date_of_birth

    return user


def process_create_or_update_user_request(user_attributes,
                                          signup_method=SignupMethod.MOBILE_SIGNUP,
                                          user_update_allowed=False):
    """
    :param user_update_allowed:
    :param signup_method:
    :param user_attributes:
    :return:
    """
    # get user data
    given_names = user_attributes.get('given_names')
    surname = user_attributes.get('surname')
    email = user_attributes.get('email')
    msisdn = user_attributes.get('msisdn')
    address = user_attributes.get('address')
    date_of_birth = user_attributes.get('date_of_birth')
    id_type = user_attributes.get('id_type')
    id_value = user_attributes.get('id_value')
    password = user_attributes.get('password')

    # validate names
    for name in [given_names, surname]:
        if not name:
            response = {'error': {'message': 'Names cannot be empty.'}}
            return response, 422

    # validate password
    if not password:
        response = {'error': {'message': 'Password cannot be empty.'}}
        return response, 422
    elif password and len(password) < 8:
        response = {'error': {'message': 'Password must be at least 8 characters long.'}}
        return response, 422

    for id_data in [id_type, id_value]:
        if not id_data:
            response = {'error': {'message': 'ID data cannot be empty.'}}
            return response, 422

    # validate msisdn
    if not msisdn:
        response = {'error': {'message': 'Phone number cannot be empty.'}}
        return response, 422
    else:
        try:
            # process phone number and ensure phone number validity
            msisdn = process_phone_number(msisdn)
        except NumberParseException as exception:
            response = {'error': {'message': 'Invalid phone number. ERROR: {}'.format(exception)}}
            return response, 422

        # check if user is already existent
        existing_user = user_model.User.query.filter_by(msisdn=msisdn).first()

        if existing_user:
            response = {'error': {'message': 'User already exists. Please Log in.'}}
            return response, 403

        # check if user update action is allowed
        if existing_user and user_update_allowed:
            try:
                user = update_loan_account_user(user_attributes,
                                                given_names=given_names,
                                                surname=surname,
                                                address=address,
                                                date_of_birth=date_of_birth)

                db.session.commit()

                response = {'data': {'user': user_schema.dump(user).data},
                            'message': 'User successfully updated.',
                            'status': 'success'}

                return response, 200

            except Exception as exception:
                response = {'error': {'message': '{}'.format(exception)}}
                return response, 400

        user = create_loan_account_user(given_names=given_names,
                                        surname=surname,
                                        email=email,
                                        msisdn=msisdn,
                                        address=address,
                                        date_of_birth=date_of_birth,
                                        password=password,
                                        id_type=id_type,
                                        id_value=id_value)

        if signup_method == SignupMethod.MOBILE_SIGNUP:
            send_one_time_pin(user=user, phone_number=msisdn)
            response = {'message': 'User created. Please verify phone number.',
                        'status': 'success'}
            return response, 200

        else:
            response = {'data': {'user': user_schema.dump(user).data},
                        'message': 'User successfully updated.',
                        'status': 'success'}
            return response, 200
