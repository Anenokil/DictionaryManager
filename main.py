import copy
import os
import platform
import shutil
import random
import math
import tkinter as tk
from tkinter import colorchooser
import tkinter.ttk as ttk
import idlelib.tooltip as ttip  # Всплывающие подсказки
from tkinter.filedialog import askdirectory
import re  # Несколько разделителей в split
import webbrowser  # Для открытия веб-страницы
import urllib.request as urllib2  # Для проверки наличия обновлений
import wget  # Для загрузки обновления
import zipfile  # Для распаковки обновления
import typing  # Аннотации

""" Информация о программе """

PROGRAM_NAME = 'Dictionary Manager'
PROGRAM_VERSION = 'v7.0.18-0'
PROGRAM_DATE = '21.2.2023'
PROGRAM_TIME = '3:48 (UTC+3)'

SAVES_VERSION = 2  # Актуальная версия сохранений словарей
LOCAL_SETTINGS_VERSION = 3  # Актуальная версия локальных настроек
GLOBAL_SETTINGS_VERSION = 2  # Актуальная версия глобальных настроек
REQUIRED_THEME_VERSION = 5  # Актуальная версия тем

""" Шрифты """

FONTSIZE_MIN = 8
FONTSIZE_MAX = 16
FONTSIZE_DEF = 10

""" Темы """

CUSTOM_TH = '</custom\\>'  # Название пользовательской темы
THEMES = [CUSTOM_TH, 'light', 'dark']  # Названия тем
DEFAULT_TH = THEMES[1]  # Тема по умолчанию

# Стили для каждой темы
ST_BG             = {THEMES[1]: '#EAEAEA', THEMES[2]: '#222222'}  # Цвет фона окна
ST_BG_FIELDS      = {THEMES[1]: '#FFFFFF', THEMES[2]: '#171717'}  # Цвет фона полей ввода

ST_FG             = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет обычного текста
ST_FG_LOGO        = {THEMES[1]: '#FF8800', THEMES[2]: '#AA4600'}  # Цвет текста логотипа
ST_FG_FOOTER      = {THEMES[1]: '#666666', THEMES[2]: '#666666'}  # Цвет текста нижнего колонтитула
ST_FG_WARN        = {THEMES[1]: '#DD2222', THEMES[2]: '#DD2222'}  # Цвет текста предупреждения
ST_FG_ENTRY       = {THEMES[1]: '#222222', THEMES[2]: '#777777'}  # Цвет вводимого текста

ST_SELECT_BG      = {THEMES[1]: '#BBBBBB', THEMES[2]: '#444444'}  # Цвет выделения фона (selectbackground)
ST_SELECT_FG      = {THEMES[1]: '#101010', THEMES[2]: '#A0A0A0'}  # Цвет выделения текста (selectforeground)

ST_RELIEF_FRAME   = {THEMES[1]: 'groove',  THEMES[2]: 'solid'  }  # Стиль рамок фреймов
ST_RELIEF_TEXT    = {THEMES[1]: 'sunken',  THEMES[2]: 'solid'  }  # Стиль рамок текстовых полей
ST_BORDERCOLOR    = {THEMES[1]: '#222222', THEMES[2]: '#111111'}  # Цвет рамок (highlightbackground; работает для solid)

ST_BTN_BG         = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1C1C1C'}  # Цвет фона обычных кнопок
ST_BTN_BG_SEL     = {THEMES[1]: '#BABABA', THEMES[2]: '#191919'}  # Цвет фона обычных кнопок при нажатии
ST_BTN_Y_BG       = {THEMES[1]: '#88DD88', THEMES[2]: '#446F44'}  # Цвет фона да-кнопок
ST_BTN_Y_BG_SEL   = {THEMES[1]: '#77CC77', THEMES[2]: '#558055'}  # Цвет фона да-кнопок при нажатии
ST_BTN_N_BG       = {THEMES[1]: '#FF6666', THEMES[2]: '#803333'}  # Цвет фона нет-кнопок
ST_BTN_N_BG_SEL   = {THEMES[1]: '#EE5555', THEMES[2]: '#904444'}  # Цвет фона нет-кнопок при нажатии

ST_BTN_IMG_BG_HOV = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1D1D1D'}  # Цвет фона кнопок-картинок при наведении
ST_BTN_IMG_BG_SEL = {THEMES[1]: '#BABABA', THEMES[2]: '#191919'}  # Цвет фона кнопок-картинок при нажатии

ST_BTN_BG_DISABL  = {THEMES[1]: '#D9D9D9', THEMES[2]: '#1E1E1E'}  # Цвет фона выключенных кнопок
ST_BTN_FG_DISABL  = {THEMES[1]: '#B0B0B0', THEMES[2]: '#454545'}  # Цвет текста выключенных кнопок

ST_CHECK_BG_SEL   = {THEMES[1]: '#DDDDDD', THEMES[2]: '#333333'}  # Цвет фона переключателя при наведении на него

ST_TAB_BG         = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1A1A1A'}  # Цвет фона закрытой вкладки
ST_TAB_BG_SEL     = {THEMES[1]: '#EAEAEA', THEMES[2]: '#222222'}  # Цвет фона открытой вкладки
ST_TAB_FG         = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста закрытой вкладки
ST_TAB_FG_SEL     = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста открытой вкладки

ST_SCROLL_BG      = {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}  # Цвет фона ползунка
ST_SCROLL_BG_SEL  = {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}  # Цвет фона ползунка при нажатии
ST_SCROLL_FG      = {THEMES[1]: '#CACACA', THEMES[2]: '#292929'}  # Цвет ползунка
ST_SCROLL_FG_SEL  = {THEMES[1]: '#ABABAB', THEMES[2]: '#333333'}  # Цвет ползунка при нажатии

# Названия стилизуемых элементов
STYLE_ELEMENTS = ('BG', 'BG_FIELDS',
                  'FG', 'FG_LOGO', 'FG_FOOTER', 'FG_WARN', 'FG_ENTRY',
                  'SELECT_BG', 'SELECT_FG',
                  'RELIEF_FRAME', 'RELIEF_TEXT', 'BORDERCOLOR',
                  'BTN_BG', 'BTN_BG_SEL', 'BTN_Y_BG', 'BTN_Y_BG_SEL', 'BTN_N_BG', 'BTN_N_BG_SEL',
                  'BTN_IMG_BG_HOV', 'BTN_IMG_BG_SEL',
                  'BTN_BG_DISABL', 'BTN_FG_DISABL',
                  'CHECK_BG_SEL',
                  'TAB_BG', 'TAB_BG_SEL', 'TAB_FG', 'TAB_FG_SEL',
                  'SCROLL_BG', 'SCROLL_BG_SEL', 'SCROLL_FG', 'SCROLL_FG_SEL')

# Стили для каждого элемента
STYLES = {STYLE_ELEMENTS[0]:  ST_BG,
          STYLE_ELEMENTS[1]:  ST_BG_FIELDS,
          STYLE_ELEMENTS[2]:  ST_FG,
          STYLE_ELEMENTS[3]:  ST_FG_LOGO,
          STYLE_ELEMENTS[4]:  ST_FG_FOOTER,
          STYLE_ELEMENTS[5]:  ST_FG_WARN,
          STYLE_ELEMENTS[6]:  ST_FG_ENTRY,
          STYLE_ELEMENTS[7]:  ST_SELECT_BG,
          STYLE_ELEMENTS[8]:  ST_SELECT_FG,
          STYLE_ELEMENTS[9]:  ST_RELIEF_FRAME,
          STYLE_ELEMENTS[10]: ST_RELIEF_TEXT,
          STYLE_ELEMENTS[11]: ST_BORDERCOLOR,
          STYLE_ELEMENTS[12]: ST_BTN_BG,
          STYLE_ELEMENTS[13]: ST_BTN_BG_SEL,
          STYLE_ELEMENTS[14]: ST_BTN_Y_BG,
          STYLE_ELEMENTS[15]: ST_BTN_Y_BG_SEL,
          STYLE_ELEMENTS[16]: ST_BTN_N_BG,
          STYLE_ELEMENTS[17]: ST_BTN_N_BG_SEL,
          STYLE_ELEMENTS[18]: ST_BTN_IMG_BG_HOV,
          STYLE_ELEMENTS[19]: ST_BTN_IMG_BG_SEL,
          STYLE_ELEMENTS[20]: ST_BTN_BG_DISABL,
          STYLE_ELEMENTS[21]: ST_BTN_FG_DISABL,
          STYLE_ELEMENTS[22]: ST_CHECK_BG_SEL,
          STYLE_ELEMENTS[23]: ST_TAB_BG,
          STYLE_ELEMENTS[24]: ST_TAB_BG_SEL,
          STYLE_ELEMENTS[25]: ST_TAB_FG,
          STYLE_ELEMENTS[26]: ST_TAB_FG_SEL,
          STYLE_ELEMENTS[27]: ST_SCROLL_BG,
          STYLE_ELEMENTS[28]: ST_SCROLL_BG_SEL,
          STYLE_ELEMENTS[29]: ST_SCROLL_FG,
          STYLE_ELEMENTS[30]: ST_SCROLL_FG_SEL}

# Названия стилей
STYLE_NAMES = {STYLE_ELEMENTS[0]:  'Цвет фона окна',
               STYLE_ELEMENTS[1]:  'Цвет фона полей ввода',
               STYLE_ELEMENTS[2]:  'Цвет обычного текста',
               STYLE_ELEMENTS[3]:  'Цвет текста логотипа',
               STYLE_ELEMENTS[4]:  'Цвет текста нижнего колонтитула',
               STYLE_ELEMENTS[5]:  'Цвет текста предупреждения',
               STYLE_ELEMENTS[6]:  'Цвет вводимого текста',
               STYLE_ELEMENTS[7]:  'Цвет выделения фона',
               STYLE_ELEMENTS[8]:  'Цвет выделения текста',
               STYLE_ELEMENTS[9]:  'Стиль рамок фреймов',
               STYLE_ELEMENTS[10]: 'Стиль рамок текстовых полей',
               STYLE_ELEMENTS[11]: 'Цвет рамок',
               STYLE_ELEMENTS[12]: 'Цвет фона обычных кнопок',
               STYLE_ELEMENTS[13]: 'Цвет фона обычных кнопок при нажатии',
               STYLE_ELEMENTS[14]: 'Цвет фона да-кнопок',
               STYLE_ELEMENTS[15]: 'Цвет фона да-кнопок при нажатии',
               STYLE_ELEMENTS[16]: 'Цвет фона нет-кнопок',
               STYLE_ELEMENTS[17]: 'Цвет фона нет-кнопок при нажатии',
               STYLE_ELEMENTS[18]: 'Цвет фона кнопок-картинок при наведении',
               STYLE_ELEMENTS[19]: 'Цвет фона кнопок-картинок при нажатии',
               STYLE_ELEMENTS[20]: 'Цвет фона выключенных кнопок',
               STYLE_ELEMENTS[21]: 'Цвет текста выключенных кнопок',
               STYLE_ELEMENTS[22]: 'Цвет фона переключателя при наведении на него',
               STYLE_ELEMENTS[23]: 'Цвет фона закрытой вкладки',
               STYLE_ELEMENTS[24]: 'Цвет фона открытой вкладки',
               STYLE_ELEMENTS[25]: 'Цвет текста закрытой вкладки',
               STYLE_ELEMENTS[26]: 'Цвет текста открытой вкладки',
               STYLE_ELEMENTS[27]: 'Цвет фона ползунка',
               STYLE_ELEMENTS[28]: 'Цвет фона ползунка при нажатии',
               STYLE_ELEMENTS[29]: 'Цвет ползунка',
               STYLE_ELEMENTS[30]: 'Цвет ползунка при нажатии'}

""" Пути, файлы, ссылки """

MAIN_PATH = os.path.dirname(__file__)  # Папка с программой
RESOURCES_DIR = 'resources'  # Папка с ресурсами
RESOURCES_PATH = os.path.join(MAIN_PATH, RESOURCES_DIR)
SAVES_DIR = 'saves'  # Папка с сохранениями
SAVES_PATH = os.path.join(RESOURCES_PATH, SAVES_DIR)
LOCAL_SETTINGS_DIR = 'local_settings'  # Папка с локальными настройками (настройки словаря)
LOCAL_SETTINGS_PATH = os.path.join(RESOURCES_PATH, LOCAL_SETTINGS_DIR)
GLOBAL_SETTINGS_FN = 'global_settings.txt'  # Файл с глобальными настройками (настройки программы)
GLOBAL_SETTINGS_PATH = os.path.join(RESOURCES_PATH, GLOBAL_SETTINGS_FN)
ADDITIONAL_THEMES_DIR = 'themes'  # Папка с дополнительными темами
ADDITIONAL_THEMES_PATH = os.path.join(RESOURCES_PATH, ADDITIONAL_THEMES_DIR)
CUSTOM_THEME_DIR = 'custom_theme'  # Папка с пользовательской темой
CUSTOM_THEME_PATH = os.path.join(RESOURCES_PATH, CUSTOM_THEME_DIR)
IMAGES_DIR = 'images'  # Папка с изображениями
IMAGES_PATH = os.path.join(RESOURCES_PATH, IMAGES_DIR)
TMP_FN = 'tmp.txt'  # Временный файл (для обновления словарей)
TMP_PATH = os.path.join(RESOURCES_PATH, TMP_FN)

# Если папки отсутствуют, то они создаются
if RESOURCES_DIR not in os.listdir(MAIN_PATH):
    os.mkdir(RESOURCES_PATH)
if SAVES_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(SAVES_PATH)
if LOCAL_SETTINGS_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(LOCAL_SETTINGS_PATH)
if ADDITIONAL_THEMES_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(ADDITIONAL_THEMES_PATH)
if CUSTOM_THEME_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(CUSTOM_THEME_PATH)
if IMAGES_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(IMAGES_PATH)

if THEMES[1] not in os.listdir(ADDITIONAL_THEMES_PATH):
    os.mkdir(os.path.join(ADDITIONAL_THEMES_PATH, THEMES[1]))
if THEMES[2] not in os.listdir(ADDITIONAL_THEMES_PATH):
    os.mkdir(os.path.join(ADDITIONAL_THEMES_PATH, THEMES[2]))

# Если временный файл не удалён, то он удаляется
if TMP_FN in os.listdir(RESOURCES_PATH):
    os.remove(TMP_PATH)

# Изображения
IMG_NAMES = ['ok', 'cancel',
             'add', 'delete', 'edit',
             'undo', 'redo',
             'about', 'about_mgsp', 'about_typo']
ICON_NAMES = IMG_NAMES[:-2]

img_ok = os.path.join(IMAGES_PATH, 'ok.png')
img_cancel = os.path.join(IMAGES_PATH, 'cancel.png')
img_add = os.path.join(IMAGES_PATH, 'add.png')
img_delete = os.path.join(IMAGES_PATH, 'delete.png')
img_edit = os.path.join(IMAGES_PATH, 'edit.png')
img_undo = os.path.join(IMAGES_PATH, 'undo.png')
img_redo = os.path.join(IMAGES_PATH, 'redo.png')
img_about = os.path.join(IMAGES_PATH, 'about.png')
img_about_mgsp = os.path.join(IMAGES_PATH, 'about_mgsp.png')
img_about_typo = os.path.join(IMAGES_PATH, 'about_typo.png')

# Название репозитория на GitHub
REPOSITORY_NAME = 'DictionaryManager'

# Ссылка на репозиторий программы на GitHub
URL_GITHUB = f'https://github.com/Anenokil/{REPOSITORY_NAME}'
# Ссылка на релизы программы
URL_RELEASES = f'https://github.com/Anenokil/{REPOSITORY_NAME}/releases'
# Ссылка на файл с названием последней версии
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/ver'
# Ссылка на файл со списком обновляемых файлов
URL_UPDATE_FILES = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/update_files'
# Ссылка для установки последней версии
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/archive/refs/heads/master.zip'

# Папки и файлы для установки обновлений
NEW_VERSION_DIR = f'{REPOSITORY_NAME}-master'
NEW_VERSION_PATH = os.path.join(MAIN_PATH, NEW_VERSION_DIR)  # Временная папка с обновлением
NEW_VERSION_ZIP = f'{NEW_VERSION_DIR}.zip'
NEW_VERSION_ZIP_PATH = os.path.join(MAIN_PATH, NEW_VERSION_ZIP)  # Архив с обновлением

""" Другие константы """

CATEGORY_SEPARATOR = '@'  # Разделитель для записи значений категории в файл локальных настроек
SPECIAL_COMBINATION_OPENING_SYMBOL = '#'  # Открывающий символ специальных комбинаций

VALUES_LEARN_METHOD = ('Угадывать слово по переводу', 'Угадывать перевод по слову')  # Варианты метода учёбы
VALUES_LEARN_WORDS = ('Все слова', 'Все слова (чаще сложные)', 'Только избранные')  # Варианты подбора слов для учёбы

""" Объекты """


# Словарная статья
class Entry(object):
    # self.wrd - слово (начальная форма)
    # self.tr - переводы
    # self.notes - сноски
    # self.forms - словоформы (кроме начальной)
    # self.count_t - количество переводов
    # self.count_n - количество сносок
    # self.count_f - количество форм слова
    # self.fav - избранное
    # self.all_att - количество всех попыток
    # self.correct_att - количество удачных попыток
    # self.score - доля удачных попыток
    # self.last_att - количество последних неудачных попыток (-1 - значит, что ещё не было попыток)
    def __init__(self,
                 wrd: str,
                 tr: str | list[str],
                 notes: str | list[str] | None = None,
                 forms: dict[tuple[str, ...], str] | None = None,
                 fav=False, all_att=0, correct_att=0, last_att=-1):
        self.wrd = wrd
        self.tr = tr.copy() if (type(tr) == list) else [tr]
        if notes is None:
            self.notes = []
        elif type(notes) == list:
            self.notes = notes.copy()
        else:
            self.notes = [notes]
        self.forms = {}
        if type(forms) == dict:
            self.forms = dict(forms.copy())
        self.count_t = len(self.tr)
        self.count_n = len(self.notes)
        self.count_f = len(self.forms)
        self.fav = fav
        self.all_att = all_att
        self.correct_att = correct_att
        self.score = correct_att / all_att if (all_att != 0) else 0
        self.last_att = last_att

    # Преобразовать переводы в читаемый вид
    def tr_to_str(self):
        if self.count_t == 0:  # Если нет переводов, возвращается пустая строка
            return ''
        res = f'> {self.tr[0]}'
        for i in range(1, self.count_t):
            res += f'\n> {self.tr[i]}'
        return res

    # Преобразовать сноски в читаемый вид
    def notes_to_str(self):
        if self.count_n == 0:  # Если нет сносок, возвращается пустая строка
            return ''
        res = f'> {self.notes[0]}'
        for i in range(1, self.count_n):
            res += f'\n> {self.notes[i]}'
        return res

    # Преобразовать словоформы в читаемый вид
    def frm_to_str(self):
        if self.count_f == 0:  # Если нет словоформ, возвращается пустая строка
            return ''
        keys = list(self.forms.keys())
        res = f'[{tpl(keys[0])}] {self.forms[keys[0]]}'
        for i in range(1, self.count_f):
            res += f'\n[{tpl(keys[i])}] {self.forms[keys[i]]}'
        return res

    # Напечатать переводы
    def tr_print(self):
        res = ''
        if self.count_t != 0:
            res += self.tr[0]
            for i in range(1, self.count_t):
                res += f', {self.tr[i]}'
        return res

    # Напечатать сноски
    def notes_print(self, tab=0):
        res = ''
        if self.count_n != 0:
            res += ' ' * tab + f'> {self.notes[0]}'
            for i in range(1, self.count_n):
                res += '\n' + ' ' * tab + f'> {self.notes[i]}'
        return res

    # Напечатать словоформы
    def frm_print(self, tab=0):
        res = ''
        keys = tuple(self.forms.keys())
        if self.count_f != 0:
            res += ' ' * tab + f'[{tpl(keys[0])}] {self.forms[keys[0]]}'
            for i in range(1, len(keys)):
                res += '\n' + ' ' * tab + f'[{tpl(keys[i])}] {self.forms[keys[i]]}'
        return res

    # Напечатать количество ошибок после последнего верного ответа
    def last_att_print(self):
        if self.last_att == -1:  # Если ещё не было попыток
            res = '-'
        else:
            res = self.last_att
        return res

    # Напечатать процент верных ответов
    def percent_print(self):
        if self.last_att == -1:  # Если ещё не было попыток
            res = '-'
        else:
            res = '{:.0%}'.format(self.score)
        return res

    # Напечатать статистику
    def stat_print(self):
        last_att = self.last_att_print()
        percent = self.percent_print()
        tab = ' ' * (4 - len(percent))
        res = f'[{last_att}:{tab}{percent}]'
        return res

    # Добавить в избранное
    def add_to_fav(self):
        self.fav = True

    # Убрать из избранного
    def remove_from_fav(self):
        self.fav = False

    # Изменить статус избранного
    def change_fav(self):
        self.fav = not self.fav

    # Служебный метод для print_briefly и print_briefly_with_forms
    def _print_briefly(self):
        if self.fav:
            res = '(*)'
        else:
            res = '   '
        res += f' {self.stat_print()} {self.wrd}: {self.tr_print()}'
        return res

    # Напечатать статью - кратко
    def print_briefly(self, len_str):
        res = self._print_briefly()
        if self.count_n != 0:
            res += f'\n{self.notes_print(tab=13)}'
        return split_text(res, len_str, tab=13)

    # Напечатать статью - кратко со словоформами
    def print_briefly_with_forms(self, len_str):
        res = self._print_briefly()
        if self.count_f != 0:
            res += f'\n{self.frm_print(tab=13)}'
        if self.count_n != 0:
            res += f'\n{self.notes_print(tab=13)}'
        return split_text(res, len_str, tab=13)

    # Напечатать статью - слово со статистикой
    def print_wrd_with_stat(self):
        res = f'{self.wrd} {self.stat_print()}'
        return res

    # Напечатать статью - перевод со статистикой
    def print_tr_with_stat(self):
        res = f'{self.tr_print()} {self.stat_print()}'
        return res

    # Напечатать статью - перевод со словоформой и со статистикой
    def print_tr_and_frm_with_stat(self, frm_key: tuple[str, ...] | list[str]):
        res = f'{self.tr_print()} ({tpl(frm_key)}) {self.stat_print()}'
        return res

    # Напечатать статью - со всей информацией
    def print_all(self, len_str, tab=0):
        res = ''
        res += f'      Слово: {self.wrd}\n'
        res += f'    Перевод: {self.tr_print()}\n'
        res += f'Формы слова: '
        if self.count_f == 0:
            res += '-\n'
        else:
            keys = [key for key in self.forms.keys()]
            res += f'[{tpl(keys[0])}] {self.forms[keys[0]]}\n'
            for i in range(1, self.count_f):
                res += f'             [{tpl(keys[i])}] {self.forms[keys[i]]}\n'
        res += '     Сноски: '
        if self.count_n == 0:
            res += '-\n'
        else:
            res += f'> {self.notes[0]}\n'
            for i in range(1, self.count_n):
                res += f'             > {self.notes[i]}\n'
        res += f'  Избранное: {self.fav}\n'
        if self.last_att == -1:
            res += ' Статистика: 1) Прошло ответов после последнего верного: -\n'
            res += '             2) Доля верных ответов: 0'
        else:
            res += f' Статистика: 1) Прошло ответов после последнего верного: {self.last_att}\n'
            res += f'             2) Доля верных ответов: '
            res += f'{self.correct_att}/{self.all_att} = ' + '{:.0%}'.format(self.score)
        return split_text(res, len_str, tab=tab)

    # Добавить перевод
    def add_tr(self, new_tr: str):
        if new_tr not in self.tr:
            self.tr += [new_tr]
            self.count_t += 1

    # Удалить перевод
    def delete_tr(self, tr: str):
        self.tr.remove(tr)
        self.count_t -= 1

    # Добавить сноску
    def add_note(self, new_note: str):
        if new_note not in self.notes:
            self.notes += [new_note]
            self.count_n += 1

    # Удалить сноску
    def delete_note(self, note: str):
        self.notes.remove(note)
        self.count_n -= 1

    # Добавить словоформу
    def add_frm(self, frm_key: tuple[str, ...] | list[str], new_frm: str):
        if frm_key not in self.forms.keys():
            self.forms[frm_key] = new_frm
            self.count_f += 1

    # Удалить словоформу
    def delete_frm(self, frm_key: tuple[str, ...] | list[str]):
        self.forms.pop(frm_key)
        self.count_f -= 1

    # Удалить данное значение категории у всех словоформ
    def delete_forms_with_val(self, pos: int, ctg_val: str):
        to_delete = []
        for key in self.forms.keys():
            if key[pos] == ctg_val:
                to_delete += [key]
                self.count_f -= 1
        for key in to_delete:
            self.forms.pop(key)

    # Переименовать данное значение категории у всех словоформ
    def rename_forms_with_val(self, pos: int, old_ctg_val: str, new_ctg_val: str):
        to_rename = []
        for key in self.forms.keys():
            if key[pos] == old_ctg_val:
                to_rename += [key]
        for key in to_rename:
            lst = list(key)
            lst[pos] = new_ctg_val
            lst = tuple(lst)
            self.forms[lst] = self.forms[key]
            self.forms.pop(key)

    # Добавить новую категорию ко всем словоформам
    def add_ctg(self):
        keys = list(self.forms.keys())
        for key in keys:
            new_key = list(key)
            new_key += ['']
            new_key = tuple(new_key)
            self.forms[new_key] = self.forms[key]
            self.forms.pop(key)

    # Удалить данную категорию у всех словоформ
    def delete_ctg(self, pos: int):
        to_delete = []
        to_edit = []
        for key in self.forms.keys():
            if key[pos] != '':
                to_delete += [key]
                self.count_f -= 1
            else:
                to_edit += [key]
        for key in to_edit:
            new_key = list(key)
            new_key.pop(pos)
            new_key = tuple(new_key)
            self.forms[new_key] = self.forms[key]
            self.forms.pop(key)
        for key in to_delete:
            self.forms.pop(key)

    # Объединить статистику при объединении двух статей
    def merge_stat(self, all_att: int, correct_att: int, last_att: int):
        self.all_att += all_att
        self.correct_att += correct_att
        self.score = self.correct_att / self.all_att if (self.all_att != 0) else 0
        self.last_att += last_att if last_att != -1 else 0

    # Обновить статистику, если совершена верная попытка
    def correct(self):
        self.all_att += 1
        self.correct_att += 1
        self.score = self.correct_att / self.all_att
        self.last_att = 0

    # Обновить статистику, если совершена неверная попытка
    def incorrect(self):
        self.all_att += 1
        self.score = self.correct_att / self.all_att
        if self.last_att == -1:
            self.last_att = 1
        else:
            self.last_att += 1

    # Сохранить статью в файл
    def save(self, file: typing.TextIO):
        file.write(f'w{self.wrd}\n')
        file.write(f'{self.all_att}:{self.correct_att}:{self.last_att}\n')
        file.write(f'{self.tr[0]}\n')
        for i in range(1, self.count_t):
            file.write(f't{self.tr[i]}\n')
        for note in self.notes:
            file.write(f'n{note}\n')
        for frm_template in self.forms.keys():
            file.write(f'f{decode_tpl(frm_template)}\n'
                       f'{self.forms[frm_template]}\n')
        if self.fav:
            file.write('*\n')

    # Распечатать статью в файл
    def print_out(self, file: typing.TextIO):
        file.write(f'|{self.wrd} - {self.tr[0]}')
        for i in range(1, self.count_t):
            file.write(f', {self.tr[i]}')
        file.write('\n')
        for note in self.notes:
            file.write(f'| > {note}\n')
        for frm_template in self.forms.keys():
            file.write(f'| [{tpl(frm_template)}] {self.forms[frm_template]}\n')
        if self.fav:
            file.write('| <Fav>\n')


# Словарь
class Dictionary(object):
    # self.d: dict[tuple[str, int], Entry] - сам словарь
    # self.count_w - количество статей (слов) в словаре
    # self.count_t - количество переводов в словаре
    # self.count_f - количество неначальных словоформ в словаре
    def __init__(self):
        self.d: dict[tuple[str, int], Entry] = {}
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0

    # Вывести информацию о количестве статей в словаре
    def dct_info(self):
        w = set_postfix(self.count_w, ('слово', 'слова', 'слов'))
        f = set_postfix(self.count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        t = set_postfix(self.count_t, ('перевод', 'перевода', 'переводов'))
        return f'< {self.count_w} {w} | {self.count_w + self.count_f} {f} | {self.count_t} {t} >'

    # Вывести информацию о количестве избранных статей в словаре
    def dct_info_fav(self, count_w: int, count_t: int, count_f: int):
        w = set_postfix(count_w, ('слово', 'слова', 'слов'))
        f = set_postfix(count_w + count_f, ('словоформа', 'словоформы', 'словоформ'))
        t = set_postfix(count_t, ('перевод', 'перевода', 'переводов'))
        return f'< {count_w}/{self.count_w} {w} | ' \
               f'{count_w + count_f}/{self.count_w + self.count_f} {f} | ' \
               f'{count_t}/{self.count_t} {t} >'

    # Подсчитать количество избранных статей
    def count_fav(self):
        count_w = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if entry.fav:
                count_w += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_w, count_t, count_f

    # Напечатать статьи, в которых слова содержат данную строку
    def get_words_with_content(self, search_wrd: str) -> list[tuple[tuple[str, int], str]] | list:
        res = []
        for key in self.d.keys():
            wrd = key_to_wrd(key)
            ans = find_and_highlight(wrd, search_wrd)
            if ans != '':
                res += [(key, ans)]
        return res

    # Напечатать статьи, в которых переводы содержат данную строку
    def get_translations_with_content(self, search_tr: str) -> list[tuple[tuple[str, int], str]] | list:
        res = []
        for key in self.d.keys():
            entry = self.d[key]
            is_first_in_line = True
            tmp = ''
            for tr in entry.tr:
                ans = find_and_highlight(tr, search_tr)
                if ans != '':
                    if is_first_in_line:
                        is_first_in_line = False
                        tmp = f'{entry.wrd}: '
                    else:
                        # Вывод запятой после найденного перевода (кроме первого в статье перевода)
                        tmp += ', '
                    tmp += ans  # Вывод перевода
            if tmp != '':
                res += [(key, tmp)]
        return res

    # Выбрать одну статью из нескольких с одинаковыми словами
    def choose_one_of_similar_entries(self, window_parent, wrd: str):
        if wrd_to_key(wrd, 1) not in self.d.keys():  # Если статья только одна, то возвращает её ключ
            return wrd_to_key(wrd, 0)
        window_note = ChooseOneOfSimilarNotesW(window_parent, wrd)
        closed, answer = window_note.open()
        if closed:
            return None
        return answer

    # Изменить слово в статье
    def edit_wrd(self, window_parent, key: tuple[str, int], new_wrd: str):
        if wrd_to_key(new_wrd, 0) in self.d.keys():  # Если в словаре уже есть статья с таким словом
            window = PopupDialogueW(window_parent, 'Статья с таким словом уже есть в словаре\n'
                                                   'Что вы хотите сделать?',
                                    'Добавить к существующей статье', 'Создать новую статью',
                                    set_enter_on_btn='none', st_left='Default', st_right='Default',
                                    val_left='l', val_right='r', val_on_close='c')
            answer = window.open()
            if answer == 'l':  # Добавить к существующей статье
                new_key = self.choose_one_of_similar_entries(window_parent, new_wrd)
                if not new_key:
                    return None

                self.count_t -= self.d[key].count_t
                self.count_t -= self.d[new_key].count_t
                self.count_f -= self.d[key].count_f
                self.count_f -= self.d[new_key].count_f

                for tr in self.d[key].tr:
                    self.d[new_key].add_tr(tr)
                for note in self.d[key].notes:
                    self.d[new_key].add_note(note)
                for frm_key in self.d[key].forms.keys():
                    frm = self.d[key].forms[frm_key]
                    self.d[new_key].add_frm(frm_key, frm)
                if self.d[key].fav:
                    self.d[new_key].fav = True
                self.d[new_key].merge_stat(self.d[key].all_att, self.d[key].correct_att, self.d[key].last_att)

                self.count_w -= 1
                self.count_t += self.d[new_key].count_t
                self.count_f += self.d[new_key].count_f

                self.d.pop(key)
                return new_key
            elif answer == 'r':  # Создать новую статью
                i = 0
                while True:
                    new_key = wrd_to_key(new_wrd, i)
                    if new_key not in self.d.keys():
                        self.d[new_key] = Entry(new_wrd, self.d[key].tr, self.d[key].notes, self.d[key].forms,
                                                self.d[key].fav, self.d[key].all_att, self.d[key].correct_att,
                                                self.d[key].last_att)
                        self.d.pop(key)
                        return new_key
                    i += 1
            else:
                return None
        else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
            new_key = wrd_to_key(new_wrd, 0)
            self.d[new_key] = Entry(new_wrd, self.d[key].tr, self.d[key].notes, self.d[key].forms,
                                    self.d[key].fav, self.d[key].all_att, self.d[key].correct_att,
                                    self.d[key].last_att)
            self.d.pop(key)
            return new_key

    # Добавить перевод к статье
    def add_tr(self, key: tuple[str, int], tr: str):
        self.count_t -= self.d[key].count_t
        self.d[key].add_tr(tr)
        self.count_t += self.d[key].count_t

    # Добавить сноску к статье
    def add_note(self, key: tuple[str, int], note: str):
        self.d[key].add_note(note)

    # Добавить словоформу к статье
    def add_frm(self, key: tuple[str, int], frm_key: tuple[str, ...] | list[str], frm: str):
        self.count_f -= self.d[key].count_f
        self.d[key].add_frm(frm_key, frm)
        self.count_f += self.d[key].count_f

    # Удалить перевод в статье
    def delete_tr(self, key: tuple[str, int], tr: str):
        self.count_t -= self.d[key].count_t
        self.d[key].delete_tr(tr)
        self.count_t += self.d[key].count_t

    # Удалить сноску в статье
    def delete_note(self, key: tuple[str, int], note: str):
        self.d[key].delete_note(note)

    # Удалить словоформу в статье
    def delete_frm(self, key: tuple[str, int], frm_key: tuple[str, ...] | list[str]):
        self.count_f -= self.d[key].count_f
        self.d[key].delete_frm(frm_key)
        self.count_f += self.d[key].count_f

    # Добавить статью в словарь (для пользователя)
    def add_entry(self, window_parent, wrd: str, tr: str):
        if wrd_to_key(wrd, 0) in self.d.keys():  # Если в словаре уже есть статья с таким словом
            while True:
                window = PopupDialogueW(window_parent, 'Статья с таким словом уже есть в словаре\n'
                                                       'Что вы хотите сделать?',
                                        'Добавить к существующей статье', 'Создать новую статью',
                                        set_enter_on_btn='none', st_left='Default', st_right='Default',
                                        val_left='l', val_right='r', val_on_close='c')
                answer = window.open()
                if answer == 'l':  # Добавить к существующей статье
                    key = self.choose_one_of_similar_entries(window_parent, wrd)
                    if not key:
                        return None
                    self.add_tr(key, tr)
                    return key
                elif answer == 'r':  # Создать новую статью
                    i = 0
                    while True:
                        key = wrd_to_key(wrd, i)
                        if key not in self.d.keys():
                            self.d[key] = Entry(wrd, [tr])
                            self.count_w += 1
                            self.count_t += 1
                            return key
                        i += 1
                else:
                    return None
        else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
            key = wrd_to_key(wrd, 0)
            self.d[key] = Entry(wrd, [tr])
            self.count_w += 1
            self.count_t += 1
            return key

    # Добавить статью в словарь (при чтении файла)
    def load_entry(self, wrd: str, tr: str, all_att: int, correct_att: int, last_att: int):
        i = 0
        while True:
            key = wrd_to_key(wrd, i)
            if key not in self.d.keys():
                self.d[key] = Entry(wrd, [tr], all_att=all_att, correct_att=correct_att, last_att=last_att)
                self.count_w += 1
                self.count_t += 1
                return key
            i += 1

    # Удалить статью
    def delete_entry(self, key: tuple[str, int]):
        self.count_w -= 1
        self.count_t -= self.d[key].count_t
        self.count_f -= self.d[key].count_f
        self.d.pop(key)

    # Добавить все статьи в избранное
    def fav_all(self):
        for note in self.d.values():
            note.add_to_fav()

    # Убрать все статьи из избранного
    def unfav_all(self):
        for note in self.d.values():
            note.remove_from_fav()

    # Удалить данное значение категории у всех словоформ
    def delete_forms_with_val(self, pos: int, ctg_val: str):
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_forms_with_val(pos, ctg_val)
            self.count_f += entry.count_f

    # Переименовать данное значение категории у всех словоформ
    def rename_forms_with_val(self, pos: int, old_ctg_val: str, new_ctg_val: str):
        for entry in self.d.values():
            entry.rename_forms_with_val(pos, old_ctg_val, new_ctg_val)

    # Добавить данную категорию ко всем словоформам
    def add_ctg(self):
        for entry in self.d.values():
            entry.add_ctg()

    # Удалить данную категорию у всех словоформ
    def delete_ctg(self, pos: int):
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_ctg(pos)
            self.count_f += entry.count_f

    # Подсчитать среднюю долю правильных ответов
    def count_rating(self):
        sum_num = 0
        sum_den = 0
        for entry in self.d.values():
            sum_num += entry.correct_att
            sum_den += entry.all_att
        if sum_den == 0:
            return 0
        return sum_num / sum_den

    # Выбрать случайное слово с учётом сложности
    def random_hard(self, min_good_score_perc: int):
        summ = 0
        for entry in self.d.values():
            summ += (100 - round(100 * entry.score)) * 7 + 1
            if entry.all_att < 5:
                summ += (5 - entry.all_att) * 20
            if 100 * entry.score < min_good_score_perc:
                summ += 100
        r = random.randint(1, summ)

        for key in self.d.keys():
            r -= (100 - round(100 * self.d[key].score)) * 7 + 1
            if self.d[key].all_att < 5:
                r -= (5 - self.d[key].all_att) * 20
            if 100 * self.d[key].score < min_good_score_perc:
                r -= 100
            if r <= 0:
                return key

    # Прочитать словарь из файла
    def read(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as file:
            file.readline()  # Первая строка - версия сохранения словаря
            while True:
                line = file.readline().strip()
                if not line:
                    break
                elif line[0] == 'w':
                    wrd = line[1:]
                    all_att, correct_att, last_att = (int(el) for el in file.readline().strip().split(':'))
                    tr = file.readline().strip()
                    key = self.load_entry(wrd, tr, all_att, correct_att, last_att)
                elif line[0] == 't':
                    self.add_tr(key, line[1:])
                elif line[0] == 'n':
                    self.add_note(key, line[1:])
                elif line[0] == 'f':
                    frm_key = encode_tpl(line[1:])
                    self.add_frm(key, frm_key, file.readline().strip())
                elif line[0] == '*':
                    self.d[key].add_to_fav()

    # Сохранить словарь в файл
    def save(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'v{SAVES_VERSION}\n')
            for entry in self.d.values():
                entry.save(file)

    # Распечатать словарь в файл
    def print_out(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.print_out(file)
                file.write('\n')


""" Функции проверки """


# Проверить строку на непустоту
def check_not_void(window_parent, value: str, msg_if_void: str):
    if value == '':
        warning(window_parent, msg_if_void)
        return False
    return True


# Проверить корректность названия словаря
def check_dct_savename(window_parent, savename: str):
    if savename == '':
        warning(window_parent, 'Название должно содержать хотя бы один символ!')
        return False
    if dct_filename(savename) in os.listdir(SAVES_PATH):  # Если уже есть сохранение с таким названием
        warning(window_parent, 'Файл с таким названием уже существует!')
        return False
    return True


# Проверить корректность изменённого слова
def check_wrd_edit(window_parent, old_wrd: str, new_wrd: str):
    if new_wrd == '':
        warning(window_parent, 'Слово должно содержать хотя бы один символ!')
        return False
    if new_wrd == old_wrd:
        warning(window_parent, 'Это то же самое слово!')
        return False
    return True


# Проверить корректность перевода
def check_tr(window_parent, translations: list[str] | tuple[str, ...], new_tr: str, wrd: str):
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations:
        warning(window_parent, f'У слова "{wrd}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность сноски
def check_note(window_parent, notes: list[str] | tuple[str, ...], new_note: str, wrd: str):
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes:
        warning(window_parent, f'У слова "{wrd}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность названия категории
def check_ctg(window_parent, categories: list[str] | tuple[str, ...], new_ctg: str):
    if new_ctg == '':
        warning(window_parent, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories:  # Если уже есть категория с таким названием
        warning(window_parent, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


# Проверить корректность значения категории
def check_ctg_val(window_parent, values: list[str] | tuple[str, ...], new_val: str):
    if new_val == '':
        warning(window_parent, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_val in values:
        warning(window_parent, f'Значение "{new_val}" уже существует!')
        return False
    if CATEGORY_SEPARATOR in new_val:
        warning(window_parent, f'Недопустимый символ: {CATEGORY_SEPARATOR}!')
        return False
    return True


""" Вспомогательные функции """


# Вычислить ширину моноширинного поля, в которое должно помещаться каждое из данных значений
def width(values: tuple[str, ...] | list[str], min_width: int, max_width: int):
    assert min_width >= 0
    assert max_width >= 0
    assert max_width >= min_width

    max_len_of_vals = max(len(val) for val in values)
    return min(max(max_len_of_vals, min_width), max_width)


# Вычислить количество строк, необходимых для записи данного текста
# в многострочное текстовое поле при данной длине строки
def height(text: str, len_str: int):
    assert len_str > 0

    segments = text.split('\n')
    return sum(math.ceil(len(segment) / len_str) for segment in segments)


# Разделить текст на части, длина которых не превышает заданное значение
def split_text(text: str, len_str: int, tab: int = 0, align_left: bool = True):
    assert len_str > 0
    assert tab < len_str

    res = ''
    while len(text) > len_str:
        segment = text[:len_str+1]
        pos = segment.find('\n')
        if pos == -1:
            segment = f'{text[:len_str]}\n'
            text = ' ' * tab + text[len_str:]
        elif pos == len_str:
            text = text[pos+1:]
        else:
            segment = text[:pos]
            if align_left:
                segment += ' ' * (len_str - pos)
            segment += '\n'
            text = text[pos+1:]
        res += segment
    while '\n' in text:
        pos = text.find('\n')
        res += text[:pos]
        if align_left:
            res += ' ' * (len_str - pos)
        res += '\n'
        text = text[pos+1:]
    if text != '':
        res += text
        if align_left:
            res += ' ' * (len_str - len(text))
    return res


# Преобразовать специальную комбинацию в читаемый вид (для отображения в настройках)
def special_combination(key: str):
    val = _0_global_special_combinations[key]
    return f'{SPECIAL_COMBINATION_OPENING_SYMBOL}{key} -> {val}'


# Преобразовать в тексте специальные комбинации в соответствующие символы
def encode_special_combinations(text: str):
    encoded_text = ''

    is_special_combination_open = False  # Встречен ли открывающий символ специальной комбинации
    for symbol in text:
        if is_special_combination_open:
            if symbol in _0_global_special_combinations.keys():  # Если есть комбинация с этим символом
                encoded_text += _0_global_special_combinations[symbol]
            elif symbol == SPECIAL_COMBINATION_OPENING_SYMBOL:  # Если встречено два открывающих символа подряд
                encoded_text += SPECIAL_COMBINATION_OPENING_SYMBOL  # (## -> #)
            else:  # Если нет комбинации с этим символом
                encoded_text += f'{SPECIAL_COMBINATION_OPENING_SYMBOL}{symbol}'
            is_special_combination_open = False
        elif symbol == SPECIAL_COMBINATION_OPENING_SYMBOL:  # Если встречен открывающий символ специальной комбинации
            is_special_combination_open = True
        else:  # Если встречен обычный символ
            encoded_text += symbol
    if is_special_combination_open:  # Если текст завершается открывающим символом специальной комбинации
        encoded_text += SPECIAL_COMBINATION_OPENING_SYMBOL

    return encoded_text


# Заменить буквы в тексте соответствующими английскими (для find_and_highlight)
def simplify(text: str):
    encoded_text = encode_special_combinations(text)
    converted_text = ''
    transformations = []

    for symbol in encoded_text:
        if symbol in ('ä', 'Ä', 'ë', 'Ë', 'ö', 'Ö', 'ü', 'Ü', 'ß', 'ẞ'):
            pos = ('ä', 'Ä', 'ë', 'Ë', 'ö', 'Ö', 'ü', 'Ü', 'ß', 'ẞ').index(symbol)
            converted_text += ('a', 'A', 'e', 'E', 'o', 'O', 'u', 'U', 'ss', 'SS')[pos]
            transformations += (['ä'], ['Ä'], ['ë'], ['Ë'], ['ö'], ['Ö'], ['ü'], ['Ü'], ['ß', ''], ['ẞ', ''])[pos]
        else:
            converted_text += symbol
            transformations += [symbol]

    return converted_text.lower(), transformations


# Конкатенация строк
def arr_to_str(arr: list[str] | tuple[str, ...]):
    res = ''
    for frag in arr:
        res += frag
    return res


# Найти в строке подстроку и выделить её (только частичные совпадения)
def find_and_highlight(target_wrd: str, search_wrd: str):
    target_wrd = encode_special_combinations(target_wrd)
    search_wrd = encode_special_combinations(search_wrd)

    target_simpl, target_arr = simplify(target_wrd)
    search_simpl, search_arr = simplify(search_wrd)

    if target_wrd != search_wrd:  # Полное совпадение не учитывается
        pos = target_simpl.find(search_simpl)
        if pos != -1:
            search_len = len(encode_special_combinations(search_simpl))
            end_pos = pos + search_len
            if search_wrd == '':  # Если искомая подстрока пустая, то она не выделяется
                res = target_wrd
            else:
                res = f'{arr_to_str(target_arr[:pos])}' \
                      f'[{arr_to_str(target_arr[pos:end_pos])}]' \
                      f'{arr_to_str(target_arr[end_pos:])}'
            return res
    return ''


# Преобразовать кортеж в читаемый вид (для вывода на экран)
def tpl(input_tuple: tuple | list):
    res = ''
    is_first = True
    for i in range(len(input_tuple)):
        if input_tuple[i] != '':
            if is_first:  # Перед первым элементом не ставится запятая
                res += f'{input_tuple[i]}'
                is_first = False
            else:  # Перед последующими элементами ставится запятая
                res += f', {input_tuple[i]}'
    return res


# Преобразовать кортеж в строку (для сохранения значений категории в файл локальных настроек)
def decode_tpl(input_tuple: tuple | list, separator=CATEGORY_SEPARATOR):
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Преобразовать строку в кортеж (для чтения значений категории из файла локальных настроек)
def encode_tpl(line: str):
    return tuple(line.split(CATEGORY_SEPARATOR))


# Перевести слово в ключ для словаря
def wrd_to_key(wrd: str, num: int):  # При изменении этой функции, не забыть поменять key_to_wrd
    return wrd, num


# Перевести ключ для словаря в слово
def key_to_wrd(key: tuple[str, int]):  # При изменении этой функции, не забыть поменять wrd_to_key
    return key[0]


# Выбрать окончание слова в зависимости от количественного числительного
def set_postfix(n: int, wrd_forms: tuple[str, str, str]):
    if 5 <= (n % 100) <= 20:
        return wrd_forms[2]  # Пример: 5 яблок
    elif n % 10 == 1:
        return wrd_forms[0]  # Пример: 1 яблоко
    elif 1 < n % 10 < 5:
        return wrd_forms[1]  # Пример: 2 яблока
    else:
        return wrd_forms[2]  # Пример: 0 яблок


# Получить название файла со словарём по названию словаря
def dct_filename(savename: str):
    return f'{savename}.txt'


""" Основные функции """


# Добавить категорию
def add_ctg(window_parent, categories: dict[str, list[str]], dct: Dictionary):
    # Ввод новой категории
    window_entry = PopupEntryW(window_parent, 'Введите название новой категории',
                               check_answer_function=lambda wnd, val: check_ctg(wnd, tuple(categories.keys()), val))
    closed, new_ctg = window_entry.open()
    if closed:
        return False
    new_ctg = encode_special_combinations(new_ctg)

    # Ввод первого значения категории
    has_changes, new_val = add_ctg_val(window_parent, (),
                                       'Необходимо добавить хотя бы одно значение для категории')
    if not new_val:
        return False
    new_val = encode_special_combinations(new_val)

    # Обновление категорий
    dct.add_ctg()
    categories[new_ctg] = []
    categories[new_ctg] += [new_val]
    return True


# Переименовать категорию
def rename_ctg(window_parent, categories: dict[str, list[str]]):
    ctg_names = [ctg_name for ctg_name in categories.keys()]
    window_choose = PopupChooseW(window_parent, ctg_names, default_value=ctg_names[0], btn_text='Переименовать',
                                 combo_width=width(ctg_names, 5, 100))  # Выбор категории, которую нужно переименовать
    closed, old_name = window_choose.open()
    if closed:
        return False

    # Ввод нового названия категории
    window_entry = PopupEntryW(window_parent, 'Введите новое название категории',
                               check_answer_function=lambda wnd, val: check_ctg(wnd, tuple(categories.keys()), val))
    closed, new_name = window_entry.open()
    if closed:
        return False
    new_name = encode_special_combinations(new_name)

    # обновление категорий
    categories[new_name] = categories[old_name]
    categories.pop(old_name)
    return True


# Удалить категорию
def delete_ctg(window_parent, categories: dict[str, list[str]], dct: Dictionary):
    ctg_names = [ctg_name for ctg_name in categories.keys()]
    window_choose = PopupChooseW(window_parent, ctg_names, default_value=ctg_names[0], btn_text='Удалить',
                                 combo_width=width(ctg_names, 5, 100))  # Выбор категории, которую нужно удалить
    closed, selected_ctg_name = window_choose.open()
    if closed:
        return False
    window_dia = PopupDialogueW(window_parent, 'Все словоформы, содержащие эту категорию, будут удалены!\n'
                                               'Хотите продолжить?')  # Подтверждение действия
    answer = window_dia.open()
    if answer:
        pos = ctg_names.index(selected_ctg_name)
        categories.pop(selected_ctg_name)
        dct.delete_ctg(pos)
        return True
    return False


# Добавить значение категории
def add_ctg_val(window_parent, values: list[str] | tuple[str, ...], text='Введите новое значение категории'):
    # Ввод нового значения
    window_entry = PopupEntryW(window_parent, text,
                               check_answer_function=lambda wnd, val: check_ctg_val(wnd, values, val))
    closed, new_val = window_entry.open()
    if closed:
        return False, None
    new_val = encode_special_combinations(new_val)

    return True, new_val


# Переименовать значение категории
def rename_ctg_val(window_parent, values: list[str] | tuple[str, ...], pos: int, dct: Dictionary):
    window_choose = PopupChooseW(window_parent, values, default_value=values[0],
                                 combo_width=width(values, 5, 100))  # Выбор значения, которое нужно переименовать
    closed, old_val = window_choose.open()
    if closed:
        return False

    # Ввод нового значения
    window_entry = PopupEntryW(window_parent, 'Введите новое значение категории',
                               check_answer_function=lambda wnd, val: check_ctg_val(wnd, values, val))
    closed, new_val = window_entry.open()
    if closed:
        return False
    new_val = encode_special_combinations(new_val)

    dct.rename_forms_with_val(pos, old_val, new_val)  # Переименовывание значения во всех словоформах, его содержащих
    index = values.index(old_val)
    values[index] = new_val
    return True


# Удалить значение категории
def delete_ctg_val(window_parent, values: list[str] | tuple[str, ...], dct: Dictionary):
    window_choose = PopupChooseW(window_parent, values, default_value=values[0],
                                 combo_width=width(values, 5, 100))  # Выбор значения, которое нужно удалить
    closed, val = window_choose.open()
    if closed:
        return False
    window_dia = PopupDialogueW(window_parent, 'Все словоформы, содержащие это значение категории, будут удалены!\n'
                                               'Хотите продолжить?')  # Подтверждение действия
    answer = window_dia.open()
    if answer:
        index = values.index(val)
        values.pop(index)
        dct.delete_forms_with_val(index, val)  # Удаление всех словоформ, содержащих это значение категории
        return True
    return False


""" Загрузка/сохранение/обновление """


# Проверить наличие обновлений программы
def check_updates(window_parent, show_updates: bool, show_if_no_updates: bool):
    print('\nПроверка наличия обновлений...')
    window_last_version = None
    try:
        data = urllib2.urlopen(URL_LAST_VERSION)
        last_version = str(data.readline().decode('utf-8')).strip()
        if PROGRAM_VERSION == last_version:
            print('Установлена последняя доступная версия программы')
            if show_updates and show_if_no_updates:
                window_last_version = PopupMsgW(window_parent, 'Установлена последняя доступная версия программы')
        else:
            print(f'Доступна новая версия: {last_version}')
            if show_updates:
                window_last_version = NewVersionAvailableW(window_parent, last_version)
    except Exception as exc:
        print(f'Ошибка: невозможно проверить наличие обновлений!\n'
              f'{exc}')
        if show_updates:
            warning(window_parent, f'Ошибка: невозможно проверить наличие обновлений!\n'
                                   f'{exc}')
    return window_last_version


# Обновить тему с 4 до 5 версии
def upgrade_theme_4_to_5(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    print(lines)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write('5\n')
        for i in range(1, 11):
            file.write(lines[i])
        file.write(lines[10])
        file.write(lines[11])
        for i in range(13, 19):
            file.write(lines[i])
        file.write(lines[13])
        file.write(lines[14])
        for i in range(19, 30):
            file.write(lines[i])


# Обновить тему старой версии до актуальной версии
def upgrade_theme(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        if first_line[0] == '4':  # Версия 4
            upgrade_theme_4_to_5(filepath)


# Загрузить дополнительные темы
def upload_themes(themes: list[str]):
    if os.listdir(ADDITIONAL_THEMES_PATH):
        print('\nЗагрузка тем...')
    for dirname in os.listdir(ADDITIONAL_THEMES_PATH):
        path = os.path.join(ADDITIONAL_THEMES_PATH, dirname)
        if not os.path.isdir(path):
            continue
        styles_filename = 'styles.txt'
        if styles_filename not in os.listdir(path):
            continue
        theme = dirname
        try:
            is_correct = True
            styles_path = os.path.join(path, styles_filename)
            with open(styles_path, 'r', encoding='utf-8') as styles_file:
                line = styles_file.readline().strip()
                theme_version = int(re.split(' |//', line)[0])  # После // идут комментарии
                if theme_version != REQUIRED_THEME_VERSION:  # Проверка версии темы
                    print(f'Не удалось загрузить тему "{theme}",\n'
                          f'  т. к. её версия не соответствует требуемой!\n'
                          f'  Актуальные темы можно загрузить здесь:\n'
                          f'  {URL_RELEASES}')
                    continue
                themes += [theme]  # Добавляем название новой темы
                for style_elem in STYLE_ELEMENTS:  # Проходимся по стилизуемым элементам
                    line = styles_file.readline().strip()
                    style = re.split(' |//', line)[0]  # После // идут комментарии
                    element = STYLES[style_elem]
                    element[theme] = style  # Добавляем новый стиль для элемента, соответствующий теме theme
                    if not style:
                        print(f'Не удалось загрузить тему "{theme}" из-за ошибки!')
                        themes.remove(theme)
                        is_correct = False
                        break
            if not is_correct:
                continue
        except Exception as exc:
            print(f'Не удалось загрузить тему "{theme}" из-за ошибки!\n'
                  f'{exc}')
        else:
            print(f'Тема "{theme}" успешно загружена')


# Загрузить пользовательскую тему
def upload_custom_theme():
    styles_filename = 'styles.txt'
    if styles_filename not in os.listdir(CUSTOM_THEME_PATH):
        create_default_custom_theme()
    styles_path = os.path.join(CUSTOM_THEME_PATH, styles_filename)
    try:
        upgrade_theme(styles_path)
        with open(styles_path, 'r', encoding='utf-8') as styles_file:
            styles_file.readline()  # Версия темы
            for style_elem in STYLE_ELEMENTS:  # Проходимся по стилизуемым элементам
                line = styles_file.readline().strip()
                style = re.split(' |//', line)[0]  # После // идут комментарии
                element = STYLES[style_elem]
                element[CUSTOM_TH] = style
                if not style:
                    create_default_custom_theme()
    except:
        create_default_custom_theme()


# Установить в качестве пользовательской темы тему по умолчанию
def create_default_custom_theme():
    styles_filename = 'styles.txt'
    styles_path = os.path.join(CUSTOM_THEME_PATH, styles_filename)
    with open(styles_path, 'w', encoding='utf-8') as styles_file:
        styles_file.write(f'{REQUIRED_THEME_VERSION}')
        for style_elem in STYLE_ELEMENTS:  # Проходимся по стилизуемым элементам
            element = STYLES[style_elem]
            style = element[DEFAULT_TH]
            element[CUSTOM_TH] = style
            styles_file.write(f'\n{style}')


# Загрузить изображения для выбранной темы
def upload_theme_img(theme: str):
    global img_ok, img_cancel, img_add, img_delete, img_edit, img_undo, img_redo, img_about, img_about_mgsp,\
        img_about_typo

    if theme == CUSTOM_TH:
        theme_dir = CUSTOM_THEME_PATH
    else:
        theme_dir = os.path.join(ADDITIONAL_THEMES_PATH, theme)

    images = [img_ok, img_cancel, img_add, img_delete, img_edit, img_undo, img_redo, img_about, img_about_mgsp,
              img_about_typo]

    for i in range(len(images)):
        file_name = f'{IMG_NAMES[i]}.png'
        if file_name in os.listdir(theme_dir):
            images[i] = os.path.join(theme_dir, file_name)
        else:
            images[i] = os.path.join(IMAGES_PATH, file_name)

    img_ok, img_cancel, img_add, img_delete, img_edit, img_undo, img_redo, img_about, img_about_mgsp,\
        img_about_typo = images


# Обновить глобальные настройки с 0 до 2 версии
def upgrade_global_settings_0_to_2():
    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write('v1\n')  # Версия глобальных настроек
        global_settings_file.write(lines[0])  # Название текущего словаря
        global_settings_file.write(lines[1])  # Уведомлять ли о выходе новых версий
        global_settings_file.write('0\n')  # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        global_settings_file.write(lines[2])  # Установленная тема

    upgrade_global_settings_1_to_2()


# Обновить глобальные настройки с 1 до 2 версии
def upgrade_global_settings_1_to_2():
    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write('v2\n')  # Версия глобальных настроек
        global_settings_file.write(lines[1])  # Название текущего словаря
        global_settings_file.write(lines[2])  # Уведомлять ли о выходе новых версий
        global_settings_file.write(lines[3])  # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        global_settings_file.write(lines[4].strip())  # Установленная тема
        global_settings_file.write('\n10')  # Размер шрифта


# Обновить глобальные настройки старой версии до актуальной версии
def upgrade_global_settings():
    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    if len(lines) == 3:  # Версия 0
        upgrade_global_settings_0_to_2()
    elif lines[0][0:2] == 'v1':  # Версия 1
        upgrade_global_settings_1_to_2()
    elif lines[0][0:2] != f'v{GLOBAL_SETTINGS_VERSION}':
        print(f'Неизвестная версия глобальных настроек: {lines[0].strip()}!\n'
              f'Проверьте наличие обновлений программы')


# Загрузить глобальные настройки (настройки программы)
def upload_global_settings():
    try:  # Открываем файл с настройками программы
        open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
            global_settings_file.write(f'v{GLOBAL_SETTINGS_VERSION}\n'
                                       f'dct\n'
                                       f'1\n'
                                       f'0\n'
                                       f'{DEFAULT_TH}\n'
                                       f'{FONTSIZE_DEF}')
    else:
        upgrade_global_settings()

    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        # Версия глобальных настроек
        global_settings_file.readline()
        # Название текущего словаря
        dct_savename = global_settings_file.readline().strip()
        # Уведомлять ли о выходе новых версий
        try:
            show_updates = int(global_settings_file.readline().strip())
        except (ValueError, TypeError):
            show_updates = 1
        # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        try:
            typo = int(global_settings_file.readline().strip())
        except (ValueError, TypeError):
            typo = 0
        # Установленная тема
        theme = global_settings_file.readline().strip()
        if theme not in THEMES:
            theme = DEFAULT_TH
        # Размер шрифта
        try:
            fontsize = int(global_settings_file.readline().strip())
        except (ValueError, TypeError):
            fontsize = FONTSIZE_DEF
    return dct_savename, show_updates, typo, theme, fontsize


# Сохранить глобальные настройки (настройки программы)
def save_global_settings(dct_savename: str, show_updates: int, typo: int, theme: str, fontsize: int):
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write(f'v{GLOBAL_SETTINGS_VERSION}\n'
                                   f'{dct_savename}\n'
                                   f'{show_updates}\n'
                                   f'{typo}\n'
                                   f'{theme}\n'
                                   f'{fontsize}')


# Сохранить название открытого словаря
def save_dct_name():
    _, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize = upload_global_settings()
    save_global_settings(_0_global_dct_savename, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize)


# Обновить локальные настройки с 0 до 3 версии
def upgrade_local_settings_0_to_3(local_settings_path: str):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v1\n')
        local_settings_file.write(lines[0])
        local_settings_file.write('\n')
        for i in range(1, len(lines)):
            local_settings_file.write(lines[i])

    upgrade_local_settings_1_to_3(local_settings_path)


# Обновить локальные настройки с 1 до 3 версии
def upgrade_local_settings_1_to_3(local_settings_path: str):
    global _0_global_special_combinations

    _, _, _0_global_special_combinations, _ = upload_local_settings(_0_global_dct_savename, upgrade=False)

    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v2\n')
        local_settings_file.write(lines[1])
        local_settings_file.write(lines[2])
        for i in range(3, len(lines)):
            if i % 2 == 1:
                local_settings_file.write(encode_special_combinations(lines[i]))
            else:
                values = lines[i].strip().split(CATEGORY_SEPARATOR)
                values = [encode_special_combinations(i) for i in values]
                local_settings_file.write(decode_tpl(values) + '\n')

    upgrade_local_settings_2_to_3(local_settings_path)


# Обновить локальные настройки со 2 до 3 версии
def upgrade_local_settings_2_to_3(local_settings_path: str):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v3\n')
        local_settings_file.write(lines[1])
        local_settings_file.write(lines[2])
        local_settings_file.write('1\n')
        for i in range(3, len(lines)):
            local_settings_file.write(lines[i])


# Обновить локальные настройки старой версии до актуальной версии
def upgrade_local_settings(local_settings_path: str):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        first_line = local_settings_file.readline()
        if first_line[0] != 'v':  # Версия 0
            upgrade_local_settings_0_to_3(local_settings_path)
        elif first_line[0:2] == 'v1':  # Версия 1
            upgrade_local_settings_1_to_3(local_settings_path)
        elif first_line[0:2] == 'v2':  # Версия 2
            upgrade_local_settings_2_to_3(local_settings_path)
        elif first_line[0:2] != f'v{LOCAL_SETTINGS_VERSION}':
            print(f'Неизвестная версия локальных настроек: {first_line.strip()}!\n'
                  f'Проверьте наличие обновлений программы')


# Загрузить локальные настройки (настройки словаря)
def upload_local_settings(savename: str, upgrade=True):
    filename = dct_filename(savename)
    local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    categories = {}
    special_combinations = {}
    try:
        open(local_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
            local_settings_file.write(f'v{LOCAL_SETTINGS_VERSION}\n'  # Версия локальных настроек
                                      f'67\n'  # МППУ
                                      f'aäAÄoöOÖuüUÜsßSẞ\n'  # Специальные комбинации
                                      f'1\n'  # Учитывать ли регистр букв при учёбе
                                      f'Число\n'
                                      f'ед.ч.{CATEGORY_SEPARATOR}мн.ч.\n'
                                      f'Род\n'
                                      f'м.р.{CATEGORY_SEPARATOR}ж.р.{CATEGORY_SEPARATOR}ср.р.\n'
                                      f'Падеж\n'
                                      f'им.п.{CATEGORY_SEPARATOR}род.п.{CATEGORY_SEPARATOR}дат.п.{CATEGORY_SEPARATOR}вин.п.\n'
                                      f'Лицо\n'
                                      f'1 л.{CATEGORY_SEPARATOR}2 л.{CATEGORY_SEPARATOR}3 л.\n'
                                      f'Время\n'
                                      f'пр.вр.{CATEGORY_SEPARATOR}н.вр.{CATEGORY_SEPARATOR}буд.вр.')
    else:
        if upgrade:
            upgrade_local_settings(local_settings_path)

    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        # Версия
        local_settings_file.readline()
        # МППУ
        try:
            min_good_score_perc = int(local_settings_file.readline().strip())
        except (ValueError, TypeError):
            min_good_score_perc = 67
        # Специальные комбинации
        line_special_combinations = local_settings_file.readline()
        for i in range(len(line_special_combinations) // 2):
            special_combinations[line_special_combinations[2 * i]] = line_special_combinations[2 * i + 1]
        # Учитывать ли регистр букв при учёбе
        try:
            check_register = int(local_settings_file.readline().strip())
        except (ValueError, TypeError):
            check_register = 1
        # Словоформы
        while True:
            key = local_settings_file.readline().strip()
            if not key:
                break
            value = local_settings_file.readline().strip().split(CATEGORY_SEPARATOR)
            categories[key] = value
    return min_good_score_perc, categories, special_combinations, check_register


# Сохранить локальные настройки (настройки словаря)
def save_local_settings(min_good_score_perc: int, check_register: int, categories: dict[str, list[str]], filename: str):
    local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write(f'v{LOCAL_SETTINGS_VERSION}\n')
        local_settings_file.write(f'{min_good_score_perc}\n')
        for key in _0_global_special_combinations:
            val = _0_global_special_combinations[key]
            local_settings_file.write(f'{key}{val}')
        local_settings_file.write('\n')
        local_settings_file.write(f'{check_register}\n')
        for key in categories.keys():
            local_settings_file.write(f'{key}\n')
            local_settings_file.write(categories[key][0])
            for i in range(1, len(categories[key])):
                local_settings_file.write(f'{CATEGORY_SEPARATOR}{categories[key][i]}')
            local_settings_file.write('\n')


# Предложить сохранение настроек, если есть изменения
def save_settings_if_has_changes(window_parent):
    window_dia = PopupDialogueW(window_parent, 'Хотите сохранить изменения настроек?', 'Да', 'Нет')
    answer = window_dia.open()
    if answer:
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th,
                             _0_global_fontsize)
        save_local_settings(_0_global_min_good_score_perc, _0_global_check_register, _0_global_categories,
                            dct_filename(_0_global_dct_savename))
        PopupMsgW(window_parent, 'Настройки успешно сохранены').open()
        print('\nНастройки успешно сохранены')


# Обновить сохранение словаря с 0 до 2 версии
def upgrade_dct_save_0_to_2(path: str):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save_tmp.write('v1\n')
            while True:
                line = dct_save.readline()
                if not line:
                    break
                dct_save_tmp.write(line)
    with open(TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if TMP_FN in os.listdir(RESOURCES_PATH):
        os.remove(TMP_PATH)

    upgrade_dct_save_1_to_2(path)


# Обновить сохранение словаря с 1 до 2 версии
def upgrade_dct_save_1_to_2(path: str):
    global _0_global_special_combinations

    _, _, _0_global_special_combinations, _ = upload_local_settings(_0_global_dct_savename)

    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v2\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(encode_special_combinations(line))
                    line = dct_save.readline()
                    dct_save_tmp.write(line.replace('#', ':'))
                    line = dct_save.readline()
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == 't':
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == 'd':
                    dct_save_tmp.write('n' + encode_special_combinations(line[1:]))
                elif line[0] == 'f':
                    old_frm_key = encode_tpl(line[1:])
                    new_frm_key = [encode_special_combinations(i) for i in old_frm_key]
                    dct_save_tmp.write('f' + decode_tpl(new_frm_key))
                    line = dct_save.readline()
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == '*':
                    dct_save_tmp.write('*\n')
    with open(TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if TMP_FN in os.listdir(RESOURCES_PATH):
        os.remove(TMP_PATH)


# Обновить сохранение словаря старой версии до актуальной версии
def upgrade_dct_save(path: str):
    with open(path, 'r', encoding='utf-8') as dct_save:
        first_line = dct_save.readline()
    if first_line == '':  # Если сохранение пустое
        return
    if first_line[0] == 'w':  # Версия 0
        upgrade_dct_save_0_to_2(path)
    elif first_line[0:2] == 'v1':  # Версия 1
        upgrade_dct_save_1_to_2(path)
    elif first_line[0:2] != f'v{SAVES_VERSION}':
        print(f'Неизвестная версия словаря: {first_line.strip()}!\n'
              f'Проверьте наличие обновлений программы')


# Загрузить словарь (с обновлением и обработкой исключений)
def upload_dct(window_parent, dct: Dictionary, savename: str, btn_close_text: str):
    filename = dct_filename(savename)
    filepath = os.path.join(SAVES_PATH, filename)
    try:
        upgrade_dct_save(filepath)  # Если требуется, сохранение обновляется
        dct.read(filepath)  # Загрузка словаря
    except FileNotFoundError:  # Если сохранение не найдено, то создаётся пустой словарь
        print(f'\nСловарь "{savename}" не найден!')
        open(filepath, 'w', encoding='utf-8').write(f'v{SAVES_VERSION}\n')
        dct.read(filepath)
        print('Создан и загружен пустой словарь')
        return savename
    except Exception as exc:  # Если сохранение повреждено, то предлагается загрузить другое
        print(f'\nФайл со словарём "{savename}" повреждён или некорректен!'
              f'\n{exc}')
        while True:
            window_dia = PopupDialogueW(window_parent, f'Файл со словарём "{savename}" повреждён или некорректен!\n'
                                                       f'Хотите открыть другой словарь?',
                                        'Да', btn_close_text, set_enter_on_btn='none', title='Warning')
            answer = window_dia.open()
            if answer:
                window_entry = PopupEntryW(window_parent, 'Введите название словаря\n'
                                                          '(если он ещё не существует, то будет создан пустой словарь)',
                                           check_answer_function=lambda wnd, val:
                                           check_not_void(wnd, val,
                                                          'Название словаря должно содержать хотя бы один символ!'))
                closed, other_savename = window_entry.open()
                if closed:
                    continue
                save_dct_name()
                dct = Dictionary()
                return upload_dct(window_parent, dct, other_savename, btn_close_text)
            else:
                return None
    else:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'\nСловарь "{savename}" успешно открыт')
        return savename


# Создать и загрузить пустой словарь
def create_dct(dct: Dictionary, savename: str):
    filename = dct_filename(savename)
    filepath = os.path.join(SAVES_PATH, filename)
    open(filepath, 'w', encoding='utf-8').write(f'v{SAVES_VERSION}\n')
    dct.read(filepath)
    print(f'\nСловарь "{savename}" успешно создан и открыт')
    return upload_local_settings(savename)


# Сохранить словарь
def save_dct(dct: Dictionary, filename: str):
    filepath = os.path.join(SAVES_PATH, filename)
    dct.save(filepath)


# Предложить сохранение словаря, если есть изменения
def save_dct_if_has_progress(window_parent, dct: Dictionary, filename: str, has_progress: bool):
    if has_progress:
        window_dia = PopupDialogueW(window_parent, 'Хотите сохранить свой прогресс?', 'Да', 'Нет')
        answer = window_dia.open()
        if answer:
            save_dct(dct, filename)
            PopupMsgW(window_parent, 'Прогресс успешно сохранён').open()
            print('\nПрогресс успешно сохранён')


# Экспортировать словарь
def dct_export(savename: str, dst_path: str):
    filename = dct_filename(savename)

    dst_dir = os.path.join(dst_path, savename)
    src_save_path = os.path.join(SAVES_PATH, filename)
    dst_save_path = os.path.join(dst_dir, 'save.txt')
    src_local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    dst_local_settings_path = os.path.join(dst_dir, 'local_settings.txt')

    os.mkdir(dst_dir)
    shutil.copyfile(src_save_path, dst_save_path)
    shutil.copyfile(src_local_settings_path, dst_local_settings_path)


# Импортировать словарь
def dct_import(window_parent, savename: str, src_path: str):
    save_filename = 'save.txt'
    local_settings_filename = 'local_settings.txt'

    filename = dct_filename(savename)

    src_save_path = os.path.join(src_path, save_filename)
    dst_save_path = os.path.join(SAVES_PATH, filename)
    src_local_settings_path = os.path.join(src_path, local_settings_filename)
    dst_local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)

    if save_filename not in os.listdir(src_save_path):
        warning(window_parent, f'Ошибка импорта сохранения!\n'
                               f'Отсутствует файл "{save_filename}"')
        return
    if local_settings_filename not in os.listdir(src_local_settings_path):
        warning(window_parent, f'Ошибка импорта сохранения!\n'
                               f'Отсутствует файл "{local_settings_filename}"')
        return
    
    shutil.copyfile(src_save_path, dst_save_path)
    shutil.copyfile(src_local_settings_path, dst_local_settings_path)


""" Графический интерфейс - вспомогательные функции """


# Вывести текст на виджет
def outp(output_widget: tk.Entry | ttk.Entry | tk.Text, text='', end='\n', mode=tk.END):
    output_widget.insert(mode, f'{text}{end}')


# Вывести сообщение с предупреждением
def warning(window_parent, msg: str):
    PopupMsgW(window_parent, msg, title='Warning').open()


# Выключить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


# Включить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_enable(btn: ttk.Button, command, style='Default'):
    btn.configure(command=command, style=f'{style}.TButton')


""" Графический интерфейс - функции валидации """


# Ввод только целых чисел от 0 до max_val
def validate_int_max(value: str, max_val: int):
    return value == '' or value.isnumeric() and int(value) <= max_val


# Ввод только целых чисел от 0 до 100
def validate_percent(value: str):
    return validate_int_max(value, 100)


# Валидация ключа специальной комбинации
def validate_special_combination_key(value: str):
    return len(value) <= 1 and value != SPECIAL_COMBINATION_OPENING_SYMBOL


# Валидация значения специальной комбинации
def validate_special_combination_val(value: str):
    return len(value) <= 1


""" Графический интерфейс - виджеты """


# Прокручиваемый фрейм
class ScrollFrame(tk.Frame):
    def __init__(self, parent, height: int, width: int):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg=ST_BG_FIELDS[th], bd=0, highlightthickness=0, height=height, width=width)
        # {
        self.frame_canvas = ttk.Frame(self.canvas, style='Default.TFrame')
        # }
        self.scrollbar_y = ttk.Scrollbar(self, command=self.canvas.yview, style='Vertical.TScrollbar')

        self.canvas.pack(     side='left',  fill='both', expand=True)
        self.scrollbar_y.pack(side='right', fill='y')

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.canvas_window = self.canvas.create_window((4, 4), window=self.frame_canvas, anchor='nw',
                                                       tags='self.frame_canvas')

        # Когда размер фрейма изменяется, соответственно изменяется и область прокрутки
        self.frame_canvas.bind('<Configure>', self.on_frame_configure)
        # Когда размер холста изменяется, соответственно изменяется и область окна
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Привязать колёсико мышки, когда курсор попадает на элемент управления
        self.frame_canvas.bind('<Enter>', self.on_enter)
        # Отвязать колёсико мышки, когда курсор покидает элемент управления
        self.frame_canvas.bind('<Leave>', self.on_leave)

        self.on_frame_configure(None)

    # Когда размер фрейма изменяется, соответственно изменяется и область прокрутки
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    # Когда размер холста изменяется, соответственно изменяется и область окна
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # Обработка событий колёсика мышки
    def on_mouse_wheel(self, event):
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

    # Привязать колёсико мышки, когда курсор попадает на элемент управления
    def on_enter(self, event):
        if platform.system() == 'Linux':
            self.canvas.bind_all('<Button-4>', self.on_mouse_wheel)
            self.canvas.bind_all('<Button-5>', self.on_mouse_wheel)
        else:
            self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)

    # Отвязать колёсико мышки, когда курсор покидает элемент управления
    def on_leave(self, event):
        if platform.system() == 'Linux':
            self.canvas.unbind_all('<Button-4>')
            self.canvas.unbind_all('<Button-5>')
        else:
            self.canvas.unbind_all('<MouseWheel>')


""" Графический интерфейс - всплывающие окна """


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg: str, btn_text='Ясно', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, align_left=False), justify='center',
                                 style='Default.TLabel')
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Default.TButton')

        self.lbl_msg.grid(row=0, column=0, padx=6, pady=4)
        self.btn_ok.grid( row=1, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Вы уверены?', btn_left_text='Да', btn_right_text='Отмена',
                 st_left: typing.Literal['Default', 'Yes', 'No'] = 'Yes',
                 st_right: typing.Literal['Default', 'Yes', 'No'] = 'No',  # Стили левой и правой кнопок
                 val_left: typing.Any = True,  # Значение, возвращаемое при нажатии на левую кнопку
                 val_right: typing.Any = False,  # Значение, возвращаемое при нажатии на правую кнопку
                 val_on_close: typing.Any = False,  # Значение, возвращаемое при закрытии окна крестиком
                 set_enter_on_btn: typing.Literal['left', 'right', 'none'] = 'left',  # Какая кнопка срабатывает при нажатии кнопки enter
                 title=PROGRAM_NAME):
        ALLOWED_ST_VALUES = ['Default', 'Yes', 'No']  # Проверка корректности параметров
        assert st_left in ALLOWED_ST_VALUES, f'Bad value: st_left\n' \
                                             f'Allowed values: {ALLOWED_ST_VALUES}'
        assert st_right in ALLOWED_ST_VALUES, f'Bad value: st_right\n' \
                                              f'Allowed values: {ALLOWED_ST_VALUES}'
        ALLOWED_FOCUS_VALUES = ['left', 'right', 'none']  # Проверка корректности параметров
        assert set_enter_on_btn in ALLOWED_FOCUS_VALUES, f'Bad value: set_enter_on_btn\n' \
                                                         f'Allowed values: {ALLOWED_FOCUS_VALUES}'

        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.set_enter_on_btn = set_enter_on_btn
        self.answer = val_on_close  # Значение, возвращаемое методом self.open
        self.val_left = val_left
        self.val_right = val_right

        self.st_left = f'{st_left}.TButton'
        self.st_right = f'{st_right}.TButton'

        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, align_left=False), justify='center',
                                 style='Default.TLabel')
        self.btn_left = ttk.Button(self, text=btn_left_text, command=self.left, takefocus=False, style=self.st_left)
        self.btn_right = ttk.Button(self, text=btn_right_text, command=self.right, takefocus=False, style=self.st_right)

        self.lbl_msg.grid(  row=0, columnspan=2, padx=6,       pady=4)
        self.btn_left.grid( row=1, column=0,     padx=(6, 10), pady=4, sticky='E')
        self.btn_right.grid(row=1, column=1,     padx=(10, 6), pady=4, sticky='W')

    # Нажатие на левую кнопку
    def left(self):
        self.answer = self.val_left
        self.destroy()

    # Нажатие на правую кнопку
    def right(self):
        self.answer = self.val_right
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        if self.set_enter_on_btn == 'left':
            self.bind('<Return>', lambda event=None: self.btn_left.invoke())
            self.bind('<Escape>', lambda event=None: self.btn_right.invoke())
        elif self.set_enter_on_btn == 'right':
            self.bind('<Return>', lambda event=None: self.btn_right.invoke())
            self.bind('<Escape>', lambda event=None: self.btn_left.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Всплывающее окно с полем ввода
class PopupEntryW(tk.Toplevel):
    def __init__(self, parent, msg='Введите строку', btn_text='Подтвердить', entry_width=30, default_value='',
                 check_answer_function=None, if_correct_function=None, if_incorrect_function=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.check_answer_function = check_answer_function  # Функция, проверяющая корректность ответа
        self.if_correct_function = if_correct_function  # Функция, вызываемая при корректном ответе
        self.if_incorrect_function = if_incorrect_function  # Функция, вызываемая при некорректном ответе
        self.closed = True  # Закрыто ли окно крестиком

        self.var_text = tk.StringVar(value=default_value)

        self.lbl_msg = ttk.Label(self, text=split_text(f'{msg}:', 45, align_left=False), justify='center',
                                 style='Default.TLabel')
        self.entry_inp = ttk.Entry(self, textvariable=self.var_text, width=entry_width, style='Default.TEntry')
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(  row=0, padx=6, pady=(6, 3))
        self.entry_inp.grid(row=1, padx=6, pady=(0, 6))
        self.btn_ok.grid(   row=2, padx=6, pady=(0, 6))

    # Нажатие на кнопку
    def ok(self):
        if self.check_answer_function:
            is_correct = self.check_answer_function(self, self.var_text.get())
            if is_correct:
                if self.if_correct_function:
                    self.if_correct_function()
            else:
                if self.if_incorrect_function:
                    self.if_incorrect_function()
                return
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_inp.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_text.get()


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values: list[str] | tuple[str, ...], msg='Выберите один из вариантов',
                 btn_text='Подтвердить', combo_width=20, default_value=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        self.var_answer = tk.StringVar(value=default_value)

        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, align_left=False), justify='center',
                                 style='Default.TLabel')
        self.combo_vals = ttk.Combobox(self, textvariable=self.var_answer, values=values, width=combo_width,
                                       font='TkFixedFont', state='readonly', style='Default.TCombobox')
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(   row=0, padx=6, pady=(4, 1))
        self.combo_vals.grid(row=1, padx=6, pady=1)
        self.btn_ok.grid(    row=2, padx=6, pady=4)

        self.option_add('*TCombobox*Listbox*Font', 'TkFixedFont')  # Моноширинный шрифт в списке combobox

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_answer.get()


# Всплывающее окно с изображением
class PopupImgW(tk.Toplevel):
    def __init__(self, parent, img_name: str, msg: str, btn_text='Ясно', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        try:
            self.img = tk.PhotoImage(file=img_name)
        except:
            self.lbl_img = ttk.Label(self, text='[!!!] Изображение не найдено [!!!]\n'
                                                'Недостающие изображения можно скачать здесь:',
                                     justify='center', style='Default.TLabel')

            self.txt_img_not_found = tk.Text(self, height=1, width=47, relief='sunken', borderwidth=1,
                                             font=('StdFont', _0_global_fontsize), bg=ST_BG[th], fg=ST_FG[th],
                                             selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                             highlightbackground=ST_BORDERCOLOR[th])
            self.txt_img_not_found.insert(tk.END, f'{URL_RELEASES}')
            self.txt_img_not_found['state'] = 'disabled'
            self.txt_img_not_found.grid(row=1, column=0, padx=6, pady=(0, 16))
        else:
            self.lbl_img = ttk.Label(self, image=self.img, style='Default.TLabel')
        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, align_left=False), justify='center',
                                 style='Default.TLabel')
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Default.TButton')

        self.lbl_img.grid(row=0, column=0, padx=6, pady=(4, 0))
        self.lbl_msg.grid(row=2, column=0, padx=6, pady=0)
        self.btn_ok.grid( row=3, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed


# Окно ввода специальной комбинации
class EnterSpecialCombinationW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        self.var_key = tk.StringVar()
        self.var_val = tk.StringVar()

        self.vcmd_key = (self.register(validate_special_combination_key), '%P')
        self.vcmd_val = (self.register(validate_special_combination_val), '%P')

        self.lbl_msg = ttk.Label(self, text='Задайте комбинацию', justify='center', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_1 = ttk.Label(self.frame_main, text=SPECIAL_COMBINATION_OPENING_SYMBOL,
                               justify='right', style='Default.TLabel')
        self.entry_key = ttk.Entry(self.frame_main, textvariable=self.var_key, width=2, justify='right',
                                   validate='key', validatecommand=self.vcmd_key, style='Default.TEntry')
        self.lbl_2 = ttk.Label(self.frame_main, text='->', justify='center', style='Default.TLabel')
        self.entry_val = ttk.Entry(self.frame_main, textvariable=self.var_val, width=2,
                                   validate='key', validatecommand=self.vcmd_val, style='Default.TEntry')
        # }
        self.btn_ok = ttk.Button(self, text='Подтвердить', command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(   row=0, padx=6, pady=(6, 3))
        self.frame_main.grid(row=1, padx=6, pady=0)
        # {
        self.lbl_1.grid(    row=0, column=0, padx=0, pady=0)
        self.entry_key.grid(row=0, column=1, padx=0, pady=0)
        self.lbl_2.grid(    row=0, column=2, padx=2, pady=0)
        self.entry_val.grid(row=0, column=3, padx=0, pady=0)
        # }
        self.btn_ok.grid(row=2, padx=6, pady=6)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_key.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_key.get(), self.var_val.get()


# Окно создания шаблона словоформы
class AddFormW(tk.Toplevel):
    def __init__(self, parent, key: tuple[str, int], combo_width=20):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком
        self.categories = list(_0_global_categories.keys())  # Список категорий
        self.ctg_values = list(_0_global_categories[self.categories[0]])  # Список значений выбранной категории
        self.template = []  # Шаблон словоформы
        for _ in range(len(self.categories)):
            self.template += ['']
        self.void_template = self.template.copy()  # Пустой шаблон (для сравнения на пустоту)
        self.key = key

        self.var_ctg = tk.StringVar(value=self.categories[0])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.var_template = tk.StringVar(value='Текущий шаблон словоформы: ""')
        self.var_form = tk.StringVar(value=_0_global_dct.d[self.key].wrd)

        self.vcmd_ctg = (self.register(lambda value: self.refresh_vals()), '%P')

        self.lbl_choose_ctg = ttk.Label(self, text='Выберите категорию:', justify='center', style='Default.TLabel')
        self.combo_ctg = ttk.Combobox(self, textvariable=self.var_ctg, values=self.categories, width=combo_width,
                                      font='TkFixedFont', validate='focusin', validatecommand=self.vcmd_ctg,
                                      state='readonly', style='Default.TCombobox')
        self.lbl_choose_val = ttk.Label(self, text='Задайте значение категории:', justify='center',
                                        style='Default.TLabel')
        self.frame_val = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.combo_val = ttk.Combobox(self.frame_val, textvariable=self.var_val, values=self.ctg_values,
                                      width=width(self.ctg_values, 5, 100),
                                      font='TkFixedFont', state='readonly', style='Default.TCombobox')
        try:
            self.img_choose = tk.PhotoImage(file=img_ok)
        except:
            self.btn_choose = ttk.Button(self.frame_val, text='Задать значение', command=self.choose,
                                         takefocus=False, style='Default.TButton')
        else:
            self.btn_choose = ttk.Button(self.frame_val, image=self.img_choose, command=self.choose,
                                         takefocus=False, style='Image.TButton')
            self.tip_btn_choose = ttip.Hovertip(self.btn_choose, 'Задать значение', hover_delay=500)
        try:
            self.img_none = tk.PhotoImage(file=img_cancel)
        except:
            self.btn_none = ttk.Button(self.frame_val, text='Не указывать/неприменимо', command=self.set_none,
                                       takefocus=False, style='Default.TButton')
        else:
            self.btn_none = ttk.Button(self.frame_val, image=self.img_none, command=self.set_none,
                                       takefocus=False, style='Image.TButton')
            self.tip_btn_none = ttip.Hovertip(self.btn_none, 'Не указывать/неприменимо', hover_delay=500)
        # }
        self.lbl_template = ttk.Label(self, textvariable=self.var_template, justify='center', style='Default.TLabel')
        self.frame_form = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_form = ttk.Label(self.frame_form, text='Форма:', justify='left', style='Default.TLabel')
        self.entry_form = ttk.Entry(self.frame_form, textvariable=self.var_form, style='Default.TEntry')
        # }
        self.btn_save = ttk.Button(self, text='Добавить', command=self.save, takefocus=False, style='Default.TButton')

        self.lbl_choose_ctg.grid(row=0, column=0, padx=(6, 1), pady=(6, 1), sticky='E')
        self.combo_ctg.grid(     row=0, column=1, padx=(0, 6), pady=(6, 1), sticky='W')
        self.lbl_choose_val.grid(row=1, column=0, padx=(6, 1), pady=1,      sticky='E')
        self.frame_val.grid(     row=1, column=1, padx=(0, 6), pady=1,      sticky='W')
        # {
        self.combo_val.grid( row=0, column=0, padx=0,      pady=0)
        self.btn_choose.grid(row=0, column=1, padx=(3, 0), pady=0)
        self.btn_none.grid(  row=0, column=2, padx=0,      pady=0)
        # }
        self.lbl_template.grid(row=2, columnspan=2, padx=6, pady=1)
        self.frame_form.grid(  row=3, columnspan=2, padx=6, pady=6)
        # {
        self.lbl_form.grid(  row=0, column=0, padx=(0, 1), pady=0, sticky='E')
        self.entry_form.grid(row=0, column=1, padx=0,      pady=0, sticky='W')
        # }
        self.btn_save.grid(row=4, columnspan=2, padx=6, pady=6)

        self.option_add('*TCombobox*Listbox*Font', 'TkFixedFont')  # Моноширинный шрифт в списке combobox

        btn_disable(self.btn_save)

    # Выбрать категорию и задать ей значение
    def choose(self):
        ctg = self.var_ctg.get()
        if ctg == '':
            return
        index = self.categories.index(ctg)

        val = self.var_val.get()
        if val == '':
            return
        self.template[index] = val

        self.var_template.set(f'Текущий шаблон словоформы: "{tpl(self.template)}"')

        if self.template == self.void_template:  # Пока шаблон пустой, нельзя нажать кнопку
            btn_disable(self.btn_save)
        else:
            btn_enable(self.btn_save, self.save)

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.template)):
            if self.template[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_vals()

    # Не указывать значение категории
    def set_none(self):
        ctg = self.var_ctg.get()
        if ctg == '':
            return
        index = self.categories.index(ctg)

        self.template[index] = ''

        self.var_template.set(f'Текущий шаблон словоформы: "{tpl(self.template)}"')

        if self.template == self.void_template:  # Пока шаблон пустой, нельзя нажать кнопку
            btn_disable(self.btn_save)
        else:
            btn_enable(self.btn_save, self.save)

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.template)):
            if self.template[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_vals()

    # Сохранить словоформу
    def save(self):
        if tuple(self.template) in _0_global_dct.d[self.key].forms.keys():
            warning(self, f'У слова "{key_to_wrd(self.key)}" уже есть форма с таким шаблоном!')
            return
        if self.var_form.get() == '':
            warning(self, 'Словоформа должна содержать хотя бы один символ!')
            return
        self.closed = False
        self.destroy()

    # Обновить combobox со значениями категории после выбора категории
    def refresh_vals(self):
        self.ctg_values = list(_0_global_categories[self.var_ctg.get()])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.combo_val.configure(textvariable=self.var_val, values=self.ctg_values,
                                 width=width(self.ctg_values, 5, 100))
        return True

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_form.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_choose.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        if self.closed:
            return None, None
        if self.template == self.void_template:
            return None, None
        if tuple(self.template) in _0_global_dct.d[self.key].forms.keys():
            return None, None
        return tuple(self.template), self.var_form.get()


""" Графический интерфейс - второстепенные окна """


# Окно выбора режима перед изучением слов
class ChooseLearnModeW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Learn')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.res = None

        self.var_order = tk.StringVar(value=VALUES_LEARN_METHOD[0])  # Метод учёбы
        self.var_forms = tk.BooleanVar(value=True)  # Со всеми ли словоформами
        self.var_words = tk.StringVar(value=VALUES_LEARN_WORDS[0])  # Способ подбора слов

        self.lbl_header = ttk.Label(self, text='Выберите способ учёбы', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_order = ttk.Label(self.frame_main, text='Метод:', style='Default.TLabel')
        self.combo_order = ttk.Combobox(self.frame_main, textvariable=self.var_order, values=VALUES_LEARN_METHOD,
                                        validate='focusin', width=30, state='readonly', style='Default.TCombobox')
        self.lbl_forms = ttk.Label(self.frame_main, text='Все словоформы:', style='Default.TLabel')
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, style='Default.TCheckbutton')
        self.lbl_words = ttk.Label(self.frame_main, text='Подбор слов:', style='Default.TLabel')
        self.combo_words = ttk.Combobox(self.frame_main, textvariable=self.var_words, values=VALUES_LEARN_WORDS,
                                        width=30, state='readonly', style='Default.TCombobox')
        # }
        self.btn_start = ttk.Button(self, text='Учить', command=self.start, takefocus=False, style='Default.TButton')

        self.lbl_header.grid(row=0, column=0, padx=6, pady=(6, 3))
        self.frame_main.grid(row=1, column=0, padx=6, pady=(0, 3))
        # {
        self.lbl_order.grid(  row=1, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.combo_order.grid(row=1, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_forms.grid(  row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.check_forms.grid(row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_words.grid(  row=3, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.combo_words.grid(row=3, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.btn_start.grid(row=2, column=0, padx=6, pady=(0, 6))

        # При выборе второго метода учёбы нельзя добавить словоформы
        def validate_order_and_forms(value: str):
            if value == VALUES_LEARN_METHOD[1]:
                self.check_forms['state'] = 'disabled'
            else:
                self.check_forms['state'] = 'normal'
            return True

        self.vcmd_order = (self.register(validate_order_and_forms), '%P')
        self.combo_order['validatecommand'] = self.vcmd_order

    # Начать учить слова
    def start(self):
        order = self.var_order.get()
        forms = self.var_forms.get()
        words = self.var_words.get()
        self.res = (order, forms, words)
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_start.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.res


# Окно с сообщением о неверном ответе
class IncorrectAnswerW(tk.Toplevel):
    def __init__(self, parent, user_answer: str, correct_answer: str, with_typo: bool):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Incorrect answer')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.with_typo = with_typo
        self.answer = 'no'  # Значение, возвращаемое методом self.open

        self.lbl_msg = ttk.Label(self, text=split_text(f'Неверно.\n'
                                                       f'Ваш ответ: {user_answer}\n'
                                                       f'Правильный ответ: {correct_answer}\n'
                                                       f'Хотите добавить слово в избранное?',
                                                       45, 5, align_left=False),
                                 justify='center', style='Default.TLabel')
        self.btn_yes = ttk.Button(self, text='Да', command=self.yes, takefocus=False, style='Yes.TButton')
        self.btn_no = ttk.Button(self, text='Нет', command=self.no, takefocus=False, style='No.TButton')
        self.btn_typo = ttk.Button(self, text='Просто опечатка', command=self.typo,
                                   takefocus=False, style='Default.TButton')

        if with_typo:
            self.lbl_msg.grid( row=0, column=0, columnspan=3, padx=6, pady=4)
            self.btn_yes.grid( row=1, column=0,               padx=6, pady=4, sticky='E')
            self.btn_no.grid(  row=1, column=1,               padx=6, pady=4)
            self.btn_typo.grid(row=1, column=2,               padx=6, pady=4, sticky='W')

            self.tip_btn_notes = ttip.Hovertip(self.btn_typo, 'Срабатывает при нажатии на Tab', hover_delay=700)
        else:
            self.lbl_msg.grid(row=0, column=0, columnspan=2, padx=6, pady=4)
            self.btn_yes.grid(row=1, column=0,               padx=6, pady=4, sticky='E')
            self.btn_no.grid( row=1, column=1,               padx=6, pady=4, sticky='W')

    # Нажатие на кнопку "Да"
    def yes(self):
        self.answer = 'yes'
        self.destroy()

    # Нажатие на кнопку "Нет"
    def no(self):
        self.answer = 'no'
        self.destroy()

    # Нажатие на кнопку "Опечатка"
    def typo(self):
        self.answer = 'typo'
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_yes.invoke())
        self.bind('<Escape>', lambda event=None: self.btn_no.invoke())
        if self.with_typo:
            self.bind('<Tab>', lambda event=None: self.btn_typo.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Окно вывода похожих статей для редактирования, если нет точного совпадения
class ParticularMatchesW(tk.Toplevel):
    def __init__(self, parent, query: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - There is no such entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.query = query

        self.lbl_header = ttk.Label(self, text=f'Слово "{self.query}" отсутствует в словаре\n'
                                               f'Возможно вы искали:',
                                    justify='center', style='Default.TLabel')
        self.lbl_wrd = ttk.Label(self, text=f'Слова, содержащие "{self.query}"', justify='center',
                                 style='Default.TLabel')
        self.scrolled_frame_wrd = ScrollFrame(self, 500, 404)
        # {
        self.widgets_wrd = []
        # }
        self.lbl_tr = ttk.Label(self, text=f'Переводы, содержащие "{self.query}"', justify='center',
                                style='Default.TLabel')
        self.scrolled_frame_tr = ScrollFrame(self, 500, 404)
        # {
        self.widgets_tr = []
        # }

        self.lbl_header.grid(        row=0, column=0, columnspan=2, padx=6,      pady=(6, 3))
        self.lbl_wrd.grid(           row=1, column=0,               padx=(6, 3), pady=(0, 3))
        self.lbl_tr.grid(            row=1, column=1,               padx=(3, 6), pady=(0, 3))
        self.scrolled_frame_wrd.grid(row=2, column=0,               padx=6,      pady=(0, 6))
        self.scrolled_frame_tr.grid( row=2, column=1,               padx=6,      pady=(0, 6))

        self.print()

    # Изменить статью
    def edit_note(self, key):
        EditW(self, key).open()

        self.destroy()

    # Вывод статей
    def print(self):
        self.search_wrd()  # Поиск статей по слову
        self.search_tr()  # Поиск статей по переводу

    # Поиск статей по слову
    def search_wrd(self):
        # Искомое слово
        query = encode_special_combinations(self.query)

        # Частичное совпадение
        self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                       text=split_text('Частичное совпадение:', 50, 0), style='Flat.TLabel')]
        particular_matches = _0_global_dct.get_words_with_content(query)
        if particular_matches:
            for (key, text) in particular_matches:
                self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                                text=split_text(text, 50, 5),
                                                command=lambda key=key: self.edit_note(key),
                                                takefocus=False, style='Flat.TButton')]
        else:
            self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                           text=split_text('Частичных совпадений не найдено', 50, 0),
                                           style='Flat.TLabel')]

        # Расположение виджетов
        for i in range(len(self.widgets_wrd)):
            self.widgets_wrd[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

    # Поиск статей по переводу
    def search_tr(self):
        # Искомый перевод
        query = encode_special_combinations(self.query)

        # Полное совпадение
        self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                      text=split_text('Полное совпадение:', 50, 0),
                                      style='Flat.TLabel')]
        count = 0
        for key in _0_global_dct.d.keys():
            entry = _0_global_dct.d[key]
            if query in entry.tr:
                self.widgets_tr += [ttk.Button(self.scrolled_frame_tr.frame_canvas,
                                               text=entry.print_all(50, 13),
                                               command=lambda key=key: self.edit_note(key),
                                               takefocus=False, style='Flat.TButton')]
                count += 1
        if count == 0:
            self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                          text=split_text(f'Слово с переводом "{query}" отсутствует в словаре',
                                                          50, 0),
                                          style='Flat.TLabel')]

        # Частичное совпадение
        self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                      text=split_text('\nЧастичное совпадение:', 50, 0), style='Flat.TLabel')]
        particular_matches = _0_global_dct.get_translations_with_content(query)
        if particular_matches:
            for (key, text) in particular_matches:
                self.widgets_tr += [ttk.Button(self.scrolled_frame_tr.frame_canvas,
                                               text=split_text(text, 50, 5),
                                               command=lambda key=key: self.edit_note(key),
                                               takefocus=False, style='Flat.TButton')]
        else:
            self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                          text=split_text('Частичных совпадений не найдено', 50, 0),
                                          style='Flat.TLabel')]

        # Расположение виджетов
        for i in range(len(self.widgets_tr)):
            self.widgets_tr[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_tr.canvas.yview_moveto(0.0)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseOneOfSimilarNotesW(tk.Toplevel):
    def __init__(self, parent, query: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Similar')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.search_wrd = query
        self.answer = None

        self.lbl_header = ttk.Label(self, text='Выберите одну из статей', justify='center', style='Default.TLabel')
        self.scrolled_frame_wrd = ScrollFrame(self, 500, 604)
        # {
        self.widgets_wrd = []
        # }

        self.lbl_header.grid(        row=0, column=0, padx=(6, 3), pady=(6, 3))
        self.scrolled_frame_wrd.grid(row=1, column=0, padx=6,      pady=(0, 6))

        self.print()

    # Выбрать статью из предложенных вариантов
    def choose_note(self, key):
        self.answer = key
        self.destroy()

    # Вывод вариантов
    def print(self):
        # Вывод вариантов
        count = 0
        while True:
            key = wrd_to_key(self.search_wrd, count)
            if key not in _0_global_dct.d.keys():
                break
            self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                            text=_0_global_dct.d[key].print_all(75, 13),
                                            command=lambda key=key: self.choose_note(key),
                                            takefocus=False, style='Flat.TButton')]
            count += 1

        # Расположение виджетов
        for i in range(len(self.widgets_wrd)):
            self.widgets_wrd[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Окно настроек категорий
class CategoriesSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.has_changes = False

        self.var_ctg = tk.StringVar()

        self.lbl_categories = ttk.Label(self, text='Существующие категории слов:',
                                        justify='center', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_categories = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                      font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                      selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                      relief=ST_RELIEF_TEXT[th], highlightbackground=ST_BORDERCOLOR[th])
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_add = ttk.Button(self.frame_buttons, text='Добавить категорию', command=self.add,
                                  takefocus=False, style='Default.TButton')
        self.btn_rename = ttk.Button(self.frame_buttons, text='Переименовать категорию', command=self.rename,
                                     takefocus=False, style='Default.TButton')
        self.btn_delete = ttk.Button(self.frame_buttons, text='Удалить категорию', command=self.delete,
                                     takefocus=False, style='Default.TButton')
        self.btn_values = ttk.Button(self.frame_buttons, text='Изменить значения категории', command=self.values,
                                     takefocus=False, style='Default.TButton')
        # }

        self.lbl_categories.grid(row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.txt_categories.grid(row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(     row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid( row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_rename.grid(row=1, padx=6, pady=3)
        self.btn_delete.grid(row=2, padx=6, pady=3)
        self.btn_values.grid(row=3, padx=6, pady=(3, 6))
        # }

        self.scrollbar.config(command=self.txt_categories.yview)

        self.refresh()

    # Добавить категорию
    def add(self):
        self.has_changes = add_ctg(self, _0_global_categories, _0_global_dct) or self.has_changes
        self.refresh()

    # Переименовать категорию
    def rename(self):
        self.has_changes = rename_ctg(self, _0_global_categories) or self.has_changes
        self.refresh()

    # Удалить категорию
    def delete(self):
        self.has_changes = delete_ctg(self, _0_global_categories, _0_global_dct) or self.has_changes
        self.refresh()

    # Перейти к настройкам значений категории
    def values(self):
        keys = [_key for _key in _0_global_categories.keys()]
        window = PopupChooseW(self, keys, 'Какую категорию вы хотите изменить?',
                              default_value=keys[0], combo_width=width(keys, 5, 100))
        closed, key = window.open()
        if closed:
            return
        self.has_changes = CategoryValuesSettingsW(self, key).open() or self.has_changes

    # Напечатать существующие категории
    def print_categories(self):
        self.txt_categories['state'] = 'normal'
        self.txt_categories.delete(1.0, tk.END)
        for key in _0_global_categories.keys():
            self.txt_categories.insert(tk.END, f'{key}\n')
        self.txt_categories['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_categories()
        if _0_global_categories:
            btn_enable(self.btn_rename, self.rename)
            btn_enable(self.btn_delete, self.delete)
            btn_enable(self.btn_values, self.values)
        else:
            btn_disable(self.btn_rename)
            btn_disable(self.btn_delete)
            btn_disable(self.btn_values)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек значений категории
class CategoryValuesSettingsW(tk.Toplevel):
    def __init__(self, parent, ctg: str):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.ctg = ctg  # Название изменяемой категории
        self.ctg_values = _0_global_categories[self.ctg]  # Значения изменяемой категории

        self.has_changes = False

        self.var_ctg = tk.StringVar()

        self.lbl_ctg_values = ttk.Label(self, text=f'Существующие значения категории\n'
                                                   f'"{ctg}":',
                                        justify='center', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_ctg_values = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                      font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                      selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                      relief=ST_RELIEF_TEXT[th], highlightbackground=ST_BORDERCOLOR[th])
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_add = ttk.Button(self.frame_buttons, text='Добавить значение', command=self.add,
                                  takefocus=False, style='Default.TButton')
        self.btn_rename = ttk.Button(self.frame_buttons, text='Переименовать значение', command=self.rename,
                                     takefocus=False, style='Default.TButton')
        self.btn_delete = ttk.Button(self.frame_buttons, text='Удалить значение', command=self.delete,
                                     takefocus=False, style='Default.TButton')
        # }

        self.lbl_ctg_values.grid(row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.txt_ctg_values.grid(row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(     row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid( row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_rename.grid(row=1, padx=6, pady=3)
        self.btn_delete.grid(row=2, padx=6, pady=3)
        # }

        self.scrollbar.config(command=self.txt_ctg_values.yview)

        self.refresh()

    # Добавить значение категории
    def add(self):
        has_changes, new_val = add_ctg_val(self, self.ctg_values)
        self.has_changes = self.has_changes or has_changes
        if not new_val:
            return
        self.ctg_values += [new_val]
        self.refresh()

    # Переименовать значение категории
    def rename(self):
        index = tuple(_0_global_categories).index(self.ctg)
        self.has_changes = rename_ctg_val(self, self.ctg_values, index, _0_global_dct) or self.has_changes
        self.refresh()

    # Удалить значение категории
    def delete(self):
        self.has_changes = delete_ctg_val(self, self.ctg_values, _0_global_dct) or self.has_changes
        self.refresh()

    # Напечатать существующие значения категории
    def print_ctg_values(self):
        self.txt_ctg_values['state'] = 'normal'
        self.txt_ctg_values.delete(1.0, tk.END)
        for key in self.ctg_values:
            self.txt_ctg_values.insert(tk.END, f'{key}\n')
        self.txt_ctg_values['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_ctg_values()
        if len(self.ctg_values) == 1:
            btn_disable(self.btn_delete)
        else:
            btn_enable(self.btn_delete, self.delete)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек специальных комбинаций
class SpecialCombinationsSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.has_changes = False

        self.lbl_combinations = ttk.Label(self, text='Существующие комбинации:', justify='center',
                                          style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_combinations = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                        font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                        selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                        relief=ST_RELIEF_TEXT[th], highlightbackground=ST_BORDERCOLOR[th])
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_add = ttk.Button(self.frame_buttons, text='Добавить комбинацию', command=self.add,
                                  takefocus=False, style='Default.TButton')
        self.btn_delete = ttk.Button(self.frame_buttons, text='Удалить комбинацию', command=self.delete,
                                     takefocus=False, style='Default.TButton')
        # }

        self.lbl_combinations.grid(row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.txt_combinations.grid(row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(       row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(   row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_delete.grid(row=1, padx=6, pady=(3, 6))
        # }

        self.scrollbar.config(command=self.txt_combinations.yview)

        self.refresh()

    # Добавить комбинацию
    def add(self):
        window = EnterSpecialCombinationW(self)
        closed, key, val = window.open()
        if closed or key == '' or val == '':
            return
        if key in _0_global_special_combinations.keys():
            warning(self, f'Комбинация #{key} уже существует!')
            return
        _0_global_special_combinations[key] = val
        self.refresh()
        self.has_changes = True

    # Удалить комбинацию
    def delete(self):
        variants = [special_combination(key) for key in _0_global_special_combinations]
        window = PopupChooseW(self, variants, 'Выберите комбинацию, которую хотите удалить', default_value=variants[0])
        closed, choose = window.open()
        if closed:
            return
        chosen_key = choose[1]
        _0_global_special_combinations.pop(chosen_key)
        self.refresh()
        self.has_changes = True

    # Напечатать существующие комбинации
    def print_combinations(self):
        self.txt_combinations['state'] = 'normal'
        self.txt_combinations.delete(1.0, tk.END)

        combinations = [special_combination(key) for key in _0_global_special_combinations]
        for combination in combinations:
            self.txt_combinations.insert(tk.END, f'{combination}\n')
        self.txt_combinations.insert(tk.END, '## -> #')

        self.txt_combinations['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_combinations()
        if _0_global_special_combinations:
            btn_enable(self.btn_delete, self.delete)
        else:
            btn_disable(self.btn_delete)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек пользовательской темы
class CustomThemeSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Custom theme settings')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.custom_styles = {}  # Стили пользовательской темы
        self.history = []  # История изменений
        self.history_undo = []  # История отмен
        self.dir_with_images = CUSTOM_THEME_PATH  # Папка с изображениями

        self.var_theme = tk.StringVar(value=DEFAULT_TH)
        self.var_images = tk.StringVar(value=DEFAULT_TH)
        self.var_relief_frame = tk.StringVar()
        self.var_relief_text = tk.StringVar()

        self.frame_themes = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_set_theme = ttk.Label(self.frame_themes, text='Взять за основу уже существующую тему:',
                                       style='Default.TLabel')
        self.combo_set_theme = ttk.Combobox(self.frame_themes, textvariable=self.var_theme, values=THEMES[1:],
                                            state='readonly', style='Default.TCombobox')
        self.btn_set_theme = ttk.Button(self.frame_themes, text='Выбрать', width=8, command=self.set_theme,
                                        takefocus=False, style='Default.TButton')
        self.lbl_set_images = ttk.Label(self.frame_themes, text='Использовать изображения из темы:',
                                        style='Default.TLabel')
        self.combo_set_images = ttk.Combobox(self.frame_themes, textvariable=self.var_images, values=THEMES[1:],
                                             state='readonly', style='Default.TCombobox')
        self.btn_set_images = ttk.Button(self.frame_themes, text='Выбрать', width=8, command=self.set_images,
                                         takefocus=False, style='Default.TButton')
        # }
        # Прокручиваемая область с настройками
        self.scrolled_frame = ScrollFrame(self, 400, 500)
        # {
        # Выбор цветов
        self.labels = [ttk.Label(self.scrolled_frame.frame_canvas, style='Default.TLabel')
                       for _ in range(len(STYLE_ELEMENTS))]
        self.buttons = [tk.Button(self.scrolled_frame.frame_canvas, relief='solid', overrelief='raised',
                                  borderwidth=1, width=18, takefocus=False)
                        for i in range(len(STYLE_ELEMENTS))]
        # Получается по 2 лишних экземпляра каждого виджета (но пусть будет так)

        for i in range(len(STYLE_ELEMENTS)):
            el = STYLE_ELEMENTS[i]
            if el not in ['RELIEF_FRAME', 'RELIEF_TEXT']:
                self.labels[i].configure(text=f'{STYLE_NAMES[el]}:')
                self.buttons[i].configure(command=lambda i=i: self.choose_color(i))

                self.labels[i].grid( row=i, column=0, padx=(6, 1), sticky='E')
                self.buttons[i].grid(row=i, column=1, padx=(0, 6), sticky='W')
                if i == 0:
                    self.labels[i].grid(pady=(6, 3))
                    self.buttons[i].grid(pady=(6, 3))
                elif i == len(STYLE_ELEMENTS) - 1:
                    self.labels[i].grid(pady=(0, 6))
                    self.buttons[i].grid(pady=(0, 6))
                else:
                    self.labels[i].grid(pady=(0, 3))
                    self.buttons[i].grid(pady=(0, 3))

        # Выбор стиля рамок
        def _choose_relief(elem, value):
            if self.custom_styles[elem] != value:
                self.history += [(elem, self.custom_styles[elem], value)]
                self.history_undo.clear()
            self.set_demo_styles()
            return True

        self.vcmd_relief_frame = (self.register(lambda value: _choose_relief('RELIEF_FRAME', value)), '%P')
        self.vcmd_relief_text = (self.register(lambda value: _choose_relief('RELIEF_TEXT', value)), '%P')

        self.lbl_relief_frame = ttk.Label(self.scrolled_frame.frame_canvas, text='Стиль рамок фреймов:',
                                          style='Default.TLabel')
        self.combo_relief_frame = ttk.Combobox(self.scrolled_frame.frame_canvas, textvariable=self.var_relief_frame,
                                               values=('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
                                               width=19, validate='focus', validatecommand=self.vcmd_relief_frame,
                                               state='readonly', style='Default.TCombobox')

        self.lbl_relief_text = ttk.Label(self.scrolled_frame.frame_canvas, text='Стиль рамок текстовых полей:',
                                         style='Default.TLabel')
        self.combo_relief_text = ttk.Combobox(self.scrolled_frame.frame_canvas, textvariable=self.var_relief_text,
                                              values=('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
                                              width=19, validate='focus', validatecommand=self.vcmd_relief_text,
                                              state='readonly', style='Default.TCombobox')
        # }
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_save = ttk.Button(self.frame_buttons, text='Сохранить', command=self.save, takefocus=False,
                                   style='Yes.TButton')
        self.frame_history = ttk.Frame(self.frame_buttons, style='Invis.TFrame')
        # { {
        try:
            self.img_undo = tk.PhotoImage(file=img_undo)
        except:
            self.btn_undo = ttk.Button(self.frame_history, text='<<', width=2, command=self.undo,
                                       takefocus=False, style='Default.TButton')
        else:
            self.btn_undo = ttk.Button(self.frame_history, image=self.img_undo, width=2, command=self.undo,
                                       takefocus=False, style='Image.TButton')
        try:
            self.img_redo = tk.PhotoImage(file=img_redo)
        except:
            self.btn_redo = ttk.Button(self.frame_history, text='>>', width=2, command=self.redo,
                                       takefocus=False, style='Default.TButton')
        else:
            self.btn_redo = ttk.Button(self.frame_history, image=self.img_redo, width=2, command=self.redo,
                                       takefocus=False, style='Image.TButton')
        # } }
        # }
        self.frame_demonstration = ttk.Frame(self, style='Window.TFrame', relief='solid')
        # {
        self.lbl_demo_header = ttk.Label(self.frame_demonstration, text='Anenokil developments presents',
                                         style='DemoHeader.TLabel')
        self.lbl_demo_logo = ttk.Label(self.frame_demonstration, text='Демонстрация', style='DemoLogo.TLabel')
        self.frame_demo_check = ttk.Frame(self.frame_demonstration, style='DemoDefault.TFrame')
        # { {
        self.lbl_demo_def = ttk.Label(self.frame_demo_check, text='Надпись:', style='DemoDefault.TLabel')
        self.check_demo = ttk.Checkbutton(self.frame_demo_check, style='DemoDefault.TCheckbutton')
        # } }
        self.btn_demo_def = ttk.Button(self.frame_demonstration, text='Кнопка', takefocus=False,
                                       style='DemoDefault.TButton')
        self.btn_demo_dis = ttk.Button(self.frame_demonstration, text='Выключена', takefocus=False,
                                       style='DemoDisabled.TButton')
        self.btn_demo_y = ttk.Button(self.frame_demonstration, text='Да', takefocus=False,
                                     style='DemoYes.TButton')
        self.btn_demo_n = ttk.Button(self.frame_demonstration, text='Нет', takefocus=False, style='DemoNo.TButton')
        self.entry_demo = ttk.Entry(self.frame_demonstration, style='DemoDefault.TEntry', width=21)
        self.txt_demo = tk.Text(self.frame_demonstration, font=('StdFont', _0_global_fontsize), width=12, height=4,
                                state='normal')
        self.scroll_demo = ttk.Scrollbar(self.frame_demonstration, command=self.txt_demo.yview,
                                         style='Demo.Vertical.TScrollbar')
        self.frame_demo_img = ttk.Frame(self.frame_demonstration, style='DemoDefault.TFrame')
        # { {
        self.images = [tk.PhotoImage(file='') for _ in range(len(ICON_NAMES))]
        self.img_buttons = [ttk.Button(self.frame_demo_img, width=2, takefocus=False) for _ in range(len(ICON_NAMES))]
        self.refresh_images()
        # } }
        self.lbl_demo_warn = ttk.Label(self.frame_demonstration, text='Предупреждение!', style='DemoWarn.TLabel')
        self.lbl_demo_footer = ttk.Label(self.frame_demonstration, text='Нижний колонтитул', style='DemoFooter.TLabel')
        # }

        # *---0------------------------1------2-----------------------*
        # |                                                           |
        # 0   *---------------------------*   *-------------------*   |
        # |   |  [lbl]   [combo]   [btn]  |   |                   |   |
        # |   |  [lbl]   [combo]   [btn]  |   |                   |   |
        # |   *---------------------------*   |                   |   |
        # |                                   |                   |   |
        # 1   *------------------------*--*   |                   |   |
        # |   |                        |  |   |                   |   |
        # |   |                        |sc|   |                   |   |
        # |   |                        |ro|   |                   |   |
        # |   |                        |ll|   |                   |   |
        # |   |                        |  |   |                   |   |
        # |   *------------------------*--*   |                   |   |
        # |                                   |                   |   |
        # 2   *---------------------------*   |                   |   |
        # |   |    [<-]  [->]   [save]    |   |                   |   |
        # |   *---------------------------*   *-------------------*   |
        # |                                                           |
        # *-----------------------------------------------------------*

        self.frame_themes.grid(row=0, column=0, columnspan=2, padx=6, pady=(6, 0))
        # {
        self.lbl_set_theme.grid(   row=0, column=0, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_set_theme.grid( row=0, column=1, padx=(0, 3), pady=(0, 6))
        self.btn_set_theme.grid(   row=0, column=2, padx=(0, 0), pady=(0, 6), sticky='W')
        self.lbl_set_images.grid(  row=1, column=0, padx=(0, 1), pady=0,      sticky='E')
        self.combo_set_images.grid(row=1, column=1, padx=(0, 3), pady=0)
        self.btn_set_images.grid(  row=1, column=2, padx=(0, 0), pady=0,      sticky='W')
        # }
        self.scrolled_frame.grid(row=1, columnspan=2, padx=6, pady=6)
        # {
        self.lbl_relief_frame.grid(  row=9,  column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_frame.grid(row=9,  column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_relief_text.grid(   row=10, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_text.grid( row=10, column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        # }
        self.frame_buttons.grid(row=2, column=0, columnspan=2, padx=6, pady=(0, 6))
        # {
        self.btn_save.grid(     row=0, column=0, padx=(0, 36), pady=0)
        self.frame_history.grid(row=0, column=1, padx=0,       pady=0)
        # { {
        self.btn_undo.grid(row=0, column=0, padx=(0, 6), pady=0, sticky='W')
        self.btn_redo.grid(row=0, column=1, padx=0,      pady=0, sticky='W')
        # } }
        # }
        self.frame_demonstration.grid(row=0, rowspan=3, column=2, padx=6, pady=6)
        # {
        self.lbl_demo_header.grid( row=0, column=0, columnspan=3, padx=12, pady=(12, 0))
        self.lbl_demo_logo.grid(   row=1, column=0, columnspan=3, padx=12, pady=(0, 12))
        self.frame_demo_check.grid(row=2, column=0,               padx=6,  pady=(0, 6), sticky='E')
        # { {
        self.lbl_demo_def.grid(row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_demo.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        # } }
        self.btn_demo_def.grid(   row=3,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_dis.grid(   row=4,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_y.grid(     row=5,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_n.grid(     row=6,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.entry_demo.grid(     row=2,            column=1, columnspan=2, padx=(0, 6), pady=(0, 6), sticky='SW')
        self.txt_demo.grid(       row=3, rowspan=4, column=1,               padx=0,      pady=(0, 6), sticky='SNWE')
        self.scroll_demo.grid(    row=3, rowspan=4, column=2,               padx=(0, 6), pady=(0, 6), sticky='SNW')
        self.frame_demo_img.grid( row=7,            column=0, columnspan=3, padx=6,      pady=(0, 6))
        # { {
        for i in range(len(ICON_NAMES)):
            self.img_buttons[i].grid(row=0, column=i, padx=3, pady=3)
        # } }
        self.lbl_demo_warn.grid(  row=8, column=0, columnspan=3, padx=6, pady=(0, 6))
        self.lbl_demo_footer.grid(row=9, column=0, columnspan=3, padx=6, pady=(0, 6))
        # }

        self.entry_demo.insert(tk.END, 'abcde 12345')
        self.txt_demo.insert(tk.END, '1')
        for i in range(2, 51):
            self.txt_demo.insert(tk.END, f'\n{i}')
        self.txt_demo.config(yscrollcommand=self.scroll_demo.set, state='disabled')

        self.read()

    # Взять за основу уже существующую тему
    def set_theme(self):
        theme_name = self.var_theme.get()
        old_vals = []
        new_vals = []
        for i in range(len(STYLE_ELEMENTS)):
            el = STYLE_ELEMENTS[i]

            if el == 'RELIEF_FRAME':
                self.var_relief_frame.set(STYLES[el][theme_name])
            elif el == 'RELIEF_TEXT':
                self.var_relief_text.set(STYLES[el][theme_name])
            else:
                self.buttons[i].config(bg=STYLES[el][theme_name], activebackground=STYLES[el][theme_name])

            old_vals += [self.custom_styles[el]]
            new_vals += [STYLES[el][theme_name]]
            self.custom_styles[el] = STYLES[el][theme_name]

        self.set_demo_styles()

        self.history += [('all', old_vals, new_vals)]
        self.history_undo.clear()

        self.var_images.set(theme_name)
        self.set_images()

    # Выбрать изображения
    def set_images(self):
        old_img = self.dir_with_images
        new_img = os.path.join(ADDITIONAL_THEMES_PATH, self.var_images.get())

        self.dir_with_images = new_img

        self.history += [('img', old_img, new_img)]
        self.history_undo.clear()

        self.refresh_images()

    # Выбрать цвет
    def choose_color(self, n: int):
        el = STYLE_ELEMENTS[n]
        hx = self.custom_styles[el]

        rgb, new_hx = colorchooser.askcolor(hx)
        if not new_hx:
            return

        self.buttons[n].config(bg=new_hx, activebackground=new_hx)
        self.custom_styles[el] = new_hx

        self.set_demo_styles()

        if new_hx != hx:
            self.history += [(el, hx, new_hx)]
            self.history_undo.clear()

    # Сохранить пользовательскую тему
    def save(self):
        self.custom_styles['RELIEF_FRAME'] = self.var_relief_frame.get()
        self.custom_styles['RELIEF_TEXT'] = self.var_relief_text.get()
        filepath = os.path.join(CUSTOM_THEME_PATH, 'styles.txt')
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'{REQUIRED_THEME_VERSION}')
            for el in STYLE_ELEMENTS:
                file.write(f'\n{self.custom_styles[el]}')

        if self.dir_with_images != CUSTOM_THEME_PATH:
            images = [img_ok, img_cancel, img_add, img_delete, img_edit, img_undo, img_redo, img_about, img_about_mgsp,
                      img_about_typo]
            for i in range(len(images)):
                file_name = f'{IMG_NAMES[i]}.png'
                src_path = os.path.join(self.dir_with_images, file_name)
                dst_path = os.path.join(CUSTOM_THEME_PATH, file_name)
                if file_name in os.listdir(CUSTOM_THEME_PATH):
                    os.remove(dst_path)
                if file_name in os.listdir(self.dir_with_images):
                    shutil.copyfile(src_path, dst_path)

    # Отменить последнее действие
    def undo(self):
        if self.history:
            last_action = self.history[-1]

            var = last_action[0]
            if var == 'all':
                vals = last_action[1]
                for i in range(len(STYLE_ELEMENTS)):
                    el = STYLE_ELEMENTS[i]

                    if el == 'RELIEF_FRAME':
                        self.var_relief_frame.set(vals[i])
                    elif el == 'RELIEF_TEXT':
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
                if el == 'RELIEF_FRAME':
                    self.var_relief_frame.set(val)
                elif el == 'RELIEF_TEXT':
                    self.var_relief_text.set(val)
                else:
                    i = STYLE_ELEMENTS.index(el)
                    self.buttons[i].config(bg=val, activebackground=val)

            self.history_undo += [last_action]
            self.history.pop(-1)

            self.set_demo_styles()

    # Вернуть отменённое действие
    def redo(self):
        if self.history_undo:
            last_undo_action = self.history_undo[-1]

            var = last_undo_action[0]
            if var == 'all':
                vals = last_undo_action[2]
                for i in range(len(STYLE_ELEMENTS)):
                    el = STYLE_ELEMENTS[i]

                    if el == 'RELIEF_FRAME':
                        self.var_relief_frame.set(vals[i])
                    elif el == 'RELIEF_TEXT':
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
                if el == 'RELIEF_FRAME':
                    self.var_relief_frame.set(val)
                elif el == 'RELIEF_TEXT':
                    self.var_relief_text.set(val)
                else:
                    i = STYLE_ELEMENTS.index(el)
                    self.buttons[i].config(bg=val, activebackground=val)

            self.history += [last_undo_action]
            self.history_undo.pop(-1)

            self.set_demo_styles()

    # Загрузить пользовательскую тему
    def read(self):
        filepath = os.path.join(CUSTOM_THEME_PATH, 'styles.txt')
        with open(filepath, 'r', encoding='utf-8') as file:
            version = file.readline().strip()  # Версия темы
            if version != f'{REQUIRED_THEME_VERSION}':
                upgrade_theme(filepath)
            for i in range(len(STYLE_ELEMENTS)):
                el = STYLE_ELEMENTS[i]

                self.custom_styles[el] = file.readline().strip()

                if el == 'RELIEF_FRAME':
                    self.var_relief_frame.set(self.custom_styles[el])
                elif el == 'RELIEF_TEXT':
                    self.var_relief_text.set(self.custom_styles[el])
                else:
                    self.buttons[i].config(bg=self.custom_styles[el], activebackground=self.custom_styles[el])

        self.set_demo_styles()

    # Обновить стили в демонстрации
    def set_demo_styles(self):
        self.custom_styles['RELIEF_FRAME'] = self.var_relief_frame.get()
        self.custom_styles['RELIEF_TEXT'] = self.var_relief_text.get()

        self.txt_demo.config(relief=self.custom_styles['RELIEF_TEXT'],
                             bg=self.custom_styles['BG_FIELDS'],
                             fg=self.custom_styles['FG'],
                             selectbackground=self.custom_styles['SELECT_BG'],
                             selectforeground=self.custom_styles['SELECT_FG'],
                             highlightbackground=self.custom_styles['BORDERCOLOR'])

        # Стиль label "demo default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure('DemoDefault.TLabel',
                                      font=('StdFont', 10),
                                      background=self.custom_styles['BG'],
                                      foreground=self.custom_styles['FG'])

        # Стиль label "demo header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('DemoHeader.TLabel',
                                     font=('StdFont', 15),
                                     background=self.custom_styles['BG'],
                                     foreground=self.custom_styles['FG'])

        # Стиль label "demo logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('DemoLogo.TLabel',
                                   font=('Times', 21),
                                   background=self.custom_styles['BG'],
                                   foreground=self.custom_styles['FG_LOGO'])

        # Стиль label "demo footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('DemoFooter.TLabel',
                                     font=('StdFont', 8),
                                     background=self.custom_styles['BG'],
                                     foreground=self.custom_styles['FG_FOOTER'])

        # Стиль label "demo warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('DemoWarn.TLabel',
                                   font=('StdFont', 10),
                                   background=self.custom_styles['BG'],
                                   foreground=self.custom_styles['FG_WARN'])

        # Стиль entry "demo"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('DemoDefault.TEntry',
                                font=('StdFont', 10))
        self.st_entry.map('DemoDefault.TEntry',
                          fieldbackground=[('readonly', self.custom_styles['BG']),
                                           ('!readonly', self.custom_styles['BG_FIELDS'])],
                          foreground=[('readonly', self.custom_styles['FG']),
                                      ('!readonly', self.custom_styles['FG_ENTRY'])],
                          selectbackground=[('readonly', self.custom_styles['SELECT_BG']),
                                            ('!readonly', self.custom_styles['SELECT_BG'])],
                          selectforeground=[('readonly', self.custom_styles['SELECT_FG']),
                                            ('!readonly', self.custom_styles['SELECT_FG'])])

        # Стиль button "demo default"
        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure('DemoDefault.TButton',
                                      font=('StdFont', 12),
                                      borderwidth=1)
        self.st_btn_default.map('DemoDefault.TButton',
                                relief=[('pressed', 'sunken'),
                                        ('active', 'flat'),
                                        ('!active', 'raised')],
                                background=[('pressed', self.custom_styles['BTN_BG_SEL']),
                                            ('active', self.custom_styles['BTN_BG']),
                                            ('!active', self.custom_styles['BTN_BG'])],
                                foreground=[('pressed', self.custom_styles['FG']),
                                            ('active', self.custom_styles['FG']),
                                            ('!active', self.custom_styles['FG'])])

        # Стиль button "demo disabled"
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure('DemoDisabled.TButton',
                                       font=('StdFont', 12),
                                       borderwidth=1)
        self.st_btn_disabled.map('DemoDisabled.TButton',
                                 relief=[('active', 'raised'),
                                         ('!active', 'raised')],
                                 background=[('active', self.custom_styles['BTN_BG_DISABL']),
                                             ('!active', self.custom_styles['BTN_BG_DISABL'])],
                                 foreground=[('active', self.custom_styles['BTN_FG_DISABL']),
                                             ('!active', self.custom_styles['BTN_FG_DISABL'])])

        # Стиль button "demo yes"
        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure('DemoYes.TButton',
                                  font=('StdFont', 12),
                                  borderwidth=1)
        self.st_btn_yes.map('DemoYes.TButton',
                            relief=[('pressed', 'sunken'),
                                    ('active', 'flat'),
                                    ('!active', 'raised')],
                            background=[('pressed', self.custom_styles['BTN_Y_BG_SEL']),
                                        ('active', self.custom_styles['BTN_Y_BG']),
                                        ('!active', self.custom_styles['BTN_Y_BG'])],
                            foreground=[('pressed', self.custom_styles['FG']),
                                        ('active', self.custom_styles['FG']),
                                        ('!active', self.custom_styles['FG'])])

        # Стиль button "demo no"
        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure('DemoNo.TButton',
                                 font=('StdFont', 12),
                                 borderwidth=1)
        self.st_btn_no.map('DemoNo.TButton',
                           relief=[('pressed', 'sunken'),
                                   ('active', 'flat'),
                                   ('!active', 'raised')],
                           background=[('pressed', self.custom_styles['BTN_N_BG_SEL']),
                                       ('active', self.custom_styles['BTN_N_BG']),
                                       ('!active', self.custom_styles['BTN_N_BG'])],
                           foreground=[('pressed', self.custom_styles['FG']),
                                       ('active', self.custom_styles['FG']),
                                       ('!active', self.custom_styles['FG'])])

        # Стиль button "demo image"
        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure('DemoImage.TButton',
                                    font=('StdFont', 12),
                                    borderwidth=0)
        self.st_btn_image.map('DemoImage.TButton',
                              relief=[('pressed', 'flat'),
                                      ('active', 'flat'),
                                      ('!active', 'flat')],
                              background=[('pressed', self.custom_styles['BTN_IMG_BG_SEL']),
                                          ('active', self.custom_styles['BTN_IMG_BG_HOV']),
                                          ('!active', self.custom_styles['BG'])],
                              foreground=[('pressed', self.custom_styles['FG']),
                                          ('active', self.custom_styles['FG']),
                                          ('!active', self.custom_styles['FG'])])

        # Стиль checkbutton "demo"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map('DemoDefault.TCheckbutton',
                          background=[('active', self.custom_styles['CHECK_BG_SEL']),
                                      ('!active', self.custom_styles['BG'])])

        # Стиль frame "demo default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure('DemoDefault.TFrame',
                                        borderwidth=1,
                                        relief=self.custom_styles['RELIEF_FRAME'],
                                        background=self.custom_styles['BG'],
                                        bordercolor=self.custom_styles['BORDERCOLOR'])

        # Стиль frame "window"
        self.st_frame_window = ttk.Style()
        self.st_frame_window.theme_use('alt')
        self.st_frame_window.configure('Window.TFrame',
                                       borderwidth=1,
                                       relief='groove',
                                       background=self.custom_styles['BG'],
                                       bordercolor='#888888')

        # Стиль scrollbar "vertical"
        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map('Demo.Vertical.TScrollbar',
                            troughcolor=[('disabled', self.custom_styles['BG']),
                                         ('pressed', self.custom_styles['SCROLL_BG_SEL']),
                                         ('!pressed', self.custom_styles['SCROLL_BG'])],
                            background=[('disabled', self.custom_styles['BG']),
                                        ('pressed', self.custom_styles['SCROLL_FG_SEL']),
                                        ('!pressed', self.custom_styles['SCROLL_FG'])])

        return True

    # Обновить изображения в демонстрации
    def refresh_images(self):
        for i in range(len(ICON_NAMES)):
            img = f'{ICON_NAMES[i]}.png'
            try:
                self.images[i].config(file=os.path.join(self.dir_with_images, img))
            except:
                try:
                    self.images[i].config(file=os.path.join(IMAGES_PATH, img))
                except:
                    self.img_buttons[i].config(text='-', image='', compound='text', style='DemoDefault.TButton')
                else:
                    self.img_buttons[i].config(image=self.images[i], compound='image', style='DemoImage.TButton')
            else:
                self.img_buttons[i].config(image=self.images[i], compound='image', style='DemoImage.TButton')

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно уведомления о выходе новой версии
class NewVersionAvailableW(tk.Toplevel):
    def __init__(self, parent, last_version: str):
        super().__init__(parent)
        self.title('A new version is available')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_url = tk.StringVar(value=URL_GITHUB)  # Ссылка, для загрузки новой версии

        self.lbl_msg = ttk.Label(self, text=f'Доступна новая версия программы:\n'
                                            f'{last_version}',
                                 justify='center', style='Default.TLabel')
        self.frame_url = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.entry_url = ttk.Entry(self.frame_url, textvariable=self.var_url, state='readonly', width=45,
                                   justify='center', style='Default.TEntry')
        self.btn_open = ttk.Button(self.frame_url, text='Открыть ссылку', command=self.open_github,
                                   takefocus=False, style='Default.TButton')
        # }
        self.btn_update = ttk.Button(self, text='Обновить', command=self.download_and_install,
                                     takefocus=False, style='Yes.TButton')
        self.btn_close = ttk.Button(self, text='Закрыть', command=self.destroy, takefocus=False, style='No.TButton')

        self.lbl_msg.grid(  row=1, columnspan=2, padx=6, pady=(4, 0))
        self.frame_url.grid(row=2, columnspan=2, padx=6, pady=(0, 4))
        # {
        self.entry_url.grid(row=0, column=0, padx=(0, 3), pady=0)
        self.btn_open.grid( row=0, column=1, padx=0,      pady=0)
        # }
        self.btn_update.grid(row=3, column=0, padx=6, pady=4)
        self.btn_close.grid( row=3, column=1, padx=6, pady=4)

    # Открыть репозиторий проекта на GitHub
    def open_github(self):
        try:
            webbrowser.open(URL_GITHUB)
        except Exception as exc:
            print(f'Не удалось открыть страницу!\n'
                  f'{exc}')
            warning(self, f'Не удалось открыть страницу!\n'
                          f'{exc}')

    # Скачать и установить обновление
    def download_and_install(self):
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(_0_global_dct_savename), _0_global_has_progress)

        # Загрузка списка обновляемых файлов
        try:
            print('\nЧтение данных...')
            data = urllib2.urlopen(URL_UPDATE_FILES)
            update_files = [str(filename.decode('utf-8')).strip() for filename in data.readlines()]
        except Exception as exc:
            print(f'Не удалось получить данные!\n'
                  f'{exc}')
            warning(self, f'Не удалось получить данные!\n'
                          f'{exc}')
            self.destroy()
            return
        # Загрузка
        try:
            # Скачиваем архив с обновлением
            print('Загрузка архива...', end='')
            wget.download(URL_DOWNLOAD_ZIP, out=MAIN_PATH)
        except Exception as exc:
            print(f'\nНе удалось загрузить обновление!\n'
                  f'{exc}')
            warning(self, f'Не удалось загрузить обновление!\n'
                          f'{exc}')
            self.destroy()
            return
        # Установка
        try:
            # Распаковываем архив во временную папку
            print('\nРаспаковка архива...')
            with zipfile.ZipFile(NEW_VERSION_ZIP_PATH, 'r') as zip_file:
                zip_file.extractall(MAIN_PATH)
            # Удаляем архив
            print('Удаление архива...')
            os.remove(NEW_VERSION_ZIP_PATH)
            # Удаляем файлы текущей версии
            print('Удаление старых файлов...')
            for filename in os.listdir(IMAGES_PATH):
                try:
                    os.remove(os.path.join(IMAGES_PATH, filename))
                except FileNotFoundError:
                    print(f'Не удалось удалить файл "{filename}", т. к. он отсутствует')
            for filename in ['ver', 'README.txt', 'README.md', 'main.py']:
                try:
                    os.remove(os.path.join(MAIN_PATH, filename))
                except FileNotFoundError:
                    print(f'Не удалось удалить файл "{filename}", т. к. он отсутствует')
            # Из временной папки достаём файлы новой версии
            print('Установка новых файлов...')
            for filename in update_files:
                os.replace(os.path.join(NEW_VERSION_PATH, filename),
                           os.path.join(MAIN_PATH, filename))
            # Удаляем временную папку
            print('Удаление временной папки...')
            shutil.rmtree(NEW_VERSION_PATH)
        except Exception as exc:
            print(f'Не удалось установить обновление!\n'
                  f'{exc}')
            warning(self, f'Не удалось установить обновление!\n'
                          f'{exc}')
            self.destroy()
            return
        else:
            print('Обновление успешно установлено!')
            PopupMsgW(self, 'Обновление успешно установлено!\n'
                            'Программа закроется').open()
            exit(777)


""" Графический интерфейс - основные окна """


# Окно просмотра словаря
class PrintW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Dictionary')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_fav = tk.BooleanVar(value=False)
        self.var_forms = tk.BooleanVar(value=True)
        self.var_info = tk.StringVar()

        self.lbl_dct_name = ttk.Label(self,
                                      text=split_text(f'Открыт словарь "{_0_global_dct_savename}"',
                                                      40, align_left=False),
                                      justify='center', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_fav = ttk.Label(self.frame_main, text='Только избранные:', style='Default.TLabel')
        self.lbl_forms = ttk.Label(self.frame_main, text='Все формы:', style='Default.TLabel')
        self.check_fav = ttk.Checkbutton(self.frame_main, variable=self.var_fav, command=lambda: self.print(True),
                                         style='Default.TCheckbutton')
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, command=lambda: self.print(True),
                                           style='Default.TCheckbutton')
        # }
        self.scrolled_frame = ScrollFrame(self, 500, 604)
        # {
        self.keys = [key for key in _0_global_dct.d.keys()]
        self.buttons = [ttk.Button(self.scrolled_frame.frame_canvas,
                                   text=_0_global_dct.d[self.keys[i]].print_briefly_with_forms(75),
                                   command=lambda i=i: self.edit_note(i), takefocus=False, style='Flat.TButton')
                        for i in range(_0_global_dct.count_w)]
        for i in range(_0_global_dct.count_w):
            self.buttons[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            #self.buttons[i].bind('<Control-F>', lambda i=i: _0_global_dct.d[self.keys[i]].add_to_fav())
            #self.buttons[i].bind('<Control-f>', lambda i=i: _0_global_dct.d[self.keys[i]].add_to_fav())
        self.tips = [ttip.Hovertip(self.buttons[i],
                                   f'Количество ответов после последнего верного ответа: '
                                   f'{_0_global_dct.d[self.keys[i]].last_att_print()}\n'
                                   f'Доля верных ответов: {_0_global_dct.d[self.keys[i]].percent_print()}',
                                   hover_delay=666)
                     for i in range(_0_global_dct.count_w)]
        # }
        self.lbl_info = ttk.Label(self, textvariable=self.var_info, style='Default.TLabel')
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_fav_all = ttk.Button(self.frame_buttons, text='Добавить всё в избранное', command=self.fav_all,
                                      takefocus=False, style='Default.TButton')
        self.btn_unfav_all = ttk.Button(self.frame_buttons, text='Убрать всё из избранного', command=self.unfav_all,
                                        takefocus=False, style='Default.TButton')
        self.btn_print_out = ttk.Button(self.frame_buttons, text='Распечатать словарь в файл', command=self.print_out,
                                        takefocus=False, style='Default.TButton')
        # }

        self.lbl_dct_name.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        self.frame_main.grid(  row=1, columnspan=2, padx=6, pady=(0, 4))
        # {
        self.lbl_fav.grid(    row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_fav.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_forms.grid(  row=0, column=2, padx=(6, 1), pady=6, sticky='E')
        self.check_forms.grid(row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        # }
        self.scrolled_frame.grid(row=2, columnspan=2, padx=6, pady=6)
        self.lbl_info.grid(      row=3, columnspan=2, padx=6, pady=(0, 6))
        self.frame_buttons.grid( row=4, columnspan=2, padx=6, pady=(0, 6))
        # {
        self.btn_fav_all.grid(  row=0, column=0,     padx=(0, 6), pady=(0, 6))
        self.btn_unfav_all.grid(row=0, column=1,     padx=0,      pady=(0, 6))
        self.btn_print_out.grid(row=1, columnspan=2, padx=0,      pady=0)
        # }

        self.var_info.set(_0_global_dct.dct_info())

        self.bind('<Up>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-U>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-u>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))

        self.bind('<Down>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-D>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-d>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))

    # Изменить статью
    def edit_note(self, index):
        EditW(self, self.keys[index]).open()

        self.print(True)

    # Напечатать словарь
    def print(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        for tip in self.tips:
            tip.__del__()

        # Выбираем нужные статьи и выводим информацию
        if self.var_fav.get():
            self.keys = [key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].fav]

            w, t, f = _0_global_dct.count_fav()
            self.var_info.set(_0_global_dct.dct_info_fav(w, t, f))
        else:
            self.keys = [key for key in _0_global_dct.d.keys()]

            self.var_info.set(_0_global_dct.dct_info())

        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.scrolled_frame.frame_canvas, command=lambda i=i: self.edit_note(i),
                                   takefocus=False, style='Flat.TButton')
                        for i in range(len(self.keys))]
        # Выводим текст на кнопки
        if self.var_forms.get():
            for i in range(len(self.keys)):
                self.buttons[i].configure(text=_0_global_dct.d[self.keys[i]].print_briefly_with_forms(75))
        else:
            for i in range(len(self.keys)):
                self.buttons[i].configure(text=_0_global_dct.d[self.keys[i]].print_briefly(75))
        # Расставляем кнопки
        for i in range(len(self.keys)):
            self.buttons[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            #self.buttons[i].bind('<Control-F>', lambda i=i: _0_global_dct.d[self.keys[i]].add_to_fav())
            #self.buttons[i].bind('<Control-f>', lambda i=i: _0_global_dct.d[self.keys[i]].add_to_fav())
        # Создаём подсказки
        self.tips = [ttip.Hovertip(self.buttons[i],
                                   f'Количество ответов после последнего верного ответа: '
                                   f'{_0_global_dct.d[self.keys[i]].last_att_print()}\n'
                                   f'Доля верных ответов: {_0_global_dct.d[self.keys[i]].percent_print()}',
                                   hover_delay=666)
                     for i in range(len(self.keys))]

        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Нажатие на кнопку "Добавить все статьи в избранное"
    def fav_all(self):
        window = PopupDialogueW(self, 'Вы действительно хотите добавить все статьи в избранное?')
        answer = window.open()
        if not answer:
            return
        _0_global_dct.fav_all()

        self.print(False)

    # Нажатие на кнопку "Убрать все статьи из избранного"
    def unfav_all(self):
        window = PopupDialogueW(self, 'Вы действительно хотите убрать все статьи из избранного?')
        answer = window.open()
        if not answer:
            return
        _0_global_dct.unfav_all()

        self.print(False)

    # Нажатие на кнопку "Распечатать словарь в файл"
    def print_out(self):
        folder = askdirectory(initialdir=MAIN_PATH, title='В какую папку сохранить файл?')
        if not folder:
            return
        filename = f'Распечатка_{_0_global_dct_savename}.txt'
        _0_global_dct.print_out(os.path.join(folder, filename))

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно изучения слов
class LearnW(tk.Toplevel):
    def __init__(self, parent, learn_method: str, with_forms: bool, words: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Learn')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.current_key = None
        self.current_form = None
        self.rnd_f = None  # Вспомогательная переменная для выбора случайного слова
        self.count_all = 0
        self.count_correct = 0
        self.used_words = set()  # Слова (формы), которые уже были угаданы
        self.learn_method = learn_method  # Метод изучения слов
        self.with_forms = with_forms  # Со всеми ли словоформами
        self.words = words  # Способ подбора слов

        self.var_input = tk.StringVar()

        self.lbl_global_rating = ttk.Label(self, text=f'Ваш общий рейтинг по словарю: {self.get_percent()}%',
                                           style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_dct = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set,
                               font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                               selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                               relief=ST_RELIEF_TEXT[th], highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar.config(command=self.txt_dct.yview)
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # { {
        self.btn_input = ttk.Button(self.frame_main, text='Ввод', command=self.input,
                                    takefocus=False, style='Default.TButton')
        self.entry_input = ttk.Entry(self.frame_main, textvariable=self.var_input, width=50, style='Default.TEntry')
        self.btn_notes = ttk.Button(self.frame_main, text='Посмотреть сноски', command=self.show_notes,
                                    takefocus=False, style='Default.TButton')
        # } }
        self.btn_stop = ttk.Button(self, text='Закончить', command=self.stop, takefocus=False, style='No.TButton')

        self.lbl_global_rating.grid(row=0, columnspan=2, padx=6,      pady=6)
        self.txt_dct.grid(          row=1, column=0,     padx=(6, 0), pady=6, sticky='NSEW')
        self.scrollbar.grid(        row=1, column=1,     padx=(0, 6), pady=6, sticky='NSW')
        self.frame_main.grid(       row=2, columnspan=2, padx=6,      pady=6)
        # { {
        self.btn_input.grid(  row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        self.btn_notes.grid(  row=0, column=2, padx=0,      pady=0, sticky='W')
        # } }
        self.btn_stop.grid(row=3, columnspan=2, padx=6, pady=6)

        self.tip_btn_notes = ttip.Hovertip(self.btn_notes, 'Срабатывает при нажатии на Tab;\n'
                                                           'Если сносок нет, то ничего не выведется',
                                           hover_delay=700)
        if learn_method == VALUES_LEARN_METHOD[0]:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите слово', hover_delay=1000)
        else:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)

        self.start()

        if self.current_key:
            entry = _0_global_dct.d[self.current_key]
            if entry.count_n == 0:
                btn_disable(self.btn_notes)

    # Печать в текстовое поле
    def outp(self, msg='', end='\n'):
        self.txt_dct['state'] = 'normal'
        self.txt_dct.insert(tk.END, f'{msg}{end}')
        self.txt_dct.yview_moveto(1.0)
        self.txt_dct['state'] = 'disabled'

    # Просмотр сносок
    def show_notes(self):
        entry = _0_global_dct.d[self.current_key]
        if entry.count_n != 0:
            self.outp(entry.notes_print())
        btn_disable(self.btn_notes)

    # Ввод ответа и переход к следующему слову
    def input(self):
        global _0_global_has_progress

        answer = encode_special_combinations(self.entry_input.get())  # Вывод пользовательского ответа
        if answer != '':
            self.outp(answer)

        if self.learn_method == VALUES_LEARN_METHOD[1]:
            self.check_tr()
        elif self.with_forms and self.rnd_f != -1:
            self.check_form()
        else:
            self.check_wrd()

        if self.learn_method == VALUES_LEARN_METHOD[0]:
            if self.with_forms:
                if self.words == VALUES_LEARN_WORDS[0]:
                    _0_global_has_progress = self.choose_f(_0_global_dct) or _0_global_has_progress
                elif self.words == VALUES_LEARN_WORDS[1]:
                    _0_global_has_progress = self.choose_f_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                             _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_f_fav(_0_global_dct) or _0_global_has_progress
            else:
                if self.words == VALUES_LEARN_WORDS[0]:
                    _0_global_has_progress = self.choose(_0_global_dct) or _0_global_has_progress
                elif self.words == VALUES_LEARN_WORDS[1]:
                    _0_global_has_progress = self.choose_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                             _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_fav(_0_global_dct) or _0_global_has_progress
        else:
            if self.words == VALUES_LEARN_WORDS[0]:
                _0_global_has_progress = self.choose_t(_0_global_dct) or _0_global_has_progress
            elif self.words == VALUES_LEARN_WORDS[1]:
                _0_global_has_progress = self.choose_t_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                         _0_global_has_progress
            else:
                _0_global_has_progress = self.choose_t_fav(_0_global_dct) or _0_global_has_progress

        entry = _0_global_dct.d[self.current_key]
        if entry.count_n == 0:
            btn_disable(self.btn_notes)
        else:
            btn_enable(self.btn_notes, self.show_notes)

        self.entry_input.delete(0, tk.END)
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {self.get_percent()}%'

    # Завершение учёбы
    def stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()
        btn_disable(self.btn_input)

        PopupMsgW(self, f'Ваш результат: {self.count_correct}/{self.count_all}')
        self.outp(f'\nВаш результат: {self.count_correct}/{self.count_all}', end='')

    # Начать учить слова
    def start(self):
        global _0_global_has_progress

        if self.learn_method == VALUES_LEARN_METHOD[0]:
            if self.with_forms:
                if self.words == VALUES_LEARN_WORDS[0]:
                    _0_global_has_progress = self.choose_f(_0_global_dct) or _0_global_has_progress
                elif self.words == VALUES_LEARN_WORDS[1]:
                    _0_global_has_progress = self.choose_f_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                             _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_f_fav(_0_global_dct) or _0_global_has_progress
            else:
                if self.words == VALUES_LEARN_WORDS[0]:
                    _0_global_has_progress = self.choose(_0_global_dct) or _0_global_has_progress
                elif self.words == VALUES_LEARN_WORDS[1]:
                    _0_global_has_progress = self.choose_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                             _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_fav(_0_global_dct) or _0_global_has_progress
        else:
            if self.words == VALUES_LEARN_WORDS[0]:
                _0_global_has_progress = self.choose_t(_0_global_dct) or _0_global_has_progress
            elif self.words == VALUES_LEARN_WORDS[1]:
                _0_global_has_progress = self.choose_t_hard(_0_global_dct, _0_global_min_good_score_perc) or\
                                         _0_global_has_progress
            else:
                _0_global_has_progress = self.choose_t_fav(_0_global_dct) or _0_global_has_progress

    # Проверка введённого ответа
    def check_answer(self, correct_answer: str, is_correct: bool,
                     current_key: tuple[str, int], current_form: tuple[str, ...] | None = None):
        entry = _0_global_dct.d[current_key]
        if is_correct:
            entry.correct()
            self.outp('Верно\n')
            if entry.fav:
                window = PopupDialogueW(self, 'Верно.\n'
                                              'Оставить слово в избранном?',
                                        'Да', 'Нет', val_on_close=True)
                answer = window.open()
                if not answer:
                    entry.fav = False
            self.count_all += 1
            self.count_correct += 1
            if current_form:
                self.used_words.add((current_key, current_form))
            else:
                self.used_words.add(current_key)
        else:
            self.outp(f'Неверно. Правильный ответ: "{correct_answer}"\n')
            if entry.fav:
                if bool(_0_global_with_typo):
                    window = PopupDialogueW(self, msg=f'Неверно.\n'
                                                      f'Ваш ответ: {encode_special_combinations(self.entry_input.get())}\n'
                                                      f'Правильный ответ: {correct_answer}',
                                            btn_left_text='Ясно', btn_right_text='Просто опечатка',
                                            st_left='Default', st_right='Default',
                                            val_left='ok', val_right='typo')
                    answer = window.open()
                    if answer != 'typo':
                        entry.incorrect()
                        self.count_all += 1
                else:
                    entry.incorrect()
                    self.count_all += 1
            else:
                window = IncorrectAnswerW(self, encode_special_combinations(self.entry_input.get()),
                                          correct_answer, bool(_0_global_with_typo))
                answer = window.open()
                if answer != 'typo':
                    entry.incorrect()
                    self.count_all += 1
                if answer == 'yes':
                    entry.fav = True

    # Проверка введённого слова
    def check_wrd(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get()) == entry.wrd
        else:
            is_correct = encode_special_combinations(self.entry_input.get()).lower() == entry.wrd.lower()
        self.check_answer(entry.wrd, is_correct, self.current_key)

    # Проверка введённой словоформы
    def check_form(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get()) == entry.forms[self.current_form]
        else:
            is_correct = encode_special_combinations(self.entry_input.get()).lower() == entry.forms[self.current_form].lower()
        self.check_answer(entry.forms[self.current_form], is_correct, self.current_key, self.current_form)

    # Проверка введённого перевода
    def check_tr(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get()) in entry.tr
        else:
            is_correct = encode_special_combinations(self.entry_input.get()).lower() in [tr.lower() for tr in entry.tr]
        self.check_answer(tpl(entry.tr), is_correct, self.current_key)

    # Выбор слова - все
    def choose(self, dct: Dictionary):
        if len(self.used_words) == dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_tr_with_stat())

        return True

    # Выбор слова - избранные
    def choose_fav(self, dct: Dictionary):
        while True:
            if len(self.used_words) == dct.count_w:
                self.stop()
                return
            self.current_key = random.choice(list(dct.d.keys()))
            if not dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                continue
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_tr_with_stat())

        return True

    # Выбор слова - все, сначала сложные
    def choose_hard(self, dct: Dictionary, min_good_score_perc: int):
        if len(self.used_words) == dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = dct.random_hard(min_good_score_perc)
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_tr_with_stat())

        return True

    # Выбор словоформы - все
    def choose_f(self, dct: Dictionary):
        if len(self.used_words) == dct.count_w + dct.count_f:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(dct.d.keys()))
            self.rnd_f = random.randint(-1, dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_with_stat())
                    break
            else:
                self.current_form = list(dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_and_frm_with_stat(self.current_form))
                    break

        return True

    # Выбор словоформы - избранные
    def choose_f_fav(self, dct: Dictionary):
        while True:
            if len(self.used_words) == dct.count_w + dct.count_f:
                self.stop()
                return
            self.current_key = random.choice(list(dct.d.keys()))
            if not dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                for frm in dct.d[self.current_key].forms.keys():
                    self.used_words.add((self.current_key, frm))
                continue
            self.rnd_f = random.randint(-1, dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_with_stat())
                    break
            else:
                self.current_form = list(dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_and_frm_with_stat(self.current_form))
                    break

        return True

    # Выбор словоформы - все, сначала сложные
    def choose_f_hard(self, dct: Dictionary, min_good_score_perc: int):
        if len(self.used_words) == dct.count_w + dct.count_f:
            self.stop()
            return
        while True:
            self.current_key = dct.random_hard(min_good_score_perc)
            self.rnd_f = random.randint(-1, dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_with_stat())
                    break
            else:
                self.current_form = list(dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.outp(dct.d[self.current_key].print_tr_and_frm_with_stat(self.current_form))
                    break

        return True

    # Выбор перевода - все
    def choose_t(self, dct: Dictionary):
        if len(self.used_words) == dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_wrd_with_stat())

        return True

    # Выбор перевода - избранные
    def choose_t_fav(self, dct: Dictionary):
        while True:
            if len(self.used_words) == dct.count_w:
                self.stop()
                return
            self.current_key = random.choice(list(dct.d.keys()))
            if not dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                continue
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_wrd_with_stat())

        return True

    # Выбор перевода - все, сначала сложные
    def choose_t_hard(self, dct: Dictionary, min_good_score_perc: int):
        if len(self.used_words) == dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = dct.random_hard(min_good_score_perc)
            if self.current_key not in self.used_words:
                break

        self.outp(dct.d[self.current_key].print_wrd_with_stat())

        return True

    # Получить глобальный процент угадываний
    def get_percent(self):
        return format(_0_global_dct.count_rating() * 100, '.1f')

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_input.invoke())
        self.bind('<Tab>', lambda event=None: self.btn_notes.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно поиска статей
class SearchW(tk.Toplevel):
    def __init__(self, parent, query: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Search')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_query = tk.StringVar(value=query)

        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_input = ttk.Label(self.frame_main, text='Введите запрос:', style='Default.TLabel')
        self.entry_input = ttk.Entry(self.frame_main, textvariable=self.var_query, width=60, style='Default.TEntry')
        self.btn_search = ttk.Button(self.frame_main, text='Поиск', command=self.search,
                                     takefocus=False, style='Default.TButton')
        # }
        self.lbl_wrd = ttk.Label(self, text='Поиск по слову', style='Default.TLabel')
        self.scrolled_frame_wrd = ScrollFrame(self, 500, 404)
        # {
        self.widgets_wrd = []
        # }
        self.lbl_tr = ttk.Label(self, text='Поиск по переводу', style='Default.TLabel')
        self.scrolled_frame_tr = ScrollFrame(self, 500, 404)
        # {
        self.widgets_tr = []
        # }

        self.frame_main.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        # {
        self.lbl_input.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.btn_search.grid( row=0, column=2, padx=6,      pady=6)
        # }
        self.lbl_wrd.grid(           row=1, column=0, padx=(6, 3), pady=(0, 3))
        self.lbl_tr.grid(            row=1, column=1, padx=(3, 6), pady=(0, 3))
        self.scrolled_frame_wrd.grid(row=2, column=0, padx=6,      pady=(0, 6))
        self.scrolled_frame_tr.grid( row=2, column=1, padx=6,      pady=(0, 6))

        self.search()

    # Изменить статью
    def edit_note(self, key):
        EditW(self, key).open()

        self.search()

    # Поиск статей
    def search(self):
        self.search_wrd()  # Поиск статей по слову
        self.search_tr()  # Поиск статей по переводу

    # Поиск статей по слову
    def search_wrd(self):
        # Удаляем старые виджеты
        for wdg in self.widgets_wrd:
            wdg.destroy()
        self.widgets_wrd = []

        # Искомое слово
        search_wrd = encode_special_combinations(self.var_query.get())

        # Полное совпадение
        self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                       text=split_text('Полное совпадение:', 50, 0),
                                       style='Flat.TLabel')]
        count = 0
        while True:
            key = wrd_to_key(search_wrd, count)
            if key not in _0_global_dct.d.keys():
                break
            self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                            text=_0_global_dct.d[key].print_all(50, 13),
                                            command=lambda key=key: self.edit_note(key),
                                            takefocus=False, style='Flat.TButton')]
            count += 1
        if count == 0:
            self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                           text=split_text(f'Слово "{search_wrd}" отсутствует в словаре', 50, 0),
                                           style='Flat.TLabel')]

        # Частичное совпадение
        self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                       text=split_text('Частичное совпадение:', 50, 0), style='Flat.TLabel')]
        particular_matches = _0_global_dct.get_words_with_content(search_wrd)
        if particular_matches:
            for (key, text) in particular_matches:
                self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                                text=split_text(text, 50, 5),
                                                command=lambda key=key: self.edit_note(key),
                                                takefocus=False, style='Flat.TButton')]
        else:
            self.widgets_wrd += [ttk.Label(self.scrolled_frame_wrd.frame_canvas,
                                           text=split_text('Частичных совпадений не найдено', 50, 0),
                                           style='Flat.TLabel')]

        # Расположение виджетов
        for i in range(len(self.widgets_wrd)):
            self.widgets_wrd[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

    # Поиск статей по переводу
    def search_tr(self):
        # Удаляем старые виджеты
        for wdg in self.widgets_tr:
            wdg.destroy()
        self.widgets_tr = []

        # Искомый перевод
        search_tr = encode_special_combinations(self.var_query.get())

        # Полное совпадение
        self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                      text=split_text('Полное совпадение:', 50, 0),
                                      style='Flat.TLabel')]
        count = 0
        for key in _0_global_dct.d.keys():
            entry = _0_global_dct.d[key]
            if search_tr in entry.tr:
                self.widgets_tr += [ttk.Button(self.scrolled_frame_tr.frame_canvas,
                                               text=entry.print_all(50, 13),
                                               command=lambda key=key: self.edit_note(key),
                                               takefocus=False, style='Flat.TButton')]
                count += 1
        if count == 0:
            self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                          text=split_text(f'Слово с переводом "{search_tr}" отсутствует в словаре',
                                                          50, 0),
                                          style='Flat.TLabel')]

        # Частичное совпадение
        self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                      text=split_text('Частичное совпадение:', 50, 0), style='Flat.TLabel')]
        particular_matches = _0_global_dct.get_translations_with_content(search_tr)
        if particular_matches:
            for (key, text) in particular_matches:
                self.widgets_tr += [ttk.Button(self.scrolled_frame_tr.frame_canvas,
                                               text=split_text(text, 50, 5),
                                               command=lambda key=key: self.edit_note(key),
                                               takefocus=False, style='Flat.TButton')]
        else:
            self.widgets_tr += [ttk.Label(self.scrolled_frame_tr.frame_canvas,
                                          text=split_text('Частичных совпадений не найдено', 50, 0),
                                          style='Flat.TLabel')]

        # Расположение виджетов
        for i in range(len(self.widgets_tr)):
            self.widgets_tr[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_tr.canvas.yview_moveto(0.0)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_search.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, key: tuple[str, int]):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Edit an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.dct_key = key
        self.line_width = 35
        self.max_height_w = 3
        self.max_height_t = 6
        self.max_height_n = 6
        self.max_height_f = 8

        self.var_wrd = tk.StringVar(value=_0_global_dct.d[key].wrd)
        self.var_fav = tk.BooleanVar(value=_0_global_dct.d[key].fav)

        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_wrd = ttk.Label(self.frame_main, text='Слово:', style='Default.TLabel')
        self.scrollbar_wrd = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_wrd = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_wrd.set,
                               font=('StdFont', _0_global_fontsize), relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                               selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                               highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar_wrd.config(command=self.txt_wrd.yview)
        try:
            self.img_edit = tk.PhotoImage(file=img_edit)
            self.btn_wrd_edt = ttk.Button(self.frame_main, image=self.img_edit, command=self.wrd_edt,
                                          takefocus=False, style='Image.TButton')
        except:
            self.btn_wrd_edt = ttk.Button(self.frame_main, text='изм.', command=self.wrd_edt, width=4,
                                          takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_wrd_edt = ttip.Hovertip(self.btn_wrd_edt, 'Изменить слово', hover_delay=500)
        #
        self.lbl_tr = ttk.Label(self.frame_main, text='Перевод:', style='Default.TLabel')
        self.scrollbar_tr = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_tr = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_tr.set,
                              font=('StdFont', _0_global_fontsize), relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                              selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                              highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar_tr.config(command=self.txt_tr.yview)
        self.frame_btns_tr = ttk.Frame(self.frame_main, style='Invis.TFrame')
        # { {
        try:
            self.img_add = tk.PhotoImage(file=img_add)
            self.btn_tr_add = ttk.Button(self.frame_btns_tr, image=self.img_add, command=self.tr_add,
                                         takefocus=False, style='Image.TButton')
        except:
            self.btn_tr_add = ttk.Button(self.frame_btns_tr, text='+', command=self.tr_add, width=2,
                                         takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_tr_add = ttip.Hovertip(self.btn_tr_add, 'Добавить перевод', hover_delay=500)
        try:
            self.img_delete = tk.PhotoImage(file=img_delete)
            self.btn_tr_del = ttk.Button(self.frame_btns_tr, image=self.img_delete, command=self.tr_del,
                                         takefocus=False, style='Image.TButton')
        except:
            self.btn_tr_del = ttk.Button(self.frame_btns_tr, text='-', command=self.tr_del, width=2,
                                         takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_tr_del = ttip.Hovertip(self.btn_tr_del, 'Удалить перевод', hover_delay=500)
        # } }
        self.lbl_notes = ttk.Label(self.frame_main, text='Сноски:', style='Default.TLabel')
        self.scrollbar_notes = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_notes = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_notes.set,
                                 font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                 selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                 highlightbackground=ST_BORDERCOLOR[th], relief='solid')
        self.scrollbar_notes.config(command=self.txt_notes.yview)
        self.frame_btns_notes = ttk.Frame(self.frame_main, style='Invis.TFrame')
        # { {
        try:
            self.btn_note_add = ttk.Button(self.frame_btns_notes, image=self.img_add, command=self.note_add,
                                            takefocus=False, style='Image.TButton')
        except:
            self.btn_note_add = ttk.Button(self.frame_btns_notes, text='+', command=self.note_add, width=2,
                                            takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_note_add = ttip.Hovertip(self.btn_note_add, 'Добавить сноску', hover_delay=500)
        try:
            self.btn_note_del = ttk.Button(self.frame_btns_notes, image=self.img_delete, command=self.note_del,
                                            takefocus=False, style='Image.TButton')
        except:
            self.btn_note_del = ttk.Button(self.frame_btns_notes, text='-', command=self.note_del, width=2,
                                            takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_note_del = ttip.Hovertip(self.btn_note_del, 'Удалить сноску', hover_delay=500)
        # } }
        self.lbl_frm = ttk.Label(self.frame_main, text='Формы слова:', style='Default.TLabel')
        self.scrollbar_frm = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_frm = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_frm.set,
                               font=('StdFont', _0_global_fontsize), relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                               selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                               highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar_frm.config(command=self.txt_frm.yview)
        self.frame_btns_frm = ttk.Frame(self.frame_main, style='Invis.TFrame')
        # { {
        try:
            self.btn_frm_add = ttk.Button(self.frame_btns_frm, image=self.img_add, command=self.frm_add,
                                          takefocus=False, style='Image.TButton')
        except:
            self.btn_frm_add = ttk.Button(self.frame_btns_frm, text='+', command=self.frm_add, width=2,
                                          takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_frm_add = ttip.Hovertip(self.btn_frm_add, 'Добавить словоформу', hover_delay=500)
        try:
            self.btn_frm_del = ttk.Button(self.frame_btns_frm, image=self.img_delete, command=self.frm_del,
                                          takefocus=False, style='Image.TButton')
        except:
            self.btn_frm_del = ttk.Button(self.frame_btns_frm, text='-', command=self.frm_del, width=2,
                                          takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_frm_del = ttip.Hovertip(self.btn_frm_del, 'Удалить словоформу', hover_delay=500)
        try:
            self.btn_frm_edt = ttk.Button(self.frame_btns_frm, image=self.img_edit, command=self.frm_edt,
                                          takefocus=False, style='Image.TButton')
        except:
            self.btn_frm_edt = ttk.Button(self.frame_btns_frm, text='изм.', command=self.frm_edt, width=4,
                                          takefocus=False, style='Default.TButton')
        else:
            self.tip_btn_frm_edt = ttip.Hovertip(self.btn_frm_edt, 'Изменить словоформу', hover_delay=500)
        # } }
        self.lbl_fav = ttk.Label(self.frame_main, text='Избранное:', style='Default.TLabel')
        self.check_fav = ttk.Checkbutton(self.frame_main, variable=self.var_fav, command=self.set_fav,
                                         style='Default.TCheckbutton')
        # }
        self.btn_back = ttk.Button(self, text='Закончить', command=self.back,
                                   takefocus=False, style='Default.TButton')
        self.btn_delete = ttk.Button(self, text='Удалить статью', command=self.delete,
                                     takefocus=False, style='No.TButton')
        #
        self.frame_main.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        # {
        self.lbl_wrd.grid(      row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.txt_wrd.grid(      row=0, column=1, padx=(0, 1), pady=(6, 3), sticky='W')
        self.scrollbar_wrd.grid(row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.btn_wrd_edt.grid(  row=0, column=3, padx=(3, 6), pady=(6, 3), sticky='W')
        #
        self.lbl_tr.grid(       row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.txt_tr.grid(       row=1, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.scrollbar_tr.grid( row=1, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.frame_btns_tr.grid(row=1, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        # { {
        self.btn_tr_add.grid(row=0, column=0, padx=(0, 1), pady=0)
        self.btn_tr_del.grid(row=0, column=1, padx=(1, 0), pady=0)
        # } }
        self.lbl_notes.grid(       row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.txt_notes.grid(       row=2, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.scrollbar_notes.grid( row=2, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.frame_btns_notes.grid(row=2, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        # { {
        self.btn_note_add.grid(row=0, column=0, padx=(0, 1), pady=0)
        self.btn_note_del.grid(row=0, column=1, padx=(1, 0), pady=0)
        # } }
        self.lbl_frm.grid(       row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.txt_frm.grid(       row=3, column=1, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.scrollbar_frm.grid( row=3, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.frame_btns_frm.grid(row=3, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        # { {
        self.btn_frm_add.grid(row=0, column=0, padx=(0, 1), pady=0)
        self.btn_frm_del.grid(row=0, column=1, padx=(1, 1), pady=0)
        self.btn_frm_edt.grid(row=0, column=2, padx=(1, 0), pady=0)
        # } }
        self.lbl_fav.grid(  row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_fav.grid(row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.btn_back.grid(  row=1, column=0, padx=(0, 1), pady=(0, 6))
        self.btn_delete.grid(row=1, column=1, padx=(0, 6), pady=(0, 6))

        self.refresh()

    # Изменить слово
    def wrd_edt(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новое слово', default_value=_0_global_dct.d[self.dct_key].wrd,
                             check_answer_function=lambda wnd, val: check_wrd_edit(wnd, key_to_wrd(self.dct_key), val))
        closed, new_wrd = window.open()
        if closed:
            return
        new_wrd = encode_special_combinations(new_wrd)

        self.dct_key = _0_global_dct.edit_wrd(self, self.dct_key, new_wrd)
        if not self.dct_key:
            return

        _0_global_has_progress = True
        self.refresh()

    # Добавить перевод
    def tr_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новый перевод',
                             check_answer_function=lambda wnd, val: check_tr(wnd, _0_global_dct.d[self.dct_key].tr,
                                                                             val, key_to_wrd(self.dct_key)))
        closed, tr = window.open()
        if closed:
            return
        tr = encode_special_combinations(tr)

        _0_global_dct.add_tr(self.dct_key, tr)

        _0_global_has_progress = True
        self.refresh()

    # Удалить перевод
    def tr_del(self):
        global _0_global_has_progress

        window_choose = PopupChooseW(self, _0_global_dct.d[self.dct_key].tr, 'Выберите, какой перевод хотите удалить',
                                     default_value=_0_global_dct.d[self.dct_key].tr[0],
                                     combo_width=width(_0_global_dct.d[self.dct_key].tr, 5, 100))
        closed, tr = window_choose.open()
        if closed:
            return

        _0_global_dct.delete_tr(self.dct_key, tr)

        _0_global_has_progress = True
        self.refresh()

    # Добавить сноску
    def note_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите сноску',
                             check_answer_function=lambda wnd, val: check_note(wnd, _0_global_dct.d[self.dct_key].notes,
                                                                               val, key_to_wrd(self.dct_key)))
        closed, note = window.open()
        if closed:
            return
        note = encode_special_combinations(note)

        _0_global_dct.add_note(self.dct_key, note)

        _0_global_has_progress = True
        self.refresh()

    # Удалить сноску
    def note_del(self):
        global _0_global_has_progress

        window_choose = PopupChooseW(self, _0_global_dct.d[self.dct_key].notes,
                                     'Выберите, какую сноску хотите удалить',
                                     default_value=_0_global_dct.d[self.dct_key].notes[0],
                                     combo_width=width(_0_global_dct.d[self.dct_key].notes, 5, 100))
        closed, note = window_choose.open()
        if closed:
            return

        _0_global_dct.delete_note(self.dct_key, note)

        _0_global_has_progress = True
        self.refresh()

    # Добавить словоформу
    def frm_add(self):
        global _0_global_has_progress

        if not _0_global_categories:
            warning(self, 'Отсутствуют категории слов!\n'
                          'Чтобы их добавить, перейдите в\n'
                          'Настройки/Настройки словаря/Грамматические категории')
            return

        window_form = AddFormW(self, self.dct_key, combo_width=width(tuple(_0_global_categories.keys()),
                                                                           5, 100))  # Создание словоформы
        frm_key, frm = window_form.open()
        if not frm_key:
            return
        frm = encode_special_combinations(frm)

        _0_global_dct.add_frm(self.dct_key, frm_key, frm)

        _0_global_has_progress = True
        self.refresh()

    # Изменить словоформу
    def frm_edt(self):
        global _0_global_has_progress

        frm_keys = tuple(_0_global_dct.d[self.dct_key].forms.keys())
        variants = tuple(f'[{tpl(key)}] {_0_global_dct.d[self.dct_key].forms[key]}' for key in frm_keys)

        window_choose = PopupChooseW(self, variants, 'Выберите словоформу, которую хотите изменить',
                                     default_value=variants[0], combo_width=width(variants, 5, 100))
        closed, answer = window_choose.open()
        if closed:
            return
        index = variants.index(answer)
        selected_key = frm_keys[index]

        window_entry = PopupEntryW(self, 'Введите форму слова',
                                   default_value=_0_global_dct.d[self.dct_key].forms[selected_key],
                                   check_answer_function=lambda wnd, val:
                                   check_not_void(wnd, val, 'Словоформа должна содержать хотя бы один символ!'))
        closed, new_frm = window_entry.open()
        if closed:
            return
        new_frm = encode_special_combinations(new_frm)

        _0_global_dct.d[self.dct_key].forms[selected_key] = new_frm

        _0_global_has_progress = True
        self.refresh()

    # Удалить словоформу
    def frm_del(self):
        global _0_global_has_progress

        frm_keys = tuple(_0_global_dct.d[self.dct_key].forms.keys())
        variants = tuple(f'[{tpl(key)}] {_0_global_dct.d[self.dct_key].forms[key]}' for key in frm_keys)

        window_choose = PopupChooseW(self, variants, 'Выберите словоформу, которую хотите удалить',
                                     default_value=variants[0], combo_width=width(variants, 5, 100))
        closed, answer = window_choose.open()
        if closed:
            return
        index = variants.index(answer)
        selected_key = frm_keys[index]

        _0_global_dct.delete_frm(self.dct_key, selected_key)

        _0_global_has_progress = True
        self.refresh()

    # Добавить в избранное/убрать из избранного
    def set_fav(self):
        _0_global_dct.d[self.dct_key].fav = self.var_fav.get()

    # Удалить статью
    def delete(self):
        global _0_global_has_progress

        window = PopupDialogueW(self, 'Вы уверены, что хотите удалить эту статью?', set_enter_on_btn='none')
        answer = window.open()
        if answer:
            _0_global_dct.delete_entry(self.dct_key)
            _0_global_has_progress = True
            self.destroy()

    # Закрыть настройки
    def back(self):
        self.destroy()

    # Обновить поля
    def refresh(self):
        height_w = max(min(height(_0_global_dct.d[self.dct_key].wrd,            self.line_width), self.max_height_w), 1)
        height_t = max(min(height(_0_global_dct.d[self.dct_key].tr_to_str(),    self.line_width), self.max_height_t), 1)
        height_n = max(min(height(_0_global_dct.d[self.dct_key].notes_to_str(), self.line_width), self.max_height_n), 1)
        height_f = max(min(height(_0_global_dct.d[self.dct_key].frm_to_str(),   self.line_width), self.max_height_f), 1)

        self.txt_wrd  ['height'] = height_w
        self.txt_tr   ['height'] = height_t
        self.txt_notes['height'] = height_n
        self.txt_frm  ['height'] = height_f

        self.txt_wrd['state'] = 'normal'
        self.txt_wrd.delete(1.0, tk.END)
        self.txt_wrd.insert(tk.END, _0_global_dct.d[self.dct_key].wrd)
        self.txt_wrd['state'] = 'disabled'

        self.txt_tr['state'] = 'normal'
        self.txt_tr.delete(1.0, tk.END)
        self.txt_tr.insert(tk.END, _0_global_dct.d[self.dct_key].tr_to_str())
        self.txt_tr['state'] = 'disabled'

        self.txt_notes['state'] = 'normal'
        self.txt_notes.delete(1.0, tk.END)
        self.txt_notes.insert(tk.END, _0_global_dct.d[self.dct_key].notes_to_str())
        self.txt_notes['state'] = 'disabled'

        self.txt_frm['state'] = 'normal'
        self.txt_frm.delete(1.0, tk.END)
        self.txt_frm.insert(tk.END, _0_global_dct.d[self.dct_key].frm_to_str())
        self.txt_frm['state'] = 'disabled'

        self.btn_tr_del.grid(     row=0, column=1, padx=(1, 0), pady=0)
        self.btn_note_del.grid(  row=0, column=1, padx=(1, 0), pady=0)
        self.btn_frm_del.grid(    row=0, column=1, padx=(1, 1), pady=0)
        self.btn_frm_edt.grid(    row=0, column=2, padx=(1, 0), pady=0)
        self.scrollbar_wrd.grid(  row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.scrollbar_tr.grid(   row=1, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_notes.grid(row=2, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_frm.grid(  row=3, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')

        if _0_global_dct.d[self.dct_key].count_t < 2:
            self.btn_tr_del.grid_remove()
        if _0_global_dct.d[self.dct_key].count_n < 1:
            self.btn_note_del.grid_remove()
        if _0_global_dct.d[self.dct_key].count_f < 1:
            self.btn_frm_del.grid_remove()
            self.btn_frm_edt.grid_remove()

        if height_w < self.max_height_w:
            self.scrollbar_wrd.grid_remove()
        if height_t < self.max_height_t:
            self.scrollbar_tr.grid_remove()
        if height_n < self.max_height_n:
            self.scrollbar_notes.grid_remove()
        if height_f < self.max_height_f:
            self.scrollbar_frm.grid_remove()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_back.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно добавления статьи
class AddW(tk.Toplevel):
    def __init__(self, parent, wrd: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Add an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.dct_key = None

        self.var_wrd = tk.StringVar(value=wrd)
        self.var_tr = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        self.lbl_wrd = ttk.Label(self, text='Введите слово:', style='Default.TLabel')
        self.entry_wrd = ttk.Entry(self, textvariable=self.var_wrd, width=60, validate='all', style='Default.TEntry')
        self.lbl_tr = ttk.Label(self, text='Введите перевод:', style='Default.TLabel')
        self.entry_tr = ttk.Entry(self, textvariable=self.var_tr, width=60, validate='all', style='Default.TEntry')
        self.lbl_fav = ttk.Label(self, text='Избранное:', style='Default.TLabel')
        self.check_fav = ttk.Checkbutton(self, variable=self.var_fav, style='Default.TCheckbutton')
        self.btn_add = ttk.Button(self, text='Добавить', command=self.add, takefocus=False, style='Default.TButton')

        self.lbl_wrd.grid(  row=0, column=0,     padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_wrd.grid(row=0, column=1,     padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr.grid(   row=1, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr.grid( row=1, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_fav.grid(  row=2, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.check_fav.grid(row=2, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.btn_add.grid(  row=3, columnspan=2, padx=6,      pady=(0, 6))

        btn_disable(self.btn_add)

        # При незаполненных полях нельзя нажать кнопку
        def validate_entries(value: str, second_value: str):
            if value == '' or second_value == '':
                btn_disable(self.btn_add)
            else:
                btn_enable(self.btn_add, self.add)
            return True

        self.vcmd_wrd = (self.register(lambda value: validate_entries(value, self.var_tr.get())), '%P')
        self.vcmd_tr = (self.register(lambda value: validate_entries(value, self.var_wrd.get())), '%P')
        self.entry_wrd['validatecommand'] = self.vcmd_wrd
        self.entry_tr['validatecommand'] = self.vcmd_tr

    # Добавление статьи
    def add(self):
        global _0_global_has_progress

        self.dct_key = _0_global_dct.add_entry(self, encode_special_combinations(self.var_wrd.get()),
                                               encode_special_combinations(self.var_tr.get()))
        if not self.dct_key:
            return
        _0_global_dct.d[self.dct_key].fav = self.var_fav.get()

        _0_global_has_progress = True
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_wrd.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_add.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.dct_key


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Settings')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.parent = parent
        self.current_tab = 1  # Текущая вкладка (1 или 2)
        self.has_ctg_changes = False
        self.has_spec_comb_changes = False
        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        self.var_mgsp = tk.StringVar(value=str(_0_global_min_good_score_perc))
        self.var_check_register = tk.BooleanVar(value=bool(_0_global_check_register))
        self.var_show_updates = tk.BooleanVar(value=bool(_0_global_show_updates))
        self.var_show_typo_button = tk.BooleanVar(value=bool(_0_global_with_typo))
        self.var_theme = tk.StringVar(value=th)
        self.var_fontsize = tk.StringVar(value=str(_0_global_fontsize))

        # Только целые числа от 0 до 100
        self.vcmd = (self.register(validate_percent), '%P')

        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tab_local = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.lbl_dct_name = ttk.Label(self, text=split_text(f'Открыт словарь "{_0_global_dct_savename}"',
                                                            30, align_left=False),
                                      justify='center', style='Default.TLabel')
        self.tabs.add(self.tab_local, text='Настройки словаря')
        # {
        self.frame_mgsp = ttk.Frame(self.tab_local, style='Default.TFrame')
        # { {
        try:
            self.img_about = tk.PhotoImage(file=img_about)
        except:
            self.btn_about_mgsp = ttk.Button(self.frame_mgsp, text='?', command=self.about_mgsp,
                                             width=2, takefocus=False, style='Default.TButton')
        else:
            self.btn_about_mgsp = ttk.Button(self.frame_mgsp, image=self.img_about, command=self.about_mgsp,
                                             width=2, takefocus=False, style='Image.TButton')
        self.lbl_mgsp = ttk.Label(self.frame_mgsp, text='Минимальный приемлемый процент угадываний слова:',
                                  style='Default.TLabel')
        self.entry_mgsp = ttk.Entry(self.frame_mgsp, textvariable=self.var_mgsp, width=5,
                                    validate='key', validatecommand=self.vcmd, style='Default.TEntry')
        # } }
        self.frame_check_register = ttk.Frame(self.tab_local, style='Default.TFrame')
        # { {
        self.lbl_check_register = ttk.Label(self.frame_check_register,
                                            text='Учитывать регистр букв при проверке ответа во время учёбы:',
                                            style='Default.TLabel')
        self.check_check_register = ttk.Checkbutton(self.frame_check_register, variable=self.var_check_register,
                                                    style='Default.TCheckbutton')
        # } }
        self.btn_forms = ttk.Button(self.tab_local, text='Грамматические категории', command=self.categories_settings,
                                    takefocus=False, style='Default.TButton')
        #
        self.btn_special_combinations = ttk.Button(self.tab_local, text='Специальные комбинации',
                                                   command=self.special_combinations_settings,
                                                   takefocus=False, style='Default.TButton')
        self.lbl_save_warn = ttk.Label(self.tab_local,
                                       text='При сохранении настроек словаря, сохраняется и сам словарь!',
                                       style='Warn.TLabel')
        # }
        self.tab_global = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.tabs.add(self.tab_global, text='Настройки программы')
        # {
        self.frame_show_updates = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_show_updates = ttk.Label(self.frame_show_updates, text='Сообщать о выходе новых версий:',
                                          style='Default.TLabel')
        self.check_show_updates = ttk.Checkbutton(self.frame_show_updates, variable=self.var_show_updates,
                                                  style='Default.TCheckbutton')
        # } }
        self.frame_show_typo_button = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        try:
            self.btn_about_typo = ttk.Button(self.frame_show_typo_button, image=self.img_about,
                                             width=2, command=self.about_typo, takefocus=False, style='Image.TButton')
        except:
            self.btn_about_typo = ttk.Button(self.frame_show_typo_button, text='?', command=self.about_typo,
                                             width=2, takefocus=False, style='Default.TButton')
        self.lbl_show_typo_button = ttk.Label(self.frame_show_typo_button, text='Показывать кнопку "Опечатка":',
                                              style='Default.TLabel')
        self.check_show_typo_button = ttk.Checkbutton(self.frame_show_typo_button, variable=self.var_show_typo_button,
                                                      style='Default.TCheckbutton')
        # } }
        self.frame_dcts = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_dcts = ttk.Label(self.frame_dcts, text='Существующие словари:', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self.frame_dcts, style='Vertical.TScrollbar')
        self.txt_dcts = tk.Text(self.frame_dcts, width=27, height=6, state='disabled', relief=ST_RELIEF_TEXT[th],
                                yscrollcommand=self.scrollbar.set, font=('StdFont', _0_global_fontsize),
                                bg=ST_BG_FIELDS[th], fg=ST_FG[th], highlightbackground=ST_BORDERCOLOR[th],
                                selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th])
        self.frame_dct_buttons = ttk.Frame(self.frame_dcts, style='Invis.TFrame')
        # { { {
        self.btn_dct_open = ttk.Button(self.frame_dct_buttons, text='Открыть словарь', command=self.dct_open,
                                       takefocus=False, style='Default.TButton')
        self.btn_dct_create = ttk.Button(self.frame_dct_buttons, text='Создать словарь', command=self.dct_create,
                                         takefocus=False, style='Default.TButton')
        self.btn_dct_rename = ttk.Button(self.frame_dct_buttons, text='Переименовать словарь', command=self.dct_rename,
                                         takefocus=False, style='Default.TButton')
        self.btn_dct_delete = ttk.Button(self.frame_dct_buttons, text='Удалить словарь', command=self.dct_delete,
                                         takefocus=False, style='Default.TButton')
        self.btn_dct_export = ttk.Button(self.frame_dct_buttons, text='Экспортировать словарь', command=self.dct_export,
                                         takefocus=False, style='Default.TButton')
        self.btn_dct_import = ttk.Button(self.frame_dct_buttons, text='Импортировать словарь', command=self.dct_import,
                                         takefocus=False, style='Default.TButton')
        # } } }
        self.lbl_dcts_warn = ttk.Label(self.frame_dcts, text='Изменения словарей сохраняются сразу!',
                                       style='Warn.TLabel')
        # } }
        self.frame_themes = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_themes = ttk.Label(self.frame_themes, text='Тема:', style='Default.TLabel')
        self.combo_themes = ttk.Combobox(self.frame_themes, textvariable=self.var_theme, values=THEMES, width=21,
                                         state='readonly', style='Default.TCombobox')
        self.lbl_themes_note = ttk.Label(self.frame_themes, text=f'Требуемая версия тем: {REQUIRED_THEME_VERSION}\n'
                                                                 f'Актуальные темы можно скачать здесь:',
                                         justify='left', style='Default.TLabel')
        self.txt_themes_note = tk.Text(self.frame_themes, height=1, width=47, relief='sunken', borderwidth=1,
                                       font=('StdFont', _0_global_fontsize), bg=ST_BG[th], fg=ST_FG[th],
                                       selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                       highlightbackground=ST_BORDERCOLOR[th])
        self.txt_themes_note.insert(tk.END, URL_RELEASES)
        self.txt_themes_note['state'] = 'disabled'
        self.btn_custom_theme = ttk.Button(self.frame_themes, text='Собственная тема', command=self.custom_theme,
                                           takefocus=False, style='Default.TButton')
        # } }
        self.frame_fontsize = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_fontsize = ttk.Label(self.frame_fontsize, text='Размер шрифта', style='Default.TLabel')
        try:
            self.img_plus = tk.PhotoImage(file=img_add)
        except:
            self.btn_fontsize_plus = ttk.Button(self.frame_fontsize, text='+', command=self.fontsize_plus,
                                                takefocus=False, width=2, state='normal', style='Default.TButton')
        else:
            self.btn_fontsize_plus = ttk.Button(self.frame_fontsize, image=self.img_plus, command=self.fontsize_plus,
                                                takefocus=False, width=2, state='normal', style='Image.TButton')
        try:
            self.img_minus = tk.PhotoImage(file=img_delete)
        except:
            self.btn_fontsize_minus = ttk.Button(self.frame_fontsize, text='-', command=self.fontsize_minus,
                                                 takefocus=False, width=2, state='normal', style='Default.TButton')
        else:
            self.btn_fontsize_minus = ttk.Button(self.frame_fontsize, image=self.img_minus, command=self.fontsize_minus,
                                                 takefocus=False, width=2, state='normal', style='Image.TButton')
        # } }
        # }
        self.btn_save = ttk.Button(self, text='Сохранить изменения', command=self.save,
                                   takefocus=False, style='Yes.TButton')
        self.btn_close = ttk.Button(self, text='Закрыть настройки', command=self.close,
                                    takefocus=False, style='No.TButton')

        self.lbl_dct_name.grid(row=0, columnspan=2, padx=6, pady=(6, 0))
        self.tabs.grid(        row=1, columnspan=2, padx=6, pady=(0, 6))
        #
        self.frame_mgsp.grid(row=0, padx=6, pady=6)
        # {
        self.btn_about_mgsp.grid(row=0, column=0, padx=(6, 0), pady=6, sticky='E')
        self.lbl_mgsp.grid(      row=0, column=1, padx=(3, 3), pady=6, sticky='E')
        self.entry_mgsp.grid(    row=0, column=2, padx=(0, 6), pady=6, sticky='W')
        # }
        self.frame_check_register.grid(row=1, padx=6, pady=6)
        # {
        self.lbl_check_register.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_check_register.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        # }
        self.btn_forms.grid(               row=2, padx=6, pady=6)
        self.btn_special_combinations.grid(row=3, padx=6, pady=6)
        self.lbl_save_warn.grid(           row=4, padx=6, pady=6, sticky='S')
        #
        self.frame_show_updates.grid(row=0, padx=6, pady=6)
        # {
        self.lbl_show_updates.grid(  row=0, column=0, padx=(6, 0), pady=6)
        self.check_show_updates.grid(row=0, column=1, padx=(0, 6), pady=6)
        # }
        self.frame_show_typo_button.grid(row=1, padx=6, pady=6)
        # {
        self.btn_about_typo.grid(        row=0, column=0, padx=(6, 0), pady=6)
        self.lbl_show_typo_button.grid(  row=0, column=1, padx=(3, 3), pady=6)
        self.check_show_typo_button.grid(row=0, column=2, padx=(0, 6), pady=6)
        # }
        self.frame_dcts.grid(row=2, padx=6, pady=6)
        # {
        self.lbl_dcts.grid(         row=0,            column=0, columnspan=2, padx=6,      pady=(6, 0))
        self.txt_dcts.grid(         row=1, rowspan=2, column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(        row=1, rowspan=2, column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_dct_buttons.grid(row=1,            column=2,               padx=1,      pady=1)
        # { {
        self.btn_dct_open.grid(  row=0, column=0, padx=6, pady=6, sticky='WE')
        self.btn_dct_create.grid(row=0, column=1, padx=6, pady=6, sticky='WE')
        self.btn_dct_rename.grid(row=1, column=0, padx=6, pady=6, sticky='WE')
        self.btn_dct_delete.grid(row=1, column=1, padx=6, pady=6, sticky='WE')
        self.btn_dct_export.grid(row=2, column=0, padx=6, pady=6, sticky='WE')
        self.btn_dct_import.grid(row=2, column=1, padx=6, pady=6, sticky='WE')
        # } }
        self.lbl_dcts_warn.grid(row=2, column=2, padx=6, pady=6, sticky='N')
        # }
        self.frame_themes.grid(row=3, padx=6, pady=6)
        # {
        self.lbl_themes.grid(      row=0, column=0, padx=(6, 1),  pady=6)
        self.combo_themes.grid(    row=0, column=1, padx=0,       pady=6)
        self.lbl_themes_note.grid( row=0, column=2, padx=(6, 12), pady=(6, 0), sticky='W')
        self.btn_custom_theme.grid(row=1, column=1, padx=0,       pady=(0, 6), sticky='W')
        self.txt_themes_note.grid( row=1, column=2, padx=(6, 12), pady=(0, 6), sticky='W')
        # }
        self.frame_fontsize.grid(row=4, padx=6, pady=6)
        # {
        self.lbl_fontsize.grid(      row=0, column=0, padx=(6, 3), pady=6)
        self.btn_fontsize_plus.grid( row=0, column=1, padx=(0, 3), pady=6)
        self.btn_fontsize_minus.grid(row=0, column=2, padx=(0, 6), pady=6)
        # }
        #
        self.btn_save.grid( row=4, column=0, padx=(6, 3), pady=(0, 6))
        self.btn_close.grid(row=4, column=1, padx=(0, 6), pady=(0, 6))

        self.scrollbar.config(command=self.txt_dcts.yview)

        self.print_dct_list()
        self.refresh_fontsize_buttons()

    # Справка о МППУ
    def about_mgsp(self):
        PopupImgW(self, img_about_mgsp, 'Статьи, у которых процент угадывания ниже этого значения,\n'
                                        'будут считаться более сложными.\n'
                                        'При выборе режима учёбы "Все слова (чаще сложные)"\n'
                                        'такие слова будут чаще попадаться.').open()

    # Настройки категорий
    def categories_settings(self):
        self.has_ctg_changes = CategoriesSettingsW(self).open() or self.has_ctg_changes

    # Настройки специальных комбинаций
    def special_combinations_settings(self):
        self.has_spec_comb_changes = SpecialCombinationsSettingsW(self).open() or self.has_spec_comb_changes

    # Справка о кнопке "Опечатка"
    def about_typo(self):
        PopupImgW(self, img_about_typo, 'Если функция включена, то\n'
                                        'когда вы неверно отвечаете при учёбе,\n'
                                        'появляется кнопка "Просто опечатка".\n'
                                        'При её нажатии, ошибка не засчитывается.\n'
                                        'Срабатывает при нажатии на Tab.').open()

    # Открыть словарь
    def dct_open(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc,\
            _0_global_categories, _0_global_special_combinations, _0_global_check_register, _0_global_has_progress

        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                if base_name != _0_global_dct_savename:
                    saves_list += [base_name]

        window = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите открыть',
                              default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, savename = window.open()
        if closed:
            return

        # Если есть прогресс, то предлагается его сохранить
        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(_0_global_dct_savename), _0_global_has_progress)

        _0_global_dct = Dictionary()
        savename = upload_dct(self, _0_global_dct, savename, 'Отмена')
        if not savename:
            self.destroy()  # Если была попытка открыть повреждённый словарь, то при сохранении настроек, текущий словарь стёрся бы
            return
        _0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations, _0_global_check_register =\
            upload_local_settings(savename)
        _0_global_dct_savename = savename
        save_dct_name()

        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(savename)

        self.has_ctg_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

        self.refresh()

    # Создать словарь
    def dct_create(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc,\
            _0_global_categories, _0_global_special_combinations, _0_global_check_register, _0_global_has_progress

        window = PopupEntryW(self, 'Введите название нового словаря', check_answer_function=check_dct_savename)
        closed, savename = window.open()
        if closed:
            return

        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(_0_global_dct_savename), _0_global_has_progress)

        _0_global_dct_savename = savename
        save_dct_name()
        _0_global_dct = Dictionary()
        _0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations, _0_global_check_register =\
            create_dct(_0_global_dct, savename)

        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(savename)

        self.has_ctg_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

        self.refresh()

    # Переименовать словарь
    def dct_rename(self):
        global _0_global_dct_savename

        saves_count = 0
        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                saves_list += [base_name]
                saves_count += 1
        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите переименовать',
                                     default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, old_savename = window_choose.open()
        if closed:
            return

        window_rename = PopupEntryW(self, 'Введите название нового словаря', check_answer_function=check_dct_savename)
        closed, new_savename = window_rename.open()
        if closed:
            return

        old_filename = dct_filename(old_savename)
        new_filename = dct_filename(new_savename)
        os.rename(os.path.join(SAVES_PATH, old_filename), os.path.join(SAVES_PATH, new_filename))
        os.rename(os.path.join(LOCAL_SETTINGS_PATH, old_filename), os.path.join(LOCAL_SETTINGS_PATH, new_filename))
        if _0_global_dct_savename == old_savename:
            _0_global_dct_savename = new_savename
            save_dct_name()
            # Обновляем надписи с названием открытого словаря
            self.refresh_open_dct_name(new_savename)
        print(f'Словарь "{old_savename}" успешно переименован в "{new_savename}"')

        self.print_dct_list()

    # Удалить словарь
    def dct_delete(self):
        saves_list = []
        for filename in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(filename)
            if ext == '.txt':
                if base_name != _0_global_dct_savename:
                    saves_list += [base_name]

        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите удалить',
                                     default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, savename = window_choose.open()
        if closed:
            return

        window_confirm = PopupDialogueW(self, f'Словарь "{savename}" будет безвозвратно удалён!\n'
                                              f'Хотите продолжить?',
                                        set_enter_on_btn='none')
        answer = window_confirm.open()
        if not answer:
            return

        filename = dct_filename(savename)
        os.remove(os.path.join(SAVES_PATH, filename))
        os.remove(os.path.join(LOCAL_SETTINGS_PATH, filename))
        PopupMsgW(self, f'Словарь "{savename}" успешно удалён').open()

        self.print_dct_list()

    # Экспортировать словарь
    def dct_export(self):
        saves_count = 0
        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                saves_list += [base_name]
                saves_count += 1
        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите экспортировать',
                                     default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, savename = window_choose.open()
        if closed:
            return

        dst_path = askdirectory(title='Выберите папку для сохранения')
        if dst_path == '':
            return

        dct_export(savename, dst_path)

    # Импортировать словарь
    def dct_import(self):
        src_path = askdirectory(title='Выберите папку сохранения')
        if src_path == '':
            return

        default_savename = re.split(r'[\\/]', src_path)[-1]
        window = PopupEntryW(self, 'Введите название для словаря', default_value=default_savename,
                             check_answer_function=check_dct_savename)
        closed, savename = window.open()
        if closed:
            return

        dct_import(self, savename, src_path)

        self.refresh()

    # Задать пользовательскую тему
    def custom_theme(self):
        CustomThemeSettingsW(self).open()
        upload_custom_theme()
        if th == CUSTOM_TH:
            self.save_theme()

    # Увеличить шрифт
    def fontsize_plus(self):
        global _0_global_fontsize

        _0_global_fontsize += 1

        self.parent.set_ttk_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.txt_dcts.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                highlightbackground=ST_BORDERCOLOR[th], relief=ST_RELIEF_TEXT[th])
        self.txt_themes_note.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG[th], fg=ST_FG[th],
                                       selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                       highlightbackground=ST_BORDERCOLOR[th])

        self.refresh_fontsize_buttons()

    # Уменьшить шрифт
    def fontsize_minus(self):
        global _0_global_fontsize

        _0_global_fontsize -= 1

        self.parent.set_ttk_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.txt_dcts.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                highlightbackground=ST_BORDERCOLOR[th], relief=ST_RELIEF_TEXT[th])
        self.txt_themes_note.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG[th], fg=ST_FG[th],
                                       selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                       highlightbackground=ST_BORDERCOLOR[th])

        self.refresh_fontsize_buttons()

    # Сохранить настройки
    def save(self):
        global _0_global_has_progress

        self.save_mgsp()
        self.save_check_register()
        self.save_show_updates()
        self.save_show_typo_button()
        self.save_theme()

        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        save_local_settings(_0_global_min_good_score_perc, _0_global_check_register, _0_global_categories,
                            dct_filename(_0_global_dct_savename))
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th,
                             _0_global_fontsize)

        if self.has_local_changes():
            save_dct(_0_global_dct, dct_filename(_0_global_dct_savename))

        self.has_ctg_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

    # Закрыть настройки без сохранения
    def close(self):
        if self.has_changes():
            window = PopupDialogueW(self, 'У вас есть несохранённые изменения?\n'
                                          'Всё равно закрыть?')
            answer = window.open()
            if not answer:
                return
        self.destroy()

    # Вывод существующих словарей
    def print_dct_list(self):
        self.txt_dcts['state'] = 'normal'
        self.txt_dcts.delete(1.0, tk.END)

        has_only_one_dct = True
        for filename in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(filename)
            if ext == '.txt':
                if base_name == _0_global_dct_savename:
                    self.txt_dcts.insert(tk.END, f'"{base_name}" (ОТКРЫТ)\n')
                else:
                    self.txt_dcts.insert(tk.END, f'"{base_name}"\n')
                    has_only_one_dct = False
        self.txt_dcts['state'] = 'disabled'

        if has_only_one_dct:
            btn_disable(self.btn_dct_open)
            btn_disable(self.btn_dct_delete)
        else:
            btn_enable(self.btn_dct_open, self.dct_open)
            btn_enable(self.btn_dct_delete, self.dct_delete)

    # Обновить кнопки изменения размера шрифта
    def refresh_fontsize_buttons(self):
        if _0_global_fontsize == FONTSIZE_MIN:
            btn_disable(self.btn_fontsize_minus)
        else:
            btn_enable(self.btn_fontsize_minus, self.fontsize_minus, style='Image')

        if _0_global_fontsize == FONTSIZE_MAX:
            btn_disable(self.btn_fontsize_plus)
        else:
            btn_enable(self.btn_fontsize_plus, self.fontsize_plus, style='Image')

    # Обновить настройки при открытии другого словаря
    def refresh(self):
        self.var_mgsp.set(str(_0_global_min_good_score_perc))
        self.print_dct_list()

    # Сохранить значение МППУ
    def save_mgsp(self):
        global _0_global_min_good_score_perc

        val = self.var_mgsp.get()
        if val == '':
            _0_global_min_good_score_perc = 0
        else:
            _0_global_min_good_score_perc = int(val)

    # Учитывать/не учитывать регистр букв при проверке введённого ответа при учёбе
    def save_check_register(self):
        global _0_global_check_register

        _0_global_check_register = int(self.var_check_register.get())  # 0 или 1

    # Разрешить/запретить сообщать о новых версиях
    def save_show_updates(self):
        global _0_global_show_updates

        _0_global_show_updates = int(self.var_show_updates.get())  # 0 или 1

    # Показывать/скрывать кнопку "Опечатка" при неверном ответе в учёбе
    def save_show_typo_button(self):
        global _0_global_with_typo

        _0_global_with_typo = int(self.var_show_typo_button.get())  # 0 или 1

    # Установить выбранную тему
    def save_theme(self):
        global th

        th = self.var_theme.get()

        self.parent.set_ttk_styles()  # Установка ttk-стилей
        upload_theme_img(th)  # Загрузка изображений темы

        # Установка изображений
        try:
            self.img_about = tk.PhotoImage(file=img_about)
        except:
            self.btn_about_mgsp.configure(text='?', compound='text', style='Default.TButton')
            self.btn_about_typo.configure(text='?', compound='text', style='Default.TButton')
        else:
            self.btn_about_mgsp.configure(image=self.img_about, compound='image', style='Image.TButton')
            self.btn_about_typo.configure(image=self.img_about, compound='image', style='Image.TButton')
        try:
            self.img_plus = tk.PhotoImage(file=img_add)
        except:
            self.btn_fontsize_plus.configure(text='+', compound='text', style='Default.TButton')
        else:
            self.btn_fontsize_plus.configure(image=self.img_plus, compound='image', style='Image.TButton')
        try:
            self.img_minus = tk.PhotoImage(file=img_delete)
        except:
            self.btn_fontsize_minus.configure(text='-', compound='text', style='Default.TButton')
        else:
            self.btn_fontsize_minus.configure(image=self.img_minus, compound='image', style='Image.TButton')

        # Установка некоторых стилей для окна настроек
        self.configure(bg=ST_BG[th])
        self.txt_dcts.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                                selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                highlightbackground=ST_BORDERCOLOR[th], relief=ST_RELIEF_TEXT[th])
        self.txt_themes_note.configure(font=('StdFont', _0_global_fontsize), bg=ST_BG[th], fg=ST_FG[th],
                                       selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                                       highlightbackground=ST_BORDERCOLOR[th])

        # Установка фона для главного окна
        self.parent.configure(bg=ST_BG[th])

        # Установка фона для окна уведомления об обновлении
        try:
            _0_global_window_last_version.configure(bg=ST_BG[th])
        except:  # Если окно обновления не открыто
            pass

    # Были ли изменения локальных настроек
    def has_local_changes(self):
        return self.has_ctg_changes or\
            self.has_spec_comb_changes or\
            int(self.var_check_register.get()) != _0_global_check_register or\
            int(f'0{self.var_mgsp.get()}') != _0_global_min_good_score_perc  # Если self.var_mgsp.get() == '', то 0

    # Были ли изменения настроек
    def has_changes(self):
        return self.has_local_changes() or\
            int(self.var_show_updates.get()) != _0_global_show_updates or\
            int(self.var_show_typo_button.get()) != _0_global_with_typo or\
            self.var_theme.get() != th or\
            int(self.var_fontsize.get()) != _0_global_fontsize

    # Обновить надписи с названием открытого словаря
    def refresh_open_dct_name(self, savename):
        self.lbl_dct_name.config(text=split_text(f'Открыт словарь "{savename}"', 30, align_left=False))
        self.parent.lbl_dct_name.config(text=f'Открыт словарь\n'
                                             f'"{split_text(savename, 20, align_left=False)}"')

    # Изменить размер окна в зависимости от открытой вкладки
    def resize_tabs(self):
        if self.current_tab == 1:
            self.frame_show_updates.grid(    row=0, padx=0, pady=0)
            self.frame_show_typo_button.grid(row=0, padx=0, pady=0)
            self.frame_dcts.grid(            row=0, padx=0, pady=0)
            self.frame_themes.grid(          row=0, padx=0, pady=0)

            self.frame_dcts.grid_remove()
            self.frame_themes.grid_remove()

            self.current_tab = 2
        else:
            self.frame_show_updates.grid(    row=0, padx=6, pady=6)
            self.frame_show_typo_button.grid(row=1, padx=6, pady=6)
            self.frame_dcts.grid(            row=2, padx=6, pady=6)
            self.frame_themes.grid(          row=3, padx=6, pady=6)

            self.current_tab = 1

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_mgsp.focus_set()
        self.bind('<Escape>', lambda event=None: self.btn_close.invoke())
        self.tabs.bind('<<NotebookTabChanged>>', lambda event=None: self.resize_tabs())

    def open(self):
        global _0_global_dct, _0_global_categories

        self.set_focus()

        self.grab_set()
        self.wait_window()

        _0_global_dct = copy.deepcopy(self.backup_dct)
        _0_global_categories = copy.deepcopy(self.backup_fp)


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_word = tk.StringVar(value='')

        self.set_ttk_styles()  # Установка ttk-стилей

        self.frame_head = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_header = ttk.Label(self.frame_head, text='Anenokil development presents', style='Header.TLabel')
        self.lbl_logo = ttk.Label(self.frame_head, text=PROGRAM_NAME, style='Logo.TLabel')
        # }
        self.frame_dct_name = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_dct_name = ttk.Label(self.frame_dct_name,
                                      text=f'Открыт словарь\n'
                                           f'"{split_text(_0_global_dct_savename, 20, align_left=False)}"',
                                      justify='center', style='Default.TLabel')
        # }
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_print = ttk.Button(self.frame_buttons, text='Просмотреть словарь', command=self.print,
                                    takefocus=False, style='Default.TButton')
        self.btn_learn = ttk.Button(self.frame_buttons, text='Учить слова', command=self.learn,
                                    takefocus=False, style='Default.TButton')
        self.frame_word = ttk.Frame(self.frame_buttons, style='Default.TFrame')
        # { {
        self.entry_word = ttk.Entry(self.frame_word, textvariable=self.var_word, width=30, style='Default.TEntry')
        self.btn_search = ttk.Button(self.frame_word, text='Найти статью', command=self.search,
                                     takefocus=False, style='Default.TButton')
        self.btn_edit = ttk.Button(self.frame_word, text='Изменить статью', command=self.edit,
                                   takefocus=False, style='Default.TButton')
        self.btn_add = ttk.Button(self.frame_word, text='Добавить статью', command=self.add,
                                  takefocus=False, style='Default.TButton')
        # } }
        self.btn_settings = ttk.Button(self.frame_buttons, text='Настройки', command=self.settings,
                                       takefocus=False, style='Default.TButton')
        self.btn_check_updates = ttk.Button(self.frame_buttons, text='Проверить обновления', command=self.check_updates,
                                            takefocus=False, style='Default.TButton')
        self.btn_save = ttk.Button(self.frame_buttons, text='Сохранить словарь', command=self.save,
                                   takefocus=False, style='Yes.TButton')
        self.btn_close = ttk.Button(self.frame_buttons, text='Закрыть программу', command=self.close,
                                    takefocus=False, style='No.TButton')
        # }
        self.lbl_footer = ttk.Label(self, text=f'{PROGRAM_VERSION}\n'
                                               f'{PROGRAM_DATE}  {PROGRAM_TIME}',
                                    justify='center', style='Footer.TLabel')

        self.frame_head.grid(row=0, padx=16, pady=16)
        # {
        self.lbl_header.grid(row=0, padx=0, pady=0)
        self.lbl_logo.grid(  row=1, padx=0, pady=0)
        # }
        self.frame_dct_name.grid(row=1, padx=6, pady=(0, 12))
        # {
        self.lbl_dct_name.grid(padx=1, pady=1)
        # }
        self.frame_buttons.grid(row=2, padx=6, pady=(0, 6))
        # {
        self.btn_print.grid( row=0, padx=0, pady=(0, 3))
        self.btn_learn.grid( row=1, padx=0, pady=(3, 3))
        self.frame_word.grid(row=2, padx=0, pady=(3, 3))
        # { {
        self.entry_word.grid(row=0, padx=6, pady=(6, 3))
        self.btn_search.grid(row=1, padx=6, pady=(3, 3))
        self.btn_edit.grid(  row=2, padx=6, pady=(3, 3))
        self.btn_add.grid(   row=3, padx=6, pady=(3, 6))
        # } }
        self.btn_settings.grid(     row=3, padx=0, pady=(3, 3))
        self.btn_check_updates.grid(row=4, padx=0, pady=(3, 3))
        self.btn_save.grid(         row=5, padx=0, pady=(3, 3))
        self.btn_close.grid(        row=6, padx=0, pady=(3, 0))
        # }
        self.lbl_footer.grid(row=3, padx=6, pady=3)

        self.tip_entry = ttip.Hovertip(self.entry_word, 'Введите слово, которое хотите\n'
                                                        'найти/изменить/добавить',
                                       hover_delay=500)

        self.set_focus()

    # Нажатие на кнопку "Просмотреть словарь"
    def print(self):
        PrintW(self).open()

    # Нажатие на кнопку "Учить слова"
    def learn(self):
        res = ChooseLearnModeW(self).open()
        if not res:
            return
        LearnW(self, res[0], res[1], res[2]).open()

    # Нажатие на кнопку "Найти статью"
    def search(self):
        wrd = self.var_word.get()
        SearchW(self, wrd).open()

    # Нажатие на кнопку "Изменить статью"
    def edit(self):
        wrd = encode_special_combinations(self.var_word.get())
        if wrd_to_key(wrd, 0) not in _0_global_dct.d.keys():
            ParticularMatchesW(self, wrd).open()  # Если такого слова нет, то выводятся частично совпадающие слова
            return
        key = _0_global_dct.choose_one_of_similar_entries(self, wrd)
        if not key:
            return None
        EditW(self, key).open()

    # Нажатие на кнопку "Добавить статью"
    def add(self):
        wrd = self.var_word.get()
        key = AddW(self, wrd).open()
        if not key:
            return
        EditW(self, key).open()

    # Нажатие на кнопку "Настройки"
    def settings(self):
        global _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_fontsize,\
            _0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations,\
            _0_global_check_register

        SettingsW(self).open()

        _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_fontsize =\
            upload_global_settings()  # Обновляем глобальные настройки
        _0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations, _0_global_check_register =\
            upload_local_settings(_0_global_dct_savename)  # Обновляем локальные настройки

        # Обновляем надпись с названием открытого словаря
        self.lbl_dct_name.config(text=f'Открыт словарь\n'
                                      f'"{split_text(_0_global_dct_savename, 20, align_left=False)}"')

        self.set_ttk_styles()  # Установка ttk-стилей

    # Нажатие на кнопку "Проверить обновления"
    def check_updates(self):
        global _0_global_window_last_version

        # Если уведомление об обновлении уже открыто, то закрываем его
        try:
            _0_global_window_last_version.destroy()
        except:
            pass
        # Открываем новое уведомление об обновлении
        _0_global_window_last_version = check_updates(self, bool(_0_global_show_updates), True)

    # Нажатие на кнопку "Сохранить словарь"
    def save(self):
        global _0_global_has_progress

        save_dct(_0_global_dct, dct_filename(_0_global_dct_savename))
        PopupMsgW(self, 'Прогресс успешно сохранён').open()
        print('\nПрогресс успешно сохранён')

        _0_global_has_progress = False

    # Нажатие на кнопку "Закрыть программу"
    def close(self):
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(_0_global_dct_savename), _0_global_has_progress)
        self.quit()

    # Установить ttk-стили
    def set_ttk_styles(self):
        # Стиль label "default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure('Default.TLabel',
                                      font=('StdFont', _0_global_fontsize),
                                      background=ST_BG[th],
                                      foreground=ST_FG[th])

        # Стиль label "header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('Header.TLabel',
                                     font=('StdFont', _0_global_fontsize + 5),
                                     background=ST_BG[th],
                                     foreground=ST_FG[th])

        # Стиль label "logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('Logo.TLabel',
                                   font=('Times', _0_global_fontsize + 11),
                                   background=ST_BG[th],
                                   foreground=ST_FG_LOGO[th])

        # Стиль label "footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('Footer.TLabel',
                                     font=('StdFont', _0_global_fontsize - 2),
                                     background=ST_BG[th],
                                     foreground=ST_FG_FOOTER[th])

        # Стиль label "warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('Warn.TLabel',
                                   font=('StdFont', _0_global_fontsize),
                                   background=ST_BG[th],
                                   foreground=ST_FG_WARN[th])

        # Стиль label "flat"
        self.st_lbl_flat = ttk.Style()
        self.st_lbl_flat.theme_use('alt')
        self.st_lbl_flat.configure('Flat.TLabel',
                                   font='TkFixedFont',
                                   background=ST_BG_FIELDS[th],
                                   foreground=ST_FG[th])

        # Стиль entry "default"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('Default.TEntry',
                                font=('StdFont', _0_global_fontsize))
        self.st_entry.map('Default.TEntry',
                          fieldbackground=[('readonly', ST_BG[th]),
                                           ('!readonly', ST_BG_FIELDS[th])],
                          foreground=[('readonly', ST_FG[th]),
                                      ('!readonly', ST_FG_ENTRY[th])],
                          selectbackground=[('readonly', ST_SELECT_BG[th]),
                                            ('!readonly', ST_SELECT_BG[th])],
                          selectforeground=[('readonly', ST_SELECT_FG[th]),
                                            ('!readonly', ST_SELECT_FG[th])])

        # Стиль button "default"
        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure('Default.TButton',
                                      font=('StdFont', _0_global_fontsize + 2),
                                      borderwidth=1)
        self.st_btn_default.map('Default.TButton',
                                relief=[('pressed', 'sunken'),
                                        ('active', 'flat'),
                                        ('!active', 'raised')],
                                background=[('pressed', ST_BTN_BG_SEL[th]),
                                            ('active', ST_BTN_BG[th]),
                                            ('!active', ST_BTN_BG[th])],
                                foreground=[('pressed', ST_FG[th]),
                                            ('active', ST_FG[th]),
                                            ('!active', ST_FG[th])])

        # Стиль button "disabled" (для выключенных "default")
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure('Disabled.TButton',
                                       font=('StdFont', _0_global_fontsize + 2),
                                       borderwidth=1)
        self.st_btn_disabled.map('Disabled.TButton',
                                 relief=[('active', 'raised'),
                                         ('!active', 'raised')],
                                 background=[('active', ST_BTN_BG_DISABL[th]),
                                             ('!active', ST_BTN_BG_DISABL[th])],
                                 foreground=[('active', ST_BTN_FG_DISABL[th]),
                                             ('!active', ST_BTN_FG_DISABL[th])])

        # Стиль button "yes"
        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure('Yes.TButton',
                                  font=('StdFont', _0_global_fontsize + 2),
                                  borderwidth=1)
        self.st_btn_yes.map('Yes.TButton',
                            relief=[('pressed', 'sunken'),
                                    ('active', 'flat'),
                                    ('!active', 'raised')],
                            background=[('pressed', ST_BTN_Y_BG_SEL[th]),
                                        ('active', ST_BTN_Y_BG[th]),
                                        ('!active', ST_BTN_Y_BG[th])],
                            foreground=[('pressed', ST_FG[th]),
                                        ('active', ST_FG[th]),
                                        ('!active', ST_FG[th])])

        # Стиль button "no"
        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure('No.TButton',
                                 font=('StdFont', _0_global_fontsize + 2),
                                 borderwidth=1)
        self.st_btn_no.map('No.TButton',
                           relief=[('pressed', 'sunken'),
                                   ('active', 'flat'),
                                   ('!active', 'raised')],
                           background=[('pressed', ST_BTN_N_BG_SEL[th]),
                                       ('active', ST_BTN_N_BG[th]),
                                       ('!active', ST_BTN_N_BG[th])],
                           foreground=[('pressed', ST_FG[th]),
                                       ('active', ST_FG[th]),
                                       ('!active', ST_FG[th])])

        # Стиль button "image"
        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure('Image.TButton',
                                    font=('StdFont', _0_global_fontsize + 2),
                                    borderwidth=0)
        self.st_btn_image.map('Image.TButton',
                              relief=[('pressed', 'flat'),
                                      ('active', 'flat'),
                                      ('!active', 'flat')],
                              background=[('pressed', ST_BTN_IMG_BG_SEL[th]),
                                          ('active', ST_BTN_IMG_BG_HOV[th]),
                                          ('!active', ST_BG[th])],
                              foreground=[('pressed', ST_FG[th]),
                                          ('active', ST_FG[th]),
                                          ('!active', ST_FG[th])])

        # Стиль button "flat"
        self.st_btn_flat = ttk.Style()
        self.st_btn_flat.theme_use('alt')
        self.st_btn_flat.configure('Flat.TButton',
                                   font='TkFixedFont',
                                   borderwidth=0)
        self.st_btn_flat.map('Flat.TButton',
                             relief=[('pressed', 'flat'),
                                     ('active', 'flat'),
                                     ('!active', 'flat')],
                             background=[('pressed', ST_BG[th]),
                                         ('active', ST_BG[th]),
                                         ('!active', ST_BG_FIELDS[th])],
                             foreground=[('pressed', ST_FG[th]),
                                         ('active', ST_FG[th]),
                                         ('!active', ST_FG[th])])

        # Стиль checkbutton "default"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map('Default.TCheckbutton',
                          background=[('active', ST_CHECK_BG_SEL[th]),
                                      ('!active', ST_BG[th])])

        # Стиль combobox "default"
        self.st_combo = ttk.Style()
        self.st_combo.theme_use('alt')
        self.st_combo.configure('Default.TCombobox',
                                font=('StdFont', _0_global_fontsize))
        self.st_combo.map('Default.TCombobox',
                          background=[('readonly', ST_BTN_BG[th]),
                                      ('!readonly', ST_BTN_BG[th])],
                          fieldbackground=[('readonly', ST_BG_FIELDS[th]),
                                           ('!readonly', ST_BG_FIELDS[th])],
                          selectbackground=[('readonly', ST_BG_FIELDS[th]),
                                            ('!readonly', ST_BG_FIELDS[th])],
                          highlightbackground=[('readonly', ST_BORDERCOLOR[th]),
                                               ('!readonly', ST_BORDERCOLOR[th])],
                          foreground=[('readonly', ST_FG[th]),
                                      ('!readonly', ST_FG[th])],
                          selectforeground=[('readonly', ST_FG[th]),
                                            ('!readonly', ST_FG[th])])

        # Стиль всплывающего списка combobox
        self.option_add('*TCombobox*Listbox*Font', ('StdFont', _0_global_fontsize))
        self.option_add('*TCombobox*Listbox*Background', ST_BG_FIELDS[th])
        self.option_add('*TCombobox*Listbox*Foreground', ST_FG[th])
        self.option_add('*TCombobox*Listbox*selectBackground', ST_SELECT_BG[th])
        self.option_add('*TCombobox*Listbox*selectForeground', ST_SELECT_FG[th])

        # Стиль scrollbar "vertical"
        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map('Vertical.TScrollbar',
                            troughcolor=[('disabled', ST_BG[th]),
                                         ('pressed', ST_SCROLL_BG_SEL[th]),
                                         ('!pressed', ST_SCROLL_BG[th])],
                            background=[('disabled', ST_BG[th]),
                                        ('pressed', ST_SCROLL_FG_SEL[th]),
                                        ('!pressed', ST_SCROLL_FG[th])])

        # Стиль scrollbar "horizontal"
        self.st_hscroll = ttk.Style()
        self.st_hscroll.theme_use('alt')
        self.st_hscroll.map('Horizontal.TScrollbar',
                            troughcolor=[('disabled', ST_BG[th]),
                                         ('pressed', ST_SCROLL_BG_SEL[th]),
                                         ('!pressed', ST_SCROLL_BG[th])],
                            background=[('disabled', ST_BG[th]),
                                        ('pressed', ST_SCROLL_FG_SEL[th]),
                                        ('!pressed', ST_SCROLL_FG[th])])

        # Стиль notebook "default"
        self.st_note = ttk.Style()
        self.st_note.theme_use('alt')
        self.st_note.configure('Default.TNotebook',
                               font=('StdFont', _0_global_fontsize))
        self.st_note.map('Default.TNotebook',
                         troughcolor=[('active', ST_BG[th]),
                                      ('!active', ST_BG[th])],
                         background=[('selected', ST_BTN_BG_SEL[th]),
                                     ('!selected', ST_BG[th])])

        # Стиль вкладок notebook
        self.st_note.map('TNotebook.Tab',
                         background=[('selected', ST_TAB_BG_SEL[th]),
                                     ('!selected', ST_TAB_BG[th])],
                         foreground=[('selected', ST_TAB_FG_SEL[th]),
                                     ('!selected', ST_TAB_FG[th])])

        # Стиль frame "default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure('Default.TFrame',
                                        borderwidth=1,
                                        relief=ST_RELIEF_FRAME[th],
                                        background=ST_BG[th],
                                        bordercolor=ST_BORDERCOLOR[th])

        # Стиль frame "invis"
        self.st_frame_invis = ttk.Style()
        self.st_frame_invis.theme_use('alt')
        self.st_frame_invis.configure('Invis.TFrame',
                                      borderwidth=0,
                                      relief=ST_RELIEF_FRAME[th],
                                      background=ST_BG[th])

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_word.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_search.invoke())


# Вывод информации о программе
print(f'=====================================================================================\n'
      f'\n'
      f'                            Anenokil development presents\n'
      f'                            {PROGRAM_NAME}  {PROGRAM_VERSION}\n'
      f'                               {PROGRAM_DATE}  {PROGRAM_TIME}\n'
      f'\n'
      f'=====================================================================================')

_0_global_dct = Dictionary()
_0_global_has_progress = False

upload_themes(THEMES)  # Загружаем дополнительные темы
upload_custom_theme()  # Загружаем пользовательскую тему
_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_fontsize =\
    upload_global_settings()  # Загружаем глобальные настройки
upload_theme_img(th)  # Загружаем изображения для выбранной темы
root = MainW()  # Создаём графический интерфейс
_0_global_dct_savename = upload_dct(root, _0_global_dct, _0_global_dct_savename,
                                    'Завершить работу')  # Загружаем словарь
if not _0_global_dct_savename:
    exit(101)
_0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations, _0_global_check_register =\
    upload_local_settings(_0_global_dct_savename)  # Загружаем локальные настройки
_0_global_window_last_version = check_updates(root, bool(_0_global_show_updates), False)  # Проверяем наличие обновлений
root.mainloop()

"""
    Про формы и категории:

    'чашка' - СЛОВО

    'чашка'   - начальная ФОРМА СЛОВА 'чашка'   (ед. число, им. падеж)
    'чашками' -           ФОРМА СЛОВА 'чашка' (множ. число, тв. падеж)

      'ед. число, им. падеж' - ШАБЛОН ФОРМЫ 'чашка'
    'множ. число, тв. падеж' - ШАБЛОН ФОРМЫ 'чашками'

    'число' и 'падеж' - КАТЕГОРИИ слов

    'ед. число' и 'множ. число' - ЗНАЧЕНИЯ категории 'число'
    'им. падеж' и   'тв. падеж' - ЗНАЧЕНИЯ категории 'падеж'
"""
