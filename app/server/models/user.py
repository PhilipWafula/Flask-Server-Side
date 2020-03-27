import bcrypt
import jwt
import pyotp

from cryptography.fernet import Fernet
from datetime import datetime
from datetime import timedelta
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified
from typing import Union

from app import config
from app.server import db
from app.server import fernet_decrypt
from app.server import fernet_encrypt
from app.server.constants import IDENTIFICATION_TYPES
from app.server.constants import STANDARD_ACCESS_ROLES
from app.server.constants import TIERED_ACCESS_ROLES
from app.server.exceptions import IdentificationTypeNotFound
from app.server.exceptions import RoleNotFound
from app.server.exceptions import TierNotFound
from app.server.models.blacklisted_token import BlacklistedToken
from app.server.models.organization import Organization
from app.server.utils.enums.auth_enums import SignupMethod
from app.server.utils.enums.access_control_enums import AccessControlType
from app.server.utils.models import BaseModel


class User(BaseModel):
    """
    Creates user object
    """
    __tablename__ = 'users'

    given_names = db.Column(db.String(length=35), nullable=False)
    surname = db.Column(db.String(length=35), nullable=False)

    _identification = db.Column(JSONB, default={}, nullable=True)
    email = db.Column(db.String)
    msisdn = db.Column(db.String(length=13), index=True, nullable=False, unique=True)
    address = db.Column(db.String)

    date_of_birth = db.Column(db.Date)

    password_hash = db.Column(db.String(200))
    _otp_secret = db.Column(db.String(200))

    is_activated = db.Column(db.Boolean, default=False)

    signup_method = db.Column(db.Enum(SignupMethod))

    _role = db.Column(JSONB, default={}, nullable=True)

    parent_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    parent_organization = db.relationship('Organization',
                                          primaryjoin=Organization.id == parent_organization_id,
                                          lazy=True,
                                          uselist=False)

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
                config.SECRET_KEY,
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
            payload = jwt.decode(jwt=token, key=config.SECRET_KEY, algorithms='HS256')
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
        signature = TimedJSONWebSignatureSerializer(config.SECRET_KEY,
                                                    expires_in=(60 * 60 * 24))
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
                config.SECRET_KEY)

            # get data from signature
            data = signature.loads(token.encode("utf-8"))

            # get user_id
            user_id = data.get('id')

            # get token type
            token_type = data.get('type')

            # check if token type is equivalent
            if token_type != required_token_type:
                return {'status': 'Fail', 'message': 'Wrong token type (needed {})'.format(required_token_type)}

            # check if user_id is present
            if not user_id:
                return {'status': 'Fail', 'message': 'No User ID provided.'}

            # check if user exists in DB
            user = cls.query.filter_by(
                id=user_id).execution_options(show_all=True).first()

            # if user is not found
            if not user:
                return {'status': 'Fail', 'message': 'User not found.'}
            return {'status': 'Success', 'user': user}

        except BadSignature:
            return {'status': 'Fail', 'message': 'Token signature not valid.'}

        except SignatureExpired:
            return {'status': 'Fail', 'message': 'Token has expired.'}

        except Exception as exception:
            return {'status': 'Fail', 'message': exception}

    def set_otp_secret(self):
        # generate random otp_secret
        otp_secret = pyotp.random_base32()

        # encrypt otp secret
        token = fernet_encrypt(otp_secret)

        # save otp secret
        self._otp_secret = token.decode('utf-8')

        # generate one time password [expires in 1 hour]
        one_time_password = pyotp.TOTP(otp_secret, interval=3600).now()

        return one_time_password

    def _get_otp_secret(self):
        return fernet_decrypt(self._otp_secret.encode('utf-8'))

    def verify_otp(self, one_time_password, expiry_interval):
        # get secret used to create one time password
        otp_secret = self._get_otp_secret()

        # verify one time password validity
        is_valid = pyotp.TOTP(otp_secret, interval=expiry_interval).verify(one_time_password)

        return is_valid

    def get_user_organization(self):
        return self.organization

    @hybrid_property
    def role(self):
        return self._role

    def set_user_role(self, role: str, tier: Union[str, None]):

        # correct role value in db.
        if self._role is None:
            self._role = {}

        # check for role system in use from user's parent organization's sys configs
        user_organization = self.get_user_organization()
        system_configs = user_organization.configuration

        if system_configs.access_control_type == AccessControlType.STANDARD_ACCESS_CONTROL:
            if role not in STANDARD_ACCESS_ROLES:
                raise RoleNotFound('The provided role: {} is not recognized.'.format(role))

            if role and tier is None:
                self._role[role] = None
                flag_modified(self, '_role')

        if system_configs.access_control_type == AccessControlType.TIERED_ACCESS_CONTROL:
            tired_roles = TIERED_ACCESS_ROLES[role]
            if tier and tier not in tired_roles:
                raise TierNotFound('The provided tier is not recognized.'.format(tier))

            if tier is None:
                self._role.pop(role, None)
            else:
                self._role[role] = tier
                flag_modified(self, '_role')
