"""
Implements the Manager class which stores Dictionaries and tracks the active one.

Author: Anenokil
"""

import os
from types import NoneType
import json

from .core.types import Tag, DctName, SerializedData
from .core.errors import UnknownVersionError
from .core.dictionary import Dictionary
from .core.trainer import TrainingConfig, Trainer
from .core.utils import validate_required_fields, validate_field_type
from .replacements import Replacer


class SearchConfig:
    """
    Configuration for Dictionary search.

    Attributes:
        to_search_only_fav: Whether to search only across favorite Entries.
        to_search_only_full: Whether to search only full matches.
        to_search_in_words: Whether to include lemmas in search.
        to_search_in_translations: Whether to include translations in search.
        to_search_in_forms: Whether to include forms in search.
        to_search_in_phrases: Whether to include phrases in search.
        to_search_in_notes: Whether to include notes in search.
        search_tags: List of tags to restrict search to, or None to search across all tags.
    """

    _schema_version = 1

    def __init__(
            self,
            to_search_only_fav: bool = False,
            to_search_only_full: bool = False,
            to_search_in_words: bool = True,
            to_search_in_translations: bool = True,
            to_search_in_forms: bool = False,
            to_search_in_phrases: bool = False,
            to_search_in_notes: bool = False,
            search_tags: list[Tag] | None = None,
    ):
        self.to_search_only_fav = to_search_only_fav
        self.to_search_only_full = to_search_only_full
        self.to_search_in_words = to_search_in_words
        self.to_search_in_translations = to_search_in_translations
        self.to_search_in_forms = to_search_in_forms
        self.to_search_in_phrases = to_search_in_phrases
        self.to_search_in_notes = to_search_in_notes
        self.search_tags = search_tags

    @classmethod
    def from_dict(cls, data: SerializedData):
        search_settings = cls()
        search_settings.load_from_dict(data)
        return search_settings

    def set_defaults(self):
        self.to_search_only_fav = False
        self.to_search_only_full = False
        self.to_search_in_words = True
        self.to_search_in_translations = True
        self.to_search_in_forms = False
        self.to_search_in_phrases = False
        self.to_search_in_notes = False
        self.search_tags = None

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'to_search_only_fav': self.to_search_only_fav,
            'to_search_only_full': self.to_search_only_full,
            'to_search_in_words': self.to_search_in_words,
            'to_search_in_translations': self.to_search_in_translations,
            'to_search_in_forms': self.to_search_in_forms,
            'to_search_in_phrases': self.to_search_in_phrases,
            'to_search_in_notes': self.to_search_in_notes,
            'search_tags': self.search_tags,
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.to_search_only_fav = data['to_search_only_fav']
        self.to_search_only_full = data['to_search_only_full']
        self.to_search_in_words = data['to_search_in_words']
        self.to_search_in_translations = data['to_search_in_translations']
        self.to_search_in_forms = data['to_search_in_forms']
        self.to_search_in_phrases = data['to_search_in_phrases']
        self.to_search_in_notes = data['to_search_in_notes']
        self.search_tags = data['search_tags']

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            SearchConfig._validate_data(data)
            return data
        raise UnknownVersionError(SearchConfig.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        bool_fields = (
            'to_search_only_fav', 'to_search_only_full', 'to_search_in_words',
            'to_search_in_translations', 'to_search_in_forms',
            'to_search_in_phrases', 'to_search_in_notes',
        )
        required_fields = bool_fields + ('search_tags',)
        validate_required_fields(data, required_fields)

        for field_name in bool_fields:
            validate_field_type(field_name, data[field_name], bool)
        validate_field_type('search_tags', data['search_tags'], (list[str], NoneType))


class DctBundle:
    """
    Main Dictionary container holding its configuration, settings and file information.

    Attributes:
        filepath: Absolute path to the Dictionary file.
        dct: The main Dictionary data structure.
        session_number: Last active session identifier.
        search_config: Search settings.
        train_config: Training settings.
        replacer: Replacer instance.
        trainer: Trainer instance.
    """

    _schema_version = 1

    def __init__(
            self,
            filepath: str | None = None,
            dct: Dictionary | None = None,
            session_number: int = 1,
            search_config: SearchConfig | None = None,
            train_config: TrainingConfig | None = None,
            replacer: Replacer | None = None,
    ):
        self.filepath = None if filepath is None else os.path.abspath(filepath)
        self.dct = Dictionary() if dct is None else dct
        self.session_number = session_number
        self.search_config = SearchConfig() if search_config is None else search_config
        self.train_config = TrainingConfig() if train_config is None else train_config
        self.replacer = Replacer() if replacer is None else replacer
        self.trainer = Trainer(self.dct, self.train_config)

    @classmethod
    def from_dict(cls, filepath: str, data: SerializedData):
        dct_bundle = cls(filepath)
        dct_bundle.load_from_dict(data)
        return dct_bundle

    def set_defaults(self):
        self.dct = Dictionary()
        self.session_number = 1
        self.search_config.set_defaults()
        self.train_config.set_defaults()
        self.replacer = Replacer()
        self.trainer = Trainer(self.dct, self.train_config)

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'data': {
                'dct': self.dct.to_json_dict(),
                'session_number': self.session_number,
                'search_config': self.search_config.to_dict(),
                'train_config': self.train_config.to_dict(),
                'replacer': self.replacer.to_json_dict(),
            }
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)
        data = data['data']

        self.dct.load_from_json_dict(data['dct'])
        self.session_number = data['session_number']
        self.search_config.load_from_dict(data['search_config'])
        self.train_config.load_from_dict(data['train_config'])
        self.replacer.load_from_json_dict(data['replacer'])
        self.trainer = Trainer(self.dct, self.train_config)

        self.session_number += 1

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            DctBundle._validate_data(data)
            return data
        raise UnknownVersionError(DctBundle.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        validate_required_fields(data, ('data',))
        data = data['data']

        required_fields = (
            'dct', 'session_number', 'search_config', 'train_config', 'replacer',
        )
        validate_required_fields(data, required_fields)

        validate_field_type('dct', data['dct'], SerializedData)
        validate_field_type('session_number', data['session_number'], int)
        validate_field_type('search_config', data['search_config'], SerializedData)
        validate_field_type('train_config', data['train_config'], SerializedData)
        validate_field_type('replacer', data['replacer'], SerializedData)


class Manager:
    """
    Manages multiple Dictionary instances and tracks the currently active one.

    Attributes:
        opened_dct_bundles: Currently opened Dictionary instances with their associated Bundles.
        active_dct_id: ID of the currently active Dictionary.
        n_opened: Number of currently opened Dictionary instances.
        active: DctBundle of the currently active Dictionary, or None if no Dictionary is active.
    """

    _schema_version = 1

    def __init__(self):
        """
        Initialize the Manager.

        Creates an empty Manager with no opened Dictionaries.
        """

        self.opened_dct_bundles: list[DctBundle] = []
        self.active_dct_id: int | None = None

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Manager':
        """
        Deserialize Manager state from a JSON format.

        Args:
            data: Dictionary containing Manager data.

        Returns:
            Manager object.
        """

        manager = cls()
        manager.load_from_json_dict(data)
        return manager

    @property
    def n_opened(self) -> int:
        """
        Get the number of opened Dictionaries.

        Returns:
            Number of opened Dictionaries.
        """

        return len(self.opened_dct_bundles)

    @property
    def active(self) -> DctBundle | None:
        """
        Get the Bundle of the currently active Dictionary.

        Returns:
            Bundle of the active Dictionary, or None if no Dictionary is active.
        """

        if self.active_dct_id is None:
            return None
        return self.opened_dct_bundles[self.active_dct_id]

    def add_dct(self, dct_bundle: DctBundle, to_activate: bool = True):
        """
        Add an existing Dictionary to the Manager.

        Args:
            dct_bundle: Bundle of the Dictionary to add.
            to_activate: If True, switch the Manager's active Dictionary to the one just added.
                         If False, add it without switching the active index.
        """

        self.opened_dct_bundles.append(dct_bundle)

        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_bundles) - 1

    def create_dct(
            self,
            filepath: str | None = None,
            name: DctName = None,
            to_activate: bool = True,
    ):
        """
        Create a new empty Dictionary and add it to the Manager.

        Args:
            filepath: Path where the Dictionary file will be saved.
            name: Name for the new Dictionary.
            to_activate: If True, switch the Manager's active Dictionary to the one just created.
                         If False, add it without switching the active index.
        """

        new_dct_bundle = DctBundle(filepath)
        new_dct_bundle.dct.rename(name)

        self.opened_dct_bundles.append(new_dct_bundle)

        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_bundles) - 1

    def open_dct(self, filepath: str, to_activate: bool = True):
        """
        Load a Dictionary from a file and add it to the Manager.

        Args:
            filepath: Path to the Dictionary file to open.
            to_activate: If True, switch the Manager's active Dictionary to the one just opened.
                         If False, add it without switching the active index.

        Raises:
            FileNotFoundError: If the file does not exist.
        """

        with open(filepath, 'r') as file:
            data = json.load(file)
        dct_bundle = DctBundle.from_dict(filepath, data)
        dct_bundle.dct.mark_saved()

        self.opened_dct_bundles.append(dct_bundle)

        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_bundles) - 1

    def switch_dct(self, dct_id: int):
        """
        Switch to a different Dictionary as the active one.

        Args:
            dct_id: Index of the Dictionary to make active.

        Raises:
            KeyError: If the Dictionary index is out of range.
        """

        if not (0 <= dct_id < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')

        self.active_dct_id = dct_id

    def close_dct(self, dct_id: int):
        """
        Close a Dictionary and remove it from the Manager.

        Args:
            dct_id: Index of the Dictionary to close.

        Raises:
            KeyError: If the Dictionary index is out of range.
        """

        if not (0 <= dct_id < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')

        if len(self.opened_dct_bundles) == 1:
            self.active_dct_id = None
        elif dct_id < self.active_dct_id or self.active_dct_id == len(self.opened_dct_bundles) - 1:
            self.active_dct_id -= 1

        del self.opened_dct_bundles[dct_id]

    def save_dct(self, dct_id: int, filepath: str | None = None):
        """
        Save a Dictionary along with its Bundle to a file.

        Args:
            dct_id: Index of the Dictionary to save.
            filepath: Path where to save the Dictionary. If None, uses the Dictionary's current
                      filepath.

        Raises:
            KeyError: If the Dictionary index is out of range.
            ValueError: If no filepath is specified and the Dictionary has none.
        """

        if not (0 <= dct_id < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')

        filepath = filepath or self.opened_dct_bundles[dct_id].filepath

        if filepath is None:
            raise ValueError('No filepath was specified')

        if not os.path.exists(filepath):
            parent_dir = os.path.split(filepath)[0]
            os.makedirs(parent_dir, exist_ok=True)

        data = self.active.to_dict()
        with open(filepath, 'w') as file:
            json.dump(data, file)

        self.opened_dct_bundles[dct_id].filepath = filepath

        self.active.dct.mark_saved()

    def rename_dct(self, dct_id: int, new_name: str):
        """
        Rename a Dictionary.

        Args:
            dct_id: Index of the Dictionary to rename.
            new_name: New Dictionary name.

        Raises:
            KeyError: If the Dictionary index is out of range.
        """

        if not (0 <= dct_id < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')

        self.opened_dct_bundles[dct_id].dct.rename(new_name)

    def move_dct(self, from_index: int, to_index: int):
        """
        Reorder opened Dictionaries.

        Args:
            from_index: Index of the Dictionary to move.
            to_index: New index of the Dictionary.

        Raises:
            KeyError: If the Dictionary index is out of range.
        """

        if not (0 <= from_index < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')
        if not (0 <= to_index < len(self.opened_dct_bundles)):
            raise KeyError('Index out of range')

        target_dct = self.opened_dct_bundles[from_index]
        is_active = from_index == self.active_dct_id

        if not is_active and self.active_dct_id > from_index:
            self.active_dct_id -= 1

        del self.opened_dct_bundles[from_index]
        self.opened_dct_bundles = self.opened_dct_bundles[:to_index] + [target_dct] + \
                                  self.opened_dct_bundles[to_index:]

        if is_active:
            self.active_dct_id = to_index
        elif self.active_dct_id > to_index:
            self.active_dct_id += 1

    def to_dict(self) -> SerializedData:
        """
        Serialize the Manager state to a JSON format.

        Returns:
            Dict containing Manager data.
        """

        return {
            'version': self._schema_version,
            'data': {
                'opened_dct_bundles': [bundle.filepath for bundle in self.opened_dct_bundles],
                'active_dct_id': self.active_dct_id,
            }
        }

    def load_from_json_dict(self, data: SerializedData):
        """
        Deserialize Manager state from a JSON format.

        Args:
            data: Dictionary containing Manager data.
        """

        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('opened_dct_bundles', 'active_dct_id')
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        opened_dct_bundles = data['opened_dct_bundles']
        active_dct_id = data['active_dct_id']

        # Validate types
        validate_field_type('opened_dct_bundles', opened_dct_bundles, list[str])
        validate_field_type('active_dct_id', active_dct_id, (int, NoneType))

        # Read opened Dictionaries
        opened_dct_bundles = [self._load_dct(filepath) for filepath in data['opened_dct_bundles']]

        # Set attributes
        self.opened_dct_bundles = opened_dct_bundles
        self.active_dct_id = active_dct_id

    @staticmethod
    def _load_dct(filepath: str) -> DctBundle:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return DctBundle.from_dict(filepath, data)
