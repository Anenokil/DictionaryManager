"""
Implements the Manager class which opens, closes, switches, and saves
multiple Dictionary instances and tracks the active dictionary.

Author: Anenokil
"""

from types import NoneType
from typing import Any, Callable

from .types import DctName, SerializedData
from .errors import MissingFieldsError
from .dictionary import Dictionary
from .utils import validate_required_fields, validate_field_type

# Typing aliases used in the module
DictionariesInfo = list[dict[str, Any]]


class Manager:
    """
    Manager for multiple dictionary instances.

    Handles opening, closing, switching between, and saving multiple dictionary files.
    Maintains a list of opened dictionaries and tracks the currently active one.

    Attributes:
    ----------
    - opened_dct_info: currently open dictionaries with metadata about
      each dictionary instance.
    - current_dct_id: ID of the currently active dictionary.
    - n_opened: Number of dictionaries currently opened in the manager.
    - dct: The currently active `Dictionary` instance or ``None`` when
      no dictionary is active.
    - filepath: File path associated with the currently active dictionary
      or ``None`` for new/unsaved dictionaries.

    Protected Attributes:
    --------------------
    - _schema_version: The version of the data format used for serialization.
    """

    _schema_version = 1

    def __init__(self):
        """
        Initialize the dictionary manager.

        Creates an empty manager with no opened dictionaries.
        """

        self.opened_dct_info: DictionariesInfo = []
        self.current_dct_id: int | None = None

    @property
    def n_opened(self) -> int:
        """
        Get the number of opened dictionaries.

        Returns:
            Number of opened dictionaries.
        """

        return len(self.opened_dct_info)

    @property
    def dct(self) -> Dictionary | None:
        """
        Get the currently active dictionary.

        Returns:
            The currently active Dictionary instance, or None if no dictionary
            is currently active.
        """

        if self.current_dct_id is None:
            return None
        return self.opened_dct_info[self.current_dct_id]['dct']

    @property
    def filepath(self) -> str | None:
        """
        Get the file path of the currently active dictionary.

        Returns:
            File path of the current dictionary, or None if no dictionary is
            active or if it's a new unsaved dictionary.
        """

        if self.current_dct_id is None:
            return None
        return self.opened_dct_info[self.current_dct_id]['filepath']

    def add_dct(self, dct: Dictionary, filepath: str | None = None, to_activate: bool = True):
        self.opened_dct_info.append({'dct': dct, 'filepath': filepath})
        if to_activate or self.n_opened == 1:
            self.current_dct_id = len(self.opened_dct_info) - 1

    def create_dct(self, name: DctName = None, to_activate: bool = True):
        """
        Create a new empty dictionary and add it to the manager.

        Args:
            name: Name for the new dictionary.
            to_activate: If True, make the newly created dictionary the
                currently active dictionary. If False, add it to the list of
                opened dictionaries without switching the active index.
        """

        dct = Dictionary(name)

        self.opened_dct_info.append({'dct': dct, 'filepath': None})
        if to_activate or self.n_opened == 1:
            self.current_dct_id = len(self.opened_dct_info) - 1

    def open_dct(
            self,
            filepath: str,
            loading_func: Callable[[str], SerializedData],
            to_activate: bool = True,
    ):
        """
        Open a dictionary from a file and add it to the manager.

        Args:
            filepath: Path to the dictionary file to open.
            loading_func: Callable that takes the file path and returns the
                deserialized dictionary data. This function is responsible
                for reading the file contents and converting them into the
                in-memory representation expected by `Dictionary.from_json_dict`.
            to_activate: If True, switch the manager's active dictionary to
                the one just opened. If False, keep the current active
                dictionary.

        Raises:
            AssertionError: If the file extension is not supported.
        """

        save_data = loading_func(filepath)

        dct = Dictionary.from_json_dict(save_data)
        dct.mark_saved()

        self.opened_dct_info.append({'dct': dct, 'filepath': filepath})
        if to_activate or self.n_opened == 1:
            self.current_dct_id = len(self.opened_dct_info) - 1

    def switch_dct(self, dct_id: int):
        """
        Switch to a different dictionary as the active one.

        Args:
            dct_id: Index of the dictionary to make active.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        self.current_dct_id = dct_id

    def close_dct(self, dct_id: int):
        """
        Close a dictionary and remove it from the manager.

        Updates the current dictionary index if necessary.

        Args:
            dct_id: Index of the dictionary to close.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        if len(self.opened_dct_info) == 1:
            self.current_dct_id = None
        elif dct_id < self.current_dct_id:
            self.current_dct_id -= 1

        del self.opened_dct_info[dct_id]

    def save_dct(
            self,
            dct_id: int,
            saving_func: Callable[[SerializedData, str], None],
            filepath: str | None = None,
    ):
        """
        Save a dictionary to a file.

        Args:
            dct_id: Index of the dictionary to save.
            saving_func: Callable that accepts two arguments — the serialized
                dictionary data and the destination file path — and writes
                the data to disk. The function should raise on failure.
            filepath: Path where to save the dictionary. If None, uses the
                dictionary's current filepath.

        Raises:
            AssertionError: If the dictionary index is out of range.
            ValueError: If no filepath is specified and the dictionary has none.
        """

        assert 0 <= dct_id <= len(self.opened_dct_info)

        if filepath is None:
            filepath = self.opened_dct_info[dct_id]['filepath']
            if filepath is None:
                raise ValueError('No filepath is specified')

        save_data = self.dct.to_json_dict()
        saving_func(save_data, filepath)
        self.dct.mark_saved()

        self.opened_dct_info[dct_id]['filepath'] = filepath

    def rename_dict(self, dct_id: int, new_name: str):
        """
        Rename a dictionary.

        Args:
            dct_id: Index of the dictionary to rename.
            new_name: New name of the dictionary.
        """

        self.opened_dct_info[dct_id]['dct'].rename(new_name)

    def reorder(self, from_index: int, to_index: int):
        """
        Reorder opened dictionaries.

        Args:
            from_index: Index of the dictionary to move.
            to_index: New index of the dictionary.
        """

        target_dct = self.opened_dct_info[from_index]
        is_current = from_index == self.current_dct_id

        if not is_current and self.current_dct_id > from_index:
            self.current_dct_id -= 1

        del self.opened_dct_info[from_index]
        self.opened_dct_info = self.opened_dct_info[:to_index] + [target_dct] + self.opened_dct_info[to_index:]

        if is_current:
            self.current_dct_id = to_index
        elif self.current_dct_id > to_index:
            self.current_dct_id += 1

    def to_dict(self) -> SerializedData:
        """
        Serialize the manager state to a dictionary format.

        Returns:
            Dictionary containing manager data.
        """

        return {
            'version': self._schema_version,
            'data': {
                'opened_dct_info': self.opened_dct_info,
                'current_dct_id': self.current_dct_id,
            }
        }

    def to_json_dict(self) -> SerializedData:
        """
        Serialize the manager state to a JSON format.

        Returns:
            Dictionary containing manager data.
        """

        data = self.to_dict()

        data['data']['opened_dct_info'] = [
            {
                'dct': item['dct'].to_json_dict(),
                'filepath': item['filepath'],
            } for item in self.opened_dct_info
        ]

        return data

    def load_from_json_dict(self, data: SerializedData):
        """
        Deserialize manager state from a JSON format.

        Args:
            data: Dictionary containing manager data.
        """

        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('opened_dct_info', 'current_dct_id')
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        opened_dct_info = data['opened_dct_info']
        current_dct_id = data['current_dct_id']

        # Validate types
        validate_field_type('opened_dct_info', opened_dct_info, list[dict[str, Any]])
        validate_field_type('current_dct_id', current_dct_id, (int, NoneType))

        # Convert types and values
        try:
            opened_dct_info = [
                {
                    'dct': Dictionary.from_json_dict(item['dct']),
                    'filepath': item['filepath'],
                } for item in data['opened_dct_info']
            ]
        except KeyError as e:
            if str(e) in ('dct', 'filepath'):
                raise MissingFieldsError(e)
            raise

        # Set attributes
        self.opened_dct_info = opened_dct_info
        self.current_dct_id = current_dct_id
