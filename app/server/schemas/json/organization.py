from typing import Optional

from app.server.schemas.json.configuration import configuration_schema

organization_json_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'is_master': {'type': "boolean"},
        'configurations': configuration_schema
    },
    'required': ['name']
}
