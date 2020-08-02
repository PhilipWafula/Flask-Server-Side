# application imports
from app.server import boilerplate_app
from worker.celery import make_celery

app = boilerplate_app()
celery = make_celery(app=app)
