from factory.alchemy import SQLAlchemyModelFactory
from app.server import db
from app.server.models.user import User


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
