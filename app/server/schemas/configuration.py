from marshmallow import fields

from app.server.utils.schemas import BaseSchema


class ConfigurationSchema(BaseSchema):
    access_control_type = fields.Function(lambda configuration: configuration.access_control_type.value)
    access_roles = fields.List(fields.String())
    access_tiers = fields.List(fields.String())


configuration_schema = ConfigurationSchema()
