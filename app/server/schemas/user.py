from marshmallow import fields

from app.server.utils.schemas import BaseSchema


class UserSchema(BaseSchema):
    given_names = fields.Str()
    surname = fields.Str()
    identification = fields.Method('get_identification_data')
    role = fields.Method('get_role_data')

    email = fields.Str()
    phone = fields.Str()
    address = fields.Str()
    signup_method = fields.Function(lambda method: method.signup_methods.value)

    date_of_birth = fields.Str()

    is_activated = fields.Boolean()

    def get_identification_data(self, user):
        return user.identification

    def get_role_data(self, user):
        return user.role.name


user_schema = UserSchema()
users_schema = UserSchema(many=True)
