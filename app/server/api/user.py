from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView

from app.server import db
from app.server.models.user import User
from app.server.utils.auth import requires_auth
from app.server.utils.query import paginate_query
from app.server.utils.user import process_create_or_update_user_request, get_user_role_from_auth_token
from app.server.schemas.user import user_schema, users_schema
from app.server.templates.responses import user_not_found, user_id_not_provided

user_blueprint = Blueprint('user', __name__)


def get_organization_by_id(user_id):
    user = User.query.execution_options(show_all=True).get(user_id)
    return user


class UserAPI(MethodView):
    @requires_auth(authenticated_roles=['ADMIN', 'CLIENT'])
    def get(self, user_id):
        if user_id:
            user = User.query.execution_options(show_all=True).get(user_id)

            if not user:
                response, status_code = user_not_found(user_id=user_id)
                return make_response(jsonify(response), status_code)

            response = {
                'data': {
                    'user': user_schema.dump(user).data
                },
                'message': 'Successfully loaded user data.',
                'status': 'Success'}
            return make_response(jsonify(response), 200)

        else:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(' ')[1]
            user_role = get_user_role_from_auth_token(auth_token)
            if user_role != 'ADMIN':
                response = {
                    'error': {
                        'message': 'User not authorized to access this resource.',
                        'status': 'Fail'
                    }
                }
                return make_response(jsonify(response), 401)
            users_query = User.query.execution_options(show_all=True)

            users, total_items, total_pages = paginate_query(users_query, User)

            if not users:
                response = {
                    'error': {
                            'message': 'No users were found.',
                            'status': 'Fail'
                    }
                }
                return make_response(jsonify(response), 404)

            response = {
                'data': {
                    'users': users_schema.dump(users).data
                },
                'items': total_items,
                'message': 'Successfully loaded all users.',
                'pages': total_pages,
                'status': 'Success'
            }
            return make_response(jsonify(response), 200)

    @requires_auth(authenticated_roles=['ADMIN', 'CLIENT'])
    def put(self, user_id: int):
        user_data = request.get_json()

        if user_id:
            user_data['user_id'] = user_id
            response, status_code = process_create_or_update_user_request(user_attributes=user_data,
                                                                          user_update_allowed=True)
            if status_code == 200:
                db.session.commit()

            return make_response(jsonify(response), status_code)

        response, status_code = user_id_not_provided()
        return make_response(jsonify(response), status_code)

    # TODO: [Philip] Decide on whether to actually purge data from the DB when a user deletes an account
    def delete(self, user_id: int):
        if user_id:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                response = {
                    'message': 'Successfully deleted user',
                    'status': 'Fail'
                }
                return make_response(jsonify(response), 200)
            response, status_code = user_not_found(user_id)
            return make_response(jsonify(response), status_code)
        response, status_code = user_id_not_provided()
        return make_response(jsonify(response), status_code)


users_view = UserAPI.as_view('users_api')
single_user_view = UserAPI.as_view('single_user_view')

user_blueprint.add_url_rule('/user/',
                            view_func=users_view,
                            methods=['GET'],
                            defaults={'user_id': None})

user_blueprint.add_url_rule('/user/<int:user_id>/',
                            view_func=single_user_view,
                            methods=['GET', 'DELETE', 'PUT'])
