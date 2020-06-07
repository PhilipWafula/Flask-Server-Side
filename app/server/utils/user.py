from jsonschema.exceptions import ValidationError
from phonenumbers import NumberParseException
from typing import Optional

from app.server import db
from app.server.constants import SUPPORTED_ROLES
from app.server.models.organization import Organization
from app.server.models.user import SignupMethod
from app.server.models.user import User
from app.server.schemas.json.user import user_json_schema
from app.server.schemas.user import user_schema
from app.server.templates.responses import (
    invalid_request_on_validation,
    mailer_not_configured,
)
from app.server.utils.mailer import Mailer, check_mailer_configured
from app.server.utils.messaging import send_one_time_pin
from app.server.utils.phone import process_phone_number
from app.server.utils.validation import validate_request


def get_organization(public_identifier: str):
    if public_identifier:
        organization = Organization.query.filter_by(
            public_identifier=public_identifier
        ).first()
        return organization
    raise ValueError("No organization matching public identifier was found.")


def get_user_from_unique_attribute(
    email: Optional[str] = None,
    user_id: Optional[int] = None,
    phone: Optional[str] = None,
):
    user = None
    if email:
        user = User.query.filter_by(email=email).first()

    if user_id:
        user = User.query.get(user_id)

    if phone:
        user = User.query.filter_by(phone=phone).first()
    return user


def get_user_role_from_auth_token(token: str):
    decoded_user_data = User.decode_auth_token(token)
    if not isinstance(decoded_user_data, str):
        user = (
            User.query.filter_by(id=decoded_user_data.get("id"))
            .execution_options(show_all=True)
            .first()
        )
        if not user:
            raise Exception("No user found.")
        else:
            return user.role.name
    else:
        raise Exception(decoded_user_data)


def create_user(
    given_names=None,
    surname=None,
    email=None,
    phone=None,
    address=None,
    date_of_birth=None,
    id_type=None,
    id_value=None,
    password=None,
    role=None,
    signup_method=None,
    organization: Organization = None,
):
    """
    :param role: The user's role
    :param organization: The organization the user belongs to
    :param signup_method: The channel through which teh user was signed up
    :param given_names: The collective first names the user identifies with
    :param surname: The user's surname
    :param email: The user's email address
    :param phone: The user's phone number
    :param address: The user's physical postal address
    :param date_of_birth: The user's date of birth
    :param id_type: The form of identification used by the user
    :param id_value: The value tied to that ID type
    :param password: Value of user's password
    :return:
    """

    # create user
    user = User(
        given_names=given_names,
        surname=surname,
        email=email,
        phone=phone,
        date_of_birth=date_of_birth,
        address=address,
        signup_method=signup_method,
    )

    user.is_activated = False

    # set identification information
    if id_value:
        user.set_identification_details(id_type=id_type, id_value=id_value)

    # hash password
    if password:
        user.hash_password(password=password)

    # unless special organization defined, default to master organization
    if not organization:
        organization = Organization.master_organisation()

    # bind user to organization
    user.bind_user_to_organization(organization)

    # set user role
    if role:
        user.set_role(role)
    # default to client role
    else:
        user.set_role("CLIENT")

    db.session.add(user)

    return user


def update_user(user, given_names=None, surname=None, address=None, date_of_birth=None):
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


def process_create_or_update_user_request(user_attributes, user_update_allowed=False):
    """
    :param user_update_allowed:
    :param user_attributes:
    :return:
    """
    # get user data
    given_names = user_attributes.get("given_names")
    surname = user_attributes.get("surname")
    email = user_attributes.get("email")
    phone = user_attributes.get("phone")
    address = user_attributes.get("address")
    date_of_birth = user_attributes.get("date_of_birth")
    id_type = user_attributes.get("id_type")
    id_value = user_attributes.get("id_value")
    password = user_attributes.get("password")
    signup_method = user_attributes.get("signup_method")
    public_identifier = user_attributes.get("public_identifier")
    role = user_attributes.get("role")
    user_id = user_attributes.get("user_id")

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
            "error": {
                "message": "User cannot be created without a parent organization."
                f"No organization found for public identifier: {public_identifier}.",
                "status": "Fail",
            }
        }

        return response, 403

    # process sign up methods
    if signup_method:
        if signup_method == "MOBILE":
            signup_method = SignupMethod.MOBILE_SIGNUP

        if signup_method == "WEB":
            signup_method = SignupMethod.WEB_SIGNUP

    if password and len(password) < 8:
        response = {
            "error": {
                "message": "Password must be at least 8 characters long.",
                "status": "Fail",
            }
        }
        return response, 422

    if role and role not in SUPPORTED_ROLES:
        response = {
            "error": {"message": "Unsupported role provided.", "status": "Fail"}
        }
        return response, 422

    # validate phone
    if not phone and signup_method == SignupMethod.MOBILE_SIGNUP:
        response = {
            "error": {"message": "Phone number cannot be empty.", "status": "Fail"}
        }
        return response, 422
    else:
        # check that id values are present
        if not (id_type, id_value):
            response = {
                "error": {"message": "ID data cannot be empty.", "status": "Fail"}
            }
            return response, 422

        # process phone number and ensure phone number validity
        try:
            phone = process_phone_number(phone)
        except NumberParseException as exception:
            response = {
                "error": {
                    "message": f"Invalid phone number. ERROR: {exception}",
                    "status": "Fail",
                }
            }
            return response, 422

        # check if user is already existent
        existing_user = get_user_from_unique_attribute(
            email=email, user_id=user_id, phone=phone
        )

        # check if request is an update request
        if existing_user and not user_update_allowed:
            response = {
                "error": {
                    "message": "User already exists. Please Log in.",
                    "status": "Fail",
                }
            }
            return response, 403

        # process update request
        if existing_user and user_update_allowed:
            try:
                user = update_user(
                    user_attributes,
                    given_names=given_names,
                    surname=surname,
                    address=address,
                    date_of_birth=date_of_birth,
                )

                response = {
                    "data": {"user": user_schema.dump(user).data},
                    "message": "User successfully updated.",
                    "status": "Success",
                }

                return response, 200

            except Exception as exception:
                response = {"error": {"message": f"{exception}", "status": "Fail"}}
                return response, 400

        # create user
        user = create_user(
            given_names=given_names,
            surname=surname,
            email=email,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
            password=password,
            id_type=id_type,
            id_value=id_value,
            role=role,
            signup_method=signup_method,
        )
        db.session.flush()

        # send user OTP to validate user's phone number
        if signup_method == SignupMethod.MOBILE_SIGNUP:
            send_one_time_pin(user=user)
            response = {
                "message": "User created. Please verify phone number.",
                "status": "Success",
            }
            return response, 200

        # send email for user to validate their email as admin
        if user.role.name == "ADMIN" and signup_method == SignupMethod.WEB_SIGNUP:
            mailer_is_configured = check_mailer_configured(organization)
            if not mailer_is_configured:
                response, status_code = mailer_not_configured()
                return response, status_code

            mailer = Mailer(organization)
            activation_token = user.encode_single_use_jws(token_type="user_activation")
            mailer.send_template_email(
                mail_type="user_activation",
                token=activation_token,
                email=user.email,
                given_names=user.given_names,
            )

            response = {
                "message": "User created. Please check your email to verify your account.",
                "status": "Success",
            }
            return response, 200
