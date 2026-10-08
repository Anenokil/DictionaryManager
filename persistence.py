"""


Author: Anenokil
"""

from typing import Literal, Callable
import os
import json

from backend.core.types import SerializedData
from backend.core.errors import UnknownVersionError
from backend.core.utils import validate_required_fields, validate_field_type, validation_and_migration
from backend.manager import Manager, DctBundle


@validation_and_migration(1, [
    ('theme', True, str),
    ('scale', True, int),
    ('to_check_for_updates', True, bool),
    ('is_typo_btn_on', True, bool),
])
class UISettingsTK:
    def __init__(self, data: SerializedData | None = None):
        self.theme: str = ...
        self.scale: int = ...
        self.to_check_for_updates: bool = ...
        self.is_typo_btn_on: bool = ...

        if data is None:
            self.set_defaults()
        else:
            self.deserialize(data)

    def set_defaults(self):
        self.theme = 'light'
        self.scale = 10
        self.to_check_for_updates = True
        self.is_typo_btn_on = False

    def deserialize(self, data: SerializedData):
        data = self._check_and_migrate(data)
        data = data['data']

        self.theme: str = data['theme']
        self.scale: int = data['scale']
        self.to_check_for_updates: bool = data['to_check_for_updates']
        self.is_typo_btn_on: bool = data['is_typo_btn_on']

    def serialize(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'data': {
                'theme': self.theme,
                'scale': self.scale,
                'to_check_for_updates': self.to_check_for_updates,
                'is_typo_btn_on': self.is_typo_btn_on,
            }
        }


class UISettingsQT:
    schema_version = 1

    def __init__(self, data: SerializedData | None = None):
        if data is None:
            self.set_defaults()
        else:
            self.deserialize(data)

    def set_defaults(self):
        pass

    def deserialize(self, data: SerializedData):
        pass

    def serialize(self) -> SerializedData:
        return {
            'version': self.schema_version,
            'data': {}
        }


class AppData:
    _schema_version = 1

    def __init__(self, path: str, ui: Literal['tk', 'qt'], load_bundle_by_id: Callable[[str], DctBundle | None]):
        assert ui in ('tk', 'qt')

        self.path = path
        self.ui = ui
        self.load_bundle_by_id = load_bundle_by_id

        self.manager = Manager()
        self.ui_settings = UISettingsTK() if (ui == 'tk') else UISettingsQT()

        if os.path.exists(path):
            self.load(True, True)
        else:
            folder, fn = os.path.split(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.path, 'w') as f:
                json.dump({}, f)
            self.save(True, True)

    def set_defaults(self):
        self.ui_settings.set_defaults()

    def save(self, manager: bool = True, ui: bool = True):
        with open(self.path, 'r') as f:
            data = json.load(f)

        data = self._check_and_migrate(data)

        data['version'] = self._schema_version
        data['data'] = {}

        if manager:
            data['data']['manager'] = self.manager.to_dict()
        if ui:
            data['data'][f'ui_{self.ui}'] = self.ui_settings.serialize()

        with open(self.path, 'w') as f:
            json.dump(data, f)

    def load(self, manager: bool = True, ui: bool = True):
        with open(self.path, 'r') as f:
            data = json.load(f)

        data = self._check_and_migrate(data)
        data = data['data']

        if manager:
            self.manager.load_from_json_dict(data['manager'], self.load_bundle_by_id)
        if ui:
            self.ui_settings.deserialize(data[f'ui_{self.ui}'])

    def _check_and_migrate(self, data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version = data['version']
        if not (1 <= version <= self._schema_version):
            raise UnknownVersionError(self.__class__.__name__, version)

        self._validate_data(data)
        return data

    def _validate_data(self, data: SerializedData):
        validate_required_fields(data, ('data',))
        validate_field_type('data', data['data'], SerializedData)

        payload = data['data']

        required_fields = ('manager', f'ui_{self.ui}')
        validate_required_fields(payload, required_fields)

        for field_name in required_fields:
            validate_field_type(field_name, payload[field_name], SerializedData)
