"""
Implements the Manager class which stores Dictionaries and tracks the active one.

Author: Anenokil
"""

from types import NoneType
from typing import Callable
from abc import ABC, abstractmethod
import os

from .core.types import DctName, SerializedData
from .core.dictionary import Dictionary
from .core.trainer import TrainingConfig
from .core.utils import (
    validate_required_fields, validate_field_type,
    validation_and_migration, save_json, read_json,
)
from .replacements import Replacer


@validation_and_migration(1, [
    ('session_number', True, int),
])
class DctMetadata:
    def __init__(self, session_number: int = 1):
        self.session_number = session_number

    @classmethod
    def from_dict(cls, data: SerializedData):
        search_settings = cls()
        search_settings.load_from_dict(data)
        return search_settings

    def set_defaults(self):
        self.session_number = 1

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'data': {
                'session_number': self.session_number,
            }
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)
        data = data['data']

        self.session_number = data['session_number']

        self.session_number += 1


class OptionalDctData(ABC):
    @abstractmethod
    def __init__(self): ...

    @property
    @abstractmethod
    def filename(self) -> str: ...

    @abstractmethod
    def to_dict(self) -> SerializedData: ...

    @abstractmethod
    def load_from_dict(self, data: SerializedData): ...

    @abstractmethod
    def read_json(self, path: str) -> SerializedData: ...


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

    def __init__(self, optional_classes: dict[str, type[OptionalDctData]] | None = None):
        self.dct = Dictionary()
        self.metadata = DctMetadata()
        self.train_config = TrainingConfig()
        self.replacer = Replacer()
        self.optional: dict[str, OptionalDctData] = {
            name: optional_class()
            for name, optional_class in optional_classes.items()
        } if optional_classes is not None else {}

    @classmethod
    def from_files(cls, folder: str, optional_classes: dict[str, type[OptionalDctData]] | None = None):
        dct_bundle = cls(optional_classes)
        dct_bundle.read(folder)
        return dct_bundle

    @classmethod
    def from_dicts(
            cls,
            dct: SerializedData,
            metadata: SerializedData,
            train_config: SerializedData,
            replacer: SerializedData,
            optional: dict[str, tuple[type[OptionalDctData], SerializedData]],
    ):
        optional_classes = {name: pair[0] for name, pair in optional.items()}
        optional_data = {name: pair[1] for name, pair in optional.items()}

        dct_bundle = cls(optional_classes)
        dct_bundle.load_from_dicts(dct, metadata, train_config, replacer, optional_data)
        return dct_bundle

    @property
    def id(self) -> str:
        return self.dct.id

    def partial_save(
            self,
            folder: str,
            dct: bool = False,
            metadata: bool = False,
            train_config: bool = False,
            replacer: bool = False,
            optional: bool | set[str] = False,
    ):
        def save(data, filename: str):
            filepath = os.path.join(folder, filename)
            save_json(data.to_dict(), filepath)

        for data, filename, to_save in [
            (self.dct, 'dct.json', dct),
            (self.metadata, 'metadata.json', metadata),
            (self.train_config, 'train_config.json', train_config),
            (self.replacer, 'replacer.json', replacer),
        ]:
            if to_save:
                save(data, filename)

        if isinstance(optional, bool):
            if optional:
                for field_name, field in self.optional.items():
                    save(field, field.filename)
        elif isinstance(optional, set):
            for field_name in optional:
                field = self.optional[field_name]
                save(field, field.filename)

    def save(self, folder: str):
        self.partial_save(folder, True, True, True, True, True)

    def load_from_dicts(
            self,
            dct: SerializedData,
            metadata: SerializedData,
            train_config: SerializedData,
            replacer: SerializedData,
            optional: dict[str, SerializedData],
    ):
        self.dct.load_from_json_dict(dct)
        self.metadata.load_from_dict(metadata)
        self.train_config.load_from_dict(train_config)
        self.replacer.load_from_json_dict(replacer)
        for field_name, data in optional.items():
            self.optional[field_name].load_from_dict(data)

    def read(self, folder: str):
        self.load_from_dicts(
            read_json(os.path.join(folder, 'dct.json')),
            read_json(os.path.join(folder, 'metadata.json')),
            read_json(os.path.join(folder, 'train_config.json')),
            read_json(os.path.join(folder, 'replacer.json')),
            {
                name: field.read_json(os.path.join(folder, field.filename))
                for name, field in self.optional.items()
            }
        )


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
    def from_json_dict(cls, data: SerializedData, load_bundle_by_id: Callable[[str], DctBundle | None]) -> 'Manager':
        """
        Deserialize Manager state from a JSON format.

        Args:
            data: Dictionary containing Manager data.

        Returns:
            Manager object.
        """

        manager = cls()
        manager.load_from_json_dict(data, load_bundle_by_id)
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
            name: DctName = None,
            to_activate: bool = True,
            optional_classes: dict[str, type[OptionalDctData]] | None = None,
    ):
        """
        Create a new empty Dictionary and add it to the Manager.

        Args:
            filepath: Path where the Dictionary file will be saved.
            name: Name for the new Dictionary.
            to_activate: If True, switch the Manager's active Dictionary to the one just created.
                         If False, add it without switching the active index.
        """

        new_dct_bundle = DctBundle(optional_classes)
        new_dct_bundle.dct.rename(name)

        self.opened_dct_bundles.append(new_dct_bundle)

        if to_activate or self.n_opened == 1:
            self.active_dct_id = len(self.opened_dct_bundles) - 1

    def open_dct(
            self,
            folder: str,
            to_activate: bool = True,
            optional_classes: dict[str, type[OptionalDctData]] | None = None,
    ):
        """
        Load a Dictionary from a file and add it to the Manager.

        Args:
            filepath: Path to the Dictionary file to open.
            to_activate: If True, switch the Manager's active Dictionary to the one just opened.
                         If False, add it without switching the active index.

        Raises:
            FileNotFoundError: If the file does not exist.
        """

        dct_bundle = DctBundle.from_files(folder, optional_classes)
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

    def save_dct(self, dct_id: int, folder: str):
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

        if not os.path.exists(folder):
            os.makedirs(folder)

        bundle = self.opened_dct_bundles[dct_id]
        bundle.dct.mark_saved()
        bundle.save(folder)

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
                'opened_dct_bundles': [bundle.id for bundle in self.opened_dct_bundles],
                'active_dct_id': self.active_dct_id,
            }
        }

    def load_from_json_dict(self, data: SerializedData, load_bundle_by_id: Callable[[str], DctBundle | None]):
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
        opened_dct_bundles = [load_bundle_by_id(bundle_id) for bundle_id in data['opened_dct_bundles']]
        opened_dct_bundles = [bundle for bundle in opened_dct_bundles if bundle is not None]

        # Set attributes
        self.opened_dct_bundles = opened_dct_bundles
        self.active_dct_id = active_dct_id
