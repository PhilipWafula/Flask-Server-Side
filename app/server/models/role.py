from app.server import db
from app.server.utils.models import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = db.Column(db.String)
    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return "<Role %r" % self.name
