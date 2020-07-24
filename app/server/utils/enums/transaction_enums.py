# system imports
from enum import Enum


class TransactionStatus(Enum):
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    INITIATED = "INITIATED"
    PENDING = "PENDING"


class TransactionServiceProvider(Enum):
    AFRICAS_TALKING = "AFRICAS_TALKING"
    DARAJA = "DARAJA"


class TransactionType(Enum):
    BUSINESS_TO_BUSINESS = "BUSINESS_TO_BUSINESS"
    BUSINESS_TO_CONSUMER = "BUSINESS_TO_CONSUMER"
    MOBILE_CHECKOUT = "MOBILE_CHECKOUT"
