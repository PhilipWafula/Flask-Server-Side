from app.server import db
from app.server.utils.enums.access_control_enums import AccessControlType
from app.server.utils.models import BaseModel


class Configuration(BaseModel):
    """
    Creates system configuration table
    """
    __tablename__ = 'configurations'
    access_control_type = db.Column(db.Enum(AccessControlType))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organizations', back_populates='configurations')
