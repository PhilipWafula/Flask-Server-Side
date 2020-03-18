import bcrypt
import jwt

from cryptography.fernet import Fernet
from datetime import datetime
from datetime import timedelta
from flask import current_app
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified

from app import config
from app.server import db
from app.server.constants import IDENTIFICATION_TYPES
from app.server.exceptions import IdentificationTypeNotFound
from app.server.models.blacklisted_token import BlacklistedToken
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
        """
        :param id_type: ID type of user [app/server/constants]
        :param id_value: ID value.
        :return: JSON object with id details eg: {'NATIONAL_ID': '12345678'}.
        """
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
    def salt_hash_secret(password: str):
        """
        :param password: user password.
        :return: encrypted password with system password pepper.
        """
        fernet_key = Fernet(config.PASSWORD_PEPPER)
        return fernet_key.encrypt(bcrypt.hashpw(password.encode(), bcrypt.gensalt())).decode()

    @staticmethod
    def check_salt_hashed_secret(password, hashed_password):
        """
        :param password: provided user password.
        :param hashed_password: hashed password stored in db.
        :return: boolean if password matches.
        """
        fernet_key = Fernet(config.PASSWORD_PEPPER)
        hashed_password = fernet_key.decrypt(hashed_password.encode())
        return bcrypt.checkpw(password.encode(), hashed_password)

    def hash_password(self, password):
        """
        :param password: user password.
        :return: hashed password with salt + pepper.
        """
        self.password_hash = self.salt_hash_secret(password)

    def verify_password(self, password):
        """
        :param password: user password.
        :return: boolean if password matches hashed password in db.
        """
        return self.check_salt_hashed_secret(password, self.password_hash)

    def encode_auth_token(self):
        """
        Generates the authentication token.
        :return: JSON Web Token.
        """
        try:

            payload = {
                'exp': datetime.utcnow() + timedelta(days=7, seconds=0),
                'iat': datetime.utcnow(),
                'id': self.id,
            }

            return jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as exception:
            return exception

    @staticmethod
    def decode_auth_token(token, token_type='Auth'):
        """
        Validates the auth token
        :param token_type: defined token type.
        :param  token: JSON Web Token
        :return: integer|string
        """
        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistedToken.check_if_blacklisted(token=token)

            if is_blacklisted_token:
                return 'Token is blacklisted. Please log in again.'
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return '{} Token Signature expired.'.format(token_type)
        except jwt.InvalidTokenError:
            return 'Invalid {} Token.'.format(token_type)

    def encode_single_use_jws(self, token_type):
        """
        :param token_type: token type to sign.
        :return: JSON Web Signature.
        """
        signature = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],
                                                    expires_in=(60*60*24))
        return signature.dumps({'id': self.id, 'type': token_type}).decode("utf-8")

    @classmethod
    def decode_single_use_jws(cls, token, required_token_type):
        """
        :param token: JSON Web Token to verify.
        :param required_token_type: token type expected in JSON Web Signature.
        :return: JSON response.
        """
        try:
            # define signature with application
            signature = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])

            # get data from signature
            data = signature.loads(token.encode("utf-8"))

            # get user_id
            user_id = data.get('id')

            # get token type
            token_type = data.get('type')

            # check if token type is equivalent
            if token_type != required_token_type:
                return {'status': 'Failed', 'message': 'Wrong token type (needed {})'.format(required_token_type)}

            # check if user_id is present
            if not user_id:
                return {'status': 'Failed', 'message': 'No User ID provided.'}

            # check if user exists in DB
            user = cls.query.filter_by(
                id=user_id).execution_options(show_all=True).first()

            # if user is not found
            if not user:
                return {'status': 'Failed', 'message': 'User not found.'}
            return {'status': 'Succeeded', 'user': user}

        except BadSignature:
            return {'status': 'Failed', 'message': 'Token signature not valid.'}

        except SignatureExpired:
            return {'status': 'Failed', 'message': 'Token has expired.'}

        except Exception as exception:
            return {'status': 'Failed', 'message': exception}
