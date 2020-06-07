from datetime import datetime
from datetime import timedelta

import bcrypt
import jwt
import pyotp
from cryptography.fernet import Fernet
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified

from app import config
from app.server import db
from app.server import fernet_decrypt
from app.server import fernet_encrypt
from app.server.constants import IDENTIFICATION_TYPES, SUPPORTED_ROLES
from app.server.exceptions import (
    IdentificationTypeNotFoundException,
    RoleNotFoundException,
)
from app.server.models.blacklisted_token import BlacklistedToken
from app.server.models.organization import Organization
from app.server.models.role import Role
from app.server.utils.enums.auth_enums import SignupMethod
from app.server.utils.models import BaseModel
from app.server.utils.models import MutableList


class User(BaseModel):
    """
    Creates user object
    """

    __tablename__ = "users"

    given_names = db.Column(db.String(length=35), nullable=False)
    surname = db.Column(db.String(length=35), nullable=False)

    _identification = db.Column(JSONB, default={}, nullable=True)
    email = db.Column(db.String, index=True, nullable=True, unique=True)
    phone = db.Column(db.String(length=13), index=True, nullable=True, unique=True)
    address = db.Column(db.String)

    date_of_birth = db.Column(db.Date)

    password_hash = db.Column(db.String(200))
    _otp_secret = db.Column(db.String(200))

    is_activated = db.Column(db.Boolean, default=False)

    signup_method = db.Column(db.Enum(SignupMethod))

    password_reset_tokens = db.Column(MutableList.as_mutable(ARRAY(db.String)))

    parent_organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))
    parent_organization = db.relationship(
        "Organization",
        primaryjoin=Organization.id == parent_organization_id,
        lazy=True,
        uselist=False,
    )

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", back_populates="users")

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
            raise IdentificationTypeNotFoundException(
                f"Identification type {id_type} not valid"
            )

        # check that id value is supplied
        if id_value is None:
            raise ValueError("ID cannot be empty")

        # corrective method in case identification is set to none
        if self._identification is None:
            self._identification = {}

        # set values
        self._identification[id_type] = id_value
        flag_modified(self, "_identification")

    @staticmethod
    def salt_hash_secret(password: str):
        """
        :param password: user password.
        :return: encrypted password with system password pepper.
        """
        fernet_key = Fernet(config.PASSWORD_PEPPER)
        return fernet_key.encrypt(
            bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        ).decode()

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
                "exp": datetime.utcnow() + timedelta(days=7, seconds=0),
                "iat": datetime.utcnow(),
                "id": self.id,
                "role": self.role.name,
            }

            return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")
        except Exception as exception:
            return exception

    @staticmethod
    def decode_auth_token(token, token_type="authentication"):
        """
        Validates the auth token
        :param token_type: defined token type.
        :param  token: JSON Web Token
        :return: integer|string
        """
        try:
            payload = jwt.decode(jwt=token, key=config.SECRET_KEY, algorithms="HS256")
            is_blacklisted_token = BlacklistedToken.check_if_blacklisted(token=token)

            if is_blacklisted_token:
                return "Token is blacklisted. Please log in again."
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return f"{token_type} Token Signature expired."
        except jwt.InvalidTokenError:
            return f"Invalid {token_type} Token."

    def encode_single_use_jws(self, token_type):
        """
        :param token_type: token type to sign.
        :return: JSON Web Signature.
        """
        signature = TimedJSONWebSignatureSerializer(
            config.SECRET_KEY, expires_in=(60 * 60 * 24)
        )
        return signature.dumps({"id": self.id, "type": token_type}).decode("utf-8")

    @classmethod
    def decode_single_use_jws(cls, token, required_token_type):
        """
        :param token: JSON Web Token to verify.
        :param required_token_type: token type expected in JSON Web Signature.
        :return: JSON response.
        """
        try:
            # define signature with application
            signature = TimedJSONWebSignatureSerializer(config.SECRET_KEY)

            # get data from signature
            data = signature.loads(token.encode("utf-8"))

            # get user_id
            user_id = data.get("id")

            # get token type
            token_type = data.get("type")

            # check if token type is equivalent
            if token_type != required_token_type:
                return {
                    "status": "Fail",
                    "message": f"Wrong token type (needed {required_token_type})",
                }

            # check if user_id is present
            if not user_id:
                return {"status": "Fail", "message": "No User ID provided."}

            # check if user exists in DB
            user = (
                cls.query.filter_by(id=user_id).execution_options(show_all=True).first()
            )

            # if user is not found
            if not user:
                return {"status": "Fail", "message": "User not found."}
            return {"status": "Success", "user": user}

        except BadSignature:
            return {"status": "Fail", "message": "Token signature not valid."}

        except SignatureExpired:
            return {"status": "Fail", "message": "Token has expired."}

        except Exception as exception:
            return {"status": "Fail", "message": exception}

    def clear_invalid_password_reset_tokens(self):
        if self.password_reset_tokens is None:
            self.password_reset_tokens = []

        valid_tokens = []
        for token in self.password_reset_tokens:
            decoded_token_response = self.decode_single_use_jws(
                token=token, required_token_type="password_reset"
            )
            is_valid_token = decoded_token_response.get("status") == "Success"
            if is_valid_token:
                valid_tokens.append(token)
        return valid_tokens

    def save_password_reset_token(self, password_reset_token):
        if self.password_reset_tokens is None:
            self.password_reset_tokens = []
        self.password_reset_tokens.append(password_reset_token)

    def check_is_used_password_reset_token(self, password_reset_token):
        self.clear_invalid_password_reset_tokens()
        is_used = password_reset_token not in self.password_reset_tokens
        return is_used

    def remove_all_password_reset_tokens(self):
        self.password_reset_tokens = []

    def set_otp_secret(self):
        # generate random otp_secret
        otp_secret = pyotp.random_base32()

        # encrypt otp secret
        token = fernet_encrypt(otp_secret)

        # save otp secret
        self._otp_secret = token.decode("utf-8")

        # generate one time password [expires in 1 hour]
        one_time_password = pyotp.TOTP(otp_secret, interval=3600).now()

        return one_time_password

    def get_otp_secret(self):
        return fernet_decrypt(self._otp_secret.encode("utf-8"))

    def verify_otp(self, one_time_password, expiry_interval):
        # get secret used to create one time password
        otp_secret = self.get_otp_secret()

        # verify one time password validity
        is_valid = pyotp.TOTP(otp_secret, interval=expiry_interval).verify(
            one_time_password
        )

        return is_valid

    def bind_user_to_organization(self, organization: Organization):
        if not self.parent_organization:
            self.parent_organization = organization

    def get_user_organization(self):
        return self.organization

    # method responsible for returning user details that make it easier to identify a user.
    def user_details(self):
        if self.given_names and self.surname:
            return f"{self.given_names} {self.surname} {self.phone}"
        return f"{self.phone}"

    def set_role(self, role: str):
        # check that role is supported in system constants
        if role not in SUPPORTED_ROLES:
            raise RoleNotFoundException("The provided role is not supported")
        user_role = Role.query.filter_by(name=role).first()
        self.role_id = user_role.id

    def __repr__(self):
        return "User %r" % self.phone
