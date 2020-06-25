# system imports
from unittest.mock import Mock

# third-party imports
import pytest

# application imports
from app import config
from app.server.utils.payments.africas_talking import AfricasTalking


@pytest.mark.parametrize(
    "amount, phone_number, product_name, provider_channel",
    [(10000.00, "0700000000", config.AFRICASTALKING_PRODUCT_NAME, "000000")],
)
def test_initiate_mobile_checkout(
    example_checkout_transaction_data: Mock,
    amount: float,
    phone_number: str,
    product_name: str,
    provider_channel: str,
):
    """It creates a checkout transaction JSON object."""
    payment = AfricasTalking(
        config.AFRICASTALKING_API_KEY, config.AFRICASTALKING_USERNAME
    )
    transaction = payment.initiate_mobile_checkout(
        amount=amount,
        phone_number=phone_number,
        product_name=product_name,
        provider_channel=provider_channel,
    )
    assert transaction == example_checkout_transaction_data


@pytest.mark.parametrize(
    "amount, destination_account, destination_channel, product_name, provider, transfer_type",
    [
        (
            10.00,
            "sandbox",
            "000000",
            config.AFRICASTALKING_PRODUCT_NAME,
            "Mpesa",
            "BusinessPayBill",
        )
    ],
)
def test_initiate_business_to_business_transaction(
    example_b2b_transaction_data: Mock,
    amount: float,
    destination_account: str,
    destination_channel: str,
    product_name: str,
    provider: str,
    transfer_type: str,
):
    """It creates a B2B transaction JSON object."""
    payment = AfricasTalking(
        config.AFRICASTALKING_API_KEY, config.AFRICASTALKING_USERNAME
    )
    transaction = payment.initiate_business_to_business_transaction(
        amount=amount,
        destination_account=destination_account,
        destination_channel=destination_channel,
        product_name=product_name,
        provider=provider,
        transfer_type=transfer_type,
    )
    assert transaction == example_b2b_transaction_data


@pytest.mark.parametrize(
    "amount, phone_number, product_name, name, provider_channel, reason",
    [
        (
            10.00,
            "0700000000",
            config.AFRICASTALKING_PRODUCT_NAME,
            "Turing",
            "000000",
            "SalaryPayment",
        )
    ],
)
def test_initiate_business_to_consumer_transaction(
    example_b2c_transaction_data: Mock,
    amount: float,
    phone_number: str,
    product_name: str,
    name: str,
    provider_channel: str,
    reason: str,
):
    """It creates a B2C transaction JSON object."""
    payment = AfricasTalking(
        config.AFRICASTALKING_API_KEY, config.AFRICASTALKING_USERNAME
    )
    transaction = payment.initiate_business_to_consumer_transaction(
        amount=amount,
        phone_number=phone_number,
        product_name=product_name,
        name=name,
        provider_channel=provider_channel,
        reason=reason,
    )
    assert transaction == example_b2c_transaction_data
