"""
Implements the Manager class which opens, closes, switches, and saves
multiple Dictionary instances and tracks the active dictionary.

Author: Anenokil
"""

from types import NoneType
from typing import Any
import json

from .core.types import DctName, SerializedData
from .core.errors import UnknownVersionError
from .core.dictionary import Dictionary
from .core.utils import validate_required_fields, validate_field_type, validate_field_len


class DctSettings:
    """
    Dictionary configuration settings.

    Attributes:
    ----------
    - is_register_sensitive: Whether dictionary operations should
      be case-sensitive.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for
      serialization.
    """

    _schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        self.is_register_sensitive: bool = ...

        if data is None:
            self.set_defaults()
        else:
            self.load_from_dict(data)

    def set_defaults(self):
        self.is_register_sensitive = True

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'is_register_sensitive': self.is_register_sensitive,
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.is_register_sensitive = data['is_register_sensitive']

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            DctSettings._validate_data(data)
            return data
        raise UnknownVersionError(DctSettings.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        required_fields = ('is_register_sensitive',)
        validate_required_fields(data, required_fields)

        validate_field_type('is_register_sensitive', data['is_register_sensitive'], bool)


class DctCache:
    """
    Dictionary cache for storing user session state.

    Attributes:
    ----------
    - session_number: Last active session identifier.
    - search_config: Search settings.
    - train_config: Training settings.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for
      serialization.
    """

    _schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        self.session_number: int = ...
        self.search_config: list[int] = ...
        self.train_config: list[int] = ...

        if data is None:
            self.set_defaults()
        else:
            self.load_from_dict(data)

    def set_defaults(self):
        self.session_number = 1
        self.search_config = [0, 0, 1, 1, 0, 0, 0, 0]
        self.train_config = [0, 0, 1, 1, 1]

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'session_number': self.session_number,
            'search_config': self.search_config,
            'train_config': self.train_config,
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.session_number = data['session_number']
        self.search_config = data['search_config']
        self.train_config = data['train_config']

        self.session_number += 1

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            DctCache._validate_data(data)
            return data
        raise UnknownVersionError(DctCache.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        required_fields = ('session_number', 'search_config', 'train_config')
        validate_required_fields(data, required_fields)

        validate_field_type('session_number', data['session_number'], int)
        validate_field_type('search_config', data['search_config'], list[int])
        validate_field_type('train_config', data['train_config'], list[int])

        validate_field_len('search_config', data['search_config'], 8)
        validate_field_len('train_config', data['train_config'], 5)


class DctInfo:
    """
    Main dictionary container holding dictionary data, settings, cache,
    and file information.

    Attributes:
    ----------
    - dct: The main dictionary data structure.
    - filepath: Path to the dictionary file, or None if not saved.
    - settings: Dictionary settings.
    - cache: User session state.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for
      serialization.
    """

    _schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        self.dct: Dictionary = ...
        self.filepath: str | None = ...
        self.settings: DctSettings = ...
        self.cache: DctCache = ...

        if data is None:
            self.set_defaults()
        else:
            self.load_from_dict(data)

    def set_defaults(self):
        self.dct = Dictionary()
        self.filepath = None
        self.settings = DctSettings()
        self.cache = DctCache()

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'dct': self.dct.to_json_dict(),
            'settings': self.settings.to_dict(),
            'cache': self.cache.to_dict(),
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.dct = Dictionary.from_json_dict(data['dct'])
        self.settings = DctSettings(data['settings'])
        self.cache = DctCache(data['cache'])

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            DctInfo._validate_data(data)
            return data
        raise UnknownVersionError(DctInfo.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        required_fields = ('dct', 'settings', 'cache')
        validate_required_fields(data, required_fields)

        validate_field_type('dct', data['dct'], SerializedData)
        validate_field_type('settings', data['settings'], SerializedData)
        validate_field_type('cache', data['cache'], SerializedData)


class Manager:
    """
    Manager for multiple dictionary instances.

    Handles opening, closing, switching between, and saving multiple
    dictionary files. Maintains a list of opened dictionaries and
    tracks the currently active one.

    Attributes:
    ----------
    - opened_dct_info: currently open dictionaries with metadata about
      each dictionary instance.
    - active_dct_id: ID of the currently active dictionary.
    - n_opened: Number of dictionaries currently opened in the manager.
    - dct: The currently active `Dictionary` instance or ``None`` when
      no dictionary is active.
    - filepath: File path associated with the currently active
      dictionary or ``None`` for new/unsaved dictionaries.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for
      serialization.
    """

    _schema_version = 1

    def __init__(self):
        """
        Initialize the dictionary manager.

        Creates an empty manager with no opened dictionaries.
        """

        self.opened_dct_info: list[DctInfo] = []
        self.active_dct_id: int | None = None

    @property
    def n_opened(self) -> int:
        """
        Get the number of opened dictionaries.

        Returns:
            Number of opened dictionaries.
        """

        return len(self.opened_dct_info)

    @property
    def active(self) -> DctInfo | None:
        """
        Get the file path of the currently active dictionary.

        Returns:
            File path of the active dictionary, or None if no
            dictionary is active or if it's a new unsaved dictionary.
        """

        if self.active_dct_id is None:
            return None
        return self.opened_dct_info[self.active_dct_id]

    def add_dct(self, dct_info: DctInfo, to_activate: bool = True):
        self.opened_dct_info.append(dct_info)

        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_info) - 1

    def create_dct(self, name: DctName = None, to_activate: bool = True):
        """
        Create a new empty dictionary and add it to the manager.

        Args:
            name: Name for the new dictionary.
            to_activate: If True, make the newly created dictionary the
                currently active dictionary. If False, add it to the
                list of opened dictionaries without switching the
                active index.
        """

        new_dct_info = DctInfo()
        new_dct_info.dct.rename(name)
        self.opened_dct_info.append(new_dct_info)

        # If needed, set this dictionary as active
        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_info) - 1

    def open_dct(self, filepath: str, to_activate: bool = True):
        """
        Open a dictionary from a file and add it to the manager.

        Args:
            filepath: Path to the dictionary file to open.
            to_activate: If True, switch the manager's active
                dictionary to the one just opened. If False, keep the
                current active dictionary.
        """

        with open(filepath, 'r') as file:
            data = json.load(file)
        dct_info = DctInfo(data)
        dct_info.dct.mark_saved()
        self.opened_dct_info.append(dct_info)

        # If needed, set this dictionary as active
        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_info) - 1

    def switch_dct(self, dct_id: int):
        """
        Switch to a different dictionary as the active one.

        Args:
            dct_id: Index of the dictionary to make active.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        self.active_dct_id = dct_id

    def close_dct(self, dct_id: int):
        """
        Close a dictionary and remove it from the manager.

        Updates the active dictionary index if necessary.

        Args:
            dct_id: Index of the dictionary to close.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        if len(self.opened_dct_info) == 1:
            self.active_dct_id = None
        elif dct_id < self.active_dct_id:
            self.active_dct_id -= 1

        del self.opened_dct_info[dct_id]

    def save_dct(self, dct_id: int, filepath: str | None = None):
        """
        Save a dictionary to a file.

        Args:
            dct_id: Index of the dictionary to save.
            filepath: Path where to save the dictionary. If None, uses
                the dictionary's current filepath.

        Raises:
            AssertionError: If the dictionary index is out of range.
            ValueError: If no filepath is specified and the dictionary
                has none.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        if filepath is None:
            filepath = self.opened_dct_info[dct_id].filepath
            if filepath is None:
                raise ValueError('No filepath is specified')

        data = self.active.to_dict()

        with open(filepath, 'w') as file:
            json.dump(data, file)

        self.active.dct.mark_saved()

        self.opened_dct_info[dct_id].filepath = filepath

    def rename_dict(self, dct_id: int, new_name: str):
        """
        Rename a dictionary.

        Args:
            dct_id: Index of the dictionary to rename.
            new_name: New name of the dictionary.
        """

        self.opened_dct_info[dct_id].dct.rename(new_name)

    def reorder(self, from_index: int, to_index: int):
        """
        Reorder opened dictionaries.

        Args:
            from_index: Index of the dictionary to move.
            to_index: New index of the dictionary.
        """

        target_dct = self.opened_dct_info[from_index]
        is_active = from_index == self.active_dct_id

        if not is_active and self.active_dct_id > from_index:
            self.active_dct_id -= 1

        del self.opened_dct_info[from_index]
        self.opened_dct_info = self.opened_dct_info[:to_index] + [target_dct] + self.opened_dct_info[to_index:]

        if is_active:
            self.active_dct_id = to_index
        elif self.active_dct_id > to_index:
            self.active_dct_id += 1

    def to_dict(self) -> SerializedData:
        """
        Serialize the manager state to a dictionary format.

        Returns:
            Dictionary containing manager data.
        """

        return {
            'version': self._schema_version,
            'data': {
                'opened_dct_info': [dct_info.to_dict() for dct_info in self.opened_dct_info],
                'active_dct_id': self.active_dct_id,
            }
        }

    def load_from_json_dict(self, data: SerializedData):
        """
        Deserialize manager state from a JSON format.

        Args:
            data: Dictionary containing manager data.
        """

        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('opened_dct_info', 'active_dct_id')
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        opened_dct_info = data['opened_dct_info']
        active_dct_id = data['active_dct_id']

        # Validate types
        validate_field_type('opened_dct_info', opened_dct_info, list[SerializedData])
        validate_field_type('active_dct_id', active_dct_id, (int, NoneType))

        # Read opened dictionaries
        opened_dct_info = [DctInfo(item) for item in data['opened_dct_info']]

        # Set attributes
        self.opened_dct_info = opened_dct_info
        self.active_dct_id = active_dct_id

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Manager':
        """
        Deserialize manager state from a JSON format.

        Args:
            data: Dictionary containing manager data.

        Returns:
            A manager object.
        """

        manager = cls()
        manager.load_from_json_dict(data)
        return manager
