import os

from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import config
from app.server.utils.celery_utils import init_celery

PACKAGE_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]


def create_app(app_name=PACKAGE_NAME, **kwargs):
    # define app
    app = Flask(app_name)

    # define config file
    app.config.from_object(config)

    # register extensions
    register_extensions(app)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    return app


def make_celery(app_name=__name__):
    return Celery(app_name,
                  backend=config.REDIS_URL,
                  broker=config.REDIS_URL)


def register_extensions(app):
    db.init_app(app)


# create instance of celery app
celery = make_celery()

# define db
db = SQLAlchemy()
