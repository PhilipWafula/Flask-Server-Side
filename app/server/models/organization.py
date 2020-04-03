import random
import string

from app.server import db
from app.server.utils.models import BaseModel


class Organization(BaseModel):
    """
    Creates an organization
    """
    __tablename__ = 'organizations'

    name = db.Column(db.String(100))
    configuration = db.relationship('Configuration', uselist=False, back_populates='organization')
    is_master = db.Column(db.Boolean, default=False, index=True)
    public_identifier = db.Column(db.String(8), nullable=False, index=True, unique=True)

    users = db.relationship('User', backref='organization')

    @staticmethod
    def master_organisation() -> "Organization":
        return Organization.query.filter_by(is_master=True).first()

    def set_public_identifier(self):
        components = string.ascii_letters + string.digits
        identifier = ''.join(random.choice(components) for i in range(8))
        self.public_identifier = identifier
