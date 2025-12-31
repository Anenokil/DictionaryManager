"""


Author: Anenokil
"""

from typing import Literal
import os
import json

from .core.types import SerializedData
from .core.errors import UnknownVersionError
from .core.utils import validate_required_fields, validate_field_type
from .manager import Manager


class GlobalSettings:
    schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        self.to_check_for_updates: bool = ...
        self.is_typo_btn_on: bool = ...

        if data is None:
            self.set_defaults()
        else:
            self.deserialize(data)

    def set_defaults(self):
        self.to_check_for_updates = True
        self.is_typo_btn_on = False

    def deserialize(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.to_check_for_updates: bool = data['to_check_for_updates']
        self.is_typo_btn_on: bool = data['is_typo_btn_on']

    def serialize(self) -> SerializedData:
        return {
            'version': self.schema_version,
            'to_check_for_updates': self.to_check_for_updates,
            'is_typo_btn_on': self.is_typo_btn_on,
        }

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            GlobalSettings._validate_data(data)
            return data
        raise UnknownVersionError(GlobalSettings.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        required_fields = ('to_check_for_updates', 'is_typo_btn_on')
        validate_required_fields(data, required_fields)

        validate_field_type('to_check_for_updates', data['to_check_for_updates'], bool)
        validate_field_type('is_typo_btn_on', data['is_typo_btn_on'], bool)


class GuiTKSettings:
    schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        self.theme: str = ...
        self.scale: int = ...

        if data is None:
            self.set_defaults()
        else:
            self.deserialize(data)

    def set_defaults(self):
       self.theme = 'light'
       self.scale = 10

    def deserialize(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.theme: str = data['theme']
        self.scale: int = data['scale']

    def serialize(self) -> SerializedData:
        return {
            'version': self.schema_version,
            'theme': self.theme,
            'scale': self.scale,
        }

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            GuiTKSettings._validate_data(data)
            return data
        raise UnknownVersionError(GuiTKSettings.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        required_fields = ('theme', 'scale')
        validate_required_fields(data, required_fields)

        validate_field_type('theme', data['theme'], str)
        validate_field_type('scale', data['scale'], int)


class AppData:
    schema_version = 1

    def __init__(self, path: str, gui: Literal['tk', 'qt']):
        assert gui in ('tk', 'qt')

        self.path = path
        self.gui = gui

        self.manager = Manager()
        self.global_settings = GlobalSettings()
        self.gui_settings = GuiTKSettings() if (gui == 'tk') else GuiQTSettings()

        if os.path.exists(path):
            self.load(True, True, True)
        else:
            folder, fn = os.path.split(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.path, 'w') as f:
                json.dump({}, f)
            self.save(True, True, True)

    def set_defaults(self, glob: bool = True, gui: bool = True):
        if glob:
           self.global_settings.set_defaults()
        if gui:
           self.gui_settings.set_defaults()

    def save(self, manager: bool = True, glob: bool = True, gui: bool = True):
        with open(self.path, 'r') as f:
            data = json.load(f)

        data['version'] = self.schema_version
        if manager:
            data['manager'] = self.manager.to_dict()
        if glob:
            data['global'] = self.global_settings.serialize()
        if gui:
            data[f'gui_{self.gui}'] = self.gui_settings.serialize()

        with open(self.path, 'w') as f:
            json.dump(data, f)

    def load(self, manager: bool = True, glob: bool = True, gui: bool = True):
        with open(self.path, 'r') as f:
            data = json.load(f)

        data = self._check_and_migrate(data)

        if manager:
            self.manager.load_from_json_dict(data['manager'])
        if glob:
            self.global_settings.deserialize(data['global'])
        if gui:
            self.gui_settings.deserialize(data[f'gui_{self.gui}'])

    def _check_and_migrate(self, data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            self._validate_data(data)
            return data
        raise UnknownVersionError(AppData.__name__, version)

    def _validate_data(self, data: SerializedData):
        required_fields = ('manager', 'global', f'gui_{self.gui}')
        validate_required_fields(data, required_fields)

        for field_name in required_fields:
            validate_field_type(field_name, data[field_name], SerializedData)
