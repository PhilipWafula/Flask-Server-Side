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

    users = db.relationship('User', backref='organization')

    @staticmethod
    def master_organisation() -> "Organization":
        return Organization.query.filter_by(is_master=True).first()
