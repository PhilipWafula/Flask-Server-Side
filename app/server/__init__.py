import africastalking
import logging
import os

from cryptography.fernet import Fernet
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from app import config

fernet_key = Fernet(config.SECRET_KEY)


def boilerplate_app():
    # define app
    app = Flask(__name__, instance_relative_config=True)

    # define config file
    app.config.from_object(config)

    # define base directory
    app.config["BASEDIR"] = os.path.abspath(os.path.dirname(__file__))

    # register extensions
    register_extensions(app)

    return app


def create_app():
    app = boilerplate_app()

    # register blueprints
    register_blueprints(app)

    return app


def register_blueprints(application):
    url_version = "/api/v1"
    from app.server.api.auth import auth_blueprint
    from app.server.api.organization import organization_blueprint
    from app.server.api.user import user_blueprint

    application.register_blueprint(auth_blueprint, url_prefix=url_version)
    application.register_blueprint(organization_blueprint, url_prefix=url_version)
    application.register_blueprint(user_blueprint, url_prefix=url_version)


def register_extensions(app):
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.before_request
    def before_request():
        if request.method == "POST":
            # check for json data
            json_data = request.get_json()
            if not json_data:
                response = {
                    "error": {
                        "message": "Invalid request format. Please provide a valid JSON body.",
                        "status": "Fail",
                    }
                }
                return make_response(jsonify(response), 403)

    db.init_app(app)
    mailer.init_app(app)


def fernet_encrypt(secret):
    # covert secret to bytes
    b_secret = bytes(secret, encoding="utf-8")
    token = fernet_key.encrypt(b_secret)
    return token


def fernet_decrypt(token):
    secret = fernet_key.decrypt(token)
    return secret


# define db
db = SQLAlchemy(session_options={"expire_on_commit": not config.IS_TEST})

# africa's talking sms client
africastalking.initialize(
    username=config.AFRICASTALKING_USERNAME, api_key=config.AFRICASTALKING_API_KEY
)

sms = africastalking.SMS

# initialize mailer
mailer = Mail()

# application logger defaults to DEBUG
logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger(__name__)


class ContextEnvironment:
    def __init__(self, app):
        self.deployment_name = app.config["DEPLOYMENT_NAME"]

    def is_development(self):
        return self.deployment_name == "development"

    def is_production(self):
        return self.deployment_name == "production"

    def is_testing(self):
        return self.deployment_name == "testing"
