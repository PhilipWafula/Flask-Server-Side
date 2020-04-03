from app.server.schemas.json.configuration import configuration_json_schema

organization_json_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'is_master': {'type': "boolean"},
        'configurations': configuration_json_schema
    },
    'required': ['name']
}
