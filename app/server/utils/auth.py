from flask import jsonify
from flask import make_response
from flask import request
from functools import partial
from functools import wraps
from typing import List
from typing import Optional

from app.server.models.user import User
from app.server.utils.access_control import AccessControl


def requires_auth(function=None,
                  authenticated_roles: Optional[List] = None):
    processed_authenticated_roles = []

    # process authenticated roles list
    if authenticated_roles:
        for role_item in authenticated_roles:
            if isinstance(role_item, str):
                role_item = {role_item: 'STANDARD'}

            role_item = role_item or {}

            processed_authenticated_roles.append(role_item)

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
                    response = {'error': {'message': 'User not found.',
                                          'status': 'Fail'}}
                    return make_response(jsonify(response), 401)

                if not user.is_activated:
                    response = {'error': {'message': 'User not activated.',
                                          'status': 'Fail'}}
                    return make_response(jsonify(response), 401)

                if len(authenticated_roles) > 0:
                    # get user role
                    user_role_dict = decoded_user_data.get('role', {})

                    # get access control
                    access_control = AccessControl(user=user)

                    # check if user has standard access control
                    has_standard_access_control = access_control.has_standard_access_control_type()

                    # check if user has tiered access control
                    has_tiered_access_control = access_control.has_tiered_access_control_type()

                    # check if user has required role
                    has_required_role = False
                    for required_role in processed_authenticated_roles:
                        has_required_role = access_control.has_required_role(user_role_dict, required_role)

                    for (role, tier) in user_role_dict.items():

                        # check if user has required tier
                        has_required_tier = access_control.has_required_tier(user_role_dict, tier)

                        if has_tiered_access_control and not has_required_tier:
                            response = {
                                'error':
                                    {'message': 'User does not have any of the roles or tiers in {}'
                                        .format(user_role_dict),
                                     'status': 'Fail'}}

                            return make_response(jsonify(response), 401)

                    if has_standard_access_control and not has_required_role:
                        response = {
                            'error':
                                {'message': 'User does not have any of the roles {}'.format(user_role_dict),
                                 'status': 'Fail'}}
                        return make_response(jsonify(response), 401)

                return function(*args, **kwargs)

            response = {'error': {'message': decoded_user_data,
                                  'status': 'Fail'}}
            return make_response(jsonify(response), 401)

        response = {'error': {'message': 'Provide a valid authentication token.',
                              'status': 'Fail'}}
        return make_response(jsonify(response), 401)

    return wrapper
