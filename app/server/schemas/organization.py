from marshmallow import fields

from app.server.utils.schemas import BaseSchema


class OrganizationSchema(BaseSchema):
    address = fields.Str()
    name = fields.Str()
    public_identifier = fields.String()


organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)
