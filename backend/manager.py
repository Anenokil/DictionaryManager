"""
Implements the Manager class which opens, closes, switches, and saves
multiple Dictionary instances and tracks the active dictionary.

Author: Anenokil
"""

from typing import Any
import os
import pickle

from .types import DctName
from .dictionary import Dictionary

# Typing aliases used in the module
DictionariesInfo = list[dict[str, Any]]


class Manager:
    """
    Manager for multiple dictionary instances.

    Handles opening, closing, switching between, and saving multiple dictionary files.
    Maintains a list of opened dictionaries and tracks the currently active one.

    Attributes:
    ----------
    - allowed_file_ext: supported file extensions for saving/loading dictionary data.
    - opened_dct_info: currently open dictionaries with metadata about each dictionary instance.
    - current_dct_id: ID of the currently active dictionary.
    """

    allowed_file_ext = ('.pkl',)

    def __init__(self):
        """
        Initialize the dictionary manager.

        Creates an empty manager with no opened dictionaries.
        """

        self.opened_dct_info: DictionariesInfo = []
        self.current_dct_id: int | None = None

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

    def create_dct(self, name: DctName):
        """
        Create a new empty dictionary and add it to the manager.

        Args:
            name: Name for the new dictionary.
        """

        dct = Dictionary(name)

        self.opened_dct_info.append({'dct': dct, 'filepath': None})
        self.current_dct_id = len(self.opened_dct_info) - 1

    def open_dct(self, filepath: str):
        """
        Open a dictionary from a file and add it to the manager.

        Args:
            filepath: Path to the dictionary file to open.

        Raises:
            AssertionError: If the file extension is not supported.
        """

        ext = os.path.splitext(filepath)[1]
        assert ext in self.allowed_file_ext, f'File extension "{ext}" not supported'

        with open(filepath, 'rb') as f:
            savedata = pickle.load(f)

        dct = Dictionary()
        dct.deserialize(savedata)
        dct.mark_saved()

        self.opened_dct_info.append({'dct': dct, 'filepath': filepath})
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

    def save_dct(self, dct_id: int, filepath: str | None = None):
        """
        Save a dictionary to a file.

        Args:
            dct_id: Index of the dictionary to save.
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

        savedata = self.dct.serialize()
        with open(filepath, 'wb') as f:
            pickle.dump(savedata, f)
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

    def serialize(self) -> dict[str, Any]:
        """
        Serialize the manager state to a dictionary format.

        Returns:
            Dictionary containing manager data.
        """

        data = {
            'opened_dct_info': self.opened_dct_info,
            'current_dct_id': self.current_dct_id,
        }
        return data

    def deserialize(self, data: dict[str, Any]):
        """
        Deserialize manager state from a dictionary format.

        Args:
            data: Dictionary containing manager data.
        """

        self.opened_dct_info = data.get('opened_dct_info', [])
        self.current_dct_id = data.get('current_dct_id', None)
