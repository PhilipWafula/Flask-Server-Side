from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask.views import MethodView

from app.server.models.user import User
from app.server.utils.query import paginate_query
from app.server.schemas.user import user_schema
from app.server.schemas.user import users_schema
from app.server.templates.responses import user_not_found

user_blueprint = Blueprint('user', __name__)


def get_organization_by_id(user_id):
    user = User.query.execution_options(show_all=True).get(user_id)
    return user


class UsersAPI(MethodView):
    def get(self, user_id):
        if user_id:
            user = User.query.execution_options(show_all=True).get(user_id)

            if not user:
                response, status_code = user_not_found(user_id=user_id)
                return make_response(jsonify(response), status_code)

            response = {
                'data': {'user': user_schema.dump(user).data},
                'message': 'Successfully loaded user data.',
                'status': 'Success'}
            return make_response(jsonify(response), 200)

        else:
            users_query = User.query.execution_options(show_all=True)

            users, total_items, total_pages = paginate_query(users_query, User)

            if not users:
                response = {
                    'error':
                        {
                            'message': 'No users were found.',
                            'status': 'Fail'
                        }}
                return make_response(jsonify(response), 404)

            response = {
                'data': {'users': users_schema.dump(users).data},
                'items': total_items,
                'message': 'Successfully loaded all users.',
                'pages': total_pages,
                'status': 'Success'
            }
            return make_response(jsonify(response), 200)


user_blueprint.add_url_rule(
    '/users/',
    view_func=UsersAPI.as_view('users_api'),
    methods=['GET'],
    defaults={'user_id': None})
