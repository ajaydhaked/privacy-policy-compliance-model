from typing import Any
import json
from src.attributeValidator import AttributeValidator

class AccessRequest:
    def __init__(self, attribute_validator):
        self.validator = attribute_validator
        self.attributes = {}
        self.description = ""

    def get(self, key):
        self.validator.validate_attribute(key)
        return str(self.attributes.get(key))

    def set(self, key, value):
        self.validator.validate_key_value(key, value)
        self.attributes[key] = value

    def get_attributes(self):
        return self.attributes

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    
