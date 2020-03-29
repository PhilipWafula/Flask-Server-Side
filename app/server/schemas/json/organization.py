from typing import Optional

from app.server.schemas.json.configurations import configurations_schema

organization_json_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'is_master': {'type': "boolean"},
        'configurations': configurations_schema
    },
    'required': ['name']
}
