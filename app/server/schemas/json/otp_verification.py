otp_verification_json_schema = {
    'type': 'object',
    'properties': {
        'msisdn': {'type': 'string'},
        'otp': {'type': 'string'},
        'otp_expiry_interval': {'type': 'number'}
    },
    'required': ['msisdn', 'otp', 'otp_expiry_interval']
}
