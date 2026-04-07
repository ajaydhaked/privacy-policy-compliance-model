from dataclasses import dataclass, field
from typing import Any
import json

@dataclass
class AttributeValidator:
    possible_attributes_possible_values: dict[str, list[str]] = field(default_factory=dict)

    def __init__(self, attributes: dict[str, list[str]]):
        self.possible_attributes_possible_values = attributes

    def validate_attribute(self, key):
        if key not in self.possible_attributes_possible_values:
            raise KeyError(f"Attribute '{key}' is not allowed")

    def validate_key_value(self, key, value):
        if key not in self.possible_attributes_possible_values:
            raise KeyError(f"Attribute '{key}' is not allowed")
        if value not in self.possible_attributes_possible_values[key]:
            raise ValueError(f"Value '{value}' is not allowed for attribute '{key}'")

