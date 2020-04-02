#!flask/bin/python
import os

from app import config
from app.server import create_app

os.environ['RUNNING_ENV'] = "DEVELOPMENT"

app = create_app()
app.run(debug=True,
        host=config.APP_HOST,
        port=config.APP_PORT,
        threaded=True)
