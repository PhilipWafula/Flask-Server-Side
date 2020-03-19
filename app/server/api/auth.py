from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app.server import db
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


auth_blueprint.add_url_rule(
    '/auth/register/',
    view_func=RegisterAPI.as_view('register_api'),
    methods=['POST']
)
