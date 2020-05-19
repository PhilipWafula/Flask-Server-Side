from flask import jsonify
from flask import make_response
from flask import request
from functools import partial
from functools import wraps
from typing import List
from typing import Optional

from app.server.models.user import User


def requires_auth(function=None,
                  authenticated_roles: Optional[List] = None):
    # returns a partial function that could take more arguments
    # implemented like this to keep this extensible but closed for modification.
    if function is None:
        return partial(requires_auth,
                       authenticated_roles=authenticated_roles)

    @wraps(function)
    def wrapper(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        auth_header = request.headers.get('Authorization')

        if auth_header:
            auth_token = auth_header.split(' ')[1]
        else:
            auth_token = ''

        if auth_token:
            # decode authentication token
            decoded_user_data = User.decode_auth_token(auth_token)

            if not isinstance(decoded_user_data, str):

                user = User.query.filter_by(id=decoded_user_data['id']).execution_options(show_all=True).first()

                if not user:
                    response = {
                        'error':
                            {
                                'message': 'User not found.',
                                'status': 'Fail'
                            }
                    }
                    return make_response(jsonify(response), 401)

                if not user.is_activated:
                    response = {
                        'error':
                            {
                                'message': 'User not activated.',
                                'status': 'Fail'
                            }
                    }
                    return make_response(jsonify(response), 401)

                # get user role
                user_role = decoded_user_data.get('role', None)

                if len(authenticated_roles) > 0:
                    # check if user's role matches any of the required roles
                    if user_role not in authenticated_roles:
                        response = {
                            'error': {
                                'message': 'User\'s is not authorized to access this role.',
                                'status': 'Fail'
                            }
                        }
                        return make_response(jsonify(response), 401)

                return function(*args, **kwargs)

            # if returned decoded data is a message.
            response = {
                'error':
                    {
                        'message': decoded_user_data,
                        'status': 'Fail'
                    }
            }
            return make_response(jsonify(response), 401)

        # if no valid authentication is provided.
        response = {
            'error':
                {
                    'message': 'Provide a valid authentication token.',
                    'status': 'Fail'
                }
        }
        return make_response(jsonify(response), 401)

    return wrapper
