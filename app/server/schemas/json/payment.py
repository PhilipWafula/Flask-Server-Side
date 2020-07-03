africas_talking_checkout_json_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "currency_code": {"type": "string"},
        "metadata": {"type": "object"},
        "payment_type": {"type": "string"},
        "phone_number": {"type": "string"},
        "product_name": {"type": "string"},
        "provider_channel": {"type": "string"},
        "provider_type": {"type": "string"},
    },
    "required": [
        "amount",
        "payment_type",
        "phone_number",
        "product_name",
        "provider_type",
    ],
}

africas_talking_business_to_business_json_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "currency_code": {"type": "string"},
        "destination_account": {"type": "string"},
        "destination_channel": {"type": "string"},
        "metadata": {"type": "object"},
        "payment_type": {"type": "string"},
        "product_name": {"type": "string"},
        "provider": {"type": "string"},
        "provider_type": {"type": "string"},
        "transfer_type": {"type": "string"},
    },
    "required": [
        "amount",
        "destination_account",
        "destination_channel",
        "payment_type",
        "product_name",
        "provider",
        "provider_type",
        "transfer_type",
    ],
}

africas_talking_business_to_consumer_json_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "currency_code": {"type": "string"},
        "metadata": {"type": "object"},
        "name": {"type": "string"},
        "payment_type": {"type": "string"},
        "phone_number": {"type": "string"},
        "product_name": {"type": "string"},
        "provider_channel": {"type": "string"},
        "provider_type": {"type": "string"},
        "transfer_type": {"type": "string"},
    },
    "required": [
        "amount",
        "payment_type",
        "phone_number",
        "product_name",
        "provider_type",
    ],
}
