import toastedmarshmallow
from marshmallow import fields
from marshmallow import Schema


class BaseSchema(Schema):
    class Meta:
        jit = toastedmarshmallow.Jit

    id = fields.Int(dump_only=True)
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)
