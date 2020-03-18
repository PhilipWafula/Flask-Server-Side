from sqlalchemy.dialects.postgresql import JSONB

from app.server import db
from app.server.utils.models import BaseModel


class User(BaseModel):
    """
    Creates user object
    """
    __tablename__ = 'users'

    given_names = db.Column(db.String(length=35), nullable=False)
    surname = db.Column(db.String(length=35), nullable=False)

    identification = db.Column(JSONB)
    email = db.Column(db.String)
    msisdn = db.Column(db.String(length=13), index=True, nullable=False, unique=True)
    address = db.Column(db.String)

    date_of_birth = db.Column(db.Date)
