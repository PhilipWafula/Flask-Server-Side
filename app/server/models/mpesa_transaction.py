# system imports
import uuid

# third party imports
from sqlalchemy.dialects.postgresql import UUID

# application imports
from app.server import db
from app.server.utils.enums.transaction_enums import MpesaTransactionStatus,\
    MpesaTransactionType,\
    MpesaTransactionServiceProvider


class MPesaTransaction(db.Model):
    __tablename__ = 'mpesa_transactions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=(uuid.uuid4))
    destination_account = db.Column(db.String, index=True)
    amount = db.Column(db.Float(precision=2))
    product_name = db.Column(db.String)
    provider = db.Column(db.String)

    # transaction reference
    service_provider_transaction_id = db.Column(db.String, index=True, unique=True)

    # transaction categorization
    status = db.Column(db.Enum(MpesaTransactionStatus))
    status_description = db.Column(db.String)
    type = db.Column(db.Enum(MpesaTransactionType))
    service_provider = db.Column(db.Enum(MpesaTransactionServiceProvider))

    # date
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
