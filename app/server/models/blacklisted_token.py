from datetime import datetime

from app.server import db
from app.server.utils.models import BaseModel


class BlacklistedToken(BaseModel):
    """
    Create a blacklisted token
    """
    __tablename__ = 'blacklisted_tokens'

    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def check_if_blacklisted(token):
        # check whether token has been blacklisted
        result = BlacklistedToken.query.filter_by(token=str(token)).first()
        if result:
            return True
        else:
            return False

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.now()

    def __repr__(self):
        return f'<id: token: {self.token}'
