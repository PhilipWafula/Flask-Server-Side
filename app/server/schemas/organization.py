from marshmallow import fields

from app.server.schemas.configuration import ConfigurationSchema
from app.server.utils.schemas import BaseSchema


class OrganizationSchema(BaseSchema):
    name = fields.Str()
    configurations = fields.Nested('ConfigurationSchema')


organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)
