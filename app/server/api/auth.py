from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app.server import db
from app.server.models.blacklisted_token import BlacklistedToken
from app.server.models.user import User
from app.server.schemas.user import user_schema
from app.server.utils.user import process_create_or_update_user_request

auth_blueprint = Blueprint('auth', __name__)


class RegisterAPI(MethodView):
    """
    Create user
    """

    def post(self):
        # get registration data
        user_data = request.get_json()

        response, status_code = process_create_or_update_user_request(user_attributes=user_data)
        if status_code == 200:
            db.session.commit()
            status_code = 201

        return make_response(jsonify(response), status_code)


class VerifyOneTimePasswordAPI(MethodView):
    """
    Verify OTP
    """

    def post(self):
        otp_data = request.get_json()

        msisdn = otp_data.get('msisdn')
        otp_token = otp_data.get('otp')
        otp_expiry_interval = otp_data.get('otp_expiry_interval')

        if not msisdn:
            response = {
                'error': {
                    'message': 'No phone number provided.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        if not otp_token:
            response = {
                'error': {
                    'message': 'No OTP token provided.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        if not otp_expiry_interval:
            response = {
                'error': {
                    'message': 'No OTP expiry interval provided.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        if not isinstance(otp_token, str):
            response = {
                'error': {
                        'message': 'OTP must be a 6 digit numeric string',
                        'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 400)

        user = User.query.filter_by(msisdn=msisdn).first()

        if user:
            is_valid_otp = user.verify_otp(one_time_password=otp_token,
                                           expiry_interval=otp_expiry_interval)

            if is_valid_otp:
                # activated user
                user.is_activated = True

                # create authentication token
                auth_token = user.encode_auth_token()

                if auth_token:

                    db.session.commit()

                    response = {
                        'authentication_token': auth_token.decode(),
                        'message': 'User successfully activated.',
                        'status': 'Success'}

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
                'message': 'No user found for phone number {}.'.format(msisdn),
                'status': 'Fail'
            }
        }
        return make_response(jsonify(response)), 400


class LoginAPI(MethodView):
    """
    Login user
    """

    def post(self):
        login_data = request.get_json()

        email = login_data.get('email')
        msisdn = login_data.get('msisdn')
        password = login_data.get('password')

        user = None

        if email:
            user = User.query.filter_by(email=email).first()

        if msisdn:
            user = User.query.filter_by(msisdn=msisdn).first()

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
                'data': {'user': user_schema.dump(user).data},
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

                    response = {'message': 'Successfully logged out.',
                                'status': 'Success'}
                    return make_response(jsonify(response)), 200

                except Exception as exception:
                    response = {'error': {'message': 'System error: {}.'.format(exception),
                                          'status': 'Fail'}}
                    return make_response(jsonify(response)), 500
            else:
                response = {'error': {'message': decoded_auth_token},
                            'status': 'Fail'}
                return make_response(jsonify(response)), 401

        else:
            response = {'error': {'message': 'Provide a valid auth token.',
                                  'status': 'Fail'}}
            return make_response(jsonify(response)), 403


auth_blueprint.add_url_rule(
    '/auth/register/',
    view_func=RegisterAPI.as_view('register_api'),
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/verify_otp/',
    view_func=VerifyOneTimePasswordAPI.as_view('verify_otp_api'),
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/login/',
    view_func=LoginAPI.as_view('login_api'),
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/logout/',
    view_func=LogoutAPI.as_view('logout_api'),
    methods=['POST']
)
