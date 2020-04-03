from jsonschema import Draft7Validator


def validate_request(instance: dict, schema: dict):
    validator = Draft7Validator(schema=schema)
    return validator.validate(instance)
