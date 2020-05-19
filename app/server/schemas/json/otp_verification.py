otp_verification_json_schema = {
    'type': 'object',
    'properties': {
        'phone': {'type': 'string'},
        'otp': {'type': 'string'},
        'otp_expiry_interval': {'type': 'number'}
    },
    'required': ['phone', 'otp', 'otp_expiry_interval']
}
