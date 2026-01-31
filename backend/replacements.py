"""
TODO

Author: Anenokil
"""

from typing import Iterable
import re

from .core.types import SerializedData
from .core.utils import validate_required_fields, validate_field_type

Replacements = dict[tuple[str, str], str]


class Replacer:
    """
    TODO

    Attributes:
    ----------
    - modifiers: Allowed modifier characters for input replacements.
    - active_modifiers: TODO
    - replacements: Mapping from input sequences to replacement characters.
    - default_modifiers: Sequence of default modifier characters used when
      no explicit `modifiers` argument is provided to `__init__`.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for serialization.
    """

    _schema_version = 1
    default_modifiers = (
        '', '\\', '/', '|', '`', "'", '"', '^', '<', '>',
        '_', '~', '+', '*', ':', '#', '%', '@', '&', '$',
    )

    def __init__(self, modifiers: Iterable[str] = default_modifiers):
        self._replacements: dict[str, dict[str, str]] = {modifier: {} for modifier in modifiers}

    @property
    def modifiers(self) -> set[str]:
        return set(self._replacements)

    @property
    def active_modifiers(self) -> set[str]:
        return {modifier for modifier, dct in self._replacements.items() if dct}

    @property
    def replacements(self) -> Replacements:
        return {
            (modifier, input_char): output_char
            for modifier, char_pair in self._replacements.items()
            for input_char, output_char in char_pair.items()
        }

    def add_replacement(self, modifier: str, input_char: str, output_char: str):
        assert modifier in self.modifiers
        assert input_char not in self.modifiers
        assert len(input_char) == 1
        assert len(output_char) == 1

        self._replacements[modifier][modifier] = modifier
        self._replacements[modifier][input_char] = output_char

    def delete_replacement(self, modifier: str, input_char: str):
        assert input_char != modifier

        del self._replacements[modifier][input_char]
        if len(self._replacements[modifier]) == 1:
            self._replacements[modifier] = {}

    def apply_replacements(self, text: str) -> str:
        replacements = {
            modifier+input_char: output_char
            for modifier, char_pair in self._replacements.items()
            for input_char, output_char in char_pair.items()
        }

        pattern = re.compile('|'.join(re.escape(key) for key in replacements.keys()))

        return pattern.sub(lambda match: replacements[match.group()], text)

    def escape(self, text: str) -> str:
        return ''.join(
            char * 2 if char in self.active_modifiers else char
            for char in text
        )

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'data': {
                'replacements': self._replacements,
            }
        }

    def to_json_dict(self) -> SerializedData:
        return self.to_dict()

    def load_from_json_dict(self, data: SerializedData):
        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('replacements',)
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        replacements = data['replacements']

        # Validate types
        validate_field_type('replacements', replacements, dict[str, dict[str, str]])

        # Set attributes
        self._replacements = replacements

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Replacer':
        replacer = cls()
        replacer.load_from_json_dict(data)
        return replacer
