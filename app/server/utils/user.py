from flask import current_app
from jsonschema.exceptions import ValidationError

from phonenumbers import NumberParseException
from urllib.parse import urlparse

from app.server import app_logger
from app.server import ContextEnvironment
from app.server import db
from app.server.models.organization import Organization
from app.server.models.user import User
from app.server.models.user import SignupMethod
from app.server.schemas.json.user import user_json_schema
from app.server.schemas.user import user_schema
from app.server.templates.responses import invalid_request_on_validation
from app.server.templates.responses import mailer_not_configured
from app.server.utils.enums.access_control_enums import AccessControlType
from app.server.utils.mailer import check_mailer_configured
from app.server.utils.mailer import Mailer
from app.server.utils.messaging import send_one_time_pin
from app.server.utils.validation import validate_request
from app.server.utils.phone import process_phone_number


def get_organization(public_identifier: str):
    if public_identifier:
        organization = Organization.query.filter_by(public_identifier=public_identifier).first()
        return organization
    raise ValueError('No organization matching public identifier was found.')


def create_user(given_names=None,
                surname=None,
                email=None,
                msisdn=None,
                address=None,
                date_of_birth=None,
                id_type=None,
                id_value=None,
                password=None,
                signup_method=SignupMethod.MOBILE_SIGNUP,
                organization: Organization = None):
    """
    :param organization:
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
    user = User(given_names=given_names,
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

    # unless special organization defined, default to master organization
    if not organization:
        organization = Organization.master_organisation()

    # bind user to organization
    user.bind_user_to_organization(organization)

    db.session.add(user)
    db.session.flush()

    # handle setting roles
    if signup_method == SignupMethod.MOBILE_SIGNUP:
        user.set_user_role(role='CLIENT')

    return user


def update_user(user,
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
                                          user_update_allowed=False):
    """
    :param user_update_allowed:
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
    signup_method = user_attributes.get('signup_method')
    public_identifier = user_attributes.get('public_identifier')

    # verify request
    try:
        validate_request(instance=user_attributes, schema=user_json_schema)

    except ValidationError as error:
        response, status_code = invalid_request_on_validation(error.message)
        return response, status_code

    # get organization to tie user to
    organization = get_organization(public_identifier)

    if not organization:
        response = {
            'error': {
                'message': 'User cannot be created without a parent organization.'
                           'No organization found for public identifier: {}.'.format(public_identifier),
                'status': 'Fail'
            }
        }

        return response, 403

    # process sign up methods
    if signup_method:
        if signup_method == 'MOBILE':
            signup_method = SignupMethod.MOBILE_SIGNUP

        if signup_method == 'WEB':
            signup_method = SignupMethod.WEB_SIGNUP

    if password and len(password) < 8:
        response = {
            'error':
                {
                    'message': 'Password must be at least 8 characters long.',
                    'status': 'Fail'}
        }
        return response, 422

    if email and signup_method == SignupMethod.WEB_SIGNUP:
        # get user's organization configs
        organization_configuration: Organization = organization.configuration

        # get domain
        domain = organization_configuration.domain
        base_domain = ''

        # process domain
        if domain:
            # get domain netloc
            parsed_domain = urlparse(domain)
            network_location = parsed_domain.netloc
            port = parsed_domain.port

            base_domain = network_location

            # process domain
            if 'www.' in network_location:
                base_domain = base_domain.strip('www.')

            if port:
                base_domain = base_domain.strip(':{}'.format(str(port)))

        # check that the base domain is in the email
        if base_domain in email:

            # check whether user with admin role exists
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:

                existing_user_is_activated = existing_user.is_activated

                if not existing_user_is_activated:
                    response = {
                        'error': {
                            'message': 'User already exists. Please check email to activate your account.',
                            'status': 'Fail'
                        }
                    }

                    return response, 403

                response = {
                    'error': {
                        'message': 'User already exists. Please log in',
                        'status': 'Fail'
                    }
                }

                return response, 403

            # ensure mailer settings are configured since admin creation relies on the application mailer
            mailer_is_configured = check_mailer_configured(organization)

            if not mailer_is_configured:
                response, status_code = mailer_not_configured()
                return response, status_code

            # create user with admin role
            admin = create_user(email=email,
                                given_names=given_names,
                                password=password,
                                surname=surname,
                                signup_method=signup_method)

            # set admin roles
            if organization_configuration.access_control_type == AccessControlType.STANDARD_ACCESS_CONTROL:
                admin.set_user_role(role='ADMIN')

            if organization_configuration.access_control_type == AccessControlType.TIERED_ACCESS_CONTROL:
                admin.set_user_role(role='ADMIN', tier='SYSTEM_ADMIN')

            # encode single use activation token
            activation_token = admin.encode_single_use_jws(token_type='user_activation')

            context_environment = ContextEnvironment(current_app)

            # send activation email
            mailer = Mailer(organization=organization)
            mailer.send_user_activation_email(activation_token=activation_token,
                                              email=email,
                                              given_names=given_names)

            if context_environment.is_development() or context_environment.is_testing():
                app_logger.info("IS NOT PRODUCTION\n"
                                "ACTIVATION TOKEN: {}".format(activation_token))

            response = {
                'data': {'user': user_schema.dump(admin).data},
                'message': 'Successfully created admin. Check email to activate.',
                'status': 'Success'
            }
            return response, 200

    # validate msisdn
    if not msisdn:
        response = {
            'error':
                {
                    'message': 'Phone number cannot be empty.',
                    'status': 'Fail'}
        }
        return response, 422
    else:
        # check that id values are present
        if not (id_type, id_value):
            response = {
                'error':
                    {
                        'message': 'ID data cannot be empty.',
                        'status': 'Fail'}
            }
            return response, 422

        # process phone number and ensure phone number validity
        try:
            msisdn = process_phone_number(msisdn)
        except NumberParseException as exception:
            response = {
                'error':
                    {
                        'message': 'Invalid phone number. ERROR: {}'.format(exception),
                        'status': 'Fail'}
            }
            return response, 422

        # check if user is already existent
        existing_user = User.query.filter_by(msisdn=msisdn).first()

        # check if request is an update request
        if existing_user and not user_update_allowed:
            response = {
                'error':
                    {
                        'message': 'User already exists. Please Log in.',
                        'status': 'Fail'}
            }
            return response, 403

        # process update request
        if existing_user and user_update_allowed:
            try:
                user = update_user(user_attributes,
                                   given_names=given_names,
                                   surname=surname,
                                   address=address,
                                   date_of_birth=date_of_birth)

                db.session.commit()

                response = {
                    'data': {'user': user_schema.dump(user).data},
                    'message': 'User successfully updated.',
                    'status': 'Success'
                }

                return response, 200

            except Exception as exception:
                response = {'error': {'message': '{}'.format(exception),
                                      'status': 'Fail'}}
                return response, 400

        # create client user
        user = create_user(given_names=given_names,
                           surname=surname,
                           email=email,
                           msisdn=msisdn,
                           address=address,
                           date_of_birth=date_of_birth,
                           password=password,
                           id_type=id_type,
                           id_value=id_value)

        # send user OTP to validate user's phone number
        if signup_method == SignupMethod.MOBILE_SIGNUP:
            send_one_time_pin(user=user, phone_number=msisdn)
            response = {
                'message': 'User created. Please verify phone number.',
                'status': 'Success'
            }
            return response, 200
