from flask_migrate import Manager
from flask_migrate import Migrate, MigrateCommand

from app.server import create_app
from app.server import db
from app.server import models

app = create_app()
migrate = Migrate(app=app, db=db)

manager = Manager(app=app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

