from marshmallow import fields

from app.server.utils.schemas import BaseSchema


def get_identification_data(user):
    identification = user.identification
    parsed_identification = {}

    for attribute in identification:
        parsed_identification[attribute.name] = attribute.value


class UserSchema(BaseSchema):
    given_name = fields.Str()
    surname = fields.Str()
    identification = fields.Method('get_identification_data')

    email = fields.Str()
    phone = fields.Str()
    address = fields.Str()
    signup_method = fields.Function(lambda method: method.signup_methods.value)

    date_of_birth = fields.Str()

    is_activated = fields.Boolean()


user_schema = UserSchema()
