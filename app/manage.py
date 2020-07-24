import os
from flask_migrate import Manager
from flask_migrate import Migrate, MigrateCommand

from app.server import create_app
from app.server import db
from app.server import models

MIGRATION_DIR = os.path.join("migrations")

app = create_app()
migrate = Migrate(app=app, db=db, directory=MIGRATION_DIR)

manager = Manager(app=app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
