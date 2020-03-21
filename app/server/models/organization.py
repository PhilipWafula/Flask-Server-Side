from app.server import db
from app.server.utils.models import BaseModel


class Organization(BaseModel):
    """
    Creates an organization
    """
    __tablename__ = 'organizations'

    name = db.Column(db.String(100))
    configuration = db.relationship('Configurations', uselist=False, back_populates='organizations')
    users = db.relationship('User', backref='organizations')
