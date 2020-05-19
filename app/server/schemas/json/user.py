user_json_schema = {
    'type': 'object',
    'properties': {
        'given_names': {'type': 'string'},
        'surname': {'type': 'string'},
        'email': {'type': 'string'},
        'phone': {'type': 'string'},
        'address': {'type': 'string'},
        'date_of_birth': {'type': 'date'},
        'id_type': {'type': 'string'},
        'id_value': {'type': 'string'},
        'password': {'type': 'string'},
        'signup_method': {'type': 'string'},
        'public_identifier': {'type': 'string'},
        'role': {'type': 'string'}
    },
    'required': ['given_names', 'surname', 'password', 'signup_method', 'public_identifier']
}
