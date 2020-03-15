#!flask/bin/python
import os

from app import server
from app.server import create_app
from app import config

os.environ['RUNNING_ENV'] = "DEVELOPMENT"

app = create_app(celery=server.celery)

app.run(debug=True,
        host=config.APP_HOST,
        port=config.APP_PORT,
        threaded=True)
