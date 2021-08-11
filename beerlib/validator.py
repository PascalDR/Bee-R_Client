from jsonschema import Validator

SCHEMA = {
    'type': 'object',
    'properties': {
        'ServerConfig': {
            'type': 'object',
            'properties': {
                'url':  { 'type': 'string' },
                'port': { 'type': 'number', 'minimum': 1024, "maximum": 9999 }
            }
        },
        'ClientConfig': {
            'type': 'object',
            'properties': {
                'id':              { 'type': 'string' },
                'metric_interval': { 'type': 'number', 'minimum': 0, "maximum": 99999 },
                'username':        { 'type': 'string' },
                'password':        { 'type': 'string' },
                'ca_path':         { 'type': 'string' },
                'db_path':         { 'type': 'string' }
            }
        },
        'Sensors': {
            'type': 'array',
            'items': { 
                'type': 'object',
                'properties': {
                    'type':    { 'type': 'string' },
                    'id':      { 'type': 'number', 'minimum': 0, "maximum": 40 },
                    'pin':     { 'type': 'number', 'minimum': 0, "maximum": 40 },
                }
            }
        }
    }
}

validator = Validator( SCHEMA )