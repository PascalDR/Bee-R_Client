from jsonschema import validate
from typing import Any

SCHEMA = {
    'type': 'object',
    'properties': {
        'ServerConfig': {
            'type': 'object',
            'properties': {
                'url':  {'type': 'string'},
                'port': {'type': 'number', 'minimum': 1024, "maximum": 9999}
            },
            'required': ['url', 'port']
        },
        'ClientConfig': {
            'type': 'object',
            'properties': {
                'metric_interval': {'type': 'number', 'minimum': 0, "maximum": 99999},
                'username':        {'type': 'string'},
                'password':        {'type': 'string'},
                'ca_path':         {'type': 'string'},
                'db_path':         {'type': 'string'}
            },
            'required': ['metric_interval', 'username', 'password']
        },
        'Sensors': {
            'type': 'array',
            'items': { 
                'type': 'object',
                'properties': {
                    'type':    {'type': 'string'},
                    'id':      {'type': 'number', 'minimum': 0, "maximum": 40},
                    'pin':     {'type': 'number', 'minimum': 0, "maximum": 40},
                },
                'required': ['type', 'id', 'pin']
            }
        }
    },
    'required': ['ServerConfig', 'ClientConfig', 'Sensors']
}


def validator(instance: object) -> Any:
    return validate(instance, SCHEMA)
