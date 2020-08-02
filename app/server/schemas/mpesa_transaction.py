# third party imports
import toastedmarshmallow
from marshmallow import fields,  Schema


class MpesaTransactionSchema(Schema):
    class Meta:
        jit = toastedmarshmallow.Jit

    id = fields.UUID(dump_only=True)
    destination_account = fields.Str()
    amount = fields.Float()
    product_name = fields.Str()
    provider = fields.Str()
    service_provider_transaction_id = fields.Str()
    idempotency_key = fields.Str()
    status = fields.Function(lambda method: method.status.value)
    status_description = fields.Str()
    type = fields.Function(lambda method: method.mpesa_trasaction_type.value)
    service_provider = fields.Function(lambda method: method.mpesa_trasaction_service_provider.value)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


mpesa_transactions_schema = MpesaTransactionSchema(many=True)
