from marshmallow import fields

from app.server.schemas.configurations import ConfigurationSchema
from app.server.utils.schemas import BaseSchema


class OrganizationSchema(BaseSchema):
    name = fields.Str()
    is_master = fields.Boolean()
    configurations = fields.Nested('ConfigurationSchema')


organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)
