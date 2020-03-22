from app.server import db
from app.server.utils.models import BaseModel


class Organization(BaseModel):
    """
    Creates an organization
    """
    __tablename__ = 'organizations'

    name = db.Column(db.String(100))
    configurations = db.relationship('Configuration', uselist=False, back_populates='organization')
    users = db.relationship('User', backref='organization')
