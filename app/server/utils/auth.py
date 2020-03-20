from flask import jsonify
from flask import make_response
from flask import request
from functools import partial
from functools import wraps

from app.server.models.user import User


def requires_auth(function=None):
    # returns a partial function that could take more arguments
    # implemented like this to keep this extensible but closed for modification.
    if function is None:
        return partial(requires_auth)

    @wraps(function)
    def wrapper(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        auth_header = request.headers.get('Authorization')

        if auth_header:
            # get auth token
            auth_token = auth_header.split(' ')[1]

            if auth_token:
                # decode authentication token
                decoded_user_data = User.decode_auth_token(auth_token)

                if not isinstance(decoded_user_data, str):

                    user = User.query.filter_by(id=decoded_user_data['id']).execution_options(show_all=True).first()

                    if not user:
                        response = {'error': {'message': 'User not found.'}}
                        return make_response(jsonify(response), 401)

                    if not user.is_activated:
                        response = {'error': {'message': 'User not activated.'}}
                        return make_response(jsonify(response), 401)

                    return function(*args, **kwargs)

                response = {'error': {'message': decoded_user_data}}
                return make_response(jsonify(response), 401)

            response = {'error': {'message': 'Provide a valid auth token.'}}
            return make_response(jsonify(response), 401)

    return wrapper
