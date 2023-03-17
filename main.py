import copy
import platform
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
from aneno_dct import *
from aneno_constants import *
from aneno_upgrades import *

""" Темы """

CUSTOM_TH = '</custom\\>'  # Название пользовательской темы
THEMES = [CUSTOM_TH, 'light', 'dark']  # Названия тем
DEFAULT_TH = THEMES[1]  # Тема по умолчанию

# Стили для каждой темы
ST_BG              = {THEMES[1]: '#F0F0F0', THEMES[2]: '#222222'}  # Цвет фона окна
ST_BG_FIELDS       = {THEMES[1]: '#FFFFFF', THEMES[2]: '#171717'}  # Цвет фона полей ввода

ST_FG              = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет обычного текста
ST_FG_LOGO         = {THEMES[1]: '#FF8800', THEMES[2]: '#AA4600'}  # Цвет текста логотипа
ST_FG_FOOTER       = {THEMES[1]: '#666666', THEMES[2]: '#666666'}  # Цвет текста нижнего колонтитула
ST_FG_WARN         = {THEMES[1]: '#DD2222', THEMES[2]: '#DD2222'}  # Цвет текста предупреждения
ST_FG_ENTRY        = {THEMES[1]: '#222222', THEMES[2]: '#777777'}  # Цвет вводимого текста

ST_SELECT_BG       = {THEMES[1]: '#BBBBBB', THEMES[2]: '#444444'}  # Цвет выделения фона (selectbackground)
ST_SELECT_FG       = {THEMES[1]: '#101010', THEMES[2]: '#A0A0A0'}  # Цвет выделения текста (selectforeground)

ST_RELIEF_FRAME    = {THEMES[1]: 'groove',  THEMES[2]: 'solid'  }  # Стиль рамок фреймов
ST_RELIEF_TEXT     = {THEMES[1]: 'sunken',  THEMES[2]: 'solid'  }  # Стиль рамок текстовых полей
ST_BORDERCOLOR     = {THEMES[1]: '#222222', THEMES[2]: '#111111'}  # Цвет рамок (работает для solid)

ST_BTN_BG          = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1E1E1E'}  # Цвет фона обычных кнопок
ST_BTN_BG_SEL      = {THEMES[1]: '#BABABA', THEMES[2]: '#1A1A1A'}  # Цвет фона обычных кнопок при нажатии
ST_BTN_Y_BG        = {THEMES[1]: '#88DD88', THEMES[2]: '#446F44'}  # Цвет фона да-кнопок
ST_BTN_Y_BG_SEL    = {THEMES[1]: '#77CC77', THEMES[2]: '#558055'}  # Цвет фона да-кнопок при нажатии
ST_BTN_N_BG        = {THEMES[1]: '#FF6666', THEMES[2]: '#803333'}  # Цвет фона нет-кнопок
ST_BTN_N_BG_SEL    = {THEMES[1]: '#EE5555', THEMES[2]: '#904444'}  # Цвет фона нет-кнопок при нажатии

ST_BTN_IMG_BG_HOV  = {THEMES[1]: '#E0E0E0', THEMES[2]: '#1E1E1E'}  # Цвет фона кнопок-картинок при наведении
ST_BTN_IMG_BG_SEL  = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1A1A1A'}  # Цвет фона кнопок-картинок при нажатии

ST_BTN_NOTE_BG     = {THEMES[1]: '#FFFFFF', THEMES[2]: '#171717'}  # Цвет фона кнопок-записей
ST_BTN_NOTE_BG_HOV = {THEMES[1]: '#E5F3FF', THEMES[2]: '#1B1B1B'}  # Цвет фона кнопок-записей при наведении
ST_BTN_NOTE_BG_SEL = {THEMES[1]: '#CCE8FF', THEMES[2]: '#1E1E1E'}  # Цвет фона кнопок-записей при нажатии
ST_BTN_NOTE_FG     = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста кнопок-записей
ST_BTN_NOTE_FG_HOV = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста кнопок-записей при наведении
ST_BTN_NOTE_FG_SEL = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста кнопок-записей при нажатии

ST_BTN_BG_DISABL   = {THEMES[1]: '#D9D9D9', THEMES[2]: '#1E1E1E'}  # Цвет фона выключенных кнопок
ST_BTN_FG_DISABL   = {THEMES[1]: '#B0B0B0', THEMES[2]: '#454545'}  # Цвет текста выключенных кнопок

ST_CHECK_BG_SEL    = {THEMES[1]: '#DDDDDD', THEMES[2]: '#333333'}  # Цвет фона переключателя при наведении на него

ST_TAB_BG          = {THEMES[1]: '#D0D0D0', THEMES[2]: '#1A1A1A'}  # Цвет фона закрытой вкладки
ST_TAB_BG_SEL      = {THEMES[1]: '#EAEAEA', THEMES[2]: '#222222'}  # Цвет фона открытой вкладки
ST_TAB_FG          = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста закрытой вкладки
ST_TAB_FG_SEL      = {THEMES[1]: '#222222', THEMES[2]: '#979797'}  # Цвет текста открытой вкладки

ST_SCROLL_BG       = {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}  # Цвет фона ползунка
ST_SCROLL_BG_SEL   = {THEMES[1]: '#E0E0E0', THEMES[2]: '#1B1B1B'}  # Цвет фона ползунка при нажатии
ST_SCROLL_FG       = {THEMES[1]: '#CACACA', THEMES[2]: '#292929'}  # Цвет ползунка
ST_SCROLL_FG_SEL   = {THEMES[1]: '#ABABAB', THEMES[2]: '#333333'}  # Цвет ползунка при нажатии

# Названия стилизуемых элементов
STYLE_ELEMENTS = ('BG', 'BG_FIELDS',
                  'FG', 'FG_LOGO', 'FG_FOOTER', 'FG_WARN', 'FG_ENTRY',
                  'SELECT_BG', 'SELECT_FG',
                  'RELIEF_FRAME', 'RELIEF_TEXT', 'BORDERCOLOR',
                  'BTN_BG', 'BTN_BG_SEL', 'BTN_Y_BG', 'BTN_Y_BG_SEL', 'BTN_N_BG', 'BTN_N_BG_SEL',
                  'BTN_IMG_BG_HOV', 'BTN_IMG_BG_SEL',
                  'BTN_NOTE_BG', 'BTN_NOTE_BG_HOV', 'BTN_NOTE_BG_SEL',
                  'BTN_NOTE_FG', 'BTN_NOTE_FG_HOV', 'BTN_NOTE_FG_SEL',
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
          STYLE_ELEMENTS[20]: ST_BTN_NOTE_BG,
          STYLE_ELEMENTS[21]: ST_BTN_NOTE_BG_HOV,
          STYLE_ELEMENTS[22]: ST_BTN_NOTE_BG_SEL,
          STYLE_ELEMENTS[23]: ST_BTN_NOTE_FG,
          STYLE_ELEMENTS[24]: ST_BTN_NOTE_FG_HOV,
          STYLE_ELEMENTS[25]: ST_BTN_NOTE_FG_SEL,
          STYLE_ELEMENTS[26]: ST_BTN_BG_DISABL,
          STYLE_ELEMENTS[27]: ST_BTN_FG_DISABL,
          STYLE_ELEMENTS[28]: ST_CHECK_BG_SEL,
          STYLE_ELEMENTS[29]: ST_TAB_BG,
          STYLE_ELEMENTS[30]: ST_TAB_BG_SEL,
          STYLE_ELEMENTS[31]: ST_TAB_FG,
          STYLE_ELEMENTS[32]: ST_TAB_FG_SEL,
          STYLE_ELEMENTS[33]: ST_SCROLL_BG,
          STYLE_ELEMENTS[34]: ST_SCROLL_BG_SEL,
          STYLE_ELEMENTS[35]: ST_SCROLL_FG,
          STYLE_ELEMENTS[36]: ST_SCROLL_FG_SEL}

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
               STYLE_ELEMENTS[20]: 'Цвет фона кнопок-записей',
               STYLE_ELEMENTS[21]: 'Цвет фона кнопок-записей при наведении',
               STYLE_ELEMENTS[22]: 'Цвет фона кнопок-записей при нажатии',
               STYLE_ELEMENTS[23]: 'Цвет текста кнопок-записей',
               STYLE_ELEMENTS[24]: 'Цвет текста кнопок-записей при наведении',
               STYLE_ELEMENTS[25]: 'Цвет текста кнопок-записей при нажатии',
               STYLE_ELEMENTS[26]: 'Цвет фона выключенных кнопок',
               STYLE_ELEMENTS[27]: 'Цвет текста выключенных кнопок',
               STYLE_ELEMENTS[28]: 'Цвет фона переключателя при наведении на него',
               STYLE_ELEMENTS[29]: 'Цвет фона закрытой вкладки',
               STYLE_ELEMENTS[30]: 'Цвет фона открытой вкладки',
               STYLE_ELEMENTS[31]: 'Цвет текста закрытой вкладки',
               STYLE_ELEMENTS[32]: 'Цвет текста открытой вкладки',
               STYLE_ELEMENTS[33]: 'Цвет фона ползунка',
               STYLE_ELEMENTS[34]: 'Цвет фона ползунка при нажатии',
               STYLE_ELEMENTS[35]: 'Цвет ползунка',
               STYLE_ELEMENTS[36]: 'Цвет ползунка при нажатии'}

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
    if savename in os.listdir(SAVES_PATH):
        warning(window_parent, 'Словарь с таким названием уже существует!')
        return False
    return True


# Проверить корректность названия словаря при изменении
def check_dct_savename_edit(window_parent, old_savename: str, new_savename: str):
    if new_savename == '':
        warning(window_parent, 'Название должно содержать хотя бы один символ!')
        return False
    if new_savename in os.listdir(SAVES_PATH) and new_savename != old_savename:
        warning(window_parent, 'Словарь с таким названием уже существует!')
        return False
    return True


# Проверить корректность перевода
def check_tr(window_parent, translations: list[str] | tuple[str, ...], new_tr: str, wrd: str):
    new_tr = encode_special_combinations(new_tr)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations:
        warning(window_parent, f'У слова "{wrd}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность перевода при изменении
def check_tr_edit(window_parent, translations: list[str] | tuple[str, ...], old_tr: str, new_tr: str, wrd: str):
    new_tr = encode_special_combinations(new_tr)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations and new_tr != old_tr:
        warning(window_parent, f'У слова "{wrd}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность сноски
def check_note(window_parent, notes: list[str] | tuple[str, ...], new_note: str, wrd: str):
    new_note = encode_special_combinations(new_note)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes:
        warning(window_parent, f'У слова "{wrd}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность сноски при изменении
def check_note_edit(window_parent, notes: list[str] | tuple[str, ...], old_note: str, new_note: str, wrd: str):
    new_note = encode_special_combinations(new_note)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes and new_note != old_note:
        warning(window_parent, f'У слова "{wrd}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность названия категории
def check_ctg(window_parent, categories: list[str] | tuple[str, ...], new_ctg: str):
    new_ctg = encode_special_combinations(new_ctg)
    if new_ctg == '':
        warning(window_parent, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories:
        warning(window_parent, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


# Проверить корректность названия категории при изменении
def check_ctg_edit(window_parent, categories: list[str] | tuple[str, ...], old_ctg: str, new_ctg: str):
    new_ctg = encode_special_combinations(new_ctg)
    if new_ctg == '':
        warning(window_parent, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories and new_ctg != old_ctg:
        warning(window_parent, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


# Проверить корректность значения категории
def check_ctg_val(window_parent, values: list[str] | tuple[str, ...], new_val: str):
    new_val = encode_special_combinations(new_val)
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


# Проверить корректность значения категории при изменении
def check_ctg_val_edit(window_parent, values: list[str] | tuple[str, ...], old_val: str, new_val: str):
    new_val = encode_special_combinations(new_val)
    if new_val == '':
        warning(window_parent, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_val in values and new_val != old_val:
        warning(window_parent, f'Значение "{new_val}" уже существует!')
        return False
    if CATEGORY_SEPARATOR in new_val:
        warning(window_parent, f'Недопустимый символ: {CATEGORY_SEPARATOR}!')
        return False
    return True


# Проверить корректность названия группы
def check_group_name(window_parent, groups: list[str] | tuple[str, ...], new_group: str):
    new_group = encode_special_combinations(new_group)
    if new_group == '':
        warning(window_parent, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_group in groups:
        warning(window_parent, f'Группа "{new_group}" уже существует!')
        return False
    return True


# Проверить корректность названия группы при изменении
def check_group_name_edit(window_parent, groups: list[str] | tuple[str, ...], old_group: str, new_group: str):
    new_group = encode_special_combinations(new_group)
    if new_group == '':
        warning(window_parent, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_group in groups and new_group != old_group:
        warning(window_parent, f'Группа "{new_group}" уже существует!')
        return False
    return True


""" Функции вывода """


# Вывести переводы
def get_tr(entry: Entry):
    return ', '.join(tuple(entry.tr))


# Вывести сноски
def get_notes(entry: Entry, tab=0):
    return '\n'.join((' ' * tab + '> ' + nt for nt in entry.notes))


# Вывести словоформы
def get_forms(entry: Entry, tab=0):
    frm_keys = entry.forms.keys()
    return '\n'.join((' ' * tab + f'[{frm_key_to_str_for_print(key)}] {entry.forms[key]}' for key in frm_keys))


# Вывести группы
def get_groups(entry: Entry):
    if entry.groups:
        return ', '.join(tuple(entry.groups))
    else:
        return '-'


# Вывести количество ошибок после последнего верного ответа
def get_correct_att_in_a_row(entry: Entry):
    if entry.all_att == 0:  # Если ещё не было попыток
        res = '-'
    elif entry.correct_att_in_a_row > 999:
        res = '+∞'
    elif entry.correct_att_in_a_row < -99:
        res = '-∞'
    else:
        res = entry.correct_att_in_a_row
    return res


# Вывести процент верных ответов
def get_entry_percent(entry: Entry):
    if entry.all_att == 0:  # Если ещё не было попыток
        res = '-'
    else:
        res = '{:.0%}'.format(entry.score)
    return res


# Вывести статистику
def get_entry_stat(entry: Entry):
    correct_att_in_a_row = get_correct_att_in_a_row(entry)
    percent = get_entry_percent(entry)
    tab_correct = ' ' * (3 - len(str(correct_att_in_a_row)))
    tab_percent = ' ' * (4 - len(percent))
    res = f'[{tab_correct}{correct_att_in_a_row}:{tab_percent}{percent}]'
    return res


# Служебная функция для get_entry_info_briefly и get_entry_info_briefly_with_forms
def _get_entry_info_briefly(entry: Entry):
    if entry.fav:
        res = '(*)'
    else:
        res = '   '
    res += f' {get_entry_stat(entry)} {entry.wrd}: {get_tr(entry)}'
    return res


# Вывести статью - кратко
def get_entry_info_briefly(entry: Entry, len_str: int):
    res = _get_entry_info_briefly(entry)
    if entry.count_n != 0:
        res += f'\n{get_notes(entry, tab=15)}'
    return split_text(res, len_str, tab=15)


# Вывести статью - кратко со словоформами
def get_entry_info_briefly_with_forms(entry: Entry, len_str: int):
    res = _get_entry_info_briefly(entry)
    if entry.count_f != 0:
        res += f'\n{get_forms(entry, tab=15)}'
    if entry.count_n != 0:
        res += f'\n{get_notes(entry, tab=15)}'
    return split_text(res, len_str, tab=15)


# Вывести слово со статистикой
def get_wrd_with_stat(entry: Entry):
    res = f'{entry.wrd} {get_entry_stat(entry)}'
    return res


# Вывести перевод со статистикой
def get_tr_with_stat(entry: Entry):
    res = f'{get_tr(entry)} {get_entry_stat(entry)}'
    return res


# Вывести перевод со словоформой и со статистикой
def get_tr_and_frm_with_stat(entry: Entry, frm_key: tuple[str, ...] | list[str]):
    res = f'{get_tr(entry)} ({frm_key_to_str_for_print(frm_key)}) {get_entry_stat(entry)}'
    return res


# Вывести статью со всей информацией
def get_all_entry_info(entry: Entry, len_str: int, tab=0):
    res = ''
    res += f'      Слово: {entry.wrd}\n'
    res += f'    Перевод: {get_tr(entry)}\n'
    res += f'Формы слова: '
    if entry.count_f == 0:
        res += '-\n'
    else:
        keys = [key for key in entry.forms.keys()]
        res += f'[{frm_key_to_str_for_print(keys[0])}] {entry.forms[keys[0]]}\n'
        for i in range(1, entry.count_f):
            res += f'             [{frm_key_to_str_for_print(keys[i])}] {entry.forms[keys[i]]}\n'
    res += '     Сноски: '
    if entry.count_n == 0:
        res += '-\n'
    else:
        res += f'> {entry.notes[0]}\n'
        for i in range(1, entry.count_n):
            res += f'             > {entry.notes[i]}\n'
    if entry.fav:
        res += '  Избранное: ДА\n'
    else:
        res += '  Избранное: НЕТ\n'
    res += f'     Группы: {get_groups(entry)}\n'
    if entry.all_att == 0:  # Если ещё не было попыток
        res += ' Статистика: 1) Верных ответов подряд: -\n'
        res += '             2) Доля верных ответов: -'
    else:
        res += f' Статистика: 1) Верных ответов подряд: {entry.correct_att_in_a_row}\n'
        res += f'             2) Доля верных ответов: '
        res += f'{entry.correct_att}/{entry.all_att} = ' + '{:.0%}'.format(entry.score)
    return split_text(res, len_str, tab=tab)


# Вывести информацию о количестве статей в словаре
def dct_info(dct: Dictionary):
    w = set_postfix(dct.count_w, ('слово', 'слова', 'слов'))
    f = set_postfix(dct.count_w + dct.count_f, ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(dct.count_t, ('перевод', 'перевода', 'переводов'))
    return f'[ {dct.count_w} {w} | {dct.count_w + dct.count_f} {f} | {dct.count_t} {t} ]'


# Вывести информацию о количестве избранных статей в словаре
def dct_info_fav(dct: Dictionary, count_w: int, count_t: int, count_f: int):
    w = set_postfix(count_w, ('слово', 'слова', 'слов'))
    f = set_postfix(count_w + count_f, ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(count_t, ('перевод', 'перевода', 'переводов'))
    return f'[ {count_w}/{dct.count_w} {w} | ' \
           f'{count_w + count_f}/{dct.count_w + dct.count_f} {f} | ' \
           f'{count_t}/{dct.count_t} {t} ]'


""" Вспомогательные функции """


# Преобразовать специальную комбинацию в читаемый вид (для отображения в настройках)
def special_combination(key: tuple[str, str]):
    value = _0_global_special_combinations[key]
    return f'{key[0]}{key[1]} -> {value}'


# Преобразовать в тексте специальные комбинации в соответствующие символы
def encode_special_combinations(text: str):
    encoded_text = ''

    opening_symbol = None  # Встречен ли открывающий символ специальной комбинации
    for symbol in text:
        if opening_symbol:
            if (opening_symbol, symbol) in _0_global_special_combinations.keys():  # Если есть такая комбинация
                encoded_text += _0_global_special_combinations[(opening_symbol, symbol)]
            elif symbol == opening_symbol:  # Если встречено два открывающих символа подряд
                encoded_text += opening_symbol  # (## -> #)
            else:  # Если нет такой комбинации
                encoded_text += f'{opening_symbol}{symbol}'
            opening_symbol = None
        elif symbol in SPECIAL_COMBINATIONS_OPENING_SYMBOLS:  # Если встречен открывающий символ специальной комбинации
            opening_symbol = symbol
        else:  # Если встречен обычный символ
            encoded_text += symbol
    if opening_symbol:  # Если текст завершается открывающим символом специальной комбинации
        encoded_text += opening_symbol

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


# Найти в строке подстроку и выделить её (только частичные совпадения)
def find_and_highlight(target_wrd: str, search_wrd: str):
    if target_wrd == search_wrd:  # Полное совпадение не учитывается
        return ''

    target_wrd = encode_special_combinations(target_wrd)
    search_wrd = encode_special_combinations(search_wrd)

    target_simpl, target_arr = simplify(target_wrd)
    search_simpl, search_arr = simplify(search_wrd)

    pos = target_simpl.find(search_simpl)
    if pos != -1:
        search_len = len(encode_special_combinations(search_simpl))
        end_pos = pos + search_len
        if search_wrd == '':  # Если искомая подстрока пустая, то она не выделяется
            res = target_wrd
        else:
            res = ''.join((s for s in target_arr[:pos] + ['['] +
                           target_arr[pos:end_pos] + [']'] + target_arr[end_pos:]))
        return res
    return ''


# Выбрать случайное слово с учётом сложности
def random_smart(dct: Dictionary, pool: set[tuple[tuple[str, int], None] | tuple[tuple[str, int], tuple[str, ...]]],
                 min_good_score_perc: int) -> tuple[tuple[str, int], None] | tuple[tuple[str, int], tuple[str, ...]]:
    summ = 0
    for (key, frm) in pool:
        entry = dct.d[key]
        score = (100 - round(100 * entry.score)) + 1
        if 100 * entry.score < min_good_score_perc:
            score *= 1.5
        score += 100 // (entry.all_att + 1)
        summ += round(score)

    r = random.randint(1, summ)
    for (key, frm) in pool:
        entry = dct.d[key]
        score = (100 - round(100 * entry.score)) + 1
        if 100 * entry.score < min_good_score_perc:
            score *= 1.5
        score += 100 // (entry.all_att + 1)
        r -= round(score)
        if r <= 0:
            return key, frm


# Разделить строку на слова
def split_line(line: str) -> list[str, str]:
    len_line = len(line)
    res = []

    i = 0
    while i < len_line and not line[i].isalnum():
        i += 1
    if i != 0:
        res += [['', line[0:i]]]

    while i < len_line:
        word = ''
        separator = ''
        while i < len_line and line[i].isalnum():
            word += line[i]
            i += 1
        while i < len_line and not line[i].isalnum():
            separator += line[i]
            i += 1
        res += [[word, separator]]

    return res


# Разделить текст на части, длина которых не превышает заданное значение
def split_text(text: str, max_str_len: int, tab: int = 0, add_right_spaces: bool = True):
    assert max_str_len > 0
    assert tab >= 0
    assert tab < max_str_len

    res = ''
    lines = text.split('\n')  # Строки
    count_lines = len(lines)  # Количество строк
    for i in range(count_lines):
        line = lines[i]
        len_line = len(line)
        # Если ширина строки соответствует требованиям, то просто записываем эту строку
        if len_line <= max_str_len:
            res += line
            # Если нужно, дополняем строку пробелами до максимальной длины
            if add_right_spaces:
                res += ' ' * (max_str_len - len_line)
        else:
            current_len = 0
            tabulate = False
            words = split_line(line)
            for (word, separator) in words:
                len_word = len(word)
                len_separator = len(separator)

                # Если слово превышает максимальную длину строки, то разбиваем его на части
                if len_word > max_str_len or (tabulate and tab + len_word > max_str_len):
                    tmp = max_str_len - current_len
                    res += word[0:tmp]
                    res += ''.join(['\n' + ' ' * tab + word[i:i+max_str_len-tab]
                                    for i in range(tmp, len_word, max_str_len-tab)])
                    current_len = tab + (len_word - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если слово не вмещается в данную строку, но может вместиться в следующую,
                # то записываем его в следующую
                elif len_word + current_len > max_str_len:
                    # Если нужно, дополняем строку пробелами до максимальной длины
                    if add_right_spaces:
                        res += ' ' * (max_str_len - current_len)
                    res += '\n'
                    res += ' ' * tab
                    res += word
                    current_len = tab + len_word
                    tabulate = True
                # Если слово вмещается в данную строку, то просто записываем его
                else:
                    res += word
                    current_len += len_word

                # Если разделитель целиком не вмещается в данную строку, то разделяем его на части
                if current_len + len_separator > max_str_len:
                    tmp = max_str_len - current_len
                    res += separator[0:tmp]
                    res += ''.join(['\n' + ' ' * tab + separator[i:i+max_str_len-tab]
                                    for i in range(tmp, len_separator, max_str_len-tab)])
                    current_len = tab + (len_separator - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если разделитель вмещается в данную строку целиком, то просто записываем его
                else:
                    res += separator
                    current_len += len_separator
            # Если нужно, дополняем строку пробелами до максимальной длины
            if add_right_spaces:
                res += ' ' * (max_str_len - current_len)
        # Если строка не последняя, то добавляем перенос строки
        if i != count_lines - 1:
            res += '\n'
    return res


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


""" Основные функции """


# Выбрать одну статью из нескольких с одинаковыми словами
def choose_one_of_similar_entries(dct: Dictionary, window_parent, wrd: str):
    if wrd_to_key(wrd, 1) not in dct.d.keys():  # Если статья только одна, то возвращает её ключ
        return wrd_to_key(wrd, 0)
    window_entries = ChooseOneOfSimilarEntriesW(window_parent, wrd)
    answer = window_entries.open()
    if not answer:
        return None
    return answer


# Изменить слово в статье
def edit_wrd_with_choose(dct: Dictionary, window_parent, key: tuple[str, int], new_wrd: str):
    if wrd_to_key(new_wrd, 0) in dct.d.keys():  # Если в словаре уже есть статья с таким словом
        window = PopupDialogueW(window_parent, 'Статья с таким словом уже есть в словаре\n'
                                               'Что вы хотите сделать?',
                                'Добавить к существующей статье', 'Оставить отдельной статьёй',
                                set_enter_on_btn='none', st_left='Default', st_right='Default',
                                val_left='l', val_right='r', val_on_close='c')
        answer = window.open()
        if answer == 'l':  # Добавить к существующей статье
            new_key = choose_one_of_similar_entries(dct, window_parent, new_wrd)
            if not new_key:
                return key
            dct.merge_entries(new_key, key)
            return new_key
        elif answer == 'r':  # Оставить отдельной статьёй
            new_key = dct.add_entry(new_wrd, dct.d[key].tr, dct.d[key].notes, dct.d[key].forms, dct.d[key].fav,
                                    dct.d[key].groups, dct.d[key].all_att, dct.d[key].correct_att,
                                    dct.d[key].correct_att_in_a_row, dct.d[key].latest_answer_session)
            dct.delete_entry(key)
            return new_key
        else:
            return key
    else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
        new_key = dct.add_entry(new_wrd, dct.d[key].tr, dct.d[key].notes, dct.d[key].forms, dct.d[key].fav,
                                dct.d[key].groups, dct.d[key].all_att, dct.d[key].correct_att,
                                dct.d[key].correct_att_in_a_row, dct.d[key].latest_answer_session)
        dct.delete_entry(key)
        return new_key


# Добавить статью в словарь (для пользователя)
def add_entry_with_choose(dct: Dictionary, window_parent, wrd: str, tr: str):
    if wrd_to_key(wrd, 0) in dct.d.keys():  # Если в словаре уже есть статья с таким словом
        window = PopupDialogueW(window_parent, 'Статья с таким словом уже есть в словаре\n'
                                               'Что вы хотите сделать?',
                                'Добавить к существующей статье', 'Создать новую статью',
                                set_enter_on_btn='none', st_left='Default', st_right='Default',
                                val_left='l', val_right='r', val_on_close='c')
        answer = window.open()
        if answer == 'l':  # Добавить к существующей статье
            key = choose_one_of_similar_entries(dct, window_parent, wrd)
            if not key:
                return None
            dct.add_tr(key, tr)
            return key
        elif answer == 'r':  # Создать новую статью
            return dct.add_entry(wrd, tr)
        else:
            return None
    else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
        return dct.add_entry(wrd, tr)


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
def rename_ctg(window_parent, categories: dict[str, list[str]], old_ctg_name: str):
    # Ввод нового названия категории
    window_entry = PopupEntryW(window_parent, 'Введите новое название категории', default_value=old_ctg_name,
                               check_answer_function=lambda wnd, val:
                               check_ctg_edit(wnd, tuple(categories.keys()), old_ctg_name, val))
    closed, new_ctg_name = window_entry.open()
    if closed:
        return False
    new_ctg_name = encode_special_combinations(new_ctg_name)
    if new_ctg_name == old_ctg_name:
        return

    # обновление категорий
    categories[new_ctg_name] = categories[old_ctg_name]
    categories.pop(old_ctg_name)
    return True


# Удалить категорию
def delete_ctg(window_parent, categories: dict[str, list[str]], ctg_name: str, dct: Dictionary, to_ask: bool):
    if to_ask:
        window_dia = PopupDialogueW(window_parent, f'Все словоформы, содержащие категорию {ctg_name}, будут удалены!\n'
                                                   f'Хотите продолжить?')  # Подтверждение действия
        answer = window_dia.open()
    else:
        answer = True
    if answer:
        ctg_names = [ctg_name for ctg_name in categories.keys()]
        pos = ctg_names.index(ctg_name)
        categories.pop(ctg_name)
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
def rename_ctg_val(window_parent, values: list[str] | tuple[str, ...], old_ctg_val: str, pos: int, dct: Dictionary):
    # Ввод нового значения
    window_entry = PopupEntryW(window_parent, 'Введите новое название значения', default_value=old_ctg_val,
                               check_answer_function=lambda wnd, val: check_ctg_val_edit(wnd, values, old_ctg_val, val))
    closed, new_ctg_val = window_entry.open()
    if closed:
        return False
    new_ctg_val = encode_special_combinations(new_ctg_val)
    if new_ctg_val == old_ctg_val:
        return

    # Переименовывание значения во всех словоформах, его содержащих
    dct.rename_forms_with_val(pos, old_ctg_val, new_ctg_val)
    index = values.index(old_ctg_val)
    values[index] = new_ctg_val
    return True


# Удалить значение категории
def delete_ctg_val(window_parent, values: list[str] | tuple[str, ...], ctg_val: str, dct: Dictionary):
    window_dia = PopupDialogueW(window_parent, f'Все словоформы, содержащие значение {ctg_val}, будут удалены!\n'
                                               f'Хотите продолжить?')  # Подтверждение действия
    answer = window_dia.open()
    if answer:
        index = values.index(ctg_val)
        values.pop(index)
        dct.delete_forms_with_val(index, ctg_val)  # Удаление всех словоформ, содержащих это значение категории
        return True
    return False


# Поиск статей в словаре
def search_entries(dct: Dictionary, keys: tuple[tuple[str, int], ...], query: str,
                   search_wrd: bool, search_tr: bool, search_frm: bool, search_nt: bool):
    full_matches = set()
    particulary_matches = set()
    if search_wrd:
        for key in keys:
            entry = dct.d[key]
            if query == entry.wrd:
                full_matches.add(key)
            elif find_and_highlight(entry.wrd, query) != '':
                if key not in full_matches:
                    particulary_matches.add(key)
    if search_tr:
        for key in keys:
            entry = dct.d[key]
            if query in entry.tr:
                full_matches.add(key)
            else:
                for tr in entry.tr:
                    if find_and_highlight(tr, query) != '':
                        if key not in full_matches:
                            particulary_matches.add(key)
            #print(frm_key_to_str_for_print(tuple(find_and_highlight(tr, query) for tr in entry.tr)))
    if search_frm:
        for key in keys:
            entry = dct.d[key]
            if query in entry.forms.values():
                full_matches.add(key)
            else:
                for frm in entry.forms.values():
                    if find_and_highlight(frm, query) != '':
                        if key not in full_matches:
                            particulary_matches.add(key)
    if search_nt:
        for key in keys:
            entry = dct.d[key]
            if query in entry.notes:
                full_matches.add(key)
            else:
                for nt in entry.notes:
                    if find_and_highlight(nt, query) != '':
                        if key not in full_matches:
                            particulary_matches.add(key)
    return full_matches, particulary_matches


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
                PopupMsgW(window_parent, 'Установлена последняя доступная версия программы').open()
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


""" Загрузка/сохранение """


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
    global img_about_mgsp, img_about_typo, img_about, img_ok, img_cancel, img_add, img_delete, img_edit, img_print_out,\
        img_undo, img_redo, img_arrow_left, img_arrow_right, img_double_arrow_left, img_double_arrow_right

    if theme == CUSTOM_TH:
        theme_dir = CUSTOM_THEME_PATH
    else:
        theme_dir = os.path.join(ADDITIONAL_THEMES_PATH, theme)

    images = [img_ok, img_cancel, img_add, img_delete, img_edit, img_undo, img_redo, img_arrow_left, img_arrow_right,
              img_double_arrow_left, img_double_arrow_right, img_print_out, img_about, img_about_mgsp, img_about_typo]

    for i in range(len(images)):
        file_name = f'{IMG_NAMES[i]}.png'
        if file_name in os.listdir(theme_dir):
            images[i] = os.path.join(theme_dir, file_name)
        else:
            images[i] = os.path.join(IMAGES_PATH, file_name)

    img_about_mgsp, img_about_typo, img_about, img_ok, img_cancel, img_add, img_delete, img_edit, img_print_out,\
        img_undo, img_redo, img_arrow_left, img_arrow_right, img_double_arrow_left, img_double_arrow_right = images


# Загрузить глобальные настройки (настройки программы)
def upload_global_settings():
    try:  # Открываем файл с настройками программы
        open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
            global_settings_file.write(f'v{GLOBAL_SETTINGS_VERSION}\n'
                                       f'\n'
                                       f'dct\n'
                                       f'1\n'
                                       f'0\n'
                                       f'{DEFAULT_TH}\n'
                                       f'{SCALE_DEF}')
    else:
        upgrade_global_settings()

    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        # Версия глобальных настроек
        global_settings_file.readline()
        # Требуется ли обновление ресурсов
        is_res_upgrade_required = global_settings_file.readline().strip() == 'UPGRADE_REQUIRED'
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
            fontsize = SCALE_DEF

    if is_res_upgrade_required:  # Если требуется обновление ресурсов
        # Обновляем
        upgrade_resources()
        # Указываем в глобальных настройках, что обновление больше не требуется
        save_global_settings(dct_savename, show_updates, typo, theme, fontsize)

    return dct_savename, show_updates, typo, theme, fontsize


# Сохранить глобальные настройки (настройки программы)
def save_global_settings(dct_savename: str, show_updates: int, typo: int, theme: str, fontsize: int):
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write(f'v{GLOBAL_SETTINGS_VERSION}\n'
                                   f'\n'
                                   f'{dct_savename}\n'
                                   f'{show_updates}\n'
                                   f'{typo}\n'
                                   f'{theme}\n'
                                   f'{fontsize}')


# Сохранить название открытого словаря
def save_dct_name():
    _, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize = upload_global_settings()
    save_global_settings(_0_global_dct_savename, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize)


# Загрузить локальные настройки (настройки словаря)
def upload_local_settings(savename: str, upgrade=True):
    local_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_SETTINGS_FN)
    try:
        open(local_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
            local_settings_file.write(f'v{LOCAL_SETTINGS_VERSION}\n'  # Версия локальных настроек
                                      f'67\n'  # МППУ
                                      f'#aä#AÄ#oö#OÖ#uü#UÜ#sß#Sẞ\n'  # Специальные комбинации
                                      f'1\n'  # Учитывать ли регистр букв при учёбе
                                      f'5\n'  # Грамматические категории
                                      f'Число\n'
                                      f'2\nед.ч.\nмн.ч.\n'
                                      f'Род\n'
                                      f'3\nм.р.\nж.р.\nср.р.\n'
                                      f'Падеж\n'
                                      f'4\nим.п.\nрод.п.\nдат.п.\nвин.п.\n'
                                      f'Лицо\n'
                                      f'3\n1 л.\n2 л.\n3 л.\n'
                                      f'Время\n'
                                      f'3\nпр.вр.\nн.вр.\nбуд.вр.\n'
                                      f'0')  # Группы
    else:
        if upgrade:
            global _0_global_special_combinations
            _, _0_global_special_combinations, _, _, _ = upload_local_settings(_0_global_dct_savename, upgrade=False)
            upgrade_local_settings(local_settings_path, encode_special_combinations)

    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        # Версия
        local_settings_file.readline()
        # МППУ
        try:
            min_good_score_perc = int(local_settings_file.readline().strip())
        except (ValueError, TypeError):
            min_good_score_perc = 67
        # Специальные комбинации
        special_combinations = {}
        try:
            line_special_combinations = local_settings_file.readline()
            for i in range(0, len(line_special_combinations) - 1, 3):
                opening_symbol = line_special_combinations[i]
                key_symbol = line_special_combinations[i + 1]
                value = line_special_combinations[i + 2]
                special_combinations[(opening_symbol, key_symbol)] = value
        except:
            special_combinations = {}
        # Учитывать ли регистр букв при учёбе
        try:
            check_register = int(local_settings_file.readline().strip())
        except (ValueError, TypeError):
            check_register = 1
        # Грамматические категории
        categories = {}
        try:
            ctg_count = int(local_settings_file.readline().strip())
            for i in range(ctg_count):
                ctg_name = local_settings_file.readline().strip('\n')
                val_count = int(local_settings_file.readline().strip())
                values = []
                for j in range(val_count):
                    values += [local_settings_file.readline().strip('\n')]
                categories[ctg_name] = values
        except:
            categories = {}
        # Группы
        groups = set()
        try:
            gr_count = int(local_settings_file.readline().strip())
            for i in range(gr_count):
                group = local_settings_file.readline().strip('\n')
                groups.add(group)
        except:
            groups = set()
    return min_good_score_perc, special_combinations, check_register, categories, groups


# Сохранить локальные настройки (настройки словаря)
def save_local_settings(min_good_score_perc: int, special_combinations: dict[tuple[str, str], str], check_register: int,
                        categories: dict[str, list[str]], groups: set[str], savename: str):
    local_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_SETTINGS_FN)
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write(f'v{LOCAL_SETTINGS_VERSION}\n')  # Версия
        local_settings_file.write(f'{min_good_score_perc}\n')  # МППУ
        # Специальные комбинации
        for key in special_combinations:
            val = special_combinations[key]
            local_settings_file.write(f'{key[0]}{key[1]}{val}')
        local_settings_file.write('\n')
        # Проверять ли регистр букв при учёбе
        local_settings_file.write(f'{check_register}\n')
        # Грамматические категории
        local_settings_file.write(f'{len(categories)}\n')
        for key in categories.keys():
            vals_count = len(categories[key])
            local_settings_file.write(f'{key}\n')
            local_settings_file.write(f'{vals_count}\n')
            for val in categories[key]:
                local_settings_file.write(f'{val}\n')
        # Группы
        local_settings_file.write(f'{len(groups)}\n')
        for group in groups:
            local_settings_file.write(f'{group}\n')


# Загрузить автосохраняемые локальные настройки (настройки словаря)
def upload_local_auto_settings(savename: str):
    local_auto_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_AUTO_SETTINGS_FN)
    try:
        open(local_auto_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_auto_settings_path, 'w', encoding='utf-8') as local_auto_settings_file:
            local_auto_settings_file.write(f'v{LOCAL_AUTO_SETTINGS_VERSION}\n'  # Версия локальных авто-настроек
                                           f'0\n'  # Номер сессии
                                           f'0 1 1 0 0\n'  # Режим поиска
                                           f'0 1 1 1')  # Режим учёбы
    else:
        upgrade_local_auto_settings(local_auto_settings_path)

    with open(local_auto_settings_path, 'r', encoding='utf-8') as local_auto_settings_file:
        # Версия
        local_auto_settings_file.readline()
        # Номер сессии
        try:
            session_number = int(local_auto_settings_file.readline().strip())
        except (ValueError, TypeError):
            session_number = 0
        # Режим поиска
        try:
            search_settings = tuple(int(el) for el in local_auto_settings_file.readline().strip().split())
        except (ValueError, TypeError):
            search_settings = (0, 0, 1, 1, 0, 0)
        else:
            if len(search_settings) != 6:
                search_settings = (0, 0, 1, 1, 0, 0)
        # Режим учёбы
        try:
            learn_settings = tuple(int(el) for el in local_auto_settings_file.readline().strip().split())
        except (ValueError, TypeError):
            learn_settings = (0, 1, 1, 1)
        else:
            if len(learn_settings) != 4:
                learn_settings = (0, 1, 1, 1)

    # Увеличиваем счётчик сессий на 1 и сохраняем изменение
    session_number += 1
    save_local_auto_settings(session_number, search_settings, learn_settings, savename)

    # Возвращаем результат
    return session_number, search_settings, learn_settings


# Сохранить автосохраняемые локальные настройки (настройки словаря)
def save_local_auto_settings(session_number: int, search_settings: tuple[int, int, int, int, int, int],
                             learn_settings: tuple[int, int, int, int], savename: str):
    local_auto_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_AUTO_SETTINGS_FN)
    with open(local_auto_settings_path, 'w', encoding='utf-8') as local_auto_settings_file:
        local_auto_settings_file.write(f'v{LOCAL_AUTO_SETTINGS_VERSION}\n')
        local_auto_settings_file.write(f'{session_number}\n')
        for el in search_settings:
            local_auto_settings_file.write(f'{el} ')
        local_auto_settings_file.write('\n')
        for el in learn_settings:
            local_auto_settings_file.write(f'{el} ')


# Предложить сохранение настроек, если есть изменения
def save_settings_if_has_changes(window_parent):
    window_dia = PopupDialogueW(window_parent, 'Хотите сохранить изменения настроек?', 'Да', 'Нет')
    answer = window_dia.open()
    if answer:
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th,
                             _0_global_scale)
        save_local_settings(_0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register,
                            _0_global_categories, _0_global_dct.groups, _0_global_dct_savename)
        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)
        PopupMsgW(window_parent, 'Настройки успешно сохранены').open()
        print('\nНастройки успешно сохранены')


# Загрузить словарь (с обновлением и обработкой исключений)
def upload_dct(window_parent, dct: Dictionary, savename: str, btn_close_text: str):
    filepath = os.path.join(SAVES_PATH, savename, DICTIONARY_SAVE_FN)
    try:
        global _0_global_special_combinations
        _, _0_global_special_combinations, _, _, _ = upload_local_settings(_0_global_dct_savename, upgrade=False)
        upgrade_dct_save(filepath, encode_special_combinations)  # Если требуется, сохранение обновляется
        dct.read(filepath, CATEGORY_SEPARATOR)  # Загрузка словаря
    except FileNotFoundError:  # Если сохранение не найдено, то создаётся пустой словарь
        print(f'\nСловарь "{savename}" не найден!')
        create_dct(dct, savename)
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
                                           validate_function=validate_savename,
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
    folder_path = os.path.join(SAVES_PATH, savename)
    filepath = os.path.join(folder_path, DICTIONARY_SAVE_FN)
    os.mkdir(folder_path)
    open(filepath, 'w', encoding='utf-8').write(f'v{SAVES_VERSION}\n')
    dct.read(filepath, CATEGORY_SEPARATOR)


# Сохранить словарь
def save_dct(dct: Dictionary, savename: str):
    filepath = os.path.join(SAVES_PATH, savename, DICTIONARY_SAVE_FN)
    dct.save(filepath, CATEGORY_SEPARATOR, SAVES_VERSION)


# Предложить сохранение словаря, если есть изменения
def save_dct_if_has_progress(window_parent, dct: Dictionary, savename: str, has_progress: bool):
    if has_progress:
        window_dia = PopupDialogueW(window_parent, 'Хотите сохранить свой прогресс?', 'Да', 'Нет')
        answer = window_dia.open()
        if answer:
            save_dct(dct, savename)
            PopupMsgW(window_parent, 'Прогресс успешно сохранён').open()
            print('\nПрогресс успешно сохранён')


# Экспортировать словарь
def dct_export(savename: str, dst_path: str):
    src_path = os.path.join(SAVES_PATH, savename)
    shutil.copytree(src_path, os.path.join(dst_path, savename))


# Импортировать словарь
def dct_import(savename: str, src_path: str):
    dst_path = os.path.join(SAVES_PATH, savename)
    shutil.copytree(src_path, dst_path)


""" Графический интерфейс - вспомогательные функции """


# Вычислить ширину моноширинного поля, в которое должно помещаться каждое из данных значений
def combobox_width(values: tuple[str, ...] | list[str], min_width: int, max_width: int):
    assert min_width >= 0
    assert max_width >= 0
    assert max_width >= min_width

    max_len_of_vals = max(len(val) for val in values)
    return min(max(max_len_of_vals, min_width), max_width)


# Вычислить количество строк, необходимых для записи данного текста
# в многострочное текстовое поле при данной длине строки
def field_height(text: str, len_str: int):
    assert len_str > 0

    segments = text.split('\n')
    return sum(math.ceil(len(segment) / len_str) for segment in segments)


# Вывести сообщение с предупреждением
def warning(window_parent, msg: str):
    PopupMsgW(window_parent, msg, title='Warning').open()


# Выключить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


# Включить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_enable(btn: ttk.Button, command, style='Default'):
    btn.configure(command=command, style=f'{style}.TButton')


# Установить изображение на кнопку
# Если изображение отсутствует, его замещает текст
def set_image(btn: ttk.Button, img: tk.PhotoImage, img_name: str, text_if_no_img: str):
    try:
        img.configure(file=img_name)
    except:
        btn.configure(text=text_if_no_img, compound='text', style='Default.TButton')
    else:
        btn.configure(image=img, compound='image', style='Image.TButton')


""" Графический интерфейс - функции валидации """


# Ввод только целых чисел от 0 до max_val
def validate_int_min_max(value: str, min_val: int, max_val: int):
    return value == '' or value.isnumeric() and min_val <= int(value) <= max_val


# Ввод только целых чисел от 0 до 100
def validate_percent(value: str):
    return validate_int_min_max(value, 0, 100)


# Валидация открывающего символа специальной комбинации
def validate_special_combination_opening_symbol(value: str):
    return value == '' or value in SPECIAL_COMBINATIONS_OPENING_SYMBOLS


# Валидация ключевого символа специальной комбинации
def validate_special_combination_key_symbol(value: str):
    return len(value) <= 1 and value not in SPECIAL_COMBINATIONS_OPENING_SYMBOLS


# Валидация значения специальной комбинации
def validate_special_combination_val(value: str):
    return len(value) <= 1


# Валидация названия словаря
def validate_savename(value: str):
    if len(value) > 99:
        return False
    for symbol in value:
        if symbol in '/|\\<>:*"?':
            return False
    return True


""" Графический интерфейс - виджеты """


# Прокручиваемый фрейм
class ScrollFrame(tk.Frame):
    def __init__(self, parent, height: int, width: int, scrollbar_position: typing.Literal['left', 'right'] = 'right'):
        super().__init__(parent)

        if scrollbar_position == 'right':
            canvas_position: typing.Literal['left', 'right'] = 'left'
        else:
            canvas_position: typing.Literal['left', 'right'] = 'right'

        self.canvas = tk.Canvas(self, bg=ST_BTN_NOTE_BG[th], bd=0, highlightthickness=0, height=height, width=width)
        # {
        self.frame_canvas = ttk.Frame(self.canvas, style='Default.TFrame')
        # }
        self.scrollbar_y = ttk.Scrollbar(self, command=self.canvas.yview, style='Vertical.TScrollbar')

        self.canvas.pack(     side=canvas_position,    fill='both', expand=True)
        self.scrollbar_y.pack(side=scrollbar_position, fill='y')

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

    # Изменить размеры фрейма
    def resize(self, height: int = None, width: int = None):
        if height:
            self.canvas.configure(height=height)
        if width:
            self.canvas.configure(width=width)


""" Графический интерфейс - всплывающие окна """


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg: str, btn_text='Ясно', msg_max_width=60,
                 msg_justify: typing.Literal['left', 'center', 'right'] = 'center', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        self.lbl_msg = ttk.Label(self, text=split_text(msg, msg_max_width, add_right_spaces=False), justify=msg_justify,
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

        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, add_right_spaces=False), justify='center',
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
    def __init__(self, parent, msg='Введите строку', btn_text='Подтвердить',
                 entry_width=45, default_value='', validate_function=None,
                 check_answer_function=None, if_correct_function=None, if_incorrect_function=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.check_answer_function = check_answer_function  # Функция, проверяющая корректность ответа
        self.if_correct_function = if_correct_function  # Функция, вызываемая при корректном ответе
        self.if_incorrect_function = if_incorrect_function  # Функция, вызываемая при некорректном ответе
        self.closed = True  # Закрыто ли окно крестиком

        self.var_text = tk.StringVar(value=default_value)

        self.lbl_msg = ttk.Label(self, text=split_text(f'{msg}:', 45, add_right_spaces=False), justify='center',
                                 style='Default.TLabel')
        self.entry_inp = ttk.Entry(self, textvariable=self.var_text, width=entry_width,
                                   style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(  row=0, padx=6, pady=(6, 3))
        self.entry_inp.grid(row=1, padx=6, pady=(0, 6))
        self.btn_ok.grid(   row=2, padx=6, pady=(0, 6))

        if validate_function:
            self.vcmd = (self.register(validate_function), '%P')
            self.entry_inp.configure(validate='key', validatecommand=self.vcmd)

        self.entry_inp.icursor(len(default_value))

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
            self.lbl_img = ttk.Label(self, text='[!!!] Изображение не найдено [!!!]',
                                     justify='center', style='Default.TLabel')
        else:
            self.lbl_img = ttk.Label(self, image=self.img, style='Default.TLabel')
        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, add_right_spaces=False), justify='center',
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


""" Графический интерфейс - второстепенные окна """


# Окно выбора режима перед изучением слов
class ChooseLearnModeW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Выбор режима')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.res: tuple[str, str, str, str] | None = None

        self.var_method = tk.StringVar(value=LEARN_VALUES_METHOD[_0_global_learn_settings[0]])  # Метод изучения слов
        self.var_words = tk.StringVar(value=LEARN_VALUES_WORDS[_0_global_learn_settings[2]])  # Способ подбора слов
        self.var_forms = tk.StringVar(value=LEARN_VALUES_FORMS[_0_global_learn_settings[1]])  # Способ подбора словоформ
        self.var_order = tk.StringVar(value=LEARN_VALUES_ORDER[_0_global_learn_settings[3]])  # Порядок следования слов

        self.lbl_header = ttk.Label(self, text='Выберите способ учёбы', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_method = ttk.Label(self.frame_main, text='Метод:', style='Default.TLabel')
        self.combo_method = ttk.Combobox(self.frame_main, textvariable=self.var_method, values=LEARN_VALUES_METHOD,
                                         validate='focusin', width=30, state='readonly', style='Default.TCombobox',
                                         font=('DejaVu Sans Mono', _0_global_scale))
        #
        self.lbl_words = ttk.Label(self.frame_main, text='Набор статей:', style='Default.TLabel')
        self.combo_words = ttk.Combobox(self.frame_main, textvariable=self.var_words, values=LEARN_VALUES_WORDS,
                                        width=30, state='readonly', style='Default.TCombobox',
                                        font=('DejaVu Sans Mono', _0_global_scale))
        #
        self.lbl_forms = ttk.Label(self.frame_main, text='Набор словоформ:', style='Default.TLabel')
        self.combo_forms = ttk.Combobox(self.frame_main, textvariable=self.var_forms, values=LEARN_VALUES_FORMS,
                                        width=30, state='readonly', style='Default.TCombobox',
                                        font=('DejaVu Sans Mono', _0_global_scale))
        #
        self.lbl_order = ttk.Label(self.frame_main, text='Порядок заданий:', style='Default.TLabel')
        self.combo_order = ttk.Combobox(self.frame_main, textvariable=self.var_order, values=LEARN_VALUES_ORDER,
                                        width=30, state='readonly', style='Default.TCombobox',
                                        font=('DejaVu Sans Mono', _0_global_scale))
        # }
        self.btn_start = ttk.Button(self, text='Учить', command=self.start, takefocus=False, style='Default.TButton')

        self.lbl_header.grid(row=0, column=0, padx=6, pady=(6, 3))
        self.frame_main.grid(row=1, column=0, padx=6, pady=(0, 3))
        # {
        self.lbl_method.grid(  row=1, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.combo_method.grid(row=1, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_words.grid(   row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_words.grid( row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_forms.grid(   row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_forms.grid( row=3, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_order.grid(   row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.combo_order.grid( row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.btn_start.grid(row=2, column=0, padx=6, pady=(0, 6))

        # При выборе второго или третьего метода учёбы нельзя добавить словоформы
        def validate_method_and_forms(value: str):
            if value == LEARN_VALUES_METHOD[0]:
                self.lbl_forms.grid(  row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
                self.combo_forms.grid(row=3, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
            else:
                self.lbl_forms.grid_remove()
                self.combo_forms.grid_remove()
            return True

        self.vcmd_method = (self.register(validate_method_and_forms), '%P')
        self.combo_method['validatecommand'] = self.vcmd_method
        validate_method_and_forms(self.var_method.get())

    # Начать учить слова
    def start(self):
        global _0_global_learn_settings

        method = self.var_method.get()
        if method == LEARN_VALUES_METHOD[0]:
            forms = self.var_forms.get()
        else:
            forms = LEARN_VALUES_FORMS[0]
        words = self.var_words.get()
        order = self.var_order.get()
        self.res = (method, forms, words, order)
        _0_global_learn_settings = (LEARN_VALUES_METHOD.index(method),
                                    LEARN_VALUES_FORMS.index(forms),
                                    LEARN_VALUES_WORDS.index(words),
                                    LEARN_VALUES_ORDER.index(order))

        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)

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


# Окно с сообщением о неверном ответе (для слов, не находящихся в избранном)
class IncorrectAnswerW(tk.Toplevel):
    def __init__(self, parent, user_answer: str, correct_answer: str, with_typo: bool):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Неверно')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.with_typo = with_typo
        self.answer = 'no'  # Значение, возвращаемое методом self.open

        self.lbl_msg = ttk.Label(self, text=split_text(f'Неверно.\n'
                                                       f'Ваш ответ: {user_answer}\n'
                                                       f'Правильный ответ: {correct_answer}\n'
                                                       f'Хотите добавить слово в избранное?',
                                                       45, 5, add_right_spaces=False),
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

            self.tip_btn_typo = ttip.Hovertip(self.btn_typo, 'Не засчитывать ошибку\n'
                                                             'Tab',
                                              hover_delay=700)
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


# Окно с параметрами поиска
class SearchSettingsW(tk.Toplevel):
    def __init__(self, parent, search_only_fav: bool, search_only_full: bool,
                 search_wrd: bool, search_tr: bool, search_frm: bool, search_nt: bool):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Параметры поиска')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_search_only_fav = tk.BooleanVar(value=search_only_fav)
        self.var_search_only_full = tk.BooleanVar(value=search_only_full)
        self.var_search_wrd = tk.BooleanVar(value=search_wrd)
        self.var_search_tr = tk.BooleanVar(value=search_tr)
        self.var_search_frm = tk.BooleanVar(value=search_frm)
        self.var_search_nt = tk.BooleanVar(value=search_nt)

        self.lbl_search_only_fav = ttk.Label(self, text='Искать только среди избранных статей:', style='Default.TLabel')
        self.check_search_only_fav = ttk.Checkbutton(self, variable=self.var_search_only_fav,
                                                     style='Default.TCheckbutton')
        self.lbl_search_only_full = ttk.Label(self, text='Искать только точные совпадения:', style='Default.TLabel')
        self.check_search_only_full = ttk.Checkbutton(self, variable=self.var_search_only_full,
                                                      style='Default.TCheckbutton')
        self.frame = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_search_wrd = ttk.Label(self.frame, text='Искать среди слов:', style='Default.TLabel')
        self.check_search_wrd = ttk.Checkbutton(self.frame, variable=self.var_search_wrd, style='Default.TCheckbutton')
        self.lbl_search_tr = ttk.Label(self.frame, text='Искать среди переводов:', style='Default.TLabel')
        self.check_search_tr = ttk.Checkbutton(self.frame, variable=self.var_search_tr, style='Default.TCheckbutton')
        self.lbl_search_frm = ttk.Label(self.frame, text='Искать среди словоформ:', style='Default.TLabel')
        self.check_search_frm = ttk.Checkbutton(self.frame, variable=self.var_search_frm, style='Default.TCheckbutton')
        self.lbl_search_nt = ttk.Label(self.frame, text='Искать среди сносок:', style='Default.TLabel')
        self.check_search_nt = ttk.Checkbutton(self.frame, variable=self.var_search_nt, style='Default.TCheckbutton')
        # }

        self.lbl_search_only_fav.grid(   row=0, column=0,               padx=(6, 1), pady=6,      sticky='E')
        self.check_search_only_fav.grid( row=0, column=1,               padx=(0, 6), pady=6,      sticky='W')
        self.lbl_search_only_full.grid(  row=1, column=0,               padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_only_full.grid(row=1, column=1,               padx=(0, 6), pady=(0, 6), sticky='W')
        self.frame.grid(                 row=2, column=0, columnspan=2, padx=6,      pady=6)
        # {
        self.lbl_search_wrd.grid(  row=0, column=0, padx=(6, 1), pady=6,      sticky='E')
        self.check_search_wrd.grid(row=0, column=1, padx=(0, 6), pady=6,      sticky='W')
        self.lbl_search_tr.grid(   row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_tr.grid( row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_frm.grid(  row=2, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_frm.grid(row=2, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_nt.grid(   row=3, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_nt.grid( row=3, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.destroy())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        global _0_global_search_settings

        self.set_focus()

        self.grab_set()
        self.wait_window()

        _0_global_search_settings = (int(self.var_search_only_fav.get()),
                                     int(self.var_search_only_full.get()),
                                     int(self.var_search_wrd.get()),
                                     int(self.var_search_tr.get()),
                                     int(self.var_search_frm.get()),
                                     int(self.var_search_nt.get()))
        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)

        return self.var_search_only_fav.get(), self.var_search_only_full.get(), self.var_search_wrd.get(),\
            self.var_search_tr.get(), self.var_search_frm.get(), self.var_search_nt.get()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseOneOfSimilarEntriesW(tk.Toplevel):
    def __init__(self, parent, query: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Найдено несколько схожих статей')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.search_wrd = query
        self.answer = None

        self.lbl_header = ttk.Label(self, text='Выберите одну из статей', justify='center', style='Default.TLabel')
        self.scrolled_frame_wrd = ScrollFrame(self, SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                              SCALE_DEFAULT_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        # {
        self.widgets_wrd = []
        # }

        self.lbl_header.grid(        row=0, column=0, padx=(6, 3), pady=(6, 3))
        self.scrolled_frame_wrd.grid(row=1, column=0, padx=6,      pady=(0, 6))

        self.print()

    # Выбрать статью из предложенных вариантов
    def choose_entry(self, key: tuple[str, int]):
        self.answer = key
        self.destroy()

    # Вывод вариантов
    def print(self):
        # Вывод вариантов
        keys = [key for key in _0_global_dct.d.keys() if key[0] == self.search_wrd]
        for key in keys:
            self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                            text=get_all_entry_info(_0_global_dct.d[key], 75, 13),
                                            command=lambda key=key: self.choose_entry(key),
                                            takefocus=False, style='Note.TButton')]

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


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, key: tuple[str, int]):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Изменение статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.dct_key = key
        self.line_width = 35
        self.max_height_w = 3
        self.max_height_t = 6
        self.max_height_n = 4
        self.max_height_f = 6

        self.var_fav = tk.BooleanVar(value=_0_global_dct.d[key].fav)

        self.img_edit = tk.PhotoImage()
        self.img_add = tk.PhotoImage()
        self.img_about = tk.PhotoImage()

        self.translations = []
        self.tr_frames = []
        self.tr_buttons = []
        #
        self.notes = []
        self.nt_frames = []
        self.nt_buttons = []
        #
        self.forms = []
        self.frm_frames = []
        self.frm_buttons = []

        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_wrd = ttk.Label(self.frame_main, text='Слово:', style='Default.TLabel')
        self.scrollbar_wrd = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_wrd = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_wrd.set,
                               font=('DejaVu Sans Mono', _0_global_scale + 1), relief='solid', bg=ST_BG_FIELDS[th],
                               fg=ST_FG[th], selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                               highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar_wrd.config(command=self.txt_wrd.yview)
        self.btn_wrd_edt = ttk.Button(self.frame_main, command=self.wrd_edt, width=4, takefocus=False)
        set_image(self.btn_wrd_edt, self.img_edit, img_edit, 'изм.')
        if self.btn_wrd_edt['style'] == 'Image.TButton':
            self.tip_btn_wrd_edt = ttip.Hovertip(self.btn_wrd_edt, 'Изменить слово', hover_delay=500)
        #
        self.lbl_tr = ttk.Label(self.frame_main, text='Перевод:', style='Default.TLabel')
        self.scrolled_frame_tr = ScrollFrame(self.frame_main,
                                             SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                             SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_tr_add = ttk.Button(self.frame_main, command=self.tr_add, width=2, takefocus=False)
        set_image(self.btn_tr_add, self.img_add, img_add, '+')
        if self.btn_tr_add['style'] == 'Image.TButton':
            self.tip_btn_tr_add = ttip.Hovertip(self.btn_tr_add, 'Добавить перевод', hover_delay=500)
        #
        self.lbl_notes = ttk.Label(self.frame_main, text='Сноски:', style='Default.TLabel')
        self.scrolled_frame_nt = ScrollFrame(self.frame_main,
                                             SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                             SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_note_add = ttk.Button(self.frame_main, command=self.note_add, width=2, takefocus=False)
        set_image(self.btn_note_add, self.img_add, img_add, '+')
        if self.btn_note_add['style'] == 'Image.TButton':
            self.tip_btn_note_add = ttip.Hovertip(self.btn_note_add, 'Добавить сноску', hover_delay=500)
        #
        self.lbl_frm = ttk.Label(self.frame_main, text='Формы слова:', style='Default.TLabel')
        self.scrolled_frame_frm = ScrollFrame(self.frame_main,
                                              SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                              SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_frm_add = ttk.Button(self.frame_main, command=self.frm_add, width=2, takefocus=False)
        set_image(self.btn_frm_add, self.img_add, img_add, '+')
        if self.btn_frm_add['style'] == 'Image.TButton':
            self.tip_btn_frm_add = ttip.Hovertip(self.btn_frm_add, 'Добавить словоформу', hover_delay=500)
        #
        self.lbl_fav = ttk.Label(self.frame_main, text='Избранное:', style='Default.TLabel')
        self.check_fav = ttk.Checkbutton(self.frame_main, variable=self.var_fav, command=self.set_fav,
                                         style='Default.TCheckbutton')
        # }
        self.btn_back = ttk.Button(self, text='Закончить', command=self.back, takefocus=False, style='Default.TButton')
        self.btn_about_window = ttk.Button(self, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.btn_delete = ttk.Button(self, text='Удалить статью', command=self.delete,
                                     takefocus=False, style='No.TButton')

        self.frame_main.grid(row=0, columnspan=3, padx=6, pady=(6, 4))
        # {
        self.lbl_wrd.grid(      row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.txt_wrd.grid(      row=0, column=1, padx=(0, 1), pady=(6, 3), sticky='W')
        self.scrollbar_wrd.grid(row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.btn_wrd_edt.grid(  row=0, column=3, padx=(3, 6), pady=(6, 3), sticky='W')
        #
        self.lbl_tr.grid(           row=1, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_tr.grid(row=1, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_tr_add.grid(       row=1, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_notes.grid(        row=2, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_nt.grid(row=2, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_note_add.grid(     row=2, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_frm.grid(           row=3, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_frm.grid(row=3, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_frm_add.grid(       row=3, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_fav.grid(  row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_fav.grid(row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.btn_back.grid(        row=1, column=0, padx=(6, 0), pady=(0, 6))
        self.btn_about_window.grid(row=1, column=1, padx=(6, 6), pady=(0, 6))
        self.btn_delete.grid(      row=1, column=2, padx=(0, 6), pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

        self.refresh(True)

    # Изменить слово
    def wrd_edt(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новое слово', default_value=_0_global_dct.d[self.dct_key].wrd,
                             check_answer_function=lambda wnd, val:
                             check_not_void(wnd, val, 'Слово должно содержать хотя бы один символ!'))
        closed, new_wrd = window.open()
        if closed:
            return
        new_wrd = encode_special_combinations(new_wrd)
        if new_wrd == _0_global_dct.d[self.dct_key].wrd:
            return

        new_key = edit_wrd_with_choose(_0_global_dct, self, self.dct_key, new_wrd)
        if new_key == self.dct_key:
            return
        self.dct_key = new_key

        _0_global_has_progress = True
        self.refresh(False)

    # Добавить перевод
    def tr_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новый перевод',
                             check_answer_function=lambda wnd, val:
                             check_tr(wnd, _0_global_dct.d[self.dct_key].tr, val, key_to_wrd(self.dct_key)))
        closed, tr = window.open()
        if closed:
            return
        tr = encode_special_combinations(tr)

        _0_global_dct.add_tr(self.dct_key, tr)

        _0_global_has_progress = True
        self.refresh(False)

    # Изменить перевод
    def tr_edt(self, tr: str):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новый перевод', default_value=tr,
                             check_answer_function=lambda wnd, val:
                             check_tr_edit(wnd, _0_global_dct.d[self.dct_key].tr, tr, val, key_to_wrd(self.dct_key)))
        closed, new_tr = window.open()
        if closed:
            return
        new_tr = encode_special_combinations(new_tr)

        _0_global_dct.delete_tr(self.dct_key, tr)
        _0_global_dct.add_tr(self.dct_key, new_tr)

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить перевод
    def tr_del(self, tr: str):
        global _0_global_has_progress

        if len(self.translations) == 1:
            warning(self, 'Вы не можете удалить единственный перевод!')
            return

        _0_global_dct.delete_tr(self.dct_key, tr)

        _0_global_has_progress = True
        self.refresh(False)

    # Добавить сноску
    def note_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите сноску',
                             check_answer_function=lambda wnd, val:
                             check_note(wnd, _0_global_dct.d[self.dct_key].notes, val, key_to_wrd(self.dct_key)))
        closed, note = window.open()
        if closed:
            return
        note = encode_special_combinations(note)

        _0_global_dct.add_note(self.dct_key, note)

        _0_global_has_progress = True
        self.refresh(False)

    # Изменить сноску
    def note_edt(self, note: str):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите сноску', default_value=note,
                             check_answer_function=lambda wnd, val:
                             check_note_edit(wnd, _0_global_dct.d[self.dct_key].notes, note, val,
                                             key_to_wrd(self.dct_key)))
        closed, new_note = window.open()
        if closed:
            return
        new_note = encode_special_combinations(new_note)

        _0_global_dct.delete_note(self.dct_key, note)
        _0_global_dct.add_note(self.dct_key, new_note)

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить сноску
    def note_del(self, note: str):
        global _0_global_has_progress

        _0_global_dct.delete_note(self.dct_key, note)

        _0_global_has_progress = True
        self.refresh(False)

    # Добавить словоформу
    def frm_add(self):
        global _0_global_has_progress

        if not _0_global_categories:
            warning(self, 'Отсутствуют категории слов!\n'
                          'Чтобы их добавить, перейдите в\n'
                          'Настройки/Настройки словаря/Грамматические категории')
            return

        window_form = AddFormW(self, self.dct_key, combo_width=combobox_width(tuple(_0_global_categories.keys()),
                                                                              5, 100))  # Создание словоформы
        frm_key, frm = window_form.open()
        if not frm_key:
            return
        frm = encode_special_combinations(frm)

        _0_global_dct.add_frm(self.dct_key, frm_key, frm)

        _0_global_has_progress = True
        self.refresh(False)

    # Изменить словоформу
    def frm_edt(self, frm_key: tuple[str, ...]):
        global _0_global_has_progress

        window_entry = PopupEntryW(self, 'Введите новую форму слова',
                                   default_value=_0_global_dct.d[self.dct_key].forms[frm_key],
                                   check_answer_function=lambda wnd, val:
                                   check_not_void(wnd, val, 'Словоформа должна содержать хотя бы один символ!'))
        closed, new_frm = window_entry.open()
        if closed:
            return
        new_frm = encode_special_combinations(new_frm)

        _0_global_dct.d[self.dct_key].forms[frm_key] = new_frm

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить словоформу
    def frm_del(self, frm_key: tuple[str, ...]):
        global _0_global_has_progress

        _0_global_dct.delete_frm(self.dct_key, frm_key)

        _0_global_has_progress = True
        self.refresh(False)

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
    def refresh(self, move_scroll: bool):
        # Обновляем поле со словом
        self.txt_wrd['state'] = 'normal'
        self.txt_wrd.delete(1.0, tk.END)
        self.txt_wrd.insert(tk.END, _0_global_dct.d[self.dct_key].wrd)
        self.txt_wrd['state'] = 'disabled'
        #
        height_w = max(min(field_height(_0_global_dct.d[self.dct_key].wrd, self.line_width), self.max_height_w), 1)
        self.txt_wrd['height'] = height_w
        #
        if height_w < self.max_height_w:
            self.scrollbar_wrd.grid_remove()
        else:
            self.scrollbar_wrd.grid(row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')

        # Удаляем старые кнопки
        for btn in self.tr_buttons + self.nt_buttons + self.frm_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.tr_frames + self.nt_frames + self.frm_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-E>')
            fr.unbind('<Control-e>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        # Выбираем комбинации
        self.translations = [tr for tr in _0_global_dct.d[self.dct_key].tr]
        self.notes = [nt for nt in _0_global_dct.d[self.dct_key].notes]
        self.forms = [frm for frm in _0_global_dct.d[self.dct_key].forms.keys()]
        tr_count = len(self.translations)
        nt_count = len(self.notes)
        frm_count = len(self.forms)

        # Создаём новые фреймы
        self.tr_frames = tuple([ttk.Frame(self.scrolled_frame_tr.frame_canvas, style='Invis.TFrame')
                                for i in range(tr_count)])
        self.nt_frames = tuple([ttk.Frame(self.scrolled_frame_nt.frame_canvas, style='Invis.TFrame')
                                for i in range(nt_count)])
        self.frm_frames = tuple([ttk.Frame(self.scrolled_frame_frm.frame_canvas, style='Invis.TFrame')
                                 for i in range(frm_count)])
        # Создаём новые кнопки
        self.tr_buttons = [ttk.Button(self.tr_frames[i], command=lambda i=i: self.tr_edt(self.translations[i]),
                                      takefocus=False, style='Note.TButton')
                           for i in range(tr_count)]
        self.nt_buttons = [ttk.Button(self.nt_frames[i], command=lambda i=i: self.note_edt(self.notes[i]),
                                      takefocus=False, style='Note.TButton')
                           for i in range(nt_count)]
        self.frm_buttons = [ttk.Button(self.frm_frames[i], command=lambda i=i: self.frm_edt(self.forms[i]),
                                       takefocus=False, style='Note.TButton')
                            for i in range(frm_count)]
        # Выводим текст на кнопки
        for i in range(tr_count):
            tr = self.translations[i]
            self.tr_buttons[i].configure(text=split_text(tr, 35))
        for i in range(nt_count):
            nt = self.notes[i]
            self.nt_buttons[i].configure(text=split_text(nt, 35))
        for i in range(frm_count):
            frm = self.forms[i]
            self.frm_buttons[i].configure(text=split_text(f'[{frm_key_to_str_for_print(frm)}] {_0_global_dct.d[self.dct_key].forms[frm]}', 35))
        # Расставляем элементы
        for i in range(tr_count):
            self.tr_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.tr_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        for i in range(nt_count):
            self.nt_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.nt_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        for i in range(frm_count):
            self.frm_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.frm_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(tr_count):
            self.tr_frames[i].bind('<Enter>', lambda event, i=i: self.tr_frames[i].focus_set())
            self.tr_frames[i].bind('<Control-D>', lambda event, i=i: self.tr_del(self.translations[i]))
            self.tr_frames[i].bind('<Control-d>', lambda event, i=i: self.tr_del(self.translations[i]))
            self.tr_frames[i].bind('<Leave>', lambda event: self.focus_set())
        for i in range(nt_count):
            self.nt_frames[i].bind('<Enter>', lambda event, i=i: self.nt_frames[i].focus_set())
            self.nt_frames[i].bind('<Control-D>', lambda event, i=i: self.note_del(self.notes[i]))
            self.nt_frames[i].bind('<Control-d>', lambda event, i=i: self.note_del(self.notes[i]))
            self.nt_frames[i].bind('<Leave>', lambda event: self.focus_set())
        for i in range(frm_count):
            self.frm_frames[i].bind('<Enter>', lambda event, i=i: self.frm_frames[i].focus_set())
            self.frm_frames[i].bind('<Control-D>', lambda event, i=i: self.frm_del(self.forms[i]))
            self.frm_frames[i].bind('<Control-d>', lambda event, i=i: self.frm_del(self.forms[i]))
            self.frm_frames[i].bind('<Leave>', lambda event: self.focus_set())
        # Изменяем высоту полей
        self.scrolled_frame_tr.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                             for btn in self.tr_buttons]),
                                                        self.max_height_t)) *
                                             SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_nt.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                             for btn in self.nt_buttons]),
                                                        self.max_height_n)) *
                                             SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_frm.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                              for btn in self.frm_buttons]),
                                                         self.max_height_f)) *
                                              SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_tr.canvas.yview_moveto(0.0)
            self.scrolled_frame_nt.canvas.yview_moveto(0.0)
            self.scrolled_frame_frm.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы изменить поле, наведите на него мышку и нажмите ЛКМ\n'
                        '* Чтобы удалить поле, наведите на него мышку и нажмите Ctrl+D',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_back.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


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

        self.img_ok = tk.PhotoImage()
        self.img_none = tk.PhotoImage()

        self.lbl_choose_ctg = ttk.Label(self, text='Выберите категорию:', justify='center', style='Default.TLabel')
        self.combo_ctg = ttk.Combobox(self, textvariable=self.var_ctg, values=self.categories, width=combo_width,
                                      state='readonly', style='Default.TCombobox',
                                      font=('DejaVu Sans Mono', _0_global_scale))
        self.lbl_choose_val = ttk.Label(self, text='Задайте значение категории:', justify='center',
                                        style='Default.TLabel')
        self.frame_val = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.combo_val = ttk.Combobox(self.frame_val, textvariable=self.var_val, values=self.ctg_values,
                                      width=combobox_width(self.ctg_values, 5, 100),
                                      state='readonly', style='Default.TCombobox',
                                      font=('DejaVu Sans Mono', _0_global_scale))
        self.btn_choose = ttk.Button(self.frame_val, command=self.choose, takefocus=False)
        set_image(self.btn_choose, self.img_ok, img_ok, 'Задать значение')
        if self.btn_choose['style'] == 'Image.TButton':
            self.tip_btn_choose = ttip.Hovertip(self.btn_choose, 'Задать значение', hover_delay=500)
        self.btn_none = ttk.Button(self.frame_val, command=self.set_none, takefocus=False)
        set_image(self.btn_none, self.img_none, img_cancel, 'Не указывать/неприменимо')
        if self.btn_none['style'] == 'Image.TButton':
            self.tip_btn_none = ttip.Hovertip(self.btn_none, 'Не указывать/неприменимо', hover_delay=500)
        # }
        self.lbl_template = ttk.Label(self, textvariable=self.var_template, justify='center', style='Default.TLabel')
        self.frame_form = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_form = ttk.Label(self.frame_form, text='Форма:', justify='left', style='Default.TLabel')
        self.entry_form = ttk.Entry(self.frame_form, textvariable=self.var_form,
                                    style='Default.TEntry', font=('StdFont', _0_global_scale))
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

        btn_disable(self.btn_save)

        self.entry_form.icursor(len(self.var_form.get()))

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

        self.var_template.set(f'Текущий шаблон словоформы: "{frm_key_to_str_for_print(self.template)}"')

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

        self.var_template.set(f'Текущий шаблон словоформы: "{frm_key_to_str_for_print(self.template)}"')

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
                                 width=combobox_width(self.ctg_values, 5, 100))

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_form.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_choose.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())
        self.combo_ctg.bind('<<ComboboxSelected>>', lambda event=None: self.refresh_vals())

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


# Окно настроек категорий
class CategoriesSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.categories = []
        self.frames = []
        self.buttons = []

        self.btn_about_window = ttk.Button(self, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_categories = ttk.Label(self, text='Существующие категории слов:',
                                        justify='center', style='Default.TLabel')
        self.scrolled_frame = ScrollFrame(self, SCALE_SMALL_FRAME_HEIGHT_TALL[_0_global_scale - SCALE_MIN],
                                          SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_add = ttk.Button(self, text='Добавить категорию', command=self.add, takefocus=False,
                                  style='Default.TButton')

        self.btn_about_window.grid(row=0, column=0,               padx=(6, 0), pady=(6, 6), sticky='E')
        self.lbl_categories.grid(  row=0, column=1,               padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame.grid(  row=1, column=0, columnspan=2, padx=6,      pady=(0, 6))
        self.btn_add.grid(         row=2, column=0, columnspan=2, padx=6,      pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

        self.print_categories(True)

    # Добавить категорию
    def add(self):
        self.has_changes = add_ctg(self, _0_global_categories, _0_global_dct) or self.has_changes
        self.print_categories(False)

    # Переименовать категорию
    def rename(self, ctg_key: str):
        self.has_changes = rename_ctg(self, _0_global_categories, ctg_key) or self.has_changes
        self.print_categories(False)

    # Удалить категорию
    def delete(self, ctg_key: str, to_ask: bool):
        self.has_changes = delete_ctg(self, _0_global_categories, ctg_key, _0_global_dct, to_ask) or self.has_changes
        self.print_categories(False)

    # Перейти к настройкам значений категории
    def values(self, ctg_key: str):
        self.has_changes = CategoryValuesSettingsW(self, ctg_key).open() or self.has_changes

    # Напечатать существующие категории
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

        # Выбираем категории
        self.categories = [key for key in _0_global_categories.keys()]
        categories_count = len(self.categories)

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(categories_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.values(self.categories[i]),
                                   takefocus=False, style='Note.TButton')
                        for i in range(categories_count)]
        # Выводим текст на кнопки
        for i in range(categories_count):
            ctg = self.categories[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))
        # Расставляем элементы
        for i in range(categories_count):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(categories_count):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.categories[i]))
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.categories[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.categories[i], True))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.categories[i], True))
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы добавить значение категории, наведите на неё мышку и нажмите ЛКМ\n'
                        '* Чтобы переименовать категорию, наведите на неё мышку и нажмите Ctrl+R\n'
                        '* Чтобы удалить категорию, наведите на неё мышку и нажмите Ctrl+D',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.destroy())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек групп
class GroupsSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.groups = []
        self.frames = []
        self.buttons = []

        self.btn_about_window = ttk.Button(self, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_groups = ttk.Label(self, text='Существующие группы:', justify='center', style='Default.TLabel')
        self.scrolled_frame = ScrollFrame(self, SCALE_SMALL_FRAME_HEIGHT_TALL[_0_global_scale - SCALE_MIN],
                                          SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_add = ttk.Button(self, text='Добавить группу', command=self.add, takefocus=False,
                                  style='Default.TButton')

        self.btn_about_window.grid(row=0, column=0,               padx=(6, 0), pady=(6, 6), sticky='E')
        self.lbl_groups.grid(      row=0, column=1,               padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame.grid(  row=1, column=0, columnspan=2, padx=6,      pady=(0, 6))
        self.btn_add.grid(         row=2, column=0, columnspan=2, padx=6,      pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

        self.print_groups(True)

    # Добавить группу
    def add(self):
        window = PopupEntryW(self, 'Введите название новой группы',
                             check_answer_function=lambda wnd, val: check_group_name(wnd, _0_global_dct.groups, val))
        closed, group = window.open()
        if closed:
            return
        group = encode_special_combinations(group)
        _0_global_dct.add_group(group)

        self.print_groups(False)
        self.has_changes = True

    # Переименовать группу
    def rename(self, group_old: str):
        window = PopupEntryW(self, 'Введите новое название группы', default_value=group_old,
                             check_answer_function=lambda wnd, val:
                             check_group_name_edit(wnd, _0_global_dct.groups, group_old, val))
        closed, group_new = window.open()
        if closed:
            return
        group_new = encode_special_combinations(group_new)
        _0_global_dct.rename_group(group_old, group_new)

        self.print_groups(False)
        self.has_changes = True

    # Удалить группу
    def delete(self, group: str):
        _0_global_dct.delete_group(group)

        self.print_groups(False)
        self.has_changes = True

    # Напечатать существующие группы
    def print_groups(self, move_scroll: bool):
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

        # Выбираем группы
        self.groups = [group for group in _0_global_dct.groups]
        groups_count = len(self.groups)

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(groups_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i], command=lambda i=i: self.rename(self.groups[i]),
                                   takefocus=False, style='Note.TButton')
                        for i in range(groups_count)]
        # Выводим текст на кнопки
        for i in range(groups_count):
            group = self.groups[i]
            self.buttons[i].configure(text=split_text(f'{group}', 35))
        # Расставляем элементы
        for i in range(groups_count):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(groups_count):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.groups[i]))
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.groups[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.groups[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.groups[i]))
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы переименовать группу, наведите на неё мышку и нажмите ЛКМ или Ctrl+R\n'
                        '* Чтобы удалить группу, наведите на неё мышку и нажмите Ctrl+D',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.destroy())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек значений категории
class CategoryValuesSettingsW(tk.Toplevel):
    def __init__(self, parent, ctg_key: str):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.parent = parent
        self.ctg_key = ctg_key  # Название изменяемой категории
        self.ctg_values = _0_global_categories[self.ctg_key]  # Значения изменяемой категории
        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.values = []
        self.frames = []
        self.buttons = []

        self.btn_about_window = ttk.Button(self, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_ctg_values = ttk.Label(self, text=f'Существующие значения категории\n'
                                                   f'"{self.ctg_key}":',
                                        justify='center', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.scrolled_frame = ScrollFrame(self, SCALE_SMALL_FRAME_HEIGHT_TALL[_0_global_scale - SCALE_MIN],
                                          SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_add = ttk.Button(self, text='Добавить значение', command=self.add, takefocus=False,
                                  style='Default.TButton')

        self.btn_about_window.grid(row=0, column=0,               padx=(6, 0), pady=(6, 6), sticky='E')
        self.lbl_ctg_values.grid(  row=0, column=1,               padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame.grid(  row=1, column=0, columnspan=2, padx=6,      pady=(0, 6))
        self.btn_add.grid(         row=2, column=0, columnspan=2, padx=6,      pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

        self.print_ctg_values(True)

    # Добавить значение категории
    def add(self):
        has_changes, new_val = add_ctg_val(self, self.ctg_values)
        self.has_changes = self.has_changes or has_changes
        if not new_val:
            return
        self.ctg_values += [new_val]
        self.print_ctg_values(False)

    # Переименовать значение категории
    def rename(self, val: str):
        index = tuple(_0_global_categories).index(self.ctg_key)
        self.has_changes = rename_ctg_val(self, self.ctg_values, val, index, _0_global_dct) or self.has_changes
        self.print_ctg_values(False)

    # Удалить значение категории
    def delete(self, val: str):
        self.has_changes = delete_ctg_val(self, self.ctg_values, val, _0_global_dct) or self.has_changes
        self.print_ctg_values(False)
        if not self.ctg_values:
            self.parent.delete(self.ctg_key, False)
            self.destroy()

    # Напечатать существующие значения категории
    def print_ctg_values(self, move_scroll: bool):
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

        # Выбираем значения
        self.values = [val for val in self.ctg_values]
        categories_count = len(self.values)

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(categories_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.rename(self.values[i]),
                                   takefocus=False, style='Note.TButton')
                        for i in range(categories_count)]
        # Выводим текст на кнопки
        for i in range(categories_count):
            ctg = self.values[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))
        # Расставляем элементы
        for i in range(categories_count):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(categories_count):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.values[i]))
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.values[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.values[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.values[i]))
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы переименовать значение, наведите на него мышку и нажмите ЛКМ или Ctrl+R\n'
                        '* Чтобы удалить значение, наведите на него мышку и нажмите Ctrl+D',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.destroy())
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

        self.img_about = tk.PhotoImage()

        self.combinations = []
        self.frames = []
        self.buttons = []

        self.btn_about_window = ttk.Button(self, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_combinations = ttk.Label(self, text='Существующие комбинации:', justify='center',
                                          style='Default.TLabel')
        self.scrolled_frame = ScrollFrame(self, SCALE_SMALL_FRAME_HEIGHT_TALL[_0_global_scale - SCALE_MIN],
                                          SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_add = ttk.Button(self, text='Добавить комбинацию', command=self.add, takefocus=False,
                                  style='Default.TButton')

        self.btn_about_window.grid(row=0, column=0,               padx=(6, 0), pady=(6, 6), sticky='E')
        self.lbl_combinations.grid(row=0, column=1,               padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame.grid(  row=1, column=0, columnspan=2, padx=6,      pady=(0, 6))
        self.btn_add.grid(         row=2, column=0, columnspan=2, padx=6,      pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

        self.print_combinations(True)

    # Добавить комбинацию
    def add(self):
        window = EnterSpecialCombinationW(self)
        closed, key, val = window.open()
        if closed or key[0] == '' or key[1] == '' or val == '':
            return
        if key in _0_global_special_combinations.keys():
            warning(self, f'Комбинация {key[0]}{key[1]} уже существует!')
            return
        _0_global_special_combinations[key] = val
        self.print_combinations(False)
        self.has_changes = True

    # Изменить комбинацию
    def edit(self, old_key: tuple[str, str]):
        old_val = _0_global_special_combinations[old_key]
        window = EnterSpecialCombinationW(self, default_value=old_key+tuple(old_val))
        closed, new_key, new_val = window.open()
        if closed or new_key[0] == '' or new_key[1] == '' or new_val == '':
            return
        if new_key == old_key and new_val == old_val:
            return

        _0_global_special_combinations.pop(old_key)

        _0_global_special_combinations[new_key] = new_val
        self.print_combinations(False)
        self.has_changes = True

    # Удалить комбинацию
    def delete(self, cmb_key: tuple[str, str]):
        _0_global_special_combinations.pop(cmb_key)
        self.print_combinations(False)
        self.has_changes = True

    # Напечатать существующие комбинации
    def print_combinations(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons:
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

        # Выбираем комбинации
        self.combinations = [key for key in _0_global_special_combinations]
        combinations_count = len(self.combinations)

        # Создаём новые фреймы
        self.frames = tuple([ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                             for i in range(combinations_count)]) +\
                      tuple([ttk.Label(self.scrolled_frame.frame_canvas,
                                       text=split_text('## -> #, %% -> % и т. д.', 35), style='Note.TLabel')])
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.edit(self.combinations[i]),
                                   takefocus=False, style='Note.TButton')
                        for i in range(combinations_count)]
        # Выводим текст на кнопки
        for i in range(combinations_count):
            cmb = self.combinations[i]
            self.buttons[i].configure(text=split_text(special_combination(cmb), 35))
        # Расставляем элементы
        for i in range(combinations_count):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        self.frames[combinations_count].grid(row=combinations_count, column=0, padx=0, pady=0, sticky='WE')
        # Привязываем события
        for i in range(combinations_count):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Control-E>', lambda event, i=i: self.edit(self.combinations[i]))
            self.frames[i].bind('<Control-e>', lambda event, i=i: self.edit(self.combinations[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.combinations[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.combinations[i]))
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы изменить комбинацию, наведите на неё мышку и нажмите ЛКМ или Ctrl+E\n'
                        '* Чтобы удалить комбинацию, наведите на неё мышку и нажмите Ctrl+D',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.destroy())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно ввода специальной комбинации
class EnterSpecialCombinationW(tk.Toplevel):
    def __init__(self, parent,
                 default_value: tuple[str, str, str] = (SPECIAL_COMBINATIONS_OPENING_SYMBOLS[0], None, None)):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Закрыто ли окно крестиком

        self.var_opening_symbol = tk.StringVar(value=default_value[0])
        self.var_key_symbol = tk.StringVar(value=default_value[1])
        self.var_val = tk.StringVar(value=default_value[2])

        self.vcmd_opening_symbol = (self.register(validate_special_combination_opening_symbol), '%P')
        self.vcmd_key_symbol = (self.register(validate_special_combination_key_symbol), '%P')
        self.vcmd_val = (self.register(validate_special_combination_val), '%P')

        self.lbl_msg = ttk.Label(self, text='Задайте комбинацию', justify='center', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.combo_opening_symbol = ttk.Combobox(self.frame_main, textvariable=self.var_opening_symbol,
                                                 values=SPECIAL_COMBINATIONS_OPENING_SYMBOLS,
                                                 validate='all', validatecommand=self.vcmd_opening_symbol,
                                                 width=3, state='normal', style='Default.TCombobox',
                                                 font=('DejaVu Sans Mono', _0_global_scale))
        self.entry_key_symbol = ttk.Entry(self.frame_main, textvariable=self.var_key_symbol, width=2, justify='right',
                                          validate='key', validatecommand=self.vcmd_key_symbol, style='Default.TEntry',
                                          font=('StdFont', _0_global_scale))
        self.lbl_arrow = ttk.Label(self.frame_main, text='->', justify='center', style='Default.TLabel')
        self.entry_val = ttk.Entry(self.frame_main, textvariable=self.var_val, width=2,
                                   validate='key', validatecommand=self.vcmd_val,
                                   style='Default.TEntry', font=('StdFont', _0_global_scale))
        # }
        self.btn_ok = ttk.Button(self, text='Подтвердить', command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(   row=0, padx=6, pady=(6, 3))
        self.frame_main.grid(row=1, padx=6, pady=0)
        # {
        self.combo_opening_symbol.grid(row=0, column=0, padx=0, pady=0)
        self.entry_key_symbol.grid(    row=0, column=1, padx=0, pady=0)
        self.lbl_arrow.grid(           row=0, column=2, padx=2, pady=0)
        self.entry_val.grid(           row=0, column=3, padx=0, pady=0)
        # }
        self.btn_ok.grid(row=2, padx=6, pady=6)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_key_symbol.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, (self.var_opening_symbol.get(), self.var_key_symbol.get()), self.var_val.get()


# Окно настроек пользовательской темы
class CustomThemeSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Настройки пользовательской темы')
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

        self.img_undo = tk.PhotoImage()
        self.img_redo = tk.PhotoImage()

        self.frame_themes = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_set_theme = ttk.Label(self.frame_themes, text='Взять за основу уже существующую тему:',
                                       style='Default.TLabel')
        self.combo_set_theme = ttk.Combobox(self.frame_themes, textvariable=self.var_theme, values=THEMES[1:],
                                            state='readonly', style='Default.TCombobox',
                                            font=('DejaVu Sans Mono', _0_global_scale))
        self.btn_set_theme = ttk.Button(self.frame_themes, text='Выбрать', width=8, command=self.set_theme,
                                        takefocus=False, style='Default.TButton')
        self.lbl_set_images = ttk.Label(self.frame_themes, text='Использовать изображения из темы:',
                                        style='Default.TLabel')
        self.combo_set_images = ttk.Combobox(self.frame_themes, textvariable=self.var_images, values=THEMES[1:],
                                             state='readonly', style='Default.TCombobox',
                                             font=('DejaVu Sans Mono', _0_global_scale))
        self.btn_set_images = ttk.Button(self.frame_themes, text='Выбрать', width=8, command=self.set_images,
                                         takefocus=False, style='Default.TButton')
        # }
        # Прокручиваемая область с настройками
        self.scrolled_frame = ScrollFrame(self, SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                          SCALE_CUSTOM_THEME_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
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
            if el not in ('RELIEF_FRAME', 'RELIEF_TEXT'):
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
                                               width=SCALE_CUSTOM_THEME_COMBO_WIDTH[_0_global_scale - SCALE_MIN],
                                               validate='focus', validatecommand=self.vcmd_relief_frame,
                                               state='readonly', style='Default.TCombobox',
                                               font=('DejaVu Sans Mono', _0_global_scale))

        self.lbl_relief_text = ttk.Label(self.scrolled_frame.frame_canvas, text='Стиль рамок текстовых полей:',
                                         style='Default.TLabel')
        self.combo_relief_text = ttk.Combobox(self.scrolled_frame.frame_canvas, textvariable=self.var_relief_text,
                                              values=('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
                                              width=SCALE_CUSTOM_THEME_COMBO_WIDTH[_0_global_scale - SCALE_MIN],
                                              validate='focus', validatecommand=self.vcmd_relief_text,
                                              state='readonly', style='Default.TCombobox',
                                              font=('DejaVu Sans Mono', _0_global_scale))
        # }
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_save = ttk.Button(self.frame_buttons, text='Сохранить', command=self.save, takefocus=False,
                                   style='Yes.TButton')
        self.frame_history = ttk.Frame(self.frame_buttons, style='Invis.TFrame')
        # { {
        self.btn_undo = ttk.Button(self.frame_history, width=2, command=self.undo, takefocus=False)
        set_image(self.btn_undo, self.img_undo, img_undo, '<<')
        self.btn_redo = ttk.Button(self.frame_history, width=2, command=self.redo, takefocus=False)
        set_image(self.btn_redo, self.img_redo, img_redo, '>>')
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
        self.entry_demo = ttk.Entry(self.frame_demonstration, width=20,
                                    style='DemoDefault.TEntry', font=('StdFont', _0_global_scale))
        self.txt_demo = tk.Text(self.frame_demonstration, font=('StdFont', _0_global_scale), width=12, height=4,
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

        # *---0-------------------------------1-----------------------*
        # |                                                           |
        # 0   *---------------------------* - - - - - - - - - - - *   |
        # |   |  [lbl]   [combo]   [btn]  |                       :   |
        # |   |  [lbl]   [combo]   [btn]  |                       :   |
        # |   *---------------------------* - - - - - - - - - - - *   |
        # |                                                           |
        # 1   *---------------------------*   *-------------------*   |
        # |   |                           |   |                   |   |
        # |   |                           |   |                   |   |
        # |   |                           |   |                   |   |
        # |   |                           |   |                   |   |
        # |   |                           |   |                   |   |
        # |   *---------------------------*   |                   |   |
        # |                                   |                   |   |
        # 2   *---------------------------*   |                   |   |
        # |   |    [<-]  [->]   [save]    |   |                   |   |
        # |   *---------------------------*   *-------------------*   |
        # |                                                           |
        # *-----------------------------------------------------------*

        self.frame_themes.grid(row=0, column=0, columnspan=2, padx=6, pady=(6, 0), sticky='W')
        # {
        self.lbl_set_theme.grid(   row=0, column=0, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_set_theme.grid( row=0, column=1, padx=(0, 3), pady=(0, 6))
        self.btn_set_theme.grid(   row=0, column=2, padx=(0, 0), pady=(0, 6), sticky='W')
        self.lbl_set_images.grid(  row=1, column=0, padx=(0, 1), pady=0,      sticky='E')
        self.combo_set_images.grid(row=1, column=1, padx=(0, 3), pady=0)
        self.btn_set_images.grid(  row=1, column=2, padx=(0, 0), pady=0,      sticky='W')
        # }
        self.scrolled_frame.grid(row=1, column=0, padx=6, pady=6)
        # {
        self.lbl_relief_frame.grid(  row=9,  column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_frame.grid(row=9,  column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_relief_text.grid(   row=10, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_text.grid( row=10, column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        # }
        self.frame_buttons.grid(row=2, column=0, padx=6, pady=(0, 6))
        # {
        self.btn_save.grid(     row=0, column=0, padx=(0, 36), pady=0)
        self.frame_history.grid(row=0, column=1, padx=0,       pady=0)
        # { {
        self.btn_undo.grid(row=0, column=0, padx=(0, 6), pady=0, sticky='W')
        self.btn_redo.grid(row=0, column=1, padx=0,      pady=0, sticky='W')
        # } }
        # }
        self.frame_demonstration.grid(row=1, rowspan=2, column=1, padx=6, pady=6)
        # {
        self.lbl_demo_header.grid( row=0, column=0, columnspan=3, padx=12, pady=(12, 0))
        self.lbl_demo_logo.grid(   row=1, column=0, columnspan=3, padx=12, pady=(0, 12))
        self.frame_demo_check.grid(row=2, column=0,               padx=6,  pady=(0, 6), sticky='E')
        # { {
        self.lbl_demo_def.grid(row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_demo.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        # } }
        self.entry_demo.grid(    row=2,            column=1, columnspan=2, padx=(0, 6), pady=(0, 6), sticky='SW')
        self.btn_demo_def.grid(  row=3,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_dis.grid(  row=4,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_y.grid(    row=5,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.btn_demo_n.grid(    row=6,            column=0,               padx=6,      pady=(0, 6), sticky='E')
        self.txt_demo.grid(      row=3, rowspan=4, column=1,               padx=0,      pady=(0, 6), sticky='SNWE')
        self.scroll_demo.grid(   row=3, rowspan=4, column=2,               padx=(0, 6), pady=(0, 6), sticky='SNW')
        self.frame_demo_img.grid(row=7,            column=0, columnspan=3, padx=6,      pady=(0, 6))
        # { {
        for i in range(len(ICON_NAMES)):
            self.img_buttons[i].grid(row=i // 7, column=i % 7, padx=3, pady=3)
        # } }
        self.lbl_demo_warn.grid(  row=8, column=0, columnspan=3, padx=6, pady=(0, 6))
        self.lbl_demo_footer.grid(row=9, column=0, columnspan=3, padx=6, pady=(0, 6))
        # }

        self.tip_btn_undo = ttip.Hovertip(self.btn_undo, 'Отменить последнее действие', hover_delay=450)
        self.tip_btn_redo = ttip.Hovertip(self.btn_redo, 'Вернуть отменённое действие', hover_delay=450)

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
            images = [img_about_mgsp, img_about_typo, img_about, img_ok, img_cancel,
                      img_add, img_delete, img_edit, img_print_out, img_undo, img_redo,
                      img_arrow_left, img_arrow_right, img_double_arrow_left, img_double_arrow_right]
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
                                      font=('StdFont', _0_global_scale),
                                      background=self.custom_styles['BG'],
                                      foreground=self.custom_styles['FG'])

        # Стиль label "demo header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('DemoHeader.TLabel',
                                     font=('StdFont', _0_global_scale + 5),
                                     background=self.custom_styles['BG'],
                                     foreground=self.custom_styles['FG'])

        # Стиль label "demo logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('DemoLogo.TLabel',
                                   font=('StdFont', _0_global_scale + 11),
                                   background=self.custom_styles['BG'],
                                   foreground=self.custom_styles['FG_LOGO'])

        # Стиль label "demo footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('DemoFooter.TLabel',
                                     font=('StdFont', _0_global_scale - 2),
                                     background=self.custom_styles['BG'],
                                     foreground=self.custom_styles['FG_FOOTER'])

        # Стиль label "demo warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('DemoWarn.TLabel',
                                   font=('StdFont', _0_global_scale),
                                   background=self.custom_styles['BG'],
                                   foreground=self.custom_styles['FG_WARN'])

        # Стиль entry "demo"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('DemoDefault.TEntry',
                                font=('StdFont', _0_global_scale))
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
                                      font=('StdFont', _0_global_scale + 2),
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
                                       font=('StdFont', _0_global_scale + 2),
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
                                  font=('StdFont', _0_global_scale + 2),
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
                                 font=('StdFont', _0_global_scale + 2),
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
                                    font=('StdFont', _0_global_scale + 2),
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


""" Графический интерфейс - основные окна """


# Окно изучения слов
class LearnW(tk.Toplevel):
    def __init__(self, parent, parameters: tuple[str, str, str, str]):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Учёба')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.current_key = None  # Текущее слово
        self.current_form = None  # Текущая форма (если начальная, то None)
        self.homonyms = []  # Омонимы к текущему слову
        self.count_all = 0  # Счётчик всех ответов
        self.count_correct = 0  # Счётчик верных ответов
        self.learn_method = parameters[0]  # Метод изучения слов
        self.with_forms = parameters[1]  # Со всеми ли словоформами
        self.words = parameters[2]  # Способ подбора слов
        self.order = parameters[3]  # Порядок следования слов
        self.pool = set()  # Набор слов для изучения

        self.create_pool()  # Формируем пул слов, которые будут использоваться при учёбе

        self.len_of_pool = len(self.pool)  # Количество изучаемых слов

        self.var_input = tk.StringVar()

        self.lbl_global_rating = ttk.Label(self, text=f'Ваш общий рейтинг по словарю: {self.get_percent()}%',
                                           style='Default.TLabel')
        self.lbl_count = ttk.Label(self, text=f'Отвечено: 0/{self.len_of_pool}', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_dct = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set,
                               font=('StdFont', _0_global_scale), bg=ST_BG_FIELDS[th], fg=ST_FG[th],
                               selectbackground=ST_SELECT_BG[th], selectforeground=ST_SELECT_FG[th],
                               relief=ST_RELIEF_TEXT[th], highlightbackground=ST_BORDERCOLOR[th])
        self.scrollbar.config(command=self.txt_dct.yview)
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_input = ttk.Button(self.frame_main, text='Ввод', command=self.input, width=6,
                                    takefocus=False, style='Default.TButton')
        self.entry_input = ttk.Entry(self.frame_main, textvariable=self.var_input, width=36,
                                     style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_show_notes = ttk.Button(self.frame_main, text='Сноски', command=self.show_notes, width=7,
                                         takefocus=False, style='Default.TButton')
        self.btn_show_homonyms = ttk.Button(self.frame_main, text='Омонимы', command=self.show_homonyms, width=8,
                                            takefocus=False, style='Default.TButton')
        # }
        self.btn_stop = ttk.Button(self, text='Закончить', command=self.stop, takefocus=False, style='No.TButton')

        self.lbl_global_rating.grid(row=0, columnspan=2, padx=6,      pady=(6, 3))
        self.lbl_count.grid(        row=1, columnspan=2, padx=6,      pady=(0, 6))
        self.txt_dct.grid(          row=2, column=0,     padx=(6, 0), pady=6, sticky='NSWE')
        self.scrollbar.grid(        row=2, column=1,     padx=(0, 6), pady=6, sticky='NSW')
        self.frame_main.grid(       row=3, columnspan=2, padx=6,      pady=6)
        # {
        self.btn_input.grid(        row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input.grid(      row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        self.btn_show_notes.grid(   row=0, column=2, padx=(0, 3), pady=0, sticky='W')
        self.btn_show_homonyms.grid(row=0, column=3, padx=0,      pady=0, sticky='W')
        # }
        self.btn_stop.grid(row=4, columnspan=2, padx=6, pady=6)

        self.tip_btn_show_notes = ttip.Hovertip(self.btn_show_notes, 'Посмотреть сноски\n'
                                                                     'Control-N',
                                                hover_delay=700)
        self.tip_btn_show_homonyms = ttip.Hovertip(self.btn_show_homonyms,
                                                   'Посмотреть остальные слова с таким же написанием\n'
                                                   'Control-O',
                                                   hover_delay=700)
        if self.learn_method == LEARN_VALUES_METHOD[0]:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите слово', hover_delay=1000)
        elif self.learn_method == LEARN_VALUES_METHOD[1]:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        else:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите артикль', hover_delay=1000)

        self.choose()

        if self.current_key:
            entry = _0_global_dct.d[self.current_key]
            if entry.count_n == 0:
                btn_disable(self.btn_show_notes)
            if not self.homonyms:
                btn_disable(self.btn_show_homonyms)

    # Формируем пул слов, которые будут использоваться при учёбе
    def create_pool(self):
        if self.learn_method == LEARN_VALUES_METHOD[2]:
            all_keys = []
            for key in _0_global_dct.d.keys():
                wrd = _0_global_dct.d[key].wrd
                if len(wrd) > 4 and wrd[0:4].lower() in ('der ', 'die ', 'das '):
                    all_keys += [key]
        else:
            all_keys = tuple(_0_global_dct.d.keys())
        if self.with_forms == LEARN_VALUES_FORMS[2]:
            all_keys = tuple(key for key in all_keys if len(_0_global_dct.d[key].forms) != 0)

        if self.words == LEARN_VALUES_WORDS[0]:  # Учить все слова
            selected_keys = all_keys
        elif self.words == LEARN_VALUES_WORDS[1]:  # Учить преимущественно избранные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].fav]

            # Помимо всех избранных слов (пусть их количество N) добавим N // 4 остальных слов
            # Выберем их из самых давно не отвечаемых слов

            # Отбираем слова, не являющиеся избранными
            unfav_keys = list(k for k in all_keys if not _0_global_dct.d[k].fav)
            # Сортируем по давности ответа
            unfav_keys = sorted(unfav_keys, key=lambda k: _0_global_dct.d[k].latest_answer_session)
            # Находим N // 4
            count_unfav_keys = min(len(unfav_keys), _0_global_dct.count_fav_info()[0] // 4)
            # Находим S - номер самой недавней сессии среди N // 4 самых старых слов
            latest_session = _0_global_dct.d[unfav_keys[count_unfav_keys - 1]].latest_answer_session
            # Оставляем только слова с номером сессии <= S
            unfav_keys = list(k for k in unfav_keys
                              if _0_global_dct.d[k].latest_answer_session[0:2] <= latest_session[0:2])
            # Перемешиваем их
            random.shuffle(unfav_keys)
            # И выбираем из них N // 4 слов
            for i in range(count_unfav_keys):
                selected_keys += [unfav_keys[i]]
        elif self.words == LEARN_VALUES_WORDS[2]:  # Учить только избранные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].fav]
        elif self.words == LEARN_VALUES_WORDS[3]:  # Учить только неотвеченные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].correct_att == 0]
        elif self.words == LEARN_VALUES_WORDS[4]:  # Учить 15 случайных слов
            selected_keys = random.sample(all_keys, min(len(all_keys), 15))
        else:  # Учить 15 случайных избранных слов
            all_keys = tuple(key for key in all_keys if _0_global_dct.d[key].fav)
            selected_keys = random.sample(all_keys, min(len(all_keys), 15))

        selected_forms = []
        if self.with_forms == LEARN_VALUES_FORMS[0]:
            for key in selected_keys:
                selected_forms += [(key, None)]
        elif self.with_forms == LEARN_VALUES_FORMS[1]:
            for key in selected_keys:
                forms = tuple([None]) + tuple(_0_global_dct.d[key].forms.keys())
                selected_forms += [(key, random.choice(forms))]
        elif self.with_forms == LEARN_VALUES_FORMS[2]:
            for key in selected_keys:
                for frm in _0_global_dct.d[key].forms.keys():
                    selected_forms += [(key, frm)]
        else:
            for key in selected_keys:
                selected_forms += [(key, None)]
                for frm in _0_global_dct.d[key].forms.keys():
                    selected_forms += [(key, frm)]

        self.pool = set(selected_forms)

    # Печать в журнал
    def outp(self, msg='', end='\n'):
        self.txt_dct['state'] = 'normal'
        self.txt_dct.insert(tk.END, f'{msg}{end}')
        self.txt_dct.yview_moveto(1.0)
        self.txt_dct['state'] = 'disabled'

    # Нажатие на кнопку "Ввод"
    # Ввод ответа и переход к следующему слову
    def input(self):
        # Вывод в журнал пользовательского ответа
        answer = encode_special_combinations(self.entry_input.get())
        if answer != '':
            self.outp(answer)

        # Проверка пользовательского ответа
        if self.learn_method == LEARN_VALUES_METHOD[1]:
            self.check_tr()
        elif self.learn_method == LEARN_VALUES_METHOD[2]:
            self.check_article()
        elif self.with_forms and self.current_form:
            self.check_form()
        else:
            self.check_wrd()

        # Выбор нового слова для угадывания
        self.choose()

        # Обновление кнопки "Посмотреть сноски"
        entry = _0_global_dct.d[self.current_key]
        if entry.count_n == 0:
            btn_disable(self.btn_show_notes)
        else:
            btn_enable(self.btn_show_notes, self.show_notes)
        # Обновление кнопки "Посмотреть омонимы"
        if not self.homonyms:
            btn_disable(self.btn_show_homonyms)
        else:
            btn_enable(self.btn_show_homonyms, self.show_homonyms)
        # Очистка поля ввода
        self.entry_input.delete(0, tk.END)
        # Обновление отображаемого рейтинга
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {self.get_percent()}%'
        self.lbl_count['text'] = f'Отвечено: {self.count_correct}/{self.len_of_pool}'

    # Нажатие на кнопку "Посмотреть сноски"
    # Просмотр сносок
    def show_notes(self):
        self.outp('Сноски:')
        entry = _0_global_dct.d[self.current_key]
        self.outp(get_notes(entry))
        btn_disable(self.btn_show_notes)

    # Нажатие на кнопку "Посмотреть омонимы"
    # Просмотр омонимов
    def show_homonyms(self):
        if self.learn_method == LEARN_VALUES_METHOD[0]:
            self.outp('Омонимы: ' + ', '.join([_0_global_dct.d[key].wrd for key in self.homonyms]))
        else:
            self.outp('Омонимы:')
            for key in self.homonyms:
                self.outp('> ' + get_tr(_0_global_dct.d[key]))
        btn_disable(self.btn_show_homonyms)

    # Нажатие на кнопку "Закончить"
    # Завершение учёбы
    def stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()
        btn_disable(self.btn_input)
        btn_disable(self.btn_show_notes)
        btn_disable(self.btn_show_homonyms)

        PopupMsgW(self, f'Ваш результат: {self.count_correct}/{self.count_all}')
        self.outp(f'\nВаш результат: {self.count_correct}/{self.count_all}', end='')

    # Проверка введённого ответа
    def check_answer(self, correct_answer: str, is_correct: bool,
                     current_key: tuple[str, int], current_form: tuple[str, ...] | None = None):
        entry = _0_global_dct.d[current_key]
        if is_correct:
            entry.correct((_0_global_session_number, _0_global_learn_session_number, self.count_all))
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
            self.pool.remove((current_key, current_form))
        else:
            self.outp(f'Неверно. Правильный ответ: "{correct_answer}"\n')
            if entry.fav:
                if bool(_0_global_with_typo):
                    window = PopupDialogueW(self,
                                            msg=f'Неверно.\n'
                                                f'Ваш ответ: {encode_special_combinations(self.entry_input.get())}\n'
                                                f'Правильный ответ: {correct_answer}',
                                            btn_left_text='Ясно', btn_right_text='Просто опечатка',
                                            st_left='Default', st_right='Default',
                                            val_left='ok', val_right='typo')
                    ttip.Hovertip(window.btn_right, 'Не засчитывать ошибку\n'
                                                    'Tab',
                                  hover_delay=700)
                    window.bind('<Tab>', lambda event=None: window.btn_right.invoke())
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
            is_correct = encode_special_combinations(self.entry_input.get()).lower() in (tr.lower() for tr in entry.tr)
        self.check_answer(frm_key_to_str_for_print(entry.tr), is_correct, self.current_key)

    # Проверка введённого артикля
    def check_article(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get()) == entry.wrd[0:3]
        else:
            is_correct = encode_special_combinations(self.entry_input.get()).lower() == entry.wrd[0:3].lower()
        self.check_answer(entry.wrd[0:3], is_correct, self.current_key)

    # Выбор слова для угадывания
    def choose(self):
        global _0_global_has_progress

        if len(self.pool) == 0:
            # Если все слова отвечены, то завершаем учёбу
            self.stop()
            return
        else:
            _0_global_has_progress = True

        # Выбор слова
        if self.order == LEARN_VALUES_ORDER[0]:
            self.current_key, self.current_form = random.choice(tuple(self.pool))
        else:
            self.current_key, self.current_form = random_smart(_0_global_dct, self.pool, _0_global_min_good_score_perc)

        # Вывод слова в журнал
        if self.learn_method == LEARN_VALUES_METHOD[0]:
            if self.with_forms and self.current_form:
                self.outp(get_tr_and_frm_with_stat(_0_global_dct.d[self.current_key], self.current_form))
            else:
                self.outp(get_tr_with_stat(_0_global_dct.d[self.current_key]))
        elif self.learn_method == LEARN_VALUES_METHOD[1]:
            self.outp(get_wrd_with_stat(_0_global_dct.d[self.current_key]))
        else:
            self.outp(get_wrd_with_stat(_0_global_dct.d[self.current_key])[4:])

        # Запись омонимов
        if self.learn_method == LEARN_VALUES_METHOD[0]:
            ans = _0_global_dct.d[self.current_key].tr
            self.homonyms = []
            for key in _0_global_dct.d.keys():
                if key != self.current_key:
                    for tr in _0_global_dct.d[key].tr:
                        if tr in ans:
                            self.homonyms += [key]
                            break
        elif self.learn_method == LEARN_VALUES_METHOD[1]:
            ans = _0_global_dct.d[self.current_key].wrd
            self.homonyms = [key for key in _0_global_dct.d.keys()
                             if _0_global_dct.d[key].wrd == ans and key != self.current_key]
        elif self.learn_method == LEARN_VALUES_METHOD[2]:
            ans = _0_global_dct.d[self.current_key].wrd
            self.homonyms = []
            for key in _0_global_dct.d.keys():
                if key != self.current_key:
                    wrd = _0_global_dct.d[key].wrd
                    if len(wrd) > 4 and wrd[0:4].lower() in ('der ', 'die ', 'das ') and wrd[4:] == ans[4:]:
                        self.homonyms += [key]

    # Получить глобальный процент угадываний
    def get_percent(self):
        return format(_0_global_dct.count_rating() * 100, '.1f')

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_input.invoke())
        self.bind('<Control-N>', lambda event=None: self.btn_show_notes.invoke())
        self.bind('<Control-n>', lambda event=None: self.btn_show_notes.invoke())
        self.bind('<Control-O>', lambda event=None: self.btn_show_homonyms.invoke())
        self.bind('<Control-o>', lambda event=None: self.btn_show_homonyms.invoke())

    def open(self):
        global _0_global_learn_session_number

        self.set_focus()

        self.grab_set()
        self.wait_window()

        _0_global_learn_session_number += 1


# Окно просмотра словаря
class PrintW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Просмотр словаря')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.max_elements_on_page = 200  # Максимальное количество элементов на одной странице ScrollFrame
        self.current_page = 1  # Номер текущей страницы ScrollFrame (начиная с 1)
        self.start_index = 0  # Номер по порядку первого слова на текущей странице ScrollFrame (начиная с 0)
        self.count_pages = None  # Количество страниц ScrollFrame
        self.count_elements = None  # Количество элементов на всех страницах ScrollFrame
        self.count_elements_on_page = None  # Количество элементов на текущей странице ScrollFrame

        self.var_fav = tk.BooleanVar(value=False)
        self.var_forms = tk.BooleanVar(value=True)
        self.var_info = tk.StringVar()
        self.var_current_page = tk.StringVar(value=str(self.current_page))
        self.var_order = tk.StringVar(value=PRINT_VALUES_ORDER[0])

        self.img_about = tk.PhotoImage()
        self.img_arrow_left = tk.PhotoImage()
        self.img_arrow_right = tk.PhotoImage()
        self.img_double_arrow_left = tk.PhotoImage()
        self.img_double_arrow_right = tk.PhotoImage()
        self.img_print_out = tk.PhotoImage()

        self.keys = []
        self.frames = []
        self.buttons = []
        self.tips = []

        def validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.count_pages)
            if res and value != '' and int(value) != self.current_page:
                self.go_to_page_with_number(int(value))
            return res
        self.vcmd_page = (self.register(validate_and_goto_page_number), '%P')

        self.frame_header = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_about_window = ttk.Button(self.frame_header, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.btn_print_out = ttk.Button(self.frame_header, command=self.print_out, takefocus=False)
        set_image(self.btn_print_out, self.img_print_out, img_print_out, 'Распечатать')
        self.lbl_dct_name = ttk.Label(self.frame_header, text=split_text(f'Открыт словарь "{_0_global_dct_savename}"',
                                                                         40, add_right_spaces=False),
                                      justify='center', style='Default.TLabel')
        # }
        self.frame_parameters = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_fav = ttk.Label(self.frame_parameters, text='Только избранные:', style='Default.TLabel')
        self.check_fav = ttk.Checkbutton(self.frame_parameters, variable=self.var_fav,
                                         command=self.go_to_first_page, style='Default.TCheckbutton')
        self.lbl_forms = ttk.Label(self.frame_parameters, text='Все словоформы:', style='Default.TLabel')
        self.check_forms = ttk.Checkbutton(self.frame_parameters, variable=self.var_forms,
                                           command=self.go_to_first_page, style='Default.TCheckbutton')
        self.lbl_order = ttk.Label(self.frame_parameters, text='Порядок:', style='Default.TLabel')
        self.combo_order = ttk.Combobox(self.frame_parameters, textvariable=self.var_order, values=PRINT_VALUES_ORDER,
                                        width=26, state='readonly', style='Default.TCombobox',
                                        font=('DejaVu Sans Mono', _0_global_scale))
        # }
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_info = ttk.Label(self.frame_main, textvariable=self.var_info, style='Default.TLabel')
        self.scrolled_frame = ScrollFrame(self.frame_main, SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                          SCALE_DEFAULT_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.frame_page_buttons = ttk.Frame(self.frame_main, style='Invis.TFrame')
        # { {
        self.btn_first_page = ttk.Button(self.frame_page_buttons, command=self.go_to_first_page, width=2,
                                         takefocus=False)
        set_image(self.btn_first_page, self.img_double_arrow_left, img_double_arrow_left, '<<')
        self.btn_prev_page = ttk.Button(self.frame_page_buttons, command=self.go_to_prev_page, width=2, takefocus=False)
        set_image(self.btn_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self.frame_current_page = ttk.Frame(self.frame_page_buttons, style='Invis.TFrame')
        # { { {
        self.lbl_current_page_1 = ttk.Label(self.frame_current_page, text='Страница', style='Default.TLabel')
        self.entry_current_page = ttk.Entry(self.frame_current_page, textvariable=self.var_current_page,
                                            validate='key', validatecommand=self.vcmd_page, justify='center', width=3,
                                            style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_current_page_2 = ttk.Label(self.frame_current_page, text='из 1', style='Default.TLabel')
        # } } }
        self.btn_next_page = ttk.Button(self.frame_page_buttons, command=self.go_to_next_page, width=2, takefocus=False)
        set_image(self.btn_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_last_page = ttk.Button(self.frame_page_buttons, command=self.go_to_last_page, width=2, takefocus=False)
        set_image(self.btn_last_page, self.img_double_arrow_right, img_double_arrow_right, '>>')
        # } }
        # }
        self.frame_fav_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_fav_all = ttk.Button(self.frame_fav_buttons, text='Добавить всё в избранное', command=self.fav_all,
                                      takefocus=False, style='Default.TButton')
        self.btn_unfav_all = ttk.Button(self.frame_fav_buttons, text='Убрать всё из избранного', command=self.unfav_all,
                                        takefocus=False, style='Default.TButton')
        # }

        self.frame_header.grid(row=0, column=0, padx=6, pady=6)
        # {
        self.btn_about_window.grid(row=0, column=0, padx=0, pady=0)
        self.btn_print_out.grid(   row=0, column=1, padx=0, pady=0)
        self.lbl_dct_name.grid(    row=0, column=2, padx=0, pady=0)
        # }
        self.frame_parameters.grid(row=1, column=0, padx=6, pady=0)
        # {
        self.lbl_fav.grid(    row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_fav.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_forms.grid(  row=0, column=2, padx=(6, 1), pady=6, sticky='E')
        self.check_forms.grid(row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        self.lbl_order.grid(  row=0, column=4, padx=(6, 1), pady=6, sticky='E')
        self.combo_order.grid(row=0, column=5, padx=(0, 6), pady=6, sticky='W')
        # }
        self.frame_main.grid(row=2, column=0, padx=6, pady=6)
        # {
        self.lbl_info.grid(          row=0, column=0, padx=0, pady=(0, 6))
        self.scrolled_frame.grid(    row=1, column=0, padx=0, pady=(0, 6))
        self.frame_page_buttons.grid(row=2, column=0, padx=0, pady=0)
        # { {
        self.btn_first_page.grid(    row=0, column=0, padx=3, pady=0)
        self.btn_prev_page.grid(     row=0, column=1, padx=3, pady=0)
        self.frame_current_page.grid(row=0, column=2, padx=3, pady=0)
        # { { {
        self.lbl_current_page_1.grid(row=0, column=0, padx=0, pady=0)
        self.entry_current_page.grid(row=0, column=1, padx=3, pady=0)
        self.lbl_current_page_2.grid(row=0, column=2, padx=0, pady=0)
        # } } }
        self.btn_next_page.grid(row=0, column=3, padx=3, pady=0)
        self.btn_last_page.grid(row=0, column=4, padx=3, pady=0)
        # } }
        # }
        self.frame_fav_buttons.grid(row=3, column=0, padx=6, pady=(0, 6))
        # {
        self.btn_fav_all.grid(  row=0, column=0, padx=(0, 6), pady=0)
        self.btn_unfav_all.grid(row=0, column=1, padx=(0, 6), pady=0)
        # }

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)
        self.tip_btn_print_out = ttip.Hovertip(self.btn_print_out, 'Распечатать словарь в файл', hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(self.btn_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(self.btn_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(self.btn_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(self.btn_last_page, 'В конец', hover_delay=650)

        self.combo_order.bind('<<ComboboxSelected>>', lambda event: self.print(False))

        self.bind('<Up>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-U>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-u>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))

        self.bind('<Down>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-D>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-d>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))

        self.print(True)  # Выводим статьи

    # Изменить статью
    def edit_entry(self, index: int):
        EditW(self, self.keys[index]).open()

        self.print(False)

    # Напечатать словарь
    def print(self, move_scroll: bool):
        # Удаляем старые подсказки
        for tip in self.tips:
            tip.__del__()
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-F>')
            fr.unbind('<Control-f>')
            fr.destroy()

        # Выбираем нужные статьи и выводим информацию о количестве статей
        if self.var_fav.get():
            self.keys = [key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].fav]

            w, t, f = _0_global_dct.count_fav_info()
            self.var_info.set(dct_info_fav(_0_global_dct, w, t, f))
        else:
            self.keys = [key for key in _0_global_dct.d.keys()]

            self.var_info.set(dct_info(_0_global_dct))
        #
        if self.var_order.get() == PRINT_VALUES_ORDER[1]:
            self.keys.reverse()
        elif self.var_order.get() == PRINT_VALUES_ORDER[2]:
            self.keys = sorted(self.keys, key=lambda k: _0_global_dct.d[k].score)
        elif self.var_order.get() == PRINT_VALUES_ORDER[3]:
            self.keys = sorted(self.keys, key=lambda k: _0_global_dct.d[k].score, reverse=True)
        elif self.var_order.get() == PRINT_VALUES_ORDER[4]:
            self.keys = sorted(self.keys, key=lambda k: _0_global_dct.d[k].latest_answer_session)
        elif self.var_order.get() == PRINT_VALUES_ORDER[5]:
            self.keys = sorted(self.keys, key=lambda k: _0_global_dct.d[k].latest_answer_session, reverse=True)

        # Вычисляем значения некоторых количественных переменных
        self.count_elements = len(self.keys)
        if self.count_elements == 0:
            self.count_pages = 1
        else:
            self.count_pages = math.ceil(self.count_elements / self.max_elements_on_page)
        if self.current_page > self.count_pages:
            self.current_page = self.count_pages
            self.start_index = (self.count_pages - 1) * self.max_elements_on_page
        if self.current_page == self.count_pages:
            if self.count_elements % self.max_elements_on_page == 0 and self.count_elements != 0:
                self.count_elements_on_page = self.max_elements_on_page
            else:
                self.count_elements_on_page = self.count_elements % self.max_elements_on_page
        else:
            self.count_elements_on_page = self.max_elements_on_page
        # Выводим номер страницы
        self.var_current_page.set(str(self.current_page))
        self.entry_current_page.icursor(len(str(self.current_page)))
        self.lbl_current_page_2.configure(text=f'из {self.count_pages}')

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(self.count_elements_on_page)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i], command=lambda i=i: self.edit_entry(self.start_index + i),
                                   takefocus=False, style='Note.TButton')
                        for i in range(self.count_elements_on_page)]
        # Выводим текст на кнопки
        if self.var_forms.get():
            for i in range(self.count_elements_on_page):
                key = self.keys[self.start_index + i]
                self.buttons[i].configure(text=get_entry_info_briefly_with_forms(_0_global_dct.d[key], 75))
        else:
            for i in range(self.count_elements_on_page):
                key = self.keys[self.start_index + i]
                self.buttons[i].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))
        # Расставляем элементы
        for i in range(self.count_elements_on_page):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Создаём подсказки
        self.tips = [ttip.Hovertip(self.buttons[i],
                                   f'Верных ответов подряд: '
                                   f'{get_correct_att_in_a_row(_0_global_dct.d[self.keys[self.start_index + i]])}\n'
                                   f'Доля верных ответов: '
                                   f'{get_entry_percent(_0_global_dct.d[self.keys[self.start_index + i]])}',
                                   hover_delay=666)
                     for i in range(self.count_elements_on_page)]
        # Привязываем события
        for i in range(self.count_elements_on_page):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Control-F>', lambda event, i=i: self.fav_one(i))
            self.frames[i].bind('<Control-f>', lambda event, i=i: self.fav_one(i))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Обновить одну из кнопок журнала
    def refresh_one_button(self, index: int):
        # Выводим текст на кнопку
        if self.var_forms.get():
            key = self.keys[self.start_index + index]
            self.buttons[index].configure(text=get_entry_info_briefly_with_forms(_0_global_dct.d[key], 75))
        else:
            key = self.keys[self.start_index + index]
            self.buttons[index].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))

        # Выводим информацию о количестве статей
        if self.var_fav.get():
            w, t, f = _0_global_dct.count_fav_info()
            self.var_info.set(dct_info_fav(_0_global_dct, w, t, f))
        else:
            self.var_info.set(dct_info(_0_global_dct))

    # Обновить все кнопки журнала
    def refresh_all_buttons(self):
        # Выводим текст на кнопки
        if self.var_forms.get():
            for i in range(self.count_elements_on_page):
                key = self.keys[self.start_index + i]
                self.buttons[i].configure(text=get_entry_info_briefly_with_forms(_0_global_dct.d[key], 75))
        else:
            for i in range(self.count_elements_on_page):
                key = self.keys[self.start_index + i]
                self.buttons[i].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))

    # Перейти на страницу с заданным номером
    def go_to_page_with_number(self, number: int):
        self.current_page = number
        self.start_index = (self.current_page - 1) * self.max_elements_on_page
        self.print(True)

    # Перейти на предыдущую страницу
    def go_to_prev_page(self):
        if self.current_page != 1:
            self.go_to_page_with_number(self.current_page - 1)

    # Перейти на следующую страницу
    def go_to_next_page(self):
        if self.current_page != self.count_pages:
            self.go_to_page_with_number(self.current_page + 1)

    # Перейти на первую страницу
    def go_to_first_page(self):
        self.go_to_page_with_number(1)

    # Перейти на последнюю страницу
    def go_to_last_page(self):
        self.go_to_page_with_number(self.count_pages)

    # Добавить одну статью в избранное (или убрать)
    def fav_one(self, index: int):
        _0_global_dct.d[self.keys[self.start_index + index]].change_fav()

        self.refresh_one_button(index)

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

        self.refresh_all_buttons()

    # Нажатие на кнопку "Распечатать словарь в файл"
    def print_out(self):
        folder = askdirectory(initialdir=MAIN_PATH, title='В какую папку сохранить файл?')
        if not folder:
            return
        filename = f'Распечатка_{_0_global_dct_savename}.txt'
        _0_global_dct.print_out(os.path.join(folder, filename))

    # Нажатие на кнопку "Справка" (картинка с вопросом)
    def about_window(self):
        PopupMsgW(self, '* Чтобы добавить статью в избранное, наведите на неё мышку и нажмите Ctrl+F\n'
                        '* Чтобы прокрутить в самый низ, нажмите Ctrl+D или DOWN\n'
                        '* Чтобы прокрутить в самый верх, нажмите Ctrl+U или UP',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно поиска статей
class SearchW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Поиск')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.search_only_fav = bool(_0_global_search_settings[0])
        self.search_only_full = bool(_0_global_search_settings[1])
        self.search_wrd = bool(_0_global_search_settings[2])
        self.search_tr = bool(_0_global_search_settings[3])
        self.search_frm = bool(_0_global_search_settings[4])
        self.search_nt = bool(_0_global_search_settings[5])

        self.max_elements_on_page = 100  # Максимальное количество элементов на одной странице ScrollFrame
        self.current_page = 1  # Номер текущей страницы ScrollFrame (начиная с 1)
        self.start_index = 0  # Номер по порядку первого слова на текущей странице ScrollFrame (начиная с 0)
        self.count_pages = None  # Количество страниц ScrollFrame
        self.count_elements = None  # Количество элементов на всех страницах ScrollFrame
        self.count_elements_on_page = None  # Количество элементов на текущей странице ScrollFrame

        self.var_query = tk.StringVar()
        self.var_info = tk.StringVar()
        self.var_current_page = tk.StringVar(value=str(self.current_page))

        self.img_about = tk.PhotoImage()
        self.img_settings = tk.PhotoImage()
        self.img_arrow_left = tk.PhotoImage()
        self.img_arrow_right = tk.PhotoImage()
        self.img_double_arrow_left = tk.PhotoImage()
        self.img_double_arrow_right = tk.PhotoImage()

        self.keys = []
        self.frames = []
        self.buttons = []

        def validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.count_pages)
            if res and value != '' and int(value) != self.current_page:
                self.go_to_page_with_number(int(value))
            return res
        self.vcmd_page = (self.register(validate_and_goto_page_number), '%P')

        self.frame_header = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_about_window = ttk.Button(self.frame_header, command=self.about_window, width=2, takefocus=False)
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_dct_name = ttk.Label(self.frame_header, text=split_text(f'Открыт словарь "{_0_global_dct_savename}"',
                                                                         40, add_right_spaces=False),
                                      justify='center', style='Default.TLabel')
        self.frame_query = ttk.Frame(self.frame_header, style='Default.TFrame')
        # { {
        self.btn_search_settings = ttk.Button(self.frame_query, command=self.search_settings, width=9, takefocus=False)
        set_image(self.btn_search_settings, self.img_settings, img_edit, 'Настройки')
        self.entry_query = ttk.Entry(self.frame_query, textvariable=self.var_query, width=50,
                                     style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_search = ttk.Button(self.frame_query, text='Поиск', command=lambda: self.print(True),
                                     width=6, takefocus=False, style='Default.TButton')
        # } }
        # }
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_info = ttk.Label(self.frame_main, textvariable=self.var_info, style='Default.TLabel')
        self.scrolled_frame = ScrollFrame(self.frame_main, SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                          SCALE_DEFAULT_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.frame_page_buttons = ttk.Frame(self.frame_main, style='Invis.TFrame')
        # { {
        self.btn_first_page = ttk.Button(self.frame_page_buttons, command=self.go_to_first_page, width=2,
                                         takefocus=False)
        set_image(self.btn_first_page, self.img_double_arrow_left, img_double_arrow_left, '<<')
        self.btn_prev_page = ttk.Button(self.frame_page_buttons, command=self.go_to_prev_page, width=2, takefocus=False)
        set_image(self.btn_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self.frame_current_page = ttk.Frame(self.frame_page_buttons, style='Invis.TFrame')
        # { { {
        self.lbl_current_page_1 = ttk.Label(self.frame_current_page, text='Страница', style='Default.TLabel')
        self.entry_current_page = ttk.Entry(self.frame_current_page, textvariable=self.var_current_page,
                                            validate='key', validatecommand=self.vcmd_page, justify='center', width=3,
                                            style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_current_page_2 = ttk.Label(self.frame_current_page, text='из 1', style='Default.TLabel')
        # } } }
        self.btn_next_page = ttk.Button(self.frame_page_buttons, command=self.go_to_next_page, width=2, takefocus=False)
        set_image(self.btn_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_last_page = ttk.Button(self.frame_page_buttons, command=self.go_to_last_page, width=2, takefocus=False)
        set_image(self.btn_last_page, self.img_double_arrow_right, img_double_arrow_right, '>>')
        # } }
        # }

        self.frame_header.grid(row=0, column=0, padx=6, pady=(6, 0))
        # {
        self.btn_about_window.grid(row=0, column=0, padx=0,      pady=0)
        self.lbl_dct_name.grid(    row=0, column=1, padx=0,      pady=0)
        self.frame_query.grid(     row=0, column=2, padx=(6, 0), pady=0)
        # { {
        self.btn_search_settings.grid(row=0, column=0, padx=(6, 1), pady=6)
        self.entry_query.grid(        row=0, column=1, padx=(0, 1), pady=6)
        self.btn_search.grid(         row=0, column=2, padx=(0, 6), pady=6)
        # } }
        # }
        self.frame_main.grid(row=1, column=0, padx=6, pady=6)
        # {
        self.lbl_info.grid(          row=0, column=0, padx=0, pady=(0, 6))
        self.scrolled_frame.grid(    row=1, column=0, padx=0, pady=(0, 6))
        self.frame_page_buttons.grid(row=2, column=0, padx=0, pady=0)
        # { {
        self.btn_first_page.grid(    row=0, column=0, padx=3, pady=0)
        self.btn_prev_page.grid(     row=0, column=1, padx=3, pady=0)
        self.frame_current_page.grid(row=0, column=2, padx=3, pady=0)
        # { { {
        self.lbl_current_page_1.grid(row=0, column=0, padx=0, pady=0)
        self.entry_current_page.grid(row=0, column=1, padx=3, pady=0)
        self.lbl_current_page_2.grid(row=0, column=2, padx=0, pady=0)
        # } } }
        self.btn_next_page.grid(row=0, column=3, padx=3, pady=0)
        self.btn_last_page.grid(row=0, column=4, padx=3, pady=0)
        # } }
        # }

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)
        self.tip_btn_search_settings = ttip.Hovertip(self.btn_search_settings, 'Параметры поиска', hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(self.btn_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(self.btn_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(self.btn_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(self.btn_last_page, 'В конец', hover_delay=650)

        self.bind('<Up>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-U>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))
        self.bind('<Control-u>', lambda event: self.scrolled_frame.canvas.yview_moveto(0.0))

        self.bind('<Down>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-D>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))
        self.bind('<Control-d>', lambda event: self.scrolled_frame.canvas.yview_moveto(1.0))

        self.print(True)  # Выводим статьи

    # Нажатие на кнопку "Настройки поиска"
    def search_settings(self):
        window = SearchSettingsW(self, self.search_only_fav, self.search_only_full,
                                 self.search_wrd, self.search_tr, self.search_frm, self.search_nt)
        self.search_only_fav, self.search_only_full, self.search_wrd, self.search_tr, self.search_frm,\
            self.search_nt = window.open()

    # Изменить статью
    def edit_entry(self, key: tuple[str, int]):
        EditW(self, key).open()

        self.print(False)

    # Нажатие на кнопку "Поиск"
    def print(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-F>')
            fr.unbind('<Control-f>')
            fr.destroy()

        # Выбираем нужные статьи
        if self.search_only_fav:
            keys = [key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].fav]
        else:
            keys = [key for key in _0_global_dct.d.keys()]
        full_matches, particular_matches = search_entries(_0_global_dct, tuple(keys), self.var_query.get(),
                                                          self.search_wrd, self.search_tr,
                                                          self.search_frm, self.search_nt)
        if self.search_only_full:
            self.keys = tuple(full_matches)
        else:
            self.keys = tuple(full_matches) + tuple(particular_matches)

        # Вычисляем значения некоторых количественных переменных
        self.count_elements = len(self.keys)
        if self.count_elements == 0:
            self.count_pages = 1
        else:
            self.count_pages = math.ceil(self.count_elements / self.max_elements_on_page)
        if self.current_page > self.count_pages:
            self.current_page = self.count_pages
            self.start_index = (self.count_pages - 1) * self.max_elements_on_page
        if self.current_page == self.count_pages:
            if self.count_elements % self.max_elements_on_page == 0 and self.count_elements != 0:
                self.count_elements_on_page = self.max_elements_on_page
            else:
                self.count_elements_on_page = self.count_elements % self.max_elements_on_page
        else:
            self.count_elements_on_page = self.max_elements_on_page
        # Выводим информацию о количестве статей
        self.var_info.set(f'Найдено статей: {self.count_elements}')
        # Выводим номер страницы
        self.var_current_page.set(str(self.current_page))
        self.entry_current_page.icursor(len(str(self.current_page)))
        self.lbl_current_page_2.configure(text=f'из {self.count_pages}')

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(self.count_elements_on_page)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.edit_entry(self.keys[self.start_index + i]),
                                   takefocus=False, style='Note.TButton')
                        for i in range(self.count_elements_on_page)]
        # Выводим текст на кнопки
        for i in range(self.count_elements_on_page):
            self.buttons[i].configure(text=get_all_entry_info(_0_global_dct.d[self.keys[self.start_index + i]], 75, 13))
        # Расставляем элементы
        for i in range(self.count_elements_on_page):
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(self.count_elements_on_page):
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event, i=i: self.entry_query.focus_set())
            self.frames[i].bind('<Control-F>', lambda event, i=i: self.fav_one(i, self.keys[self.start_index + i]))
            self.frames[i].bind('<Control-f>', lambda event, i=i: self.fav_one(i, self.keys[self.start_index + i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Обновить одну из кнопок журнала
    def refresh_one_button(self, index: int, key: tuple[str, int]):
        # Выводим текст на кнопку
        self.buttons[index].configure(text=get_all_entry_info(_0_global_dct.d[key], 75, 13))

        # Выводим информацию о количестве статей
        self.var_info.set(f'Найдено статей: {self.count_elements}')

    # Перейти на страницу с заданным номером
    def go_to_page_with_number(self, number: int):
        self.current_page = number
        self.start_index = (self.current_page - 1) * self.max_elements_on_page
        self.print(True)

    # Перейти на предыдущую страницу
    def go_to_prev_page(self):
        if self.current_page != 1:
            self.go_to_page_with_number(self.current_page - 1)

    # Перейти на следующую страницу
    def go_to_next_page(self):
        if self.current_page != self.count_pages:
            self.go_to_page_with_number(self.current_page + 1)

    # Перейти на первую страницу
    def go_to_first_page(self):
        self.go_to_page_with_number(1)

    # Перейти на последнюю страницу
    def go_to_last_page(self):
        self.go_to_page_with_number(self.count_pages)

    # Добавить одну статью в избранное (или убрать)
    def fav_one(self, index: int, key: tuple[str, int]):
        _0_global_dct.d[key].change_fav()

        self.refresh_one_button(index, key)

    # Нажатие на кнопку "Справка" (картинка с вопросом)
    def about_window(self):
        PopupMsgW(self, '* Чтобы добавить статью в избранное, наведите на неё мышку и нажмите Ctrl+F\n'
                        '* Чтобы прокрутить в самый низ, нажмите Ctrl+D или DOWN\n'
                        '* Чтобы прокрутить в самый верх, нажмите Ctrl+U или UP',
                  msg_justify='left').open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_query.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_search.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно добавления статьи
class AddW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Добавление статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.dct_key = None

        self.var_wrd = tk.StringVar()
        self.var_tr = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        self.lbl_wrd = ttk.Label(self, text='Введите слово:', style='Default.TLabel')
        self.entry_wrd = ttk.Entry(self, textvariable=self.var_wrd, width=50, validate='all',
                                   style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_tr = ttk.Label(self, text='Введите перевод:', style='Default.TLabel')
        self.entry_tr = ttk.Entry(self, textvariable=self.var_tr, width=50, validate='all',
                                  style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_fav = ttk.Label(self, text='Избранное:', style='Default.TLabel')
        self.frame = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.check_fav = ttk.Checkbutton(self.frame, variable=self.var_fav, style='Default.TCheckbutton')
        self.lbl_msg = ttk.Label(self.frame, justify='left', style='Default.TLabel')
        # }
        self.btn_add = ttk.Button(self, text='Добавить', command=self.add, takefocus=False, style='Default.TButton')

        self.lbl_wrd.grid(  row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_wrd.grid(row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr.grid(   row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr.grid( row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_fav.grid(  row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.frame.grid(    row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        # {
        self.check_fav.grid(row=0, column=0, padx=0,      pady=0)
        self.lbl_msg.grid(  row=0, column=1, padx=(6, 0), pady=0)
        # }
        self.btn_add.grid(row=3, columnspan=2, padx=6, pady=(0, 6))

        btn_disable(self.btn_add)

        # При незаполненных полях нельзя нажать кнопку
        def validate_entries(value_wrd: str, value_tr: str):
            if value_wrd == '' or value_tr == '':
                btn_disable(self.btn_add)
            else:
                btn_enable(self.btn_add, self.add)

            words = (entry.wrd for entry in _0_global_dct.d.values())
            translations = []
            for tr in (entry.tr for entry in _0_global_dct.d.values()):
                translations += tr

            if value_wrd in words:
                keys_with_this_word = (key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].wrd == value_wrd)
                translations = []
                for tr in (_0_global_dct.d[key].tr for key in keys_with_this_word):
                    translations += tr
                if value_tr in translations:
                    self.lbl_msg.configure(text='Такая статья уже есть в словаре')
                else:
                    self.lbl_msg.configure(text='Такое слово уже есть в словаре')
            elif value_tr in translations:
                self.lbl_msg.configure(text='Слово с таким переводом уже есть в словаре')
            else:
                self.lbl_msg.configure(text='')

            return True

        self.vcmd_wrd = (self.register(lambda value: validate_entries(value, self.var_tr.get())), '%P')
        self.vcmd_tr = (self.register(lambda value: validate_entries(self.var_wrd.get(), value)), '%P')
        self.entry_wrd['validatecommand'] = self.vcmd_wrd
        self.entry_tr['validatecommand'] = self.vcmd_tr

        self.entry_wrd.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_wrd.focus_set())

        self.entry_wrd.icursor(len(self.var_wrd.get()))

    # Добавление статьи
    def add(self):
        global _0_global_has_progress

        self.dct_key = add_entry_with_choose(_0_global_dct, self, encode_special_combinations(self.var_wrd.get()),
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
        self.title(f'{PROGRAM_NAME} - Настройки')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.parent = parent
        self.current_tab = 1  # Текущая вкладка (1 или 2)
        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)
        self.backup_scale = _0_global_scale

        self.var_mgsp = tk.StringVar(value=str(_0_global_min_good_score_perc))
        self.var_check_register = tk.BooleanVar(value=bool(_0_global_check_register))
        self.var_show_updates = tk.BooleanVar(value=bool(_0_global_show_updates))
        self.var_show_typo_button = tk.BooleanVar(value=bool(_0_global_with_typo))
        self.var_theme = tk.StringVar(value=th)
        self.var_themes_url = tk.StringVar(value=URL_RELEASES)

        self.img_about = tk.PhotoImage()
        self.img_plus = tk.PhotoImage()
        self.img_minus = tk.PhotoImage()

        self.dcts_savenames = []
        self.dcts_frames = []
        self.dcts_buttons = []

        # Только целые числа от 0 до 100
        self.vcmd = (self.register(validate_percent), '%P')

        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tab_local = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.lbl_dct_name = ttk.Label(self, text=split_text(f'Открыт словарь "{_0_global_dct_savename}"',
                                                            30, add_right_spaces=False),
                                      justify='center', style='Default.TLabel')
        self.tabs.add(self.tab_local, text='Настройки словаря')
        # {
        self.frame_mgsp = ttk.Frame(self.tab_local, style='Default.TFrame')
        # { {
        self.btn_about_mgsp = ttk.Button(self.frame_mgsp, command=self.about_mgsp, width=2, takefocus=False)
        set_image(self.btn_about_mgsp, self.img_about, img_about, '?')
        self.lbl_mgsp = ttk.Label(self.frame_mgsp, text='Минимальный приемлемый процент угадываний слова:',
                                  style='Default.TLabel')
        self.entry_mgsp = ttk.Entry(self.frame_mgsp, textvariable=self.var_mgsp, width=4,
                                    validate='key', validatecommand=self.vcmd,
                                    style='Default.TEntry', font=('StdFont', _0_global_scale))
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
        self.btn_groups = ttk.Button(self.tab_local, text='Группы', #command=self.groups_settings,
                                     takefocus=False, style='Default.TButton')
        #
        self.btn_special_combinations = ttk.Button(self.tab_local, text='Специальные комбинации',
                                                   command=self.special_combinations_settings,
                                                   takefocus=False, style='Default.TButton')
        #
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
        self.btn_about_typo = ttk.Button(self.frame_show_typo_button, command=self.about_typo, width=2, takefocus=False)
        set_image(self.btn_about_typo, self.img_about, img_about, '?')
        self.lbl_show_typo_button = ttk.Label(self.frame_show_typo_button, text='Показывать кнопку "Опечатка":',
                                              style='Default.TLabel')
        self.check_show_typo_button = ttk.Checkbutton(self.frame_show_typo_button, variable=self.var_show_typo_button,
                                                      style='Default.TCheckbutton')
        # } }
        self.frame_dcts = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_dcts = ttk.Label(self.frame_dcts, text='Существующие словари:', style='Default.TLabel')
        self.btn_about_dcts = ttk.Button(self.frame_dcts, command=self.about_dcts, width=2, takefocus=False)
        set_image(self.btn_about_dcts, self.img_about, img_about, '?')
        self.scrolled_frame_dcts = ScrollFrame(self.frame_dcts,
                                               SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                               SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.frame_dct_buttons = ttk.Frame(self.frame_dcts, style='Invis.TFrame')
        # { { {
        self.btn_dct_create = ttk.Button(self.frame_dct_buttons, text='Новый словарь', command=self.dct_create,
                                         takefocus=False, style='Default.TButton')
        self.btn_dct_import = ttk.Button(self.frame_dct_buttons, text='Импортировать словарь', command=self.dct_import,
                                         takefocus=False, style='Default.TButton')
        # } } }
        self.lbl_dcts_warn = ttk.Label(self.frame_dcts, text='Изменения словарей\n'
                                                             'сохраняются сразу!',
                                       style='Warn.TLabel')
        # } }
        self.frame_themes = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.lbl_themes = ttk.Label(self.frame_themes, text='Тема:', style='Default.TLabel')
        self.combo_themes = ttk.Combobox(self.frame_themes, textvariable=self.var_theme, values=THEMES,
                                         state='readonly', width=15, style='Default.TCombobox',
                                         font=('DejaVu Sans Mono', _0_global_scale))
        self.lbl_themes_version = ttk.Label(self.frame_themes, text=f'Требуемая версия тем: {REQUIRED_THEME_VERSION}\n'
                                                                    f'Актуальные темы можно скачать здесь:',
                                            justify='left', style='Default.TLabel')
        self.entry_themes_version = ttk.Entry(self.frame_themes, textvariable=self.var_themes_url,
                                              state='readonly', width=47, justify='center',
                                              style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_custom_theme = ttk.Button(self.frame_themes, text='Собственная тема', command=self.custom_theme,
                                           takefocus=False, style='Default.TButton')
        # } }
        self.frame_scale = ttk.Frame(self.tab_global, style='Default.TFrame')
        # { {
        self.btn_scale_minus = ttk.Button(self.frame_scale, command=self.scale_minus,
                                          width=2, state='normal', takefocus=False)
        set_image(self.btn_scale_minus, self.img_minus, img_delete, '-')
        self.lbl_scale = ttk.Label(self.frame_scale, text=f'Масштаб ({_0_global_scale}x)', style='Default.TLabel')
        self.btn_scale_plus = ttk.Button(self.frame_scale, command=self.scale_plus,
                                         width=2, state='normal', takefocus=False)
        set_image(self.btn_scale_plus, self.img_plus, img_add, '+')
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
        self.btn_groups.grid(              row=3, padx=6, pady=6)
        self.btn_special_combinations.grid(row=4, padx=6, pady=6)
        self.lbl_save_warn.grid(           row=5, padx=6, pady=6, sticky='S')
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
        self.lbl_dcts.grid(           row=0,            column=0, padx=6,      pady=(6, 0))
        self.btn_about_dcts.grid(     row=0,            column=1, padx=6,      pady=(6, 0))
        self.scrolled_frame_dcts.grid(row=1, rowspan=2, column=0, padx=(6, 0), pady=(0, 6))
        self.frame_dct_buttons.grid(  row=1,            column=1, padx=6,      pady=0)
        # { {
        self.btn_dct_create.grid(row=0, column=0, padx=0, pady=(0, 3), sticky='WE')
        self.btn_dct_import.grid(row=1, column=0, padx=0, pady=(3, 0), sticky='WE')
        # } }
        self.lbl_dcts_warn.grid(row=2, column=1, padx=6, pady=(3, 6))
        # }
        self.frame_themes.grid(row=3, padx=6, pady=6)
        # {
        self.lbl_themes.grid(          row=0, column=0,               padx=(6, 1), pady=6,      sticky='S')
        self.combo_themes.grid(        row=0, column=1,               padx=0,      pady=6,      sticky='S')
        self.lbl_themes_version.grid(  row=0, column=2,               padx=6,      pady=(6, 0), sticky='WS')
        self.btn_custom_theme.grid(    row=1, column=0, columnspan=2, padx=0,      pady=(0, 6), sticky='E')
        self.entry_themes_version.grid(row=1, column=2,               padx=6,      pady=(0, 6), sticky='WENS')
        # }
        self.frame_scale.grid(row=4, padx=6, pady=6)
        # {
        self.btn_scale_minus.grid(row=0, column=0, padx=(6, 3), pady=6)
        self.lbl_scale.grid(      row=0, column=1, padx=(3, 3), pady=6)
        self.btn_scale_plus.grid( row=0, column=2, padx=(3, 6), pady=6)
        # }
        #
        self.btn_save.grid( row=4, column=0, padx=(6, 3), pady=(0, 6))
        self.btn_close.grid(row=4, column=1, padx=(0, 6), pady=(0, 6))

        self.tip_btn_about_mgsp = ttip.Hovertip(self.btn_about_mgsp, 'Справка', hover_delay=450)
        self.tip_btn_about_typo = ttip.Hovertip(self.btn_about_typo, 'Справка', hover_delay=450)
        self.tip_btn_about_dcts = ttip.Hovertip(self.btn_about_dcts, 'Справка', hover_delay=450)

        self.entry_mgsp.icursor(len(self.var_mgsp.get()))
        self.print_dct_list(True)
        self.refresh_scale_buttons()

    # Справка о МППУ (срабатывает при нажатии на кнопку)
    def about_mgsp(self):
        PopupImgW(self, img_about_mgsp, 'Статьи, у которых процент угадывания ниже этого значения,\n'
                                        'будут считаться более сложными.\n'
                                        'При выборе режима учёбы "В первую очередь сложные"\n'
                                        'такие слова будут чаще попадаться.').open()

    # Настройки грамматических категорий (срабатывает при нажатии на кнопку)
    def categories_settings(self):
        self.has_ctg_changes = CategoriesSettingsW(self).open() or self.has_ctg_changes

    # Настройки групп (срабатывает при нажатии на кнопку)
    def groups_settings(self):
        self.has_groups_changes = GroupsSettingsW(self).open() or self.has_groups_changes

    # Настройки специальных комбинаций (срабатывает при нажатии на кнопку)
    def special_combinations_settings(self):
        self.has_spec_comb_changes = SpecialCombinationsSettingsW(self).open() or self.has_spec_comb_changes

    # Справка о кнопке "Опечатка" (срабатывает при нажатии на кнопку)
    def about_typo(self):
        PopupImgW(self, img_about_typo, 'Если функция включена, то\n'
                                        'когда вы неверно отвечаете при учёбе,\n'
                                        'появляется кнопка "Просто опечатка".\n'
                                        'При её нажатии, ошибка не засчитывается.\n'
                                        'Срабатывает при нажатии на Tab.').open()

    # Справка о словарях (срабатывает при нажатии на кнопку)
    def about_dcts(self):
        PopupMsgW(self, '* Чтобы открыть словарь, наведите на него мышку и нажмите ЛКМ\n'
                        '* Чтобы переименовать словарь, наведите на него мышку и нажмите Ctrl+R\n'
                        '* Чтобы удалить словарь, наведите на него мышку и нажмите Ctrl+D\n'
                        '* Чтобы экспортировать словарь, наведите на него мышку и нажмите Ctrl+E',
                  msg_justify='left').open()

    # Открыть словарь
    def dct_open(self, savename: str):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc, _0_global_categories,\
            _0_global_special_combinations, _0_global_check_register, _0_global_has_progress,\
            _0_global_session_number, _0_global_search_settings, _0_global_learn_settings

        if savename == _0_global_dct_savename:
            return

        # Если есть прогресс, то предлагается его сохранить
        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, _0_global_dct_savename, _0_global_has_progress)

        _0_global_dct = Dictionary()
        savename = upload_dct(self, _0_global_dct, savename, 'Отмена')
        if not savename:
            self.destroy()  # Если была попытка открыть повреждённый словарь, то при сохранении настроек, текущий словарь стёрся бы
            return
        _0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register, _0_global_categories,\
            _0_global_dct.groups = upload_local_settings(savename)
        _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
            upload_local_auto_settings(savename)
        _0_global_dct_savename = savename
        save_dct_name()

        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(savename)

        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

        self.refresh()

    # Переименовать словарь
    def dct_rename(self, old_savename: str):
        global _0_global_dct_savename

        window_rename = PopupEntryW(self, f'Введите новое название для словаря "{old_savename}"',
                                    default_value=old_savename, validate_function=validate_savename,
                                    check_answer_function=lambda wnd, val:
                                    check_dct_savename_edit(wnd, old_savename, val))
        closed, new_savename = window_rename.open()
        if closed or new_savename == old_savename:
            return

        os.rename(os.path.join(SAVES_PATH, old_savename), os.path.join(SAVES_PATH, new_savename))
        if _0_global_dct_savename == old_savename:
            _0_global_dct_savename = new_savename
            save_dct_name()
            # Обновляем надписи с названием открытого словаря
            self.refresh_open_dct_name(new_savename)
        print(f'Словарь "{old_savename}" успешно переименован в "{new_savename}"')

        self.print_dct_list(False)

    # Удалить словарь
    def dct_delete(self, savename: str):
        if savename == _0_global_dct_savename:
            warning(self, 'Вы не можете удалить словарь, когда он открыт!')
            return

        window_confirm = PopupDialogueW(self, f'Словарь "{savename}" будет безвозвратно удалён!\n'
                                              f'Хотите продолжить?',
                                        set_enter_on_btn='none')
        answer = window_confirm.open()
        if not answer:
            return

        shutil.rmtree(os.path.join(SAVES_PATH, savename))
        PopupMsgW(self, f'Словарь "{savename}" успешно удалён').open()

        self.print_dct_list(False)

    # Создать словарь (срабатывает при нажатии на кнопку)
    def dct_create(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc, _0_global_categories,\
            _0_global_special_combinations, _0_global_check_register, _0_global_has_progress,\
            _0_global_session_number, _0_global_search_settings, _0_global_learn_settings

        window = PopupEntryW(self, 'Введите название нового словаря', validate_function=validate_savename,
                             check_answer_function=check_dct_savename)
        closed, savename = window.open()
        if closed:
            return

        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, _0_global_dct_savename, _0_global_has_progress)

        _0_global_dct = Dictionary()
        create_dct(_0_global_dct, savename)
        _0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register, _0_global_categories,\
            _0_global_dct.groups = upload_local_settings(savename)
        _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
            upload_local_auto_settings(savename)
        _0_global_dct_savename = savename
        save_dct_name()

        print(f'\nСловарь "{savename}" успешно создан и открыт')

        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(savename)

        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

        self.refresh()

    # Экспортировать словарь
    def dct_export(self, savename: str):
        dst_path = askdirectory(title='Выберите папку для сохранения')
        if dst_path == '':
            return

        dct_export(savename, dst_path)

    # Импортировать словарь (срабатывает при нажатии на кнопку)
    def dct_import(self):
        src_path = askdirectory(title='Выберите папку сохранения')
        if src_path == '':
            return

        default_savename = re.split(r'[\\/]', src_path)[-1]
        window = PopupEntryW(self, 'Введите название для словаря', default_value=default_savename,
                             validate_function=validate_savename, check_answer_function=check_dct_savename)
        closed, savename = window.open()
        if closed:
            return

        dct_import(savename, src_path)

        self.refresh()

    # Задать пользовательскую тему (срабатывает при нажатии на кнопку)
    def custom_theme(self):
        CustomThemeSettingsW(self).open()
        upload_custom_theme()
        if th == CUSTOM_TH:
            self.set_theme()
        self.refresh_scale_buttons()

    # Увеличить масштаб (срабатывает при нажатии на кнопку)
    def scale_plus(self):
        global _0_global_scale

        _0_global_scale += 1

        self.parent.set_ttk_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.lbl_scale.configure(text=f'Масштаб ({_0_global_scale}x)')
        self.scrolled_frame_dcts.resize(SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                        SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.combo_themes.configure(font=('DejaVu Sans Mono', _0_global_scale))
        self.entry_themes_version.configure(font=('StdFont', _0_global_scale))
        self.entry_mgsp.configure(font=('StdFont', _0_global_scale))

        # Установка масштаба для окна уведомления об обновлении
        try:
            _0_global_window_last_version.entry_url.configure(font=('StdFont', _0_global_scale))
        except:  # Если окно обновления не открыто
            pass

        self.refresh_scale_buttons()

    # Уменьшить масштаб (срабатывает при нажатии на кнопку)
    def scale_minus(self):
        global _0_global_scale

        _0_global_scale -= 1

        self.parent.set_ttk_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.lbl_scale.configure(text=f'Масштаб ({_0_global_scale}x)')
        self.scrolled_frame_dcts.resize(SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                        SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.combo_themes.configure(font=('DejaVu Sans Mono', _0_global_scale))
        self.entry_themes_version.configure(font=('StdFont', _0_global_scale))
        self.entry_mgsp.configure(font=('StdFont', _0_global_scale))

        # Установка масштаба для окна уведомления об обновлении
        try:
            _0_global_window_last_version.entry_url.configure(font=('StdFont', _0_global_scale))
        except:  # Если окно обновления не открыто
            pass

        self.refresh_scale_buttons()

    # Сохранить настройки (срабатывает при нажатии на кнопку)
    def save(self):
        global _0_global_min_good_score_perc, _0_global_check_register, _0_global_show_updates, _0_global_with_typo,\
            _0_global_has_progress

        # Сохранить значение МППУ
        val = self.var_mgsp.get()
        if val == '':
            _0_global_min_good_score_perc = 0
        else:
            _0_global_min_good_score_perc = int(val)

        # Учитывать/не учитывать регистр букв при проверке введённого ответа при учёбе
        _0_global_check_register = int(self.var_check_register.get())  # 0 или 1

        # Разрешить/запретить сообщать о новых версиях
        _0_global_show_updates = int(self.var_show_updates.get())  # 0 или 1

        # Показывать/скрывать кнопку "Опечатка" при неверном ответе в учёбе
        _0_global_with_typo = int(self.var_show_typo_button.get())  # 0 или 1

        # Установка выбранной темы
        self.set_theme()

        # Обновление бэкапов сохранения
        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_fp = copy.deepcopy(_0_global_categories)
        self.backup_scale = _0_global_scale

        # Сохранение настроек в файлы
        save_local_settings(_0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register,
                            _0_global_categories, _0_global_dct.groups, _0_global_dct_savename)
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th,
                             _0_global_scale)
        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)

        # Сохранение словаря, если были изменения локальных настроек
        if self.has_local_changes():
            save_dct(_0_global_dct, _0_global_dct_savename)

        # Обнуление переменных, показывающих наличие изменений
        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        _0_global_has_progress = False

        # Обновить кнопки изменения масштаба
        self.refresh_scale_buttons()

    # Закрыть настройки без сохранения (срабатывает при нажатии на кнопку)
    def close(self):
        if self.has_changes():
            window = PopupDialogueW(self, 'У вас есть несохранённые изменения?\n'
                                          'Всё равно закрыть?')
            answer = window.open()
            if not answer:
                return
        self.destroy()

    # Вывод списка существующих словарей в текстовое поле
    def print_dct_list(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.dcts_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.dcts_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-R>')
            fr.unbind('<Control-r>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Control-E>')
            fr.unbind('<Control-e>')
            fr.unbind('<Leave>')
            fr.destroy()

        # Выбираем словари
        self.dcts_savenames = [savename for savename in os.listdir(SAVES_PATH)
                               if os.path.isdir(os.path.join(SAVES_PATH, savename))]
        dcts_count = len(self.dcts_savenames)

        # Создаём новые фреймы
        self.dcts_frames = [ttk.Frame(self.scrolled_frame_dcts.frame_canvas, style='Invis.TFrame')
                            for i in range(dcts_count)]
        # Создаём новые кнопки
        self.dcts_buttons = [ttk.Button(self.dcts_frames[i],
                                        command=lambda i=i: self.dct_open(self.dcts_savenames[i]),
                                        takefocus=False, style='Note.TButton')
                             for i in range(dcts_count)]
        # Выводим текст на кнопки
        for i in range(dcts_count):
            savename = self.dcts_savenames[i]
            if savename == _0_global_dct_savename:
                self.dcts_buttons[i].configure(text=split_text(f'{savename} (ОТКРЫТ)', 35))
            else:
                self.dcts_buttons[i].configure(text=split_text(f'{savename}', 35))
        # Расставляем элементы
        for i in range(dcts_count):
            self.dcts_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.dcts_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(dcts_count):
            self.dcts_frames[i].bind('<Enter>', lambda event, i=i: self.dcts_frames[i].focus_set())
            self.dcts_frames[i].bind('<Control-R>', lambda event, i=i: self.dct_rename(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-r>', lambda event, i=i: self.dct_rename(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-D>', lambda event, i=i: self.dct_delete(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-d>', lambda event, i=i: self.dct_delete(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-E>', lambda event, i=i: self.dct_export(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-e>', lambda event, i=i: self.dct_export(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Leave>', lambda event: self.focus_set())

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_dcts.canvas.yview_moveto(0.0)

    # Обновить кнопки изменения масштаба
    def refresh_scale_buttons(self):
        # Если масштаб минимальный, то кнопка минуса становится неактивной
        if _0_global_scale == SCALE_MIN:
            btn_disable(self.btn_scale_minus)
        else:
            btn_enable(self.btn_scale_minus, self.scale_minus, style='Image')

        # Если масштаб максимальный, то кнопка плюса становится неактивной
        if _0_global_scale == SCALE_MAX:
            btn_disable(self.btn_scale_plus)
        else:
            btn_enable(self.btn_scale_plus, self.scale_plus, style='Image')

    # Обновить настройки при открытии другого словаря
    def refresh(self):
        self.var_mgsp.set(str(_0_global_min_good_score_perc))
        self.var_check_register.set(bool(_0_global_check_register))
        self.print_dct_list(False)

    # Установить выбранную тему
    def set_theme(self):
        global th

        th = self.var_theme.get()

        self.parent.set_ttk_styles()  # Установка ttk-стилей
        upload_theme_img(th)  # Загрузка изображений темы

        # Установка изображений
        set_image(self.btn_about_mgsp, self.img_about, img_about, '?')
        set_image(self.btn_about_typo, self.img_about, img_about, '?')
        set_image(self.btn_about_dcts, self.img_about, img_about, '?')
        set_image(self.btn_scale_plus, self.img_plus, img_add, '+')
        set_image(self.btn_scale_minus, self.img_minus, img_delete, '-')

        # Установка некоторых стилей для окна настроек
        self.configure(bg=ST_BG[th])
        self.scrolled_frame_dcts.canvas.configure(bg=ST_BG_FIELDS[th])

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
            self.has_groups_changes or\
            self.has_spec_comb_changes or\
            int(self.var_check_register.get()) != _0_global_check_register or\
            int(f'0{self.var_mgsp.get()}') != _0_global_min_good_score_perc  # Если self.var_mgsp.get() == '', то 0

    # Были ли изменения настроек
    def has_changes(self):
        return self.has_local_changes() or\
            int(self.var_show_updates.get()) != _0_global_show_updates or\
            int(self.var_show_typo_button.get()) != _0_global_with_typo or\
            self.var_theme.get() != th or\
            self.backup_scale != _0_global_scale

    # Обновить надписи с названием открытого словаря
    def refresh_open_dct_name(self, savename: str):
        self.lbl_dct_name.config(text=split_text(f'Открыт словарь "{savename}"', 30, add_right_spaces=False))
        self.parent.lbl_dct_name.config(text=f'Открыт словарь\n'
                                             f'"{split_text(savename, 20, add_right_spaces=False)}"')

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


# Окно уведомления о выходе новой версии
class NewVersionAvailableW(tk.Toplevel):
    def __init__(self, parent, last_version: str):
        super().__init__(parent)
        self.title('Доступна новая версия')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_url = tk.StringVar(value=URL_GITHUB)  # Ссылка, для загрузки новой версии

        self.lbl_msg = ttk.Label(self, text=f'Доступна новая версия программы:\n'
                                            f'{last_version}',
                                 justify='center', style='Default.TLabel')
        self.frame_url = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.entry_url = ttk.Entry(self.frame_url, textvariable=self.var_url, state='readonly', justify='center',
                                   width=39, style='Default.TEntry', font=('StdFont', _0_global_scale))
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
        save_dct_if_has_progress(self, _0_global_dct, _0_global_dct_savename, _0_global_has_progress)

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
            for filename in ('resources/icon.png', 'aneno_dct.py', 'aneno_functions.py', 'aneno_constants.py',
                             'main.py'):
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


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

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
                                           f'"{split_text(_0_global_dct_savename, 20, add_right_spaces=False)}"',
                                      justify='center', style='Default.TLabel')
        # }
        self.frame_buttons = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_learn = ttk.Button(self.frame_buttons, text='Учить слова', command=self.learn,
                                    takefocus=False, style='Default.TButton')
        self.btn_print = ttk.Button(self.frame_buttons, text='Просмотреть словарь', command=self.print,
                                    takefocus=False, style='Default.TButton')
        self.btn_search = ttk.Button(self.frame_buttons, text='Найти статью', command=self.search,
                                     takefocus=False, style='Default.TButton')
        self.btn_add = ttk.Button(self.frame_buttons, text='Добавить статью', command=self.add,
                                  takefocus=False, style='Default.TButton')
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
        self.btn_learn.grid(        row=0, padx=0, pady=(0, 3))
        self.btn_print.grid(        row=1, padx=0, pady=(3, 3))
        self.btn_search.grid(       row=2, padx=0, pady=(3, 3))
        self.btn_add.grid(          row=3, padx=0, pady=(3, 3))
        self.btn_settings.grid(     row=4, padx=0, pady=(3, 3))
        self.btn_check_updates.grid(row=5, padx=0, pady=(3, 3))
        self.btn_save.grid(         row=6, padx=0, pady=(3, 3))
        self.btn_close.grid(        row=7, padx=0, pady=(3, 0))
        # }
        self.lbl_footer.grid(row=3, padx=6, pady=3)

        self.set_focus()

    # Нажатие на кнопку "Просмотреть словарь"
    def print(self):
        self.disable_all_buttons()
        PrintW(self).open()
        self.enable_all_buttons()

    # Нажатие на кнопку "Учить слова"
    def learn(self):
        self.disable_all_buttons()

        res = ChooseLearnModeW(self).open()
        if not res:
            self.enable_all_buttons()
            return
        LearnW(self, res).open()

        self.enable_all_buttons()

    # Нажатие на кнопку "Найти статью"
    def search(self):
        self.disable_all_buttons()
        SearchW(self).open()
        self.enable_all_buttons()

    # Нажатие на кнопку "Добавить статью"
    def add(self):
        self.disable_all_buttons()

        key = AddW(self).open()
        if not key:
            self.enable_all_buttons()
            return
        EditW(self, key).open()

        self.enable_all_buttons()

    # Нажатие на кнопку "Настройки"
    def settings(self):
        global _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale,\
            _0_global_min_good_score_perc, _0_global_categories, _0_global_special_combinations,\
            _0_global_check_register, _0_global_learn_settings

        self.disable_all_buttons()
        SettingsW(self).open()
        self.enable_all_buttons()

        # Обновляем глобальные настройки
        _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale =\
            upload_global_settings()
        # Обновляем локальные настройки
        _0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register, _0_global_categories,\
            _0_global_dct.groups = upload_local_settings(_0_global_dct_savename)
        # Обновляем локальные авто-настройки
        _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
            upload_local_auto_settings(_0_global_dct_savename)

        # Обновляем надпись с названием открытого словаря
        self.lbl_dct_name.config(text=f'Открыт словарь\n'
                                      f'"{split_text(_0_global_dct_savename, 20, add_right_spaces=False)}"')

        # Установка масштаба для окна уведомления об обновлении
        try:
            _0_global_window_last_version.entry_url.configure(font=('StdFont', _0_global_scale))
        except:  # Если окно обновления не открыто
            pass

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

        save_dct(_0_global_dct, _0_global_dct_savename)
        PopupMsgW(self, 'Прогресс успешно сохранён').open()
        print('\nПрогресс успешно сохранён')

        _0_global_has_progress = False

    # Нажатие на кнопку "Закрыть программу"
    def close(self):
        save_dct_if_has_progress(self, _0_global_dct, _0_global_dct_savename, _0_global_has_progress)
        self.quit()

    # Отключить все кнопки на главном окне
    def disable_all_buttons(self):
        for btn in (self.btn_learn, self.btn_print, self.btn_search, self.btn_add, self.btn_settings,
                    self.btn_check_updates, self.btn_save, self.btn_close):
            btn_disable(btn)

    # Включить все кнопки на главном окне
    def enable_all_buttons(self):
        btn_enable(self.btn_learn, self.learn)
        btn_enable(self.btn_print, self.print)
        btn_enable(self.btn_search, self.search)
        btn_enable(self.btn_add, self.add)
        btn_enable(self.btn_settings, self.settings)
        btn_enable(self.btn_check_updates, self.check_updates)
        btn_enable(self.btn_save, self.save, 'Yes')
        btn_enable(self.btn_close, self.close, 'No')

    # Установить ttk-стили
    def set_ttk_styles(self):
        # Стиль label "default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure('Default.TLabel',
                                      font=('StdFont', _0_global_scale),
                                      background=ST_BG[th],
                                      foreground=ST_FG[th])

        # Стиль label "header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('Header.TLabel',
                                     font=('StdFont', _0_global_scale + 5),
                                     background=ST_BG[th],
                                     foreground=ST_FG[th])

        # Стиль label "logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('Logo.TLabel',
                                   font=('Times', _0_global_scale + 11),
                                   background=ST_BG[th],
                                   foreground=ST_FG_LOGO[th])

        # Стиль label "footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('Footer.TLabel',
                                     font=('StdFont', _0_global_scale - 2),
                                     background=ST_BG[th],
                                     foreground=ST_FG_FOOTER[th])

        # Стиль label "warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('Warn.TLabel',
                                   font=('StdFont', _0_global_scale),
                                   background=ST_BG[th],
                                   foreground=ST_FG_WARN[th])

        # Стиль label "note"
        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure('Note.TLabel',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   background=ST_BTN_NOTE_BG[th],
                                   foreground=ST_BTN_NOTE_FG[th])

        # Стиль entry "default"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('Default.TEntry',
                                font=('StdFont', _0_global_scale))
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
                                      font=('StdFont', _0_global_scale + 2),
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
                                       font=('StdFont', _0_global_scale + 2),
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
                                  font=('StdFont', _0_global_scale + 2),
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
                                 font=('StdFont', _0_global_scale + 2),
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
                                    font=('StdFont', _0_global_scale + 2),
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

        # Стиль button "note"
        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure('Note.TButton',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   borderwidth=0)
        self.st_btn_note.map('Note.TButton',
                             relief=[('pressed', 'flat'),
                                     ('active', 'flat'),
                                     ('!active', 'flat')],
                             background=[('pressed', ST_BTN_NOTE_BG_SEL[th]),
                                         ('active', ST_BTN_NOTE_BG_HOV[th]),
                                         ('!active', ST_BTN_NOTE_BG[th])],
                             foreground=[('pressed', ST_BTN_NOTE_FG_SEL[th]),
                                         ('active', ST_BTN_NOTE_FG_HOV[th]),
                                         ('!active', ST_BTN_NOTE_FG[th])])

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
                                font=('DejaVu Sans Mono', _0_global_scale))
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
        self.option_add('*TCombobox*Listbox*Font', ('DejaVu Sans Mono', _0_global_scale))
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

        # Стиль notebook "default"
        self.st_note = ttk.Style()
        self.st_note.theme_use('alt')
        self.st_note.configure('Default.TNotebook',
                               font=('StdFont', _0_global_scale))
        self.st_note.map('Default.TNotebook',
                         troughcolor=[('active', ST_BG[th]),
                                      ('!active', ST_BG[th])],
                         background=[('selected', ST_BTN_BG_SEL[th]),
                                     ('!selected', ST_BG[th])])

        # Стиль вкладок notebook
        self.st_note.configure('TNotebook.Tab',
                               font=('StdFont', _0_global_scale))
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


""" Выполнение программы """


# Если папки отсутствуют, то они создаются
if RESOURCES_DIR not in os.listdir(MAIN_PATH):
    os.mkdir(RESOURCES_PATH)
if SAVES_DIR not in os.listdir(RESOURCES_PATH):
    os.mkdir(SAVES_PATH)
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

# Вывод информации о программе
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

_0_global_dct = Dictionary()
_0_global_has_progress = False

upload_themes(THEMES)  # Загружаем дополнительные темы
upload_custom_theme()  # Загружаем пользовательскую тему
_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale =\
    upload_global_settings()  # Загружаем глобальные настройки
upload_theme_img(th)  # Загружаем изображения для выбранной темы
root = MainW()  # Создаём графический интерфейс
_0_global_dct_savename = upload_dct(root, _0_global_dct, _0_global_dct_savename,
                                    'Завершить работу')  # Загружаем словарь
if not _0_global_dct_savename:
    exit(101)
_0_global_min_good_score_perc, _0_global_special_combinations, _0_global_check_register, _0_global_categories,\
    _0_global_dct.groups = upload_local_settings(_0_global_dct_savename)  # Загружаем локальные настройки
_0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
    upload_local_auto_settings(_0_global_dct_savename)  # Загружаем локальные авто-настройки
_0_global_window_last_version = check_updates(root, bool(_0_global_show_updates), False)  # Проверяем наличие обновлений
_0_global_learn_session_number = 0
root.iconphoto(True, tk.PhotoImage(file=ICON_PATH))  # Устанавливаем иконку
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
