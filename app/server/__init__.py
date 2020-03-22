import africastalking
import os

from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

from app import config
from app.server.utils.celery import init_celery

PACKAGE_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
fernet_key = Fernet(str(config.SECRET_KEY))


def create_app(app_name=PACKAGE_NAME, **kwargs):
    # define app
    app = Flask(app_name)

    # define config file
    app.config.from_object(config)

    # register extensions
    register_extensions(app)

    # register blueprints
    register_blueprints(app)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    return app


def make_celery(app_name=__name__):
    return Celery(app_name,
                  backend=config.REDIS_URL,
                  broker=config.REDIS_URL)


def register_blueprints(application):
    url_version = '/api/v1'
    from app.server.api.auth import auth_blueprint
    from app.server.api.organization import organization_blueprint
    application.register_blueprint(auth_blueprint, url_prefix=url_version)
    application.register_blueprint(organization_blueprint, url_prefix=url_version)


def register_extensions(app):
    db.init_app(app)


def fernet_encrypt(secret):
    # covert secret to bytes
    b_secret = bytes(secret, encoding='utf-8')
    token = fernet_key.encrypt(b_secret)
    return token


def fernet_decrypt(token):
    secret = fernet_key.decrypt(token)
    return secret


# create instance of celery app
celery = make_celery()

# define db
db = SQLAlchemy()

# africa's talking sms client
africastalking.initialize(username=config.AFRICASTALKING_USERNAME,
                          api_key=config.AFRICASTALKING_API_KEY)

sms = africastalking.SMS
