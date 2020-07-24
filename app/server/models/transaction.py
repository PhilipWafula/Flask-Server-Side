# system imports
import uuid

# third party imports
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import UUID

# application imports
from app.server import db
from app.server.utils.enums.transaction_enums import TransactionStatus, TransactionType, TransactionServiceProvider


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=(uuid.uuid4()))
    phone = db.Column(db.String, index=True)
    amount = db.Column(db.Float(precision=2))
    product_name = db.Column(db.String)
    provider = db.Column(db.String)

    # transaction references
    reference = db.Column(db.String, default=uuid.uuid4(), index=True, unique=True)
    service_provider_transaction_reference = db.Column(db.String, index=True, unique=True)

    # transaction categorization
    status = db.Column(db.Enum(TransactionStatus))
    type = db.Column(db.Enum(TransactionType))
    service_provider = db.Column(db.Enum(TransactionServiceProvider))
