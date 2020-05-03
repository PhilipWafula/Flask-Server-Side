reset_password_json_schema = {
    'type': 'object',
    'properties': {
        'new_password': {'type': 'string'},
        'password_reset_token': {'type': 'string'}
    },
    'required': ['new_password', 'password_reset_token']
}
