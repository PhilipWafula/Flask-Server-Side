import bcrypt

from cryptography.fernet import Fernet
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified

from app import config
from app.server import db
from app.server.constants import IDENTIFICATION_TYPES
from app.server.exceptions import IdentificationTypeNotFound
from app.server.utils.models import BaseModel


class User(BaseModel):
    """
    Creates user object
    """
    __tablename__ = 'users'

    given_names = db.Column(db.String(length=35), nullable=False)
    surname = db.Column(db.String(length=35), nullable=False)

    _identification = db.Column(JSONB, default={})
    email = db.Column(db.String)
    msisdn = db.Column(db.String(length=13), index=True, nullable=False, unique=True)
    address = db.Column(db.String)

    date_of_birth = db.Column(db.Date)

    password_hash = db.Column(db.String(200))

    @hybrid_property
    def identification(self):
        return self._identification

    def set_identification_details(self, id_type: str, id_value: str):
        # check if id type is in identification types
        if id_type not in IDENTIFICATION_TYPES:
            raise IdentificationTypeNotFound('Identification type {} not valid'.format(id_type))

        # check that id value is supplied
        if id_value is None:
            raise ValueError('ID cannot be empty')

        # corrective method in case identification is set to none
        if self._identification is None:
            self._identification = {}

        # set values
        self._identification[id_type] = id_value
        flag_modified(self, '_identification')

    @staticmethod
    def salt_hash_secret(password):
        fernet_key = Fernet(config.PASSWORD_PEPPER)
        return fernet_key.encrypt(bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()

    @staticmethod
    def check_salt_hashed_secret(password, hashed_password):
        fernet_key = Fernet(config.PASSWORD_PEPPER)
        hashed_password = fernet_key.decrypt(hashed_password.encode())
        return bcrypt.checkpw(password.encode(), hashed_password)

    def hash_password(self, password):
        self.password_hash = self.salt_hash_secret(password)

    def verify_password(self, password):
        return self.check_salt_hashed_secret(password, self.password_hash)
