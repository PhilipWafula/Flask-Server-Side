from marshmallow import fields

from app.server.utils.schemas import BaseSchema


class ConfigurationSchema(BaseSchema):
    access_control_type = fields.Function(lambda configuration: configuration.access_control_type.value)


configuration_schema = ConfigurationSchema()
