"""
Implements GUI using tkinter.

Author: Anenokil
"""

from types import NoneType
from typing import Any, Literal, TypeVar, Type, Callable, Iterable
import inspect
import math
import re
import platform
from pathlib import Path
import shutil
import platformdirs
import unicodedata
import json
import webbrowser
import urllib.request as urllib2
import wget
import zipfile

import tkinter as tk
from tkinter import colorchooser
from tkinter.font import Font
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
import tkinter.ttk as ttk
import idlelib.tooltip as ttip

from backend import (
    Entry, Dictionary, OptionalDctData, DctBundle, Manager, Replacer,
    Trainer, TrainingConfig, TrainingFormat, TrainingOrder, EntrySelection, FormSelection,
    GramForm, WordForm, gram_form_to_str, Tag, SerializedData, validation_and_migration,
    get_dct_name_from_dict, get_dct_id_from_dict, set_dct_name_in_dict, read_json, save_json,
)
from constants import (
    SCALE_SMALL_FRAME_HEIGHT_SHORT, SCALE_SMALL_FRAME_HEIGHT_TALL, SCALE_CUSTOM_THEME_FRAME_WIDTH,
    SCALE_MAX, SCALE_MIN, SCALE_SMALL_FRAME_WIDTH, SCALE_DEFAULT_FRAME_WIDTH,
    SCALE_CUSTOM_THEME_COMBO_WIDTH, RET_TH_OLD, RET_TH_OK,
    SCALE_DEFAULT_FRAME_HEIGHT, SCALE_FRAME_HEIGHT_ONE_LINE, PROGRAM_VERSION, REQUIRED_THEME_VERSION,
    IMG_NAMES, ICON_NAMES, PROGRAM_DATE, PROGRAM_TIME, EXIT_UPDATE, PROGRAM_NAME, ALL_TAGS,

    LEARN_VALUES_WORDS, LEARN_VALUES_FORMS, LEARN_VALUES_FORMAT, LEARN_VALUES_ORDER,
    PRINT_VALUES_ORDER,
)
from upgrades import upgrade_theme

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / 'resources' / 'tk'
ICON_PATH = str(RESOURCES_DIR / 'icon.png')
THEMES_DIR = RESOURCES_DIR / 'themes'
CUSTOM_THEME_DIR = RESOURCES_DIR / 'custom_theme'
STYLES_FN = 'styles.txt'
IMAGES_DIR = RESOURCES_DIR / 'images'
IMG_ADD_PATH = str(IMAGES_DIR / 'add.png')

DATA_DIR = Path(platformdirs.user_data_dir('DictionaryManager'))
MANAGER_PATH = str(DATA_DIR / 'manager_tk.json')
GUI_CONFIG_PATH = str(DATA_DIR / 'tk_config.json')
SAVES_DIR = DATA_DIR / 'saves'
DCT_SAVE_DIR = lambda dct_id: SAVES_DIR / dct_id
DCT_MAIN_DATA_FILENAME = 'dct.json'
DCT_MAIN_DATA_PATH = lambda dct_id: str(DCT_SAVE_DIR(dct_id) / DCT_MAIN_DATA_FILENAME)
DCT_METADATA_FILENAME = 'metadata.json'
DCT_PRACTICE_CONFIG_FILENAME = 'train_config.json'
DCT_REPLACER_FILENAME = 'replacer.json'
DCT_GUI_DATA_FILENAME = 'tk_config.json'
DCT_GUI_DATA_PATH = lambda dct_id: str(DCT_SAVE_DIR(dct_id) / DCT_GUI_DATA_FILENAME)

REPOSITORY_NAME = 'DictionaryManager'
URL_GITHUB = f'https://github.com/Anenokil/{REPOSITORY_NAME}'
URL_RELEASES = f'https://github.com/Anenokil/{REPOSITORY_NAME}/releases'
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/dev/ver'
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/archive/refs/heads/dev.zip'

NEW_VERSION_DIRNAME = f'{REPOSITORY_NAME}-master'
NEW_VERSION_DIR = BASE_DIR / NEW_VERSION_DIRNAME
NEW_VERSION_ZIP_PATH = BASE_DIR / f'{NEW_VERSION_DIRNAME}.zip'
UPDATE_FILES_FILENAME = 'update_files'

CompoundValues = Literal['none', 'image', 'text', 'left', 'right', 'top', 'bottom', 'center']
T = TypeVar('T', bound=ttk.Widget)

""" Темы """

CUSTOM_TH = '</custom\\>'
THEMES = [CUSTOM_TH, 'light', 'dark']
DEFAULT_TH = THEMES[1]

# {стилизуемый_элемент: (описание, {тема: стиль})}
STYLES = {
    '*.BG.*':              ('Цвет фона окна',                                {THEMES[1]: '#F0F0F0', THEMES[2]: '#222222'}),
    '*.BG.ENTRY':          ('Цвет фона полей ввода',                         {THEMES[1]: '#FFFFFF', THEMES[2]: '#171717'}),
    '*.FG.*':              ('Цвет обычного текста',                          {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    '*.FG.LOGO':           ('Цвет текста логотипа',                          {THEMES[1]: '#FF8800', THEMES[2]: '#AA4600'}),
    '*.FG.FOOTER':         ('Цвет текста нижнего колонтитула',               {THEMES[1]: '#666666', THEMES[2]: '#666666'}),
    '*.FG.WARN':           ('Цвет текста предупреждения',                    {THEMES[1]: '#DD2222', THEMES[2]: '#DD2222'}),
    '*.FG.ENTRY':          ('Цвет вводимого текста',                         {THEMES[1]: '#222222', THEMES[2]: '#777777'}),
    '*.BG.SEL':            ('Цвет выделения фона',                           {THEMES[1]: '#BBBBBB', THEMES[2]: '#444444'}),
    '*.FG.SEL':            ('Цвет выделения текста',                         {THEMES[1]: '#101010', THEMES[2]: '#A0A0A0'}),
    'BTN.BG.*':            ('Цвет фона обычных кнопок',                      {THEMES[1]: '#D0D0D0', THEMES[2]: '#1E1E1E'}),
    'BTN.BG.ACT':          ('Цвет фона обычных кнопок при нажатии',          {THEMES[1]: '#BABABA', THEMES[2]: '#1A1A1A'}),
    'BTN.BG.Y':            ('Цвет фона да-кнопок',                           {THEMES[1]: '#88DD88', THEMES[2]: '#446F44'}),
    'BTN.BG.Y_ACT':        ('Цвет фона да-кнопок при нажатии',               {THEMES[1]: '#77CC77', THEMES[2]: '#558055'}),
    'BTN.BG.N':            ('Цвет фона нет-кнопок',                          {THEMES[1]: '#FF6666', THEMES[2]: '#803333'}),
    'BTN.BG.N_ACT':        ('Цвет фона нет-кнопок при нажатии',              {THEMES[1]: '#EE5555', THEMES[2]: '#904444'}),
    'BTN.BG.IMG_HOV':      ('Цвет фона кнопок-картинок при наведении',       {THEMES[1]: '#E0E0E0', THEMES[2]: '#1E1E1E'}),
    'BTN.BG.IMG_ACT':      ('Цвет фона кнопок-картинок при нажатии',         {THEMES[1]: '#D0D0D0', THEMES[2]: '#1A1A1A'}),
    'BTN.BG.DISABL':       ('Цвет фона выключенных кнопок',                  {THEMES[1]: '#D9D9D9', THEMES[2]: '#1E1E1E'}),
    'BTN.FG.DISABL':       ('Цвет текста выключенных кнопок',                {THEMES[1]: '#B0B0B0', THEMES[2]: '#454545'}),
    'FLAT_BTN.BG.1':       ('Цвет фона кнопок-записей (1)',                  {THEMES[1]: '#FFFFFF', THEMES[2]: '#171717'}),
    'FLAT_BTN.BG.2':       ('Цвет фона кнопок-записей (2)',                  {THEMES[1]: '#FAFAFA', THEMES[2]: '#171717'}),
    'FLAT_BTN.BG.HOV':     ('Цвет фона кнопок-записей при наведении',        {THEMES[1]: '#E0F1FF', THEMES[2]: '#1B1B1B'}),
    'FLAT_BTN.BG.ACT':     ('Цвет фона кнопок-записей при нажатии',          {THEMES[1]: '#CCE8FF', THEMES[2]: '#1F1F1F'}),
    'FLAT_BTN.FG.1':       ('Цвет текста кнопок-записей (1)',                {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.2':       ('Цвет текста кнопок-записей (2)',                {THEMES[1]: '#202020', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.HOV':     ('Цвет текста кнопок-записей при наведении',      {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.ACT':     ('Цвет текста кнопок-записей при нажатии',        {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FLAT_BTN.BG.SEL_1':   ('Цвет фона выдел. кн.-записей (1)',              {THEMES[1]: '#CCFFE8', THEMES[2]: '#1B1B22'}),
    'FLAT_BTN.BG.SEL_2':   ('Цвет фона выдел. кн.-записей (2)',              {THEMES[1]: '#C7FAE3', THEMES[2]: '#1B1B22'}),
    'FLAT_BTN.BG.SEL_HOV': ('Цвет фона выдел. кн.-записей при наведении',    {THEMES[1]: '#A8FFD6', THEMES[2]: '#1B1B2A'}),
    'FLAT_BTN.BG.SEL_ACT': ('Цвет фона выдел. кн.-записей при нажатии',      {THEMES[1]: '#82FFC4', THEMES[2]: '#1B1B31'}),
    'FLAT_BTN.FG.SEL_1':   ('Цвет текста выдел. кн.-записей (1)',            {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.SEL_2':   ('Цвет текста выдел. кн.-записей (2)',            {THEMES[1]: '#202020', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.SEL_HOV': ('Цвет текста выдел. кн.-записей при наведении',  {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FLAT_BTN.FG.SEL_ACT': ('Цвет текста выдел. кн.-записей при нажатии',    {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'CHECK.BG.SEL':        ('Цвет фона переключателя при наведении на него', {THEMES[1]: '#DDDDDD', THEMES[2]: '#333333'}),
    'SCROLL.BG.*':         ('Цвет фона ползунка',                            {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}),
    'SCROLL.BG.ACT':       ('Цвет фона ползунка при нажатии',                {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}),
    'SCROLL.FG.*':         ('Цвет ползунка',                                 {THEMES[1]: '#CACACA', THEMES[2]: '#292929'}),
    'SCROLL.FG.ACT':       ('Цвет ползунка при нажатии',                     {THEMES[1]: '#ABABAB', THEMES[2]: '#333333'}),
    'TAB.BG.*':            ('Цвет фона закрытой вкладки',                    {THEMES[1]: '#D0D0D0', THEMES[2]: '#1A1A1A'}),
    'TAB.BG.SEL':          ('Цвет фона открытой вкладки',                    {THEMES[1]: '#EAEAEA', THEMES[2]: '#222222'}),
    'TAB.FG.*':            ('Цвет текста закрытой вкладки',                  {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'TAB.FG.SEL':          ('Цвет текста открытой вкладки',                  {THEMES[1]: '#222222', THEMES[2]: '#979797'}),
    'FRAME.RELIEF.*':      ('Стиль рамок фреймов',                           {THEMES[1]: 'groove',  THEMES[2]: 'solid'  }),
    'TXT.RELIEF.*':        ('Стиль рамок текстовых полей',                   {THEMES[1]: 'sunken',  THEMES[2]: 'solid'  }),
    '*.BORDER_CLR.*':      ('Цвет рамок',                                    {THEMES[1]: '#222222', THEMES[2]: '#111111'}),
}
STYLE_KEYS = list(STYLES.keys())


@validation_and_migration(1, [
    ('search_page_to_match_whole_word', False, bool),
    ('search_page_to_search_in_words', False, bool),
    ('search_page_to_search_in_translations', False, bool),
    ('search_page_to_search_in_forms', False, bool),
    ('search_page_to_search_in_phrases', False, bool),
    ('search_page_to_search_in_notes', False, bool),
    ('search_page_to_filter_fav', False, bool),
    ('search_page_search_tag', False, (str, NoneType)),
])
class DctUISettings(OptionalDctData):
    _filename = DCT_GUI_DATA_FILENAME

    def __init__(self, data: SerializedData | None = None):
        self.search_page_to_match_whole_word: bool = ...
        self.search_page_to_search_in_words: bool = ...
        self.search_page_to_search_in_translations: bool = ...
        self.search_page_to_search_in_forms: bool = ...
        self.search_page_to_search_in_phrases: bool = ...
        self.search_page_to_search_in_notes: bool = ...
        self.search_page_to_filter_fav: bool = ...
        self.search_page_search_tag: str | None = ...

        if data is None:
            self.set_defaults()
        else:
            self.load_from_dict(data)

    @property
    def filename(self) -> str:
        return self._filename

    @classmethod
    def from_json(cls, path: str) -> 'DctUISettings':
        instance = cls()
        instance.load_from_json(path)
        return instance

    def set_defaults(self):
        self.search_page_to_match_whole_word = False
        self.search_page_to_search_in_words = True
        self.search_page_to_search_in_translations = True
        self.search_page_to_search_in_forms = False
        self.search_page_to_search_in_phrases = False
        self.search_page_to_search_in_notes = False
        self.search_page_to_filter_fav = False
        self.search_page_search_tag = None

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)
        data = data['data']

        self.search_page_to_match_whole_word: bool = data['search_page_to_match_whole_word']
        self.search_page_to_search_in_words: bool = data['search_page_to_search_in_words']
        self.search_page_to_search_in_translations: bool = data['search_page_to_search_in_translations']
        self.search_page_to_search_in_forms: bool = data['search_page_to_search_in_forms']
        self.search_page_to_search_in_phrases: bool = data['search_page_to_search_in_phrases']
        self.search_page_to_search_in_notes: bool = data['search_page_to_search_in_notes']
        self.search_page_to_filter_fav: bool = data['search_page_to_filter_fav']
        self.search_page_search_tag: str | None = data['search_page_search_tag']

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'data': {
                'search_page_to_match_whole_word': self.search_page_to_match_whole_word,
                'search_page_to_search_in_words': self.search_page_to_search_in_words,
                'search_page_to_search_in_translations': self.search_page_to_search_in_translations,
                'search_page_to_search_in_forms': self.search_page_to_search_in_forms,
                'search_page_to_search_in_phrases': self.search_page_to_search_in_phrases,
                'search_page_to_search_in_notes': self.search_page_to_search_in_notes,
                'search_page_to_filter_fav': self.search_page_to_filter_fav,
                'search_page_search_tag': self.search_page_search_tag,
            }
        }

    def read_json(self, path: str) -> SerializedData:
        if not Path(path).exists():
            self.set_defaults()
            return self.to_dict()

        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def load_from_json(self, path: str):
        data = self.read_json(path)
        self.load_from_dict(data)

    def save_to_json(self, path: str):
        data = self.to_dict()
        with open(path, 'w') as f:
            json.dump(data, f)


@validation_and_migration(1, [
    ('theme', False, str),
    ('scale', False, int),
    ('to_check_for_updates', False, bool),
    ('is_typo_btn_on', False, bool),
])
class UISettings:
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


class AppData:
    def __init__(self):
        self.manager = Manager()
        self.ui_settings = UISettings()

        if Path(MANAGER_PATH).exists():
            self.load(True, True)
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.save(True, True)

    @staticmethod
    def load_bundle_by_id(bundle_id: str) -> DctBundle | None:
        folder = DCT_SAVE_DIR(bundle_id)
        if not folder.exists():
            return None
        return DctBundle.from_files(folder, {'tk': DctUISettings})

    def save(self, manager: bool = True, ui: bool = True):
        if manager:
            save_json(self.manager.to_dict(), MANAGER_PATH)
        if ui:
            save_json(self.ui_settings.serialize(), GUI_CONFIG_PATH)

    def load(self, manager: bool = True, ui: bool = True):
        if manager:
            self.manager.load_from_json_dict(read_json(MANAGER_PATH), self.load_bundle_by_id)
        if ui:
            self.ui_settings.deserialize(read_json(GUI_CONFIG_PATH))


""" Функции проверки """


def check_dct_name(window_parent: tk.Misc, app_data: AppData, name: str) -> bool:
    """Validate a dictionary name."""

    if len(name) > 100:
        warning(window_parent, app_data, 'Название слишком длинное (> 100)!')
        return False
    if name == '':
        warning(window_parent, app_data, 'Название должно содержать хотя бы один символ!')
        return False
    return True


def check_variant(
        window_parent: tk.Misc,
        app_data: AppData,
        variants: list[str] | tuple[str, ...],
        new_variant: str,
        lemma: str,
) -> bool:
    """Validate a new word variant."""

    if new_variant == '':
        warning(window_parent, app_data, 'Вариант написания должен содержать хотя бы один символ!')
        return False
    if new_variant in variants:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть такой вариант написания!')
        return False
    return True


def check_variant_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        variants: list[str] | tuple[str, ...],
        old_variant: str,
        new_variant: str,
        lemma: str,
) -> bool:
    """Validate a word variant on edit."""

    if new_variant == '':
        warning(window_parent, app_data, 'Вариант написания должен содержать хотя бы один символ!')
        return False
    if new_variant in variants and new_variant != old_variant:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть вариант написания!')
        return False
    return True


def check_tr(
        window_parent: tk.Misc,
        app_data: AppData,
        translations: list[str] | tuple[str, ...],
        new_tr: str,
        lemma: str,
) -> bool:
    """Validate a new translation."""

    if new_tr == '':
        warning(window_parent, app_data, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть такой перевод!')
        return False
    return True


def check_tr_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        translations: list[str] | tuple[str, ...],
        old_tr: str,
        new_tr: str,
        lemma: str,
) -> bool:
    """Validate a translation on edit."""

    if new_tr == '':
        warning(window_parent, app_data, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations and new_tr != old_tr:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть такой перевод!')
        return False
    return True


def check_phr(
        window_parent: tk.Misc,
        app_data: AppData,
        phrases: dict[str, list[str]],
        new_phrase_pair: tuple[str, str],
        lemma: str,
) -> bool:
    """Validate a new phrase."""

    phrase, phrase_tr = new_phrase_pair

    if phrase == '' or phrase_tr == '':
        warning(window_parent, app_data, 'Фраза должна содержать хотя бы один символ!')
        return False
    if phrase in phrases and phrase_tr in phrases[phrase]:
        warning(window_parent, app_data, f'Со словом "{lemma}" уже есть такая фраза!')
        return False
    return True


def check_phr_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        phrases: dict[str, list[str]],
        old_phrase_pair: tuple[str, str],
        new_phrase_pair: tuple[str, str],
        lemma: str,
) -> bool:
    """Validate a phrase on edit."""

    new_phrase, new_phrase_tr = new_phrase_pair

    if new_phrase == '' or new_phrase_tr == '':
        warning(window_parent, app_data, 'Фраза должна содержать хотя бы один символ!')
        return False
    if (
            (new_phrase in phrases) and
            (new_phrase_tr in phrases[new_phrase]) and
            (new_phrase_pair != old_phrase_pair)
    ):
        warning(window_parent, app_data, f'Со словом "{lemma}" уже есть такая фраза!')
        return False
    return True


def check_note(
        window_parent: tk.Misc,
        app_data: AppData,
        notes: list[str] | tuple[str, ...],
        new_note: str,
        lemma: str,
) -> bool:
    """Validate a new note."""

    if new_note == '':
        warning(window_parent, app_data, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть такая сноска!')
        return False
    return True


def check_note_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        notes: list[str] | tuple[str, ...],
        old_note: str,
        new_note: str,
        lemma: str,
) -> bool:
    """Validate a note on edit."""

    if new_note == '':
        warning(window_parent, app_data, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes and new_note != old_note:
        warning(window_parent, app_data, f'У слова "{lemma}" уже есть такая сноска!')
        return False
    return True


def check_tag_name(
        window_parent: tk.Misc,
        app_data: AppData,
        tags: list[str] | tuple[str, ...],
        new_tag: str,
) -> bool:
    """Validate a new tag."""

    if new_tag == '':
        warning(window_parent, app_data, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_tag == ALL_TAGS:
        warning(window_parent, app_data, 'Группа не может иметь такое название!')
        return False
    if new_tag in tags:
        warning(window_parent, app_data, f'Группа "{new_tag}" уже существует!')
        return False
    return True


def check_tag_name_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        tags: list[str] | tuple[str, ...],
        old_tag: str,
        new_tag: str,
) -> bool:
    """Validate a tag on edit."""

    if new_tag == '':
        warning(window_parent, app_data, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_tag == ALL_TAGS:
        warning(window_parent, app_data, 'Группа не может иметь такое название!')
        return False
    if new_tag in tags and new_tag != old_tag:
        warning(window_parent, app_data, f'Группа "{new_tag}" уже существует!')
        return False
    return True


def check_ctg(
        window_parent: tk.Misc,
        app_data: AppData,
        categories: list[str] | tuple[str, ...],
        new_ctg: str,
) -> bool:
    """Validate a new category name."""

    if new_ctg == '':
        warning(window_parent, app_data, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories:
        warning(window_parent, app_data, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


def check_ctg_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        categories: list[str] | tuple[str, ...],
        old_ctg: str,
        new_ctg: str,
) -> bool:
    """Validate a category name on edit."""

    if new_ctg == '':
        warning(window_parent, app_data, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories and new_ctg != old_ctg:
        warning(window_parent, app_data, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


def check_ctg_val(
        window_parent: tk.Misc,
        app_data: AppData,
        ctg_values: list[str] | tuple[str, ...],
        new_value: str,
) -> bool:
    """Validate a new category value."""

    if new_value == '':
        warning(window_parent, app_data, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_value in ctg_values:
        warning(window_parent, app_data, f'Значение "{new_value}" уже существует!')
        return False
    return True


def check_ctg_val_edit(
        window_parent: tk.Misc,
        app_data: AppData,
        ctg_values: list[str] | tuple[str, ...],
        old_value: str,
        new_value: str,
) -> bool:
    """Validate a category value on edit."""

    if new_value == '':
        warning(window_parent, app_data, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_value in ctg_values and new_value != old_value:
        warning(window_parent, app_data, f'Значение "{new_value}" уже существует!')
        return False
    return True


def is_separator(char: str) -> bool:
    return not (char.isalnum() or char in '()[]{}<>_-+*%!?.,;:`"\'')


""" Функции вывода """


def variants_repr(entry: Entry) -> str:
    res = str(entry.lemma)
    if entry.n_variants > 1:
        res += f' ({", ".join(entry.variants[1:])})'
    return res


def tr_repr(entry: Entry) -> str:
    return ', '.join(entry.tr)


def forms_repr(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join((
        f'[{gram_form_to_str(gram_form)}] {", ".join(word_form)}'
        for gram_form, word_form in entry.forms.items()
    ))


def phrase_tr_repr(entry: Entry, phrase: str) -> str:
    return ', '.join(entry.phrases[phrase])


def phrases_repr(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join((
        f'{phrase} - {phrase_tr_repr(entry, phrase)}'
        for phrase in entry.phrases
    ))


def notes_repr(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join(entry.notes)


def tags_repr(entry: Entry) -> str:
    if entry.tags:
        return ', '.join(entry.tags)
    return '-'


def win_streak_repr(entry: Entry) -> str:
    if entry.total_att == 0:
        return '-'
    if entry.win_streak > 999:
        return '+∞'
    if entry.win_streak < -99:
        return '-∞'
    return str(entry.win_streak)


def accuracy_repr(entry: Entry) -> str:
    if entry.total_att == 0:
        return '-'
    return '{:.0%}'.format(entry.accuracy)


def entry_stats_repr(entry: Entry) -> str:
    win_streak = win_streak_repr(entry)
    accuracy = accuracy_repr(entry)
    tab_win_streak = ' ' * (3 - len(str(win_streak)))
    tab_accuracy = ' ' * (4 - len(accuracy))
    return f'[{tab_win_streak}{win_streak}:{tab_accuracy}{accuracy}]'


def _entry_repr_brief(entry: Entry) -> str:
    fav = '(*)' if entry.is_fav else '   '
    return f'{fav} {entry_stats_repr(entry)} {variants_repr(entry)}: {tr_repr(entry)}'


def entry_repr_brief(entry: Entry, str_len: int) -> str:
    return split_text(_entry_repr_brief(entry), str_len, tab=15)


def entry_repr_details(entry: Entry, str_len: int) -> str:
    res = _entry_repr_brief(entry)
    if entry.n_gram_forms != 0:
        res += f'\n  Формы слова: {forms_repr(entry, tab=15)}'
    if entry.phrases.keys():
        res += f'\n        Фразы: {phrases_repr(entry, tab=15)}'
    if entry.n_notes != 0:
        res += f'\n       Сноски: {notes_repr(entry, tab=15)}'
    if entry.tags:
        res += f'\n       Группы: {tags_repr(entry)}'
    return split_text(res, str_len, tab=15)


def entry_repr_complete(entry: Entry, str_len: int, tab: int = 0) -> str:
    res  = f'      Слово: {variants_repr(entry)}\n'
    res += f'    Перевод: {tr_repr(entry)}\n'

    res += f'Формы слова: '
    if entry.n_gram_forms == 0:
        res += '-\n'
    else:
        gram_forms = tuple(entry.forms.keys())
        res += f'[{gram_form_to_str(gram_forms[0])}] {", ".join(entry.forms[gram_forms[0]])}\n'
        for i in range(1, entry.n_gram_forms):
            res += f'             [{gram_form_to_str(gram_forms[i])}] '\
                   f'{", ".join(entry.forms[gram_forms[i]])}\n'

    res += '      Фразы: '
    res += '-' if entry.n_phrases == 0 else phrases_repr(entry, tab=13)

    res += '\n     Сноски: '
    res += '-' if entry.n_notes == 0 else notes_repr(entry, tab=13)

    res += '\n  Избранное: '
    res += '+' if entry.is_fav else '-'

    res += f'\n     Группы: {tags_repr(entry)}\n'

    if entry.total_att == 0:
        res += ' Статистика: 1) Верных ответов подряд: -\n'
        res += '             2) Доля верных ответов: -'
    else:
        res += f' Статистика: 1) Верных ответов подряд: {entry.win_streak}\n'
        res += f'             2) Доля верных ответов: '
        res += f'{entry.correct_att}/{entry.total_att} = ' + '{:.0%}'.format(entry.accuracy)

    return split_text(res, str_len, tab=tab)


def lemma_and_stats_repr(entry: Entry) -> str:
    return f'{variants_repr(entry)} {entry_stats_repr(entry)}'


def tr_and_stats_repr(entry: Entry) -> str:
    return f'{tr_repr(entry)} {entry_stats_repr(entry)}'


def tr_and_forms_and_stats_repr(entry: Entry, gram_form: Iterable[str]) -> str:
    return f'{tr_repr(entry)} ({gram_form_to_str(gram_form)}) {entry_stats_repr(entry)}'


def phrase_and_stats_repr(entry: Entry, phrase: str) -> str:
    return f'{phrase} {entry_stats_repr(entry)}'


def phrase_tr_and_stats_repr(entry: Entry, phrase: str) -> str:
    return f'{phrase_tr_repr(entry, phrase)} {entry_stats_repr(entry)}'


def dct_stats_repr(count_e: int, count_t: int, count_wf: int) -> str:
    w = select_word_form(count_e, ('слово', 'слова', 'слов'))
    f = select_word_form(count_e + count_wf, ('словоформа', 'словоформы', 'словоформ'))
    t = select_word_form(count_t, ('перевод', 'перевода', 'переводов'))
    return f'[ {count_e} {w} | {count_e + count_wf} {f} | {count_t} {t} ]'


def dct_fav_stats_repr(
        count_e: tuple[int, int],
        count_t: tuple[int, int],
        count_wf: tuple[int, int],
) -> str:
    w = select_word_form(count_e[0], ('слово', 'слова', 'слов'))
    f = select_word_form(count_e[0] + count_wf[0], ('словоформа', 'словоформы', 'словоформ'))
    t = select_word_form(count_t[0], ('перевод', 'перевода', 'переводов'))
    return (
        f'[ {count_e[0]}/{count_e[1]} {w} '
        f'| {count_e[0] + count_wf[0]}/{count_e[1] + count_wf[1]} {f} '
        f'| {count_t[0]}/{count_t[1]} {t} ]'
    )


def replacement_repr(input_pair: tuple[str, str], output: str) -> str:
    return f'{input_pair[0]}{input_pair[1]} -> {output}'


""" Вспомогательные функции """


def word_in_line(word: str, line: str) -> bool:
    words = re.split(r'[.,;:!? \n()\[\]{}]', line)
    words = {w for w in words if w != ''}
    return word in words


def normalize(text: str) -> str:
    """
    Convert text to lowercase without diacritics for accent-insensitive search.

    Letters that Unicode decomposition doesn't split (ß, æ, œ, ø) are first
    replaced with their ASCII equivalents.
    """

    special_map = {
        'ß': 'ss', 'ẞ': 'SS',
        'æ': 'ae', 'Æ': 'AE',
        'œ': 'oe', 'Œ': 'OE',
        'ø': 'o',  'Ø': 'O',
    }

    text = ''.join(special_map.get(ch, ch) for ch in text)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def split_line(line: str) -> list[list[str]]:
    """
    Split a line into words and the separators that follow them.

    A separator is any character for which is_separator returns True.
    A word is a maximal run of non-separator characters.
    Each word is paired with the run of separators right after it;
    for the last word the separator part may be empty;
    If the line starts with separators, they form the first pair
    with an empty word.

    Args:
        line: The line to split.

    Returns:
        A list of (word, separator) pairs. Joining all words and separators
        in order restores the original line. An empty line gives an empty list.
    """

    line_len = len(line)
    res = []

    i = 0
    while i < line_len and is_separator(line[i]):
        i += 1
    if i != 0:
        res.append(['', line[0:i]])

    while i < line_len:
        word = ''
        separator = ''
        while i < line_len and not is_separator(line[i]):
            word += line[i]
            i += 1
        while i < line_len and is_separator(line[i]):
            separator += line[i]
            i += 1
        res.append([word, separator])

    return res


def split_text(text: str, max_str_len: int, tab: int = 0, to_add_right_spaces: bool = True) -> str:
    """
    Wrap text so that no line is longer than the specified value.

    Existing line breaks are preserved: each line of the input is wrapped
    independently. Lines are broken between words (see split_line). A word
    or a separator that is longer than the space available is split across
    lines, so no characters are lost.

    Lines created by wrapping (continuation lines) are indented by spaces;
    the first line of each source line is not indented.

    Args:
        text: The text to wrap.
        max_str_len: Maximum line length. Must be positive.
        tab: Number of spaces to indent continuation lines. Must be
             non-negative and less than max_str_len.
        to_add_right_spaces: If True, pad every line with trailing spaces
                             up to exactly max_str_len characters.

    Returns:
        The wrapped text, with lines separated by newlines.

    Raises:
        AssertionError: If max_str_len or tab is out of the allowed range.
    """

    assert max_str_len > 0
    assert tab >= 0
    assert tab < max_str_len

    res = ''
    lines = text.split('\n')
    n_lines = len(lines)
    for i in range(n_lines):
        line = lines[i]
        line_len = len(line)
        # Если ширина строки соответствует требованиям, то просто записываем эту строку
        if line_len <= max_str_len:
            res += line
            if to_add_right_spaces:
                res += ' ' * (max_str_len - line_len)
        else:
            current_len = 0
            to_indent = False
            words = split_line(line)
            for word, separator in words:
                word_len = len(word)
                separator_len = len(separator)

                # Если слово превышает максимальную длину строки, то разбиваем его на части
                if word_len > max_str_len or (to_indent and tab + word_len > max_str_len):
                    rem_len = max_str_len - current_len
                    res += word[0:rem_len]
                    res += ''.join([
                        '\n' + ' ' * tab + word[i:i+max_str_len-tab]
                        for i in range(rem_len, word_len, max_str_len-tab)
                    ])
                    current_len = tab + (word_len - rem_len) % (max_str_len - tab)
                    to_indent = True
                # Если слово не вмещается в данную строку, но может вместиться в следующую,
                # то записываем его в следующую
                elif word_len + current_len > max_str_len:
                    if to_add_right_spaces:
                        res += ' ' * (max_str_len - current_len)
                    res += '\n'
                    res += ' ' * tab
                    res += word
                    current_len = tab + word_len
                    to_indent = True
                # Если слово вмещается в данную строку, то просто записываем его
                else:
                    res += word
                    current_len += word_len

                # Если разделитель целиком не вмещается в данную строку, то разделяем его на части
                if current_len + separator_len > max_str_len:
                    rem_len = max_str_len - current_len
                    res += separator[0:rem_len]
                    res += ''.join([
                        '\n' + ' ' * tab + separator[i:i+max_str_len-tab]
                        for i in range(rem_len, separator_len, max_str_len-tab)
                    ])
                    current_len = tab + (separator_len - rem_len) % (max_str_len - tab)
                    to_indent = True
                # Если разделитель вмещается в данную строку целиком, то просто записываем его
                else:
                    res += separator
                    current_len += separator_len
            if to_add_right_spaces:
                res += ' ' * (max_str_len - current_len)
        if i != n_lines - 1:
            res += '\n'
    return res


def select_word_form(n: int, word_forms: tuple[str, str, str]) -> str:
    """
    Choose the Russian word form that agrees with the number n.

    Args:
        n: The quantity.
        word_forms: Forms for 1, for 2-4, and for 5+ items.

    Returns:
        Word form.
    """

    if 5 <= n % 100 <= 20:
        return word_forms[2]
    if n % 10 == 1:
        return word_forms[0]
    if 1 < n % 10 < 5:
        return word_forms[1]
    return word_forms[2]


""" Основные функции """


def select_entry(app_data: AppData, window_parent: tk.Misc, lemma: str) -> Entry | None:
    """Choose one entry from several entries with the same word (homographs)."""

    homographs = app_data.manager.active.dct.search(variants=[lemma])
    if len(homographs) == 1:
        return homographs.pop()
    result = SelectEntryFromHomographsW(window_parent, app_data, lemma).open()
    return result


def edit_variant_or_merge(
        app_data: AppData,
        window_parent: tk.Misc,
        entry: Entry,
        old_variant: str,
        new_variant: str,
) -> tuple[Entry | None, bool]:
    dct = app_data.manager.active.dct

    if dct.search(variants=[new_variant]):
        window = TwoOptionsDialog(
            window_parent, app_data,
            'Статья с таким словом уже есть в словаре\n'
            'Что вы хотите сделать?',
            'Добавить к существующей статье',
            'Оставить отдельной статьёй',
            focused_btn='none', left_btn_style='Default', right_btn_style='Default',
            val_left='l', val_right='r', val_cancel='c',
        )
        result = window.open()
        if result == 'l':  # Добавить к существующей статье
            new_entry = select_entry(app_data, window_parent, new_variant)
            if not new_entry:
                return entry, False
            dct.merge_entries(new_entry, entry)
            return new_entry, True
        elif result == 'r':  # Оставить отдельной статьёй
            dct.edit_variant(entry, old_variant, new_variant)
            return entry, True
        else:
            return entry, False
    else:
        dct.edit_variant(entry, old_variant, new_variant)
        return entry, True


def add_homograph(app_data: AppData, window_parent: tk.Misc, lemma: str, tr: str) -> Entry | None:
    """
    Add a new word to the dictionary.

    If an entry with the same word already exists, offer to add the new word to that entry instead.
    """

    dct = app_data.manager.active.dct

    if dct.search(variants=[lemma]):
        window = TwoOptionsDialog(
            window_parent, app_data,
            'Статья с таким словом уже есть в словаре\n'
            'Что вы хотите сделать?',
            'Добавить к существующей статье',
            'Создать новую статью',
            focused_btn='none', left_btn_style='Default', right_btn_style='Default',
            val_left='l', val_right='r', val_cancel='c',
        )
        result = window.open()
        if result == 'l':  # Добавить к существующей статье
            entry = select_entry(app_data, window_parent, lemma)
            if not entry:
                return None
            dct.add_tr(entry, tr)
            return entry
        elif result == 'r':  # Создать новую статью
            return dct.add_entry(lemma, tr)
        else:
            return None
    else:
        return dct.add_entry(lemma, tr)


def count_filtered_entries(
        dct: Dictionary,
        tag: Tag | None = None,
        to_filter_fav: bool = False,
) -> tuple[int, int, int, int]:
    """
    Count entries, translations, and inflected forms, optionally restricted by tag and favorite status.

    Args:
        dct: Dictionary whose entries are counted.
        tag: If specified, counts only entries that have this tag.
             If None, counts entries across the entire dictionary.
        to_filter_fav: If True, counts only favorite entries.

    Returns:
        Tuple (n_entries, n_translations, n_gram_forms, n_word_forms).
        - n_entries: Number of matching entries.
        - n_translations: Total number of translations across matching entries.
        - n_gram_forms: Total number of grammatical forms across matching entries.
        - n_word_forms: Total number of word forms across matching entries.
    """

    if tag is None:
        target = dct
    else:
        target = dct.search(tags=[tag])

    n_entries = 0
    n_translations = 0
    n_gram_forms = 0
    n_word_forms = 0
    for entry in target:
        if to_filter_fav and not entry.is_fav:
            continue
        n_entries += 1
        n_translations += entry.n_translations
        n_gram_forms += entry.n_gram_forms
        n_word_forms += entry.n_word_forms
    return n_entries, n_translations, n_gram_forms, n_word_forms


def search_entries(
        entries: Iterable[Entry],
        query: str,
        to_search_lemma: bool,
        to_search_tr: bool,
        to_search_frm: bool,
        to_search_phr: bool,
        to_search_nt: bool,
) -> list[set[Entry]]:
    query_lower = query.lower()
    query_norm = normalize(query)

    results = [set() for _ in range(9)]
    for entry in entries:
        targets = set()
        if to_search_lemma:
            targets.update(entry.variants)
        if to_search_tr:
            targets.update(entry.tr)
        if to_search_frm:
            targets.update(*entry.forms.values())
        if to_search_phr:
            targets.update(entry.phrases.keys())
            targets.update(*entry.phrases.values())
        if to_search_nt:
            targets.update(entry.notes)

        targets_lower = {val.lower() for val in targets}
        targets_norm = {normalize(val) for val in targets}

        if query in targets:
            results[0].add(entry)
        elif query_lower in targets_lower:
            results[1].add(entry)
        elif query_norm in targets_norm:
            results[2].add(entry)

        elif any(word_in_line(query, val) for val in targets):
            results[3].add(entry)
        elif any(word_in_line(query_lower, val.lower()) for val in targets_lower):
            results[4].add(entry)
        elif any(word_in_line(query_norm, normalize(val)) for val in targets_norm):
            results[5].add(entry)

        elif any(query in val for val in targets):
            results[6].add(entry)
        elif any(query_lower in val.lower() for val in targets_lower):
            results[7].add(entry)
        elif any(query_norm in normalize(val) for val in targets_norm):
            results[8].add(entry)
    return results


def check_updates(
        window_parent: tk.Misc,
        app_data: AppData,
        to_show_if_no_updates: bool,
):
    to_check_for_updates = app_data.ui_settings.to_check_for_updates

    print('\nПроверка наличия обновлений...')
    window_new_version = None
    try:
        data = urllib2.urlopen(URL_LAST_VERSION)
        latest_version = str(data.readline().decode('utf-8')).strip()
        if PROGRAM_VERSION == latest_version:
            print('Установлена последняя доступная версия программы')
            if to_check_for_updates and to_show_if_no_updates:
                MessageDialog(
                    window_parent, app_data,
                    'Установлена последняя доступная версия программы'
                ).open()
        else:
            print(f'Доступна новая версия: {latest_version}')
            if to_check_for_updates:
                window_new_version = NewVersionAvailableW(
                    window_parent, app_data, latest_version
                )
    except Exception as exc:
        print(f'Ошибка: невозможно проверить наличие обновлений!\n'
              f'{exc}')
        if to_check_for_updates:
            warning(
                window_parent, app_data,
                f'Ошибка: невозможно проверить наличие обновлений!\n'
                f'{exc}',
            )
    return window_new_version


""" Загрузка/сохранение """


def create_default_custom_theme():
    """Set the default theme as the custom theme."""

    styles_path = CUSTOM_THEME_DIR / STYLES_FN
    with open(styles_path, 'w', encoding='utf-8') as styles_file:
        styles_file.write(
            f'{REQUIRED_THEME_VERSION}\n'
            f'1'
        )
        for key in STYLES.keys():
            style = STYLES[key][1][DEFAULT_TH]
            STYLES[key][1][CUSTOM_TH] = style
            styles_file.write(f'\n{key} = {style}')


def upload_one_theme(theme_path: str, theme_name: str) -> int:
    styles_path = Path(theme_path) / STYLES_FN
    with open(styles_path, 'r', encoding='utf-8') as styles_file:
        theme_version = styles_file.readline().strip()
        theme_version = int(re.split(' |//', theme_version)[0])  # После // идут комментарии
        to_update = styles_file.readline().strip()
    if theme_version != REQUIRED_THEME_VERSION:
        if to_update == '1':
            print(f'Тема устарела. Идёт обновление с версии {theme_version} '
                  f'до версии {REQUIRED_THEME_VERSION}')
            upgrade_theme(styles_path)
        else:
            return RET_TH_OLD
    with open(styles_path, 'r', encoding='utf-8') as styles_file:
        styles_file.readline().strip()  # Версия темы
        styles_file.readline().strip()  # Переменная обновлений
        # Сначала устанавливаем значения по умолчанию
        for key in STYLES:
            STYLES[key][1][theme_name] = STYLES[key][1][DEFAULT_TH]

        while True:
            line = styles_file.readline().strip()
            data = [v for v in re.split(' |=|//', line) if v != '']  # После // идут комментарии
            if not data:
                break
            key = data[0].strip()
            if key not in STYLES:
                continue
            val = data[1].strip()
            STYLES[key][1][theme_name] = val
    return RET_TH_OK


def upload_themes(themes: list[str]):
    for dir_name in THEMES_DIR.iterdir():
        theme_dir_path = THEMES_DIR / dir_name
        if not theme_dir_path.is_dir():
            continue
        if not (theme_dir_path / STYLES_FN).exists():
            continue

        theme_name = dir_name
        print(f'Загрузка темы "{theme_name}". ', end='')
        try:
            ret = upload_one_theme(theme_dir_path, theme_name)
        except Exception as exc:
            print(f'Ошибка: {exc}')
        else:
            if ret == RET_TH_OK:
                print('Тема успешно загружена')
                if theme_name not in themes:
                    themes.append(theme_name)
            elif ret == RET_TH_OLD:
                print(f'Не удалось загрузить тему, т. к. её версия не соответствует требуемой!'
                      f' Актуальные темы можно загрузить здесь: {URL_RELEASES}')


def upload_custom_theme(to_print: bool = True):
    if not (CUSTOM_THEME_DIR / STYLES_FN).exists():
        create_default_custom_theme()
        return

    print('Загрузка пользовательской темы. ', end='')
    try:
        ret = upload_one_theme(CUSTOM_THEME_DIR, CUSTOM_TH)
    except Exception as exc:
        print(f'Ошибка: {exc}')
    else:
        if ret == RET_TH_OK and to_print:
            print('Тема успешно загружена')
        elif ret == RET_TH_OLD:
            print('Не удалось загрузить тему, т. к. её версия не соответствует требуемой!')


def img_path(theme: str, img_name: str) -> str:
    assert img_name in IMG_NAMES

    if theme == CUSTOM_TH:
        theme_dir = CUSTOM_THEME_DIR
    else:
        theme_dir = THEMES_DIR / theme

    file_name = f'{img_name}.png'
    if (theme_dir / file_name).exists():
        return theme_dir / file_name
    return IMAGES_DIR / file_name


def rename_dct_on_disk(dct_id: str, new_name: str):
    path = DCT_MAIN_DATA_PATH(dct_id)
    disk_data = read_json(path)
    set_dct_name_in_dict(disk_data, new_name)
    save_json(disk_data, path)


def save_settings_if_has_changes(window_parent: tk.Misc, app_data: AppData):
    window_dia = TwoOptionsDialog(
        window_parent, app_data,
        'Хотите сохранить изменения настроек словаря?', 'Да', 'Нет',
    )
    result = window_dia.open()
    if result:
        dct_bundle = app_data.manager.active
        dct_bundle.partial_save(DCT_SAVE_DIR(dct_bundle.id), replacer=True, optional={'tk'})
        MessageDialog(window_parent, app_data, 'Настройки словаря успешно сохранены').open()
        print('\nНастройки словаря успешно сохранены')


def save_dct_if_has_progress(window_parent: tk.Misc, app_data: AppData):
    manager = app_data.manager
    dct = manager.active.dct
    dct_idx = manager.active_idx

    if dct.is_modified:
        window_dia = TwoOptionsDialog(
            window_parent, app_data,
            'Хотите сохранить свой прогресс?', 'Да', 'Нет',
        )
        result = window_dia.open()
        if result:
            manager.save_dct(dct_idx, DCT_SAVE_DIR(dct.id))
            MessageDialog(window_parent, app_data, 'Прогресс успешно сохранён').open()
            print('\nПрогресс успешно сохранён')


""" Графический интерфейс - вспомогательные функции """


def combobox_width(values: tuple[str, ...] | list[str], min_width: int, max_width: int) -> int:
    """
    Calculate the width (in characters) of a monospace field that fits every
    value, limited to the range from min_width to max_width.
    """

    assert min_width >= 0
    assert max_width >= 0
    assert max_width >= min_width

    max_len_of_vals = max(len(val) for val in values)
    return min(max(max_len_of_vals, min_width), max_width)


def field_height(text: str, str_len: int) -> int:
    """
    Calculate the number of rows needed to display text in a multiline field
    whose lines are str_len characters long.
    """

    assert str_len > 0

    lines = text.split('\n')
    return sum(math.ceil(len(line) / str_len) for line in lines)


def toplevel_geometry(window_parent: tk.Misc, window: tk.Wm):
    window.geometry(f'+{window_parent.winfo_x() + 20}+{window_parent.winfo_y() + 20}')


def bind_ctrl_a(widget: tk.Entry | ttk.Entry):
    def handler(event=None):
        widget.select_range(0, 'end')
        widget.icursor('end')
        return 'break'

    widget.bind('<Control-a>', handler, add='+')
    widget.bind('<Control-A>', handler, add='+')


def warning(window_parent: tk.Misc, app_data: AppData, msg: str):
    MessageDialog(window_parent, app_data, msg, tab=0, title='Warning').open()


def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


def btn_enable(btn: ttk.Button, command: str | Callable, style: str = 'Default'):
    btn.configure(command=command, style=f'{style}.TButton')


def set_image(
        btn: ttk.Button,
        img: tk.PhotoImage,
        img_name: str,
        text_if_no_img: str,
        compound: CompoundValues = 'image',
):
    try:
        img.configure(file=img_name)
    except tk.TclError:
        btn.configure(text=text_if_no_img, compound='text', style='Default.TButton')
    else:
        btn.configure(image=img, compound=compound, style='Image.TButton')


def _create_widget(widget_type: Type[T], **kwargs) -> T:
    # Get parameters
    params = kwargs
    if 'kwargs' in params:
        params.update(params.pop('kwargs'))
    params = {
        name: value
        for name, value in params.items()
        if value is not None
    }

    grid_param_names = (
        'row', 'rowspan', 'column', 'columnspan', 'padx', 'pady', 'ipadx', 'ipady', 'sticky'
    )

    # Create widget
    init_params = {
        name: value
        for name, value in params.items()
        if name not in grid_param_names
    }
    widget = widget_type(**init_params)

    # Place widget
    grid_params = {
        name: value
        for name, value in params.items()
        if name in grid_param_names
    }
    if grid_params:
        widget.grid(**grid_params)

    return widget


def create_frame(
        master: tk.Misc | None,
        style: str | None = 'Default.TFrame',
        **kwargs,
) -> ttk.Frame:
    return _create_widget(ttk.Frame, **locals())


def create_label(
        master: tk.Misc | None,
        text: str | None = None,
        style: str | None = 'Default.TLabel',
        **kwargs,
) -> ttk.Label:
    return _create_widget(ttk.Label, **locals())


def create_button(
        master: tk.Misc | None,
        command: Callable[[], Any] | None = None,
        text: str | None = None,
        takefocus: bool | None = False,
        style: str | None = 'Default.TButton',
        **kwargs,
) -> ttk.Button:
    return _create_widget(ttk.Button, **locals())


def create_checkbutton(
        master: tk.Misc | None,
        variable: tk.Variable | None = None,
        style: str | None = 'Default.TCheckbutton',
        **kwargs,
) -> ttk.Checkbutton:
    return _create_widget(ttk.Checkbutton, **locals())


def create_entry(
        master: tk.Misc | None,
        textvariable: tk.Variable | None = None,
        width: int | None = None,
        style: str | None = 'Default.TEntry',
        font: Font | str | tuple[str, int] | AppData | None = None,
        **kwargs,
) -> ttk.Entry:
    params = locals()
    if isinstance(font, AppData):
        params['font'] = ('StdFont', font.ui_settings.scale)
    return _create_widget(ttk.Entry, **params)


def create_combobox(
        master: tk.Misc | None,
        textvariable: tk.Variable | None = None,
        values: list[str] | tuple[str, ...] | None = None,
        width: int | None = None,
        style: str | None = 'Default.TCombobox',
        font: Font | str | tuple[str, int] | AppData | None = None,
        **kwargs,
) -> ttk.Combobox:
    params = locals()
    if isinstance(font, AppData):
        params['font'] = ('StdFont', font.ui_settings.scale)
    return _create_widget(ttk.Combobox, **params)


""" Графический интерфейс - функции валидации """


def validate_int_min_max(value: str, min_val: int, max_val: int) -> bool:
    return value == '' or value.isnumeric() and min_val <= int(value) <= max_val


def validate_replacement_modifier(value: str, replacer: Replacer) -> bool:
    return value in replacer.modifiers


def validate_replacement_base(value: str, replacer: Replacer) -> bool:
    return len(value) <= 1 and value not in replacer.modifiers


def validate_replacement_output(value: str) -> bool:
    return len(value) <= 1


def validate_savename(value: str) -> bool:
    if len(value) > 99:
        return False
    for char in value:
        if char in '/|\\<>:*"?':
            return False
    return True


""" Графический интерфейс - виджеты """


class ScrollFrame(tk.Frame):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            height: int,
            width: int,
            scrollbar_position: Literal['left', 'right'] = 'right',
    ):
        super().__init__(parent)

        self.app_data = app_data

        if scrollbar_position == 'right':
            canvas_position: Literal['left', 'right'] = 'left'
        else:
            canvas_position: Literal['left', 'right'] = 'right'

        self._create_widgets(height, width, canvas_position, scrollbar_position)
        self._create_bindings()

        self.on_frame_configure(None)

    def _create_widgets(
            self,
            height: int,
            width: int,
            canvas_position: Literal['left', 'right'],
            scrollbar_position: Literal['left', 'right'],
    ):
        self.canvas = tk.Canvas(
            self, bg=STYLES['FLAT_BTN.BG.2'][1][self.app_data.ui_settings.theme],
            bd=0, highlightthickness=0, height=height, width=width)
        self.canvas.pack(side=canvas_position, fill='both', expand=True)
        self.frame_canvas = create_frame(self.canvas)
        self.scrollbar_y = ttk.Scrollbar(
            self, command=self.canvas.yview, style='Vertical.TScrollbar')
        self.scrollbar_y.pack(side=scrollbar_position, fill='y')

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.canvas_window = self.canvas.create_window(
            (4, 4), window=self.frame_canvas, anchor='nw', tags='self.frame_canvas')

    def _create_bindings(self):
        self.frame_canvas.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.frame_canvas.bind('<Enter>', self.on_enter)
        self.frame_canvas.bind('<Leave>', self.on_leave)

    def on_frame_configure(self, event):
        """Update the scroll region when the frame size changes."""

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_canvas_configure(self, event):
        """Adjust the canvas window width when the canvas size changes."""

        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mouse_wheel(self, event):
        """Handle mouse wheel events."""

        if not (self.canvas.yview()[0] == 0.0 and event.delta > 0):
            if platform.system() == 'Windows':
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            elif platform.system() == 'Darwin':
                self.canvas.yview_scroll(int(-1 * event.delta), 'units')
            else:
                if event.num == 4:
                    self.canvas.yview_scroll(-1, 'units')
                elif event.num == 5:
                    self.canvas.yview_scroll(1, 'units')

    def on_enter(self, event):
        """Bind the mouse wheel when the cursor enters the widget."""

        if platform.system() == 'Linux':
            self.canvas.bind_all('<Button-4>', self.on_mouse_wheel)
            self.canvas.bind_all('<Button-5>', self.on_mouse_wheel)
        else:
            self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)

    def on_leave(self, event):
        """Unbind the mouse wheel when the cursor leaves the widget."""

        if platform.system() == 'Linux':
            self.canvas.unbind_all('<Button-4>')
            self.canvas.unbind_all('<Button-5>')
        else:
            self.canvas.unbind_all('<MouseWheel>')

    def scroll_down_small(self):
        self.canvas.yview_scroll(1, 'units')
        return 'break'

    def scroll_up_small(self):
        self.canvas.yview_scroll(-1, 'units')
        return 'break'

    def resize(self, height: int = None, width: int = None):
        if height:
            self.canvas.configure(height=height)
        if width:
            self.canvas.configure(width=width)


""" Графический интерфейс - всплывающие окна """


class MessageDialog(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            msg: str,
            btn_text: str = 'Ясно',
            msg_max_width: int = 60,
            tab: int = 5,
            msg_justify: Literal['left', 'center', 'right'] = 'center',
            title: str = PROGRAM_NAME,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.cancelled = True  # Закрыто ли окно крестиком

        self._configure_window(title)
        self._create_widgets(msg, btn_text, msg_max_width, tab, msg_justify)

    def _configure_window(self, title: str):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(
            self,
            msg: str,
            btn_text: str,
            msg_max_width: int,
            tab: int,
            msg_justify: Literal['left', 'center', 'right'],
    ):
        self.lbl_msg = create_label(
            self, split_text(msg, msg_max_width, tab=tab, to_add_right_spaces=False),
            justify=msg_justify,
            row=0, column=0, padx=6, pady=4)
        self.btn_ok = create_button(
            self, self.on_ok, btn_text,
            row=1, column=0, padx=6, pady=4)

    def on_ok(self):
        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> bool:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.cancelled


class TwoOptionsDialog(tk.Toplevel):
    ALLOWED_ST_VALUES = ('Default', 'Yes', 'No')
    ALLOWED_FOCUS_VALUES = ('left', 'right', 'none')

    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            msg: str = 'Вы уверены?',
            left_btn_text: str = 'Да',
            right_btn_text: str = 'Отмена',
            left_btn_style: Literal['Default', 'Yes', 'No'] = 'Yes',
            right_btn_style: Literal['Default', 'Yes', 'No'] = 'No',
            val_left: Any = True,
            val_right: Any = False,
            val_cancel: Any = False,
            focused_btn: Literal['left', 'right', 'none'] = 'left',
            title: str = PROGRAM_NAME,
    ):
        """
        Args:
            parent: Parent widget.
            app_data: Application data.
            msg: The message shown in the dialog.
            left_btn_text: Text of the left button.
            right_btn_text: Text of the right button.
            left_btn_style: Style of the left button: 'Default', 'Yes', or 'No'.
            right_btn_style: Style of the right button: 'Default', 'Yes', or 'No'.
            val_left: Value returned when the left button is pressed.
            val_right: Value returned when the right button is pressed.
            val_cancel: Value returned when the window is closed with the X button.
            focused_btn: The button activated by the Enter key: 'left', 'right', or 'none'.
            title: Window title.
        """

        assert left_btn_style in self.ALLOWED_ST_VALUES,\
            f'Bad value: st_left\n' \
            f'Allowed values: {self.ALLOWED_ST_VALUES}'
        assert right_btn_style in self.ALLOWED_ST_VALUES,\
            f'Bad value: st_right\n' \
            f'Allowed values: {self.ALLOWED_ST_VALUES}'
        assert focused_btn in self.ALLOWED_FOCUS_VALUES,\
            f'Bad value: focused_btn\n' \
            f'Allowed values: {self.ALLOWED_FOCUS_VALUES}'

        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.focused_btn = focused_btn
        self.result = val_cancel
        self.val_left = val_left
        self.val_right = val_right

        self.left_btn_style = f'{left_btn_style}.TButton'
        self.right_btn_style = f'{right_btn_style}.TButton'

        self._configure_window(title)
        self._create_widgets(msg, left_btn_text, right_btn_text)

    def _configure_window(self, title: str):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, msg: str, left_btn_text: str, right_btn_text: str):
        self.lbl_msg = create_label(
            self, split_text(msg, 45, to_add_right_spaces=False),
            justify='center',
            row=0, columnspan=2, padx=6, pady=4)
        self.btn_left = create_button(
            self, self.on_left, left_btn_text, style=self.left_btn_style,
            row=1, column=0, padx=(6, 10), pady=4, sticky='E')
        self.btn_right = create_button(
            self, self.on_right, right_btn_text, style=self.right_btn_style,
            row=1, column=1, padx=(10, 6), pady=4, sticky='W')

    def on_left(self):
        self.result = self.val_left
        self.destroy()

    def on_right(self):
        self.result = self.val_right
        self.destroy()

    def set_focus(self):
        self.focus_set()

        if self.focused_btn == 'left':
            self.bind('<Return>', lambda event: self.btn_left.invoke())
            self.bind('<Escape>', lambda event: self.btn_right.invoke())
        elif self.focused_btn == 'right':
            self.bind('<Return>', lambda event: self.btn_right.invoke())
            self.bind('<Escape>', lambda event: self.btn_left.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.result


class InputDialog(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            msg: str = 'Введите строку',
            btn_text: str = 'Подтвердить',
            entry_width: int = 45,
            default_value: str | None = '',
            validate_function: Callable[[str], bool] | None = None,
            check_answer_function: Callable[[tk.Misc, str], bool] | None = None,
            if_correct_function: Callable[[], Any] | None = None,
            if_incorrect_function: Callable[[], Any] | None = None,
            title: str = PROGRAM_NAME,
            to_replace: bool = True,
    ):
        """
        Args:
            parent: Parent widget.
            app_data: Application data.
            msg: The message shown in the dialog.
            btn_text: Text of the button.
            entry_width: Width (in characters) of the input field.
            default_value: Text initially shown in the input field.
            validate_function: Optional function that validates the entered text.
            check_answer_function: Optional function that determines whether the answer is correct.
                                   Its result decides which of if_correct_function and
                                   if_incorrect_function is called.
            if_correct_function: Optional function that is called when the answer is correct.
            if_incorrect_function: Optional function that is called when the answer is incorrect.
            title: Window title.
            to_replace: Whether to apply replacements.
        """

        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.replacer = app_data.manager.active.replacer

        self.check_answer_function = check_answer_function
        self.if_correct_function = if_correct_function
        self.if_incorrect_function = if_incorrect_function
        self.to_replace = to_replace

        self.cancelled = True  # Закрыто ли окно крестиком

        if to_replace:
            default_value = self.replacer.escape(default_value)
        self.var_text = tk.StringVar(value=default_value)

        self._configure_window(title)
        self._create_widgets(msg, btn_text, entry_width)

        if validate_function:
            if to_replace:
                replace_and_validate = lambda x: validate_function(self.replacer.replace(x))
                self.vcmd = (self.register(replace_and_validate), '%P')
            else:
                self.vcmd = (self.register(validate_function), '%P')
            self.entry.configure(validate='key', validatecommand=self.vcmd)

        self.entry.icursor(len(default_value))

    def _configure_window(self, title: str):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, msg: str, btn_text: str, entry_width: int):
        self.lbl_msg = create_label(
            self, split_text(f'{msg}:', 45, to_add_right_spaces=False),
            justify='center',
            row=0, padx=6, pady=(6, 3))
        self.entry = create_entry(
            self, self.var_text, entry_width, font=self.app_data,
            row=1, padx=6, pady=(0, 6))
        self.btn_ok = create_button(
            self, self.on_ok, btn_text, style='Yes.TButton',
            row=2, padx=6, pady=(0, 6))

    def on_ok(self):
        if self.check_answer_function:
            text = self.var_text.get()
            if self.to_replace:
                text = self.replacer.replace(text)
            is_correct = self.check_answer_function(self, text)
            if is_correct:
                if self.if_correct_function:
                    self.if_correct_function()
            else:
                if self.if_incorrect_function:
                    self.if_incorrect_function()
                return
        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()
        self.entry.focus_set()

        bind_ctrl_a(self.entry)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> tuple[bool, str]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        text = self.var_text.get()
        if self.to_replace:
            text = self.replacer.replace(text)

        return self.cancelled, text


class ChoiceDialog(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            values: list[str] | tuple[str, ...],
            msg: str = 'Выберите один из вариантов',
            btn_text: str = 'Подтвердить',
            combo_width: int = 40,
            default_value: str | None = None,
            title: str = PROGRAM_NAME,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.cancelled = True  # Закрыто ли окно крестиком

        self.var_answer = tk.StringVar(value=default_value)

        self._configure_window(title)
        self._create_widgets(msg, values, combo_width, btn_text)

    def _configure_window(self, title: str):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(
            self,
            msg: str,
            values: list[str] | tuple[str, ...],
            combo_width: int,
            btn_text: str,
    ):
        self.lbl_msg = create_label(
            self, split_text(msg, 45, to_add_right_spaces=False),
            justify='center',
            row=0, padx=6, pady=(4, 1))
        self.combo = create_combobox(
            self, self.var_answer, values, combo_width, state='readonly',
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            row=1, padx=6, pady=1)
        self.btn_ok = create_button(
            self, self.on_ok, btn_text, style='Yes.TButton',
            row=2, padx=6, pady=4)

    def on_ok(self):
        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> tuple[bool, str]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.cancelled, self.var_answer.get()


class ImageDialog(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            img_name: str,
            msg: str,
            btn_text: str = 'Ясно',
            title: str = PROGRAM_NAME,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.cancelled = True  # Закрыто ли окно крестиком

        self._configure_window(title)
        self._create_widgets(img_name, msg, btn_text)

    def _configure_window(self, title: str):
        self.title(title)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, img_name: str, msg: str, btn_text: str):
        try:
            self.img = tk.PhotoImage(file=img_name)
        except:
            self.lbl_img = create_label(
                self, '[!!!] Изображение не найдено [!!!]', justify='center')
        else:
            self.lbl_img = create_label(self, image=self.img)
        self.lbl_img.grid(
            row=0, column=0, padx=6, pady=(4, 0))
        self.lbl_msg = create_label(
            self, split_text(msg, 45, to_add_right_spaces=False),
            justify='center',
            row=2, column=0, padx=6, pady=0)
        self.btn_ok = create_button(
            self, self.on_ok, btn_text,
            row=3, column=0, padx=6, pady=4)

    def on_ok(self):
        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> bool:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.cancelled


""" Графический интерфейс - второстепенные окна """


class TrainSettingsW(tk.Toplevel):
    txt_to_format = {
        'Угадывать слово по переводу': TrainingFormat.TRANS_TO_WORD,
        'Угадывать перевод по слову': TrainingFormat.WORD_TO_TRANS,
        'Угадывать фразу по переводу': TrainingFormat.TRANS_TO_PHRASE,
        'Угадывать перевод по фразе': TrainingFormat.PHRASE_TO_TRANS,
        'Der-Die-Das (для немецкого)': TrainingFormat.ARTICLES_GERMAN,
    }
    txt_to_order = {
        'Случайный порядок': TrainingOrder.RANDOM,
        'В первую очередь сложные': TrainingOrder.DIFFICULT_FIRST,
    }
    txt_to_entries = {
        'Все': EntrySelection.ALL,
        'Преимущ. избранные (рекоменд.)': EntrySelection.MOSTLY_FAV,
        'Только избранные': EntrySelection.FAV,
        'Только неотвеченные': EntrySelection.UNANSWERED,
        '10 случайных': EntrySelection.RANDOM_10,
        '10 случайных из избранных': EntrySelection.RANDOM_10_FAV,
    }
    txt_to_forms = {
        'Только начальная форма': FormSelection.LEMMAS,
        'По одной случайной словоформе': FormSelection.RANDOM,
        'Все формы, кроме начальной': FormSelection.INFLECTED,
        'Все словоформы': FormSelection.ALL,
    }

    format_to_txt = {v: k for k, v in txt_to_format.items()}
    order_to_txt = {v: k for k, v in txt_to_order.items()}
    entries_to_txt = {v: k for k, v in txt_to_entries.items()}
    forms_to_txt = {v: k for k, v in txt_to_forms.items()}

    def __init__(self, parent: tk.Misc, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active
        self.dct = app_data.manager.active.dct
        self.train_config = app_data.manager.active.train_config

        self.cancelled = True
        self.tag_options = [ALL_TAGS] + self.dct.tags

        self.var_case_sensitive = tk.BooleanVar(
            value=self.train_config.is_case_sensitive
        )
        self.var_format = tk.StringVar(
            value=self.format_to_txt[self.train_config.format]
        )
        self.var_tag = tk.StringVar(
            value=self.train_config.tags[0] if self.train_config.tags else ALL_TAGS
        )
        self.var_words = tk.StringVar(
            value=self.entries_to_txt[self.train_config.entries]
        )
        self.var_forms = tk.StringVar(
            value=self.forms_to_txt[self.train_config.forms]
        )
        self.var_order = tk.StringVar(
            value=self.order_to_txt[self.train_config.order]
        )

        self._configure_window()
        self._create_widgets()
        self._add_validation()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Выбор режима')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_header = create_label(
            self, 'Выберите способ учёбы',
            row=0, column=0, padx=6, pady=(6, 3))
        self._create_main_frame()
        self.btn_start = create_button(
            self, self.on_start, 'Учить',
            row=2, column=0, padx=6, pady=(0, 6))

    def _create_main_frame(self):
        self.frame_main = create_frame(self, row=1, column=0, padx=6, pady=(0, 3))

        self.lbl_case_sensitive = create_label(
            self.frame_main,
            'Учитывать регистр:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.check_case_sensitive = create_checkbutton(
            self.frame_main, self.var_case_sensitive,
            row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_format = create_label(
            self.frame_main, 'Метод:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_format = create_combobox(
            self.frame_main, self.var_format, LEARN_VALUES_FORMAT, 30,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly', validate='focusin',
            row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_tag = create_label(
            self.frame_main, 'Группа:',
            row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_tag = create_combobox(
            self.frame_main, self.var_tag, self.tag_options, 30,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_words = create_label(
            self.frame_main, 'Набор статей:',
            row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_words = create_combobox(
            self.frame_main, self.var_words, LEARN_VALUES_WORDS, 30,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=3, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_forms = create_label(
            self.frame_main, 'Набор словоформ:',
            row=4, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_forms = create_combobox(
            self.frame_main, self.var_forms, LEARN_VALUES_FORMS, 30,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=4, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_order = create_label(
            self.frame_main, 'Порядок заданий:',
            row=5, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.combo_order = create_combobox(
            self.frame_main, self.var_order, LEARN_VALUES_ORDER, 30,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=5, column=1, padx=(0, 6), pady=(0, 6), sticky='W')

    def _add_validation(self):
        def validate_format_and_forms(value: str):
            """Allow adding word forms only for the first study method."""

            if value == LEARN_VALUES_FORMAT[0]:
                self.lbl_forms.grid(  row=4, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
                self.combo_forms.grid(row=4, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
            else:
                self.lbl_forms.grid_remove()
                self.combo_forms.grid_remove()
            return True

        self.vcmd_format = (self.register(validate_format_and_forms), '%P')
        self.combo_format['validatecommand'] = self.vcmd_format

        validate_format_and_forms(self.var_format.get())

    def on_start(self):
        format = self.var_format.get()
        tag = self.var_tag.get()
        words = self.var_words.get()
        if format == LEARN_VALUES_FORMAT[0]:
            forms = self.var_forms.get()
        else:
            forms = LEARN_VALUES_FORMS[0]
        order = self.var_order.get()

        self.dct_bundle.train_config = TrainingConfig(
            self.var_case_sensitive.get(),
            self.txt_to_format[format],
            self.txt_to_order[order],
            self.txt_to_entries[words],
            self.txt_to_forms[forms],
            None if tag == ALL_TAGS else [tag],
        )

        self.cancelled = False

        self.dct_bundle.partial_save(DCT_SAVE_DIR(self.dct_bundle.id), metadata=True, train_config=True)

        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_start.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> bool:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.cancelled


class IncorrectAnswerW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            user_answer: str,
            correct_answer: str,
            with_typo: bool,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.with_typo = with_typo
        self.result = 'no'  # Значение, возвращаемое методом self.open

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Неверно')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_msg = create_label(
            self,
            split_text(
                f'Неверно.\n'
                f'Ваш ответ: {self.user_answer}\n'
                f'Правильный ответ: {self.correct_answer}\n'
                f'Хотите добавить слово в избранное?',
                45, 5, to_add_right_spaces=False,
            ),
            justify='center')
        self.btn_yes = create_button(self, self.on_yes, 'Да', style='Yes.TButton')
        self.btn_no = create_button(self, self.on_no, 'Нет', style='No.TButton')
        self.btn_typo = create_button(self, self.on_typo, 'Просто опечатка')

        if self.with_typo:
            self.lbl_msg.grid( row=0, column=0, columnspan=3, padx=6, pady=4)
            self.btn_yes.grid( row=1, column=0,               padx=6, pady=4, sticky='E')
            self.btn_no.grid(  row=1, column=1,               padx=6, pady=4)
            self.btn_typo.grid(row=1, column=2,               padx=6, pady=4, sticky='W')

            self.tip_btn_typo = ttip.Hovertip(
                self.btn_typo,
                'Не засчитывать ошибку\n'
                'Tab',
                hover_delay=700)
        else:
            self.lbl_msg.grid(row=0, column=0, columnspan=2, padx=6, pady=4)
            self.btn_yes.grid(row=1, column=0,               padx=6, pady=4, sticky='E')
            self.btn_no.grid( row=1, column=1,               padx=6, pady=4, sticky='W')

    def on_yes(self):
        self.result = 'yes'
        self.destroy()

    def on_no(self):
        self.result = 'no'
        self.destroy()

    def on_typo(self):
        self.result = 'typo'
        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_yes.invoke())
        self.bind('<Escape>', lambda event: self.btn_no.invoke())
        if self.with_typo:
            self.bind('<Tab>', lambda event: self.btn_typo.invoke())

    def open(self) -> str:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.result


class SearchSettingsW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            to_search_only_fav: bool,
            to_search_only_full: bool,
            to_search_wrd: bool,
            to_search_tr: bool,
            to_search_frm: bool,
            to_search_phr: bool,
            to_search_nt: bool,
            search_tag: str,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active

        self.tag_options = [ALL_TAGS] + self.dct_bundle.dct.tags

        self.var_search_only_fav = tk.BooleanVar(value=to_search_only_fav)
        self.var_search_only_full = tk.BooleanVar(value=to_search_only_full)
        self.var_search_wrd = tk.BooleanVar(value=to_search_wrd)
        self.var_search_tr = tk.BooleanVar(value=to_search_tr)
        self.var_search_frm = tk.BooleanVar(value=to_search_frm)
        self.var_search_phr = tk.BooleanVar(value=to_search_phr)
        self.var_search_nt = tk.BooleanVar(value=to_search_nt)
        self.var_search_tag = tk.StringVar(value=search_tag)

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Параметры поиска')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_search_only_fav = create_label(
            self, 'Искать только среди избранных статей:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_search_only_fav = create_checkbutton(
            self, self.var_search_only_fav,
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_search_only_full = create_label(
            self, 'Искать слово целиком:',
            row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_only_full = create_checkbutton(
            self, self.var_search_only_full,
            row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self._create_main_frame()
        self._create_tag_frame()

    def _create_main_frame(self):
        self.frame_main = create_frame(self, row=2, column=0, columnspan=2, padx=6, pady=6)

        self.lbl_search_wrd = create_label(
            self.frame_main, 'Искать среди слов:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_search_wrd = create_checkbutton(
            self.frame_main, self.var_search_wrd,
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_search_tr = create_label(
            self.frame_main, 'Искать среди переводов:',
            row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_tr = create_checkbutton(
            self.frame_main, self.var_search_tr,
            row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_frm = create_label(
            self.frame_main, 'Искать среди словоформ:',
            row=2, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_frm = create_checkbutton(
            self.frame_main, self.var_search_frm,
            row=2, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_phr = create_label(
            self.frame_main, 'Искать среди фраз:',
            row=3, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_phr = create_checkbutton(
            self.frame_main, self.var_search_phr,
            row=3, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_nt = create_label(
            self.frame_main, 'Искать среди сносок:',
            row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_nt = create_checkbutton(
            self.frame_main, self.var_search_nt,
            row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')

    def _create_tag_frame(self):
        self.frame_tag = create_frame(
            self, 'Invis.TFrame',
            row=3, column=0, columnspan=2, padx=6, pady=6)

        self.lbl_search_tag = create_label(
            self.frame_tag, 'Группа:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.combo_search_tag = create_combobox(
            self.frame_tag, self.var_search_tag,
            [ALL_TAGS] + self.dct_bundle.dct.tags, 26,
            state='readonly',
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> tuple[bool, bool, bool, bool, bool, bool, bool, str]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        config: DctUISettings = self.dct_bundle.optional['tk']
        config.search_page_to_filter_fav = self.var_search_only_fav.get()
        config.search_page_to_match_whole_word = self.var_search_only_full.get()
        config.search_page_to_search_in_words = self.var_search_wrd.get()
        config.search_page_to_search_in_translations = self.var_search_tr.get()
        config.search_page_to_search_in_forms = self.var_search_frm.get()
        config.search_page_to_search_in_phrases = self.var_search_phr.get()
        config.search_page_to_search_in_notes = self.var_search_nt.get()
        config.search_page_search_tag = None if self.var_search_tag.get() == ALL_TAGS else self.var_search_tag.get()

        self.dct_bundle.partial_save(DCT_SAVE_DIR(self.dct_bundle.id), metadata=True, optional={'tk'})

        return (
            self.var_search_only_fav.get(), self.var_search_only_full.get(),
            self.var_search_wrd.get(), self.var_search_tr.get(), self.var_search_frm.get(),
            self.var_search_phr.get(), self.var_search_nt.get(), self.var_search_tag.get()
        )


class SelectEntryFromHomographsW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData, query: str):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.to_search_wrd = query
        self.result = None

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Найдено несколько схожих статей')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_header = create_label(
            self, 'Выберите одну из статей', justify='center',
            row=0, column=0, padx=(6, 3), pady=(6, 3))
        self.scrolled_frame_wrd = ScrollFrame(
            self, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_wrd.grid(
            row=1, column=0, padx=6, pady=(0, 6))
        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

        entries = self.dct.search(variants=[self.to_search_wrd])
        self.widgets_wrd = [
            create_button(
                self.scrolled_frame_wrd.frame_canvas,
                lambda entry=entry: self.select_entry(entry),
                entry_repr_complete(entry, 75, 13),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i, entry in enumerate(entries)
        ]

    def select_entry(self, entry: Entry):
        self.result = entry
        self.destroy()

    def set_focus(self):
        self.focus_set()

        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> Entry | None:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.result


class EnterPhraseW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            title: str,
            app_data: AppData,
            default_value: tuple[str, str] = ('', ''),
            check_answer_function: Callable[[tk.Misc, tuple[str, str]], bool] | None = None,
    ):
        """
        Args:
            parent: Parent widget.
            title: Window title.
            app_data: Application data.
            default_value: The phrase and its translation initially shown
                           in the input fields.
            check_answer_function: Optional function that validates the entered pair. It is called
                                   with a parent widget and the (phrase, translation) pair,
                                   returns True if the pair is correct, and may have side effects
                                   (for example, showing a warning).
        """

        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.replacer = app_data.manager.active.replacer

        self.cancelled = True  # Закрыто ли окно крестиком
        self.check_answer_function = check_answer_function

        phr = self.replacer.escape(default_value[0])
        phr_tr = self.replacer.escape(default_value[1])
        self.var_phr = tk.StringVar(value=phr)
        self.var_tr = tk.StringVar(value=phr_tr)

        self._configure_window(title)
        self._create_widgets()
        self._create_bindings()

        self.entry_phr.icursor(len(self.var_phr.get()))

    def _configure_window(self, title: str):
        self.title(f'{PROGRAM_NAME} - {title}')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_phr = create_label(
            self, text='Фраза:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_phr = create_entry(
            self, self.var_phr, 45,
            font=self.app_data, validate='all',
            row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr = create_label(
            self, text='Перевод:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr = create_entry(
            self, self.var_tr, 45,
            font=self.app_data, validate='all',
            row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.btn_ok = create_button(
            self, self.on_ok, 'Готово',
            row=3, columnspan=2, padx=6, pady=(0, 6))

    def _create_bindings(self):
        self.entry_phr.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_phr.focus_set())

    def on_ok(self):
        if self.check_answer_function:
            phr = self.replacer.replace(self.var_phr.get())
            phr_tr = self.replacer.replace(self.var_tr.get())
            is_correct = self.check_answer_function(self, (phr, phr_tr))
            if not is_correct:
                return

        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()
        self.entry_phr.focus_set()

        bind_ctrl_a(self.entry_phr)
        bind_ctrl_a(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> tuple[bool, str, str]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        phr = self.replacer.replace(self.var_phr.get())
        phr_tr = self.replacer.replace(self.var_tr.get())
        return self.cancelled, phr, phr_tr


class EditEntryW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData, entry: Entry):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct
        self.entry = entry

        self.line_width = 35
        self.max_height_w = 3
        self.max_height_t = 4
        self.max_height_f = 4
        self.max_height_p = 3
        self.max_height_n = 3
        self.max_height_g = 3

        self.var_fav = tk.BooleanVar(value=entry.is_fav)

        self.img_edit = tk.PhotoImage()
        self.img_add = tk.PhotoImage()
        self.img_help = tk.PhotoImage()

        self.variants = []
        self.var_frames = []
        self.var_buttons = []
        #
        self.translations = []
        self.tr_frames = []
        self.tr_buttons = []
        #
        self.forms = []
        self.frm_frames = []
        self.frm_buttons = []
        #
        self.phrases = []
        self.phr_frames = []
        self.phr_buttons = []
        #
        self.notes = []
        self.nt_frames = []
        self.nt_buttons = []
        #
        self.tags = []
        self.gr_frames = []
        self.gr_buttons = []

        self._configure_window()
        self._create_widgets()

        self.refresh(True)

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Изменение статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        theme = self.app_data.ui_settings.theme

        self._create_main_frame()
        self.btn_back = create_button(
            self, self.close, 'Закончить',
            row=1, column=0, padx=(6, 0), pady=(0, 6))
        self.btn_help = create_button(
            self, self.show_help, width=2,
            row=1, column=1, padx=(6, 6), pady=(0, 6))
        set_image(self.btn_help, self.img_help, img_path(theme, 'about'), '?')
        self.btn_delete = create_button(
            self, self.delete_entry, 'Удалить статью', style='No.TButton',
            row=1, column=2, padx=(0, 6), pady=(0, 6))

        self.tip_btn_help = ttip.Hovertip(self.btn_help, 'Справка', hover_delay=450)

    def _create_main_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_main = create_frame(self, row=0, columnspan=3, padx=6, pady=(6, 4))

        self.lbl_variants = create_label(
            self.frame_main, 'Слово:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.scrolled_frame_variants = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_variants.grid(
            row=0, column=1, padx=(0, 1), pady=(6, 3), sticky='WE')
        self.btn_variant_add = create_button(
            self.frame_main, self.add_variant, width=2,
            row=0, column=2, padx=(3, 6), pady=(6, 3), sticky='W')
        set_image(self.btn_variant_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_tr = create_label(
            self.frame_main, text='Перевод:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_tr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_tr.grid(
            row=1, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_tr_add = create_button(
            self.frame_main, self.add_translation, width=2,
            row=1, column=2, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_tr_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_frm = create_label(
            self.frame_main, text='Формы слова:',
            row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_frm = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_frm.grid(
            row=2, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_frm_add = create_button(
            self.frame_main, self.add_form, width=2,
            row=2, column=2, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_frm_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_phrases = create_label(
            self.frame_main, 'Фразы:',
            row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_phr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_phr.grid(
            row=3, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_phrase_add = create_button(
            self.frame_main, self.add_phrase, width=2,
            row=3, column=2, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_phrase_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_notes = create_label(
            self.frame_main, 'Сноски:',
            row=4, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_nt = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_nt.grid(
            row=4, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_note_add = create_button(
            self.frame_main, self.add_note, width=2,
            row=4, column=2, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_note_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_gr = create_label(
            self.frame_main, 'Группы:',
            row=5, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_gr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame_gr.grid(
            row=5, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_gr_add = create_button(
            self.frame_main, self.add_tag, width=2,
            row=5, column=2, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_gr_add, self.img_add, img_path(theme, 'add'), '+')

        self.lbl_fav = create_label(
            self.frame_main, 'Избранное:',
            row=6, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_fav = create_checkbutton(
            self.frame_main, self.var_fav, command=self.set_fav,
            row=6, column=1, padx=(0, 6), pady=(0, 6), sticky='W')

        if self.btn_variant_add['style'] == 'Image.TButton':
            self.tip_btn_wrd_add = ttip.Hovertip(
                self.btn_variant_add, 'Добавить вариант написания', hover_delay=500)
        if self.btn_tr_add['style'] == 'Image.TButton':
            self.tip_btn_tr_add = ttip.Hovertip(
                self.btn_tr_add, 'Добавить перевод', hover_delay=500)
        if self.btn_frm_add['style'] == 'Image.TButton':
            self.tip_btn_frm_add = ttip.Hovertip(
                self.btn_frm_add, 'Добавить словоформу', hover_delay=500)
        if self.btn_phrase_add['style'] == 'Image.TButton':
            self.tip_btn_phrase_add = ttip.Hovertip(
                self.btn_phrase_add, 'Добавить фразу', hover_delay=500)
        if self.btn_note_add['style'] == 'Image.TButton':
            self.tip_btn_note_add = ttip.Hovertip(
                self.btn_note_add, 'Добавить сноску', hover_delay=500)
        if self.btn_gr_add['style'] == 'Image.TButton':
            self.tip_btn_gr_add = ttip.Hovertip(
                self.btn_gr_add, 'Добавить группу', hover_delay=500)

    def add_variant(self):
        window = InputDialog(
            self, self.app_data,
            'Введите новый вариант написания',
            check_answer_function=lambda wnd, val: check_variant(
                wnd, self.app_data, tuple(self.entry.variants),
                val, self.entry.lemma,
            ),
        )
        cancelled, variant = window.open()
        if cancelled:
            return

        self.dct.add_variant(self.entry, variant)

        self.refresh(False)

    def edit_variant(self, variant: str):
        window = InputDialog(
            self, self.app_data,
            'Введите новое слово',
            default_value=variant,
            check_answer_function=lambda wnd, val: check_variant_edit(
                wnd, self.app_data, tuple(self.entry.variants),
                variant, val, self.entry.lemma,
            ),
        )
        cancelled, new_variant = window.open()
        if cancelled:
            return

        new_entry, has_progres = edit_variant_or_merge(
            self.app_data, self, self.entry, variant, new_variant
        )
        if not has_progres:
            return
        self.entry = new_entry

        self.refresh(False)

    def remove_variant(self, variant: str):
        if len(self.variants) == 1:
            warning(self, self.app_data, 'Вы не можете удалить единственный вариант написания!')
            return

        self.dct.delete_variant(self.entry, variant)

        self.refresh(False)

    def add_translation(self):
        window = InputDialog(
            self, self.app_data,
            'Введите новый перевод',
            check_answer_function=lambda wnd, val: check_tr(
                wnd, self.app_data, self.entry.tr,
                val, self.entry.lemma,
            ),
        )
        cancelled, tr = window.open()
        if cancelled:
            return

        self.dct.add_tr(self.entry, tr)

        self.refresh(False)

    def edit_translation(self, tr: str):
        window = InputDialog(
            self, self.app_data,
            'Введите новый перевод',
            default_value=tr,
            check_answer_function=lambda wnd, val: check_tr_edit(
                wnd, self.app_data, self.entry.tr,
                tr, val, self.entry.lemma,
            ),
        )
        cancelled, new_tr = window.open()
        if cancelled:
            return

        self.dct.edit_tr(self.entry, tr, new_tr)

        self.refresh(False)

    def remove_translation(self, tr: str):
        if len(self.translations) == 1:
            warning(self, self.app_data, 'Вы не можете удалить единственный перевод!')
            return

        self.dct.delete_tr(self.entry, tr)

        self.refresh(False)

    def add_form(self):
        if not self.dct.features:
            warning(
                self, self.app_data,
                'Отсутствуют категории слов!\n'
                'Чтобы их добавить, перейдите в\n'
                'Настройки/Настройки открытого словаря/Грамматические категории',
            )
            return

        window_form = EnterFormW(
            self, self.app_data, self.entry, self.entry.lemma,
            combo_width=combobox_width(tuple(self.dct.features.keys()), 5, 100),
        )
        gram_form, word_form = window_form.open()
        if not gram_form:
            return

        self.dct.add_form(self.entry, gram_form, word_form)

        self.refresh(False)

    def edit_form(self, form: tuple[GramForm, WordForm]):
        gram_form, word_form = form

        window_form = EnterFormW(
            self, self.app_data, self.entry, word_form, list(gram_form),
            combo_width=combobox_width(tuple(self.dct.features.keys()), 5, 100),
        )
        new_gram_form, new_word_form = window_form.open()
        if not new_gram_form:
            return

        self.dct.edit_form(self.entry, gram_form, word_form, new_gram_form, new_word_form)

        self.refresh(False)

    def remove_form(self, form: tuple[GramForm, WordForm]):
        gram_form, word_form = form
        self.dct.delete_form(self.entry, gram_form, word_form)

        self.refresh(False)

    def add_phrase(self):
        window = EnterPhraseW(
            self, 'Добавление фразы', self.app_data,
            check_answer_function=lambda wnd, val: check_phr(
                wnd, self.app_data, self.entry.phrases,
                val, self.entry.lemma,
            ),
        )
        cancelled, phrase, phrase_tr = window.open()
        if cancelled:
            return

        self.dct.add_phrase(self.entry, phrase, phrase_tr)

        self.refresh(False)

    def edit_phrase(self, phrase_pair: tuple[str, str]):
        phrase, phrase_tr = phrase_pair

        window = EnterPhraseW(
            self, 'Изменение фразы', self.app_data,
            default_value=(phrase, phrase_tr),
            check_answer_function=lambda wnd, val: check_phr_edit(
                wnd, self.app_data, self.entry.phrases,
                (phrase, phrase_tr), val, self.entry.lemma,
            ),
        )
        cancelled, new_phrase, new_phrase_tr = window.open()
        if cancelled:
            return

        self.dct.edit_phrase(self.entry, phrase, phrase_tr, new_phrase, new_phrase_tr)

        self.refresh(False)

    def remove_phrase(self, phrase_pair: tuple[str, str]):
        phrase, phrase_tr = phrase_pair
        self.dct.delete_phrase(self.entry, phrase, phrase_tr)

        self.refresh(False)

    def add_note(self):
        window = InputDialog(
            self, self.app_data,
            'Введите сноску',
            check_answer_function=lambda wnd, val: check_note(
                wnd, self.app_data, self.entry.notes,
                val, self.entry.lemma,
            ),
        )
        cancelled, note = window.open()
        if cancelled:
            return

        self.dct.add_note(self.entry, note)

        self.refresh(False)

    def edit_note(self, note: str):
        window = InputDialog(
            self, self.app_data,
            'Введите сноску',
            default_value=note,
            check_answer_function=lambda wnd, val: check_note_edit(
                wnd, self.app_data, self.entry.notes,
                note, val, self.entry.lemma,
            ),
        )
        cancelled, new_note = window.open()
        if cancelled:
            return

        self.dct.edit_note(self.entry, note, new_note)

        self.refresh(False)

    def remove_note(self, note: str):
        self.dct.delete_note(self.entry, note)

        self.refresh(False)

    def add_tag(self):
        if not self.dct.tags:
            warning(
                self, self.app_data,
                'Отсутствуют группы!\n'
                'Чтобы их добавить, перейдите в\n'
                'Настройки/Настройки открытого словаря/Группы',
            )
            return
        values = [
            tag for tag in self.dct.tags
            if tag not in self.entry.tags
        ]
        if not values:
            warning(self, self.app_data, 'Статья уже добавлена во все группы')
            return

        window_tag = ChoiceDialog(
            self, self.app_data, values,
            'Выберите группу',
            default_value=values[0],
        )
        cancelled, tag = window_tag.open()
        if cancelled:
            return

        self.dct.add_tag_to_entries(tag, [self.entry])

        self.refresh(False)

    def remove_tag(self, tag: str):
        self.dct.remove_tag_from_entries(tag, [self.entry])

        self.refresh(False)

    def set_fav(self):
        self.entry.is_fav = self.var_fav.get()

    def delete_entry(self):
        window = TwoOptionsDialog(
            self, self.app_data,
            'Вы уверены, что хотите удалить эту статью?',
            focused_btn='none',
        )
        result = window.open()
        if result:
            self.dct.delete_entry(self.entry)
            self.destroy()

    def close(self):
        self.destroy()

    def refresh(self, move_scroll: bool):
        """Update displayed fields."""

        # Удаляем старые кнопки
        for btn in (
                self.var_buttons + self.tr_buttons + self.nt_buttons +
                self.phr_buttons + self.frm_buttons + self.gr_buttons
        ):
            btn.destroy()
        # Удаляем старые фреймы
        for fr in (
                self.var_frames + self.tr_frames + self.nt_frames +
                self.phr_frames + self.frm_frames + self.gr_frames
        ):
            fr.unbind('<Enter>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        # Выбираем содержимое
        self.variants = [var for var in self.entry.variants]
        self.translations = [tr for tr in self.entry.tr]
        self.notes = [note for note in self.entry.notes]
        self.phrases = []
        for phrase in self.entry.phrases.keys():
            for pt in self.entry.phrases[phrase]:
                self.phrases.append((phrase, pt))
        self.forms = []
        for gram_form, word_forms in self.entry.forms.items():
            for word_form in word_forms:
                self.forms.append((gram_form, word_form))
        self.tags = list(self.entry.tags)

        var_count = len(self.variants)
        tr_count = len(self.translations)
        nt_count = len(self.notes)
        phr_count = len(self.phrases)
        frm_count = len(self.forms)
        gr_count = len(self.tags)

        # Создаём новые фреймы
        self.var_frames = tuple(
            create_frame(
                self.scrolled_frame_variants.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(var_count)
        )
        self.tr_frames = tuple(
            create_frame(
                self.scrolled_frame_tr.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(tr_count)
        )
        self.nt_frames = tuple(
            create_frame(
                self.scrolled_frame_nt.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(nt_count)
        )
        self.phr_frames = tuple(
            create_frame(
                self.scrolled_frame_phr.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(phr_count)
        )
        self.frm_frames = tuple(
            create_frame(
                self.scrolled_frame_frm.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(frm_count)
        )
        self.gr_frames = tuple(
            create_frame(
                self.scrolled_frame_gr.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(gr_count)
        )

        # Создаём новые кнопки
        self.var_buttons = [
            create_button(
                self.var_frames[i],
                lambda i=i: self.edit_variant(self.variants[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(var_count)
        ]
        for i in range(var_count):
            variant = self.variants[i]
            self.var_buttons[i].configure(text=split_text(variant, 35))

        self.tr_buttons = [
            create_button(
                self.tr_frames[i],
                lambda i=i: self.edit_translation(self.translations[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(tr_count)
        ]
        for i in range(tr_count):
            tr = self.translations[i]
            self.tr_buttons[i].configure(text=split_text(tr, 35))

        self.nt_buttons = [
            create_button(
                self.nt_frames[i],
                lambda i=i: self.edit_note(self.notes[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(nt_count)
        ]
        for i in range(nt_count):
            note = self.notes[i]
            self.nt_buttons[i].configure(text=split_text(note, 35))

        self.phr_buttons = [
            create_button(
                self.phr_frames[i],
                lambda i=i: self.edit_phrase(self.phrases[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(phr_count)
        ]
        for i in range(phr_count):
            phrase = self.phrases[i][0]
            phrase_tr = self.phrases[i][1]
            self.phr_buttons[i].configure(text=split_text(f'{phrase} - {phrase_tr}', 35))

        self.frm_buttons = [
            create_button(
                self.frm_frames[i],
                lambda i=i: self.edit_form(self.forms[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(frm_count)
        ]
        for i in range(frm_count):
            gram_form = self.forms[i][0]
            word_form = self.forms[i][1]
            text = f'[{gram_form_to_str(gram_form)}] {word_form}'
            self.frm_buttons[i].configure(text=split_text(text, 35))

        self.gr_buttons = [
            create_button(
                self.gr_frames[i],
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(gr_count)
        ]
        for i in range(gr_count):
            tag = self.tags[i]
            self.gr_buttons[i].configure(text=split_text(tag, 35))

        # Привязываем события
        for i in range(var_count):
            self.var_frames[i].bind('<Enter>', lambda event, i=i: self.var_frames[i].focus_set())
            self.var_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.var_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_variant(self.variants[i]))
            self.var_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_variant(self.variants[i]))
        for i in range(tr_count):
            self.tr_frames[i].bind('<Enter>', lambda event, i=i: self.tr_frames[i].focus_set())
            self.tr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.tr_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_translation(self.translations[i]))
            self.tr_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_translation(self.translations[i]))
        for i in range(nt_count):
            self.nt_frames[i].bind('<Enter>', lambda event, i=i: self.nt_frames[i].focus_set())
            self.nt_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.nt_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_note(self.notes[i]))
            self.nt_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_note(self.notes[i]))
        for i in range(phr_count):
            self.phr_frames[i].bind('<Enter>', lambda event, i=i: self.phr_frames[i].focus_set())
            self.phr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.phr_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_phrase(self.phrases[i]))
            self.phr_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_phrase(self.phrases[i]))
        for i in range(frm_count):
            self.frm_frames[i].bind('<Enter>', lambda event, i=i: self.frm_frames[i].focus_set())
            self.frm_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frm_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_form(self.forms[i]))
            self.frm_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_form(self.forms[i]))
        for i in range(gr_count):
            self.gr_frames[i].bind('<Enter>', lambda event, i=i: self.gr_frames[i].focus_set())
            self.gr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.gr_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.remove_tag(self.tags[i]))
            self.gr_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.remove_tag(self.tags[i]))

        # Изменяем высоту полей
        self.scrolled_frame_variants.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.var_buttons
            ]), self.max_height_t)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_tr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.tr_buttons
            ]), self.max_height_t)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_nt.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.nt_buttons
            ]), self.max_height_n)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_phr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.phr_buttons
            ]), self.max_height_p)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_frm.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.frm_buttons
            ]), self.max_height_f)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_gr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.gr_buttons
            ]), self.max_height_g)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.ui_settings.scale - SCALE_MIN]
        )

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_variants.canvas.yview_moveto(0.0)
            self.scrolled_frame_tr.canvas.yview_moveto(0.0)
            self.scrolled_frame_nt.canvas.yview_moveto(0.0)
            self.scrolled_frame_phr.canvas.yview_moveto(0.0)
            self.scrolled_frame_frm.canvas.yview_moveto(0.0)
            self.scrolled_frame_gr.canvas.yview_moveto(0.0)

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы изменить поле, наведите на него мышку и нажмите ЛКМ\n'
            '* Чтобы удалить поле, наведите на него мышку и нажмите Ctrl+D\n\n'
            'Фразы: Сюда вы можете записать любые фразы с этим словом, '
            'как пример его употребления\n'
            'Сноски: Здесь вы можете указать любые факты об этом слове, '
            'которые посчитаете нужными\n'
            'Группы: Вы можете объединять слова, чтобы учить их группами\n',
            msg_justify='left',
        ).open()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_back.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


class EnterFormW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            entry: Entry,
            initial_value: str = '',
            gram_form: list[str] | None = None,
            combo_width: int = 20,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active
        self.dct = self.dct_bundle.dct
        self.replacer = self.dct_bundle.replacer

        self.entry = entry

        self.cancelled = True  # Закрыто ли окно крестиком
        self.categories = list(self.dct.features.keys())
        self.ctg_values = list(self.dct.features[self.categories[0]])
        self.initial_gram_form = ['' for _ in range(len(self.categories))]  # Пустой шаблон (для сравнения на пустоту)
        self.gram_form = gram_form or ['' for _ in range(len(self.categories))]

        self.var_ctg = tk.StringVar(value=self.categories[0])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.var_gram_form = tk.StringVar(
            value=f'Текущий шаблон словоформы: "{gram_form_to_str(self.gram_form)}"'
        )
        self.var_form = tk.StringVar(value=self.replacer.escape(initial_value))

        self.img_ok = tk.PhotoImage()
        self.img_none = tk.PhotoImage()

        self._configure_window()
        self._create_widgets(combo_width)

        if self.gram_form == self.initial_gram_form:
            btn_disable(self.btn_save)

        self.entry_form.icursor(len(self.var_form.get()))

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.gram_form)):
            if self.gram_form[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_ctg_values()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, combo_width: int):
        self.lbl_choose_ctg = create_label(
            self, 'Выберите категорию:', justify='center',
            row=0, column=0, padx=(6, 1), pady=(6, 1), sticky='E')
        self.combo_ctg = create_combobox(
            self, self.var_ctg, self.categories, combo_width,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=0, column=1, padx=(0, 6), pady=(6, 1), sticky='W')
        self.lbl_choose_val = create_label(
            self, 'Задайте значение категории:', justify='center',
            row=1, column=0, padx=(6, 1), pady=1, sticky='E')
        self._create_val_frame()
        self.lbl_gram_form = create_label(
            self, textvariable=self.var_gram_form, justify='center',
            row=2, columnspan=2, padx=6, pady=1)
        self._create_form_frame()
        self.btn_save = create_button(
            self, self.save, 'Готово',
            row=4, columnspan=2, padx=6, pady=6)

    def _create_val_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_val = create_frame(
            self, 'Invis.TFrame',
            row=1, column=1, padx=(0, 6), pady=1, sticky='W')

        self.combo_val = create_combobox(
            self.frame_val, self.var_val, self.ctg_values,
            combobox_width(self.ctg_values, 5, 100),
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=0, column=0, padx=0, pady=0)
        self.btn_choose = create_button(
            self.frame_val, self.select_ctg_value,
            row=0, column=1, padx=(3, 0), pady=0)
        set_image(self.btn_choose, self.img_ok, img_path(theme, 'ok'), 'Задать значение')
        self.btn_none = create_button(
            self.frame_val, self.remove_ctg_value,
            row=0, column=2, padx=0, pady=0)
        set_image(self.btn_none, self.img_none, img_path(theme, 'cancel'),
                  'Не указывать/неприменимо')

        if self.btn_choose['style'] == 'Image.TButton':
            self.tip_btn_choose = ttip.Hovertip(
                self.btn_choose, 'Задать значение', hover_delay=500)
        if self.btn_none['style'] == 'Image.TButton':
            self.tip_btn_none = ttip.Hovertip(
                self.btn_none, 'Не указывать/неприменимо', hover_delay=500)

    def _create_form_frame(self):
        self.frame_form = create_frame(
            self, 'Invis.TFrame',
            row=3, columnspan=2, padx=6, pady=6)

        self.lbl_form = create_label(
            self.frame_form, 'Форма:', justify='left',
            row=0, column=0, padx=(0, 1), pady=0, sticky='E')
        self.entry_form = create_entry(
            self.frame_form, self.var_form, font=self.app_data,
            row=0, column=1, padx=0, pady=0, sticky='W')

    def select_ctg_value(self):
        ctg = self.var_ctg.get()
        if ctg == '':
            return
        index = self.categories.index(ctg)

        val = self.var_val.get()
        if val == '':
            return
        self.gram_form[index] = val

        self.var_gram_form.set(f'Текущий шаблон словоформы: "{gram_form_to_str(self.gram_form)}"')

        if self.gram_form == self.initial_gram_form:
            btn_disable(self.btn_save)
        else:
            btn_enable(self.btn_save, self.save)

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.gram_form)):
            if self.gram_form[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_ctg_values()

    def remove_ctg_value(self):
        ctg = self.var_ctg.get()
        if ctg == '':
            return
        index = self.categories.index(ctg)

        self.gram_form[index] = ''

        self.var_gram_form.set(f'Текущий шаблон словоформы: "{gram_form_to_str(self.gram_form)}"')

        if self.gram_form == self.initial_gram_form:
            btn_disable(self.btn_save)
        else:
            btn_enable(self.btn_save, self.save)

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.gram_form)):
            if self.gram_form[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_ctg_values()

    def save(self):
        forms = self.entry.forms
        gram_form = tuple(self.gram_form)
        word_form = self.replacer.replace(self.var_form.get())

        if gram_form in forms and word_form == forms[gram_form]:
            warning(
                self, self.app_data,
                f'У слова "{self.entry.lemma}" уже есть такая форма!',
            )
            return
        if word_form == '':
            warning(self, self.app_data, 'Словоформа должна содержать хотя бы один символ!')
            return
        self.cancelled = False
        self.destroy()

    def refresh_ctg_values(self):
        self.ctg_values = list(self.dct.features[self.var_ctg.get()])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.combo_val.configure(
            textvariable=self.var_val, values=self.ctg_values,
            width=combobox_width(self.ctg_values, 5, 100),
        )

    def set_focus(self):
        self.focus_set()
        self.entry_form.focus_set()

        bind_ctrl_a(self.entry_form)
        self.bind('<Return>', lambda event: self.btn_choose.invoke())
        self.bind('<Escape>', lambda event: self.destroy())
        self.combo_ctg.bind('<<ComboboxSelected>>', lambda event: self.refresh_ctg_values())

    def open(self) -> tuple[GramForm, str] | tuple[None, None]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        if self.cancelled:
            return None, None
        if self.gram_form == self.initial_gram_form:
            return None, None
        forms = self.entry.forms
        gram_form = tuple(self.gram_form)
        word_form = self.replacer.replace(self.var_form.get())
        if gram_form in forms and word_form == forms[gram_form]:
            return None, None
        return gram_form, word_form


def change_tracked(cls):
    """
    Class decorator, similar to @dataclass, that adds change tracking.

    Fields are declared as annotations. For each field x the class gets:
        * x_cur - the current value;
        * x_init - the initial value (None if the item is new);
        * property `x` that reads/writes x_cur.

    Also added: is_new, is_deleted, delete(), _state(), and the status property.
    The generated __init__ takes the fields (in order) followed by is_new.
    """

    Status = Literal['new', 'deleted', 'modified', 'no changes']
    RESERVED = {'is_new', 'is_deleted', 'delete', 'status'}

    annotations = inspect.get_annotations(cls)
    fields = list(annotations)

    if not fields:
        raise TypeError(f'{cls.__name__}: no fields declared')
    for name in fields:
        if name in RESERVED:
            raise TypeError(f'{cls.__name__}: field name {name!r} is reserved')
        if name in vars(cls):
            raise TypeError(f'{cls.__name__}.{name}: default values are not supported')

    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    signature = inspect.Signature([
        inspect.Parameter('self', kind),
        *(inspect.Parameter(name, kind, annotation=annotations[name]) for name in fields),
        inspect.Parameter('is_new', kind, annotation=bool),
    ])

    def __init__(self, *args, **kwargs):
        arguments = signature.bind(self, *args, **kwargs).arguments
        is_new = arguments['is_new']
        for name in fields:
            value = arguments[name]
            setattr(self, f'{name}_cur', value)
            setattr(self, f'{name}_init', None if is_new else value)
        self.is_new = is_new
        self.is_deleted = False

    __init__.__signature__ = signature

    def _state(self) -> tuple:
        return (
            *(getattr(self, f'{name}_cur') for name in fields),
            *(getattr(self, f'{name}_init') for name in fields),
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is not self.__class__:
            return False

        return self._state() == other._state()

    def __str__(self) -> str:
        res = []
        if self.status == 'no changes':
            for name in fields:
                value_cur = getattr(self, f'{name}_cur')
                res.append(f'{name}: {value_cur}')
        else:
            for name in fields:
                value_cur = getattr(self, f'{name}_cur')
                value_init = getattr(self, f'{name}_init')
                res.append(f'{name}: {value_cur} [{value_init}]')
        return self.status + ' ~~~ ' + ',   '.join(res)

    def delete(self):
        for name in fields:
            setattr(self, f'{name}_cur', None)
        self.is_deleted = True

    def status(self) -> Status:
        if self.is_new:
            if self.is_deleted:
                return 'no changes'
            return 'new'
        if self.is_deleted:
            return 'deleted'
        for name in fields:
            if getattr(self, f'{name}_cur') != getattr(self, f'{name}_init'):
                return 'modified'
        return 'no changes'

    def make_property(name):
        cur = f'{name}_cur'
        return property(
            lambda self: getattr(self, cur),
            lambda self, value: setattr(self, cur, value),
            doc=f'Current value of {name!r}.',
        )

    cls.__init__ = __init__
    cls._state = _state
    cls.__eq__ = __eq__
    cls.__hash__ = None  # mutable object: must not be hashable
    cls.__str__ = __str__
    cls.delete = delete
    cls.status = property(status)
    for name in fields:
        setattr(cls, name, make_property(name))

    return cls


@change_tracked
class EditedTag:
    name: str
    is_default: bool


@change_tracked
class EditedCtgValue:
    name: str


@change_tracked
class EditedCtgName:
    name: str


@change_tracked
class EditedReplacement:
    modifier: str
    input_char: str
    output_char: str


class CategoriesSettingsW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            categories: list[tuple[EditedCtgName, list[EditedCtgValue]]],
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.img_help = tk.PhotoImage()

        self.categories = categories
        self.frames = []
        self.buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_categories(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        theme = self.app_data.ui_settings.theme

        self.btn_help = create_button(
            self, self.show_help, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_help, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_categories = create_label(
            self, 'Существующие категории слов:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add_ctg, 'Добавить категорию',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_help, 'Справка', hover_delay=450
        )

    def add_ctg(self):
        window_ctg = InputDialog(
            self, self.app_data,
            'Введите название новой категории',
            check_answer_function=lambda wnd, val: check_ctg(
                wnd, self.app_data, [c.name for c, _ in self.categories], val
            ),
        )
        cancelled, new_ctg = window_ctg.open()
        if cancelled:
            return

        window_val = InputDialog(
            self, self.app_data,
            'Необходимо добавить хотя бы одно значение для категории',
            check_answer_function=lambda wnd, val: check_ctg_val(wnd, self.app_data, (), val),
        )
        cancelled, new_ctg_val = window_val.open()
        if cancelled:
            return

        self.categories.append((
            EditedCtgName(new_ctg, is_new=True),
            [EditedCtgValue(new_ctg_val, is_new=True)]
        ))

        self.print_categories(False)

    def rename_ctg(self, ctg: EditedCtgName):
        window_entry = InputDialog(
            self, self.app_data,
            'Введите новое название категории',
            default_value=ctg.name,
            check_answer_function=lambda wnd, val: check_ctg_edit(
                wnd, self.app_data, [c.name for c, _ in self.categories], ctg.name, val
            ),
        )
        cancelled, new_ctg_name = window_entry.open()
        if cancelled:
            return
        if new_ctg_name == ctg.name:
            return

        ctg.name = new_ctg_name

        self.print_categories(False)

    def delete_ctg(self, ctg: EditedCtgName):
        window_dia = TwoOptionsDialog(
            self, self.app_data,
            f'Все словоформы, содержащие категорию {ctg.name}, будут удалены!\n'
            f'Хотите продолжить?',
        )
        result = window_dia.open()
        if not result:
            return

        ctg.delete()

        self.print_categories(False)

    def edit_ctg_values(self, ctg: EditedCtgName, ctg_vals: list[EditedCtgValue]):
        new_ctg_vals = CategoryValuesSettingsW(self, self.app_data, ctg.name, ctg_vals).open()

        if all(val.is_deleted for val in new_ctg_vals):
            ctg.delete()
            self.print_categories(False)

    def print_categories(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-R>')
            fr.unbind('<Control-r>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        categories = [(k, v) for k, v in self.categories if not k.is_deleted]
        categories_count = len(categories)

        # Создаём новые фреймы
        self.frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(categories_count)
        ]
        # Создаём новые кнопки
        self.buttons = [
            create_button(
                self.frames[i],
                lambda ctg=ctg, vals=vals: self.edit_ctg_values(ctg, vals),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i, (ctg, vals) in enumerate(categories)
        ]
        for i, (ctg, vals) in enumerate(categories):
            self.buttons[i].configure(text=split_text(f'{ctg.name}', 35))

            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, ctg=ctg: self.rename_ctg(ctg))
            self.frames[i].bind('<Control-R>', lambda event, ctg=ctg: self.rename_ctg(ctg))
            self.frames[i].bind('<Control-d>', lambda event, ctg=ctg: self.delete_ctg(ctg))
            self.frames[i].bind('<Control-D>', lambda event, ctg=ctg: self.delete_ctg(ctg))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы добавить значение категории, наведите на неё мышку и нажмите ЛКМ\n'
            '* Чтобы переименовать категорию, наведите на неё мышку и нажмите Ctrl+R\n'
            '* Чтобы удалить категорию, наведите на неё мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> list[tuple[EditedCtgName, list[EditedCtgValue]]]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.categories


class TagSettingsW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData, tags: list[EditedTag]):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.img_help = tk.PhotoImage()

        self.tags = tags
        self.frames = []
        self.buttons = []
        self.tips = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_tags(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        theme = self.app_data.ui_settings.theme

        self.btn_help = create_button(
            self, self.show_help, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_help, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_tags = create_label(
            self, 'Существующие группы:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add_tag, 'Добавить группу',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_help, 'Справка', hover_delay=450
        )

    def add_tag(self):
        window = InputDialog(
            self, self.app_data,
            'Введите название новой группы',
            check_answer_function=lambda wnd, val: check_tag_name(
                wnd, self.app_data, [t.name for t in self.tags], val
            ),
        )
        cancelled, tag = window.open()
        if cancelled:
            return

        self.tags.append(EditedTag(tag, False, is_new=True))

        self.print_tags(False)

    def rename_tag(self, tag: EditedTag):
        window = InputDialog(
            self, self.app_data,
            'Введите новое название группы',
            default_value=tag.name,
            check_answer_function=lambda wnd, val: check_tag_name_edit(
                wnd, self.app_data, [t.name for t in self.tags], tag.name, val
            ),
        )
        cancelled, tag_new = window.open()
        if cancelled:
            return

        tag.name = tag_new

        self.print_tags(False)

    def delete_tag(self, tag: EditedTag):
        tag_size = count_filtered_entries(self.dct, tag.name)[0]
        if tag_size != 0:
            tmp = select_word_form(
                tag_size,
                ('слова будет убрано', 'слов будут убраны', 'слов будут убраны'),
            )
            window_dia = TwoOptionsDialog(
                self, self.app_data,
                f'До {tag_size} {tmp} из группы "{tag.name}", а сама группа будет удалена!\n'
                f'Хотите продолжить?',
            )
            result = window_dia.open()
            if not result:
                return

        tag.delete()

        self.print_tags(False)

    def set_tag_default(self, tag: EditedTag):
        tag.is_default = not tag.is_default

        self.print_tags(False)

    def print_tags(self, move_scroll: bool):
        # Удаляем старые подсказки
        for tip in self.tips:
            tip.__del__()
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-R>')
            fr.unbind('<Control-r>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        tags = [tag for tag in self.tags if not tag.is_deleted]
        tags_count = len(self.tags)

        # Создаём новые фреймы
        self.frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(tags_count)
        ]
        # Создаём новые кнопки
        self.buttons = [
            create_button(
                self.frames[i],
                lambda tag=tag: self.rename_tag(tag),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i, tag in enumerate(tags)
        ]
        # Создаём новые подсказки
        self.tips = [
            ttip.Hovertip(
                self.buttons[i],
                f'Статей в группе: {count_filtered_entries(self.dct, tag.name)[0]}',
                hover_delay=500,
            ) for i, tag in enumerate(tags)
        ]
        for i, tag in enumerate(tags):
            if tag.is_default:
                self.buttons[i].configure(text=split_text(f'{tag.name} (*)', 35))
            else:
                self.buttons[i].configure(text=split_text(f'{tag.name}', 35))

            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, tag=tag: self.rename_tag(tag))
            self.frames[i].bind('<Control-R>', lambda event, tag=tag: self.rename_tag(tag))
            self.frames[i].bind('<Control-d>', lambda event, tag=tag: self.delete_tag(tag))
            self.frames[i].bind('<Control-D>', lambda event, tag=tag: self.delete_tag(tag))
            self.frames[i].bind('<Control-f>', lambda event, tag=tag: self.set_tag_default(tag))
            self.frames[i].bind('<Control-F>', lambda event, tag=tag: self.set_tag_default(tag))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы переименовать группу, наведите на неё мышку и нажмите ЛКМ или Ctrl+R\n'
            '* Чтобы удалить группу, наведите на неё мышку и нажмите Ctrl+D\n'
            '* Чтобы все новые статьи автоматически добавлялись в группу, '
            'наведите на эту группу мышку и нажмите Ctrl+F',
            msg_justify='left',
        ).open()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> list[EditedTag]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.tags


class CategoryValuesSettingsW(tk.Toplevel):
    def __init__(self, parent: CategoriesSettingsW, app_data: AppData, ctg_name: str, ctg_values: list[EditedCtgValue]):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.img_help = tk.PhotoImage()

        self.ctg_name = ctg_name
        self.ctg_values = ctg_values
        self.frames = []
        self.buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_values(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        theme = self.app_data.ui_settings.theme

        self.btn_help = create_button(
            self, self.show_help, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_help, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_ctg_values = create_label(
            self,
            f'Существующие значения категории\n'
            f'"{self.ctg_name}":',
            justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add_value, 'Добавить значение',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_help, 'Справка', hover_delay=450
        )

    def add_value(self):
        window_entry = InputDialog(
            self, self.app_data,
            'Введите новое значение категории',
            check_answer_function=lambda wnd, val: check_ctg_val(
                wnd, self.app_data, [v.name for v in self.ctg_values], val
            ),
        )
        cancelled, new_ctg_val = window_entry.open()
        if cancelled:
            return

        self.ctg_values.append(EditedCtgValue(new_ctg_val, is_new=True))

        self.print_values(False)

    def rename_value(self, val: EditedCtgValue):
        window_entry = InputDialog(
            self, self.app_data,
            'Введите новое название значения',
            default_value=val.name,
            check_answer_function=lambda wnd, new_val: check_ctg_val_edit(
                wnd, self.app_data, [v.name for v in self.ctg_values], val.name, new_val
            ),
        )
        cancelled, new_ctg_val = window_entry.open()
        if cancelled:
            return
        if new_ctg_val == val.name:
            return

        val.name = new_ctg_val

        self.print_values(False)

    def delete_value(self, val: EditedCtgValue):
        window_dia = TwoOptionsDialog(
            self, self.app_data,
            f'Все словоформы, содержащие значение {val.name}, будут удалены!\n'
            f'Хотите продолжить?',
        )
        result = window_dia.open()
        if not result:
            return

        val.delete()

        self.print_values(False)
        if all(val.is_deleted for val in self.ctg_values):
            self.parent.print_categories(False)
            self.destroy()

    def print_values(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-R>')
            fr.unbind('<Control-r>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        ctg_values = [val for val in self.ctg_values if not val.is_deleted]
        n_values = len(ctg_values)

        # Создаём новые фреймы
        self.frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(n_values)
        ]
        # Создаём новые кнопки
        self.buttons = [
            create_button(
                self.frames[i],
                lambda val=val: self.rename_value(val),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i, val in enumerate(ctg_values)
        ]
        for i, val in enumerate(ctg_values):
            self.buttons[i].configure(text=split_text(f'{val.name}', 35))

            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, val=val: self.rename_value(val))
            self.frames[i].bind('<Control-R>', lambda event, val=val: self.rename_value(val))
            self.frames[i].bind('<Control-d>', lambda event, val=val: self.delete_value(val))
            self.frames[i].bind('<Control-D>', lambda event, val=val: self.delete_value(val))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы переименовать значение, наведите на него мышку и нажмите ЛКМ или Ctrl+R\n'
            '* Чтобы удалить значение, наведите на него мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> list[EditedCtgValue]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.ctg_values


class InputReplacementsSettingsW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData, replacements: list[EditedReplacement]):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.img_help = tk.PhotoImage()

        self.replacements = replacements
        self.frames = []
        self.buttons = {}

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_replacements(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        theme = self.app_data.ui_settings.theme

        self.btn_help = create_button(
            self, self.show_help, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_help, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_replacements = create_label(
            self, 'Существующие комбинации:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add_replacement, 'Добавить комбинацию',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_help, 'Справка', hover_delay=450
        )

    def add_replacement(self):
        window = EnterInputReplacementW(self, self.app_data)
        cancelled, modifier, key, val = window.open()
        if cancelled or modifier == '' or key == '' or val == '':
            return
        if (modifier, key) in self.replacements:
            warning(self, self.app_data, f'Комбинация {modifier}{key} уже существует!')
            return

        self.replacements.append(EditedReplacement(modifier, key, val, is_new=True))

        self.print_replacements(False)

    def edit_replacement(self, rep: EditedReplacement):
        window = EnterInputReplacementW(
            self, self.app_data, default_value=(rep.modifier, rep.input_char, rep.output_char)
        )
        cancelled, new_modifier, new_key, new_val = window.open()
        if cancelled or new_modifier == '' or new_key == '' or new_val == '':
            return
        if new_modifier == rep.modifier and new_key == rep.input_char and new_val == rep.output_char:
            return

        rep.modifier = new_modifier
        rep.input_char = new_key
        rep.output_char = new_val

        self.print_replacements(False)

    def delete_replacement(self, rep: EditedReplacement):
        rep.delete()

        self.print_replacements(False)

    def print_replacements(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons.values():
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-E>')
            fr.unbind('<Control-e>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        replacements = [rep for rep in self.replacements if not rep.is_deleted]

        # Создаём новые фреймы
        self.frames = [
            create_label(
                self.scrolled_frame.frame_canvas,
                replacement_repr((rep.modifier, rep.input_char), rep.output_char),
                'FlatL.TLabel',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            )
            if rep.modifier == rep.input_char else
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            )
            for i, rep in enumerate(replacements)
        ]
        # Создаём новые кнопки
        self.buttons = {
            i: create_button(
                self.frames[i],
                lambda rep=rep: self.edit_replacement(rep),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i, rep in enumerate(replacements) if rep.modifier != rep.input_char
        }

        for i, rep in enumerate(replacements):
            if rep.modifier == rep.input_char:
                continue

            self.buttons[i].configure(text=split_text(
                replacement_repr((rep.modifier, rep.input_char), rep.output_char), 35
            ))

            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-e>', lambda event, rep=rep: self.edit_replacement(rep))
            self.frames[i].bind('<Control-E>', lambda event, rep=rep: self.edit_replacement(rep))
            self.frames[i].bind('<Control-d>', lambda event, rep=rep: self.delete_replacement(rep))
            self.frames[i].bind('<Control-D>', lambda event, rep=rep: self.delete_replacement(rep))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы изменить комбинацию, наведите на неё мышку и нажмите ЛКМ или Ctrl+E\n'
            '* Чтобы удалить комбинацию, наведите на неё мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> list[EditedReplacement]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.replacements


class EnterInputReplacementW(tk.Toplevel):
    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            default_value: tuple[str, str, str] | None = None,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.replacer = app_data.manager.active.replacer

        self.cancelled = True  # Закрыто ли окно крестиком

        if not default_value:
            default_value = (tuple(self.replacer.modifiers)[0], None, None)
        self.var_modifier = tk.StringVar(value=default_value[0])
        self.var_base = tk.StringVar(value=default_value[1])
        self.var_output = tk.StringVar(value=default_value[2])

        self.vcmd_modifier = (
            self.register(lambda val: validate_replacement_modifier(val, self.replacer)), '%P'
        )
        self.vcmd_base = (
            self.register(lambda val: validate_replacement_base(val, self.replacer)), '%P'
        )
        self.vcmd_output = (self.register(validate_replacement_output), '%P')

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_msg = create_label(
            self, 'Задайте комбинацию', justify='center',
            row=0, padx=6, pady=(6, 3))
        self._create_main_frame()
        self.btn_ok = create_button(
            self, self.on_ok, 'Подтвердить', style='Yes.TButton',
            row=2, padx=6, pady=6)

    def _create_main_frame(self):
        self.frame_main = create_frame(self, 'Invis.TFrame', row=1, padx=6, pady=0)

        self.combo_modifier = create_combobox(
            self.frame_main, self.var_modifier, tuple(self.replacer.modifiers), 3,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale), state='normal',
            validate='all', validatecommand=self.vcmd_modifier,
            row=0, column=0, padx=0, pady=0)
        self.entry_key = create_entry(
            self.frame_main, self.var_base, 2, font=self.app_data,
            justify='right', validate='key', validatecommand=self.vcmd_base,
            row=0, column=1, padx=0, pady=0)
        self.lbl_arrow = create_label(
            self.frame_main, '->', justify='center',
            row=0, column=2, padx=2, pady=0)
        self.entry_val = create_entry(
            self.frame_main, self.var_output, 2, font=self.app_data,
            validate='key', validatecommand=self.vcmd_output,
            row=0, column=3, padx=0, pady=0)

    def on_ok(self):
        self.cancelled = False
        self.destroy()

    def set_focus(self):
        self.focus_set()
        self.entry_key.focus_set()

        bind_ctrl_a(self.entry_val)
        bind_ctrl_a(self.entry_key)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> tuple[bool, str, str, str]:
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.cancelled, self.var_modifier.get(), self.var_base.get(), self.var_output.get()


class CustomThemeSettingsW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.custom_styles = {}  # Стили пользовательской темы
        self.history = []  # История изменений
        self.history_undo = []  # История отмен
        self.dir_with_images = CUSTOM_THEME_DIR

        self.var_theme = tk.StringVar(value=DEFAULT_TH)
        self.var_images = tk.StringVar(value=DEFAULT_TH)
        self.var_relief_frame = tk.StringVar()
        self.var_relief_text = tk.StringVar()

        self.img_undo = tk.PhotoImage()
        self.img_redo = tk.PhotoImage()

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.entry_demo.insert(tk.END, 'abcde 12345')
        self.txt_demo.insert(tk.END, '1')
        for i in range(2, 51):
            self.txt_demo.insert(tk.END, f'\n{i}')
        self.txt_demo.config(yscrollcommand=self.scroll_demo.set, state='disabled')

        self._load()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Настройки пользовательской темы')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self._create_themes_frame()
        self._create_scrolled_frame()
        self._create_buttons_frame()
        self._create_demonstration_frame()

    def _create_themes_frame(self):
        self.frame_themes = create_frame(
            self, 'Invis.TFrame',
            row=0, column=0, columnspan=2, padx=6, pady=(6, 0), sticky='W')

        self.lbl_set_theme = create_label(
            self.frame_themes, 'Взять за основу уже существующую тему:',
            row=0, column=0, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_set_theme = create_combobox(
            self.frame_themes, self.var_theme, THEMES[1:],
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=0, column=1, padx=(0, 3), pady=(0, 6))
        self.btn_set_theme = create_button(
            self.frame_themes, self.set_theme, 'Выбрать', width=8,
            row=0, column=2, padx=(0, 0), pady=(0, 6), sticky='W')
        self.lbl_set_images = create_label(
            self.frame_themes, 'Использовать изображения из темы:',
            row=1, column=0, padx=(0, 1), pady=0, sticky='E')
        self.combo_set_images = create_combobox(
            self.frame_themes, self.var_images, THEMES[1:],
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=1, column=1, padx=(0, 3), pady=0)
        self.btn_set_images = create_button(
            self.frame_themes, self.set_images, 'Выбрать', width=8,
            row=1, column=2, padx=(0, 0), pady=0, sticky='W')

    def _create_scrolled_frame(self):
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_CUSTOM_THEME_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(row=1, column=0, padx=6, pady=6)

        self.labels = [
            create_label(self.scrolled_frame.frame_canvas)
            for _ in range(len(STYLE_KEYS))
        ]
        self.buttons = [
            tk.Button(
                self.scrolled_frame.frame_canvas,
                relief='solid', overrelief='raised',
                borderwidth=1, width=18,
            ) for _ in range(len(STYLE_KEYS))
        ]
        # Получается по 2 лишних экземпляра каждого виджета (но пусть будет так)

        for i in range(len(STYLE_KEYS)):
            st_key = STYLE_KEYS[i]
            if st_key not in ('FRAME.RELIEF.*', 'TXT.RELIEF.*'):
                self.labels[i].configure(text=f'{STYLES[st_key][0]}:')
                self.buttons[i].configure(command=lambda i=i: self.select_color(i))

                self.labels[i].grid(row=i, column=0, padx=(6, 1), sticky='E')
                self.buttons[i].grid(row=i, column=1, padx=(0, 6), sticky='W')
                if i == 0:
                    self.labels[i].grid(pady=(6, 3))
                    self.buttons[i].grid(pady=(6, 3))
                elif i == len(STYLE_KEYS) - 1:
                    self.labels[i].grid(pady=(0, 6))
                    self.buttons[i].grid(pady=(0, 6))
                else:
                    self.labels[i].grid(pady=(0, 3))
                    self.buttons[i].grid(pady=(0, 3))

        def _choose_relief(elem, value):
            if self.custom_styles[elem] != value:
                self.history.append((elem, self.custom_styles[elem], value))
                self.history_undo.clear()
            self.set_demo_styles()
            return True

        self.vcmd_relief_frame = (
            self.register(lambda value: _choose_relief('FRAME.RELIEF.*', value)), '%P')
        self.vcmd_relief_text = (
            self.register(lambda value: _choose_relief('TXT.RELIEF.*', value)), '%P')

        self.lbl_relief_frame = create_label(
            self.scrolled_frame.frame_canvas, 'Стиль рамок фреймов:',
            row=9, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_frame = create_combobox(
            self.scrolled_frame.frame_canvas, self.var_relief_frame,
            ('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
            SCALE_CUSTOM_THEME_COMBO_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN],
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            validate='focus', validatecommand=self.vcmd_relief_frame, state='readonly',
            row=9, column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_relief_text = create_label(
            self.scrolled_frame.frame_canvas, 'Стиль рамок текстовых полей:',
            row=10, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_text = create_combobox(
            self.scrolled_frame.frame_canvas, self.var_relief_text,
            ('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
            SCALE_CUSTOM_THEME_COMBO_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN],
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            validate='focus', validatecommand=self.vcmd_relief_text, state='readonly',
            row=10, column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')

    def _create_buttons_frame(self):
        self.frame_buttons = create_frame(
            self, 'Invis.TFrame',
            row=2, column=0, padx=6, pady=(0, 6))

        self.btn_save = create_button(
            self.frame_buttons, self.save, 'Сохранить', style='Yes.TButton',
            row=0, column=0, padx=(0, 36), pady=0)
        self._create_history_frame()

    def _create_history_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_history = create_frame(
            self.frame_buttons, 'Invis.TFrame',
            row=0, column=1, padx=0, pady=0)

        self.btn_undo = create_button(
            self.frame_history, self.undo, width=2,
            row=0, column=0, padx=(0, 6), pady=0, sticky='W')
        set_image(self.btn_undo, self.img_undo, img_path(theme, 'undo'), '<<')
        self.btn_redo = create_button(
            self.frame_history, self.redo, width=2,
            row=0, column=1, padx=0, pady=0, sticky='W')
        set_image(self.btn_redo, self.img_redo, img_path(theme, 'redo'), '>>')

    def _create_demonstration_frame(self):
        self.frame_demonstration = create_frame(
            self, 'Window.TFrame', relief='solid',
            row=1, rowspan=2, column=1, padx=6, pady=6)

        self.lbl_demo_header = create_label(
            self.frame_demonstration,
            'Anenokil development presents', 'DemoHeader.TLabel',
            row=0, column=0, columnspan=3, padx=12, pady=(12, 0))
        self.lbl_demo_logo = create_label(
            self.frame_demonstration,
            'Демонстрация', 'DemoLogo.TLabel',
            row=1, column=0, columnspan=3, padx=12, pady=(0, 12))
        self._create_demo_check_frame()
        self.entry_demo = create_entry(
            self.frame_demonstration,
            width=20, style='DemoDefault.TEntry',
            font=('StdFont', self.app_data.ui_settings.scale),
            row=2, column=1, columnspan=2, padx=(0, 6), pady=(0, 6), sticky='SW')
        self.btn_demo_def = create_button(
            self.frame_demonstration,
            text='Кнопка', style='DemoDefault.TButton',
            row=3, column=0, padx=6, pady=(0, 6), sticky='E')
        self.btn_demo_dis = create_button(
            self.frame_demonstration,
            text='Выключена', style='DemoDisabled.TButton',
            row=4, column=0, padx=6, pady=(0, 6), sticky='E')
        self.btn_demo_y = create_button(
            self.frame_demonstration,
            text='Да', style='DemoYes.TButton',
            row=5, column=0, padx=6, pady=(0, 6), sticky='E')
        self.btn_demo_n = create_button(
            self.frame_demonstration,
            text='Нет', style='DemoNo.TButton',
            row=6, column=0, padx=6, pady=(0, 6), sticky='E')
        self.txt_demo = tk.Text(
            self.frame_demonstration,
            font=('StdFont', self.app_data.ui_settings.scale),
            width=12, height=4, state='normal')
        self.txt_demo.grid(
            row=3, rowspan=4, column=1, padx=0, pady=(0, 6), sticky='SNWE')
        self.scroll_demo = ttk.Scrollbar(
            self.frame_demonstration,
            command=self.txt_demo.yview,
            style='Demo.Vertical.TScrollbar')
        self.scroll_demo.grid(
            row=3, rowspan=4, column=2, padx=(0, 6), pady=(0, 6), sticky='SNW')
        self._create_demo_img_frame()
        self.lbl_demo_warn = create_label(
            self.frame_demonstration,
            'Предупреждение!', 'DemoWarn.TLabel',
            row=8, column=0, columnspan=3, padx=6, pady=(0, 6))
        self.lbl_demo_footer = create_label(
            self.frame_demonstration,
            'Нижний колонтитул', 'DemoFooter.TLabel',
            row=9, column=0, columnspan=3, padx=6, pady=(0, 6))

    def _create_demo_check_frame(self):
        self.frame_demo_check = create_frame(
            self.frame_demonstration, 'DemoDefault.TFrame',
            row=2, column=0, padx=6, pady=(0, 6), sticky='E')

        self.lbl_demo_def = create_label(
            self.frame_demo_check, 'Надпись:', 'DemoDefault.TLabel',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_demo = create_checkbutton(
            self.frame_demo_check, style='DemoDefault.TCheckbutton',
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')

    def _create_demo_img_frame(self):
        self.frame_demo_img = create_frame(
            self.frame_demonstration, 'DemoDefault.TFrame',
            row=7, column=0, columnspan=3, padx=6, pady=(0, 6))

        self.images = [tk.PhotoImage(file='') for _ in range(len(ICON_NAMES))]
        self.img_buttons = [
            create_button(
                self.frame_demo_img, width=2,
                row=i // 7, column=i % 7, padx=3, pady=3
            ) for i in range(len(ICON_NAMES))
        ]
        self.refresh_images()

    def _create_tips(self):
        self.tip_btn_undo = ttip.Hovertip(
            self.btn_undo, 'Отменить последнее действие', hover_delay=450
        )
        self.tip_btn_redo = ttip.Hovertip(
            self.btn_redo, 'Вернуть отменённое действие', hover_delay=450
        )

    def set_theme(self):
        """Use an existing theme as a base."""

        theme_name = self.var_theme.get()
        old_vals = []
        new_vals = []
        for i in range(len(STYLE_KEYS)):
            st_key = STYLE_KEYS[i]
            st_val = STYLES[st_key][1][theme_name]

            if st_key == 'FRAME.RELIEF.*':
                self.var_relief_frame.set(st_val)
            elif st_key == 'TXT.RELIEF.*':
                self.var_relief_text.set(st_val)
            else:
                self.buttons[i].config(bg=st_val, activebackground=st_val)

            old_vals.append(self.custom_styles[st_key])
            new_vals.append(st_val)
            self.custom_styles[st_key] = st_val

        self.set_demo_styles()

        self.history.append(('all', old_vals, new_vals))
        self.history_undo.clear()

        self.var_images.set(theme_name)
        self.set_images()

    def set_images(self):
        """Choose images."""

        old_img = self.dir_with_images
        new_img = THEMES_DIR / self.var_images.get()

        self.dir_with_images = new_img

        self.history.append(('img', old_img, new_img))
        self.history_undo.clear()

        self.refresh_images()

    def select_color(self, n: int):
        st_key = STYLE_KEYS[n]
        hx = self.custom_styles[st_key]

        rgb, new_hx = colorchooser.askcolor(hx)
        if not new_hx:
            return

        self.buttons[n].config(bg=new_hx, activebackground=new_hx)
        self.custom_styles[st_key] = new_hx

        self.set_demo_styles()

        if new_hx != hx:
            self.history.append((st_key, hx, new_hx))
            self.history_undo.clear()

    def save(self):
        self.custom_styles['FRAME.RELIEF.*'] = self.var_relief_frame.get()
        self.custom_styles['TXT.RELIEF.*'] = self.var_relief_text.get()
        filepath = CUSTOM_THEME_DIR / STYLES_FN
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'{REQUIRED_THEME_VERSION}')
            file.write('\n1')
            for el in STYLE_KEYS:
                file.write(f'\n{el} = {self.custom_styles[el]}')

        if self.dir_with_images != CUSTOM_THEME_DIR:
            for img_name in IMG_NAMES:
                file_name = f'{img_name}.png'
                src_path = self.dir_with_images / file_name
                dst_path = CUSTOM_THEME_DIR / file_name
                if (CUSTOM_THEME_DIR / file_name).exists():
                    dst_path.unlink()
                if (self.dir_with_images / file_name).exists():
                    shutil.copyfile(src_path, dst_path)

    def undo(self):
        if self.history:
            last_action = self.history[-1]

            var = last_action[0]
            if var == 'all':
                vals = last_action[1]
                for i in range(len(STYLE_KEYS)):
                    el = STYLE_KEYS[i]

                    if el == 'FRAME.RELIEF.*':
                        self.var_relief_frame.set(vals[i])
                    elif el == 'TXT.RELIEF.*':
                        self.var_relief_text.set(vals[i])
                    else:
                        self.buttons[i].config(bg=vals[i], activebackground=vals[i])

                    self.custom_styles[el] = vals[i]
            elif var == 'img':
                val = last_action[1]
                self.dir_with_images = val

                self.refresh_images()
            else:
                el = var
                val = last_action[1]
                self.custom_styles[el] = val
                if el == 'FRAME.RELIEF.*':
                    self.var_relief_frame.set(val)
                elif el == 'TXT.RELIEF.*':
                    self.var_relief_text.set(val)
                else:
                    i = STYLE_KEYS.index(el)
                    self.buttons[i].config(bg=val, activebackground=val)

            self.history_undo.append(last_action)
            self.history.pop(-1)

            self.set_demo_styles()

    def redo(self):
        if self.history_undo:
            last_undo_action = self.history_undo[-1]

            var = last_undo_action[0]
            if var == 'all':
                vals = last_undo_action[2]
                for i in range(len(STYLE_KEYS)):
                    el = STYLE_KEYS[i]

                    if el == 'FRAME.RELIEF.*':
                        self.var_relief_frame.set(vals[i])
                    elif el == 'TXT.RELIEF.*':
                        self.var_relief_text.set(vals[i])
                    else:
                        self.buttons[i].config(bg=vals[i], activebackground=vals[i])

                    self.custom_styles[el] = vals[i]
            elif var == 'img':
                val = last_undo_action[2]
                self.dir_with_images = val

                self.refresh_images()
            else:
                el = var
                val = last_undo_action[2]
                self.custom_styles[el] = val
                if el == 'FRAME.RELIEF.*':
                    self.var_relief_frame.set(val)
                elif el == 'TXT.RELIEF.*':
                    self.var_relief_text.set(val)
                else:
                    i = STYLE_KEYS.index(el)
                    self.buttons[i].config(bg=val, activebackground=val)

            self.history.append(last_undo_action)
            self.history_undo.pop(-1)

            self.set_demo_styles()

    def _load(self):
        filepath = CUSTOM_THEME_DIR / STYLES_FN
        upgrade_theme(filepath)
        with open(filepath, 'r', encoding='utf-8') as file:
            file.readline()  # Версия темы
            file.readline()  # Переменная обновлений
            i = 0
            while True:
                line = file.readline().strip()
                data = [v for v in re.split(' |=|//', line) if v != '']  # После // идут комментарии
                if not data:
                    break
                key = data[0].strip()
                val = data[1].strip()
                self.custom_styles[key] = val  # Добавляем новый стиль для элемента, соответствующий теме theme

                if key == 'FRAME.RELIEF.*':
                    self.var_relief_frame.set(self.custom_styles[key])
                elif key == 'TXT.RELIEF.*':
                    self.var_relief_text.set(self.custom_styles[key])
                else:
                    self.buttons[i].config(
                        bg=self.custom_styles[key], activebackground=self.custom_styles[key]
                    )
                i += 1
        # Устанавливаем значения оставшихся стилей на значения по умолчанию
        for key in STYLE_KEYS:
            if key not in self.custom_styles:
                self.custom_styles[key] = STYLES[key][1][DEFAULT_TH]

        self.set_demo_styles()

    def set_demo_styles(self):
        self.custom_styles['FRAME.RELIEF.*'] = self.var_relief_frame.get()
        self.custom_styles['TXT.RELIEF.*'] = self.var_relief_text.get()

        self.txt_demo.config(
            relief=self.custom_styles['TXT.RELIEF.*'],
            bg=self.custom_styles['*.BG.ENTRY'],
            fg=self.custom_styles['*.FG.*'],
            selectbackground=self.custom_styles['*.BG.SEL'],
            selectforeground=self.custom_styles['*.FG.SEL'],
            highlightbackground=self.custom_styles['*.BORDER_CLR.*'],
        )

        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure(
            'DemoDefault.TLabel',
            font=('StdFont', self.app_data.ui_settings.scale),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.*'],
        )

        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure(
            'DemoHeader.TLabel',
            font=('StdFont', self.app_data.ui_settings.scale + 5),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.*'],
        )

        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure(
            'DemoLogo.TLabel',
            font=('Times', self.app_data.ui_settings.scale + 11),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.LOGO'],
        )

        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure(
            'DemoFooter.TLabel',
            font=('StdFont', self.app_data.ui_settings.scale - 2),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.FOOTER'],
        )

        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure(
            'DemoWarn.TLabel',
            font=('StdFont', self.app_data.ui_settings.scale),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.WARN'],
        )

        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure(
            'DemoDefault.TEntry',
            font=('StdFont', self.app_data.ui_settings.scale),
        )
        self.st_entry.map(
            'DemoDefault.TEntry',
            fieldbackground=[
                ('readonly', self.custom_styles['*.BG.*']),
                ('!readonly', self.custom_styles['*.BG.ENTRY']),
            ],
            foreground=[
                ('readonly', self.custom_styles['*.FG.*']),
                ('!readonly', self.custom_styles['*.FG.ENTRY']),
            ],
            selectbackground=[
                ('readonly', self.custom_styles['*.BG.SEL']),
                ('!readonly', self.custom_styles['*.BG.SEL']),
            ],
            selectforeground=[
                ('readonly', self.custom_styles['*.FG.SEL']),
                ('!readonly', self.custom_styles['*.FG.SEL']),
            ],
        )

        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure(
            'DemoDefault.TButton',
            font=('StdFont', self.app_data.ui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_default.map(
            'DemoDefault.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', self.custom_styles['BTN.BG.ACT']),
                ('active', self.custom_styles['BTN.BG.*']),
                ('!active', self.custom_styles['BTN.BG.*']),
            ],
            foreground=[
                ('pressed', self.custom_styles['*.FG.*']),
                ('active', self.custom_styles['*.FG.*']),
                ('!active', self.custom_styles['*.FG.*']),
            ],
        )

        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure(
            'DemoDisabled.TButton',
            font=('StdFont', self.app_data.ui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_disabled.map(
            'DemoDisabled.TButton',
            relief=[
                ('active', 'raised'),
                ('!active', 'raised'),
            ],
            background=[
                ('active', self.custom_styles['BTN.BG.DISABL']),
                ('!active', self.custom_styles['BTN.BG.DISABL']),
            ],
            foreground=[
                ('active', self.custom_styles['BTN.FG.DISABL']),
                ('!active', self.custom_styles['BTN.FG.DISABL']),
            ],
        )

        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure(
            'DemoYes.TButton',
            font=('StdFont', self.app_data.ui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_yes.map(
            'DemoYes.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', self.custom_styles['BTN.BG.Y_ACT']),
                ('active', self.custom_styles['BTN.BG.Y']),
                ('!active', self.custom_styles['BTN.BG.Y']),
            ],
            foreground=[
                ('pressed', self.custom_styles['*.FG.*']),
                ('active', self.custom_styles['*.FG.*']),
                ('!active', self.custom_styles['*.FG.*']),
            ],
        )

        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure(
            'DemoNo.TButton',
            font=('StdFont', self.app_data.ui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_no.map(
            'DemoNo.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', self.custom_styles['BTN.BG.N_ACT']),
                ('active', self.custom_styles['BTN.BG.N']),
                ('!active', self.custom_styles['BTN.BG.N']),
            ],
            foreground=[
                ('pressed', self.custom_styles['*.FG.*']),
                ('active', self.custom_styles['*.FG.*']),
                ('!active', self.custom_styles['*.FG.*']),
            ],
        )

        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure(
            'DemoImage.TButton',
            font=('StdFont', self.app_data.ui_settings.scale + 2),
            borderwidth=0,
        )
        self.st_btn_image.map(
            'DemoImage.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', self.custom_styles['BTN.BG.IMG_ACT']),
                ('active', self.custom_styles['BTN.BG.IMG_HOV']),
                ('!active', self.custom_styles['*.BG.*']),
            ],
            foreground=[
                ('pressed', self.custom_styles['*.FG.*']),
                ('active', self.custom_styles['*.FG.*']),
                ('!active', self.custom_styles['*.FG.*']),
            ],
        )

        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map(
            'DemoDefault.TCheckbutton',
            background=[
                ('active', self.custom_styles['CHECK.BG.SEL']),
                ('!active', self.custom_styles['*.BG.*']),
            ],
        )

        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure(
            'DemoDefault.TFrame',
            borderwidth=1,
            relief=self.custom_styles['FRAME.RELIEF.*'],
            background=self.custom_styles['*.BG.*'],
            bordercolor=self.custom_styles['*.BORDER_CLR.*'],
        )

        self.st_frame_window = ttk.Style()
        self.st_frame_window.theme_use('alt')
        self.st_frame_window.configure(
            'Window.TFrame',
            borderwidth=1,
            relief='groove',
            background=self.custom_styles['*.BG.*'],
            bordercolor='#888888',
        )

        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map(
            'Demo.Vertical.TScrollbar',
            troughcolor=[
                ('disabled', self.custom_styles['*.BG.*']),
                ('pressed', self.custom_styles['SCROLL.BG.ACT']),
                ('!pressed', self.custom_styles['SCROLL.BG.*']),
            ],
            background=[
                ('disabled', self.custom_styles['*.BG.*']),
                ('pressed', self.custom_styles['SCROLL.FG.ACT']),
                ('!pressed', self.custom_styles['SCROLL.FG.*']),
            ],
        )

        return True

    def refresh_images(self):
        for i in range(len(ICON_NAMES)):
            img = f'{ICON_NAMES[i]}.png'
            try:
                self.images[i].config(file=self.dir_with_images / img)
            except tk.TclError:
                try:
                    self.images[i].config(file=IMAGES_DIR / img)
                except tk.TclError:
                    self.img_buttons[i].config(
                        text='-', image='', compound='text', style='DemoDefault.TButton'
                    )
                else:
                    self.img_buttons[i].config(
                        image=self.images[i], compound='image', style='DemoImage.TButton'
                    )
            else:
                self.img_buttons[i].config(
                    image=self.images[i], compound='image', style='DemoImage.TButton'
                )

    def set_focus(self):
        self.focus_set()

        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


""" Графический интерфейс - основные окна """


class TrainingW(tk.Toplevel):
    _session_number = 0

    def __init__(
            self,
            parent: tk.Misc,
            app_data: AppData,
            train_config: TrainingConfig,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active
        self.dct = self.dct_bundle.dct
        self.replacer = self.dct_bundle.replacer

        self.trainer = Trainer(self.dct_bundle.dct, train_config)
        self.trainer.initialize()
        self.initial_pool_size = len(self.trainer.pool)
        self.current_entry = None
        self.current_form = None  # Текущая форма (если начальная, то None)
        self.current_phrase = None
        self.homonyms = []
        self.count_all = 0
        self.count_correct = 0

        self.var_input = tk.StringVar()

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.pick_next_word()

        if self.current_entry:
            entry = self.current_entry
            if entry.n_notes == 0 or train_config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                                             TrainingFormat.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_notes)
            if not self.homonyms or train_config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                                            TrainingFormat.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_homonyms)
            if train_config.format not in (TrainingFormat.TRANS_TO_PHRASE,
                                           TrainingFormat.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_word_and_tr)

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Учёба')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_global_rating = create_label(
            self, f'Ваш общий рейтинг по словарю: {self.calc_stats()}',
            row=0, columnspan=2, padx=6, pady=(6, 3))
        self.lbl_count = create_label(
            self, f'Отвечено: 0/{self.initial_pool_size}',
            row=1, columnspan=2, padx=6, pady=(0, 6))

        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.scrollbar.grid(row=2, column=1, padx=(0, 6), pady=6, sticky='NSW')
        self.txt_dct = tk.Text(
            self, width=70, height=30, state='disabled',
            yscrollcommand=self.scrollbar.set,
            font=('StdFont', self.app_data.ui_settings.scale),
            bg=STYLES['*.BG.ENTRY'][1][self.app_data.ui_settings.theme],
            fg=STYLES['*.FG.*'][1][self.app_data.ui_settings.theme],
            selectbackground=STYLES['*.BG.SEL'][1][self.app_data.ui_settings.theme],
            selectforeground=STYLES['*.FG.SEL'][1][self.app_data.ui_settings.theme],
            relief=STYLES['TXT.RELIEF.*'][1][self.app_data.ui_settings.theme],
            highlightbackground=STYLES['*.BORDER_CLR.*'][1][self.app_data.ui_settings.theme])
        self.txt_dct.grid(row=2, column=0, padx=(6, 0), pady=6, sticky='NSWE')
        self.scrollbar.config(command=self.txt_dct.yview)

        self._create_main_frame()
        self.btn_stop = create_button(
            self, self.on_stop, 'Закончить', style='No.TButton',
            row=4, columnspan=2, padx=6, pady=6)

    def _create_main_frame(self):
        self.frame_main = create_frame(self, 'Invis.TFrame', row=3, columnspan=2, padx=6, pady=6)

        self.btn_input = create_button(
            self.frame_main, self.on_input, 'Ввод', width=6,
            row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input = create_entry(
            self.frame_main, self.var_input, 36, font=self.app_data,
            row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        self.btn_show_word_and_tr = create_button(
            self.frame_main, self.show_word_and_tr, 'Слово и перевод', width=15)
        self.btn_show_notes = create_button(
            self.frame_main, self.show_notes, 'Сноски', width=7)
        self.btn_show_homonyms = create_button(
            self.frame_main, self.show_homonyms, 'Омонимы', width=8)

        if self.trainer.config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                          TrainingFormat.PHRASE_TO_TRANS):
            self.btn_show_word_and_tr.grid(row=0, column=2, padx=0, pady=0, sticky='W')
        else:
            self.btn_show_notes.grid(row=0, column=2, padx=(0, 3), pady=0, sticky='W')
            self.btn_show_homonyms.grid(row=0, column=3, padx=0, pady=0, sticky='W')

    def _create_tips(self):
        self.tip_btn_show_word_and_tr = ttip.Hovertip(
            self.btn_show_word_and_tr,
            'Посмотреть само слово и его перевод\n'
            'Control-W',
            hover_delay=700)
        self.tip_btn_show_notes = ttip.Hovertip(
            self.btn_show_notes,
            'Посмотреть сноски\n'
            'Control-N',
            hover_delay=700)
        self.tip_btn_show_homonyms = ttip.Hovertip(
            self.btn_show_homonyms,
            'Посмотреть остальные слова с таким же написанием\n'
            'Control-O',
            hover_delay=700)

        if self.trainer.config.format == TrainingFormat.TRANS_TO_WORD:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите слово', hover_delay=1000)
        elif self.trainer.config.format == TrainingFormat.WORD_TO_TRANS:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        elif self.trainer.config.format == TrainingFormat.TRANS_TO_PHRASE:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите фразу', hover_delay=1000)
        elif self.trainer.config.format == TrainingFormat.PHRASE_TO_TRANS:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        else:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите артикль', hover_delay=1000)

    def print(self, msg: Any = '', end: Any = '\n'):
        self.txt_dct['state'] = 'normal'
        self.txt_dct.insert(tk.END, f'{msg}{end}')
        self.txt_dct.yview_moveto(1.0)
        self.txt_dct['state'] = 'disabled'

    def calc_stats(self):
        correct, total = self.trainer.dct.total_score
        percent = (100 * correct / total) if total else 0
        return f'{correct} / {total} = {percent:.1f}%'

    def pick_next_word(self):
        if self.trainer.is_finished():
            self.on_stop()
            return

        (self.current_entry, self.current_form, self.current_phrase,
         self.homonyms) = self.trainer.get_task()

        # Вывод слова в журнал
        if self.trainer.config.format == TrainingFormat.TRANS_TO_WORD:
            if self.trainer.config.forms and self.current_form:
                self.print(tr_and_forms_and_stats_repr(
                    self.current_entry, self.current_form,
                ))
            else:
                self.print(tr_and_stats_repr(self.current_entry))
        elif self.trainer.config.format == TrainingFormat.WORD_TO_TRANS:
            self.print(lemma_and_stats_repr(self.current_entry))
        elif self.trainer.config.format == TrainingFormat.TRANS_TO_PHRASE:
            self.print(phrase_tr_and_stats_repr(
                self.current_entry, self.current_phrase,
            ))
        elif self.trainer.config.format == TrainingFormat.PHRASE_TO_TRANS:
            self.print(phrase_and_stats_repr(
                self.current_entry, self.current_phrase,
            ))
        else:
            self.print(lemma_and_stats_repr(self.current_entry)[4:])

    def on_input(self):
        user_answer = self.replacer.replace(self.entry_input.get())
        if user_answer != '':
            self.print(user_answer)

        self.check_answer(user_answer)

        self.pick_next_word()

        if self.trainer.config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                          TrainingFormat.PHRASE_TO_TRANS):
            btn_enable(self.btn_show_word_and_tr, self.show_word_and_tr)

        entry = self.current_entry
        if entry.n_notes == 0 or self.trainer.config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                                                TrainingFormat.PHRASE_TO_TRANS):
            btn_disable(self.btn_show_notes)
        else:
            btn_enable(self.btn_show_notes, self.show_notes)

        if not self.homonyms or self.trainer.config.format in (TrainingFormat.TRANS_TO_PHRASE,
                                                               TrainingFormat.PHRASE_TO_TRANS):
            btn_disable(self.btn_show_homonyms)
        else:
            btn_enable(self.btn_show_homonyms, self.show_homonyms)

        self.entry_input.delete(0, tk.END)

        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {self.calc_stats()}'
        self.lbl_count['text'] = f'Отвечено: {self.count_correct}/{self.initial_pool_size}'

    def show_word_and_tr(self):
        entry = self.current_entry
        self.print(f'Слово: {variants_repr(entry)}\n'
                   f'Перевод: {tr_repr(entry)}')
        btn_disable(self.btn_show_word_and_tr)

    def show_notes(self):
        self.print('Сноски:')
        entry = self.current_entry
        self.print(notes_repr(entry))
        btn_disable(self.btn_show_notes)

    def show_homonyms(self):
        self.print('Омонимы:')
        for entry in self.homonyms:
            self.print(f'> {variants_repr(entry)}: {tr_repr(entry)}')
        btn_disable(self.btn_show_homonyms)

    def on_stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()
        btn_disable(self.btn_input)
        btn_disable(self.btn_show_notes)
        btn_disable(self.btn_show_homonyms)
        btn_disable(self.btn_show_word_and_tr)

        self.print(f'\nВаш результат: {self.count_correct}/{self.count_all}', end='')

    def check_answer(self, result: str):
        is_correct = self.trainer.is_answer_correct(result)
        correct_answers = self.trainer.get_correct_answers()
        correct_answers_repr = ', '.join(correct_answers)

        entry = self.current_entry
        if is_correct:
            self.dct.register_correct_answer(entry, (
                self.dct_bundle.metadata.session_number,
                self._session_number,
                self.count_all,
            ))
            self.print('Верно\n')
            if entry.is_fav:
                window = TwoOptionsDialog(
                    self, self.app_data,
                    'Верно.\n'
                    'Оставить слово в избранном?',
                    'Да', 'Нет', val_cancel=True,
                )
                ttip.Hovertip(window.btn_right, 'Alt+N', hover_delay=700)
                window.bind('<Alt-N>', lambda event: window.btn_right.invoke())
                result = window.open()
                if not result:
                    entry.is_fav = False
            self.count_all += 1
            self.count_correct += 1
        else:
            self.print(f'Неверно. Правильный ответ: "{correct_answers_repr}"\n')
            if entry.is_fav:
                if self.app_data.ui_settings.is_typo_btn_on:
                    window = TwoOptionsDialog(
                        self, self.app_data,
                        f'Неверно.\n'
                        f'Ваш ответ: {self.replacer.replace(
                            self.entry_input.get()
                        )}\n'
                        f'Правильный ответ: {correct_answers_repr}',
                        left_btn_text='Ясно', right_btn_text='Просто опечатка',
                        left_btn_style='Default', right_btn_style='Default',
                        val_left='ok', val_right='typo')
                    ttip.Hovertip(
                        window.btn_right,
                        'Не засчитывать ошибку\n'
                        'Tab',
                        hover_delay=700,
                    )
                    window.bind('<Tab>', lambda event: window.btn_right.invoke())
                    result = window.open()
                    if result != 'typo':
                        self.dct.register_incorrect_answer(entry, (
                            self.dct_bundle.metadata.session_number,
                            self._session_number,
                            self.count_all,
                        ))
                        self.count_all += 1
                else:
                    self.dct.register_incorrect_answer(entry, (
                        self.dct_bundle.metadata.session_number,
                        self._session_number,
                        self.count_all,
                    ))
                    self.count_all += 1
            else:
                window = IncorrectAnswerW(
                    self, self.app_data,
                    self.replacer.replace(self.entry_input.get()),
                    correct_answers_repr,
                    self.app_data.ui_settings.is_typo_btn_on,
                )
                result = window.open()
                if result != 'typo':
                    self.dct.register_incorrect_answer(entry, (
                        self.dct_bundle.metadata.session_number,
                        self._session_number,
                        self.count_all,
                    ))
                    self.count_all += 1
                if result == 'yes':
                    entry.is_fav = True

    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()

        bind_ctrl_a(self.entry_input)
        self.bind('<Return>', lambda event: self.btn_input.invoke())
        self.bind('<Control-n>', lambda event: self.btn_show_notes.invoke())
        self.bind('<Control-N>', lambda event: self.btn_show_notes.invoke())
        self.bind('<Control-o>', lambda event: self.btn_show_homonyms.invoke())
        self.bind('<Control-O>', lambda event: self.btn_show_homonyms.invoke())
        self.bind('<Control-w>', lambda event: self.btn_show_word_and_tr.invoke())
        self.bind('<Control-W>', lambda event: self.btn_show_word_and_tr.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        TrainingW._session_number += 1


class DictionaryW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.active_tab = 0

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Словарь "{self.dct.name}"')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tabs.grid(row=0, column=0, padx=0, pady=0)

        self.tab_browse = BrowseDctTab(self, 'Invis.TFrame', self.app_data)
        self.tabs.add(self.tab_browse, text='Просмотр словаря')

        self.tab_search = SearchTab(self, 'Invis.TFrame', self.app_data)
        self.tabs.add(self.tab_search, text='Поиск')

        self.tab_add_entry = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_add_entry, text='Добавить запись в словарь')

    def fav_selected(self, entries: list[Entry]):
        if not entries:
            return

        self.dct.add_to_fav(entries)

        self.tab_browse.refresh_all_entries()
        self.tab_search.refresh_all_entries()

    def unfav_selected(self, entries: list[Entry]):
        if not entries:
            return

        self.dct.remove_from_fav(entries)

        self.tab_browse.refresh_all_entries()
        self.tab_search.refresh_all_entries()

    def add_tag_to_selected(self, entries: list[Entry]):
        if not entries:
            return
        if not self.dct.tags:
            MessageDialog(self, self.app_data, 'Не найдено ни одной группы!').open()
            return

        sets = [set(entry.tags) for entry in entries]
        values_intersec = set.intersection(*sets)
        values = [tag for tag in self.dct.tags if tag not in values_intersec]
        if not values:
            MessageDialog(
                self, self.app_data,
                'Выделенные статьи уже состоят во всех группах!',
            ).open()
            return
        window_tags = ChoiceDialog(
            self, self.app_data,
            msg='Выберите группу, в которую хотите добавить выбранные слова:',
            values=values,
            default_value=self.dct.tags[0],
        )
        cancelled, tag = window_tags.open()
        if cancelled:
            return
        self.dct.add_tag_to_entries(tag, entries)

        if tag == self.tab_browse.var_tag.get():
            self.tab_browse.display_entries(True)
        else:
            self.tab_browse.refresh_all_entries()
        self.tab_search.refresh_all_entries()

    def remove_tag_from_selected(self, entries: list[Entry]):
        if not entries:
            return
        if not self.dct.tags:
            MessageDialog(self, self.app_data, 'Не найдено ни одной группы!').open()
            return

        values = []
        for entry in entries:
            for tag in entry.tags:
                if tag not in values:
                    values.append(tag)
        if not values:
            MessageDialog(
                self, self.app_data,
                'Выделенные статьи не состоят ни в каких группах!',
            ).open()
            return
        if (
                (self.tab_browse.var_tag.get() == ALL_TAGS) or
                (self.tabs.index(self.tabs.select()) == 1)
        ):
            default_value = values[0]
        else:
            default_value = self.tab_browse.var_tag.get()
        window_tags = ChoiceDialog(
            self, self.app_data,
            msg='Выберите группу, из которой хотите убрать выбранные слова:',
            values=values,
            default_value=default_value,
        )
        cancelled, tag = window_tags.open()
        if cancelled:
            return
        self.dct.remove_tag_from_entries(tag, entries)

        if tag == self.tab_browse.var_tag.get():
            self.tab_browse.display_entries(True)
        else:
            self.tab_browse.refresh_all_entries()
        self.tab_search.refresh_all_entries()

    def delete_selected(self, entries: list[Entry]):
        if not entries:
            return

        count_selected = len(entries)
        tmp = select_word_form(count_selected, ('статью', 'статьи', 'статей'))
        window = TwoOptionsDialog(
            self, self.app_data,
            f'Вы действительно хотите удалить {count_selected} {tmp}?',
            focused_btn='none',
        )
        result = window.open()
        if not result:
            return

        for entry in entries:
            self.dct.delete_entry(entry)

        self.tab_browse.display_entries(True)
        self.tab_search.display_entries(True)

    def edit_entry(self, entry: Entry):
        EditEntryW(self, self.app_data, entry).open()

        self.tab_search.display_entries(False)
        self.tab_browse.display_entries(False)

    def add_entry(self):
        entry = AddEntryW(self, self.app_data).open()
        if not entry:
            return
        EditEntryW(self, self.app_data, entry).open()

        self.tab_search.display_entries(False)
        self.tab_browse.display_entries(False)

    def change_tab(self):
        if self.tabs.index(self.tabs.select()) == 0:
            self.active_tab = 0
            self.tab_browse.set_focus()
        elif self.tabs.index(self.tabs.select()) == 1:
            self.active_tab = 1
            self.tab_search.set_focus()
        else:
            self.tabs.select(self.active_tab)
            self.add_entry()

    def open(self, tab: Literal['browse', 'search'] = 'browse'):
        self.focus_set()
        self.bind('<Escape>', lambda event: self.destroy())

        if tab == 'browse':
            self.active_tab = 0
            self.tab_browse.set_focus()
        elif tab == 'search':
            self.active_tab = 1
            self.tabs.select(self.tab_search)
            self.tab_search.set_focus()

        self.tabs.bind('<<NotebookTabChanged>>', lambda event: self.change_tab())

        self.grab_set()
        self.wait_window()


class SearchTab(ttk.Frame):
    def __init__(self, master: DictionaryW, style: str, app_data: AppData):
        super().__init__(master, style=style)
        self.master: DictionaryW = master

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active
        self.dct = self.dct_bundle.dct
        self.replacer = self.dct_bundle.replacer

        self.max_entries_on_page = 50
        self.current_page = 1
        self.first_entry_idx = 0
        self.n_pages = None
        self.n_entries_total = None
        self.n_entries_on_page = None

        # Параметры поиска
        config: DctUISettings = self.dct_bundle.optional['tk']
        self.to_search_only_fav = config.search_page_to_filter_fav
        self.to_search_only_full = config.search_page_to_match_whole_word
        self.to_search_wrd = config.search_page_to_search_in_words
        self.to_search_tr = config.search_page_to_search_in_translations
        self.to_search_frm = config.search_page_to_search_in_forms
        self.to_search_phr = config.search_page_to_search_in_phrases
        self.to_search_nt = config.search_page_to_search_in_notes
        self.search_tag = config.search_page_search_tag or ''

        self.var_query = tk.StringVar()
        self.var_info = tk.StringVar()
        self.var_info_selected = tk.StringVar()
        self.var_current_page = tk.StringVar(value=str(self.current_page))

        self.img_help = tk.PhotoImage()
        self.img_arrow_left = tk.PhotoImage()
        self.img_arrow_right = tk.PhotoImage()
        self.img_double_arrow_left = tk.PhotoImage()
        self.img_double_arrow_right = tk.PhotoImage()
        self.img_select_page = tk.PhotoImage()
        self.img_unselect_page = tk.PhotoImage()
        self.img_select_all = tk.PhotoImage()
        self.img_unselect_all = tk.PhotoImage()
        self.img_fav = tk.PhotoImage()
        self.img_unfav = tk.PhotoImage()
        self.img_add_tag = tk.PhotoImage()
        self.img_remove_tag = tk.PhotoImage()
        self.img_delete = tk.PhotoImage()
        self.img_settings = tk.PhotoImage()

        # Вспомогательные массивы для ScrollFrame
        self.entries = []
        self.selected_entries = []
        self.entry_frames = []
        self.entry_buttons = []

        self._add_validation()
        self._create_widgets()
        self._create_tips()

        self.display_entries(True)

    def _add_validation(self):
        def validate_and_go_to_page(value: str):
            res = validate_int_min_max(value, 1, self.n_pages)
            if res and value != '' and int(value) != self.current_page:
                self.go_to_page(int(value))
            return res

        self.vcmd_page_number = (self.register(validate_and_go_to_page), '%P')

    def _create_widgets(self):
        self._create_header_frame()
        self._create_main_frame()

    def _create_header_frame(self):
        self.frame_header = create_frame(
            self, 'Invis.TFrame',
            row=0, column=0, padx=6, pady=(6, 0), sticky='W')

        self._create_query_frame()
        self._create_bulk_selection_frame()
        self._create_info_frame()
        self.lbl_info_selected = create_label(
            self.frame_header, textvariable=self.var_info_selected,
            row=1, column=1, padx=0, pady=0, sticky='E')
        self._create_selection_actions_frame()

    def _create_query_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_query = create_frame(
            self.frame_header,
            row=0, column=0, columnspan=2, padx=0, pady=(0, 6))

        self.btn_search_settings = create_button(
            self.frame_query, self.open_search_settings, width=9,
            row=0, column=0, padx=(6, 3), pady=6)
        set_image(self.btn_search_settings, self.img_settings,
                  img_path(theme, 'edit'), 'Настройки')
        self.entry_query = create_entry(
            self.frame_query, self.var_query, 50, font=self.app_data,
            row=0, column=1, padx=(0, 1), pady=6)
        self.btn_search = create_button(
            self.frame_query, lambda: self.go_to_first_page(True),
            'Поиск', width=6,
            row=0, column=2, padx=(0, 6), pady=6)

    def _create_bulk_selection_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_bulk_selection = create_frame(
            self.frame_header,
            row=0, column=2, padx=(6, 0), pady=(0, 6), sticky='WS')

        self.btn_select_page = create_button(
            self.frame_bulk_selection, self.select_page, width=3,
            row=0, column=0)
        set_image(self.btn_select_page, self.img_select_page,
                  img_path(theme, 'select_page'), '[X]')
        self.btn_unselect_page = create_button(
            self.frame_bulk_selection, self.unselect_page, width=3,
            row=0, column=1)
        set_image(self.btn_unselect_page, self.img_unselect_page,
                  img_path(theme, 'unselect_page'), '[ ]')
        self.btn_select_all = create_button(
            self.frame_bulk_selection, self.select_all, width=3,
            row=0, column=2)
        set_image(self.btn_select_all, self.img_select_all,
                  img_path(theme, 'select_all'), '[X]')
        self.btn_unselect_all = create_button(
            self.frame_bulk_selection, self.unselect_all, width=3,
            row=0, column=3)
        set_image(self.btn_unselect_all, self.img_unselect_all,
                  img_path(theme, 'unselect_all'), '[ ]')

    def _create_info_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_info = create_frame(
            self.frame_header, 'Invis.TFrame',
            row=1, column=0, padx=(6, 0), pady=0, sticky='W')

        self.btn_show_help = create_button(
            self.frame_info, self.show_help, width=2,
            row=0, column=0, padx=0, pady=0)
        set_image(self.btn_show_help, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_info = create_label(
            self.frame_info, textvariable=self.var_info,
            row=0, column=1, padx=0, pady=0)

    def _create_selection_actions_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_selection_actions = create_frame(self.frame_header)

        self.btn_fav = create_button(
            self.frame_selection_actions,
            lambda: self.master.fav_selected(self.selected_entries),
            width=3,
            row=0, column=0)
        set_image(self.btn_fav, self.img_fav, img_path(theme, 'fav'), '*+')
        self.btn_unfav = create_button(
            self.frame_selection_actions,
            lambda: self.master.unfav_selected(self.selected_entries),
            width=3,
            row=0, column=1)
        set_image(self.btn_unfav, self.img_unfav, img_path(theme, 'unfav'), '*-')
        self.btn_add_tag = create_button(
            self.frame_selection_actions,
            lambda: self.master.add_tag_to_selected(self.selected_entries),
            width=3,
            row=0, column=2)
        set_image(self.btn_add_tag, self.img_add_tag,
                  img_path(theme, 'add_to_group'), 'G+')
        self.btn_remove_tag = create_button(
            self.frame_selection_actions,
            lambda: self.master.remove_tag_from_selected(self.selected_entries),
            width=3,
            row=0, column=3)
        set_image(self.btn_remove_tag, self.img_remove_tag,
                  img_path(theme, 'remove_from_group'), 'G-')
        self.btn_delete = create_button(
            self.frame_selection_actions,
            lambda: self.master.delete_selected(self.selected_entries),
            width=3,
            row=0, column=4)
        set_image(self.btn_delete, self.img_delete, img_path(theme, 'trashcan'), 'DEL')

    def _create_main_frame(self):
        self.frame_main = create_frame(
            self, 'Invis.TFrame',
            row=1, column=0, padx=6, pady=6)

        self.scrolled_frame = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=0, column=0, padx=0, pady=(0, 6))
        self._create_navigation_frame()

    def _create_navigation_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_navigation = create_frame(
            self.frame_main, 'Invis.TFrame',
            row=1, column=0, padx=0, pady=0)

        self.btn_first_page = create_button(
            self.frame_navigation, self.go_to_first_page, width=2,
            row=0, column=0, padx=3, pady=0)
        set_image(self.btn_first_page, self.img_double_arrow_left,
                  img_path(theme, 'double_arrow_left'), '<<')
        self.btn_prev_page = create_button(
            self.frame_navigation, self.go_to_prev_page, width=2,
            row=0, column=1, padx=3, pady=0)
        set_image(self.btn_prev_page, self.img_arrow_left,
                  img_path(theme, 'arrow_left'), '<')
        self._create_current_page_frame()
        self.btn_next_page = create_button(
            self.frame_navigation, self.go_to_next_page, width=2,
            row=0, column=3, padx=3, pady=0)
        set_image(self.btn_next_page, self.img_arrow_right,
                  img_path(theme, 'arrow_right'), '>')
        self.btn_last_page = create_button(
            self.frame_navigation, self.go_to_last_page, width=2,
            row=0, column=4, padx=3, pady=0)
        set_image(self.btn_last_page, self.img_double_arrow_right,
                  img_path(theme, 'double_arrow_right'), '>>')

    def _create_current_page_frame(self):
        self.frame_current_page = create_frame(
            self.frame_navigation, 'Invis.TFrame',
            row=0, column=2, padx=3, pady=0)

        self.lbl_current_page_1 = create_label(
            self.frame_current_page, 'Страница',
            row=0, column=0, padx=0, pady=0)
        self.entry_current_page = create_entry(
            self.frame_current_page, self.var_current_page, 3,
            font=self.app_data, justify='center',
            validate='key', validatecommand=self.vcmd_page_number,
            row=0, column=1, padx=3, pady=0)
        self.lbl_current_page_2 = create_label(
            self.frame_current_page, 'из 1',
            row=0, column=2, padx=0, pady=0)

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_show_help, 'Справка', hover_delay=450)
        self.tip_btn_search_settings = ttip.Hovertip(
            self.btn_search_settings, 'Параметры поиска', hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(
            self.btn_fav,
            'Добавить выделенные статьи в избранное\n'
            'Ctrl+F',
            hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(
            self.btn_unfav,
            'Убрать выделенные статьи из избранного\n'
            'Ctrl+Shift+F',
            hover_delay=450)
        self.tip_btn_add_tag = ttip.Hovertip(
            self.btn_add_tag,
            'Добавить выделенные статьи в группу\n'
            'Ctrl+G',
            hover_delay=450)
        self.tip_btn_remove_tag = ttip.Hovertip(
            self.btn_remove_tag,
            'Убрать выделенные статьи из группы\n'
            'Ctrl+Shift+G',
            hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(
            self.btn_delete,
            'Удалить выделенные статьи\n'
            'Alt+D / Delete',
            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(
            self.btn_select_page,
            'Выделить все статьи на текущей странице\n'
            'Ctrl+P',
            hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(
            self.btn_unselect_page,
            'Снять выделение со всех статей на текущей странице\n'
            'Ctrl+Shift+P',
            hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(
            self.btn_select_all,
            'Выделить все статьи\n'
            'Ctrl+A / Alt+A',
            hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(
            self.btn_unselect_all,
            'Снять выделение со всех статей\n'
            'Ctrl+Shift+A',
            hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(
            self.btn_first_page,
            'В начало\n'
            'Shift+Left',
            hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(
            self.btn_prev_page,
            'На предыдущую страницу\n'
            'Left',
            hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(
            self.btn_next_page,
            'На следующую страницу\n'
            'Right',
            hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(
            self.btn_last_page,
            'В конец\n'
            'Shift+Right',
            hover_delay=650)

    def open_search_settings(self):
        window = SearchSettingsW(
            self, self.app_data, self.to_search_only_fav,
            self.to_search_only_full, self.to_search_wrd, self.to_search_tr,
            self.to_search_frm, self.to_search_phr, self.to_search_nt,
            self.search_tag,
        )
        (self.to_search_only_fav, self.to_search_only_full, self.to_search_wrd,
         self.to_search_tr, self.to_search_frm, self.to_search_phr,
         self.to_search_nt, self.search_tag) = window.open()

    def display_stats(self):
        tmp_1 = select_word_form(self.n_entries_total, ('Найдена', 'Найдены', 'Найдено'))
        tmp_2 = select_word_form(self.n_entries_total, ('статья', 'статьи', 'статей'))
        info = f'{tmp_1} {self.n_entries_total} {tmp_2}'
        self.var_info.set(info)

        count_selected = len(self.selected_entries)
        if count_selected == 0:
            info_selected = ''
        else:
            tmp_1 = select_word_form(count_selected, ('Выделена', 'Выделены', 'Выделено'))
            tmp_2 = select_word_form(count_selected, ('статья', 'статьи', 'статей'))
            info_selected = f'{tmp_1} {count_selected} {tmp_2}'
        self.var_info_selected.set(info_selected)

    def display_entries(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.entry_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.entry_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Button-2>')
            fr.unbind('<Button-3>')
            fr.destroy()

        # Выбираем нужные статьи
        if self.to_search_only_fav:
            entries = [
                entry for entry in self.dct
                if entry.is_fav
            ]
        else:
            entries = list(self.dct)
        # Если нужно, оставляем только одну группу
        if self.search_tag != ALL_TAGS:
            entries = [
                entry for entry in entries
                if self.search_tag in entry.tags
            ]
        # Среди оставшихся ищем статьи, содержащие искомый текст
        results = search_entries(
            entries,
            self.replacer.replace(self.var_query.get()),
            self.to_search_wrd, self.to_search_tr, self.to_search_frm,
            self.to_search_phr, self.to_search_nt,
        )
        # Объединяем результаты в один список
        self.entries = []
        for i in range(6 if self.to_search_only_full else 9):
            self.entries += sorted(
                list(results[i]),
                key=lambda e: (e.lemma.lower(), e.lemma),
            )
        # Из выделенных статей оставляем, только удовлетворяющие поисковому запросу
        self.selected_entries = [
            entry for entry in self.selected_entries
            if entry in self.entries
        ]
        # Если выделенных статей нет, убираем связанные с ними кнопки
        if not self.selected_entries:
            self.frame_selection_actions.grid_remove()

        # Вычисляем значения некоторых количественных переменных
        self.n_entries_total = len(self.entries)
        if self.n_entries_total == 0:
            self.n_pages = 1
        else:
            self.n_pages = math.ceil(
                self.n_entries_total / self.max_entries_on_page
            )
        if self.current_page > self.n_pages:
            self.current_page = self.n_pages
            self.first_entry_idx = (self.n_pages - 1) * self.max_entries_on_page
        if self.current_page == self.n_pages:
            if (
                    (self.n_entries_total % self.max_entries_on_page == 0) and
                    (self.n_entries_total != 0)
            ):
                self.n_entries_on_page = self.max_entries_on_page
            else:
                self.n_entries_on_page = self.n_entries_total % self.max_entries_on_page
        else:
            self.n_entries_on_page = self.max_entries_on_page
        # Выводим информацию о количестве статей
        self.display_stats()
        # Выводим номер страницы
        self.var_current_page.set(str(self.current_page))
        self.entry_current_page.icursor(len(str(self.current_page)))
        self.lbl_current_page_2.configure(text=f'из {self.n_pages}')

        # Создаём новые фреймы
        self.entry_frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.n_entries_on_page)
        ]
        # Создаём новые кнопки
        self.entry_buttons = [
            create_button(
                self.entry_frames[i],
                lambda i=i: self.master.edit_entry(
                    self.entries[self.first_entry_idx + i]
                ),
                entry_repr_complete(
                    self.entries[self.first_entry_idx + i], 75, 13
                ),
                style=(
                    ('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                    if self.entries[self.first_entry_idx + i]
                       in self.selected_entries
                    else ('FlatD.TButton' if i % 2 else 'FlatL.TButton')
                ),
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.n_entries_on_page)
        ]

        for i in range(self.n_entries_on_page):
            self.entry_frames[i].bind(
                '<Enter>', lambda event, i=i: self.entry_frames[i].focus_set())
            self.entry_frames[i].bind(
                '<Leave>', lambda event: self.entry_query.focus_set())
            self.entry_buttons[i].bind(
                '<Button-2>', lambda event, i=i: self.toggle_entry_selection(i))
            self.entry_buttons[i].bind(
                '<Button-3>', lambda event, i=i: self.toggle_entry_selection(i))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def refresh_entry(self, index: int, entry: Entry):
        self.entry_buttons[index].configure(
            text=entry_repr_complete(entry, 75, 13)
        )

        self.display_stats()

    def refresh_all_entries(self):
        for i in range(self.n_entries_on_page):
            entry = self.entries[self.first_entry_idx + i]
            self.entry_buttons[i].configure(
                text=entry_repr_complete(entry, 75, 13)
            )

        self.display_stats()

    def go_to_page(self, number: int):
        self.current_page = number
        self.first_entry_idx = (self.current_page - 1) * self.max_entries_on_page
        self.display_entries(True)

    def go_to_prev_page(self):
        if self.current_page != 1:
            self.go_to_page(self.current_page - 1)

    def go_to_next_page(self):
        if self.current_page != self.n_pages:
            self.go_to_page(self.current_page + 1)

    def go_to_first_page(self, to_reset_selected_entries: bool = False):
        if self.current_page != 1 or to_reset_selected_entries:
            if to_reset_selected_entries:
                self.selected_entries = []
                self.frame_selection_actions.grid_remove()
            self.go_to_page(1)

    def go_to_last_page(self):
        if self.current_page != self.n_pages:
            self.go_to_page(self.n_pages)

    def toggle_entry_selection(self, index: int):
        entry = self.entries[self.first_entry_idx + index]
        if entry in self.selected_entries:
            self.selected_entries.remove(entry)
            self.entry_buttons[index].configure(
                style='FlatD.TButton' if index % 2 else 'FlatL.TButton'
            )
            if not self.selected_entries:
                self.frame_selection_actions.grid_remove()
        else:
            self.selected_entries.append(entry)
            self.entry_buttons[index].configure(
                style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton')
            self.frame_selection_actions.grid(
                row=1, column=2, padx=(6, 0), pady=0, sticky='W'
            )
        self.display_stats()

    def select_page(self):
        for i in range(self.n_entries_on_page):
            entry = self.entries[self.first_entry_idx + i]
            if entry not in self.selected_entries:
                self.selected_entries.append(entry)
            btn = self.entry_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_selection_actions.grid(
            row=1, column=2, padx=(6, 0), pady=0, sticky='W'
        )
        self.display_stats()

    def unselect_page(self):
        for i in range(self.n_entries_on_page):
            entry = self.entries[self.first_entry_idx + i]
            if entry in self.selected_entries:
                self.selected_entries.remove(entry)
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        if not self.selected_entries:
            self.frame_selection_actions.grid_remove()
        self.display_stats()

    def select_all(self):
        self.selected_entries = list(self.entries)
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_selection_actions.grid(
            row=1, column=2, padx=(6, 0), pady=0, sticky='W'
        )
        self.display_stats()

    def unselect_all(self):
        self.selected_entries = []
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        self.frame_selection_actions.grid_remove()
        self.display_stats()

    def set_focus(self):
        self.entry_query.focus_set()

        self.entry_current_page.bind(
            '<Enter>', lambda event: self.entry_current_page.focus_set())

        bind_ctrl_a(self.entry_query)
        bind_ctrl_a(self.entry_current_page)

        self.entry_query.bind(
            '<Return>',
            lambda event: self.go_to_first_page(True))
        self.master.bind(
            '<Right>',
            lambda event: self.go_to_next_page())
        self.master.bind(
            '<Shift-Right>',
            lambda event: self.go_to_last_page())
        self.master.bind(
            '<Left>',
            lambda event: self.go_to_prev_page())
        self.master.bind(
            '<Shift-Left>',
            lambda event: self.go_to_first_page())
        self.master.bind(
            '<Up>',
            lambda event: self.scrolled_frame.scroll_up_small())
        self.master.bind(
            '<Control-u>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.master.bind(
            '<Control-U>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.master.bind(
            '<Down>',
            lambda event: self.scrolled_frame.scroll_down_small())
        self.master.bind(
            '<Control-d>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.master.bind(
            '<Control-D>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.master.bind(
            '<Control-p>',
            lambda event: self.select_page())
        self.master.bind(
            '<Control-P>',
            lambda event: self.select_page())
        self.master.bind(
            '<Control-Shift-p>',
            lambda event: self.unselect_page())
        self.master.bind(
            '<Control-Shift-P>',
            lambda event: self.unselect_page())
        self.master.bind(
            '<Alt-a>',
            lambda event: self.select_all())
        self.master.bind(
            '<Alt-A>',
            lambda event: self.select_all())
        self.master.bind(
            '<Control-a>',
            lambda event: self.select_all())
        self.master.bind(
            '<Control-A>',
            lambda event: self.select_all())
        self.master.bind(
            '<Control-Shift-a>',
            lambda event: self.unselect_all())
        self.master.bind(
            '<Control-Shift-A>',
            lambda event: self.unselect_all())
        self.master.bind(
            '<Control-f>',
            lambda event: self.master.fav_selected(self.selected_entries))
        self.master.bind(
            '<Control-F>',
            lambda event: self.master.fav_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-f>',
            lambda event: self.master.unfav_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-F>',
            lambda event: self.master.unfav_selected(self.selected_entries))
        self.master.bind(
            '<Control-g>',
            lambda event: self.master.add_tag_to_selected(self.selected_entries))
        self.master.bind(
            '<Control-G>',
            lambda event: self.master.add_tag_to_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-g>',
            lambda event: self.master.remove_tag_from_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-G>',
            lambda event: self.master.remove_tag_from_selected(self.selected_entries))
        self.master.bind(
            '<Alt-d>',
            lambda event: self.master.delete_selected(self.selected_entries))
        self.master.bind(
            '<Alt-D>',
            lambda event: self.master.delete_selected(self.selected_entries))
        self.master.bind(
            '<Delete>',
            lambda event: self.master.delete_selected(self.selected_entries))

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы прокрутить в самый низ, нажмите Ctrl+D\n'
            '* Чтобы прокрутить в самый верх, нажмите Ctrl+U\n'
            '* Чтобы выделить статью, наведите на неё мышку и нажмите ПКМ',
            msg_justify='left',
        ).open()


class BrowseDctTab(ttk.Frame):
    def __init__(self, master: DictionaryW, style: str, app_data: AppData):
        super().__init__(master, style=style)
        self.master: DictionaryW = master

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.max_entries_on_page = 100
        self.current_page = 1
        self.first_entry_idx = 0
        self.n_pages = None
        self.n_entries_total = None
        self.n_entries_on_page = None

        self.tag_options = [ALL_TAGS] + self.dct.tags

        self.var_fav_only = tk.BooleanVar(value=False)
        self.var_briefly = tk.BooleanVar(value=False)
        self.var_info = tk.StringVar()
        self.var_info_selected = tk.StringVar()
        self.var_current_page = tk.StringVar(value=str(self.current_page))
        self.var_order = tk.StringVar(value=PRINT_VALUES_ORDER[0])
        self.var_tag = tk.StringVar(value=ALL_TAGS)

        self.img_help = tk.PhotoImage()
        self.img_arrow_left = tk.PhotoImage()
        self.img_arrow_right = tk.PhotoImage()
        self.img_double_arrow_left = tk.PhotoImage()
        self.img_double_arrow_right = tk.PhotoImage()
        self.img_export = tk.PhotoImage()
        self.img_select_page = tk.PhotoImage()
        self.img_unselect_page = tk.PhotoImage()
        self.img_select_all = tk.PhotoImage()
        self.img_unselect_all = tk.PhotoImage()
        self.img_fav = tk.PhotoImage()
        self.img_unfav = tk.PhotoImage()
        self.img_add_tag = tk.PhotoImage()
        self.img_remove_tag = tk.PhotoImage()
        self.img_delete = tk.PhotoImage()

        # Вспомогательные массивы для ScrollFrame
        self.entries = []
        self.selected_entries = []
        self.entry_frames = []
        self.entry_buttons = []
        self.entry_tips = []

        self._add_validation()
        self._create_widgets()
        self._create_tips()
        self._create_bindings()

        self.display_entries(True)

    def _add_validation(self):
        def validate_and_go_to_page(value: str):
            res = validate_int_min_max(value, 1, self.n_pages)
            if res and value != '' and int(value) != self.current_page:
                self.go_to_page(int(value))
            return res

        self.vcmd_page_number = (self.register(validate_and_go_to_page), '%P')

    def _create_widgets(self):
        self._create_menu_frame()
        self._create_main_frame()

    def _create_menu_frame(self):
        self.frame_menu = create_frame(
            self, 'Invis.TFrame',
            row=0, column=0, padx=6, pady=(6, 0), sticky='W')

        self._create_header_frame()
        self._create_selection_actions_frame()
        self._create_bulk_selection_frame()
        self.lbl_info = create_label(
            self.frame_menu,
            textvariable=self.var_info,
            row=2, column=0, padx=0, pady=0)
        self.lbl_info_selected = create_label(
            self.frame_menu, justify='left',
            textvariable=self.var_info_selected,
            row=2, column=1, padx=(6, 0), pady=0, sticky='W')

    def _create_header_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_header = create_frame(
            self.frame_menu, 'Invis.TFrame',
            row=0, rowspan=2, column=0, padx=0, pady=0)

        self.btn_show_help = create_button(
            self.frame_header, self.show_help, width=2,
            row=0, column=0, padx=0, pady=0)
        set_image(self.btn_show_help, self.img_help, img_path(theme, 'about'), '?')
        self.btn_export = create_button(
            self.frame_header, self.export,
            row=1, column=0, padx=0, pady=0)
        set_image(self.btn_export, self.img_export,
                  img_path(theme, 'print_out'), 'Распечатать')
        self._create_parameters_frame()

    def _create_parameters_frame(self):
        self.frame_parameters = create_frame(
            self.frame_header,
            row=0, rowspan=2, column=1, padx=(6, 0), pady=0)

        self.lbl_fav_only = create_label(
            self.frame_parameters, 'Только избр.:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_fav_only = create_checkbutton(
            self.frame_parameters, self.var_fav_only,
            command=lambda: self.go_to_first_page(True),
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_tag = create_label(
            self.frame_parameters, 'Группа:',
            row=0, column=2, padx=(0, 1), pady=6, sticky='E')
        self.combo_tag = create_combobox(
            self.frame_parameters, self.var_tag,
            self.tag_options, 28,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale),
            state='readonly',
            row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        self.lbl_briefly = create_label(
            self.frame_parameters, 'Кратко:',
            row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_briefly = create_checkbutton(
            self.frame_parameters, self.var_briefly,
            command=lambda: self.display_entries(True),
            row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_order = create_label(
            self.frame_parameters, 'Порядок:',
            row=1, column=2, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_order = create_combobox(
            self.frame_parameters, self.var_order, PRINT_VALUES_ORDER, 28,
            font=('DejaVu Sans Mono', self.app_data.ui_settings.scale), state='readonly',
            row=1, column=3, padx=(0, 6), pady=(0, 6), sticky='W')

    def _create_selection_actions_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_selection_actions = create_frame(self.frame_menu)

        self.btn_fav = create_button(
            self.frame_selection_actions,
            lambda: self.master.fav_selected(self.selected_entries),
            width=3,
            row=0, column=0)
        set_image(self.btn_fav, self.img_fav, img_path(theme, 'fav'), '*+')
        self.btn_unfav = create_button(
            self.frame_selection_actions,
            lambda: self.master.unfav_selected(self.selected_entries),
            width=3,
            row=0, column=1)
        set_image(self.btn_unfav, self.img_unfav, img_path(theme, 'unfav'), '*-')
        self.btn_add_tag = create_button(
            self.frame_selection_actions,
            lambda: self.master.add_tag_to_selected(self.selected_entries),
            width=3,
            row=0, column=2)
        set_image(self.btn_add_tag, self.img_add_tag,
                  img_path(theme, 'add_to_group'), 'G+')
        self.btn_remove_tag = create_button(
            self.frame_selection_actions,
            lambda: self.master.remove_tag_from_selected(self.selected_entries),
            width=3,
            row=0, column=3)
        set_image(self.btn_remove_tag, self.img_remove_tag,
                  img_path(theme, 'remove_from_group'), 'G-')
        self.btn_delete = create_button(
            self.frame_selection_actions,
            lambda: self.master.delete_selected(self.selected_entries),
            width=3,
            row=0, column=4)
        set_image(self.btn_delete, self.img_delete, img_path(theme, 'trashcan'), 'DEL')

    def _create_bulk_selection_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_bulk_selection = create_frame(
            self.frame_menu,
            row=1, column=1, padx=(6, 0), pady=0, sticky='WS')

        self.btn_select_page = create_button(
            self.frame_bulk_selection, self.select_page, width=3,
            row=0, column=0)
        set_image(self.btn_select_page, self.img_select_page,
                  img_path(theme, 'select_page'), '[X]')
        self.btn_unselect_page = create_button(
            self.frame_bulk_selection, self.unselect_page, width=3,
            row=0, column=1)
        set_image(self.btn_unselect_page, self.img_unselect_page,
                  img_path(theme, 'unselect_page'), '[ ]')
        self.btn_select_all = create_button(
            self.frame_bulk_selection, self.select_all, width=3,
            row=0, column=2)
        set_image(self.btn_select_all, self.img_select_all,
                  img_path(theme, 'select_all'), '[X]')
        self.btn_unselect_all = create_button(
            self.frame_bulk_selection, self.unselect_all, width=3,
            row=0, column=3)
        set_image(self.btn_unselect_all, self.img_unselect_all,
                  img_path(theme, 'unselect_all'), '[ ]')

    def _create_main_frame(self):
        self.frame_main = create_frame(
            self, 'Invis.TFrame',
            row=1, column=0, padx=6, pady=6)

        self.scrolled_frame = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.ui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.ui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=0, column=0, padx=0, pady=(0, 6))
        self._create_navigation_frame()

    def _create_navigation_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_navigation = create_frame(
            self.frame_main, 'Invis.TFrame',
            row=1, column=0, padx=0, pady=0)

        self.btn_first_page = create_button(
            self.frame_navigation, self.go_to_first_page, width=2,
            row=0, column=0, padx=3, pady=0)
        set_image(self.btn_first_page, self.img_double_arrow_left,
                  img_path(theme, 'double_arrow_left'), '<<')
        self.btn_prev_page = create_button(
            self.frame_navigation, self.go_to_prev_page, width=2,
            row=0, column=1, padx=3, pady=0)
        set_image(self.btn_prev_page, self.img_arrow_left,
                  img_path(theme, 'arrow_left'), '<')
        self._create_current_page_frame()
        self.btn_next_page = create_button(
            self.frame_navigation, self.go_to_next_page, width=2,
            row=0, column=3, padx=3, pady=0)
        set_image(self.btn_next_page, self.img_arrow_right,
                  img_path(theme, 'arrow_right'), '>')
        self.btn_last_page = create_button(
            self.frame_navigation, self.go_to_last_page, width=2,
            row=0, column=4, padx=3, pady=0)
        set_image(self.btn_last_page, self.img_double_arrow_right,
                  img_path(theme, 'double_arrow_right'), '>>')

    def _create_current_page_frame(self):
        self.frame_current_page = create_frame(
            self.frame_navigation, 'Invis.TFrame',
            row=0, column=2, padx=3, pady=0)

        self.lbl_current_page_1 = create_label(
            self.frame_current_page, 'Страница',
            row=0, column=0, padx=0, pady=0)
        self.entry_current_page = create_entry(
            self.frame_current_page, self.var_current_page, 3,
            font=self.app_data, justify='center',
            validate='key', validatecommand=self.vcmd_page_number,
            row=0, column=1, padx=3, pady=0)
        self.lbl_current_page_2 = create_label(
            self.frame_current_page, 'из 1',
            row=0, column=2, padx=0, pady=0)

    def _create_tips(self):
        self.tip_btn_help = ttip.Hovertip(
            self.btn_show_help, 'Справка', hover_delay=450)
        self.tip_btn_export = ttip.Hovertip(
            self.btn_export, 'Распечатать словарь в файл', hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(
            self.btn_fav,
            'Добавить выделенные статьи в избранное\n'
            'Ctrl+F',
            hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(
            self.btn_unfav,
            'Убрать выделенные статьи из избранного\n'
            'Ctrl+Shift+F',
            hover_delay=450)
        self.tip_btn_add_tag = ttip.Hovertip(
            self.btn_add_tag,
            'Добавить выделенные статьи в группу\n'
            'Ctrl+G',
            hover_delay=450)
        self.tip_btn_remove_tag = ttip.Hovertip(
            self.btn_remove_tag,
            'Убрать выделенные статьи из группы\n'
            'Ctrl+Shift+G',
            hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(
            self.btn_delete,
            'Удалить выделенные статьи\n'
            'Alt+D / Delete',
            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(
            self.btn_select_page,
            'Выделить все статьи на текущей странице\n'
            'Ctrl+P',
            hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(
            self.btn_unselect_page,
            'Снять выделение со всех статей на текущей странице\n'
            'Ctrl+Shift+P',
            hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(
            self.btn_select_all,
            'Выделить все статьи\n'
            'Ctrl+A',
            hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(
            self.btn_unselect_all,
            'Снять выделение со всех статей\n'
            'Ctrl+Shift+A',
            hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(
            self.btn_first_page,
            'В начало\n'
            'Shift+Left',
            hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(
            self.btn_prev_page,
            'На предыдущую страницу\n'
            'Left',
            hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(
            self.btn_next_page,
            'На следующую страницу\n'
            'Right',
            hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(
            self.btn_last_page,
            'В конец\n'
            'Shift+Right',
            hover_delay=650)

    def _create_bindings(self):
        self.combo_order.bind(
            '<<ComboboxSelected>>', lambda event: self.display_entries(False))
        self.combo_tag.bind(
            '<<ComboboxSelected>>', lambda event: self.go_to_first_page(True))

    def export(self):
        folder = askdirectory(initialdir=BASE_DIR, title='В какую папку сохранить файл?')
        if not folder:
            return
        filename = f'Распечатка_{self.dct.name}.txt'
        self.dct.to_txt(Path(folder) / filename)

    def display_stats(self):
        tag = self.var_tag.get()
        if tag == ALL_TAGS:
            if self.var_fav_only.get():
                w, t, gf, wf = count_filtered_entries(self.dct, to_filter_fav=True)
                info = dct_fav_stats_repr(
                    (w, self.dct.count('lemmas')),
                    (t, self.dct.count('translations')),
                    (wf, self.dct.count('word_forms')),
                )
            else:
                info = dct_stats_repr(
                    self.dct.count('lemmas'),
                    self.dct.count('translations'),
                    self.dct.count('word_forms'),
                )
        else:
            if self.var_fav_only.get():
                w1, t1, gf1, wf1 = count_filtered_entries(self.dct, tag, to_filter_fav=True)
                w2, t2, gf2, wf2 = count_filtered_entries(self.dct, tag)
                info = dct_fav_stats_repr((w1, w2), (t1, t2), (wf1, wf2))
            else:
                w, t, gf, wf = count_filtered_entries(self.dct, tag)
                info = dct_stats_repr(w, t, wf)
        self.var_info.set(info)

        count_selected = len(self.selected_entries)
        if count_selected == 0:
            info_selected = ''
        else:
            tmp_1 = select_word_form(count_selected, ('Выделена', 'Выделены', 'Выделено'))
            tmp_2 = select_word_form(count_selected, ('статья', 'статьи', 'статей'))
            info_selected = f'{tmp_1} {count_selected} {tmp_2}'
        self.var_info_selected.set(info_selected)

    def display_entries(self, move_scroll: bool):
        # Удаляем старые подсказки
        for tip in self.entry_tips:
            tip.__del__()
        # Удаляем старые кнопки
        for btn in self.entry_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.entry_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Button-2>')
            fr.unbind('<Button-3>')
            fr.destroy()

        # Выбираем нужные статьи
        tag = self.var_tag.get()
        if self.var_fav_only.get():
            if tag == ALL_TAGS:
                self.entries = [
                    entry for entry in self.dct
                    if entry.is_fav
                ]
            else:
                self.entries = [
                    entry for entry in self.dct
                    if entry.is_fav and tag in entry.tags
                ]
        else:
            if tag == ALL_TAGS:
                self.entries = list(self.dct)
            else:
                self.entries = [
                    entry for entry in self.dct
                    if tag in entry.tags
                ]
        self.selected_entries = [
            entry for entry in self.selected_entries
            if entry in self.entries
        ]
        if not self.selected_entries:
            self.frame_selection_actions.grid_remove()
        # Сортируем статьи
        if self.var_order.get() == PRINT_VALUES_ORDER[1]:
            self.entries.reverse()
        elif self.var_order.get() == PRINT_VALUES_ORDER[2]:
            self.entries.sort(key=lambda e: (
                e.accuracy,
                e.win_streak / (1 + e.n_gram_forms + e.n_phrases),
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[3]:
            self.entries.sort(key=lambda e: (
                -e.accuracy,
                -e.win_streak / (1 + e.n_gram_forms + e.n_phrases),
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[4]:
            self.entries.sort(key=lambda e: (
                e.latest_att_timestamp,
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[5]:
            self.entries.sort(key=lambda e: (
                [-val for val in e.latest_att_timestamp],
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[6]:
            self.entries.sort(key=lambda e: (
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[7]:
            self.entries.sort(
                key=lambda e: (e.lemma.lower(), e.lemma),
                reverse=True,
            )
        elif self.var_order.get() == PRINT_VALUES_ORDER[8]:
            self.entries.sort(key=lambda e: (
                len(e.lemma),
                e.lemma.lower(),
                e.lemma,
            ))
        elif self.var_order.get() == PRINT_VALUES_ORDER[9]:
            self.entries.sort(key=lambda e: (
                -len(e.lemma),
                e.lemma.lower(),
                e.lemma,
            ))
        # Выводим информацию о количестве статей
        self.display_stats()

        # Вычисляем значения некоторых количественных переменных
        self.n_entries_total = len(self.entries)
        if self.n_entries_total == 0:
            self.n_pages = 1
        else:
            self.n_pages = math.ceil(
                self.n_entries_total / self.max_entries_on_page
            )
        if self.current_page > self.n_pages:
            self.current_page = self.n_pages
            self.first_entry_idx = (self.n_pages - 1) * self.max_entries_on_page
        if self.current_page == self.n_pages:
            if (
                    (self.n_entries_total % self.max_entries_on_page == 0) and
                    (self.n_entries_total != 0)
            ):
                self.n_entries_on_page = self.max_entries_on_page
            else:
                self.n_entries_on_page = self.n_entries_total % self.max_entries_on_page
        else:
            self.n_entries_on_page = self.max_entries_on_page
        # Выводим номер страницы
        self.var_current_page.set(str(self.current_page))
        self.entry_current_page.icursor(len(str(self.current_page)))
        self.lbl_current_page_2.configure(text=f'из {self.n_pages}')

        # Создаём новые фреймы
        self.entry_frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.n_entries_on_page)
        ]
        # Создаём новые кнопки
        self.entry_buttons = [
            create_button(
                self.entry_frames[i],
                lambda i=i: self.master.edit_entry(self.entries[self.first_entry_idx + i]),
                style=(
                    ('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                    if self.entries[self.first_entry_idx + i]
                       in self.selected_entries
                    else ('FlatD.TButton' if i % 2 else 'FlatL.TButton')
                ),
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.n_entries_on_page)
        ]
        # Создаём подсказки
        self.entry_tips = [
            ttip.Hovertip(
                self.entry_buttons[i],
                f'Верных ответов подряд: {win_streak_repr(
                    self.entries[self.first_entry_idx + i]
                )}\n'
                f'Доля верных ответов: {accuracy_repr(
                    self.entries[self.first_entry_idx + i]
                )}',
                hover_delay=666,
            ) for i in range(self.n_entries_on_page)
        ]
        if self.var_briefly.get():
            for i in range(self.n_entries_on_page):
                entry = self.entries[self.first_entry_idx + i]
                self.entry_buttons[i].configure(
                    text=entry_repr_brief(entry, 75)
                )
        else:
            for i in range(self.n_entries_on_page):
                entry = self.entries[self.first_entry_idx + i]
                self.entry_buttons[i].configure(
                    text=entry_repr_details(entry, 75)
                )

        for i in range(self.n_entries_on_page):
            self.entry_frames[i].bind(
                '<Enter>', lambda event, i=i: self.entry_frames[i].focus_set())
            self.entry_buttons[i].bind(
                '<Button-2>', lambda event, i=i: self.toggle_entry_selection(i))
            self.entry_buttons[i].bind(
                '<Button-3>', lambda event, i=i: self.toggle_entry_selection(i))

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    def refresh_entry(self, index: int):
        if self.var_briefly.get():
            entry = self.entries[self.first_entry_idx + index]
            self.entry_buttons[index].configure(
                text=entry_repr_brief(entry, 75)
            )
        else:
            entry = self.entries[self.first_entry_idx + index]
            self.entry_buttons[index].configure(
                text=entry_repr_details(entry, 75)
            )

        self.display_stats()

    def refresh_all_entries(self):
        if self.var_briefly.get():
            for i in range(self.n_entries_on_page):
                entry = self.entries[self.first_entry_idx + i]
                self.entry_buttons[i].configure(
                    text=entry_repr_brief(entry, 75)
                )
        else:
            for i in range(self.n_entries_on_page):
                entry = self.entries[self.first_entry_idx + i]
                self.entry_buttons[i].configure(
                    text=entry_repr_details(entry, 75)
                )

    def go_to_page(self, number: int):
        self.current_page = number
        self.first_entry_idx = (self.current_page - 1) * self.max_entries_on_page
        self.display_entries(True)

    def go_to_prev_page(self):
        if self.current_page != 1:
            self.go_to_page(self.current_page - 1)

    def go_to_next_page(self):
        if self.current_page != self.n_pages:
            self.go_to_page(self.current_page + 1)

    def go_to_first_page(self, to_reset_selected_entries: bool = False):
        if self.current_page != 1 or to_reset_selected_entries:
            if to_reset_selected_entries:
                self.selected_entries = []
                self.frame_selection_actions.grid_remove()
            self.go_to_page(1)

    def go_to_last_page(self):
        if self.current_page != self.n_pages:
            self.go_to_page(self.n_pages)

    def toggle_entry_selection(self, index: int):
        entry = self.entries[self.first_entry_idx + index]
        if entry in self.selected_entries:
            self.selected_entries.remove(entry)
            self.entry_buttons[index].configure(
                style='FlatD.TButton' if index % 2 else 'FlatL.TButton'
            )
            if not self.selected_entries:
                self.frame_selection_actions.grid_remove()
        else:
            self.selected_entries.append(entry)
            self.entry_buttons[index].configure(
                style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton'
            )
            self.frame_selection_actions.grid(
                row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
            )
        self.display_stats()

    def select_page(self):
        for i in range(self.n_entries_on_page):
            entry = self.entries[self.first_entry_idx + i]
            if entry not in self.selected_entries:
                self.selected_entries.append(entry)
            btn = self.entry_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_selection_actions.grid(
            row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
        )
        self.display_stats()

    def unselect_page(self):
        for i in range(self.n_entries_on_page):
            entry = self.entries[self.first_entry_idx + i]
            if entry in self.selected_entries:
                self.selected_entries.remove(entry)
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        if not self.selected_entries:
            self.frame_selection_actions.grid_remove()
        self.display_stats()

    def select_all(self):
        self.selected_entries = list(self.entries)
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_selection_actions.grid(
            row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
        )
        self.display_stats()

    def unselect_all(self):
        self.selected_entries = []
        for i in range(len(self.entry_buttons)):
            btn = self.entry_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        self.frame_selection_actions.grid_remove()
        self.display_stats()

    def set_focus(self):
        self.focus_set()

        self.unbind('<Return>')

        self.entry_current_page.bind(
            '<Enter>', lambda event: self.entry_current_page.focus_set())

        bind_ctrl_a(self.entry_current_page)

        self.master.bind(
            '<Right>',
            lambda event: self.go_to_next_page())
        self.master.bind(
            '<Shift-Right>',
            lambda event: self.go_to_last_page())
        self.master.bind(
            '<Left>',
            lambda event: self.go_to_prev_page())
        self.master.bind(
            '<Shift-Left>',
            lambda event: self.go_to_first_page())
        self.master.bind(
            '<Up>',
            lambda event: self.scrolled_frame.scroll_up_small())
        self.master.bind(
            '<Control-u>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.master.bind(
            '<Control-U>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.master.bind(
            '<Down>',
            lambda event: self.scrolled_frame.scroll_down_small())
        self.master.bind(
            '<Control-d>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.master.bind(
            '<Control-D>',
            lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.master.bind(
            '<Control-p>',
            lambda event: self.select_page())
        self.master.bind(
            '<Control-P>',
            lambda event: self.select_page())
        self.master.bind(
            '<Control-Shift-p>',
            lambda event: self.unselect_page())
        self.master.bind(
            '<Control-Shift-P>',
            lambda event: self.unselect_page())
        self.master.bind(
            '<Control-a>',
            lambda event: self.select_all())
        self.master.bind(
            '<Control-A>',
            lambda event: self.select_all())
        self.master.bind(
            '<Control-Shift-a>',
            lambda event: self.unselect_all())
        self.master.bind(
            '<Control-Shift-A>',
            lambda event: self.unselect_all())
        self.master.bind(
            '<Control-f>',
            lambda event: self.master.fav_selected(self.selected_entries))
        self.master.bind(
            '<Control-F>',
            lambda event: self.master.fav_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-f>',
            lambda event: self.master.unfav_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-F>',
            lambda event: self.master.unfav_selected(self.selected_entries))
        self.master.bind(
            '<Control-g>',
            lambda event: self.master.add_tag_to_selected(self.selected_entries))
        self.master.bind(
            '<Control-G>',
            lambda event: self.master.add_tag_to_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-g>',
            lambda event: self.master.remove_tag_from_selected(self.selected_entries))
        self.master.bind(
            '<Control-Shift-G>',
            lambda event: self.master.remove_tag_from_selected(self.selected_entries))
        self.master.bind(
            '<Alt-d>',
            lambda event: self.master.delete_selected(self.selected_entries))
        self.master.bind(
            '<Alt-D>',
            lambda event: self.master.delete_selected(self.selected_entries))
        self.master.bind(
            '<Delete>',
            lambda event: self.master.delete_selected(self.selected_entries))

    def show_help(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы прокрутить в самый низ, нажмите Ctrl+D\n'
            '* Чтобы прокрутить в самый верх, нажмите Ctrl+U\n'
            '* Чтобы выделить статью, наведите на неё мышку и нажмите ПКМ',
            msg_justify='left',
        ).open()


class AddEntryW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_bundle = app_data.manager.active
        self.dct = self.dct_bundle.dct
        self.replacer = self.dct_bundle.replacer

        self.entry = None

        self.var_word = tk.StringVar()
        self.var_tr = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        self._configure_window()
        self._create_widgets()
        self._add_validation()
        self._create_bindings()

        btn_disable(self.btn_add)
        self.entry_word.icursor(len(self.var_word.get()))

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Добавление статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_word = create_label(
            self, 'Введите слово:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_word = create_entry(
            self, self.var_word, 50, font=self.app_data, validate='all',
            row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr = create_label(
            self, 'Введите перевод:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr = create_entry(
            self, self.var_tr, 50, font=self.app_data, validate='all',
            row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_fav = create_label(
            self, 'Избранное:',
            row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self._create_frame()
        self.btn_add = create_button(
            self, self.on_add_clicked, 'Добавить',
            row=3, columnspan=2, padx=6, pady=(0, 6))

    def _create_frame(self):
        self.frame = create_frame(
            self, 'Invis.TFrame',
            row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')

        self.check_fav = create_checkbutton(
            self.frame, self.var_fav,
            row=0, column=0, padx=0, pady=0)
        self.lbl_msg = create_label(
            self.frame, justify='left',
            row=0, column=1, padx=(6, 0), pady=0)

    def _add_validation(self):
        def validate_entries(value_word: str, value_tr: str):
            """
            Check the entered word and translation before saving.

            Forbids saving if a field is not filled in. Also shows messages about
            existing entries that are homonyms or synonyms of the entered ones.

            Args:
                value_word: The entered word.
                value_tr: The entered translation.

            Returns:
                True if the entry can be saved, False otherwise.
            """

            value_word = self.replacer.replace(value_word)
            value_tr = self.replacer.replace(value_tr)

            if value_word == '' or value_tr == '':
                btn_disable(self.btn_add)
            else:
                btn_enable(self.btn_add, self.on_add_clicked)

            words = {
                variant
                for entry in self.dct
                for variant in entry.variants
            }

            if value_word in words:
                entries_with_this_word = self.dct.search(variants=[value_word])
                translations = set().union(*(
                    entry.tr for entry in entries_with_this_word
                ))
                if value_tr in translations:
                    self.lbl_msg.configure(text='Такая статья уже есть в словаре')
                else:
                    self.lbl_msg.configure(text='Такое слово уже есть в словаре')
            else:
                translations = set().union(*(entry.tr for entry in self.dct))
                if value_tr in translations:
                    self.lbl_msg.configure(text='Слово с таким переводом уже есть в словаре')
                else:
                    self.lbl_msg.configure(text='')

            return True

        self.vcmd_word = (
            self.register(lambda value: validate_entries(value, self.var_tr.get())), '%P'
        )
        self.vcmd_tr = (
            self.register(lambda value: validate_entries(self.var_word.get(), value)), '%P'
        )
        self.entry_word['validatecommand'] = self.vcmd_word
        self.entry_tr['validatecommand'] = self.vcmd_tr

    def _create_bindings(self):
        self.entry_word.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_word.focus_set())

    def on_add_clicked(self):
        self.entry = add_homograph(
            self.app_data, self,
            self.replacer.replace(self.var_word.get()),
            self.replacer.replace(self.var_tr.get()),
        )
        if not self.entry:
            return
        self.entry.is_fav = self.var_fav.get()
        for tag in self.dct.default_tags:
            self.dct.add_tag_to_entries(tag, [self.entry])

        self.destroy()

    def set_focus(self):
        self.focus_set()
        self.entry_word.focus_set()

        bind_ctrl_a(self.entry_word)
        bind_ctrl_a(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_add.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self) -> Entry | None:
        self.set_focus()

        self.update()

        self.grab_set()
        self.wait_window()

        return self.entry


class SettingsW(tk.Toplevel):
    def __init__(self, parent: 'MainW', app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.manager = app_data.manager

        self.active_tab = 0  # Текущая вкладка (0 или 1)

        self.features: list[tuple[EditedCtgName, list[EditedCtgValue]]] = ...
        self.tags: list[EditedTag] = ...
        self.replacements: list[EditedReplacement] = ...
        self._set_dct_settings()
        self.scale = self.app_data.ui_settings.scale

        self.var_show_updates = tk.BooleanVar(
            value=self.app_data.ui_settings.to_check_for_updates
        )
        self.var_show_typo_button = tk.BooleanVar(
            value=self.app_data.ui_settings.is_typo_btn_on
        )
        self.var_theme = tk.StringVar(value=self.app_data.ui_settings.theme)
        self.var_themes_url = tk.StringVar(value=URL_RELEASES)

        self.img_help = tk.PhotoImage()
        self.img_plus = tk.PhotoImage()
        self.img_minus = tk.PhotoImage()

        self.dct_names = []
        self.dct_frames = []
        self.dct_buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_dct_list(True)
        self.refresh_scale_buttons()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Настройки')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_dct_name = create_label(
            self,
            split_text(f'Открыт словарь "{self.manager.active.dct.name}"',
                       30, to_add_right_spaces=False),
            justify='center',
            row=0, columnspan=2, padx=6, pady=(6, 0))
        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tabs.grid(
            row=1, columnspan=2, padx=6, pady=(0, 6))
        self._create_local_settings_frame()
        self._create_global_settings_frame()
        self.btn_save = create_button(
            self, self.save, 'Сохранить изменения', style='Yes.TButton',
            row=4, column=0, padx=(6, 3), pady=(0, 6))
        self.btn_close = create_button(
            self, self.close, 'Закрыть настройки', style='No.TButton',
            row=4, column=1, padx=(0, 6), pady=(0, 6))

    def _create_local_settings_frame(self):
        self.tab_local = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_local, text='Настройки открытого словаря')

        self.btn_forms = create_button(
            self.tab_local, self.open_features_settings, 'Грамматические категории',
            row=1, padx=6, pady=6)
        self.btn_tags = create_button(
            self.tab_local, self.open_tags_settings, 'Группы',
            row=2, padx=6, pady=6)
        self.btn_replacements = create_button(
            self.tab_local, self.open_replacements_settings, 'Специальные комбинации',
            row=3, padx=6, pady=6)
        self.lbl_save_warn = create_label(
            self.tab_local,
            'При сохранении настроек словаря, сохраняется и сам словарь!',
            'Warn.TLabel',
            row=4, padx=6, pady=6, sticky='S')

    def _create_global_settings_frame(self):
        self.tab_global = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_global, text='Настройки программы')

        self._create_updates_frame()
        self._create_typo_button_frame()
        self._create_dictionaries_frame()
        self._create_themes_frame()
        self._create_scale_frame()

    def _create_updates_frame(self):
        self.frame_show_updates = create_frame(self.tab_global, row=0, padx=6, pady=6)

        self.lbl_show_updates = create_label(
            self.frame_show_updates, 'Сообщать о выходе новых версий:',
            row=0, column=0, padx=(6, 0), pady=6)
        self.check_show_updates = create_checkbutton(
            self.frame_show_updates, self.var_show_updates,
            row=0, column=1, padx=(0, 6), pady=6)

    def _create_typo_button_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_show_typo_button = create_frame(self.tab_global, row=1, padx=6, pady=6)

        self.btn_help_typo = create_button(
            self.frame_show_typo_button, self.open_help_typo, width=2,
            row=0, column=0, padx=(6, 0), pady=6)
        set_image(self.btn_help_typo, self.img_help, img_path(theme, 'about'), '?')
        self.lbl_show_typo_button = create_label(
            self.frame_show_typo_button, 'Показывать кнопку "Опечатка":',
            row=0, column=1, padx=(3, 3), pady=6)
        self.check_show_typo_button = create_checkbutton(
            self.frame_show_typo_button, self.var_show_typo_button,
            row=0, column=2, padx=(0, 6), pady=6)

    def _create_dictionaries_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_dcts = create_frame(self.tab_global, row=2, padx=6, pady=6)

        self.lbl_dcts = create_label(
            self.frame_dcts, 'Существующие словари:',
            row=0, column=0, padx=6, pady=(6, 0))
        self.btn_help_dcts = create_button(
            self.frame_dcts, self.open_help_dcts, width=2,
            row=0, column=1, padx=6, pady=(6, 0))
        set_image(self.btn_help_dcts, self.img_help, img_path(theme, 'about'), '?')
        self.scrolled_frame_dcts = ScrollFrame(
            self.frame_dcts, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.scale - SCALE_MIN])
        self.scrolled_frame_dcts.grid(
            row=1, rowspan=2, column=0, padx=(6, 0), pady=(0, 6))
        self._create_dictionary_buttons_frame()
        self.lbl_dcts_warn = create_label(
            self.frame_dcts,
            'Изменения словарей\n'
            'сохраняются сразу!',
            style='Warn.TLabel',
            row=2, column=1, padx=6, pady=(3, 6))

    def _create_dictionary_buttons_frame(self):
        self.frame_dct_buttons = create_frame(
            self.frame_dcts, 'Invis.TFrame',
            row=1, column=1, padx=6, pady=0)

        self.btn_create_dct = create_button(
            self.frame_dct_buttons, self.create_dct, 'Новый словарь',
            row=0, column=0, padx=0, pady=(0, 3), sticky='WE')
        self.btn_import_dct = create_button(
            self.frame_dct_buttons, self.import_dct, 'Импортировать словарь',
            row=1, column=0, padx=0, pady=(3, 0), sticky='WE')

    def _create_themes_frame(self):
        self.frame_themes = create_frame(self.tab_global, row=3, padx=6, pady=6)

        self.lbl_themes = create_label(
            self.frame_themes, 'Тема:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='S')
        self.combo_themes = create_combobox(
            self.frame_themes, self.var_theme, THEMES, 15,
            font=self.app_data, state='readonly',
            row=0, column=1, padx=0, pady=6, sticky='S')
        self.lbl_themes_version = create_label(
            self.frame_themes,
            f'Требуемая версия тем: {REQUIRED_THEME_VERSION}\n'
            f'Актуальные темы можно скачать здесь:',
            justify='left',
            row=0, column=2, padx=6, pady=(6, 0), sticky='WS')
        self.btn_custom_theme_settings = create_button(
            self.frame_themes, self.open_custom_theme_settings, 'Собственная тема',
            row=1, column=0, columnspan=2, padx=0, pady=(0, 6), sticky='E')
        self.entry_themes_version = create_entry(
            self.frame_themes, self.var_themes_url, 47, font=self.app_data,
            state='readonly', justify='center',
            row=1, column=2, padx=6, pady=(0, 6), sticky='WENS')

    def _create_scale_frame(self):
        theme = self.app_data.ui_settings.theme

        self.frame_scale = create_frame(self.tab_global, row=4, padx=6, pady=6)

        self.btn_zoom_out = create_button(
            self.frame_scale, self.zoom_out,
            width=2, state='normal',
            row=0, column=0, padx=(6, 3), pady=6)
        set_image(self.btn_zoom_out, self.img_minus, img_path(theme, 'delete'), '-')
        self.lbl_scale = create_label(
            self.frame_scale, f'Масштаб ({self.scale}x)',
            row=0, column=1, padx=(3, 3), pady=6)
        self.btn_zoom_in = create_button(
            self.frame_scale, self.zoom_in,
            width=2, state='normal',
            row=0, column=2, padx=(3, 6), pady=6)
        set_image(self.btn_zoom_in, self.img_plus, img_path(theme, 'add'), '+')

    def _create_tips(self):
        self.tip_btn_help_typo = ttip.Hovertip(self.btn_help_typo, 'Справка', hover_delay=450)
        self.tip_btn_help_dcts = ttip.Hovertip(self.btn_help_dcts, 'Справка', hover_delay=450)

    def _set_dct_settings(self):
        dct = self.manager.active.dct

        self.features = [
            (EditedCtgName(name, is_new=False), [EditedCtgValue(val, is_new=False) for val in vals])
            for name, vals in dct.features.items()
        ]
        self.tags = [
            EditedTag(tag, dct.is_default_tag(tag), is_new=False)
            for tag in dct.tags
        ]
        self.replacements = [
            EditedReplacement(m, i, o, is_new=False)
            for (m, i), o in self.manager.active.replacer.replacements.items()
        ]

    def open_features_settings(self):
        self.features = CategoriesSettingsW(self, self.app_data, self.features).open()

    def open_tags_settings(self):
        self.tags = TagSettingsW(self, self.app_data, self.tags).open()

    def open_replacements_settings(self):
        self.replacements = InputReplacementsSettingsW(self, self.app_data, self.replacements).open()

    def open_help_typo(self):
        theme = self.app_data.ui_settings.theme

        ImageDialog(
            self, self.app_data,
            img_path(theme, 'about_typo'),
            'Если функция включена, то\n'
            'когда вы неверно отвечаете при учёбе,\n'
            'появляется кнопка "Просто опечатка".\n'
            'При её нажатии, ошибка не засчитывается.\n'
            'Срабатывает при нажатии на Tab.',
        ).open()

    def open_help_dcts(self):
        MessageDialog(
            self, self.app_data,
            '* Чтобы открыть словарь, наведите на него мышку и нажмите ЛКМ\n'
            '* Чтобы переименовать словарь, наведите на него мышку и нажмите Ctrl+R\n'
            '* Чтобы удалить словарь, наведите на него мышку и нажмите Ctrl+D\n'
            '* Чтобы экспортировать словарь, наведите на него мышку и нажмите Ctrl+E',
            msg_justify='left',
        ).open()

    def open_dct(self, dct_id: str):
        if dct_id == self.manager.active.id:
            return

        if self.has_local_changes:
            save_settings_if_has_changes(self, self.app_data)
        save_dct_if_has_progress(self, self.app_data)

        self.manager.close_dct(self.manager.active_idx)
        dct_bundle = self.manager.open_dct(DCT_SAVE_DIR(dct_id), optional_classes={'tk': DctUISettings})
        self.app_data.save(ui=False)

        self.refresh_dct_name()

        self._set_dct_settings()

        self.refresh()

    def rename_dct(self, old_name: str, dct_id: str):
        window_rename = InputDialog(
            self, self.app_data,
            f'Введите новое название для словаря "{old_name}"',
            default_value=old_name,
            validate_function=validate_savename,
            check_answer_function=lambda wnd, val: check_dct_name(
                wnd, self.app_data, val
            ),
            to_replace=False,
        )
        cancelled, new_name = window_rename.open()
        if cancelled or new_name == old_name:
            return

        rename_dct_on_disk(dct_id, new_name)
        if self.manager.active.id == dct_id:
            is_modified = self.manager.active.dct
            self.manager.active.dct.rename(new_name)
            if not is_modified:
                self.manager.active.dct.mark_saved()

            self.refresh_dct_name()
        print(f'Словарь "{old_name}" успешно переименован в "{new_name}"')

        self.print_dct_list(False)

    def delete_dct(self, dct_name: str, dct_id: str):
        if dct_name == self.manager.active.dct.name:
            warning(self, self.app_data, 'Вы не можете удалить словарь, когда он открыт!')
            return

        window_confirm = TwoOptionsDialog(
            self, self.app_data,
            f'Словарь "{dct_name}" будет безвозвратно удалён!\n'
            f'Хотите продолжить?',
            focused_btn='none',
        )
        result = window_confirm.open()
        if not result:
            return

        shutil.rmtree(DCT_SAVE_DIR(dct_id))

        self.print_dct_list(False)

    def create_dct(self):
        window = InputDialog(
            self, self.app_data,
            'Введите название нового словаря',
            validate_function=validate_savename,
            check_answer_function=lambda wnd, val: check_dct_name(wnd, self.app_data, val),
            to_replace=False,
        )
        cancelled, savename = window.open()
        if cancelled:
            return

        if self.has_local_changes:
            save_settings_if_has_changes(self, self.app_data)
        save_dct_if_has_progress(self, self.app_data)

        self.manager.close_dct(self.manager.active_idx)
        new_dct_bundle = self.manager.create_dct(savename, optional_classes={'tk': DctUISettings})
        self.manager.save_dct(self.manager.active_idx, DCT_SAVE_DIR(new_dct_bundle.id))
        self.app_data.save(ui=False)

        print(f'\nСловарь "{savename}" успешно создан и открыт')

        self.refresh_dct_name()

        self._set_dct_settings()

        self.refresh()

    def export_dct(self, dct_name: str, dct_id: str):
        dest_path = asksaveasfilename(
            title='Выберите файл для сохранения',
            initialfile=f'{dct_name}.dmdct',
            filetypes=[('Пакет Словаря', '*.dmdct')],
        )
        if not dest_path:
            return

        source_folder = DCT_SAVE_DIR(dct_id)
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_folder.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_folder)
                    zf.write(file_path, arcname=arcname)

    def import_dct(self):
        file_path = askopenfilename(
            title='Выберите файл сохранения',
            filetypes=[('Пакет Словаря', '*.dmdct')],
        )
        if not file_path:
            return

        with zipfile.ZipFile(file_path, 'r') as zf:
            dct_data = json.loads(zf.read(DCT_MAIN_DATA_FILENAME).decode('utf-8'))
            dct = Dictionary.from_json_dict(dct_data)
            dct._set_id()

            dest_folder = DCT_SAVE_DIR(dct.id)
            dest_folder.mkdir(parents=True, exist_ok=True)
            for filename in [
                DCT_METADATA_FILENAME, DCT_PRACTICE_CONFIG_FILENAME,
                DCT_REPLACER_FILENAME, DCT_GUI_DATA_FILENAME,
            ]:
                if filename in zf.namelist():
                    zf.extract(filename, dest_folder)
            save_json(dct.to_dict(), DCT_MAIN_DATA_PATH(dct.id))

        self.refresh()

    def open_custom_theme_settings(self):
        CustomThemeSettingsW(self, self.app_data).open()
        upload_custom_theme(False)
        if self.app_data.ui_settings.theme == CUSTOM_TH:
            self.set_theme()
        self.refresh_scale_buttons()

    def zoom_in(self):
        self.scale += 1

        self.parent.setup_styles()

        self.lbl_scale.configure(text=f'Масштаб ({self.scale}x)')
        self.scrolled_frame_dcts.resize(
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.scale - SCALE_MIN],
        )
        self.combo_themes.configure(font=('DejaVu Sans Mono', self.scale))
        self.entry_themes_version.configure(font=('StdFont', self.scale))

        self.refresh_scale_buttons()

    def zoom_out(self):
        self.scale -= 1

        self.parent.setup_styles()

        self.lbl_scale.configure(text=f'Масштаб ({self.scale}x)')
        self.scrolled_frame_dcts.resize(
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.scale - SCALE_MIN],
        )
        self.combo_themes.configure(font=('DejaVu Sans Mono', self.scale))
        self.entry_themes_version.configure(font=('StdFont', self.scale))

        self.refresh_scale_buttons()

    def save(self):
        self.app_data.ui_settings.to_check_for_updates = self.var_show_updates.get()
        self.app_data.ui_settings.is_typo_btn_on = self.var_show_typo_button.get()
        self.app_data.ui_settings.scale = self.scale

        dct: Dictionary = self.manager.active.dct
        for tag in self.tags:
            match tag.status:
                case 'no changes':
                    continue
                case 'deleted':
                    dct.delete_tag(tag.name_init)
                case 'new':
                    dct.add_tag(tag.name_cur, tag.is_default_cur)
                case 'modified':
                    if tag.name_cur != tag.name_init:
                        dct.rename_tag(tag.name_init, tag.name_cur)
                    if tag.is_default_cur != tag.is_default_init:
                        dct.mark_tag_as_default(tag.name_cur, tag.is_default_cur)
        for ctg, vals in self.features:
            match ctg.status:
                case 'deleted':
                    dct.delete_ctg(ctg.name_init)
                    continue
                case 'new':
                    dct.add_ctg(ctg.name_cur, [val.name_cur for val in vals if not val.is_deleted])
                    continue
                case 'modified':
                    dct.rename_ctg(ctg.name_init, ctg.name_cur)
            for val in vals:
                match val.status:
                    case 'no changes':
                        continue
                    case 'deleted':
                        dct.delete_ctg_value(ctg.name_cur, val.name_init)
                    case 'new':
                        dct.add_ctg_value(ctg.name_cur, val.name_cur)
                    case 'modified':
                        dct.rename_ctg_value(ctg.name_cur, val.name_init, val.name_cur)

        replacer: Replacer = self.manager.active.replacer
        for rep in self.replacements:
            match rep.status:
                case 'no changes':
                    continue
                case 'deleted':
                    replacer.delete_replacement(rep.modifier_init, rep.input_char_init)
                case 'new':
                    replacer.set_replacement(rep.modifier_cur, rep.input_char_cur, rep.output_char_cur)
                case 'modified':
                    replacer.delete_replacement(rep.modifier_init, rep.input_char_init)
                    replacer.set_replacement(rep.modifier_cur, rep.input_char_cur, rep.output_char_cur)

        self.set_theme()

        self.app_data.save(manager=False, ui=True)
        self.manager.active.partial_save(
            DCT_SAVE_DIR(self.manager.active.id),
            dct=True, metadata=True, replacer=True, optional={'tk'}
        )

        self._set_dct_settings()

        self.refresh_scale_buttons()

    def close(self):
        if self.has_changes:
            window = TwoOptionsDialog(
                self, self.app_data,
                'У вас есть несохранённые изменения?\n'
                'Всё равно закрыть?',
            )
            result = window.open()
            if not result:
                return
        self.destroy()

    def print_dct_list(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.dct_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for frame in self.dct_frames:
            frame.unbind('<Enter>')
            frame.unbind('<Control-R>')
            frame.unbind('<Control-r>')
            frame.unbind('<Control-D>')
            frame.unbind('<Control-d>')
            frame.unbind('<Control-E>')
            frame.unbind('<Control-e>')
            frame.unbind('<Leave>')
            frame.destroy()

        opened_ids = {bundle.id for bundle in self.manager.opened}

        options = [(self.manager.active.dct.name, self.manager.active.id)]
        for save_dir in sorted(SAVES_DIR.iterdir()):
            if save_dir.is_dir():
                try:
                    data = read_json(save_dir / DCT_MAIN_DATA_FILENAME)
                    dct_id = get_dct_id_from_dict(data)
                    dct_name = get_dct_name_from_dict(data)
                except Exception as e:
                    print(e)
                    continue
                if dct_id in opened_ids:
                    continue
                options.append((dct_name, dct_id))

        if not options:
            self.dct_names, ids = [], []
        else:
            self.dct_names, ids = zip(*sorted(options))

        n_dcts = len(self.dct_names)

        # Создаём новые фреймы
        self.dct_frames = [
            create_frame(
                self.scrolled_frame_dcts.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(n_dcts)
        ]
        # Создаём новые кнопки
        self.dct_buttons = [
            create_button(
                self.dct_frames[i],
                lambda i=i: self.open_dct(ids[i]),
                takefocus=False,
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(n_dcts)
        ]
        for i in range(n_dcts):
            savename = self.dct_names[i]
            dct_id = ids[i]
            if dct_id == self.manager.active.id:
                self.dct_buttons[i].configure(text=split_text(f'{savename} (ОТКРЫТ)', 35))
            else:
                self.dct_buttons[i].configure(text=split_text(f'{savename}', 35))

            self.dct_frames[i].bind('<Enter>', lambda event, i=i: self.dct_frames[i].focus_set())
            self.dct_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.dct_frames[i].bind(
                '<Control-r>', lambda event, i=i: self.rename_dct(self.dct_names[i], ids[i]))
            self.dct_frames[i].bind(
                '<Control-R>', lambda event, i=i: self.rename_dct(self.dct_names[i], ids[i]))
            self.dct_frames[i].bind(
                '<Control-d>', lambda event, i=i: self.delete_dct(self.dct_names[i], ids[i]))
            self.dct_frames[i].bind(
                '<Control-D>', lambda event, i=i: self.delete_dct(self.dct_names[i], ids[i]))
            self.dct_frames[i].bind(
                '<Control-e>', lambda event, i=i: self.export_dct(self.dct_names[i], ids[i]))
            self.dct_frames[i].bind(
                '<Control-E>', lambda event, i=i: self.export_dct(self.dct_names[i], ids[i]))

        if move_scroll:
            self.scrolled_frame_dcts.canvas.yview_moveto(0.0)

    def refresh_scale_buttons(self):
        if self.scale == SCALE_MIN:
            btn_disable(self.btn_zoom_out)
        else:
            btn_enable(self.btn_zoom_out, self.zoom_out, style='Image')

        if self.scale == SCALE_MAX:
            btn_disable(self.btn_zoom_in)
        else:
            btn_enable(self.btn_zoom_in, self.zoom_in, style='Image')

    def refresh(self):
        """Refresh UI when another dictionary is opened."""

        self.print_dct_list(False)

    def set_theme(self):
        self.app_data.ui_settings.theme = self.var_theme.get()
        theme = self.app_data.ui_settings.theme

        self.parent.setup_styles()

        set_image(self.btn_help_typo, self.img_help, img_path(theme, 'about'), '?')
        set_image(self.btn_help_dcts, self.img_help, img_path(theme, 'about'), '?')
        set_image(self.btn_zoom_in, self.img_plus, img_path(theme, 'add'), '+')
        set_image(self.btn_zoom_out, self.img_minus, img_path(theme, 'delete'), '-')

        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        self.scrolled_frame_dcts.canvas.configure(
            bg=STYLES['*.BG.ENTRY'][1][self.app_data.ui_settings.theme]
        )

        self.parent.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])

    @property
    def has_local_changes(self):
        return (
            any(
                c.status != 'no changes' or
                any(v.status != 'no changes' for v in vals)
                for c, vals in self.features
            ) or
            any(t.status != 'no changes' for t in self.tags) or
            any(e.status != 'no changes' for e in self.replacements)
        )

    @property
    def has_changes(self):
        return (
            self.has_local_changes or
            self.var_show_updates.get() != self.app_data.ui_settings.to_check_for_updates or
            self.var_show_typo_button.get() != self.app_data.ui_settings.is_typo_btn_on or
            self.var_theme.get() != self.app_data.ui_settings.theme or
            self.scale != self.app_data.ui_settings.scale
        )

    def refresh_dct_name(self):
        self.lbl_dct_name.config(text=split_text(
            f'Открыт словарь "{self.manager.active.dct.name}"', 30, to_add_right_spaces=False
        ))
        self.parent.refresh_dct_name()

    def on_tab_changed(self):
        if self.active_tab == 0:
            self.frame_show_updates.grid(    row=0, padx=0, pady=0)
            self.frame_show_typo_button.grid(row=0, padx=0, pady=0)
            self.frame_dcts.grid(            row=0, padx=0, pady=0)
            self.frame_themes.grid(          row=0, padx=0, pady=0)

            self.frame_dcts.grid_remove()
            self.frame_themes.grid_remove()

            self.active_tab = 1
        else:
            self.frame_show_updates.grid(    row=0, padx=6, pady=6)
            self.frame_show_typo_button.grid(row=1, padx=6, pady=6)
            self.frame_dcts.grid(            row=2, padx=6, pady=6)
            self.frame_themes.grid(          row=3, padx=6, pady=6)

            self.active_tab = 0

    def set_focus(self):
        self.focus_set()

        self.bind('<Escape>', lambda event: self.btn_close.invoke())
        self.tabs.bind('<<NotebookTabChanged>>', lambda event: self.on_tab_changed())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


class NewVersionAvailableW(tk.Toplevel):
    def __init__(self, parent: tk.Misc, app_data: AppData, last_version: str):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.var_url = tk.StringVar(value=URL_GITHUB)

        self._configure_window()
        self._create_widgets(last_version)

    def _configure_window(self):
        self.title('Доступна новая версия')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, last_version: str):
        self.lbl_msg = create_label(
            self,
            f'Доступна новая версия программы:\n'
            f'{last_version}',
            justify='center',
            row=1, columnspan=2, padx=6, pady=(4, 0))
        self._create_url_frame()
        self.btn_update = create_button(
            self, self.download_and_install, 'Обновить', style='Yes.TButton',
            row=3, column=0, padx=6, pady=4)
        self.btn_close = create_button(
            self, self.destroy, 'Закрыть', style='No.TButton',
            row=3, column=1, padx=6, pady=4)

    def _create_url_frame(self):
        self.frame_url = create_frame(
            self, 'Invis.TFrame',
            row=2, columnspan=2, padx=6, pady=(0, 4))

        self.entry_url = create_entry(
            self.frame_url, self.var_url, 39, font=self.app_data,
            state='readonly', justify='center',
            row=0, column=0, padx=(0, 3), pady=0)
        self.btn_open = create_button(
            self.frame_url, self.open_github, 'Открыть ссылку',
            row=0, column=1, padx=0, pady=0)

    def open_github(self):
        try:
            webbrowser.open(URL_GITHUB)
        except Exception as exc:
            print(f'Не удалось открыть страницу!\n'
                  f'{exc}')
            warning(
                self, self.app_data,
                f'Не удалось открыть страницу!\n'
                f'{exc}',
            )

    def download_and_install(self):
        save_dct_if_has_progress(self, self.app_data)

        # Загрузка
        try:
            print('Загрузка архива...', end='')
            wget.download(URL_DOWNLOAD_ZIP, out=BASE_DIR)
        except Exception as exc:
            print(f'\nНе удалось загрузить обновление!\n'
                  f'{exc}')
            warning(
                self, self.app_data,
                f'Не удалось загрузить обновление!\n'
                f'{exc}',
            )
            self.destroy()
            return
        # Установка
        try:
            print('\nРаспаковка архива...')
            with zipfile.ZipFile(NEW_VERSION_ZIP_PATH, 'r') as zip_file:
                zip_file.extractall(BASE_DIR)

            print('Удаление архива...')
            NEW_VERSION_ZIP_PATH.unlink()

            files_to_update = [
                fn.strip() for fn in open(Path(NEW_VERSION_DIRNAME) / UPDATE_FILES_FILENAME, 'r').readlines()
            ]

            print('Удаление старых файлов...')
            for filename in IMAGES_DIR.iterdir():
                try:
                    (IMAGES_DIR / filename).unlink()
                except FileNotFoundError:
                    print(f'Не удалось удалить файл "{filename}", т. к. он отсутствует')
            for filename in ('resources/icon.png', 'backend.py', 'constants.py', 'gui.py'):
                try:
                    (BASE_DIR / filename).unlink()
                except FileNotFoundError:
                    print(f'Не удалось удалить файл "{filename}", т. к. он отсутствует')

            print('Установка новых файлов...')
            for filename in files_to_update:
                (NEW_VERSION_DIR / filename).replace(BASE_DIR / filename)

            print('Удаление временной папки...')
            shutil.rmtree(NEW_VERSION_DIR)
        except Exception as exc:
            print(f'Не удалось установить обновление!\n'
                  f'{exc}')
            warning(
                self, self.app_data,
                f'Не удалось установить обновление!\n'
                f'{exc}',
            )
            self.destroy()
            return
        else:
            print('Обновление успешно установлено!')
            MessageDialog(
                self, self.app_data,
                'Обновление успешно установлено!\n'
                'Программа закроется',
            ).open()
            exit(EXIT_UPDATE)


class MainW(tk.Tk):
    """The main window."""

    def __init__(self, app_data: AppData):
        super().__init__()

        self.app_data = app_data
        self.manager = app_data.manager

        self._configure_window()
        self.setup_styles()
        self._create_widgets()
        self.set_focus()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.ui_settings.theme])

    def _create_widgets(self):
        self._create_head_frame()
        self._create_label_frame()
        self._create_buttons_frame()

        self.lbl_footer = create_label(
            self,
            f'{PROGRAM_VERSION}\n'
            f'{PROGRAM_DATE}  {PROGRAM_TIME}',
            'Footer.TLabel',
            justify='center',
            row=3, padx=6, pady=3)

    def _create_head_frame(self):
        self.frame_head = create_frame(self, 'Invis.TFrame', row=0, padx=16, pady=16)

        self.lbl_header = create_label(
            self.frame_head, 'Anenokil development presents', 'Header.TLabel',
            row=0, padx=0, pady=0)
        self.lbl_logo = create_label(
            self.frame_head, PROGRAM_NAME, 'Logo.TLabel',
            row=1, padx=0, pady=0)

    def _create_label_frame(self):
        self.frame_dct_name = create_frame(self, row=1, padx=6, pady=(0, 12))

        self.lbl_dct_name = create_label(
            self.frame_dct_name, '',
            justify='center',
            padx=1, pady=1)

        self.refresh_dct_name()

    def _create_buttons_frame(self):
        self.frame_buttons = create_frame(self, 'Invis.TFrame', row=2, padx=6, pady=(0, 6))

        self.btn_practice = create_button(
            self.frame_buttons, self.open_trainer, 'Учить слова',
            row=0, padx=0, pady=(0, 3))
        self.btn_browse_dct = create_button(
            self.frame_buttons, self.open_entry_list, 'Просмотреть словарь',
            row=1, padx=0, pady=(3, 3))
        self.btn_search = create_button(
            self.frame_buttons, self.open_search, 'Поиск',
            row=2, padx=0, pady=(3, 3))
        self.btn_add_entry = create_button(
            self.frame_buttons, self.open_add_entry_dialog, 'Добавить запись в словарь',
            row=3, padx=0, pady=(3, 3))
        self.btn_settings = create_button(
            self.frame_buttons, self.open_settings, 'Настройки',
            row=4, padx=0, pady=(3, 3))
        self.btn_check_updates = create_button(
            self.frame_buttons, self.check_updates, 'Проверить обновления',
            row=5, padx=0, pady=(3, 3))
        self.btn_save = create_button(
            self.frame_buttons, self.save, 'Сохранить словарь', style='Yes.TButton',
            row=6, padx=0, pady=(3, 3))
        self.btn_close = create_button(
            self.frame_buttons, self.close, 'Закрыть программу', style='No.TButton',
            row=7, padx=0, pady=(3, 0))

    def refresh_dct_name(self):
        self.lbl_dct_name.config(text=(
            f'Открыт словарь\n'
            f'"{split_text(self.manager.active.dct.name, 20, to_add_right_spaces=False)}"'
        ))

    def open_trainer(self):
        self.disable_all_buttons()

        cancelled = TrainSettingsW(self, self.app_data).open()
        if not cancelled:
            train_config = self.manager.active.train_config
            TrainingW(self, self.app_data, train_config).open()

        self.enable_all_buttons()

    def open_entry_list(self):
        self.disable_all_buttons()
        DictionaryW(self, self.app_data).open()
        self.enable_all_buttons()

    def open_search(self):
        self.disable_all_buttons()
        DictionaryW(self, self.app_data).open(tab='search')
        self.enable_all_buttons()

    def open_add_entry_dialog(self):
        self.disable_all_buttons()

        entry = AddEntryW(self, self.app_data).open()
        if entry is not None:
            EditEntryW(self, self.app_data, entry).open()

        self.enable_all_buttons()

    def open_settings(self):
        self.disable_all_buttons()
        SettingsW(self, self.app_data).open()
        self.enable_all_buttons()

        self.setup_styles()

    def check_updates(self):
        print('\nChecking for updates...')
        check_updates(self, self.app_data, True)

    def save(self):
        self.manager.save_dct(self.manager.active_idx, DCT_SAVE_DIR(self.manager.active.id))
        MessageDialog(self, self.app_data, 'Прогресс успешно сохранён').open()
        print('\nПрогресс успешно сохранён')

    def close(self):
        save_dct_if_has_progress(self, self.app_data)
        self.app_data.save()
        self.quit()

    def disable_all_buttons(self):
        for widget in self.frame_buttons.children.values():
            if isinstance(widget, ttk.Button):
                btn_disable(widget)

    def enable_all_buttons(self):
        btn_enable(self.btn_practice, self.open_trainer)
        btn_enable(self.btn_browse_dct, self.open_entry_list)
        btn_enable(self.btn_search, self.open_search)
        btn_enable(self.btn_add_entry, self.open_add_entry_dialog)
        btn_enable(self.btn_settings, self.open_settings)
        btn_enable(self.btn_check_updates, self.check_updates)
        btn_enable(self.btn_save, self.save, 'Yes')
        btn_enable(self.btn_close, self.close, 'No')

    def setup_styles(self):
        scale = self.app_data.ui_settings.scale
        theme = self.app_data.ui_settings.theme

        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure(
            'Default.TLabel',
            font=('StdFont', scale),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.*'][1][theme],
        )

        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure(
            'Header.TLabel',
            font=('StdFont', scale + 5),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.*'][1][theme],
        )

        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure(
            'Logo.TLabel',
            font=('Times', scale + 11),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.LOGO'][1][theme],
        )

        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure(
            'Footer.TLabel',
            font=('StdFont', scale - 2),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.FOOTER'][1][theme],
        )

        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure(
            'Warn.TLabel',
            font=('StdFont', scale),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.WARN'][1][theme],
        )

        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure(
            'FlatL.TLabel',
            font=('DejaVu Sans Mono', scale + 1),
            background=STYLES['FLAT_BTN.BG.1'][1][theme],
            foreground=STYLES['FLAT_BTN.FG.1'][1][theme],
        )

        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure(
            'FlatD.TLabel',
            font=('DejaVu Sans Mono', scale + 1),
            background=STYLES['FLAT_BTN.BG.2'][1][theme],
            foreground=STYLES['FLAT_BTN.FG.2'][1][theme],
        )

        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure(
            'Default.TEntry',
            font=('StdFont', scale),
        )
        self.st_entry.map(
            'Default.TEntry',
            fieldbackground=[
                ('readonly', STYLES['*.BG.*'][1][theme]),
                ('!readonly', STYLES['*.BG.ENTRY'][1][theme]),
            ],
            foreground=[
                ('readonly', STYLES['*.FG.*'][1][theme]),
                ('!readonly', STYLES['*.FG.ENTRY'][1][theme]),
            ],
            selectbackground=[
                ('readonly', STYLES['*.BG.SEL'][1][theme]),
                ('!readonly', STYLES['*.BG.SEL'][1][theme]),
            ],
            selectforeground=[
                ('readonly', STYLES['*.FG.SEL'][1][theme]),
                ('!readonly', STYLES['*.FG.SEL'][1][theme]),
            ],
        )

        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure(
            'Default.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_default.map(
            'Default.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', STYLES['BTN.BG.ACT'][1][theme]),
                ('active', STYLES['BTN.BG.*'][1][theme]),
                ('!active', STYLES['BTN.BG.*'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['*.FG.*'][1][theme]),
                ('active', STYLES['*.FG.*'][1][theme]),
                ('!active', STYLES['*.FG.*'][1][theme]),
            ],
        )

        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure(
            'Disabled.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_disabled.map(
            'Disabled.TButton',
            relief=[
                ('active', 'raised'),
                ('!active', 'raised'),
            ],
            background=[
                ('active', STYLES['BTN.BG.DISABL'][1][theme]),
                ('!active', STYLES['BTN.BG.DISABL'][1][theme]),
            ],
            foreground=[
                ('active', STYLES['BTN.FG.DISABL'][1][theme]),
                ('!active', STYLES['BTN.FG.DISABL'][1][theme]),
            ],
        )

        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure(
            'Yes.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_yes.map(
            'Yes.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', STYLES['BTN.BG.Y_ACT'][1][theme]),
                ('active', STYLES['BTN.BG.Y'][1][theme]),
                ('!active', STYLES['BTN.BG.Y'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['*.FG.*'][1][theme]),
                ('active', STYLES['*.FG.*'][1][theme]),
                ('!active', STYLES['*.FG.*'][1][theme]),
            ],
        )

        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure(
            'No.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_no.map(
            'No.TButton',
            relief=[
                ('pressed', 'sunken'),
                ('active', 'flat'),
                ('!active', 'raised'),
            ],
            background=[
                ('pressed', STYLES['BTN.BG.N_ACT'][1][theme]),
                ('active', STYLES['BTN.BG.N'][1][theme]),
                ('!active', STYLES['BTN.BG.N'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['*.FG.*'][1][theme]),
                ('active', STYLES['*.FG.*'][1][theme]),
                ('!active', STYLES['*.FG.*'][1][theme]),
            ],
        )

        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure(
            'Image.TButton',
            font=('StdFont', scale + 2),
            borderwidth=0,
        )
        self.st_btn_image.map(
            'Image.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', STYLES['BTN.BG.IMG_ACT'][1][theme]),
                ('active', STYLES['BTN.BG.IMG_HOV'][1][theme]),
                ('!active', STYLES['*.BG.*'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['*.FG.*'][1][theme]),
                ('active', STYLES['*.FG.*'][1][theme]),
                ('!active', STYLES['*.FG.*'][1][theme]),
            ],
        )

        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure(
            'FlatL.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note.map(
            'FlatL.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', STYLES['FLAT_BTN.BG.ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.BG.HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.BG.1'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['FLAT_BTN.FG.ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.FG.HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.FG.1'][1][theme]),
            ],
        )

        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure(
            'FlatD.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note.map(
            'FlatD.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', STYLES['FLAT_BTN.BG.ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.BG.HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.BG.2'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['FLAT_BTN.FG.ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.FG.HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.FG.2'][1][theme]),
            ],
        )

        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure(
            'FlatSelectedL.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note_selected.map(
            'FlatSelectedL.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', STYLES['FLAT_BTN.BG.SEL_ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.BG.SEL_HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.BG.SEL_1'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['FLAT_BTN.FG.SEL_ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.FG.SEL_HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.FG.SEL_1'][1][theme]),
            ],
        )

        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure(
            'FlatSelectedD.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note_selected.map(
            'FlatSelectedD.TButton',
            relief=[
                ('pressed', 'flat'),
                ('active', 'flat'),
                ('!active', 'flat'),
            ],
            background=[
                ('pressed', STYLES['FLAT_BTN.BG.SEL_ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.BG.SEL_HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.BG.SEL_2'][1][theme]),
            ],
            foreground=[
                ('pressed', STYLES['FLAT_BTN.FG.SEL_ACT'][1][theme]),
                ('active', STYLES['FLAT_BTN.FG.SEL_HOV'][1][theme]),
                ('!active', STYLES['FLAT_BTN.FG.SEL_2'][1][theme]),
            ],
        )

        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map(
            'Default.TCheckbutton',
            background=[
                ('active', STYLES['CHECK.BG.SEL'][1][theme]),
                ('!active', STYLES['*.BG.*'][1][theme]),
            ],
        )

        self.st_combo = ttk.Style()
        self.st_combo.theme_use('alt')
        self.st_combo.configure(
            'Default.TCombobox',
            font=('DejaVu Sans Mono', scale),
        )
        self.st_combo.map(
            'Default.TCombobox',
            background=[
                ('readonly', STYLES['BTN.BG.*'][1][theme]),
                ('!readonly', STYLES['BTN.BG.*'][1][theme]),
            ],
            fieldbackground=[
                ('readonly', STYLES['*.BG.ENTRY'][1][theme]),
                ('!readonly', STYLES['*.BG.ENTRY'][1][theme]),
            ],
            selectbackground=[
                ('readonly', STYLES['*.BG.ENTRY'][1][theme]),
                ('!readonly', STYLES['*.BG.ENTRY'][1][theme]),
            ],
            highlightbackground=[
                ('readonly', STYLES['*.BORDER_CLR.*'][1][theme]),
                ('!readonly', STYLES['*.BORDER_CLR.*'][1][theme]),
            ],
            foreground=[
                ('readonly', STYLES['*.FG.*'][1][theme]),
                ('!readonly', STYLES['*.FG.*'][1][theme]),
            ],
            selectforeground=[
                ('readonly', STYLES['*.FG.*'][1][theme]),
                ('!readonly', STYLES['*.FG.*'][1][theme]),
            ],
        )

        # Стиль всплывающего списка combobox
        for pattern, value in [
            ('*TCombobox*Listbox*Font', ('DejaVu Sans Mono', scale)),
            ('*TCombobox*Listbox*Background', STYLES['*.BG.ENTRY'][1][theme]),
            ('*TCombobox*Listbox*Foreground', STYLES['*.FG.*'][1][theme]),
            ('*TCombobox*Listbox*selectBackground', STYLES['*.BG.SEL'][1][theme]),
            ('*TCombobox*Listbox*selectForeground', STYLES['*.FG.SEL'][1][theme]),
        ]:
            self.option_add(pattern, value)

        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map(
            'Vertical.TScrollbar',
            troughcolor=[
                ('disabled', STYLES['*.BG.*'][1][theme]),
                ('pressed', STYLES['SCROLL.BG.ACT'][1][theme]),
                ('!pressed', STYLES['SCROLL.BG.*'][1][theme]),
            ],
            background=[
                ('disabled', STYLES['*.BG.*'][1][theme]),
                ('pressed', STYLES['SCROLL.FG.ACT'][1][theme]),
                ('!pressed', STYLES['SCROLL.FG.*'][1][theme]),
            ],
        )

        self.st_note = ttk.Style()
        self.st_note.theme_use('alt')
        self.st_note.configure(
            'Default.TNotebook',
            font=('StdFont', scale),
        )
        self.st_note.map(
            'Default.TNotebook',
            troughcolor=[
                ('active', STYLES['*.BG.*'][1][theme]),
                ('!active', STYLES['*.BG.*'][1][theme]),
            ],
            background=[
                ('selected', STYLES['BTN.BG.ACT'][1][theme]),
                ('!selected', STYLES['*.BG.*'][1][theme]),
            ],
        )

        self.st_note.configure(
            'TNotebook.Tab',
            font=('StdFont', scale),
        )
        self.st_note.map(
            'TNotebook.Tab',
            background=[
                ('selected', STYLES['TAB.BG.SEL'][1][theme]),
                ('!selected', STYLES['TAB.BG.*'][1][theme]),
            ],
            foreground=[
                ('selected', STYLES['TAB.FG.SEL'][1][theme]),
                ('!selected', STYLES['TAB.FG.*'][1][theme]),
            ],
        )

        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure(
            'Default.TFrame',
            borderwidth=1,
            relief=STYLES['FRAME.RELIEF.*'][1][theme],
            background=STYLES['*.BG.*'][1][theme],
            bordercolor=STYLES['*.BORDER_CLR.*'][1][theme],
        )

        self.st_frame_invis = ttk.Style()
        self.st_frame_invis.theme_use('alt')
        self.st_frame_invis.configure(
            'Invis.TFrame',
            borderwidth=0,
            relief=STYLES['FRAME.RELIEF.*'][1][theme],
            background=STYLES['*.BG.*'][1][theme],
        )

    def set_focus(self):
        self.focus_set()


""" Выполнение программы """


def main():
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    CUSTOM_THEME_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for i in (1, 2):
        theme_path = THEMES_DIR / THEMES[i]
        theme_path.mkdir(parents=True, exist_ok=True)

    CONSOLE_LOGO_FRAME_WIDTH = 85
    CONSOLE_LOGO_1_LINE = 'Anenokil development presents'
    CONSOLE_LOGO_2_LINE = PROGRAM_NAME + ' ' * (1 + (len(PROGRAM_NAME) + len(PROGRAM_VERSION)) % 2) + PROGRAM_VERSION
    CONSOLE_LOGO_3_LINE = PROGRAM_DATE + ' ' * (1 + (len(PROGRAM_DATE) + len(PROGRAM_TIME)) % 2) + PROGRAM_TIME
    CONSOLE_LOGO_1_LINE_TAB = (CONSOLE_LOGO_FRAME_WIDTH - len(CONSOLE_LOGO_1_LINE)) // 2
    CONSOLE_LOGO_2_LINE_TAB = (CONSOLE_LOGO_FRAME_WIDTH - len(CONSOLE_LOGO_2_LINE)) // 2
    CONSOLE_LOGO_3_LINE_TAB = (CONSOLE_LOGO_FRAME_WIDTH - len(CONSOLE_LOGO_3_LINE)) // 2
    print('=' * CONSOLE_LOGO_FRAME_WIDTH)
    print()
    print(' ' * CONSOLE_LOGO_1_LINE_TAB + CONSOLE_LOGO_1_LINE)
    print(' ' * CONSOLE_LOGO_2_LINE_TAB + CONSOLE_LOGO_2_LINE)
    print(' ' * CONSOLE_LOGO_3_LINE_TAB + CONSOLE_LOGO_3_LINE)
    print()
    print('=' * CONSOLE_LOGO_FRAME_WIDTH)

    print('\nПрограмма запускается...')

    print('\nЗагрузка тем...')
    upload_themes(THEMES)
    upload_custom_theme()

    app_data = AppData()

    if app_data.manager.n_opened == 0:
        app_data.manager.create_dct('New Dictionary', optional_classes={'tk': DctUISettings})

    root = MainW(app_data)
    if Path(ICON_PATH).exists():
        root.iconphoto(True, tk.PhotoImage(file=ICON_PATH))

    print('\nЗапуск программы прошёл успешно')
    root.mainloop()

    print('\nПрограмма успешно завершилась')


if __name__ == '__main__':
    main()
