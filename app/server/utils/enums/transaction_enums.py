# system imports
from enum import Enum


class MpesaTransactionStatus(Enum):
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    INITIATED = "INITIATED"
    PENDING = "PENDING"


class MpesaTransactionServiceProvider(Enum):
    AFRICAS_TALKING = "AFRICAS_TALKING"
    DARAJA = "DARAJA"


class MpesaTransactionType(Enum):
    MOBILE_BUSINESS_TO_BUSINESS = "MOBILE_BUSINESS_TO_BUSINESS"
    MOBILE_BUSINESS_TO_CONSUMER = "MOBILE_BUSINESS_TO_CONSUMER"
    MOBILE_CHECKOUT = "MOBILE_CHECKOUT"
