import pyotp
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView
from jsonschema.exceptions import ValidationError

from app.server import db
from app.server.models.blacklisted_token import BlacklistedToken
from app.server.models.user import User
from app.server.schemas.json.otp_verification import otp_verification_json_schema
from app.server.schemas.json.reset_password import reset_password_json_schema
from app.server.schemas.user import user_schema
from app.server.templates.responses import invalid_request_on_validation, mailer_not_configured, otp_resent_successfully
from app.server.utils.mailer import check_mailer_configured
from app.server.utils.mailer import Mailer
from app.server.utils.messaging import send_sms, send_one_time_pin
from app.server.utils.user import process_create_or_update_user_request
from app.server.utils.validation import validate_request

auth_blueprint = Blueprint('auth', __name__)


class RegisterAPI(MethodView):
    """
    Create user
    """
    def post(self):
        user_data = request.get_json()

        response, status_code = process_create_or_update_user_request(user_attributes=user_data)
        if status_code == 200:
            db.session.commit()
            status_code = 201

        return make_response(jsonify(response), status_code)


class ActivateUserAPI(MethodView):
    """
    Activate users
    """

    def post(self):
        activate_user_data = request.get_json()

        activation_token = activate_user_data.get('activation_token', None)

        if not activation_token:
            response = {
                'error': {
                    'message': 'Activation token is required.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 401)

        decoded_token_response = User.decode_single_use_jws(token=activation_token,
                                                            required_token_type='user_activation')

        is_valid_token = decoded_token_response.get('status') == 'Success'
        if not is_valid_token:
            response = {
                'error': {
                    'message': decoded_token_response.get('message'),
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 401)

        user: User = decoded_token_response.get('user', None)
        is_already_activated = user.is_activated

        if is_already_activated:
            response = {
                'error': {
                    'message': 'User is already activated. Please login.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 403)

        user.is_activated = True
        authentication_token = user.encode_auth_token()
        db.session.commit()

        response = {
            'authentication_token': authentication_token.decode(),
            'data': {
                'user': user_schema.dump(user).data
            },
            'message': 'User successfully activated.',
            'status': 'Success'
        }
        return make_response(jsonify(response), 200)


class VerifyOneTimePasswordAPI(MethodView):
    """
    Verify OTP
    """

    def post(self):
        otp_data = request.get_json()

        phone = otp_data.get('phone')
        otp_token = otp_data.get('otp')
        otp_expiry_interval = otp_data.get('otp_expiry_interval')

        # validate request
        try:
            validate_request(instance=otp_data, schema=otp_verification_json_schema)

        except ValidationError as error:
            response, status_code = invalid_request_on_validation(error.message)
            return response, status_code

        if not isinstance(otp_token, str):
            response = {
                'error': {
                    'message': 'OTP must be a 6 digit numeric string',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        user = User.query.filter_by(phone=phone).first()

        if user:
            is_valid_otp = user.verify_otp(one_time_password=otp_token,
                                           expiry_interval=otp_expiry_interval)

            if is_valid_otp:
                # activated user
                user.is_activated = True

                # create authentication token
                authentication_token = user.encode_auth_token()
                db.session.commit()

                response = {
                    'authentication_token': authentication_token.decode('utf-8'),
                    'data': {
                        'user': user_schema.dump(user).data
                    },
                    'message': 'User successfully activated.',
                    'status': 'Success'
                }
                return make_response(jsonify(response), 200)

            response = {
                'error': {
                    'message': 'Invalid OTP provided.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        response = {
            'error': {
                'message': 'No user found for phone number {}.'.format(phone),
                'status': 'Fail'
            }
        }
        return make_response(jsonify(response), 400)


class ResendOneTimePasswordAPI(MethodView):
    """
    Request OTP to be resent
    """

    def post(self):
        resend_otp_data = request.get_json()
        phone = resend_otp_data.get('phone')
        user = User.query.filter_by(phone=phone).first()
        otp_secret = user.get_otp_secret()

        # check if use is always activated
        if user.is_activated:
            response = {
                'error': {
                    'message': 'User is already activated, please log in.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        # get old OTP
        old_otp = pyotp.TOTP(otp_secret, interval=3600).now()

        # check if old OTP is expired
        is_valid_otp = user.verify_otp(one_time_password=old_otp, expiry_interval=3600)
        if is_valid_otp:
            message = f'Hello {user.given_names}, your activation code is: {old_otp}'
            send_sms(message=message, phone_number=phone)
        else:
            # generate new OTP
            send_one_time_pin(user)

        response, status_code = otp_resent_successfully()
        return make_response(jsonify(response), status_code)


class LoginAPI(MethodView):
    """
    Login user
    """

    def post(self):
        login_data = request.get_json()

        email = login_data.get('email')
        phone = login_data.get('phone')
        password = login_data.get('password')

        user = None

        if email:
            user = User.query.filter_by(email=email).first()

        if phone:
            user = User.query.filter_by(phone=phone).first()

        if user:
            if not user.verify_password(password):
                response = {
                    'error': {
                        'message': 'Invalid phone number or password.',
                        'status': 'Fail'
                    }
                }
                return response, 401

            if not user.is_activated:
                response = {
                    'error': {
                        'message': 'Account has not been activated. Please verify your phone number or email.',
                        'status': 'Fail'
                    }
                }
                return response, 403

            auth_token = user.encode_auth_token()

            if not auth_token:
                response = {
                    'error': {
                        'message': 'Invalid credentials, phone number, email or password',
                        'status': 'Fail'
                    }
                }
                return response, 401

            response = {
                'authentication_token': auth_token.decode(),
                'data': {
                    'user': user_schema.dump(user).data
                },
                'message': 'Successfully logged in.',
                'status': 'Success'
            }
            return response, 200

        response = {
            'error': {
                'message': 'Invalid credentials, phone number, email or password',
                'status': 'Fail'
            }
        }
        return response, 401


class LogoutAPI(MethodView):
    """
    Logout out
    """

    def post(self):

        logout_instruction = request.get_json()

        action = logout_instruction.get('action', None)

        if not action or action != 'logout':
            response = {
                'error': {
                    'message': 'Invalid action provided for logout.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        # get auth token
        auth_header = request.headers.get('Authorization')

        # get auth token
        if auth_header:
            auth_token = auth_header.split(' ')[1]
        else:
            auth_token = ''

        if auth_token:
            decoded_auth_token = User.decode_auth_token(auth_token)
            if not isinstance(decoded_auth_token, str):

                # mark the token as blacklisted
                blacklist_token = BlacklistedToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()

                    response = {
                        'message': 'Successfully logged out.',
                        'status': 'Success'
                    }
                    return make_response(jsonify(response)), 200

                except Exception as exception:
                    response = {
                        'error': {
                            'message': f'System error: {exception}.',
                            'status': 'Fail'
                        }
                    }
                    return make_response(jsonify(response)), 500
            else:
                response = {
                    'error': {
                        'message': decoded_auth_token,
                        'status': 'Fail'
                    }
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'error': {
                    'message': 'Provide a valid auth token.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response)), 403


class RequestPasswordResetEmailAPI(MethodView):
    def post(self):
        request_password_reset_data = request.get_json()
        email = request_password_reset_data.get('email')

        if not email:
            response = {
                'error': {
                    'message': 'No email was provided.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        user = User.query.filter_by(email=email).first()
        if not user:
            response = {
                'error': {
                    'message': 'No user with that email was found.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 403)

        password_reset_token = user.encode_single_use_jws(token_type='reset_password')
        organization = user.parent_organization
        given_names = user.given_names

        mailer_is_configured = check_mailer_configured(organization)

        if not mailer_is_configured:
            response, status_code = mailer_not_configured()
            return make_response(jsonify(response), status_code)

        user.save_password_reset_token(password_reset_token)
        db.session.commit()

        mailer = Mailer(organization=organization)
        mailer.send_template_email(mail_type='reset_password',
                                   email=email,
                                   given_names=given_names,
                                   token=password_reset_token)

        response = {
            'message': 'A password reset email has been sent, please check your email for instructions.',
            'status': 'Success'
        }
        return make_response(jsonify(response), 200)


class ResetPasswordAPI(MethodView):
    def post(self):
        reset_password_data = request.get_json()

        # attempt validation
        validate_request(instance=reset_password_data, schema=reset_password_json_schema)
        new_password = reset_password_data.get('new_password', None)
        password_reset_token = reset_password_data.get('password_reset_token', None)

        if new_password and len(new_password) < 8:
            response = {
                'error': {
                    'message': 'Password must be at least 8 characters long.',
                    'status': 'Fail'
                }
            }
            return response, 422

        decoded_token_response = User.decode_single_use_jws(token=password_reset_token,
                                                            required_token_type='reset_password')

        is_valid_token = decoded_token_response['status'] == 'Success'
        if not is_valid_token:
            response = {
                'error': {
                    'message': decoded_token_response['message'],
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 401)

        user: User = decoded_token_response.get('user', None)

        is_used_token = user.check_is_used_password_reset_token(password_reset_token=password_reset_token)
        if is_used_token:
            response = {
                'error': {
                    'message': 'This token has already been used.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 401)

        user.hash_password(new_password)
        user.remove_all_password_reset_tokens()
        db.session.commit()

        response = {
            'message': 'Password successfully changed. Please log in.',
            'status': 'Success'
        }
        return make_response(jsonify(response), 200)


register_api_view = RegisterAPI.as_view('register_api')
activate_user_api_view = ActivateUserAPI.as_view('activate_user_api')
verify_otp_api_view = VerifyOneTimePasswordAPI.as_view('verify_otp_api')
login_api_view = LoginAPI.as_view('login_api')
logout_api_view = LogoutAPI.as_view('logout_api')
resend_otp_api_view = ResendOneTimePasswordAPI.as_view('resend_otp_api')
request_password_reset_email_api_view = RequestPasswordResetEmailAPI.as_view('request_password_reset_email_api')
reset_password_api_view = ResetPasswordAPI.as_view('reset_password_api')

auth_blueprint.add_url_rule(
    '/auth/register/',
    view_func=register_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/activate_user/',
    view_func=activate_user_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/verify_otp/',
    view_func=verify_otp_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/resend_otp/',
    view_func=resend_otp_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/login/',
    view_func=login_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/logout/',
    view_func=logout_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/request_password_reset_email/',
    view_func=request_password_reset_email_api_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/reset_password/',
    view_func=reset_password_api_view,
    methods=['POST']
)
