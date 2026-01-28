import os
import shutil
from typing import Any, Literal, TypeVar, Type, Callable
import copy
import platform
import math
import json
import tkinter as tk
from tkinter import colorchooser
from tkinter.font import Font
import tkinter.ttk as ttk
import idlelib.tooltip as ttip  # Всплывающие подсказки
from tkinter.filedialog import askdirectory
import re  # Несколько разделителей в split
import webbrowser  # Для открытия веб-страницы
import urllib.request as urllib2  # Для проверки наличия обновлений
import wget  # Для загрузки обновления
import zipfile  # Для распаковки обновления
from itertools import chain

from backend import (
    Entry, Dictionary, Trainer, EntryID, GramForm,
    gram_form_to_str, create_training_config,
    TrainingMethod, TrainingOrder, EntrySelection,
    FormSelection, TrainingConfig,
)
from constants import *
from upgrades import *

CompoundValues = Literal['none', 'image', 'text', 'left', 'right', 'top', 'bottom', 'center']
T = TypeVar('T', bound=ttk.Widget)

""" Темы """

CUSTOM_TH = '</custom\\>'  # Название пользовательской темы
THEMES = [CUSTOM_TH, 'light', 'dark']  # Названия тем
DEFAULT_TH = THEMES[1]  # Тема по умолчанию

# Стили
# {стилизуемый_элемент: (описание, {тема: стиль})}
STYLES = {'*.BG.*':              ('Цвет фона окна',                                {THEMES[1]: '#F0F0F0', THEMES[2]: '#222222'}),
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

""" Функции проверки """


# Проверить строку на непустоту
def check_not_void(window_parent, value: str, msg_if_void: str) -> bool:
    if value == '':
        warning(window_parent, msg_if_void)
        return False
    return True


# Проверить корректность названия словаря
def check_dct_savename(window_parent, savename: str) -> bool:
    if len(savename) > 100:
        warning(window_parent, 'Название слишком длинное (> 100)!')
        return False
    if savename == '':
        warning(window_parent, 'Название должно содержать хотя бы один символ!')
        return False
    if savename in os.listdir(SAVES_PATH):
        warning(window_parent, 'Словарь с таким названием уже существует!')
        return False
    return True


# Проверить корректность названия словаря при изменении
def check_dct_savename_edit(window_parent, old_savename: str, new_savename: str) -> bool:
    if len(new_savename) > 100:
        warning(window_parent, 'Название слишком длинное (> 100)!')
        return False
    if new_savename == '':
        warning(window_parent, 'Название должно содержать хотя бы один символ!')
        return False
    if new_savename in os.listdir(SAVES_PATH) and new_savename != old_savename:
        warning(window_parent, 'Словарь с таким названием уже существует!')
        return False
    return True


# Проверить корректность перевода
def check_tr(
        window_parent,
        translations: list[str] | tuple[str, ...],
        new_tr: str,
        lemma: str,
) -> bool:
    new_tr = encode_special_combinations(new_tr, _0_global_special_combinations)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations:
        warning(window_parent, f'У слова "{lemma}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность перевода при изменении
def check_tr_edit(
        window_parent,
        translations: list[str] | tuple[str, ...],
        old_tr: str,
        new_tr: str,
        lemma: str,
) -> bool:
    new_tr = encode_special_combinations(new_tr, _0_global_special_combinations)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations and new_tr != old_tr:
        warning(window_parent, f'У слова "{lemma}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность фразы
def check_phr(
        window_parent,
        phrases: dict[str, list[str]],
        new_phr: tuple[str, str],
        lemma: str,
) -> bool:
    n1 = encode_special_combinations(new_phr[0], _0_global_special_combinations)
    n2 = encode_special_combinations(new_phr[1], _0_global_special_combinations)
    if n1 == '' or n2 == '':
        warning(window_parent, 'Фраза должна содержать хотя бы один символ!')
        return False
    if new_phr[0] in phrases.keys() and new_phr[1] in phrases[new_phr[0]]:
        warning(window_parent, f'Со словом "{lemma}" уже есть такая фраза!')
        return False
    return True


# Проверить корректность фразы при изменении
def check_phr_edit(
        window_parent,
        phrases: dict[str, list[str]],
        old_phr: tuple[str, str],
        new_phr: tuple[str, str],
        lemma: str,
) -> bool:
    n1 = encode_special_combinations(new_phr[0], _0_global_special_combinations)
    n2 = encode_special_combinations(new_phr[1], _0_global_special_combinations)
    if n1 == '' or n2 == '':
        warning(window_parent, 'Фраза должна содержать хотя бы один символ!')
        return False
    if new_phr[0] in phrases.keys() and new_phr[1] in phrases[new_phr[0]] and new_phr != old_phr:
        warning(window_parent, f'Со словом "{lemma}" уже есть такая фраза!')
        return False
    return True


# Проверить корректность сноски
def check_note(
        window_parent,
        notes: list[str] | tuple[str, ...],
        new_note: str,
        lemma: str,
) -> bool:
    new_note = encode_special_combinations(new_note, _0_global_special_combinations)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes:
        warning(window_parent, f'У слова "{lemma}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность сноски при изменении
def check_note_edit(
        window_parent,
        notes: list[str] | tuple[str, ...],
        old_note: str,
        new_note: str,
        lemma: str,
) -> bool:
    new_note = encode_special_combinations(new_note, _0_global_special_combinations)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes and new_note != old_note:
        warning(window_parent, f'У слова "{lemma}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность названия группы
def check_group_name(window_parent, groups: list[str] | tuple[str, ...], new_group: str) -> bool:
    new_group = encode_special_combinations(new_group, _0_global_special_combinations)
    if new_group == '':
        warning(window_parent, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_group == ALL_GROUPS:
        warning(window_parent, 'Группа не может иметь такое название!')
        return False
    if new_group in groups:
        warning(window_parent, f'Группа "{new_group}" уже существует!')
        return False
    return True


# Проверить корректность названия группы при изменении
def check_group_name_edit(
        window_parent,
        groups: list[str] | tuple[str, ...],
        old_group: str,
        new_group: str,
) -> bool:
    new_group = encode_special_combinations(new_group, _0_global_special_combinations)
    if new_group == '':
        warning(window_parent, 'Название группы должно содержать хотя бы один символ!')
        return False
    if new_group == ALL_GROUPS:
        warning(window_parent, 'Группа не может иметь такое название!')
        return False
    if new_group in groups and new_group != old_group:
        warning(window_parent, f'Группа "{new_group}" уже существует!')
        return False
    return True


# Проверить корректность названия категории
def check_ctg(window_parent, categories: list[str] | tuple[str, ...], new_ctg: str) -> bool:
    new_ctg = encode_special_combinations(new_ctg, _0_global_special_combinations)
    if new_ctg == '':
        warning(window_parent, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories:
        warning(window_parent, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


# Проверить корректность названия категории при изменении
def check_ctg_edit(
        window_parent,
        categories: list[str] | tuple[str, ...],
        old_ctg: str,
        new_ctg: str,
) -> bool:
    new_ctg = encode_special_combinations(new_ctg, _0_global_special_combinations)
    if new_ctg == '':
        warning(window_parent, 'Название категории должно содержать хотя бы один символ!')
        return False
    if new_ctg in categories and new_ctg != old_ctg:
        warning(window_parent, f'Категория "{new_ctg}" уже существует!')
        return False
    return True


# Проверить корректность значения категории
def check_ctg_val(window_parent, values: list[str] | tuple[str, ...], new_val: str) -> bool:
    new_val = encode_special_combinations(new_val, _0_global_special_combinations)
    if new_val == '':
        warning(window_parent, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_val in values:
        warning(window_parent, f'Значение "{new_val}" уже существует!')
        return False
    return True


# Проверить корректность значения категории при изменении
def check_ctg_val_edit(
        window_parent,
        values: list[str] | tuple[str, ...],
        old_val: str,
        new_val: str,
) -> bool:
    new_val = encode_special_combinations(new_val, _0_global_special_combinations)
    if new_val == '':
        warning(window_parent, 'Значение категории должно содержать хотя бы один символ!')
        return False
    if new_val in values and new_val != old_val:
        warning(window_parent, f'Значение "{new_val}" уже существует!')
        return False
    return True


# Проверить является ли строка разделимой (для split_line)
def is_splittable(line: str) -> bool:
    for c in line:
        if not (c.isalnum() or c in '()[]{}<>_-+*%!?.,;:`"\''):
            return True
    return False


""" Функции вывода """


# Вывести переводы
def get_tr(entry: Entry) -> str:
    return ', '.join(entry.tr)


# Вывести словоформы
def get_forms(entry: Entry, tab: int = 0) -> str:
    frm_keys = entry.forms.keys()
    return ('\n' + ' ' * tab).join((
        f'[{gram_form_to_str(key)}] {', '.join(entry.forms[key])}'
        for key in frm_keys
    ))


# Вывести переводы фразы
def get_phr_tr(entry: Entry, phr_key: str) -> str:
    return ', '.join(pt for pt in entry.phrases[phr_key])


# Вывести фразы
def get_phrases(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join((
        phr + ' - ' + get_phr_tr(entry, phr)
        for phr in entry.phrases
    ))


# Вывести сноски
def get_notes(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join(entry.notes)


# Вывести группы
def get_groups(entry: Entry) -> str:
    if entry.groups:
        return ', '.join(tuple(entry.groups))
    else:
        return '-'


# Вывести количество ошибок после последнего верного ответа
def get_correct_att_in_a_row(entry: Entry) -> str | int:
    if entry.total_att == 0:  # Если ещё не было попыток
        res = '-'
    elif entry.win_streak > 999:
        res = '+∞'
    elif entry.win_streak < -99:
        res = '-∞'
    else:
        res = entry.win_streak
    return res


# Вывести процент верных ответов
def get_entry_percent(entry: Entry) -> str:
    if entry.total_att == 0:  # Если ещё не было попыток
        res = '-'
    else:
        res = '{:.0%}'.format(entry.accuracy)
    return res


# Вывести статистику
def get_entry_stat(entry: Entry) -> str:
    win_streak = get_correct_att_in_a_row(entry)
    percent = get_entry_percent(entry)
    tab_correct = ' ' * (3 - len(str(win_streak)))
    tab_percent = ' ' * (4 - len(percent))
    res = f'[{tab_correct}{win_streak}:{tab_percent}{percent}]'
    return res


# Служебная функция для get_entry_info_briefly и get_entry_info_briefly_with_forms
def _get_entry_info_briefly(entry: Entry) -> str:
    if entry.is_fav:
        res = '(*)'
    else:
        res = '   '
    res += f' {get_entry_stat(entry)} {entry.lemma}: {get_tr(entry)}'
    return res


# Вывести статью - кратко
def get_entry_info_briefly(entry: Entry, len_str: int) -> str:
    return split_text(_get_entry_info_briefly(entry), len_str, tab=15)


# Вывести статью - подробно
def get_entry_info_detailed(entry: Entry, len_str: int) -> str:
    res = _get_entry_info_briefly(entry)
    if entry.n_gram_forms != 0:
        res += f'\n  Формы слова: {get_forms(entry, tab=15)}'
    if entry.phrases.keys():
        res += f'\n        Фразы: {get_phrases(entry, tab=15)}'
    if entry.n_notes != 0:
        res += f'\n       Сноски: {get_notes(entry, tab=15)}'
    if entry.groups:
        res += f'\n       Группы: {get_groups(entry)}'
    return split_text(res, len_str, tab=15)


# Вывести статью - со всей информацией
def get_all_entry_info(entry: Entry, len_str: int, tab: int = 0) -> str:
    res  = f'      Слово: {entry.lemma}\n'
    res += f'    Перевод: {get_tr(entry)}\n'

    res += f'Формы слова: '
    if entry.n_gram_forms == 0:
        res += '-\n'
    else:
        keys = [key for key in entry.forms.keys()]
        res += f'[{gram_form_to_str(keys[0])}] {', '.join(entry.forms[keys[0]])}\n'
        for i in range(1, entry.n_gram_forms):
            res += f'             [{gram_form_to_str(keys[i])}] {', '.join(entry.forms[keys[i]])}\n'

    res += '      Фразы: '
    if entry.n_phrases == 0:
        res += '-'
    else:
        res += get_phrases(entry, tab=13)

    res += '\n     Сноски: '
    if entry.n_notes == 0:
        res += '-'
    else:
        res += get_notes(entry, tab=13)

    res += '\n  Избранное: '
    if entry.is_fav:
        res += '+'
    else:
        res += '-'

    res += f'\n     Группы: {get_groups(entry)}\n'

    if entry.total_att == 0:  # Если ещё не было попыток
        res += ' Статистика: 1) Верных ответов подряд: -\n'
        res += '             2) Доля верных ответов: -'
    else:
        res += f' Статистика: 1) Верных ответов подряд: {entry.win_streak}\n'
        res += f'             2) Доля верных ответов: '
        res += f'{entry.correct_att}/{entry.total_att} = ' + '{:.0%}'.format(entry.accuracy)

    return split_text(res, len_str, tab=tab)


# Вывести слово со статистикой
def get_wrd_with_stat(entry: Entry) -> str:
    res = f'{entry.lemma} {get_entry_stat(entry)}'
    return res


# Вывести перевод со статистикой
def get_tr_with_stat(entry: Entry) -> str:
    res = f'{get_tr(entry)} {get_entry_stat(entry)}'
    return res


# Вывести перевод со словоформой и со статистикой
def get_tr_and_frm_with_stat(entry: Entry, frm_key: GramForm | list[str]) -> str:
    res = f'{get_tr(entry)} ({gram_form_to_str(frm_key)}) {get_entry_stat(entry)}'
    return res


# Вывести фразу со статистикой
def get_phr_with_stat(entry: Entry, phr_key: str) -> str:
    res = f'{phr_key} {get_entry_stat(entry)}'
    return res


# Вывести перевод фразы со статистикой
def get_phr_tr_with_stat(entry: Entry, phr_key: str) -> str:
    res = f'{get_phr_tr(entry, phr_key)} {get_entry_stat(entry)}'
    return res


# Вывести информацию о количестве статей в словаре
def dct_info(count_e: int, count_t: int, count_gf: int, count_wf: int) -> str:
    w = set_postfix(count_e, ('слово', 'слова', 'слов'))
    f = set_postfix(count_e + count_wf, ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(count_t, ('перевод', 'перевода', 'переводов'))
    return f'[ {count_e} {w} | {count_e + count_wf} {f} | {count_t} {t} ]'


# Вывести информацию о количестве избранных статей в словаре
def dct_info_fav(
        count_e: tuple[int, int],
        count_t: tuple[int, int],
        count_gf: tuple[int, int],
        count_wf: tuple[int, int],
) -> str:
    w = set_postfix(count_e[0], ('слово', 'слова', 'слов'))
    f = set_postfix(count_e[0] + count_wf[0], ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(count_t[0], ('перевод', 'перевода', 'переводов'))
    return f'[ {count_e[0]}/{count_e[1]} {w} '\
           f'| {count_e[0] + count_wf[0]}/{count_e[1] + count_wf[1]} {f} '\
           f'| {count_t[0]}/{count_t[1]} {t} ]'


""" Вспомогательные функции """


# Преобразовать специальную комбинацию в читаемый вид (для отображения в настройках)
def special_combination(key: tuple[str, str]) -> str:
    value = _0_global_special_combinations[key]
    return f'{key[0]}{key[1]} -> {value}'


# Преобразовать в тексте специальные комбинации в соответствующие символы
def encode_special_combinations(
        text: str,
        special_combinations: dict[tuple[str, str], str],
) -> str:
    encoded_text = ''

    opening_symbol = None  # Встречен ли открывающий символ специальной комбинации
    for symbol in text:
        if opening_symbol:
            if (opening_symbol, symbol) in special_combinations.keys():  # Если есть такая комбинация
                encoded_text += special_combinations[opening_symbol, symbol]
            elif symbol == opening_symbol:  # Если встречено два открывающих символа подряд
                encoded_text += opening_symbol  # $$ -> $
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
def simplify(text: str) -> tuple[str, list[str]]:
    encoded_text = encode_special_combinations(text, _0_global_special_combinations)
    converted_text = ''
    transformations = []

    for symbol in encoded_text:
        if symbol in ('ä', 'Ä', 'ë', 'Ë', 'ö', 'Ö', 'ü', 'Ü', 'ß', 'ẞ'):
            pos = ('ä', 'Ä', 'ë', 'Ë', 'ö', 'Ö', 'ü', 'Ü', 'ß', 'ẞ').index(symbol)
            converted_text += ('a', 'A', 'e', 'E', 'o', 'O', 'u', 'U', 'ss', 'SS')[pos]
            transformations += (
                ['ä'], ['Ä'], ['ë'], ['Ë'], ['ö'], ['Ö'], ['ü'], ['Ü'], ['ß', ''], ['ẞ', '']
            )[pos]
        else:
            converted_text += symbol
            transformations += [symbol]

    return converted_text.lower(), transformations


# Найти в строке подстроку и выделить её (только частичные совпадения)
def find_and_highlight(target_wrd: str, to_search_wrd: str) -> str:
    if target_wrd == to_search_wrd:  # Полное совпадение не учитывается
        return ''

    target_wrd = encode_special_combinations(target_wrd, _0_global_special_combinations)
    to_search_wrd = encode_special_combinations(to_search_wrd, _0_global_special_combinations)

    target_simpl, target_arr = simplify(target_wrd)
    search_simpl, search_arr = simplify(to_search_wrd)

    pos = target_simpl.find(search_simpl)
    if pos != -1:
        search_len = len(encode_special_combinations(search_simpl, _0_global_special_combinations))
        end_pos = pos + search_len
        if to_search_wrd == '':  # Если искомая подстрока пустая, то она не выделяется
            res = target_wrd
        else:
            res = ''.join((
                s for s in
                target_arr[:pos] + ['['] + target_arr[pos:end_pos] + [']'] + target_arr[end_pos:]
            ))
        return res
    return ''


# Разделить строку на слова
def split_line(line: str) -> list[list[str]]:
    len_line = len(line)
    res = []

    i = 0
    while i < len_line and is_splittable(line[i]):
        i += 1
    if i != 0:
        res += [['', line[0:i]]]

    while i < len_line:
        word = ''
        separator = ''
        while i < len_line and not is_splittable(line[i]):
            word += line[i]
            i += 1
        while i < len_line and is_splittable(line[i]):
            separator += line[i]
            i += 1
        res += [[word, separator]]

    return res


# Разделить текст на части, длина которых не превышает заданное значение
def split_text(text: str, max_str_len: int, tab: int = 0, to_add_right_spaces: bool = True) -> str:
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
            if to_add_right_spaces:
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
                    res += ''.join([
                        '\n' + ' ' * tab + word[i:i+max_str_len-tab]
                        for i in range(tmp, len_word, max_str_len-tab)
                    ])
                    current_len = tab + (len_word - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если слово не вмещается в данную строку, но может вместиться в следующую,
                # то записываем его в следующую
                elif len_word + current_len > max_str_len:
                    # Если нужно, дополняем строку пробелами до максимальной длины
                    if to_add_right_spaces:
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
                    res += ''.join([
                        '\n' + ' ' * tab + separator[i:i+max_str_len-tab]
                        for i in range(tmp, len_separator, max_str_len-tab)
                    ])
                    current_len = tab + (len_separator - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если разделитель вмещается в данную строку целиком, то просто записываем его
                else:
                    res += separator
                    current_len += len_separator
            # Если нужно, дополняем строку пробелами до максимальной длины
            if to_add_right_spaces:
                res += ' ' * (max_str_len - current_len)
        # Если строка не последняя, то добавляем перенос строки
        if i != count_lines - 1:
            res += '\n'
    return res


# Выбрать окончание слова в зависимости от количественного числительного
def set_postfix(n: int, wrd_forms: tuple[str, str, str]) -> str:
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
def choose_one_of_similar_entries(dct: Dictionary, window_parent, lemma: str):
    homograph_ids = dct.search([('lemmas', lemma)])
    if len(homograph_ids) == 1:  # Если статья только одна, то возвращает её ключ
        return homograph_ids.pop()
    window_entries = ChooseOneOfSimilarEntriesW(window_parent, dct, lemma)
    answer = window_entries.open()
    if not answer:
        return None
    return answer


# Изменить слово в статье
def edit_wrd_with_choose(
        dct: Dictionary,
        window_parent,
        key: EntryID,
        new_wrd: str,
) -> tuple[EntryID | None, bool]:
    if dct.search([('lemmas', new_wrd)]):  # Если в словаре уже есть статья с таким словом
        window = PopupDialogueW(
            window_parent,
            'Статья с таким словом уже есть в словаре\n'
            'Что вы хотите сделать?',
            'Добавить к существующей статье',
            'Оставить отдельной статьёй',
            set_enter_on_btn='none', st_left='Default', st_right='Default',
            val_left='l', val_right='r', val_on_close='c',
        )
        answer = window.open()
        if answer == 'l':  # Добавить к существующей статье
            new_key = choose_one_of_similar_entries(dct, window_parent, new_wrd)
            if not new_key:
                return key, False
            dct.merge_entries(new_key, key)
            return new_key, True
        elif answer == 'r':  # Оставить отдельной статьёй
            dct.edit_lemma(key, new_wrd)
            return key, True
        else:
            return key, False
    else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
        dct.edit_lemma(key, new_wrd)
        return key, True


# Добавить статью в словарь (для пользователя)
def add_entry_with_choose(dct: Dictionary, window_parent, lemma: str, tr: str) -> EntryID | None:
    if dct.search([('lemmas', lemma)]):  # Если в словаре уже есть статья с таким словом
        window = PopupDialogueW(
            window_parent,
            'Статья с таким словом уже есть в словаре\n'
            'Что вы хотите сделать?',
            'Добавить к существующей статье',
            'Создать новую статью',
            set_enter_on_btn='none', st_left='Default', st_right='Default',
            val_left='l', val_right='r', val_on_close='c',
        )
        answer = window.open()
        if answer == 'l':  # Добавить к существующей статье
            key = choose_one_of_similar_entries(dct, window_parent, lemma)
            if not key:
                return None
            dct.add_tr(key, tr)
            return key
        elif answer == 'r':  # Создать новую статью
            return dct.add_entry(lemma, tr)
        else:
            return None
    else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
        return dct.add_entry(lemma, tr)


# Добавить категорию
def add_ctg(window_parent, dct: Dictionary) -> bool:
    # Ввод названия новой категории
    window_ctg = PopupEntryW(
        window_parent,
        'Введите название новой категории',
        check_answer_function=lambda wnd, val: check_ctg(wnd, tuple(dct.features.keys()), val),
    )
    closed, new_ctg = window_ctg.open()
    if closed:
        return False
    new_ctg = encode_special_combinations(new_ctg, _0_global_special_combinations)

    # Ввод первого значения категории
    window_val = PopupEntryW(
        window_parent,
        'Необходимо добавить хотя бы одно значение для категории',
        check_answer_function=lambda wnd, val: check_ctg_val(wnd, (), val),
    )
    closed, new_val = window_val.open()
    if closed:
        return False
    new_val = encode_special_combinations(new_val, _0_global_special_combinations)

    # Обновление категорий
    dct.add_ctg(new_ctg, [new_val])
    return True


# Переименовать категорию
def rename_ctg(window_parent, dct: Dictionary, old_ctg_name: str) -> bool | None:
    # Ввод нового названия категории
    window_entry = PopupEntryW(
        window_parent,
        'Введите новое название категории',
        default_value=old_ctg_name,
        check_answer_function=lambda wnd, val: check_ctg_edit(
            wnd, tuple(dct.features.keys()), old_ctg_name, val
        ),
    )
    closed, new_ctg_name = window_entry.open()
    if closed:
        return False
    new_ctg_name = encode_special_combinations(new_ctg_name, _0_global_special_combinations)
    if new_ctg_name == old_ctg_name:
        return

    # Обновление категорий
    dct.rename_ctg(old_ctg_name, new_ctg_name)
    return True


# Удалить категорию
def delete_ctg(window_parent, dct: Dictionary, ctg_name: str) -> bool:
    window_dia = PopupDialogueW(
        window_parent,
        f'Все словоформы, содержащие категорию {ctg_name}, будут удалены!\n'
        f'Хотите продолжить?',
    )  # Подтверждение действия
    answer = window_dia.open()
    if not answer:
        return False

    # Обновление категорий
    dct.delete_ctg(ctg_name)
    return True


# Добавить значение категории
def add_ctg_value(
        window_parent,
        dct: Dictionary,
        ctg_name: str,
        values: list[str] | tuple[str, ...],
) -> bool:
    # Ввод нового значения
    window_entry = PopupEntryW(
        window_parent,
        'Введите новое значение категории',
        check_answer_function=lambda wnd, val: check_ctg_val(wnd, values, val),
    )
    closed, new_val = window_entry.open()
    if closed:
        return False

    new_val = encode_special_combinations(new_val, _0_global_special_combinations)
    dct.add_ctg_value(ctg_name, new_val)
    return True


# Переименовать значение категории
def rename_ctg_value(window_parent, dct: Dictionary, ctg_name: str, old_ctg_val: str) -> bool:
    # Ввод нового значения
    window_entry = PopupEntryW(
        window_parent,
        'Введите новое название значения',
        default_value=old_ctg_val,
        check_answer_function=lambda wnd, val: check_ctg_val_edit(
            wnd, dct.features[ctg_name], old_ctg_val, val
        ),
    )
    closed, new_ctg_val = window_entry.open()
    if closed:
        return False
    new_ctg_val = encode_special_combinations(new_ctg_val, _0_global_special_combinations)
    if new_ctg_val == old_ctg_val:
        return False

    # Переименовывание значения во всех словоформах, его содержащих
    dct.rename_ctg_value(ctg_name, old_ctg_val, new_ctg_val)
    return True


# Удалить значение категории
def delete_ctg_value(window_parent, dct: Dictionary, ctg_name: str, ctg_val: str) -> bool:
    window_dia = PopupDialogueW(
        window_parent,
        f'Все словоформы, содержащие значение {ctg_val}, будут удалены!\n'
        f'Хотите продолжить?',
    )  # Подтверждение действия
    answer = window_dia.open()
    if not answer:
        return False

    # Удаление всех словоформ, содержащих это значение категории
    dct.delete_ctg_value(ctg_name, ctg_val)
    return True


# Есть ли слово в строке
def wrd_in_line(line: str, wrd: str) -> bool:
    words = re.split(r'[.,;:!? \n()\[\]{}]', line)
    words = [w for w in words if w != '']
    return wrd in words


# Поиск статей в словаре
def search_entries(
        dct: Dictionary,
        dct_keys: tuple[EntryID, ...],
        query: str,
        to_search_wrd: bool,
        to_search_tr: bool,
        to_search_frm: bool,
        to_search_phr: bool,
        to_search_nt: bool,
) -> list[set]:
    query_l = query.lower()
    query_s = simplify(query)[0].replace('ё', 'е')
    results = [set() for _ in range(9)]
    for key in dct_keys:
        entry = dct[key]

        # Все фразы и переводы фраз для данной статьи
        phrases = list(entry.phrases.keys())
        for phr_key in entry.phrases.keys():
            for phr_tr in entry.phrases[phr_key]:
                phrases += [phr_tr]

        # TODO: code style

        if to_search_wrd and query == entry.lemma or\
           to_search_tr  and query in entry.tr or\
           to_search_frm and query in chain(*entry.forms.values()) or\
           to_search_phr and query in phrases or\
           to_search_nt  and query in entry.notes:
            results[0].add(key)
        elif to_search_wrd and query_l == entry.lemma.lower() or\
             to_search_tr  and query_l in [ tr.lower() for tr  in entry.tr] or\
             to_search_frm and query_l in [frm.lower() for frm in chain(*entry.forms.values())] or\
             to_search_phr and query_l in [phr.lower() for phr in phrases] or\
             to_search_nt  and query_l in [ nt.lower() for nt  in entry.notes]:
            results[1].add(key)
        elif to_search_wrd and query_s == simplify(entry.lemma)[0].replace('ё', 'е') or\
             to_search_tr  and query_s in [simplify( tr)[0].replace('ё', 'е') for tr  in entry.tr] or\
             to_search_frm and query_s in [simplify(frm)[0].replace('ё', 'е') for frm in chain(*entry.forms.values())] or\
             to_search_phr and query_s in [simplify(phr)[0].replace('ё', 'е') for phr in phrases] or\
             to_search_nt  and query_s in [simplify( nt)[0].replace('ё', 'е') for nt  in entry.notes]:
            results[2].add(key)

        elif to_search_wrd and wrd_in_line(entry.lemma, query) or\
             to_search_tr  and True in [wrd_in_line( tr, query) for tr  in entry.tr] or\
             to_search_frm and True in [wrd_in_line(frm, query) for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [wrd_in_line(phr, query) for phr in phrases] or\
             to_search_nt  and True in [wrd_in_line( nt, query) for nt  in entry.notes]:
            results[3].add(key)
        elif to_search_wrd and wrd_in_line(entry.lemma.lower(), query_l) or\
             to_search_tr  and True in [wrd_in_line( tr.lower(), query_l) for tr  in entry.tr] or\
             to_search_frm and True in [wrd_in_line(frm.lower(), query_l) for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [wrd_in_line(phr.lower(), query_l) for phr in phrases] or\
             to_search_nt  and True in [wrd_in_line( nt.lower(), query_l) for nt  in entry.notes]:
            results[4].add(key)
        elif to_search_wrd and wrd_in_line(simplify(entry.lemma)[0].replace('ё', 'е'), query_s) or\
             to_search_tr  and True in [wrd_in_line(simplify( tr)[0].replace('ё', 'е'), query_s) for tr  in entry.tr] or\
             to_search_frm and True in [wrd_in_line(simplify(frm)[0].replace('ё', 'е'), query_s) for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [wrd_in_line(simplify(phr)[0].replace('ё', 'е'), query_s) for phr in phrases] or\
             to_search_nt  and True in [wrd_in_line(simplify( nt)[0].replace('ё', 'е'), query_s) for nt  in entry.notes]:
            results[5].add(key)

        elif to_search_wrd and query in entry.lemma or\
             to_search_tr  and True in [query in tr  for tr  in entry.tr] or\
             to_search_frm and True in [query in frm for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [query in phr for phr in phrases] or\
             to_search_nt  and True in [query in nt  for nt  in entry.notes]:
            results[6].add(key)
        elif to_search_wrd and query_l in entry.lemma.lower() or\
             to_search_tr  and True in [query_l in  tr.lower() for tr  in entry.tr] or\
             to_search_frm and True in [query_l in frm.lower() for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [query_l in phr.lower() for phr in phrases] or\
             to_search_nt  and True in [query_l in  nt.lower() for nt  in entry.notes]:
            results[7].add(key)
        elif to_search_wrd and query_s in simplify(entry.lemma)[0].replace('ё', 'е') or\
             to_search_tr  and True in [query_s in simplify( tr)[0].replace('ё', 'е') for tr  in entry.tr] or\
             to_search_frm and True in [query_s in simplify(frm)[0].replace('ё', 'е') for frm in chain(*entry.forms.values())] or\
             to_search_phr and True in [query_s in simplify(phr)[0].replace('ё', 'е') for phr in phrases] or\
             to_search_nt  and True in [query_s in simplify( nt)[0].replace('ё', 'е') for nt  in entry.notes]:
            results[8].add(key)
    return results


# Проверить наличие обновлений программы
def check_updates(
        window_parent,
        app_data: AppData,
        to_show_if_no_updates: bool,
):
    to_check_for_updates = app_data.global_settings.to_check_for_updates

    print('\nПроверка наличия обновлений...')
    window_last_version = None
    try:
        data = urllib2.urlopen(URL_LAST_VERSION)
        last_version = str(data.readline().decode('utf-8')).strip()
        if PROGRAM_VERSION == last_version:
            print('Установлена последняя доступная версия программы')
            if to_check_for_updates and to_show_if_no_updates:
                PopupMsgW(
                    window_parent, app_data,
                    'Установлена последняя доступная версия программы'
                ).open()
        else:
            print(f'Доступна новая версия: {last_version}')
            if to_check_for_updates:
                window_last_version = NewVersionAvailableW(
                    window_parent, app_data, last_version
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
    return window_last_version


""" Загрузка/сохранение """


# Установить в качестве пользовательской темы тему по умолчанию
def create_default_custom_theme():
    styles_path = os.path.join(CUSTOM_THEME_PATH, STYLES_FN)
    with open(styles_path, 'w', encoding='utf-8') as styles_file:
        styles_file.write(
            f'{REQUIRED_THEME_VERSION}\n'
            f'1'
        )
        for key in STYLES.keys():  # Проходимся по стилизуемым элементам
            style = STYLES[key][1][DEFAULT_TH]
            STYLES[key][1][CUSTOM_TH] = style
            styles_file.write(f'\n{key} = {style}')


# Загрузить одну тему
def upload_one_theme(theme_path: str, theme_name: str) -> int:
    styles_path = os.path.join(theme_path, STYLES_FN)
    with open(styles_path, 'r', encoding='utf-8') as styles_file:
        theme_version = styles_file.readline().strip()  # Версия темы
        theme_version = int(re.split(' |//', theme_version)[0])  # После // идут комментарии
        to_update = styles_file.readline().strip()  # Переменная обновлений
    if theme_version != REQUIRED_THEME_VERSION:  # Проверка версии темы
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
        # Далее устанавливаем заданные значения
        while True:
            line = styles_file.readline().strip()
            data = [v for v in re.split(' |=|//', line) if v != '']  # После // идут комментарии
            if not data:  # Если настройки стилей закончились, выходим из цикла
                break
            key = data[0].strip()
            if key not in STYLES:  # Если считанный ключ отсутствует в текущей версии тем, то пропускаем его
                continue
            val = data[1].strip()
            STYLES[key][1][theme_name] = val  # Добавляем новый стиль для элемента
    return RET_TH_OK


# Загрузить дополнительные темы
def upload_themes(themes: list[str]):
    for dirname in os.listdir(ADDITIONAL_THEMES_PATH):
        theme_dir_path = os.path.join(ADDITIONAL_THEMES_PATH, dirname)
        if not os.path.isdir(theme_dir_path):
            continue
        if STYLES_FN not in os.listdir(theme_dir_path):
            continue

        theme_name = dirname
        print(f'Загрузка темы "{theme_name}". ', end='')
        try:
            ret = upload_one_theme(theme_dir_path, theme_name)
        except Exception as exc:
            print(f'Ошибка: {exc}')
        else:
            if ret == RET_TH_OK:
                print(f'Тема успешно загружена')
                if theme_name not in themes:  # Добавляем название новой темы
                    themes += [theme_name]
            elif ret == RET_TH_OLD:
                print(f'Не удалось загрузить тему, т. к. её версия не соответствует требуемой!'
                      f' Актуальные темы можно загрузить здесь: {URL_RELEASES}')


# Загрузить пользовательскую тему
def upload_custom_theme(to_print: bool = True):
    if STYLES_FN not in os.listdir(CUSTOM_THEME_PATH):
        create_default_custom_theme()
        return

    print(f'Загрузка пользовательской темы. ', end='')
    try:
        ret = upload_one_theme(CUSTOM_THEME_PATH, CUSTOM_TH)
    except Exception as exc:
        print(f'Ошибка: {exc}')
    else:
        if ret == RET_TH_OK and to_print:
            print(f'Тема успешно загружена')
        elif ret == RET_TH_OLD:
            print(f'Не удалось загрузить тему, т. к. её версия не соответствует требуемой!')


# Загрузить изображения для выбранной темы
def upload_theme_img(theme: str):
    global img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group, \
        img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page, \
        img_select_all, img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left, \
        img_arrow_right, img_double_arrow_left, img_double_arrow_right, img_trashcan

    if theme == CUSTOM_TH:
        theme_dir = CUSTOM_THEME_PATH
    else:
        theme_dir = os.path.join(ADDITIONAL_THEMES_PATH, theme)

    images = [
        img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group,
        img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page,
        img_select_all, img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left,
        img_arrow_right, img_double_arrow_left, img_double_arrow_right, img_trashcan,
    ]

    for i in range(len(images)):
        file_name = f'{IMG_NAMES[i]}.png'
        if file_name in os.listdir(theme_dir):
            images[i] = os.path.join(theme_dir, file_name)
        else:
            images[i] = os.path.join(IMAGES_PATH, file_name)

    img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group, \
        img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page, \
        img_select_all, img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left, \
        img_arrow_right, img_double_arrow_left, img_double_arrow_right, img_trashcan = images


# Загрузить глобальные настройки (настройки программы)
def upload_global_settings():
    try:  # Открываем файл с настройками программы
        open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
            global_settings_file.write(
                f'v{GLOBAL_SETTINGS_VERSION}\n'
                f'\n'
                f'dct\n'
                f'1\n'
                f'0\n'
                f'{DEFAULT_TH}\n'
                f'{SCALE_DEF}'
            )
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
        to_show_updates = int(global_settings_file.readline().strip())
        # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        typo = int(global_settings_file.readline().strip())
        # Установленная тема
        theme = global_settings_file.readline().strip()
        if theme not in THEMES:
            theme = DEFAULT_TH
        # Размер шрифта
        fontsize = int(global_settings_file.readline().strip())

    if is_res_upgrade_required:  # Если требуется обновление ресурсов
        # Обновляем
        upgrade_resources()
        # Указываем в глобальных настройках, что обновление больше не требуется
        save_global_settings(dct_savename, to_show_updates, typo, theme, fontsize)

    return dct_savename, to_show_updates, typo, theme, fontsize


# Сохранить глобальные настройки (настройки программы)
def save_global_settings(
        dct_savename: str,
        to_show_updates: int,
        typo: int,
        theme: str,
        fontsize: int,
):
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write(
            f'v{GLOBAL_SETTINGS_VERSION}\n'
            f'\n'
            f'{dct_savename}\n'
            f'{to_show_updates}\n'
            f'{typo}\n'
            f'{theme}\n'
            f'{fontsize}'
        )


# Сохранить название открытого словаря
def save_dct_name():
    _, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize = upload_global_settings()
    save_global_settings(_0_global_dct_savename, tmp_show_updates, tmp_typo, tmp_th, tmp_fontsize)


# Загрузить локальные настройки (настройки словаря)
def upload_local_settings(savename: str):
    local_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_SETTINGS_FN)
    try:
        open(local_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
            local_settings_file.write(DEFAULT_LOCAL_SETTINGS_FILE)
    else:
        upgrade_local_settings(local_settings_path, encode_special_combinations)

    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        # Версия локальных настроек
        local_settings_file.readline()
        # Учитывать ли регистр букв при учёбе
        check_register = int(local_settings_file.readline().strip())
        # Специальные комбинации
        special_combinations = {}
        line_special_combinations = local_settings_file.readline()
        for i in range(0, len(line_special_combinations) - 1, 3):
            opening_symbol = line_special_combinations[i]
            key_symbol = line_special_combinations[i + 1]
            value = line_special_combinations[i + 2]
            special_combinations[(opening_symbol, key_symbol)] = value
        # Грамматические категории
        categories = {}
        ctg_count = int(local_settings_file.readline().strip())
        for i in range(ctg_count):
            ctg_name = local_settings_file.readline().strip('\n')
            val_count = int(local_settings_file.readline().strip())
            values = []
            for j in range(val_count):
                values += [local_settings_file.readline().strip('\n')]
            categories[ctg_name] = values
        # Группы
        groups = []
        fav_groups = []
        gr_count = int(local_settings_file.readline().strip())
        for i in range(gr_count):
            line = local_settings_file.readline().strip('\n')
            group = line[1:]
            groups += [group]
            if line[0] == '1':
                fav_groups += [group]
    return check_register, special_combinations, categories, groups, fav_groups


# Сохранить локальные настройки (настройки словаря)
def save_local_settings(
        check_register: int,
        special_combinations: dict[tuple[str, str], str],
        categories: dict[str, list[str]],
        groups: list[str],
        fav_groups: list[str],
        savename: str,
):
    local_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_SETTINGS_FN)
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write(f'v{LOCAL_SETTINGS_VERSION}\n')  # Версия
        # Проверять ли регистр букв при учёбе
        local_settings_file.write(f'{check_register}\n')
        # Специальные комбинации
        for key in special_combinations:
            val = special_combinations[key]
            local_settings_file.write(f'{key[0]}{key[1]}{val}')
        local_settings_file.write('\n')
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
            if group in fav_groups:
                local_settings_file.write(f'1{group}\n')
            else:
                local_settings_file.write(f'0{group}\n')


# Загрузить автосохраняемые локальные настройки (настройки словаря)
def upload_local_auto_settings(savename: str):
    local_auto_settings_path = os.path.join(SAVES_PATH, savename, LOCAL_AUTO_SETTINGS_FN)
    try:
        open(local_auto_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_auto_settings_path, 'w', encoding='utf-8') as local_auto_settings_file:
            local_auto_settings_file.write(DEFAULT_LOCAL_AUTO_SETTINGS_FILE)
    else:
        upgrade_local_auto_settings(local_auto_settings_path)

    with open(local_auto_settings_path, 'r', encoding='utf-8') as local_auto_settings_file:
        # Версия
        local_auto_settings_file.readline()
        # Номер сессии
        session_number = int(local_auto_settings_file.readline().strip())
        # Режим поиска
        search_settings = tuple(
            int(el) for el in local_auto_settings_file.readline().strip().split()
        )
        if len(search_settings) != 8:
            search_settings = (0, 0, 1, 1, 0, 0, 0, 0)
        # Режим учёбы
        learn_settings = [int(el) for el in local_auto_settings_file.readline().strip().split()]
        if len(learn_settings) != 5:
            learn_settings = [0, 0, 1, 1, 1]

    # Увеличиваем счётчик сессий на 1 и сохраняем изменение
    session_number += 1
    save_local_auto_settings(session_number, search_settings, learn_settings, savename)

    # Возвращаем результат
    return session_number, search_settings, learn_settings


# Сохранить автосохраняемые локальные настройки (настройки словаря)
def save_local_auto_settings(
        session_number: int,
        search_settings: tuple[int, int, int, int, int, int, int, int],
        learn_settings: list[int, int, int, int, int],
        savename: str,
):
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
def save_settings_if_has_changes(window_parent, dct: Dictionary):
    window_dia = PopupDialogueW(window_parent, 'Хотите сохранить изменения настроек?', 'Да', 'Нет')
    answer = window_dia.open()
    if answer:
        save_global_settings(
            _0_global_dct_savename, _0_global_show_updates,
            _0_global_with_typo, th, _0_global_scale,
        )
        save_local_settings(
            _0_global_check_register, _0_global_special_combinations, dct.features,
            dct.groups, _0_global_fav_groups, _0_global_dct_savename,
        )
        save_local_auto_settings(
            _0_global_session_number, _0_global_search_settings,
            _0_global_learn_settings, _0_global_dct_savename,
        )
        PopupMsgW(window_parent, 'Настройки успешно сохранены').open()
        print('\nНастройки успешно сохранены')


# Создать и загрузить пустой словарь
def create_dct(savename: str):
    folder_path = os.path.join(SAVES_PATH, savename)
    os.mkdir(folder_path)
    filepath = os.path.join(folder_path, DICTIONARY_SAVE_FN)
    dct = Dictionary()
    save_data = dct.to_json_dict()
    with open(filepath, 'w') as f:
        json.dump(save_data, f)
    return dct


# Сохранить словарь
def save_dct(dct: Dictionary, savename: str):
    filepath = os.path.join(SAVES_PATH, savename, DICTIONARY_SAVE_FN)
    save_data = dct.to_json_dict()
    with open(filepath, 'w') as f:
        json.dump(save_data, f)


# Предложить сохранение словаря, если есть изменения
def save_dct_if_has_progress(window_parent, dct: Dictionary, savename: str):
    if not dct.is_saved:
        window_dia = PopupDialogueW(window_parent, 'Хотите сохранить свой прогресс?', 'Да', 'Нет')
        answer = window_dia.open()
        if answer:
            save_dct(dct, savename)
            PopupMsgW(window_parent, 'Прогресс успешно сохранён').open()
            print('\nПрогресс успешно сохранён')


# Загрузить сохранение
def upload_save(window_parent, dct: Dictionary, savename: str, btn_close_text: str):
    save_file_path = os.path.join(SAVES_PATH, savename, DICTIONARY_SAVE_FN)
    try:
        check_register, special_combinations, dct._features, dct._groups, fav_groups =\
            upload_local_settings(savename)
        #upgrade_dct_save(save_file_path, lambda line: encode_special_combinations(line, special_combinations))  # Если требуется, сохранение обновляется  # TODO
        with open(save_file_path, 'r') as f:
            save_data = json.load(f)
        dct.load_from_json_dict(save_data)  # Загрузка словаря
    except FileNotFoundError:  # Если сохранение не найдено, то создаётся пустой словарь
        print(f'\nСловарь "{savename}" не найден!')
        dct = create_dct(savename)
        check_register, special_combinations, dct._features, dct._groups, fav_groups =\
            upload_local_settings(savename)
        print('Создан и загружен пустой словарь')
        return savename, check_register, special_combinations, fav_groups
    except Exception as exc:  # Если сохранение повреждено, то предлагается загрузить другое
        print(f'\nФайл со словарём "{savename}" повреждён или некорректен!'
              f'\n{exc}')
        while True:
            window_dia = PopupDialogueW(
                window_parent,
                f'Файл со словарём "{savename}" повреждён или некорректен!\n'
                f'Хотите открыть другой словарь?',
                'Да', btn_close_text, set_enter_on_btn='none', title='Warning',
            )
            answer = window_dia.open()
            if answer:
                window_entry = PopupEntryW(
                    window_parent,
                    'Введите название словаря\n'
                    '(если он ещё не существует, то будет создан пустой словарь)',
                    validate_function=validate_savename,
                    check_answer_function=lambda wnd, val: check_not_void(
                        wnd, val, 'Название словаря должно содержать хотя бы один символ!'
                    ),
                )
                closed, other_savename = window_entry.open()
                if closed:
                    continue
                save_dct_name()
                dct = Dictionary()
                return upload_save(window_parent, dct, other_savename, btn_close_text)
            else:
                return None
    else:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'\nСловарь "{savename}" успешно загружен')
        return savename, check_register, special_combinations, fav_groups


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
def combobox_width(values: tuple[str, ...] | list[str], min_width: int, max_width: int) -> int:
    assert min_width >= 0
    assert max_width >= 0
    assert max_width >= min_width

    max_len_of_vals = max(len(val) for val in values)
    return min(max(max_len_of_vals, min_width), max_width)


# Вычислить количество строк, необходимых для записи данного текста
# в многострочное текстовое поле при данной длине строки
def field_height(text: str, len_str: int) -> int:
    assert len_str > 0

    segments = text.split('\n')
    return sum(math.ceil(len(segment) / len_str) for segment in segments)


# Разместить окно tk.Toplevel
def toplevel_geometry(window_parent, window):
    window.geometry(f'+{window_parent.winfo_x() + 20}+{window_parent.winfo_y() + 20}')


# Привязать функцию к нажатию клавиши
def bind_keypress(event, keys_and_cmd: list[tuple[str, any]], is_latin: bool = True):
    for (key, cmd) in keys_and_cmd:
        if event.keycode == ord(key):
            if is_latin or event.keysym.lower() != key.lower():
                cmd()


def bind_ctrl_a(widget):
    assert isinstance(widget, (tk.Entry, ttk.Entry))

    def handler(event=None):
        widget.select_range(0, 'end')
        widget.icursor('end')
        return 'break'

    widget.bind('<Control-a>', handler, add='+')
    widget.bind('<Control-A>', handler, add='+')


# Вывести сообщение с предупреждением
def warning(window_parent, app_data: AppData, msg: str):
    PopupMsgW(window_parent, app_data, msg, tab=0, title='Warning').open()


# Выключить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


# Включить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_enable(btn: ttk.Button, command, style='Default'):
    btn.configure(command=command, style=f'{style}.TButton')


# Установить изображение на кнопку
# Если изображение отсутствует, его замещает текст
def set_image(
        btn: ttk.Button,
        img: tk.PhotoImage,
        img_name: str,
        text_if_no_img: str,
        compound: CompoundValues = 'image',
):
    # TODO: remove try-except
    try:
        img.configure(file=img_name)
    except:
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
        params['font'] = ('StdFont', font.gui_settings.scale)
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
        params['font'] = ('StdFont', font.gui_settings.scale)
    return _create_widget(ttk.Combobox, **params)


""" Графический интерфейс - функции валидации """


# Ввод только целых чисел от 0 до max_val
def validate_int_min_max(value: str, min_val: int, max_val: int) -> bool:
    return value == '' or value.isnumeric() and min_val <= int(value) <= max_val


# Валидация открывающего символа специальной комбинации
def validate_special_combination_opening_symbol(value: str) -> bool:
    return value == '' or value in SPECIAL_COMBINATIONS_OPENING_SYMBOLS


# Валидация ключевого символа специальной комбинации
def validate_special_combination_key_symbol(value: str) -> bool:
    return len(value) <= 1 and value not in SPECIAL_COMBINATIONS_OPENING_SYMBOLS


# Валидация значения специальной комбинации
def validate_special_combination_val(value: str) -> bool:
    return len(value) <= 1


# Валидация названия словаря
def validate_savename(value: str) -> bool:
    if len(value) > 99:
        return False
    for symbol in value:
        if symbol in '/|\\<>:*"?':
            return False
    return True


""" Графический интерфейс - виджеты """


# Прокручиваемый фрейм
class ScrollFrame(tk.Frame):
    def __init__(
            self,
            parent,
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
            self, bg=STYLES['FLAT_BTN.BG.2'][1][self.app_data.gui_settings.theme],
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
        # Когда размер фрейма изменяется, соответственно изменяется и область прокрутки
        self.frame_canvas.bind('<Configure>', self.on_frame_configure)
        # Когда размер холста изменяется, соответственно изменяется и область окна
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Привязать колёсико мышки, когда курсор попадает на элемент управления
        self.frame_canvas.bind('<Enter>', self.on_enter)
        # Отвязать колёсико мышки, когда курсор покидает элемент управления
        self.frame_canvas.bind('<Leave>', self.on_leave)

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
    def __init__(
            self,
            parent,
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

        self.closed = True  # Закрыто ли окно крестиком

        self._configure_window(title)
        self._create_widgets(msg, btn_text, msg_max_width, tab, msg_justify)

    def _configure_window(self, title):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
            self, self.ok, btn_text,
            row=1, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            msg: str = 'Вы уверены?',
            btn_left_text: str = 'Да',
            btn_right_text: str = 'Отмена',
            st_left: Literal['Default', 'Yes', 'No'] = 'Yes',
            st_right: Literal['Default', 'Yes', 'No'] = 'No',  # Стили левой и правой кнопок
            val_left: Any = True,  # Значение, возвращаемое при нажатии на левую кнопку
            val_right: Any = False,  # Значение, возвращаемое при нажатии на правую кнопку
            val_on_close: Any = False,  # Значение, возвращаемое при закрытии окна крестиком
            set_enter_on_btn: Literal['left', 'right', 'none'] = 'left',  # Какая кнопка срабатывает при нажатии кнопки enter
            title: str = PROGRAM_NAME,
    ):
        ALLOWED_ST_VALUES = ['Default', 'Yes', 'No']  # Проверка корректности параметров
        assert st_left in ALLOWED_ST_VALUES, f'Bad value: st_left\n' \
                                             f'Allowed values: {ALLOWED_ST_VALUES}'
        assert st_right in ALLOWED_ST_VALUES, f'Bad value: st_right\n' \
                                              f'Allowed values: {ALLOWED_ST_VALUES}'
        ALLOWED_FOCUS_VALUES = ['left', 'right', 'none']  # Проверка корректности параметров
        assert set_enter_on_btn in ALLOWED_FOCUS_VALUES, f'Bad value: set_enter_on_btn\n' \
                                                         f'Allowed values: {ALLOWED_FOCUS_VALUES}'

        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.set_enter_on_btn = set_enter_on_btn
        self.answer = val_on_close  # Значение, возвращаемое методом self.open
        self.val_left = val_left
        self.val_right = val_right

        self.st_left = f'{st_left}.TButton'
        self.st_right = f'{st_right}.TButton'

        self._configure_window(title)
        self._create_widgets(msg, btn_left_text, btn_right_text)

    def _configure_window(self, title):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, msg: str, btn_left_text: str, btn_right_text: str):
        self.lbl_msg = create_label(
            self, split_text(msg, 45, to_add_right_spaces=False),
            justify='center',
            row=0, columnspan=2, padx=6, pady=4)
        self.btn_left = create_button(
            self, self.left, btn_left_text, style=self.st_left,
            row=1, column=0, padx=(6, 10), pady=4, sticky='E')
        self.btn_right = create_button(
            self, self.right, btn_right_text, style=self.st_right,
            row=1, column=1, padx=(10, 6), pady=4, sticky='W')

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
            self.bind('<Return>', lambda event: self.btn_left.invoke())
            self.bind('<Escape>', lambda event: self.btn_right.invoke())
        elif self.set_enter_on_btn == 'right':
            self.bind('<Return>', lambda event: self.btn_right.invoke())
            self.bind('<Escape>', lambda event: self.btn_left.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Всплывающее окно с полем ввода
class PopupEntryW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            msg: str = 'Введите строку',
            btn_text: str = 'Подтвердить',
            entry_width: int = 45,
            default_value: str | None = '',
            validate_function: Any = None,
            check_answer_function: Any = None,
            if_correct_function: Any = None,
            if_incorrect_function: Any = None,
            title: str = PROGRAM_NAME,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.check_answer_function = check_answer_function  # Функция, проверяющая корректность ответа
        self.if_correct_function = if_correct_function  # Функция, вызываемая при корректном ответе
        self.if_incorrect_function = if_incorrect_function  # Функция, вызываемая при некорректном ответе
        self.closed = True  # Закрыто ли окно крестиком

        self.var_text = tk.StringVar(value=default_value)

        self._configure_window(title)
        self._create_widgets(msg, btn_text, entry_width)

        if validate_function:
            self.vcmd = (self.register(validate_function), '%P')
            self.entry_inp.configure(validate='key', validatecommand=self.vcmd)

        self.entry_inp.icursor(len(default_value))

    def _configure_window(self, title):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, msg: str, btn_text: str, entry_width: int):
        self.lbl_msg = create_label(
            self, split_text(f'{msg}:', 45, to_add_right_spaces=False),
            justify='center',
            row=0, padx=6, pady=(6, 3))
        self.entry_inp = create_entry(
            self, self.var_text, entry_width, font=self.app_data,
            row=1, padx=6, pady=(0, 6))
        self.btn_ok = create_button(
            self, self.ok, btn_text, style='Yes.TButton',
            row=2, padx=6, pady=(0, 6))

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

        bind_ctrl_a(self.entry_inp)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_text.get()


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(
            self,
            parent,
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

        self.closed = True  # Закрыто ли окно крестиком

        self.var_answer = tk.StringVar(value=default_value)

        self._configure_window(title)
        self._create_widgets(msg, values, combo_width, btn_text)

    def _configure_window(self, title):
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
        self.combo_vals = create_combobox(
            self, self.var_answer, values, combo_width, state='readonly',
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            row=1, padx=6, pady=1)
        self.btn_ok = create_button(
            self, self.ok, btn_text, style='Yes.TButton',
            row=2, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_answer.get()


# Всплывающее окно с изображением
class PopupImgW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            img_name: str,
            msg: str,
            btn_text: str = 'Ясно',
            title: str = PROGRAM_NAME,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.closed = True  # Закрыто ли окно крестиком

        self._configure_window(title)
        self._create_widgets(img_name, msg, btn_text)

    def _configure_window(self, title):
        self.title(title)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
            self, self.ok, btn_text,
            row=3, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed


""" Графический интерфейс - второстепенные окна """


# Окно выбора режима перед изучением слов
class ChooseLearnModeW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_info = app_data.manager.dct_info
        self.dct = app_data.manager.dct_info.dct
        self.train_config = app_data.manager.active.cache.train_config

        self.res: tuple[str, str, str, str, str] | None = None
        self.group_vals = [ALL_GROUPS] + self.dct.groups

        # Метод учёбы
        self.var_method = tk.StringVar(
            value=LEARN_VALUES_METHOD[self.train_config[0]]
        )
        # Группа слов
        self.var_group = tk.StringVar(
            value=self.group_vals[self.train_config[1]]
        )
        # Способ набора слов
        self.var_words = tk.StringVar(
            value=LEARN_VALUES_WORDS[self.train_config[2]]
        )
        # Способ набора словоформ
        self.var_forms = tk.StringVar(
            value=LEARN_VALUES_FORMS[self.train_config[3]]
        )
        # Порядок следования слов
        self.var_order = tk.StringVar(
            value=LEARN_VALUES_ORDER[self.train_config[4]]
        )

        self._configure_window()
        self._create_widgets()
        self._add_validation()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Выбор режима')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_header = create_label(
            self, 'Выберите способ учёбы',
            row=0, column=0, padx=6, pady=(6, 3))
        self._create_main_frame()
        self.btn_start = create_button(
            self, self.start, 'Учить',
            row=2, column=0, padx=6, pady=(0, 6))

    def _create_main_frame(self):
        self.frame_main = create_frame(self, row=1, column=0, padx=6, pady=(0, 3))

        self.lbl_method = create_label(
            self.frame_main, 'Метод:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.combo_method = create_combobox(
            self.frame_main, self.var_method, LEARN_VALUES_METHOD, 30,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly', validate='focusin',
            row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_group = create_label(
            self.frame_main, 'Группа:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_group = create_combobox(
            self.frame_main, self.var_group, self.group_vals, 30,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_words = create_label(
            self.frame_main, 'Набор статей:',
            row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_words = create_combobox(
            self.frame_main, self.var_words, LEARN_VALUES_WORDS, 30,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_forms = create_label(
            self.frame_main, 'Набор словоформ:',
            row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_forms = create_combobox(
            self.frame_main, self.var_forms, LEARN_VALUES_FORMS, 30,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=3, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_order = create_label(
            self.frame_main, 'Порядок заданий:',
            row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.combo_order = create_combobox(
            self.frame_main, self.var_order, LEARN_VALUES_ORDER, 30,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')

    def _add_validation(self):
        # При выборе любого метода учёбы кроме первого нельзя добавить словоформы
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
        method = self.var_method.get()
        group = self.var_group.get()
        words = self.var_words.get()
        if method == LEARN_VALUES_METHOD[0]:
            forms = self.var_forms.get()
        else:
            forms = LEARN_VALUES_FORMS[0]
        order = self.var_order.get()
        self.res = (method, group, words, forms, order)
        learn_settings = [
            LEARN_VALUES_METHOD.index(method),
            self.group_vals.index(group),
            LEARN_VALUES_WORDS.index(words),
            LEARN_VALUES_FORMS.index(forms),
            LEARN_VALUES_ORDER.index(order),
        ]

        save_local_auto_settings(
            self.dct_info.cache.session_number, self.dct_info.cache.search_config,
            learn_settings, self.dct_info.dct.name,
        )

        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_start.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return create_training_config(
            method={
                'Угадывать слово по переводу': TrainingMethod.TRANS_TO_WORD,
                'Угадывать перевод по слову': TrainingMethod.WORD_TO_TRANS,
                'Угадывать фразу по переводу': TrainingMethod.TRANS_TO_PHRASE,
                'Угадывать перевод по фразе': TrainingMethod.PHRASE_TO_TRANS,
                'Der-Die-Das (для немецкого)': TrainingMethod.ARTICLES_GERMAN,
            }[self.res[0]],
            groups=None if self.res[1] == ALL_GROUPS else [self.res[1]],
            entries={
                'Все': EntrySelection.ALL,
                'Преимущ. избранные (рекоменд.)': EntrySelection.MOSTLY_FAV,
                'Только избранные': EntrySelection.FAV,
                'Только неотвеченные': EntrySelection.UNANSWERED,
                '10 случайных': EntrySelection.RANDOM_10,
                '10 случайных из избранных': EntrySelection.RANDOM_10_FAV,
            }[self.res[2]],
            forms={
                'Только начальная форма': FormSelection.LEMMAS,
                'По одной случайной словоформе': FormSelection.RANDOM,
                'Все формы, кроме начальной': FormSelection.INFLECTED,
                'Все словоформы': FormSelection.ALL,
            }[self.res[3]],
            order={
                'Случайный порядок': TrainingOrder.RANDOM,
                'В первую очередь сложные': TrainingOrder.DIFFICULT_FIRST,
            }[self.res[4]],
        )


# Окно с сообщением о неверном ответе (для слов, не находящихся в избранном)
class IncorrectAnswerW(tk.Toplevel):
    def __init__(
            self,
            parent,
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
        self.answer = 'no'  # Значение, возвращаемое методом self.open

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Неверно')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
        self.btn_yes = create_button(self, self.yes, 'Да', style='Yes.TButton')
        self.btn_no = create_button(self, self.no, 'Нет', style='No.TButton')
        self.btn_typo = create_button(self, self.typo, 'Просто опечатка')

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

        self.bind('<Return>', lambda event: self.btn_yes.invoke())
        self.bind('<Escape>', lambda event: self.btn_no.invoke())
        if self.with_typo:
            self.bind('<Tab>', lambda event: self.btn_typo.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Окно с параметрами поиска
class SearchSettingsW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            to_search_only_fav: bool,
            to_search_only_full: bool,
            to_search_wrd: bool,
            to_search_tr: bool,
            to_search_frm: bool,
            to_search_phr: bool,
            to_search_nt: bool,
            search_group: str,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_info = app_data.manager.active

        self.group_vals = [ALL_GROUPS] + self.dct_info.dct.groups

        self.var_search_only_fav = tk.BooleanVar(value=to_search_only_fav)
        self.var_search_only_full = tk.BooleanVar(value=to_search_only_full)
        self.var_search_wrd = tk.BooleanVar(value=to_search_wrd)
        self.var_search_tr = tk.BooleanVar(value=to_search_tr)
        self.var_search_frm = tk.BooleanVar(value=to_search_frm)
        self.var_search_phr = tk.BooleanVar(value=to_search_phr)
        self.var_search_nt = tk.BooleanVar(value=to_search_nt)
        self.var_search_group = tk.StringVar(value=search_group)

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Параметры поиска')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
        self._create_group_frame()

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

    def _create_group_frame(self):
        self.frame_group = create_frame(
            self, 'Invis.TFrame',
            row=3, column=0, columnspan=2, padx=6, pady=6)

        self.lbl_search_group = create_label(
            self.frame_group, 'Группа:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.combo_search_group = create_combobox(
            self.frame_group, self.var_search_group,
            [ALL_GROUPS] + self.dct_info.dct.groups, 26,
            state='readonly',
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        self.dct_info.cache.train_config = [
            int(self.var_search_only_fav.get()),
            int(self.var_search_only_full.get()),
            int(self.var_search_wrd.get()),
            int(self.var_search_tr.get()),
            int(self.var_search_frm.get()),
            int(self.var_search_phr.get()),
            int(self.var_search_nt.get()),
            self.group_vals.index(self.var_search_group.get()),
        ]
        save_local_auto_settings(
            self.dct_info.cache.session_number, self.dct_info.cache.search_config,
            self.dct_info.cache.train_config, self.dct_info.dct.name,
        )

        return self.var_search_only_fav.get(), self.var_search_only_full.get(), \
            self.var_search_wrd.get(), self.var_search_tr.get(), self.var_search_frm.get(), \
            self.var_search_phr.get(), self.var_search_nt.get(), self.var_search_group.get()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseOneOfSimilarEntriesW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData, query: str):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.to_search_wrd = query
        self.answer = None

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Найдено несколько схожих статей')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_header = create_label(
            self, 'Выберите одну из статей', justify='center',
            row=0, column=0, padx=(6, 3), pady=(6, 3))
        self.scrolled_frame_wrd = ScrollFrame(
            self, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_wrd.grid(
            row=1, column=0, padx=6, pady=(0, 6))
        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

        keys = self.dct.search([('lemmas', self.to_search_wrd)])
        self.widgets_wrd = [
            create_button(
                self.scrolled_frame_wrd.frame_canvas,
                lambda key=key: self.choose_entry(key),
                get_all_entry_info(self.dct[key], 75, 13),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i, key in enumerate(keys)
        ]

    # Выбрать статью из предложенных вариантов
    def choose_entry(self, key: EntryID):
        self.answer = key
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.answer


# Окно добавления фразы
class AddPhraseW(tk.Toplevel):
    def __init__(
            self,
            parent,
            title: str,
            app_data: AppData,
            default_value: tuple[str, str] = ('', ''),
            check_answer_function: Any = None,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.closed = True  # Закрыто ли окно крестиком
        self.check_answer_function = check_answer_function  # Функция, проверяющая корректность ответа

        self.var_phr = tk.StringVar(value=default_value[0])
        self.var_tr = tk.StringVar(value=default_value[1])

        self._configure_window(title)
        self._create_widgets()
        self._create_bindings()

        self.entry_phr.icursor(len(self.var_phr.get()))

    def _configure_window(self, title):
        self.title(f'{PROGRAM_NAME} - {title}')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
            self, self.ok, 'Готово',
            row=3, columnspan=2, padx=6, pady=(0, 6))

    def _create_bindings(self):
        self.entry_phr.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_phr.focus_set())

    # Добавление фразы
    def ok(self):
        if self.check_answer_function:
            is_correct = self.check_answer_function(self, (self.var_phr.get(), self.var_tr.get()))
            if not is_correct:
                return

        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_phr.focus_set()

        bind_ctrl_a(self.entry_phr)
        bind_ctrl_a(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_phr.get(), self.var_tr.get()


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData, key: EntryID):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct
        self.dct_key = key

        self.line_width = 35
        self.max_height_w = 3
        self.max_height_t = 4
        self.max_height_f = 4
        self.max_height_p = 3
        self.max_height_n = 3
        self.max_height_g = 3

        self.var_fav = tk.BooleanVar(value=self.dct[key].is_fav)

        self.img_edit = tk.PhotoImage()
        self.img_add = tk.PhotoImage()
        self.img_about = tk.PhotoImage()

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
        self.groups = []
        self.gr_frames = []
        self.gr_buttons = []

        self._configure_window()
        self._create_widgets()

        self.refresh(True)

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Изменение статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self._create_main_frame()
        self.btn_back = create_button(
            self, self.back, 'Закончить',
            row=1, column=0, padx=(6, 0), pady=(0, 6))
        self.btn_about_window = create_button(
            self, self.about_window, width=2,
            row=1, column=1, padx=(6, 6), pady=(0, 6))
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.btn_delete = create_button(
            self, self.delete, 'Удалить статью', style='No.TButton',
            row=1, column=2, padx=(0, 6), pady=(0, 6))

        self.tip_btn_about_window = ttip.Hovertip(self.btn_about_window, 'Справка', hover_delay=450)

    def _create_main_frame(self):
        self.frame_main = create_frame(self, row=0, columnspan=3, padx=6, pady=(6, 4))

        self.lbl_wrd = create_label(
            self.frame_main, 'Слово:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.scrollbar_wrd = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.scrollbar_wrd.grid(
            row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.txt_wrd = tk.Text(
            self.frame_main, width=self.line_width,
            yscrollcommand=self.scrollbar_wrd.set, relief='solid',
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale + 1),
            bg=STYLES['*.BG.ENTRY'][1][self.app_data.gui_settings.theme],
            fg=STYLES['*.FG.*'][1][self.app_data.gui_settings.theme],
            selectbackground=STYLES['*.BG.SEL'][1][self.app_data.gui_settings.theme],
            selectforeground=STYLES['*.FG.SEL'][1][self.app_data.gui_settings.theme],
            highlightbackground=STYLES['*.BORDER_CLR.*'][1][self.app_data.gui_settings.theme])
        self.txt_wrd.grid(
            row=0, column=1, padx=(0, 1), pady=(6, 3), sticky='W')
        self.scrollbar_wrd.config(command=self.txt_wrd.yview)
        self.btn_wrd_edt = create_button(
            self.frame_main, self.wrd_edt, width=4,
            row=0, column=3, padx=(3, 6), pady=(6, 3), sticky='W')
        set_image(self.btn_wrd_edt, self.img_edit, img_edit, 'изм.')
        self.lbl_tr = create_label(
            self.frame_main, text='Перевод:',
            row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_tr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_tr.grid(
            row=1, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_tr_add = create_button(
            self.frame_main, self.tr_add, width=2,
            row=1, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_tr_add, self.img_add, img_add, '+')
        self.lbl_frm = create_label(
            self.frame_main, text='Формы слова:',
            row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_frm = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_frm.grid(
            row=2, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_frm_add = create_button(
            self.frame_main, self.frm_add, width=2,
            row=2, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_frm_add, self.img_add, img_add, '+')
        self.lbl_phrases = create_label(
            self.frame_main, 'Фразы:',
            row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_phr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_phr.grid(
            row=3, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_phrase_add = create_button(
            self.frame_main, self.phrase_add, width=2,
            row=3, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_phrase_add, self.img_add, img_add, '+')
        self.lbl_notes = create_label(
            self.frame_main, 'Сноски:',
            row=4, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_nt = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_nt.grid(
            row=4, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_note_add = create_button(
            self.frame_main, self.note_add, width=2,
            row=4, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_note_add, self.img_add, img_add, '+')
        self.lbl_gr = create_label(
            self.frame_main, 'Группы:',
            row=5, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_gr = ScrollFrame(
            self.frame_main, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_gr.grid(
            row=5, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_gr_add = create_button(
            self.frame_main, self.gr_add, width=2,
            row=5, column=3, padx=(3, 6), pady=(0, 3), sticky='W')
        set_image(self.btn_gr_add, self.img_add, img_add, '+')
        self.lbl_fav = create_label(
            self.frame_main, 'Избранное:',
            row=6, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_fav = create_checkbutton(
            self.frame_main, self.var_fav, command=self.set_fav,
            row=6, column=1, padx=(0, 6), pady=(0, 6), sticky='W')

        if self.btn_wrd_edt['style'] == 'Image.TButton':
            self.tip_btn_wrd_edt = ttip.Hovertip(
                self.btn_wrd_edt, 'Изменить слово', hover_delay=500)
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

    # Изменить слово
    def wrd_edt(self):
        window = PopupEntryW(
            self, self.app_data,
            'Введите новое слово',
            default_value=self.dct[self.dct_key].lemma,
            check_answer_function=lambda wnd, val: check_not_void(
                wnd, val, 'Слово должно содержать хотя бы один символ!'
            ),
        )
        closed, new_wrd = window.open()
        if closed:
            return
        new_wrd = encode_special_combinations(new_wrd, self.dct.input_replacements)
        if new_wrd == self.dct[self.dct_key].lemma:
            return

        new_key, has_progres = edit_wrd_with_choose(self.dct, self, self.dct_key, new_wrd)
        if not has_progres:
            return
        self.dct_key = new_key

        self.refresh(False)

    # Добавить перевод
    def tr_add(self):
        window = PopupEntryW(
            self, self.app_data,
            'Введите новый перевод',
            check_answer_function=lambda wnd, val: check_tr(
                wnd, self.dct[self.dct_key].tr, val, self.dct[self.dct_key].lemma,
            ),
        )
        closed, tr = window.open()
        if closed:
            return
        tr = encode_special_combinations(tr, self.dct.input_replacements)

        self.dct.add_tr(self.dct_key, tr)

        self.refresh(False)

    # Изменить перевод
    def tr_edt(self, tr: str):
        window = PopupEntryW(
            self, self.app_data,
            'Введите новый перевод',
            default_value=tr,
            check_answer_function=lambda wnd, val: check_tr_edit(
                wnd, self.dct[self.dct_key].tr, tr,
                val, self.dct[self.dct_key].lemma,
            ),
        )
        closed, new_tr = window.open()
        if closed:
            return
        new_tr = encode_special_combinations(new_tr, self.dct.input_replacements)

        self.dct.edit_tr(self.dct_key, tr, new_tr)

        self.refresh(False)

    # Удалить перевод
    def tr_del(self, tr: str):
        if len(self.translations) == 1:
            warning(self, self.app_data, 'Вы не можете удалить единственный перевод!')
            return

        self.dct.delete_tr(self.dct_key, tr)

        self.refresh(False)

    # Добавить словоформу
    def frm_add(self):
        if not self.dct.features:
            warning(
                self, self.app_data,
                'Отсутствуют категории слов!\n'
                'Чтобы их добавить, перейдите в\n'
                'Настройки/Настройки открытого словаря/Грамматические категории',
            )
            return

        window_form = AddFormW(
            self, self.app_data, self.dct_key,
            combo_width=combobox_width(tuple(self.dct.features.keys()), 5, 100),
        )  # Создание словоформы
        frm_key, frm = window_form.open()
        if not frm_key:
            return
        frm = encode_special_combinations(frm, self.dct.input_replacements)

        self.dct.add_form(self.dct_key, frm_key, frm)

        self.refresh(False)

    # Изменить словоформу
    def frm_edt(self, form: tuple[GramForm, WordForm]):
        gram_form, word_form = form

        window_form = AddFormW(
            self, self.app_data, self.dct_key, word_form, list(gram_form),
            combo_width=combobox_width(tuple(self.dct.features.keys()), 5, 100),
        )  # Создание словоформы
        new_gram_form, new_word_form = window_form.open()
        if not new_gram_form:
            return
        new_frm = encode_special_combinations(new_frm, self.dct.input_replacements)

        self.dct.edit_form(self.dct_key, gram_form, word_form, new_gram_form, new_word_form)

        self.refresh(False)

    # Удалить словоформу
    def frm_del(self, frm_key: GramForm):
        self.dct.delete_form(self.dct_key, frm_key)

        self.refresh(False)

    # Добавить фразу
    def phrase_add(self):
        window = AddPhraseW(
            self, 'Добавление фразы', self.app_data,
            check_answer_function=lambda wnd, val: check_phr(
                wnd, self.dct[self.dct_key].phrases,
                val, self.dct[self.dct_key].lemma,
            ),
        )
        closed, phr, phr_tr = window.open()
        if closed:
            return
        phr = encode_special_combinations(phr, self.dct.input_replacements)
        phr_tr = encode_special_combinations(phr_tr, self.dct.input_replacements)

        self.dct.add_phrase(self.dct_key, phr, phr_tr)

        self.refresh(False)

    # Изменить фразу
    def phrase_edt(self, p: tuple[str, str]):
        phr, phr_tr = p

        window = AddPhraseW(
            self, 'Изменение фразы', self.app_data,
            default_value=(phr, phr_tr),
            check_answer_function=lambda wnd, val: check_phr_edit(
                wnd, self.dct[self.dct_key].phrases, (phr, phr_tr),
                val, self.dct[self.dct_key].lemma,
            ),
        )
        closed, new_phr, new_phr_tr = window.open()
        if closed:
            return
        new_phr = encode_special_combinations(new_phr, self.dct.input_replacements)
        new_phr_tr = encode_special_combinations(new_phr_tr, self.dct.input_replacements)

        self.dct.edit_phrase(self.dct_key, phr, phr_tr, new_phr, new_phr_tr)

        self.refresh(False)

    # Удалить фразу
    def phrase_del(self, p: tuple[str, str]):
        phr, phr_tr = p
        self.dct.delete_phrase(self.dct_key, phr, phr_tr)

        self.refresh(False)

    # Добавить сноску
    def note_add(self):
        window = PopupEntryW(
            self, self.app_data,
            'Введите сноску',
            check_answer_function=lambda wnd, val: check_note(
                wnd, self.dct[self.dct_key].notes,
                val, self.dct[self.dct_key].lemma,
            ),
        )
        closed, note = window.open()
        if closed:
            return
        note = encode_special_combinations(note, self.dct.input_replacements)

        self.dct.add_note(self.dct_key, note)

        self.refresh(False)

    # Изменить сноску
    def note_edt(self, note: str):
        window = PopupEntryW(
            self, self.app_data,
            'Введите сноску',
            default_value=note,
            check_answer_function=lambda wnd, val: check_note_edit(
                wnd, self.dct[self.dct_key].notes, note, val, self.dct[self.dct_key].lemma
            ),
        )
        closed, new_note = window.open()
        if closed:
            return
        new_note = encode_special_combinations(new_note, self.dct.input_replacements)

        self.dct.edit_note(self.dct_key, note, new_note)

        self.refresh(False)

    # Удалить сноску
    def note_del(self, note: str):
        self.dct.delete_note(self.dct_key, note)

        self.refresh(False)

    # Добавить группу
    def gr_add(self):
        if not self.dct.groups:
            warning(
                self, self.app_data,
                'Отсутствуют группы!\n'
                'Чтобы их добавить, перейдите в\n'
                'Настройки/Настройки открытого словаря/Группы',
            )
            return
        values = [group for group in self.dct.groups if group not in self.dct[self.dct_key].groups]
        if not values:
            warning(self, self.app_data, 'Статья уже добавлена во все группы')
            return

        window_group = PopupChooseW(
            self, self.app_data, values,
            'Выберите группу',
            default_value=values[0],
        )
        closed, group = window_group.open()
        if closed:
            return
        group = encode_special_combinations(group, self.dct.input_replacements)

        self.dct.add_entries_to_group(group, [self.dct_key])

        self.refresh(False)

    # Удалить группу
    def gr_del(self, group: str):
        self.dct.remove_entries_from_group(group, [self.dct_key])

        self.refresh(False)

    # Добавить в избранное/убрать из избранного
    def set_fav(self):
        self.dct[self.dct_key].is_fav = self.var_fav.get()

    # Удалить статью
    def delete(self):
        window = PopupDialogueW(
            self, self.app_data,
            'Вы уверены, что хотите удалить эту статью?',
            set_enter_on_btn='none',
        )
        answer = window.open()
        if answer:
            self.dct.delete_entry(self.dct_key)
            self.destroy()

    # Закрыть окно
    def back(self):
        self.destroy()

    # Обновить поля
    def refresh(self, move_scroll: bool):
        # Обновляем поле со словом
        self.txt_wrd['state'] = 'normal'
        self.txt_wrd.delete(1.0, tk.END)
        self.txt_wrd.insert(tk.END, self.dct[self.dct_key].lemma)
        self.txt_wrd['state'] = 'disabled'

        height_w = max(
            min(
                field_height(self.dct[self.dct_key].lemma, self.line_width),
                self.max_height_w
            ), 1
        )
        self.txt_wrd['height'] = height_w

        if height_w < self.max_height_w:
            self.scrollbar_wrd.grid_remove()
        else:
            self.scrollbar_wrd.grid(row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')

        # Удаляем старые кнопки
        for btn in (
                self.tr_buttons + self.nt_buttons + self.phr_buttons +
                self.frm_buttons + self.gr_buttons
        ):
            btn.destroy()
        # Удаляем старые фреймы
        for fr in (
                self.tr_frames + self.nt_frames + self.phr_frames +
                self.frm_frames + self.gr_frames
        ):
            fr.unbind('<Enter>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        # Выбираем содержимое
        self.translations = [tr for tr in self.dct[self.dct_key].tr]
        self.notes = [nt for nt in self.dct[self.dct_key].notes]
        self.phrases = []
        for phr in self.dct[self.dct_key].phrases.keys():
            for pt in self.dct[self.dct_key].phrases[phr]:
                self.phrases += [(phr, pt)]
        self.forms = [frm for frm in self.dct[self.dct_key].forms.keys()]
        self.groups = [gr for gr in self.dct[self.dct_key].groups]
        tr_count = len(self.translations)
        nt_count = len(self.notes)
        phr_count = len(self.phrases)
        frm_count = len(self.forms)
        gr_count = len(self.groups)

        # Создаём новые фреймы
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
        self.tr_buttons = [
            create_button(
                self.tr_frames[i],
                lambda i=i: self.tr_edt(self.translations[i]),
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
                lambda i=i: self.note_edt(self.notes[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(nt_count)
        ]
        for i in range(nt_count):
            nt = self.notes[i]
            self.nt_buttons[i].configure(text=split_text(nt, 35))

        self.phr_buttons = [
            create_button(
                self.phr_frames[i],
                lambda i=i: self.phrase_edt(self.phrases[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(phr_count)
        ]
        for i in range(phr_count):
            phr = self.phrases[i][0]
            phr_tr = self.phrases[i][1]
            self.phr_buttons[i].configure(text=split_text(f'{phr} - {phr_tr}', 35))

        self.frm_buttons = [
            create_button(
                self.frm_frames[i],
                lambda i=i: self.frm_edt(self.forms[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(frm_count)
        ]
        for i in range(frm_count):
            frm = self.forms[i]
            text = f'[{gram_form_to_str(frm)}] {self.dct[self.dct_key].forms[frm]}'
            self.frm_buttons[i].configure(text=split_text(text, 35))

        self.gr_buttons = [
            create_button(
                self.gr_frames[i],
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(gr_count)
        ]
        for i in range(gr_count):
            gr = self.groups[i]
            self.gr_buttons[i].configure(text=split_text(gr, 35))

        # Привязываем события
        for i in range(tr_count):
            self.tr_frames[i].bind('<Enter>', lambda event, i=i: self.tr_frames[i].focus_set())
            self.tr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.tr_frames[i].bind('<Control-d>', lambda event, i=i: self.tr_del(self.translations[i]))
            self.tr_frames[i].bind('<Control-D>', lambda event, i=i: self.tr_del(self.translations[i]))
        for i in range(nt_count):
            self.nt_frames[i].bind('<Enter>', lambda event, i=i: self.nt_frames[i].focus_set())
            self.nt_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.nt_frames[i].bind('<Control-d>', lambda event, i=i: self.note_del(self.notes[i]))
            self.nt_frames[i].bind('<Control-D>', lambda event, i=i: self.note_del(self.notes[i]))
        for i in range(phr_count):
            self.phr_frames[i].bind('<Enter>', lambda event, i=i: self.phr_frames[i].focus_set())
            self.phr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.phr_frames[i].bind('<Control-d>', lambda event, i=i: self.phrase_del(self.phrases[i]))
            self.phr_frames[i].bind('<Control-D>', lambda event, i=i: self.phrase_del(self.phrases[i]))
        for i in range(frm_count):
            self.frm_frames[i].bind('<Enter>', lambda event, i=i: self.frm_frames[i].focus_set())
            self.frm_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frm_frames[i].bind('<Control-d>', lambda event, i=i: self.frm_del(self.forms[i]))
            self.frm_frames[i].bind('<Control-D>', lambda event, i=i: self.frm_del(self.forms[i]))
        for i in range(gr_count):
            self.gr_frames[i].bind('<Enter>', lambda event, i=i: self.gr_frames[i].focus_set())
            self.gr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.gr_frames[i].bind('<Control-d>', lambda event, i=i: self.gr_del(self.groups[i]))
            self.gr_frames[i].bind('<Control-D>', lambda event, i=i: self.gr_del(self.groups[i]))

        # Изменяем высоту полей
        self.scrolled_frame_tr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.tr_buttons
            ]), self.max_height_t)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.gui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_nt.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.nt_buttons
            ]), self.max_height_n)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.gui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_phr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.phr_buttons
            ]), self.max_height_p)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.gui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_frm.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.frm_buttons
            ]), self.max_height_f)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.gui_settings.scale - SCALE_MIN]
        )
        self.scrolled_frame_gr.resize(
            height=max(1, min(sum([
                field_height(btn['text'], 35)
                for btn in self.gr_buttons
            ]), self.max_height_g)) *
            SCALE_FRAME_HEIGHT_ONE_LINE[self.app_data.gui_settings.scale - SCALE_MIN]
        )

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_tr.canvas.yview_moveto(0.0)
            self.scrolled_frame_nt.canvas.yview_moveto(0.0)
            self.scrolled_frame_phr.canvas.yview_moveto(0.0)
            self.scrolled_frame_frm.canvas.yview_moveto(0.0)
            self.scrolled_frame_gr.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(
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

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.btn_back.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


# Окно создания шаблона словоформы
class AddFormW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            key: EntryID,
            initial_value: str = '',
            template: list[str] | None = None,
            combo_width: int = 20,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct
        self.key = key

        self.closed = True  # Закрыто ли окно крестиком
        self.categories = list(self.dct.features.keys())  # Список категорий
        self.ctg_values = list(self.dct.features[self.categories[0]])  # Список значений выбранной категории
        self.void_template = ['' for _ in range(len(self.categories))]  # Пустой шаблон (для сравнения на пустоту)
        self.template = template or self.void_template  # Шаблон словоформы

        self.var_ctg = tk.StringVar(value=self.categories[0])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.var_template = tk.StringVar(
            value=f'Текущий шаблон словоформы: "{gram_form_to_str(self.template)}"'
        )
        self.var_form = tk.StringVar(value=initial_value)

        self.img_ok = tk.PhotoImage()
        self.img_none = tk.PhotoImage()

        self._configure_window()
        self._create_widgets(combo_width)

        if self.template == self.void_template:  # Пока шаблон пустой, нельзя нажать кнопку
            btn_disable(self.btn_save)

        self.entry_form.icursor(len(self.var_form.get()))

        # В combobox значением по умолчанию становится первая ещё не заданная категория
        for i in range(len(self.template)):
            if self.template[i] == '':
                self.var_ctg.set(self.categories[i])
                break
        self.refresh_vals()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self, combo_width: int):
        self.lbl_choose_ctg = create_label(
            self, 'Выберите категорию:', justify='center',
            row=0, column=0, padx=(6, 1), pady=(6, 1), sticky='E')
        self.combo_ctg = create_combobox(
            self, self.var_ctg, self.categories, combo_width,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=0, column=1, padx=(0, 6), pady=(6, 1), sticky='W')
        self.lbl_choose_val = create_label(
            self, 'Задайте значение категории:', justify='center',
            row=1, column=0, padx=(6, 1), pady=1, sticky='E')
        self._create_val_frame()
        self.lbl_template = create_label(
            self, textvariable=self.var_template, justify='center',
            row=2, columnspan=2, padx=6, pady=1)
        self._create_form_frame()
        self.btn_save = create_button(
            self, self.save, 'Готово',
            row=4, columnspan=2, padx=6, pady=6)

    def _create_val_frame(self):
        self.frame_val = create_frame(
            self, 'Invis.TFrame',
            row=1, column=1, padx=(0, 6), pady=1, sticky='W')

        self.combo_val = create_combobox(
            self.frame_val, self.var_val, self.ctg_values,
            combobox_width(self.ctg_values, 5, 100),
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=0, column=0, padx=0, pady=0)
        self.btn_choose = create_button(
            self.frame_val, self.choose,
            row=0, column=1, padx=(3, 0), pady=0)
        set_image(self.btn_choose, self.img_ok, img_ok, 'Задать значение')
        self.btn_none = create_button(
            self.frame_val, self.set_none,
            row=0, column=2, padx=0, pady=0)
        set_image(self.btn_none, self.img_none, img_cancel, 'Не указывать/неприменимо')

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

        self.var_template.set(f'Текущий шаблон словоформы: "{gram_form_to_str(self.template)}"')

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

        self.var_template.set(f'Текущий шаблон словоформы: "{gram_form_to_str(self.template)}"')

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
        if tuple(self.template) in self.dct[self.key].forms.keys():
            warning(
                self, self.app_data,
                f'У слова "{self.dct[self.key].lemma}" уже есть форма с таким шаблоном!',
            )
            return
        if self.var_form.get() == '':
            warning(self, self.app_data, 'Словоформа должна содержать хотя бы один символ!')
            return
        self.closed = False
        self.destroy()

    # Обновить combobox со значениями категории после выбора категории
    def refresh_vals(self):
        self.ctg_values = list(self.dct.features[self.var_ctg.get()])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.combo_val.configure(
            textvariable=self.var_val, values=self.ctg_values,
            width=combobox_width(self.ctg_values, 5, 100),
        )

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_form.focus_set()

        bind_ctrl_a(self.entry_form)
        self.bind('<Return>', lambda event: self.btn_choose.invoke())
        self.bind('<Escape>', lambda event: self.destroy())
        self.combo_ctg.bind('<<ComboboxSelected>>', lambda event: self.refresh_vals())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        if self.closed:
            return None, None
        if self.template == self.void_template:
            return None, None
        if tuple(self.template) in self.dct[self.key].forms.keys():
            return None, None
        return tuple(self.template), self.var_form.get()


# Окно настроек грамматических категорий
class CategoriesSettingsW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.categories = []
        self.frames = []
        self.buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_categories(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.btn_about_window = create_button(
            self, self.about_window, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_categories = create_label(
            self, 'Существующие категории слов:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add, 'Добавить категорию',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_about_window, 'Справка', hover_delay=450
        )

    # Добавить категорию
    def add(self):
        self.has_changes = add_ctg(self, self.dct) or self.has_changes
        self.print_categories(False)

    # Переименовать категорию
    def rename(self, ctg_key: str):
        self.has_changes = rename_ctg(self, self.dct, ctg_key) or self.has_changes
        self.print_categories(False)

    # Удалить категорию
    def delete(self, ctg_key: str):
        self.has_changes = delete_ctg(self, self.dct, ctg_key) or self.has_changes
        self.print_categories(False)

    # Перейти к настройкам значений категории
    def values(self, ctg_key: str):
        self.has_changes = CategoryValuesSettingsW(
            self, ctg_key, self.app_data
        ).open() or self.has_changes

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
        self.categories = list(self.dct.features.keys())
        categories_count = len(self.categories)

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
                lambda i=i: self.values(self.categories[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(categories_count)
        ]
        for i in range(categories_count):
            # Выводим текст на кнопки
            ctg = self.categories[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.categories[i]))
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.categories[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.categories[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.categories[i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы добавить значение категории, наведите на неё мышку и нажмите ЛКМ\n'
            '* Чтобы переименовать категорию, наведите на неё мышку и нажмите Ctrl+R\n'
            '* Чтобы удалить категорию, наведите на неё мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек групп
class GroupsSettingsW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_info = app_data.manager.active

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.groups = []
        self.frames = []
        self.buttons = []
        self.tips = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_groups(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.btn_about_window = create_button(
            self, self.about_window, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_groups = create_label(
            self, 'Существующие группы:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add, 'Добавить группу',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_about_window, 'Справка', hover_delay=450
        )

    # Добавить группу
    def add(self):
        window = PopupEntryW(
            self, self.app_data,
            'Введите название новой группы',
            check_answer_function=lambda wnd, val: check_group_name(
                wnd, self.dct_info.dct.groups, val
            ),
        )
        closed, group = window.open()
        if closed:
            return
        group = encode_special_combinations(group, self.dct_info.dct.input_replacements)
        self.dct_info.dct.add_group(group)

        self.print_groups(False)
        self.has_changes = True

    # Переименовать группу
    def rename(self, group_old: str):
        window = PopupEntryW(
            self, self.app_data,
            'Введите новое название группы',
            default_value=group_old,
            check_answer_function=lambda wnd, val: check_group_name_edit(
                wnd, self.dct_info.dct.groups, group_old, val
            ),
        )
        closed, group_new = window.open()
        if closed:
            return
        group_new = encode_special_combinations(group_new, self.dct_info.dct.input_replacements)

        if self.dct_info.dct.groups.index(group_old) + 1 == self.dct_info.cache.train_config[1]:
            self.dct_info.cache.train_config[1] = len(self.dct_info.dct.groups)
        elif self.dct_info.dct.groups.index(group_old) + 1 < self.dct_info.cache.train_config[1]:
            self.dct_info.cache.train_config[1] -= 1
        self.dct_info.dct.rename_group(group_old, group_new)
        if self.dct_info.dct.is_default_group(group_old):
            self.dct_info.dct.unmark_default_group(group_old)
            self.dct_info.dct.mark_group_as_default(group_new)

        self.print_groups(False)
        self.has_changes = True

    # Удалить группу
    def delete(self, group: str):
        group_size = self.dct_info.dct.count_entries_in_group(group)[0]
        if group_size != 0:
            tmp = set_postfix(
                group_size,
                ('слово будет убрано', 'слова будут убраны', 'слов будут убраны'),
            )
            window_dia = PopupDialogueW(
                self, self.app_data,
                f'{group_size} {tmp} из группы "{group}", а сама группа будет удалена!\n'
                f'Хотите продолжить?',
            )
            answer = window_dia.open()
            if not answer:
                return

        if self.dct_info.dct.groups.index(group) + 1 == self.dct_info.cache.train_config[1]:
            self.dct_info.cache.train_config[1] = 0
        elif self.dct_info.dct.groups.index(group) + 1 < self.dct_info.cache.train_config[1]:
            self.dct_info.cache.train_config[1] -= 1
        self.dct_info.dct.delete_group(group)
        if self.dct_info.dct.is_default_group(group):
            self.dct_info.dct.unmark_default_group(group)

        self.print_groups(False)
        self.has_changes = True

    # Добавить группу в избранное
    def fav(self, group: str):
        if self.dct_info.dct.is_default_group(group):
            self.dct_info.dct.unmark_default_group(group)
        else:
            self.dct_info.dct.mark_group_as_default(group)

        self.print_groups(False)
        self.has_changes = True

    # Напечатать существующие группы
    def print_groups(self, move_scroll: bool):
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

        # Выбираем группы
        self.groups = list(self.dct_info.dct.groups)
        groups_count = len(self.groups)

        # Создаём новые фреймы
        self.frames = [
            create_frame(
                self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(groups_count)
        ]
        # Создаём новые кнопки
        self.buttons = [
            create_button(
                self.frames[i],
                lambda i=i: self.rename(self.groups[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(groups_count)
        ]
        # Создаём новые подсказки
        self.tips = [
            ttip.Hovertip(
                self.buttons[i],
                f'Статей в группе: {self.dct_info.dct.count_entries_in_group(self.groups[i])[0]}',
                hover_delay=500,
            ) for i in range(groups_count)
        ]
        for i in range(groups_count):
            # Выводим текст на кнопки
            group = self.groups[i]
            if self.dct_info.dct.is_default_group(group):
                self.buttons[i].configure(text=split_text(f'{group} (*)', 35))
            else:
                self.buttons[i].configure(text=split_text(f'{group}', 35))

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.groups[i]))
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.groups[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.groups[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.groups[i]))
            self.frames[i].bind('<Control-f>', lambda event, i=i: self.fav(self.groups[i]))
            self.frames[i].bind('<Control-F>', lambda event, i=i: self.fav(self.groups[i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы переименовать группу, наведите на неё мышку и нажмите ЛКМ или Ctrl+R\n'
            '* Чтобы удалить группу, наведите на неё мышку и нажмите Ctrl+D\n'
            '* Чтобы все новые статьи автоматически добавлялись в группу, '
            'наведите на эту группу мышку и нажмите Ctrl+F',
            msg_justify='left',
        ).open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек значений грамматической категории
class CategoryValuesSettingsW(tk.Toplevel):
    def __init__(self, parent, ctg_key: str, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.ctg_key = ctg_key  # Название изменяемой категории
        self.ctg_values = self.dct.features[self.ctg_key]  # Значения изменяемой категории
        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.values = []
        self.frames = []
        self.buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_ctg_values(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.btn_about_window = create_button(
            self, self.about_window, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_ctg_values = create_label(
            self,
            f'Существующие значения категории\n'
            f'"{self.ctg_key}":',
            justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add, 'Добавить значение',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_about_window, 'Справка', hover_delay=450
        )

    # Добавить значение категории
    def add(self):
        self.has_changes = add_ctg_value(
            self, self.dct, self.ctg_key, self.ctg_values
        ) or self.has_changes
        self.print_ctg_values(False)

    # Переименовать значение категории
    def rename(self, val: str):
        self.has_changes = rename_ctg_value(self, self.dct, self.ctg_key, val) or self.has_changes
        self.print_ctg_values(False)

    # Удалить значение категории
    def delete(self, val: str):
        self.has_changes = delete_ctg_value(self, self.dct, self.ctg_key, val) or self.has_changes
        self.print_ctg_values(False)
        if self.ctg_key not in self.dct.features:
            self.parent.print_categories(False)
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
                lambda i=i: self.rename(self.values[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(categories_count)
        ]
        for i in range(categories_count):
            # Выводим текст на кнопки
            ctg = self.values[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-r>', lambda event, i=i: self.rename(self.values[i]))
            self.frames[i].bind('<Control-R>', lambda event, i=i: self.rename(self.values[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(self.values[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(self.values[i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы переименовать значение, наведите на него мышку и нажмите ЛКМ или Ctrl+R\n'
            '* Чтобы удалить значение, наведите на него мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно настроек специальных комбинаций
class SpecialCombinationsSettingsW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.combinations = []
        self.frames = []
        self.buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_combinations(True)

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.btn_about_window = create_button(
            self, self.about_window, width=2,
            row=0, column=0, padx=(6, 0), pady=(6, 6), sticky='E')
        set_image(self.btn_about_window, self.img_about, img_about, '?')
        self.lbl_combinations = create_label(
            self, 'Существующие комбинации:', justify='center',
            row=0, column=1, padx=(0, 6), pady=(6, 0), sticky='W')
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_TALL[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(
            row=1, column=0, columnspan=2, padx=6, pady=(0, 6))
        self.btn_add = create_button(
            self, self.add, 'Добавить комбинацию',
            row=2, column=0, columnspan=2, padx=6, pady=(0, 6))

    def _create_tips(self):
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_about_window, 'Справка', hover_delay=450
        )

    # Добавить комбинацию
    def add(self):
        window = EnterSpecialCombinationW(self, self.app_data)
        closed, key, val = window.open()
        if closed or key[0] == '' or key[1] == '' or val == '':
            return
        if key in self.dct.input_replacements.keys():
            warning(self, self.app_data, f'Комбинация {key[0]}{key[1]} уже существует!')
            return
        self.dct.add_replacement(*key, val)
        self.print_combinations(False)
        self.has_changes = True

    # Изменить комбинацию
    def edit(self, old_key: tuple[str, str]):
        old_val = self.dct.input_replacements[old_key]
        window = EnterSpecialCombinationW(
            self, self.app_data, default_value=old_key+tuple(old_val)
        )
        closed, new_key, new_val = window.open()
        if closed or new_key[0] == '' or new_key[1] == '' or new_val == '':
            return
        if new_key == old_key and new_val == old_val:
            return

        self.dct.delete_replacement(*old_key)

        self.dct.add_replacement(*new_key, new_val)
        self.print_combinations(False)
        self.has_changes = True

    # Удалить комбинацию
    def delete(self, cmb_key: tuple[str, str]):
        self.dct.delete_replacement(*cmb_key)
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
        self.combinations = [key for key in self.dct.input_replacements]
        combinations_count = len(self.combinations)

        # Создаём новые фреймы
        self.frames = tuple(
            [
                create_frame(
                    self.scrolled_frame.frame_canvas, 'Invis.TFrame',
                    row=i, column=0, padx=0, pady=0, sticky='WE',
                ) for i in range(combinations_count)
            ] + [create_label(
                self.scrolled_frame.frame_canvas,
                split_text('## -> #, %% -> % и т. д.', 35),
                'FlatL.TLabel',
                row=combinations_count, column=0, padx=0, pady=0, sticky='WE',
            )]
        )
        # Создаём новые кнопки
        self.buttons = [
            create_button(
                self.frames[i],
                lambda i=i: self.edit(self.combinations[i]),
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(combinations_count)
        ]
        for i in range(combinations_count):
            # Выводим текст на кнопки
            cmb = self.combinations[i]
            self.buttons[i].configure(text=split_text(special_combination(cmb), 35))

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-e>', lambda event, i=i: self.edit(nontrivial_keys[i]))
            self.frames[i].bind('<Control-E>', lambda event, i=i: self.edit(nontrivial_keys[i]))
            self.frames[i].bind('<Control-d>', lambda event, i=i: self.delete(nontrivial_keys[i]))
            self.frames[i].bind('<Control-D>', lambda event, i=i: self.delete(nontrivial_keys[i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы изменить комбинацию, наведите на неё мышку и нажмите ЛКМ или Ctrl+E\n'
            '* Чтобы удалить комбинацию, наведите на неё мышку и нажмите Ctrl+D',
            msg_justify='left',
        ).open()

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.has_changes


# Окно ввода специальной комбинации
class EnterSpecialCombinationW(tk.Toplevel):
    def __init__(
            self,
            parent,
            app_data: AppData,
            default_value: tuple[str, str, str] = (SPECIAL_COMBINATIONS_OPENING_SYMBOLS[0],
                                                   None, None),
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

        self.closed = True  # Закрыто ли окно крестиком

        self.var_opening_symbol = tk.StringVar(value=default_value[0])
        self.var_key_symbol = tk.StringVar(value=default_value[1])
        self.var_val = tk.StringVar(value=default_value[2])

        self.vcmd_opening_symbol = (
            self.register(validate_special_combination_opening_symbol), '%P'
        )
        self.vcmd_key_symbol = (self.register(validate_special_combination_key_symbol), '%P')
        self.vcmd_val = (self.register(validate_special_combination_val), '%P')

        self._configure_window()
        self._create_widgets()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_msg = create_label(
            self, 'Задайте комбинацию', justify='center',
            row=0, padx=6, pady=(6, 3))
        self._create_main_frame()
        self.btn_ok = create_button(
            self, self.ok, 'Подтвердить', style='Yes.TButton',
            row=2, padx=6, pady=6)

    def _create_main_frame(self):
        self.frame_main = create_frame(self, 'Invis.TFrame', row=1, padx=6, pady=0)

        self.combo_opening_symbol = create_combobox(
            self.frame_main, self.var_opening_symbol, SPECIAL_COMBINATIONS_OPENING_SYMBOLS, 3,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale), state='normal',
            validate='all', validatecommand=self.vcmd_opening_symbol,
            row=0, column=0, padx=0, pady=0)
        self.entry_key_symbol = create_entry(
            self.frame_main, self.var_key_symbol, 2, font=self.app_data,
            justify='right', validate='key', validatecommand=self.vcmd_key_symbol,
            row=0, column=1, padx=0, pady=0)
        self.lbl_arrow = create_label(
            self.frame_main, '->', justify='center',
            row=0, column=2, padx=2, pady=0)
        self.entry_val = create_entry(
            self.frame_main, self.var_val, 2, font=self.app_data,
            validate='key', validatecommand=self.vcmd_val,
            row=0, column=3, padx=0, pady=0)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_key_symbol.focus_set()

        bind_ctrl_a(self.entry_val)
        bind_ctrl_a(self.entry_key_symbol)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return (
            self.closed,
            (self.var_opening_symbol.get(), self.var_key_symbol.get()),
            self.var_val.get(),
        )


# Окно настроек пользовательской темы
class CustomThemeSettingsW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data

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

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.entry_demo.insert(tk.END, 'abcde 12345')
        self.txt_demo.insert(tk.END, '1')
        for i in range(2, 51):
            self.txt_demo.insert(tk.END, f'\n{i}')
        self.txt_demo.config(yscrollcommand=self.scroll_demo.set, state='disabled')

        self.read()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Настройки пользовательской темы')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
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
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=1, column=1, padx=(0, 3), pady=0)
        self.btn_set_images = create_button(
            self.frame_themes, self.set_images, 'Выбрать', width=8,
            row=1, column=2, padx=(0, 0), pady=0, sticky='W')

    def _create_scrolled_frame(self):
        self.scrolled_frame = ScrollFrame(
            self, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_CUSTOM_THEME_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame.grid(row=1, column=0, padx=6, pady=6)

        # Выбор цветов
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
                self.buttons[i].configure(command=lambda i=i: self.choose_color(i))

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

        # Выбор стиля рамок
        def _choose_relief(elem, value):
            if self.custom_styles[elem] != value:
                self.history += [(elem, self.custom_styles[elem], value)]
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
            SCALE_CUSTOM_THEME_COMBO_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN],
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            validate='focus', validatecommand=self.vcmd_relief_frame, state='readonly',
            row=9, column=1, columnspan=2, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_relief_text = create_label(
            self.scrolled_frame.frame_canvas, 'Стиль рамок текстовых полей:',
            row=10, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_relief_text = create_combobox(
            self.scrolled_frame.frame_canvas, self.var_relief_text,
            ('raised', 'sunken', 'flat', 'ridge', 'solid', 'groove'),
            SCALE_CUSTOM_THEME_COMBO_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN],
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
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
        self.frame_history = create_frame(
            self.frame_buttons, 'Invis.TFrame',
            row=0, column=1, padx=0, pady=0)

        self.btn_undo = create_button(
            self.frame_history, self.undo, width=2,
            row=0, column=0, padx=(0, 6), pady=0, sticky='W')
        set_image(self.btn_undo, self.img_undo, img_undo, '<<')
        self.btn_redo = create_button(
            self.frame_history, self.redo, width=2,
            row=0, column=1, padx=0, pady=0, sticky='W')
        set_image(self.btn_redo, self.img_redo, img_redo, '>>')

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
            font=('StdFont', self.app_data.gui_settings.scale),
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
            font=('StdFont', self.app_data.gui_settings.scale),
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

    # Взять за основу уже существующую тему
    def set_theme(self):
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

            old_vals += [self.custom_styles[st_key]]
            new_vals += [st_val]
            self.custom_styles[st_key] = st_val

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
        st_key = STYLE_KEYS[n]
        hx = self.custom_styles[st_key]

        rgb, new_hx = colorchooser.askcolor(hx)
        if not new_hx:
            return

        self.buttons[n].config(bg=new_hx, activebackground=new_hx)
        self.custom_styles[st_key] = new_hx

        self.set_demo_styles()

        if new_hx != hx:
            self.history += [(st_key, hx, new_hx)]
            self.history_undo.clear()

    # Сохранить пользовательскую тему
    def save(self):
        self.custom_styles['FRAME.RELIEF.*'] = self.var_relief_frame.get()
        self.custom_styles['TXT.RELIEF.*'] = self.var_relief_text.get()
        filepath = os.path.join(CUSTOM_THEME_PATH, STYLES_FN)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'{REQUIRED_THEME_VERSION}')
            file.write('\n1')
            for el in STYLE_KEYS:
                file.write(f'\n{el} = {self.custom_styles[el]}')

        if self.dir_with_images != CUSTOM_THEME_PATH:
            images = [
                img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav,
                img_add_to_group, img_remove_from_group, img_edit, img_add, img_delete,
                img_select_page, img_unselect_page, img_select_all, img_unselect_all,
                img_print_out, img_redo, img_undo, img_arrow_left, img_arrow_right,
                img_double_arrow_left, img_double_arrow_right, img_trashcan,
            ]
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

            self.history += [last_undo_action]
            self.history_undo.pop(-1)

            self.set_demo_styles()

    # Загрузить пользовательскую тему
    def read(self):
        filepath = os.path.join(CUSTOM_THEME_PATH, STYLES_FN)
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

    # Обновить стили в демонстрации
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

        # Стиль label "demo default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure(
            'DemoDefault.TLabel',
            font=('StdFont', self.app_data.gui_settings.scale),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.*'],
        )

        # Стиль label "demo header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure(
            'DemoHeader.TLabel',
            font=('StdFont', self.app_data.gui_settings.scale + 5),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.*'],
        )

        # Стиль label "demo logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure(
            'DemoLogo.TLabel',
            font=('Times', self.app_data.gui_settings.scale + 11),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.LOGO'],
        )

        # Стиль label "demo footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure(
            'DemoFooter.TLabel',
            font=('StdFont', self.app_data.gui_settings.scale - 2),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.FOOTER'],
        )

        # Стиль label "demo warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure(
            'DemoWarn.TLabel',
            font=('StdFont', self.app_data.gui_settings.scale),
            background=self.custom_styles['*.BG.*'],
            foreground=self.custom_styles['*.FG.WARN'],
        )

        # Стиль entry "demo"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure(
            'DemoDefault.TEntry',
            font=('StdFont', self.app_data.gui_settings.scale),
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

        # Стиль button "demo default"
        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure(
            'DemoDefault.TButton',
            font=('StdFont', self.app_data.gui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_default.map(
            'DemoDefault.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "demo disabled"
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure(
            'DemoDisabled.TButton',
            font=('StdFont', self.app_data.gui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_disabled.map(
            'DemoDisabled.TButton',
            relief=[('active', 'raised'),
                    ('!active', 'raised')],
            background=[
                ('active', self.custom_styles['BTN.BG.DISABL']),
                ('!active', self.custom_styles['BTN.BG.DISABL']),
            ],
            foreground=[
                ('active', self.custom_styles['BTN.FG.DISABL']),
                ('!active', self.custom_styles['BTN.FG.DISABL']),
            ],
        )

        # Стиль button "demo yes"
        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure(
            'DemoYes.TButton',
            font=('StdFont', self.app_data.gui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_yes.map(
            'DemoYes.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "demo no"
        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure(
            'DemoNo.TButton',
            font=('StdFont', self.app_data.gui_settings.scale + 2),
            borderwidth=1,
        )
        self.st_btn_no.map(
            'DemoNo.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "demo image"
        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure(
            'DemoImage.TButton',
            font=('StdFont', self.app_data.gui_settings.scale + 2),
            borderwidth=0,
        )
        self.st_btn_image.map(
            'DemoImage.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль checkbutton "demo"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map(
            'DemoDefault.TCheckbutton',
            background=[
                ('active', self.custom_styles['CHECK.BG.SEL']),
                ('!active', self.custom_styles['*.BG.*']),
            ],
        )

        # Стиль frame "demo default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure(
            'DemoDefault.TFrame',
            borderwidth=1,
            relief=self.custom_styles['FRAME.RELIEF.*'],
            background=self.custom_styles['*.BG.*'],
            bordercolor=self.custom_styles['*.BORDER_CLR.*'],
        )

        # Стиль frame "window"
        self.st_frame_window = ttk.Style()
        self.st_frame_window.theme_use('alt')
        self.st_frame_window.configure(
            'Window.TFrame',
            borderwidth=1,
            relief='groove',
            background=self.custom_styles['*.BG.*'],
            bordercolor='#888888',
        )

        # Стиль scrollbar "vertical"
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

    # Обновить изображения в демонстрации
    def refresh_images(self):
        for i in range(len(ICON_NAMES)):
            img = f'{ICON_NAMES[i]}.png'
            # TODO: remove try-except
            try:
                self.images[i].config(file=os.path.join(self.dir_with_images, img))
            except:
                # TODO: remove try-except
                try:
                    self.images[i].config(file=os.path.join(IMAGES_PATH, img))
                except:
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

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


""" Графический интерфейс - основные окна """


# Окно изучения слов
class LearnW(tk.Toplevel):
    _session_number = 0

    def __init__(
            self,
            parent,
            app_data: AppData,
            train_config: TrainingConfig,
    ):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_info = app_data.manager.active
        self.trainer = Trainer(self.dct_info.dct, train_config)
        self.trainer.initialize()
        self.initial_pool_size = len(self.trainer.pool)
        self.current_entry_id = None  # Текущее слово
        self.current_form = None  # Текущая форма (если начальная, то None)
        self.current_phrase = None  # Текущая фраза
        self.homonyms = []  # Омонимы к текущему слову
        self.count_all = 0  # Счётчик всех ответов
        self.count_correct = 0  # Счётчик верных ответов

        self.var_input = tk.StringVar()

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.choose()

        if self.current_entry_id:
            entry = self.trainer.dct[self.current_entry_id]
            if entry.n_notes == 0 or train_config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                                             TrainingMethod.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_notes)
            if not self.homonyms or train_config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                                            TrainingMethod.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_homonyms)
            if train_config.method not in (TrainingMethod.TRANS_TO_PHRASE,
                                           TrainingMethod.PHRASE_TO_TRANS):
                btn_disable(self.btn_show_entry)

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Учёба')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_global_rating = create_label(
            self, f'Ваш общий рейтинг по словарю: {self.get_percent()}',
            row=0, columnspan=2, padx=6, pady=(6, 3))
        self.lbl_count = create_label(
            self, f'Отвечено: 0/{self.initial_pool_size}',
            row=1, columnspan=2, padx=6, pady=(0, 6))

        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.scrollbar.grid(row=2, column=1, padx=(0, 6), pady=6, sticky='NSW')
        self.txt_dct = tk.Text(
            self, width=70, height=30, state='disabled',
            yscrollcommand=self.scrollbar.set,
            font=('StdFont', self.app_data.gui_settings.scale),
            bg=STYLES['*.BG.ENTRY'][1][self.app_data.gui_settings.theme],
            fg=STYLES['*.FG.*'][1][self.app_data.gui_settings.theme],
            selectbackground=STYLES['*.BG.SEL'][1][self.app_data.gui_settings.theme],
            selectforeground=STYLES['*.FG.SEL'][1][self.app_data.gui_settings.theme],
            relief=STYLES['TXT.RELIEF.*'][1][self.app_data.gui_settings.theme],
            highlightbackground=STYLES['*.BORDER_CLR.*'][1][self.app_data.gui_settings.theme])
        self.txt_dct.grid(row=2, column=0, padx=(6, 0), pady=6, sticky='NSWE')
        self.scrollbar.config(command=self.txt_dct.yview)

        self._create_main_frame()
        self.btn_stop = create_button(
            self, self.stop, 'Закончить', style='No.TButton',
            row=4, columnspan=2, padx=6, pady=6)

    def _create_main_frame(self):
        self.frame_main = create_frame(self, 'Invis.TFrame', row=3, columnspan=2, padx=6, pady=6)

        self.btn_input = create_button(
            self.frame_main, self.input, 'Ввод', width=6,
            row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input = create_entry(
            self.frame_main, self.var_input, 36, font=self.app_data,
            row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        self.btn_show_entry = create_button(
            self.frame_main, self.show_entry, 'Слово и перевод', width=15)
        self.btn_show_notes = create_button(
            self.frame_main, self.show_notes, 'Сноски', width=7)
        self.btn_show_homonyms = create_button(
            self.frame_main, self.show_homonyms, 'Омонимы', width=8)

        if self.trainer.config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                          TrainingMethod.PHRASE_TO_TRANS):
            self.btn_show_entry.grid(row=0, column=2, padx=0, pady=0, sticky='W')
        else:
            self.btn_show_notes.grid(row=0, column=2, padx=(0, 3), pady=0, sticky='W')
            self.btn_show_homonyms.grid(row=0, column=3, padx=0, pady=0, sticky='W')

    def _create_tips(self):
        self.tip_btn_show_entry = ttip.Hovertip(
            self.btn_show_entry,
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

        if self.trainer.config.method == TrainingMethod.TRANS_TO_WORD:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите слово', hover_delay=1000)
        elif self.trainer.config.method == TrainingMethod.WORD_TO_TRANS:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        elif self.trainer.config.method == TrainingMethod.TRANS_TO_PHRASE:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите фразу', hover_delay=1000)
        elif self.trainer.config.method == TrainingMethod.PHRASE_TO_TRANS:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        else:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите артикль', hover_delay=1000)

    # Печать в журнал
    def outp(self, msg: Any = '', end: Any = '\n'):
        self.txt_dct['state'] = 'normal'
        self.txt_dct.insert(tk.END, f'{msg}{end}')
        self.txt_dct.yview_moveto(1.0)
        self.txt_dct['state'] = 'disabled'

    # Получить глобальный процент угадываний
    def get_percent(self):
        correct, total = self.trainer.dct.score()
        percent = (100 * correct / total) if total else 0
        return f'{correct} / {total} = {percent:.1f}%'

    # Выбор слова для угадывания
    def choose(self):
        if self.trainer.is_finished():
            # Если все слова отвечены, то завершаем учёбу
            self.stop()
            return
        else:
            self.dct_info.dct.mark_modified()

        # Выбор слова
        self.current_entry_id, self.current_form, self.current_phrase, \
            self.homonyms = self.trainer.get_task()

        # Вывод слова в журнал
        if self.trainer.config.method == TrainingMethod.TRANS_TO_WORD:
            if self.trainer.config.forms and self.current_form:
                self.outp(get_tr_and_frm_with_stat(
                    self.trainer.dct[self.current_entry_id],
                    self.current_form,
                ))
            else:
                self.outp(get_tr_with_stat(self.trainer.dct[self.current_entry_id]))
        elif self.trainer.config.method == TrainingMethod.WORD_TO_TRANS:
            self.outp(get_wrd_with_stat(self.trainer.dct[self.current_entry_id]))
        elif self.trainer.config.method == TrainingMethod.TRANS_TO_PHRASE:
            self.outp(get_phr_tr_with_stat(
                self.trainer.dct[self.current_entry_id],
                self.current_phrase,
            ))
        elif self.trainer.config.method == TrainingMethod.PHRASE_TO_TRANS:
            self.outp(get_phr_with_stat(
                self.trainer.dct[self.current_entry_id],
                self.current_phrase,
            ))
        else:
            self.outp(get_wrd_with_stat(self.trainer.dct[self.current_entry_id])[4:])

    # Нажатие на кнопку "Ввод"
    # Ввод ответа и переход к следующему слову
    def input(self):
        # Вывод в журнал пользовательского ответа
        user_answer = encode_special_combinations(
            self.entry_input.get(), self.dct_info.dct.input_replacements
        )
        if user_answer != '':
            self.outp(user_answer)

        # Проверка пользовательского ответа
        self.check_answer(user_answer)

        # Выбор нового слова для угадывания
        self.choose()

        # Обновление кнопки "Посмотреть слово и перевод"
        if self.trainer.config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                          TrainingMethod.PHRASE_TO_TRANS):
            btn_enable(self.btn_show_entry, self.show_entry)
        # Обновление кнопки "Посмотреть сноски"
        entry = self.trainer.dct[self.current_entry_id]
        if entry.n_notes == 0 or self.trainer.config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                                                TrainingMethod.PHRASE_TO_TRANS):
            btn_disable(self.btn_show_notes)
        else:
            btn_enable(self.btn_show_notes, self.show_notes)
        # Обновление кнопки "Посмотреть омонимы"
        if not self.homonyms or self.trainer.config.method in (TrainingMethod.TRANS_TO_PHRASE,
                                                               TrainingMethod.PHRASE_TO_TRANS):
            btn_disable(self.btn_show_homonyms)
        else:
            btn_enable(self.btn_show_homonyms, self.show_homonyms)
        # Очистка поля ввода
        self.entry_input.delete(0, tk.END)
        # Обновление отображаемого рейтинга
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {self.get_percent()}'
        self.lbl_count['text'] = f'Отвечено: {self.count_correct}/{self.initial_pool_size}'

    # Нажатие на кнопку "Посмотреть слово и перевод"
    # Просмотр слова с переводом
    def show_entry(self):
        entry = self.trainer.dct[self.current_entry_id]
        self.outp(f'Слово: {entry.lemma}\n'
                  f'Перевод: {get_tr(entry)}')
        btn_disable(self.btn_show_entry)

    # Нажатие на кнопку "Посмотреть сноски"
    # Просмотр сносок
    def show_notes(self):
        self.outp('Сноски:')
        entry = self.trainer.dct[self.current_entry_id]
        self.outp(get_notes(entry))
        btn_disable(self.btn_show_notes)

    # Нажатие на кнопку "Посмотреть омонимы"
    # Просмотр омонимов
    def show_homonyms(self):
        self.outp('Омонимы:')
        for key in self.homonyms:
            self.outp('> ' + self.trainer.dct[key].lemma + ': ' + get_tr(self.trainer.dct[key]))
        btn_disable(self.btn_show_homonyms)

    # Нажатие на кнопку "Закончить"
    # Завершение учёбы
    def stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()
        btn_disable(self.btn_input)
        btn_disable(self.btn_show_notes)
        btn_disable(self.btn_show_homonyms)
        btn_disable(self.btn_show_entry)

        self.outp(f'\nВаш результат: {self.count_correct}/{self.count_all}', end='')

    # Проверка введённого ответа
    def check_answer(self, answer: str):
        is_correct = self.trainer.is_answer_correct(
            answer,
            is_case_sensitive=self.dct_info.settings.is_register_sensitive,
        )
        correct_answers = self.trainer.get_correct_answers()
        correct_answer = ', '.join(correct_answers)

        entry = self.trainer.dct[self.current_entry_id]
        if is_correct:
            entry.correct((
                self.dct_info.cache.session_number,
                self._session_number,
                self.count_all,
            ))
            self.outp('Верно\n')
            if entry.is_fav:
                window = PopupDialogueW(
                    self, self.app_data,
                    'Верно.\n'
                    'Оставить слово в избранном?',
                    'Да', 'Нет', val_on_close=True,
                )
                ttip.Hovertip(window.btn_right, 'Alt+N', hover_delay=700)
                window.bind('<Alt-N>', lambda event: window.btn_right.invoke())
                answer = window.open()
                if not answer:
                    entry.is_fav = False
            self.count_all += 1
            self.count_correct += 1
        else:
            self.outp(f'Неверно. Правильный ответ: "{correct_answer}"\n')
            if entry.is_fav:
                if self.app_data.global_settings.is_typo_btn_on:
                    window = PopupDialogueW(
                        self, self.app_data,
                        f'Неверно.\n'
                        f'Ваш ответ: {encode_special_combinations(
                            self.entry_input.get(), self.dct_info.dct.input_replacements
                        )}\n'
                        f'Правильный ответ: {correct_answer}',
                        btn_left_text='Ясно', btn_right_text='Просто опечатка',
                        st_left='Default', st_right='Default',
                        val_left='ok', val_right='typo')
                    ttip.Hovertip(
                        window.btn_right,
                        'Не засчитывать ошибку\n'
                        'Tab',
                        hover_delay=700,
                    )
                    window.bind('<Tab>', lambda event: window.btn_right.invoke())
                    answer = window.open()
                    if answer != 'typo':
                        entry.incorrect((
                            self.dct_info.cache.session_number,
                            self._session_number,
                            self.count_all,
                        ))
                        self.count_all += 1
                else:
                    entry.incorrect((
                        self.dct_info.cache.session_number,
                        self._session_number,
                        self.count_all,
                    ))
                    self.count_all += 1
            else:
                window = IncorrectAnswerW(
                    self, self.app_data,
                    encode_special_combinations(
                        self.entry_input.get(), self.dct_info.dct.input_replacements,
                    ),
                    correct_answer,
                    self.app_data.global_settings.is_typo_btn_on,
                )
                answer = window.open()
                if answer != 'typo':
                    entry.incorrect((
                        self.dct_info.cache.session_number,
                        self._session_number,
                        self.count_all,
                    ))
                    self.count_all += 1
                if answer == 'yes':
                    entry.is_fav = True

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()

        bind_ctrl_a(self.entry_input)
        self.bind('<Return>', lambda event: self.btn_input.invoke())
        self.bind('<Control-n>', lambda event: self.btn_show_notes.invoke())
        self.bind('<Control-N>', lambda event: self.btn_show_notes.invoke())
        self.bind('<Control-o>', lambda event: self.btn_show_homonyms.invoke())
        self.bind('<Control-O>', lambda event: self.btn_show_homonyms.invoke())
        self.bind('<Control-w>', lambda event: self.btn_show_entry.invoke())
        self.bind('<Control-W>', lambda event: self.btn_show_entry.invoke())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        LearnW._session_number += 1


# Окно просмотра словаря
class PrintW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct_info = app_data.manager.active

        self.current_tab = 0  # Номер текущей вкладки

        # Константы для вкладки печати
        self.print_max_elements_on_page = 100  # Максимальное количество элементов на одной странице ScrollFrame
        self.print_current_page = 1  # Номер текущей страницы ScrollFrame (начиная с 1)
        self.print_start_index = 0  # Номер по порядку первого слова на текущей странице ScrollFrame (начиная с 0)
        self.print_count_pages = None  # Количество страниц ScrollFrame
        self.print_count_elements = None  # Количество элементов на всех страницах ScrollFrame
        self.print_count_elements_on_page = None  # Количество элементов на текущей странице ScrollFrame
        # Константы для вкладки поиска
        self.search_max_elements_on_page = 50  # Максимальное количество элементов на одной странице ScrollFrame
        self.search_current_page = 1  # Номер текущей страницы ScrollFrame (начиная с 1)
        self.search_start_index = 0  # Номер по порядку первого слова на текущей странице ScrollFrame (начиная с 0)
        self.search_count_pages = None  # Количество страниц ScrollFrame
        self.search_count_elements = None  # Количество элементов на всех страницах ScrollFrame
        self.search_count_elements_on_page = None  # Количество элементов на текущей странице ScrollFrame

        self.group_vals = [ALL_GROUPS] + self.dct_info.dct.groups

        # Параметры поиска
        search_config = self.dct_info.cache.search_config
        self.to_search_only_fav = search_config.to_search_only_fav
        self.to_search_only_full = search_config.to_search_only_full
        self.to_search_wrd = search_config.to_search_in_words
        self.to_search_tr = search_config.to_search_in_translations
        self.to_search_frm = search_config.to_search_in_forms
        self.to_search_phr = search_config.to_search_in_phrases
        self.to_search_nt = search_config.to_search_in_notes
        self.search_group = search_config.search_groups

        # Переменные для вкладки печати
        self.var_print_fav = tk.BooleanVar(value=False)
        self.var_print_briefly = tk.BooleanVar(value=False)
        self.var_print_info = tk.StringVar()
        self.var_print_info_selected = tk.StringVar()
        self.var_print_current_page = tk.StringVar(value=str(self.print_current_page))
        self.var_print_order = tk.StringVar(value=PRINT_VALUES_ORDER[0])
        self.var_print_group = tk.StringVar(value=ALL_GROUPS)
        # Переменные для вкладки поиска
        self.var_search_query = tk.StringVar()
        self.var_search_info = tk.StringVar()
        self.var_search_info_selected = tk.StringVar()
        self.var_search_current_page = tk.StringVar(value=str(self.search_current_page))

        self.img_about = tk.PhotoImage()
        self.img_arrow_left = tk.PhotoImage()
        self.img_arrow_right = tk.PhotoImage()
        self.img_double_arrow_left = tk.PhotoImage()
        self.img_double_arrow_right = tk.PhotoImage()
        self.img_print_out = tk.PhotoImage()
        self.img_select_page = tk.PhotoImage()
        self.img_unselect_page = tk.PhotoImage()
        self.img_select_all = tk.PhotoImage()
        self.img_unselect_all = tk.PhotoImage()
        self.img_fav = tk.PhotoImage()
        self.img_unfav = tk.PhotoImage()
        self.img_add_to_group = tk.PhotoImage()
        self.img_remove_from_group = tk.PhotoImage()
        self.img_delete = tk.PhotoImage()
        self.img_settings = tk.PhotoImage()

        # Вспомогательные массивы для ScrollFrame для вкладки печати
        self.print_keys = []
        self.print_selected_keys = []
        self.print_frames = []
        self.print_buttons = []
        self.print_tips = []
        # Вспомогательные массивы для ScrollFrame для вкладки поиска
        self.search_keys = []
        self.search_selected_keys = []
        self.search_frames = []
        self.search_buttons = []

        self._configure_window()
        self._add_validation()
        self._create_widgets()
        self._create_tips()
        self._create_bindings()

        self.print_print(True)  # Выводим статьи
        self.search_print(True)  # Выводим статьи

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Словарь "{self.dct_info.dct.name}"')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _add_validation(self):
        def print_validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.print_count_pages)
            if res and value != '' and int(value) != self.print_current_page:
                self.print_go_to_page_with_number(int(value))
            return res

        def validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.search_count_pages)
            if res and value != '' and int(value) != self.search_current_page:
                self.search_go_to_page_with_number(int(value))
            return res

        self.vcmd_print_page = (self.register(print_validate_and_goto_page_number), '%P')
        self.vcmd_page = (self.register(validate_and_goto_page_number), '%P')

    def _create_widgets(self):
        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tabs.grid(row=0, column=0, padx=0, pady=0)

        self._create_print_tab()
        self._create_search_tab()

        self.tab_add = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_add, text='Добавить запись в словарь')

    def _create_print_tab(self):
        self.tab_print = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_print, text='Просмотр словаря')

        self._create_print_menu_frame()
        self._create_print_main_frame()

    def _create_print_menu_frame(self):
        self.frame_print_menu = create_frame(
            self.tab_print, 'Invis.TFrame',
            row=0, column=0, padx=6, pady=(6, 0), sticky='W')

        self._create_print_header_frame()
        self._create_print_buttons_for_selected_frame()
        self._create_print_selection_buttons_frame()
        self.lbl_print_info = create_label(
            self.frame_print_menu,
            textvariable=self.var_print_info,
            row=2, column=0, padx=0, pady=0)
        self.lbl_print_info_selected = create_label(
            self.frame_print_menu, justify='left',
            textvariable=self.var_print_info_selected,
            row=2, column=1, padx=(6, 0), pady=0, sticky='W')

    def _create_print_header_frame(self):
        self.frame_print_header = create_frame(
            self.frame_print_menu, 'Invis.TFrame',
            row=0, rowspan=2, column=0, padx=0, pady=0)

        self.btn_print_about_window = create_button(
            self.frame_print_header, self.about_window, width=2,
            row=0, column=0, padx=0, pady=0)
        set_image(self.btn_print_about_window, self.img_about, img_about, '?')
        self.btn_print_print_out = create_button(
            self.frame_print_header, self.print_out,
            row=1, column=0, padx=0, pady=0)
        set_image(self.btn_print_print_out, self.img_print_out, img_print_out, 'Распечатать')
        self._create_print_parameters_frame()

    def _create_print_parameters_frame(self):
        self.frame_print_parameters = create_frame(
            self.frame_print_header,
            row=0, rowspan=2, column=1, padx=(6, 0), pady=0)

        self.lbl_print_fav = create_label(
            self.frame_print_parameters, 'Только избр.:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_print_fav = create_checkbutton(
            self.frame_print_parameters, self.var_print_fav,
            command=lambda: self.print_go_to_first_page(True),
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_print_group = create_label(
            self.frame_print_parameters, 'Группа:',
            row=0, column=2, padx=(0, 1), pady=6, sticky='E')
        self.combo_print_group = create_combobox(
            self.frame_print_parameters, self.var_print_group,
            [ALL_GROUPS] + self.dct_info.dct.groups, 28,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale),
            state='readonly',
            row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        self.lbl_print_briefly = create_label(
            self.frame_print_parameters, 'Кратко:',
            row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_print_briefly = create_checkbutton(
            self.frame_print_parameters, self.var_print_briefly,
            command=lambda: self.print_print(True),
            row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_print_order = create_label(
            self.frame_print_parameters, 'Порядок:',
            row=1, column=2, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_print_order = create_combobox(
            self.frame_print_parameters, self.var_print_order, PRINT_VALUES_ORDER, 28,
            font=('DejaVu Sans Mono', self.app_data.gui_settings.scale), state='readonly',
            row=1, column=3, padx=(0, 6), pady=(0, 6), sticky='W')

    def _create_print_buttons_for_selected_frame(self):
        self.frame_print_buttons_for_selected = create_frame(self.frame_print_menu)

        self.btn_print_fav = create_button(
            self.frame_print_buttons_for_selected,
            lambda: self.fav_selected(self.print_selected_keys),
            width=3,
            row=0, column=0)
        set_image(self.btn_print_fav, self.img_fav, img_fav, '*+')
        self.btn_print_unfav = create_button(
            self.frame_print_buttons_for_selected,
            lambda: self.unfav_selected(self.print_selected_keys),
            width=3,
            row=0, column=1)
        set_image(self.btn_print_unfav, self.img_unfav, img_unfav, '*-')
        self.btn_print_add_to_group = create_button(
            self.frame_print_buttons_for_selected,
            lambda: self.add_selected_to_group(self.print_selected_keys),
            width=3,
            row=0, column=2)
        set_image(self.btn_print_add_to_group, self.img_add_to_group, img_add_to_group, 'G+')
        self.btn_print_remove_from_group = create_button(
            self.frame_print_buttons_for_selected,
            lambda: self.remove_selected_from_group(self.print_selected_keys),
            width=3,
            row=0, column=3)
        set_image(self.btn_print_remove_from_group, self.img_remove_from_group,
                  img_remove_from_group, 'G-')
        self.btn_print_delete = create_button(
            self.frame_print_buttons_for_selected,
            lambda: self.delete_selected(self.print_selected_keys),
            width=3,
            row=0, column=4)
        set_image(self.btn_print_delete, self.img_delete, img_trashcan, 'DEL')

    def _create_print_selection_buttons_frame(self):
        self.frame_print_selection_buttons = create_frame(
            self.frame_print_menu,
            row=1, column=1, padx=(6, 0), pady=0, sticky='WS')

        self.btn_print_select_page = create_button(
            self.frame_print_selection_buttons, self.print_select_page, width=3,
            row=0, column=0)
        set_image(self.btn_print_select_page, self.img_select_page, img_select_page, '[X]')
        self.btn_print_unselect_page = create_button(
            self.frame_print_selection_buttons, self.print_unselect_page, width=3,
            row=0, column=1)
        set_image(self.btn_print_unselect_page, self.img_unselect_page, img_unselect_page, '[ ]')
        self.btn_print_select_all = create_button(
            self.frame_print_selection_buttons, self.print_select_all, width=3,
            row=0, column=2)
        set_image(self.btn_print_select_all, self.img_select_all, img_select_all, '[X]')
        self.btn_print_unselect_all = create_button(
            self.frame_print_selection_buttons, self.print_unselect_all, width=3,
            row=0, column=3)
        set_image(self.btn_print_unselect_all, self.img_unselect_all, img_unselect_all, '[ ]')

    def _create_print_main_frame(self):
        self.frame_print_main = create_frame(
            self.tab_print, 'Invis.TFrame',
            row=1, column=0, padx=6, pady=6)

        self.scrolled_frame_print = ScrollFrame(
            self.frame_print_main, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_print.grid(
            row=0, column=0, padx=0, pady=(0, 6))
        self._create_print_page_buttons_frame()

    def _create_print_page_buttons_frame(self):
        self.frame_print_page_buttons = create_frame(
            self.frame_print_main, 'Invis.TFrame',
            row=1, column=0, padx=0, pady=0)

        self.btn_print_first_page = create_button(
            self.frame_print_page_buttons, self.print_go_to_first_page, width=2,
            row=0, column=0, padx=3, pady=0)
        set_image(self.btn_print_first_page, self.img_double_arrow_left,
                  img_double_arrow_left, '<<')
        self.btn_print_prev_page = create_button(
            self.frame_print_page_buttons, self.print_go_to_prev_page, width=2,
            row=0, column=1, padx=3, pady=0)
        set_image(self.btn_print_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self._create_print_current_page_frame()
        self.btn_print_next_page = create_button(
            self.frame_print_page_buttons, self.print_go_to_next_page, width=2,
            row=0, column=3, padx=3, pady=0)
        set_image(self.btn_print_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_print_last_page = create_button(
            self.frame_print_page_buttons, self.print_go_to_last_page, width=2,
            row=0, column=4, padx=3, pady=0)
        set_image(self.btn_print_last_page, self.img_double_arrow_right,
                  img_double_arrow_right, '>>')

    def _create_print_current_page_frame(self):
        self.frame_print_current_page = create_frame(
            self.frame_print_page_buttons, 'Invis.TFrame',
            row=0, column=2, padx=3, pady=0)

        self.lbl_print_current_page_1 = create_label(
            self.frame_print_current_page, 'Страница',
            row=0, column=0, padx=0, pady=0)
        self.entry_print_current_page = create_entry(
            self.frame_print_current_page, self.var_print_current_page, 3,
            font=self.app_data, justify='center',
            validate='key', validatecommand=self.vcmd_print_page,
            row=0, column=1, padx=3, pady=0)
        self.lbl_print_current_page_2 = create_label(
            self.frame_print_current_page, 'из 1',
            row=0, column=2, padx=0, pady=0)

    def _create_search_tab(self):
        self.tab_search = create_frame(self.tabs, 'Invis.TFrame')
        self.tabs.add(self.tab_search, text='Поиск')

        self._create_search_header_frame()
        self._create_search_main_frame()

    def _create_search_header_frame(self):
        self.frame_search_header = create_frame(
            self.tab_search, 'Invis.TFrame',
            row=0, column=0, padx=6, pady=(6, 0), sticky='W')

        self._create_search_query_frame()
        self._create_search_selection_button()
        self._create_search_info_frame()
        self.lbl_search_info_selected = create_label(
            self.frame_search_header, textvariable=self.var_search_info_selected,
            row=1, column=1, padx=0, pady=0, sticky='E')
        self._create_search_buttons_for_selected_frame()

    def _create_search_query_frame(self):
        self.frame_search_query = create_frame(
            self.frame_search_header,
            row=0, column=0, columnspan=2, padx=0, pady=(0, 6))

        self.btn_search_search_settings = create_button(
            self.frame_search_query, self.search_settings, width=9,
            row=0, column=0, padx=(6, 3), pady=6)
        set_image(self.btn_search_search_settings, self.img_settings, img_edit, 'Настройки')
        self.entry_search_query = create_entry(
            self.frame_search_query, self.var_search_query, 50, font=self.app_data,
            row=0, column=1, padx=(0, 1), pady=6)
        self.btn_search_search = create_button(
            self.frame_search_query, lambda: self.search_go_to_first_page(True),
            'Поиск', width=6,
            row=0, column=2, padx=(0, 6), pady=6)

    def _create_search_selection_button(self):
        self.frame_search_selection_buttons = create_frame(
            self.frame_search_header,
            row=0, column=2, padx=(6, 0), pady=(0, 6), sticky='WS')

        self.btn_search_select_page = create_button(
            self.frame_search_selection_buttons, self.search_select_page, width=3,
            row=0, column=0)
        set_image(self.btn_search_select_page, self.img_select_page, img_select_page, '[X]')
        self.btn_search_unselect_page = create_button(
            self.frame_search_selection_buttons, self.search_unselect_page, width=3,
            row=0, column=1)
        set_image(self.btn_search_unselect_page, self.img_unselect_page, img_unselect_page, '[ ]')
        self.btn_search_select_all = create_button(
            self.frame_search_selection_buttons, self.search_select_all, width=3,
            row=0, column=2)
        set_image(self.btn_search_select_all, self.img_select_all, img_select_all, '[X]')
        self.btn_search_unselect_all = create_button(
            self.frame_search_selection_buttons, self.search_unselect_all, width=3,
            row=0, column=3)
        set_image(self.btn_search_unselect_all, self.img_unselect_all, img_unselect_all, '[ ]')

    def _create_search_info_frame(self):
        self.frame_search_info = create_frame(
            self.frame_search_header, 'Invis.TFrame',
            row=1, column=0, padx=(6, 0), pady=0, sticky='W')

        self.btn_search_about_window = create_button(
            self.frame_search_info, self.about_window, width=2,
            row=0, column=0, padx=0, pady=0)
        set_image(self.btn_search_about_window, self.img_about, img_about, '?')
        self.lbl_search_info = create_label(
            self.frame_search_info, textvariable=self.var_search_info,
            row=0, column=1, padx=0, pady=0)

    def _create_search_buttons_for_selected_frame(self):
        self.frame_search_buttons_for_selected = create_frame(self.frame_search_header)

        self.btn_search_fav = create_button(
            self.frame_search_buttons_for_selected,
            lambda: self.fav_selected(self.search_selected_keys),
            width=3,
            row=0, column=0)
        set_image(self.btn_search_fav, self.img_fav, img_fav, '*+')
        self.btn_search_unfav = create_button(
            self.frame_search_buttons_for_selected,
            lambda: self.unfav_selected(self.search_selected_keys),
            width=3,
            row=0, column=1)
        set_image(self.btn_search_unfav, self.img_unfav, img_unfav, '*-')
        self.btn_search_add_to_group = create_button(
            self.frame_search_buttons_for_selected,
            lambda: self.add_selected_to_group(self.search_selected_keys),
            width=3,
            row=0, column=2)
        set_image(self.btn_search_add_to_group, self.img_add_to_group, img_add_to_group, 'G+')
        self.btn_search_remove_from_group = create_button(
            self.frame_search_buttons_for_selected,
            lambda: self.remove_selected_from_group(self.search_selected_keys),
            width=3,
            row=0, column=3)
        set_image(self.btn_search_remove_from_group, self.img_remove_from_group,
                  img_remove_from_group, 'G-')
        self.btn_search_delete = create_button(
            self.frame_search_buttons_for_selected,
            lambda: self.delete_selected(self.search_selected_keys),
            width=3,
            row=0, column=4)
        set_image(self.btn_search_delete, self.img_delete, img_trashcan, 'DEL')

    def _create_search_main_frame(self):
        self.frame_search_main = create_frame(
            self.tab_search, 'Invis.TFrame',
            row=1, column=0, padx=6, pady=6)

        self.scrolled_frame_search = ScrollFrame(
            self.frame_search_main, self.app_data,
            SCALE_DEFAULT_FRAME_HEIGHT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_DEFAULT_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
        self.scrolled_frame_search.grid(
            row=0, column=0, padx=0, pady=(0, 6))
        self._create_search_page_buttons()

    def _create_search_page_buttons(self):
        self.frame_search_page_buttons = create_frame(
            self.frame_search_main, 'Invis.TFrame',
            row=1, column=0, padx=0, pady=0)

        self.btn_search_first_page = create_button(
            self.frame_search_page_buttons, self.search_go_to_first_page, width=2,
            row=0, column=0, padx=3, pady=0)
        set_image(self.btn_search_first_page, self.img_double_arrow_left,
                  img_double_arrow_left, '<<')
        self.btn_search_prev_page = create_button(
            self.frame_search_page_buttons, self.search_go_to_prev_page, width=2,
            row=0, column=1, padx=3, pady=0)
        set_image(self.btn_search_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self._create_search_current_page()
        self.btn_search_next_page = create_button(
            self.frame_search_page_buttons, self.search_go_to_next_page, width=2,
            row=0, column=3, padx=3, pady=0)
        set_image(self.btn_search_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_search_last_page = create_button(
            self.frame_search_page_buttons, self.search_go_to_last_page, width=2,
            row=0, column=4, padx=3, pady=0)
        set_image(self.btn_search_last_page, self.img_double_arrow_right,
                  img_double_arrow_right, '>>')

    def _create_search_current_page(self):
        self.frame_search_current_page = create_frame(
            self.frame_search_page_buttons, 'Invis.TFrame',
            row=0, column=2, padx=3, pady=0)

        self.lbl_search_current_page_1 = create_label(
            self.frame_search_current_page, 'Страница',
            row=0, column=0, padx=0, pady=0)
        self.entry_search_current_page = create_entry(
            self.frame_search_current_page, self.var_search_current_page, 3,
            font=self.app_data, justify='center',
            validate='key', validatecommand=self.vcmd_page,
            row=0, column=1, padx=3, pady=0)
        self.lbl_search_current_page_2 = create_label(
            self.frame_search_current_page, 'из 1',
            row=0, column=2, padx=0, pady=0)

    def _create_tips(self):
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_print_about_window, 'Справка', hover_delay=450)
        self.tip_btn_print_out = ttip.Hovertip(
            self.btn_print_print_out, 'Распечатать словарь в файл', hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(
            self.btn_print_fav,
            'Добавить выделенные статьи в избранное\n'
            'Alt+F',
            hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(
            self.btn_print_unfav,
            'Убрать выделенные статьи из избранного\n'
            'Alt+Shift+F',
            hover_delay=450)
        self.tip_btn_add_to_group = ttip.Hovertip(
            self.btn_print_add_to_group,
            'Добавить выделенные статьи в группу\n'
            'Alt+G',
            hover_delay=450)
        self.tip_btn_remove_from_group = ttip.Hovertip(
            self.btn_print_remove_from_group,
            'Убрать выделенные статьи из группы\n'
            'Alt+Shift+G',
            hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(
            self.btn_print_delete,
            'Удалить выделенные статьи\n'
            'Alt+D',
            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(
            self.btn_print_select_page,
            'Выделить все статьи на текущей странице\n'
            'Alt+P',
            hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(
            self.btn_print_unselect_page,
            'Снять выделение со всех статей на текущей странице\n'
            'Alt+Shift+P',
            hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(
            self.btn_print_select_all,
            'Выделить все статьи\n'
            'Alt+A',
            hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(
            self.btn_print_unselect_all,
            'Снять выделение со всех статей\n'
            'Alt+Shift+A',
            hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(
            self.btn_print_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(
            self.btn_print_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(
            self.btn_print_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(
            self.btn_print_last_page, 'В конец', hover_delay=650)
        self.tip_btn_about_window = ttip.Hovertip(
            self.btn_search_about_window, 'Справка', hover_delay=450)
        self.tip_btn_search_settings = ttip.Hovertip(
            self.btn_search_search_settings, 'Параметры поиска', hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(
            self.btn_search_fav,
            'Добавить выделенные статьи в избранное\n'
            'Alt+F',
            hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(
            self.btn_search_unfav,
            'Убрать выделенные статьи из избранного\n'
            'Alt+Shift+F',
            hover_delay=450)
        self.tip_btn_add_to_group = ttip.Hovertip(
            self.btn_search_add_to_group,
            'Добавить выделенные статьи в группу\n'
            'Alt+G',
            hover_delay=450)
        self.tip_btn_remove_from_group = ttip.Hovertip(
            self.btn_search_remove_from_group,
            'Убрать выделенные статьи из группы\n'
            'Alt+Shift+G',
            hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(
            self.btn_search_delete,
            'Удалить выделенные статьи\n'
            'Alt+D',
            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(
            self.btn_search_select_page,
            'Выделить все статьи на текущей странице\n'
            'Alt+P',
            hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(
            self.btn_search_unselect_page,
            'Снять выделение со всех статей на текущей странице\n'
            'Alt+Shift+P',
            hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(
            self.btn_search_select_all,
            'Выделить все статьи\n'
            'Alt+A',
            hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(
            self.btn_search_unselect_all,
            'Снять выделение со всех статей\n'
            'Alt+Shift+A',
            hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(
            self.btn_search_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(
            self.btn_search_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(
            self.btn_search_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(
            self.btn_search_last_page, 'В конец', hover_delay=650)

    def _create_bindings(self):
        self.combo_print_order.bind('<<ComboboxSelected>>', lambda event: self.print_print(False))
        self.combo_print_group.bind(
            '<<ComboboxSelected>>',
            lambda event: self.print_go_to_first_page(True),
        )

    # Нажатие на кнопку "Распечатать словарь в файл"
    def print_out(self):
        folder = askdirectory(initialdir=MAIN_PATH, title='В какую папку сохранить файл?')
        if not folder:
            return
        filename = f'Распечатка_{self.dct_info.dct.name}.txt'
        self.dct_info.dct.to_txt(os.path.join(folder, filename))

    # Нажатие на кнопку "Настройки поиска"
    def search_settings(self):
        window = SearchSettingsW(
            self, self.app_data, self.dct_info, self.to_search_only_fav,
            self.to_search_only_full, self.to_search_wrd, self.to_search_tr,
            self.to_search_frm, self.to_search_phr, self.to_search_nt,
            self.search_group,
        )
        self.to_search_only_fav, self.to_search_only_full, self.to_search_wrd, \
            self.to_search_tr, self.to_search_frm, self.to_search_phr, \
            self.to_search_nt, self.search_group = window.open()

    # Изменить статью
    def edit_entry(self, key: EntryID):
        EditW(self, self.app_data, key).open()

        self.search_print(False)
        self.print_print(False)

    # Вывести информацию о количестве статей (1)
    def print_print_info(self):
        group = self.var_print_group.get()
        if group == ALL_GROUPS:
            if self.var_print_fav.get():
                w, t, gf, wf = self.dct_info.dct.count_fav_entries()
                info = dct_info_fav(
                    (w, self.dct_info.dct.count('lemmas')),
                    (t, self.dct_info.dct.count('translations')),
                    (gf, self.dct_info.dct.count('gram_forms')),
                    (wf, self.dct_info.dct.count('word_forms')),
                )
            else:
                info = dct_info(
                    self.dct_info.dct.count('lemmas'),
                    self.dct_info.dct.count('translations'),
                    self.dct_info.dct.count('gram_forms'),
                    self.dct_info.dct.count('word_forms'),
                )
        else:
            if self.var_print_fav.get():
                w1, t1, gf1, wf1 = self.dct_info.dct.count_fav_entries(group)
                w2, t2, gf2, wf2 = self.dct_info.dct.count_entries_in_group(group)
                info = dct_info_fav((w1, w2), (t1, t2), (gf1, gf2), (wf1, wf2))
            else:
                w, t, gf, wf = self.dct_info.dct.count_entries_in_group(group)
                info = dct_info(w, t, gf, wf)
        self.var_print_info.set(info)

        count_selected = len(self.print_selected_keys)
        if count_selected == 0:
            info_selected = ''
        else:
            tmp_1 = set_postfix(count_selected, ('Выделена', 'Выделены', 'Выделено'))
            tmp_2 = set_postfix(count_selected, ('статья', 'статьи', 'статей'))
            info_selected = f'{tmp_1} {count_selected} {tmp_2}'
        self.var_print_info_selected.set(info_selected)

    # Вывести информацию о количестве статей (2)
    def search_print_info(self):
        tmp_1 = set_postfix(self.search_count_elements, ('Найдена', 'Найдены', 'Найдено'))
        tmp_2 = set_postfix(self.search_count_elements, ('статья', 'статьи', 'статей'))
        info = f'{tmp_1} {self.search_count_elements} {tmp_2}'
        self.var_search_info.set(info)

        count_selected = len(self.search_selected_keys)
        if count_selected == 0:
            info_selected = ''
        else:
            tmp_1 = set_postfix(count_selected, ('Выделена', 'Выделены', 'Выделено'))
            tmp_2 = set_postfix(count_selected, ('статья', 'статьи', 'статей'))
            info_selected = f'{tmp_1} {count_selected} {tmp_2}'
        self.var_search_info_selected.set(info_selected)

    # Напечатать словарь
    def print_print(self, move_scroll: bool):
        # Удаляем старые подсказки
        for tip in self.print_tips:
            tip.__del__()
        # Удаляем старые кнопки
        for btn in self.print_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.print_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Button-2>')
            fr.unbind('<Button-3>')
            fr.destroy()

        # Выбираем нужные статьи
        group = self.var_print_group.get()
        if self.var_print_fav.get():
            if group == ALL_GROUPS:
                self.print_keys = [
                    key for key in self.dct_info.dct.get_entry_ids()
                    if self.dct_info.dct[key].is_fav
                ]
            else:
                self.print_keys = [
                    key for key in self.dct_info.dct.get_entry_ids()
                    if self.dct_info.dct[key].is_fav and group in self.dct_info.dct[key].groups
                ]
        else:
            if group == ALL_GROUPS:
                self.print_keys = [key for key in self.dct_info.dct.get_entry_ids()]
            else:
                self.print_keys = [
                    key for key in self.dct_info.dct.get_entry_ids()
                    if group in self.dct_info.dct[key].groups
                ]
        self.print_selected_keys = [
            key for key in self.print_selected_keys
            if key in self.print_keys
        ]
        if not self.print_selected_keys:
            self.frame_print_buttons_for_selected.grid_remove()
        # Сортируем статьи
        if self.var_print_order.get() == PRINT_VALUES_ORDER[1]:
            self.print_keys.reverse()
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[2]:
            """
            self.print_keys.sort(key=lambda k: (
                self.dct_info.dct[k].accuracy,
                self.dct_info.dct[k].win_streak,
            ))
            """
            self.print_keys.sort(key=lambda k: (
                self.dct_info.dct[k].accuracy,
                self.dct_info.dct[k].win_streak / (1 + len(self.dct_info.dct[k].forms.keys()) +
                                                   len(self.dct_info.dct[k].phrases.keys())),
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[3]:
            """
            self.print_keys.sort(
                key=lambda k: (
                    self.dct_info.dct[k].accuracy,
                    self.dct_info.dct[k].win_streak,
                ),
                reverse=True,
            )
            """
            self.print_keys.sort(key=lambda k: (
                -self.dct_info.dct[k].accuracy,
                -self.dct_info.dct[k].win_streak / (1 + len(self.dct_info.dct[k].forms.keys()) +
                                                    len(self.dct_info.dct[k].phrases.keys())),
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[4]:
            self.print_keys.sort(key=lambda k: (
                self.dct_info.dct[k].latest_att_timestamp,
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[5]:
            self.print_keys.sort(key=lambda k: (
                [-val for val in self.dct_info.dct[k].latest_att_timestamp],
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[6]:
            self.print_keys.sort(key=lambda k: (
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[7]:
            self.print_keys.sort(
                key=lambda k: (
                    self.dct_info.dct[k].lemma.lower(),
                    self.dct_info.dct[k].lemma
                ),
                reverse=True,
            )
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[8]:
            self.print_keys.sort(key=lambda k: (
                len(self.dct_info.dct[k].lemma),
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[9]:
            self.print_keys.sort(key=lambda k: (
                -len(self.dct_info.dct[k].lemma),
                self.dct_info.dct[k].lemma.lower(),
                self.dct_info.dct[k].lemma,
            ))
        # Выводим информацию о количестве статей
        self.print_print_info()

        # Вычисляем значения некоторых количественных переменных
        self.print_count_elements = len(self.print_keys)
        if self.print_count_elements == 0:
            self.print_count_pages = 1
        else:
            self.print_count_pages = math.ceil(
                self.print_count_elements / self.print_max_elements_on_page
            )
        if self.print_current_page > self.print_count_pages:
            self.print_current_page = self.print_count_pages
            self.print_start_index = (self.print_count_pages - 1) * self.print_max_elements_on_page
        if self.print_current_page == self.print_count_pages:
            if self.print_count_elements % self.print_max_elements_on_page == 0 and\
                    self.print_count_elements != 0:
                self.print_count_elements_on_page = self.print_max_elements_on_page
            else:
                self.print_count_elements_on_page =\
                    self.print_count_elements % self.print_max_elements_on_page
        else:
            self.print_count_elements_on_page = self.print_max_elements_on_page
        # Выводим номер страницы
        self.var_print_current_page.set(str(self.print_current_page))
        self.entry_print_current_page.icursor(len(str(self.print_current_page)))
        self.lbl_print_current_page_2.configure(text=f'из {self.print_count_pages}')

        # Создаём новые фреймы
        self.print_frames = [
            create_frame(
                self.scrolled_frame_print.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.print_count_elements_on_page)
        ]
        # Создаём новые кнопки
        self.print_buttons = [
            create_button(
                self.print_frames[i],
                lambda i=i: self.edit_entry(self.print_keys[self.print_start_index + i]),
                style=(
                    ('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                    if self.print_keys[self.print_start_index + i] in self.print_selected_keys
                    else ('FlatD.TButton' if i % 2 else 'FlatL.TButton')
                ),
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.print_count_elements_on_page)
        ]
        # Создаём подсказки
        self.print_tips = [
            ttip.Hovertip(
                self.print_buttons[i],
                f'Верных ответов подряд: {get_correct_att_in_a_row(
                    self.dct_info.dct[self.print_keys[self.print_start_index + i]]
                )}\n'
                f'Доля верных ответов: {get_entry_percent(
                    self.dct_info.dct[self.print_keys[self.print_start_index + i]]
                )}',
                hover_delay=666,
            ) for i in range(self.print_count_elements_on_page)
        ]
        # Выводим текст на кнопки
        if self.var_print_briefly.get():
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(
                    text=get_entry_info_briefly(self.dct_info.dct[key], 75)
                )
        else:
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(
                    text=get_entry_info_detailed(self.dct_info.dct[key], 75)
                )

        for i in range(self.print_count_elements_on_page):
            # Привязываем события
            self.print_frames[i].bind(
                '<Enter>',
                lambda event, i=i: self.print_frames[i].focus_set(),
            )
            self.print_buttons[i].bind('<Button-2>', lambda event, i=i: self.print_select_one(i))
            self.print_buttons[i].bind('<Button-3>', lambda event, i=i: self.print_select_one(i))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_print.canvas.yview_moveto(0.0)

    # Нажатие на кнопку "Поиск"
    def search_print(self, move_scroll: bool):
        # Удаляем старые кнопки
        for btn in self.search_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.search_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Button-2>')
            fr.unbind('<Button-3>')
            fr.destroy()

        # Выбираем нужные статьи
        # Если нужно, оставляем только избранные
        if self.to_search_only_fav:
            keys = [
                key for key in self.dct_info.dct.get_entry_ids()
                if self.dct_info.dct[key].is_fav
            ]
        else:
            keys = [key for key in self.dct_info.dct.get_entry_ids()]
        # Если нужно, оставляем только одну группу
        if self.search_group != ALL_GROUPS:
            keys = [key for key in keys if self.search_group in self.dct_info.dct[key].groups]
        # Среди оставшихся ищем статьи, содержащие искомый текст
        results = search_entries(
            self.dct_info.dct, tuple(keys), self.var_search_query.get(),
            self.to_search_wrd, self.to_search_tr, self.to_search_frm,
            self.to_search_phr, self.to_search_nt,
        )
        # Объединяем результаты в один список
        self.search_keys = []
        for i in range(6 if self.to_search_only_full else 9):
            self.search_keys += sorted(
                list(results[i]),
                key=lambda k: (self.dct_info.dct[k].lemma.lower(), self.dct_info.dct[k].lemma),
            )
        # Из выделенных статей оставляем, только удовлетворяющие поисковому запросу
        self.search_selected_keys = [
            key for key in self.search_selected_keys if key in self.search_keys
        ]
        # Если выделенных статей нет, убираем связанные с ними кнопки
        if not self.search_selected_keys:
            self.frame_search_buttons_for_selected.grid_remove()

        # Вычисляем значения некоторых количественных переменных
        self.search_count_elements = len(self.search_keys)
        if self.search_count_elements == 0:
            self.search_count_pages = 1
        else:
            self.search_count_pages = math.ceil(
                self.search_count_elements / self.search_max_elements_on_page
            )
        if self.search_current_page > self.search_count_pages:
            self.search_current_page = self.search_count_pages
            self.search_start_index =\
                (self.search_count_pages - 1) * self.search_max_elements_on_page
        if self.search_current_page == self.search_count_pages:
            if self.search_count_elements % self.search_max_elements_on_page == 0 and\
                    self.search_count_elements != 0:
                self.search_count_elements_on_page = self.search_max_elements_on_page
            else:
                self.search_count_elements_on_page =\
                    self.search_count_elements % self.search_max_elements_on_page
        else:
            self.search_count_elements_on_page = self.search_max_elements_on_page
        # Выводим информацию о количестве статей
        self.search_print_info()
        # Выводим номер страницы
        self.var_search_current_page.set(str(self.search_current_page))
        self.entry_search_current_page.icursor(len(str(self.search_current_page)))
        self.lbl_search_current_page_2.configure(text=f'из {self.search_count_pages}')

        # Создаём новые фреймы
        self.search_frames = [
            create_frame(
                self.scrolled_frame_search.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.search_count_elements_on_page)
        ]
        # Создаём новые кнопки
        self.search_buttons = [
            create_button(
                self.search_frames[i],
                lambda i=i: self.edit_entry(self.search_keys[self.search_start_index + i]),
                get_all_entry_info(
                    self.dct_info.dct[self.search_keys[self.search_start_index + i]], 75, 13
                ),
                style=(
                    ('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                    if self.search_keys[self.search_start_index + i] in self.search_selected_keys
                    else ('FlatD.TButton' if i % 2 else 'FlatL.TButton')
                ),
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(self.search_count_elements_on_page)
        ]

        for i in range(self.search_count_elements_on_page):
            # Привязываем события
            self.search_frames[i].bind(
                '<Enter>', lambda event, i=i: self.search_frames[i].focus_set()
            )
            self.search_frames[i].bind(
                '<Leave>', lambda event, i=i: self.entry_search_query.focus_set()
            )
            self.search_buttons[i].bind('<Button-2>', lambda event, i=i: self.search_select_one(i))
            self.search_buttons[i].bind('<Button-3>', lambda event, i=i: self.search_select_one(i))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_search.canvas.yview_moveto(0.0)

    # Обновить одну из кнопок журнала (1)
    def print_refresh_one_button(self, index: int):
        # Выводим текст на кнопку
        if self.var_print_briefly.get():
            key = self.print_keys[self.print_start_index + index]
            self.print_buttons[index].configure(
                text=get_entry_info_briefly(self.dct_info.dct[key], 75)
            )
        else:
            key = self.print_keys[self.print_start_index + index]
            self.print_buttons[index].configure(
                text=get_entry_info_detailed(self.dct_info.dct[key], 75)
            )

        # Выводим информацию о количестве статей
        self.print_print_info()

    # Обновить одну из кнопок журнала (2)
    def search_refresh_one_button(self, index: int, key: EntryID):
        # Выводим текст на кнопку
        self.search_buttons[index].configure(
            text=get_all_entry_info(self.dct_info.dct[key], 75, 13)
        )

        # Выводим информацию о количестве статей
        self.search_print_info()

    # Обновить все кнопки журнала (1)
    def print_refresh_all_buttons(self):
        # Выводим текст на кнопки
        if self.var_print_briefly.get():
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(
                    text=get_entry_info_briefly(self.dct_info.dct[key], 75)
                )
        else:
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(
                    text=get_entry_info_detailed(self.dct_info.dct[key], 75)
                )

    # Обновить все кнопки журнала (2)
    def search_refresh_all_buttons(self):
        # Выводим текст на кнопки
        for i in range(self.search_count_elements_on_page):
            key = self.search_keys[self.search_start_index + i]
            self.search_buttons[i].configure(
                text=get_all_entry_info(self.dct_info.dct[key], 75, 13)
            )

        # Выводим информацию о количестве статей
        self.search_print_info()

    # Перейти на страницу с заданным номером (1)
    def print_go_to_page_with_number(self, number: int):
        self.print_current_page = number
        self.print_start_index = (self.print_current_page - 1) * self.print_max_elements_on_page
        self.print_print(True)

    # Перейти на страницу с заданным номером (2)
    def search_go_to_page_with_number(self, number: int):
        self.search_current_page = number
        self.search_start_index = (self.search_current_page - 1) * self.search_max_elements_on_page
        self.search_print(True)

    # Перейти на предыдущую страницу (1)
    def print_go_to_prev_page(self):
        if self.print_current_page != 1:
            self.print_go_to_page_with_number(self.print_current_page - 1)

    # Перейти на предыдущую страницу (2)
    def search_go_to_prev_page(self):
        if self.search_current_page != 1:
            self.search_go_to_page_with_number(self.search_current_page - 1)

    # Перейти на следующую страницу (1)
    def print_go_to_next_page(self):
        if self.print_current_page != self.print_count_pages:
            self.print_go_to_page_with_number(self.print_current_page + 1)

    # Перейти на следующую страницу (2)
    def search_go_to_next_page(self):
        if self.search_current_page != self.search_count_pages:
            self.search_go_to_page_with_number(self.search_current_page + 1)

    # Перейти на первую страницу (1)
    def print_go_to_first_page(self, to_reset_selected_keys: bool = False):
        if to_reset_selected_keys:
            self.print_selected_keys = []
            self.frame_print_buttons_for_selected.grid_remove()
        self.print_go_to_page_with_number(1)

    # Перейти на первую страницу (2)
    def search_go_to_first_page(self, to_reset_selected_keys: bool = False):
        if to_reset_selected_keys:
            self.search_selected_keys = []
            self.frame_search_buttons_for_selected.grid_remove()
        self.search_go_to_page_with_number(1)

    # Перейти на последнюю страницу (1)
    def print_go_to_last_page(self):
        self.print_go_to_page_with_number(self.print_count_pages)

    # Перейти на последнюю страницу (2)
    def search_go_to_last_page(self):
        self.search_go_to_page_with_number(self.search_count_pages)

    # Выделить одну статью (или убрать выделение) (1)
    def print_select_one(self, index: int):
        key = self.print_keys[self.print_start_index + index]
        if key in self.print_selected_keys:
            self.print_selected_keys.remove(key)
            self.print_buttons[index].configure(
                style='FlatD.TButton' if index % 2 else 'FlatL.TButton'
            )
            if not self.print_selected_keys:
                self.frame_print_buttons_for_selected.grid_remove()
        else:
            self.print_selected_keys += [key]
            self.print_buttons[index].configure(
                style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton'
            )
            self.frame_print_buttons_for_selected.grid(
                row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
            )
        self.print_print_info()

    # Выделить одну статью (или убрать выделение) (2)
    def search_select_one(self, index: int):
        key = self.search_keys[self.search_start_index + index]
        if key in self.search_selected_keys:
            self.search_selected_keys.remove(key)
            self.search_buttons[index].configure(
                style='FlatD.TButton' if index % 2 else 'FlatL.TButton'
            )
            if not self.search_selected_keys:
                self.frame_search_buttons_for_selected.grid_remove()
        else:
            self.search_selected_keys += [key]
            self.search_buttons[index].configure(
                style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton')
            self.frame_search_buttons_for_selected.grid(
                row=1, column=2, padx=(6, 0), pady=0, sticky='W'
            )
        self.search_print_info()

    # Выделить все статьи на странице (1)
    def print_select_page(self):
        for i in range(self.print_count_elements_on_page):
            key = self.print_keys[self.print_start_index + i]
            if key not in self.print_selected_keys:
                self.print_selected_keys += [key]
            btn = self.print_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_print_buttons_for_selected.grid(
            row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
        )
        self.print_print_info()

    # Выделить все статьи на странице (2)
    def search_select_page(self):
        for i in range(self.search_count_elements_on_page):
            key = self.search_keys[self.search_start_index + i]
            if key not in self.search_selected_keys:
                self.search_selected_keys += [key]
            btn = self.search_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_search_buttons_for_selected.grid(
            row=1, column=2, padx=(6, 0), pady=0, sticky='W'
        )
        self.search_print_info()

    # Снять выделение со всех статей на странице (1)
    def print_unselect_page(self):
        for i in range(self.print_count_elements_on_page):
            key = self.print_keys[self.print_start_index + i]
            if key in self.print_selected_keys:
                self.print_selected_keys.remove(key)
        for i in range(len(self.print_buttons)):
            btn = self.print_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        if not self.print_selected_keys:
            self.frame_print_buttons_for_selected.grid_remove()
        self.print_print_info()

    # Снять выделение со всех статей на странице (2)
    def search_unselect_page(self):
        for i in range(self.search_count_elements_on_page):
            key = self.search_keys[self.search_start_index + i]
            if key in self.search_selected_keys:
                self.search_selected_keys.remove(key)
        for i in range(len(self.search_buttons)):
            btn = self.search_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        if not self.search_selected_keys:
            self.frame_search_buttons_for_selected.grid_remove()
        self.search_print_info()

    # Выделить все статьи (1)
    def print_select_all(self):
        self.print_selected_keys = list(self.print_keys)
        for i in range(len(self.print_buttons)):
            btn = self.print_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_print_buttons_for_selected.grid(
            row=0, column=1, padx=(6, 0), pady=0, sticky='WS'
        )
        self.print_print_info()

    # Выделить все статьи (2)
    def search_select_all(self):
        self.search_selected_keys = list(self.search_keys)
        for i in range(len(self.search_buttons)):
            btn = self.search_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_search_buttons_for_selected.grid(
            row=1, column=2, padx=(6, 0), pady=0, sticky='W'
        )
        self.search_print_info()

    # Снять выделение со всех статей (1)
    def print_unselect_all(self):
        self.print_selected_keys = []
        for i in range(len(self.print_buttons)):
            btn = self.print_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        self.frame_print_buttons_for_selected.grid_remove()
        self.print_print_info()

    # Снять выделение со всех статей (2)
    def search_unselect_all(self):
        self.search_selected_keys = []
        for i in range(len(self.search_buttons)):
            btn = self.search_buttons[i]
            btn.configure(style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
        self.frame_search_buttons_for_selected.grid_remove()
        self.search_print_info()

    # Добавить выделенные статьи в избранное
    def fav_selected(self, keys: list[EntryID]):
        if not keys:
            return

        self.dct_info.dct.add_to_fav(tuple(keys))

        self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

    # Убрать выделенные статьи из избранного
    def unfav_selected(self, keys: list[EntryID]):
        if not keys:
            return

        self.dct_info.dct.remove_from_fav(tuple(keys))

        self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

    # Добавить выделенные статьи в группу
    def add_selected_to_group(self, keys: list[EntryID]):
        if not keys:
            return
        if not self.dct_info.dct.groups:
            PopupMsgW(self, self.app_data, 'Не найдено ни одной группы!').open()
            return

        sets = [self.dct_info.dct[key].groups for key in keys]
        values_intersec = set.intersection(*sets)
        values = [gr for gr in self.dct_info.dct.groups if gr not in values_intersec]
        if not values:
            PopupMsgW(
                self, self.app_data,
                'Выделенные статьи уже состоят во всех группах!',
            ).open()
            return
        window_groups = PopupChooseW(
            self, self.app_data,
            msg='Выберите группу, в которую хотите добавить выбранные слова:',
            values=values,
            default_value=self.dct_info.dct.groups[0],
        )
        closed, group = window_groups.open()
        if closed:
            return
        self.dct_info.dct.add_entries_to_group(group, tuple(keys))

        if group == self.var_print_group.get():
            self.print_print(True)
        else:
            self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

    # Убрать выделенные статьи из группы
    def remove_selected_from_group(self, keys: list[EntryID]):
        if not keys:
            return
        if not self.dct_info.dct.groups:
            PopupMsgW(self, self.app_data, 'Не найдено ни одной группы!').open()
            return

        values = []
        for key in keys:
            for gr in self.dct_info.dct[key].groups:
                if gr not in values:
                    values += [gr]
        if not values:
            PopupMsgW(
                self, self.app_data,
                'Выделенные статьи не состоят ни в каких группах!',
            ).open()
            return
        if self.var_print_group.get() == ALL_GROUPS or self.tabs.index(self.tabs.select()) == 1:
            default_value = values[0]
        else:
            default_value = self.var_print_group.get()
        window_groups = PopupChooseW(
            self, self.app_data,
            msg='Выберите группу, из которой хотите убрать выбранные слова:',
            values=values,
            default_value=default_value,
        )
        closed, group = window_groups.open()
        if closed:
            return
        self.dct_info.dct.remove_entries_from_group(group, tuple(keys))

        if group == self.var_print_group.get():
            self.print_print(True)
        else:
            self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

    # Удалить выделенные статьи
    def delete_selected(self, keys: list[EntryID]):
        if not keys:
            return

        count_selected = len(keys)
        tmp = set_postfix(count_selected, ('статью', 'статьи', 'статей'))
        window = PopupDialogueW(
            self, self.app_data,
            f'Вы действительно хотите удалить {count_selected} {tmp}?',
            set_enter_on_btn='none',
        )
        answer = window.open()
        if not answer:
            return

        for key in keys:
            self.dct_info.dct.delete_entry(key)

        self.print_print(True)
        self.search_print(True)

    # Справка об окне
    def about_window(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы прокрутить в самый низ, нажмите Ctrl+D или DOWN\n'
            '* Чтобы прокрутить в самый верх, нажмите Ctrl+U или UP\n'
            '* Чтобы выделить статью, наведите на неё мышку и нажмите ПКМ',
            msg_justify='left',
        ).open()

    # Нажатие на кнопку "Добавить запись в словарь"
    def add_entry(self):
        key = AddW(self, self.app_data).open()
        if not key:
            return
        EditW(self, self.app_data, key).open()

        self.search_print(False)
        self.print_print(False)

    # Установить фокус (вкладка "Просмотр словаря")
    def set_focus_print(self):
        self.focus_set()

        self.unbind('<Return>')

        bind_ctrl_a(self.entry_print_current_page)
        self.bind('<Up>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(0.0))
        self.bind('<Control-u>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(0.0))
        self.bind('<Control-U>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(0.0))
        self.bind('<Down>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(1.0))
        self.bind('<Control-d>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(1.0))
        self.bind('<Control-D>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(1.0))
        self.bind('<Alt-Shift-p>', lambda event: self.print_unselect_page())
        self.bind('<Alt-Shift-P>', lambda event: self.print_unselect_page())
        self.bind('<Alt-Shift-a>', lambda event: self.print_unselect_all())
        self.bind('<Alt-Shift-A>', lambda event: self.print_unselect_all())
        self.bind('<Alt-Shift-g>', lambda event: self.remove_selected_from_group(self.print_selected_keys))
        self.bind('<Alt-Shift-G>', lambda event: self.remove_selected_from_group(self.print_selected_keys))
        self.bind('<Alt-Shift-f>', lambda event: self.unfav_selected(self.print_selected_keys))
        self.bind('<Alt-Shift-F>', lambda event: self.unfav_selected(self.print_selected_keys))
        self.bind('<Alt-p>', lambda event: self.print_select_page())
        self.bind('<Alt-P>', lambda event: self.print_select_page())
        self.bind('<Alt-a>', lambda event: self.print_select_all())
        self.bind('<Alt-A>', lambda event: self.print_select_all())
        self.bind('<Alt-g>', lambda event: self.add_selected_to_group(self.print_selected_keys))
        self.bind('<Alt-G>', lambda event: self.add_selected_to_group(self.print_selected_keys))
        self.bind('<Alt-f>', lambda event: self.fav_selected(self.print_selected_keys))
        self.bind('<Alt-F>', lambda event: self.fav_selected(self.print_selected_keys))
        self.bind('<Alt-d>', lambda event: self.delete_selected(self.print_selected_keys))
        self.bind('<Alt-D>', lambda event: self.delete_selected(self.print_selected_keys))

    # Установить фокус (вкладка "Поиск")
    def set_focus_search(self):
        self.entry_search_query.focus_set()

        bind_ctrl_a(self.entry_search_query)
        bind_ctrl_a(self.entry_search_current_page)
        self.frame_search_query.bind('<Return>', lambda event: self.btn_search_search.invoke())
        self.bind('<Up>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(0.0))
        self.bind('<Control-u>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(0.0))
        self.bind('<Control-U>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(0.0))
        self.bind('<Down>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(1.0))
        self.bind('<Control-d>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(1.0))
        self.bind('<Control-D>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(1.0))
        self.bind('<Alt-Shift-p>', lambda event: self.search_unselect_page())
        self.bind('<Alt-Shift-P>', lambda event: self.search_unselect_page())
        self.bind('<Alt-Shift-a>', lambda event: self.search_unselect_all())
        self.bind('<Alt-Shift-A>', lambda event: self.search_unselect_all())
        self.bind('<Alt-Shift-g>', lambda event: self.remove_selected_from_group(self.search_selected_keys))
        self.bind('<Alt-Shift-G>', lambda event: self.remove_selected_from_group(self.search_selected_keys))
        self.bind('<Alt-Shift-f>', lambda event: self.unfav_selected(self.search_selected_keys))
        self.bind('<Alt-Shift-F>', lambda event: self.unfav_selected(self.search_selected_keys))
        self.bind('<Alt-p>', lambda event: self.search_select_page())
        self.bind('<Alt-P>', lambda event: self.search_select_page())
        self.bind('<Alt-a>', lambda event: self.search_select_all())
        self.bind('<Alt-A>', lambda event: self.search_select_all())
        self.bind('<Alt-g>', lambda event: self.add_selected_to_group(self.search_selected_keys))
        self.bind('<Alt-G>', lambda event: self.add_selected_to_group(self.search_selected_keys))
        self.bind('<Alt-f>', lambda event: self.fav_selected(self.search_selected_keys))
        self.bind('<Alt-F>', lambda event: self.fav_selected(self.search_selected_keys))
        self.bind('<Alt-d>', lambda event: self.delete_selected(self.search_selected_keys))
        self.bind('<Alt-D>', lambda event: self.delete_selected(self.search_selected_keys))

    # Смена вкладки
    def change_tab(self):
        if self.tabs.index(self.tabs.select()) == 0:
            self.current_tab = 0
            self.set_focus_print()
        elif self.tabs.index(self.tabs.select()) == 1:
            self.current_tab = 1
            self.set_focus_search()
        else:
            self.tabs.select(self.current_tab)
            self.add_entry()

    def open(self, tab: Literal['print', 'search'] = 'print'):
        self.focus_set()
        self.bind('<Escape>', lambda event: self.destroy())

        if tab == 'print':
            self.current_tab = 0
            self.set_focus_print()
        elif tab == 'search':
            self.current_tab = 1
            self.tabs.select(self.tab_search)
            self.set_focus_search()

        self.tabs.bind('<<NotebookTabChanged>>', lambda event: self.change_tab())

        self.grab_set()
        self.wait_window()


# Окно добавления статьи
class AddW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.dct_key = None

        self.var_wrd = tk.StringVar()
        self.var_tr = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        self._configure_window()
        self._create_widgets()
        self._add_validation()
        self._create_bindings()

        btn_disable(self.btn_add)
        self.entry_wrd.icursor(len(self.var_wrd.get()))

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Добавление статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        toplevel_geometry(self.parent, self)

    def _create_widgets(self):
        self.lbl_wrd = create_label(
            self, 'Введите слово:',
            row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_wrd = create_entry(
            self, self.var_wrd, 50, font=self.app_data, validate='all',
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
            self, self.add, 'Добавить',
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
        # При незаполненных полях нельзя нажать кнопку
        def validate_entries(value_wrd: str, value_tr: str):
            value_wrd = encode_special_combinations(value_wrd, self.dct.input_replacements)
            value_tr = encode_special_combinations(value_tr, self.dct.input_replacements)

            if value_wrd == '' or value_tr == '':
                btn_disable(self.btn_add)
            else:
                btn_enable(self.btn_add, self.add)

            words = (entry.lemma for entry in self.dct.get_entries())
            translations = []
            for tr in (entry.tr for entry in self.dct.get_entries()):
                translations += tr

            if value_wrd in words:
                keys_with_this_word = (key for key in self.dct.get_entry_ids()
                                       if self.dct[key].lemma == value_wrd)
                translations = []
                for tr in (self.dct[key].tr for key in keys_with_this_word):
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

        self.vcmd_wrd = (
            self.register(lambda value: validate_entries(value, self.var_tr.get())), '%P'
        )
        self.vcmd_tr = (
            self.register(lambda value: validate_entries(self.var_wrd.get(), value)), '%P'
        )
        self.entry_wrd['validatecommand'] = self.vcmd_wrd
        self.entry_tr['validatecommand'] = self.vcmd_tr

    def _create_bindings(self):
        self.entry_wrd.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_wrd.focus_set())

    # Добавление статьи
    def add(self):
        self.dct_key = add_entry_with_choose(
            self.dct, self,
            encode_special_combinations(self.var_wrd.get(), self.dct.input_replacements),
            encode_special_combinations(self.var_tr.get(), self.dct.input_replacements),
        )
        if not self.dct_key:
            return
        self.dct[self.dct_key].is_fav = self.var_fav.get()
        for group in self.dct.default_groups:
            self.dct[self.dct_key].add_to_group(group)

        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_wrd.focus_set()

        bind_ctrl_a(self.entry_wrd)
        bind_ctrl_a(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_add.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.update()

        self.grab_set()
        self.wait_window()

        return self.dct_key


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.manager = app_data.manager

        self.current_tab = 1  # Текущая вкладка (1 или 2)
        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.backup_dct = copy.deepcopy(self.manager.active.dct)
        self.backup_scale = self.app_data.gui_settings.scale

        self.var_check_register = tk.BooleanVar(
            value=self.manager.active.settings.is_register_sensitive
        )
        self.var_show_updates = tk.BooleanVar(
            value=self.app_data.global_settings.to_check_for_updates
        )
        self.var_show_typo_button = tk.BooleanVar(
            value=self.app_data.global_settings.is_typo_btn_on
        )
        self.var_theme = tk.StringVar(value=self.app_data.gui_settings.theme)
        self.var_themes_url = tk.StringVar(value=URL_RELEASES)

        self.img_about = tk.PhotoImage()
        self.img_plus = tk.PhotoImage()
        self.img_minus = tk.PhotoImage()

        self.dcts_savenames = []
        self.dcts_frames = []
        self.dcts_buttons = []

        self._configure_window()
        self._create_widgets()
        self._create_tips()

        self.print_dct_list(True)
        self.refresh_scale_buttons()

    def _configure_window(self):
        self.title(f'{PROGRAM_NAME} - Настройки')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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

        self._create_register_frame()
        self.btn_forms = create_button(
            self.tab_local, self.categories_settings, 'Грамматические категории',
            row=2, padx=6, pady=6)
        self.btn_groups = create_button(
            self.tab_local, self.groups_settings, 'Группы',
            row=3, padx=6, pady=6)
        self.btn_special_combinations = create_button(
            self.tab_local, self.special_combinations_settings, 'Специальные комбинации',
            row=4, padx=6, pady=6)
        self.lbl_save_warn = create_label(
            self.tab_local,
            'При сохранении настроек словаря, сохраняется и сам словарь!',
            'Warn.TLabel',
            row=5, padx=6, pady=6, sticky='S')

    def _create_register_frame(self):
        self.frame_check_register = create_frame(self.tab_local, row=1, padx=6, pady=6)

        self.lbl_check_register = create_label(
            self.frame_check_register,
            'Учитывать регистр букв при проверке ответа во время учёбы:',
            row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_check_register = create_checkbutton(
            self.frame_check_register, self.var_check_register,
            row=0, column=1, padx=(0, 6), pady=6, sticky='W')

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
        self.frame_show_typo_button = create_frame(self.tab_global, row=1, padx=6, pady=6)

        self.btn_about_typo = create_button(
            self.frame_show_typo_button, self.about_typo, width=2,
            row=0, column=0, padx=(6, 0), pady=6)
        set_image(self.btn_about_typo, self.img_about, img_about, '?')
        self.lbl_show_typo_button = create_label(
            self.frame_show_typo_button, 'Показывать кнопку "Опечатка":',
            row=0, column=1, padx=(3, 3), pady=6)
        self.check_show_typo_button = create_checkbutton(
            self.frame_show_typo_button, self.var_show_typo_button,
            row=0, column=2, padx=(0, 6), pady=6)

    def _create_dictionaries_frame(self):
        self.frame_dcts = create_frame(self.tab_global, row=2, padx=6, pady=6)

        self.lbl_dcts = create_label(
            self.frame_dcts, 'Существующие словари:',
            row=0, column=0, padx=6, pady=(6, 0))
        self.btn_about_dcts = create_button(
            self.frame_dcts, self.about_dcts, width=2,
            row=0, column=1, padx=6, pady=(6, 0))
        set_image(self.btn_about_dcts, self.img_about, img_about, '?')
        self.scrolled_frame_dcts = ScrollFrame(
            self.frame_dcts, self.app_data,
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN])
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

        self.btn_dct_create = create_button(
            self.frame_dct_buttons, self.dct_create, 'Новый словарь',
            row=0, column=0, padx=0, pady=(0, 3), sticky='WE')
        self.btn_dct_import = create_button(
            self.frame_dct_buttons, self.dct_import, 'Импортировать словарь',
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
        self.btn_custom_theme = create_button(
            self.frame_themes, self.custom_theme, 'Собственная тема',
            row=1, column=0, columnspan=2, padx=0, pady=(0, 6), sticky='E')
        self.entry_themes_version = create_entry(
            self.frame_themes, self.var_themes_url, 47, font=self.app_data,
            state='readonly', justify='center',
            row=1, column=2, padx=6, pady=(0, 6), sticky='WENS')

    def _create_scale_frame(self):
        self.frame_scale = create_frame(self.tab_global, row=4, padx=6, pady=6)

        self.btn_scale_minus = create_button(
            self.frame_scale, self.scale_minus,
            width=2, state='normal',
            row=0, column=0, padx=(6, 3), pady=6)
        set_image(self.btn_scale_minus, self.img_minus, img_delete, '-')
        self.lbl_scale = create_label(
            self.frame_scale, f'Масштаб ({self.app_data.gui_settings.scale}x)',
            row=0, column=1, padx=(3, 3), pady=6)
        self.btn_scale_plus = create_button(
            self.frame_scale, self.scale_plus,
            width=2, state='normal',
            row=0, column=2, padx=(3, 6), pady=6)
        set_image(self.btn_scale_plus, self.img_plus, img_add, '+')

    def _create_tips(self):
        self.tip_btn_about_typo = ttip.Hovertip(self.btn_about_typo, 'Справка', hover_delay=450)
        self.tip_btn_about_dcts = ttip.Hovertip(self.btn_about_dcts, 'Справка', hover_delay=450)

    # Настройки грамматических категорий (срабатывает при нажатии на кнопку)
    def categories_settings(self):
        self.has_ctg_changes = CategoriesSettingsW(
            self, self.app_data
        ).open() or self.has_ctg_changes

    # Настройки групп (срабатывает при нажатии на кнопку)
    def groups_settings(self):
        self.has_groups_changes = GroupsSettingsW(
            self, self.app_data
        ).open() or self.has_groups_changes

    # Настройки специальных комбинаций (срабатывает при нажатии на кнопку)
    def special_combinations_settings(self):
        self.has_spec_comb_changes = SpecialCombinationsSettingsW(
            self, self.app_data
        ).open() or self.has_spec_comb_changes

    # Справка о кнопке "Опечатка" (срабатывает при нажатии на кнопку)
    def about_typo(self):
        PopupImgW(
            self,
            self.app_data,
            img_about_typo,
            'Если функция включена, то\n'
            'когда вы неверно отвечаете при учёбе,\n'
            'появляется кнопка "Просто опечатка".\n'
            'При её нажатии, ошибка не засчитывается.\n'
            'Срабатывает при нажатии на Tab.',
        ).open()

    # Справка о словарях (срабатывает при нажатии на кнопку)
    def about_dcts(self):
        PopupMsgW(
            self, self.app_data,
            '* Чтобы открыть словарь, наведите на него мышку и нажмите ЛКМ\n'
            '* Чтобы переименовать словарь, наведите на него мышку и нажмите Ctrl+R\n'
            '* Чтобы удалить словарь, наведите на него мышку и нажмите Ctrl+D\n'
            '* Чтобы экспортировать словарь, наведите на него мышку и нажмите Ctrl+E',
            msg_justify='left',
        ).open()

    # Открыть словарь
    def dct_open(self, savename: str):
        if savename == self.manager.active.dct.name:
            return

        # Если есть прогресс, то предлагается его сохранить
        if self.has_local_changes():
            save_settings_if_has_changes(self, self.manager.active.dct)
        save_dct_if_has_progress(self, self.manager.active.dct, self.manager.active.dct.name)

        self.manager.active.dct = Dictionary()
        res = upload_save(self, self.manager.active.dct, savename, 'Отмена')
        if not res:
            # Если была попытка открыть повреждённый словарь, то при
            # сохранении настроек, текущий словарь стёрся бы
            self.destroy()
            return
        self.manager.active.dct.name, self.manager.active.settings.is_register_sensitive, \
            self.manager.active.dct._input_replacements, self.manager.active.dct._default_groups =\
            res
        self.manager.active.cache.session_number, self.manager.active.cache.search_config, \
            self.manager.active.cache.train_config =\
            upload_local_auto_settings(self.manager.active.dct.name)
        save_dct_name()

        self.backup_dct = copy.deepcopy(self.manager.active.dct)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(self.manager.active.dct.name)

        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.manager.active.dct.mark_saved()

        self.refresh()

    # Переименовать словарь
    def dct_rename(self, old_savename: str):
        window_rename = PopupEntryW(
            self, self.app_data,
            f'Введите новое название для словаря "{old_savename}"',
            default_value=old_savename,
            validate_function=validate_savename,
            check_answer_function=lambda wnd, val: check_dct_savename_edit(wnd, old_savename, val),
        )
        closed, new_savename = window_rename.open()
        if closed or new_savename == old_savename:
            return

        os.rename(os.path.join(SAVES_PATH, old_savename), os.path.join(SAVES_PATH, new_savename))
        if self.manager.active.dct.name == old_savename:
            self.manager.active.dct.name = new_savename
            save_dct_name()
            # Обновляем надписи с названием открытого словаря
            self.refresh_open_dct_name(new_savename)
        print(f'Словарь "{old_savename}" успешно переименован в "{new_savename}"')

        self.print_dct_list(False)

    # Удалить словарь
    def dct_delete(self, savename: str):
        if savename == self.manager.active.dct.name:
            warning(self, self.app_data, 'Вы не можете удалить словарь, когда он открыт!')
            return

        window_confirm = PopupDialogueW(
            self, self.app_data,
            f'Словарь "{savename}" будет безвозвратно удалён!\n'
            f'Хотите продолжить?',
            set_enter_on_btn='none',
        )
        answer = window_confirm.open()
        if not answer:
            return

        shutil.rmtree(os.path.join(SAVES_PATH, savename))

        self.print_dct_list(False)

    # Создать словарь (срабатывает при нажатии на кнопку)
    def dct_create(self):
        window = PopupEntryW(
            self, self.app_data,
            'Введите название нового словаря',
            validate_function=validate_savename,
            check_answer_function=check_dct_savename,
        )
        closed, savename = window.open()
        if closed:
            return

        if self.has_local_changes():
            save_settings_if_has_changes(self, self.manager.active.dct)
        save_dct_if_has_progress(self, self.manager.active.dct, self.manager.active.dct.name)

        self.manager.active.dct = create_dct(savename)
        self.manager.active.settings.is_register_sensitive, \
            self.manager.active.dct._input_replacements, self.manager.active.dct._features, \
            self.manager.active.dct._groups, self.manager.active.dct._default_groups =\
            upload_local_settings(savename)
        self.manager.active.cache.session_number, self.manager.active.cache.search_config, \
            self.manager.active.cache.train_config = upload_local_auto_settings(savename)
        self.manager.active.dct.name = savename
        save_dct_name()

        print(f'\nСловарь "{savename}" успешно создан и открыт')

        self.backup_dct = copy.deepcopy(self.manager.active.dct)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(savename)

        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.manager.active.dct.mark_saved()

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
        window = PopupEntryW(
            self, self.app_data,
            'Введите название для словаря',
            default_value=default_savename,
            validate_function=validate_savename,
            check_answer_function=check_dct_savename,
        )
        closed, savename = window.open()
        if closed:
            return

        dct_import(savename, src_path)

        self.refresh()

    # Задать пользовательскую тему (срабатывает при нажатии на кнопку)
    def custom_theme(self):
        CustomThemeSettingsW(self, self.app_data).open()
        upload_custom_theme(False)
        if self.app_data.gui_settings.theme == CUSTOM_TH:
            self.set_theme()
        self.refresh_scale_buttons()

    # Увеличить масштаб (срабатывает при нажатии на кнопку)
    def scale_plus(self):
        self.app_data.gui_settings.scale += 1

        self.parent.setup_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.lbl_scale.configure(text=f'Масштаб ({self.app_data.gui_settings.scale}x)')
        self.scrolled_frame_dcts.resize(
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN],
        )
        self.combo_themes.configure(font=('DejaVu Sans Mono', self.app_data.gui_settings.scale))
        self.entry_themes_version.configure(font=('StdFont', self.app_data.gui_settings.scale))

        # TODO: remove try-catch
        # Установка масштаба для окна уведомления об обновлении
        try:
            # TODO: remove global variable
            _0_global_window_last_version.entry_url.configure(
                font=('StdFont', self.app_data.gui_settings.scale)
            )
        except NameError:  # Если окно обновления не открыто
            pass

        self.refresh_scale_buttons()

    # Уменьшить масштаб (срабатывает при нажатии на кнопку)
    def scale_minus(self):
        self.app_data.gui_settings.scale -= 1

        self.parent.setup_styles()  # Установка ttk-стилей

        # Установка некоторых стилей для окна настроек
        self.lbl_scale.configure(text=f'Масштаб ({self.app_data.gui_settings.scale}x)')
        self.scrolled_frame_dcts.resize(
            SCALE_SMALL_FRAME_HEIGHT_SHORT[self.app_data.gui_settings.scale - SCALE_MIN],
            SCALE_SMALL_FRAME_WIDTH[self.app_data.gui_settings.scale - SCALE_MIN],
        )
        self.combo_themes.configure(font=('DejaVu Sans Mono', self.app_data.gui_settings.scale))
        self.entry_themes_version.configure(font=('StdFont', self.app_data.gui_settings.scale))

        # TODO: remove try-catch
        # Установка масштаба для окна уведомления об обновлении
        try:
            # TODO: remove global variable
            _0_global_window_last_version.entry_url.configure(
                font=('StdFont', self.app_data.gui_settings.scale)
            )
        except NameError:  # Если окно обновления не открыто
            pass

        self.refresh_scale_buttons()

    # Сохранить настройки (срабатывает при нажатии на кнопку)
    def save(self):
        # Учитывать/не учитывать регистр букв при проверке введённого ответа при учёбе
        self.manager.active.settings.is_register_sensitive = self.var_check_register.get()

        # Разрешить/запретить сообщать о новых версиях
        self.app_data.global_settings.to_check_for_updates = self.var_show_updates.get()

        # Показывать/скрывать кнопку "Опечатка" при неверном ответе в учёбе
        self.app_data.global_settings.is_typo_btn_on = self.var_show_typo_button.get()

        # Установка выбранной темы
        self.set_theme()

        # Обновление бэкапов сохранения
        self.backup_dct = copy.deepcopy(self.manager.active.dct)
        self.backup_scale = self.app_data.gui_settings.scale

        # Сохранение настроек в файлы
        save_local_settings(
            self.manager.active.settings.is_register_sensitive,
            self.manager.active.dct.input_replacements, self.manager.active.dct.features,
            self.manager.active.dct.groups, self.manager.active.dct.default_groups,
            self.manager.active.dct.name,
        )
        save_global_settings(
            self.manager.active.dct.name, self.app_data.global_settings.to_check_for_updates,
            self.app_data.global_settings.is_typo_btn_on, self.app_data.gui_settings.theme,
            self.app_data.gui_settings.scale,
        )
        save_local_auto_settings(
            self.manager.active.cache.session_number, self.manager.active.cache.search_config,
            self.manager.active.cache.train_config, self.manager.active.dct.name,
        )

        # Сохранение словаря, если были изменения локальных настроек
        if self.has_local_changes():
            save_dct(self.manager.active.dct, self.manager.active.dct.name)

        # Обнуление переменных, показывающих наличие изменений
        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.manager.active.dct.mark_saved()

        # Обновить кнопки изменения масштаба
        self.refresh_scale_buttons()

    # Закрыть настройки без сохранения (срабатывает при нажатии на кнопку)
    def close(self):
        if self.has_changes():
            window = PopupDialogueW(
                self, self.app_data,
                'У вас есть несохранённые изменения?\n'
                'Всё равно закрыть?',
            )
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
        for frame in self.dcts_frames:
            frame.unbind('<Enter>')
            frame.unbind('<Control-R>')
            frame.unbind('<Control-r>')
            frame.unbind('<Control-D>')
            frame.unbind('<Control-d>')
            frame.unbind('<Control-E>')
            frame.unbind('<Control-e>')
            frame.unbind('<Leave>')
            frame.destroy()

        # Выбираем словари
        self.dcts_savenames = [
            savename for savename in os.listdir(SAVES_PATH)
            if os.path.isdir(os.path.join(SAVES_PATH, savename))
        ]
        dcts_count = len(self.dcts_savenames)

        # Создаём новые фреймы
        self.dcts_frames = [
            create_frame(
                self.scrolled_frame_dcts.frame_canvas, 'Invis.TFrame',
                row=i, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(dcts_count)
        ]
        # Создаём новые кнопки
        self.dcts_buttons = [
            create_button(
                self.dcts_frames[i],
                lambda i=i: self.dct_open(self.dcts_savenames[i]),
                takefocus=False,
                style='FlatD.TButton' if i % 2 else 'FlatL.TButton',
                row=0, column=0, padx=0, pady=0, sticky='WE',
            ) for i in range(dcts_count)
        ]
        for i in range(dcts_count):
            # Выводим текст на кнопки
            savename = self.dcts_savenames[i]
            if savename == self.manager.active.dct.name:
                self.dcts_buttons[i].configure(text=split_text(f'{savename} (ОТКРЫТ)', 35))
            else:
                self.dcts_buttons[i].configure(text=split_text(f'{savename}', 35))

            # Привязываем события
            self.dcts_frames[i].bind('<Enter>', lambda event, i=i: self.dcts_frames[i].focus_set())
            self.dcts_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.dcts_frames[i].bind('<Control-r>', lambda event, i=i: self.dct_rename(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-R>', lambda event, i=i: self.dct_rename(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-d>', lambda event, i=i: self.dct_delete(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-D>', lambda event, i=i: self.dct_delete(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-e>', lambda event, i=i: self.dct_export(self.dcts_savenames[i]))
            self.dcts_frames[i].bind('<Control-E>', lambda event, i=i: self.dct_export(self.dcts_savenames[i]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_dcts.canvas.yview_moveto(0.0)

    # Обновить кнопки изменения масштаба
    def refresh_scale_buttons(self):
        # Если масштаб минимальный, то кнопка минуса становится неактивной
        if self.app_data.gui_settings.scale == SCALE_MIN:
            btn_disable(self.btn_scale_minus)
        else:
            btn_enable(self.btn_scale_minus, self.scale_minus, style='Image')

        # Если масштаб максимальный, то кнопка плюса становится неактивной
        if self.app_data.gui_settings.scale == SCALE_MAX:
            btn_disable(self.btn_scale_plus)
        else:
            btn_enable(self.btn_scale_plus, self.scale_plus, style='Image')

    # Обновить настройки при открытии другого словаря
    def refresh(self):
        self.var_check_register.set(self.manager.active.settings.is_register_sensitive)
        self.print_dct_list(False)

    # Установить выбранную тему
    def set_theme(self):
        self.app_data.gui_settings.theme = self.var_theme.get()

        self.parent.setup_styles()  # Установка ttk-стилей
        upload_theme_img(self.app_data.gui_settings.theme)  # Загрузка изображений темы

        # Установка изображений
        set_image(self.btn_about_typo, self.img_about, img_about, '?')
        set_image(self.btn_about_dcts, self.img_about, img_about, '?')
        set_image(self.btn_scale_plus, self.img_plus, img_add, '+')
        set_image(self.btn_scale_minus, self.img_minus, img_delete, '-')

        # Установка некоторых стилей для окна настроек
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
        self.scrolled_frame_dcts.canvas.configure(
            bg=STYLES['*.BG.ENTRY'][1][self.app_data.gui_settings.theme]
        )

        # Установка фона для главного окна
        self.parent.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])

        # TODO: remove try-catch
        # Установка фона для окна уведомления об обновлении
        try:
            # TODO: remove global variable
            _0_global_window_last_version.configure(
                bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme]
            )
        except NameError:  # Если окно обновления не открыто
            pass

    # Были ли изменения локальных настроек
    def has_local_changes(self):
        return self.has_ctg_changes or\
            self.has_groups_changes or\
            self.has_spec_comb_changes or\
            self.var_check_register.get() != self.manager.active.settings.is_register_sensitive

    # Были ли изменения настроек
    def has_changes(self):
        return self.has_local_changes() or\
            self.var_show_updates.get() != self.app_data.global_settings.to_check_for_updates or\
            self.var_show_typo_button.get() != self.app_data.global_settings.is_typo_btn_on or\
            self.var_theme.get() != self.app_data.gui_settings.theme or\
            self.backup_scale != self.app_data.gui_settings.scale

    # Обновить надписи с названием открытого словаря
    def refresh_open_dct_name(self, savename: str):
        self.lbl_dct_name.config(text=split_text(
            f'Открыт словарь "{savename}"', 30, to_add_right_spaces=False
        ))
        self.parent.lbl_dct_name.config(text=(
            f'Открыт словарь\n'
            f'"{split_text(savename, 20, to_add_right_spaces=False)}"'
        ))

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

        self.bind('<Escape>', lambda event: self.btn_close.invoke())
        self.tabs.bind('<<NotebookTabChanged>>', lambda event: self.resize_tabs())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        # TODO: remove deepcopy (?)
        self.manager.active.dct = copy.deepcopy(self.backup_dct)


# Окно уведомления о выходе новой версии
class NewVersionAvailableW(tk.Toplevel):
    def __init__(self, parent, app_data: AppData, last_version: str):
        super().__init__(parent)
        self.parent = parent

        self.app_data = app_data
        self.dct = app_data.manager.active.dct

        self.var_url = tk.StringVar(value=URL_GITHUB)  # Ссылка, для загрузки новой версии

        self._configure_window()
        self._create_widgets(last_version)

    def _configure_window(self):
        self.title('Доступна новая версия')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])
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

    # Открыть репозиторий проекта на GitHub
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

    # Скачать и установить обновление
    def download_and_install(self):
        save_dct_if_has_progress(self, self.dct, self.dct.name)

        # Загрузка
        try:
            # Скачиваем архив с обновлением
            print('Загрузка архива...', end='')
            wget.download(URL_DOWNLOAD_ZIP, out=MAIN_PATH)
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
            # Распаковываем архив во временную папку
            print('\nРаспаковка архива...')
            with zipfile.ZipFile(NEW_VERSION_ZIP_PATH, 'r') as zip_file:
                zip_file.extractall(MAIN_PATH)
            # Удаляем архив
            print('Удаление архива...')
            os.remove(NEW_VERSION_ZIP_PATH)
            # Получаем список обновляемых файлов
            update_files = [
                fn.strip() for fn in open(f'{NEW_VERSION_DIR}/{UPDATE_FILES}', 'r').readlines()
            ]
            # Удаляем файлы текущей версии
            print('Удаление старых файлов...')
            for filename in os.listdir(IMAGES_PATH):
                try:
                    os.remove(os.path.join(IMAGES_PATH, filename))
                except FileNotFoundError:
                    print(f'Не удалось удалить файл "{filename}", т. к. он отсутствует')
            for filename in ('resources/icon.png', 'backend.py', 'constants.py', 'gui.py'):
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
            warning(
                self, self.app_data,
                f'Не удалось установить обновление!\n'
                f'{exc}',
            )
            self.destroy()
            return
        else:
            print('Обновление успешно установлено!')
            PopupMsgW(
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

        self._configure_window()
        self.setup_styles()
        self._create_widgets()
        self.set_focus()

    def _configure_window(self):
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][self.app_data.gui_settings.theme])

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
            self.frame_dct_name,
            f'Открыт словарь\n'
            f'"{split_text(
                self.app_data.manager.active.dct.name, 20, to_add_right_spaces=False
            )}"',
            justify='center',
            padx=1, pady=1)

    def _create_buttons_frame(self):
        self.frame_buttons = create_frame(self, 'Invis.TFrame', row=2, padx=6, pady=(0, 6))

        self.btn_learn = create_button(
            self.frame_buttons, self.learn, 'Учить слова',
            row=0, padx=0, pady=(0, 3))
        self.btn_print = create_button(
            self.frame_buttons, self.print, 'Просмотреть словарь',
            row=1, padx=0, pady=(3, 3))
        self.btn_search = create_button(
            self.frame_buttons, self.search, 'Поиск',
            row=2, padx=0, pady=(3, 3))
        self.btn_add = create_button(
            self.frame_buttons, self.add, 'Добавить запись в словарь',
            row=3, padx=0, pady=(3, 3))
        self.btn_settings = create_button(
            self.frame_buttons, self.settings, 'Настройки',
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

    # Нажатие на кнопку "Учить слова"
    def learn(self):
        self.disable_all_buttons()

        train_config = ChooseLearnModeW(self, self.app_data).open()
        if train_config:
            LearnW(self, self.app_data, train_config).open()

        self.enable_all_buttons()

    # Нажатие на кнопку "Просмотреть словарь"
    def print(self):
        self.disable_all_buttons()
        PrintW(self, self.app_data).open()
        self.enable_all_buttons()

    # Нажатие на кнопку "Поиск"
    def search(self):
        self.disable_all_buttons()
        PrintW(self, self.app_data).open(tab='search')
        self.enable_all_buttons()

    # Нажатие на кнопку "Добавить запись в словарь"
    def add(self):
        self.disable_all_buttons()

        key = AddW(self, self.app_data).open()
        if key:
            EditW(self, self.app_data, key).open()

        self.enable_all_buttons()

    # Нажатие на кнопку "Настройки"
    def settings(self):
        self.disable_all_buttons()
        SettingsW(self, self.app_data).open()
        self.enable_all_buttons()

        # TODO:
        # Обновляем глобальные настройки
        # Обновляем локальные настройки
        # Обновляем локальные авто-настройки

        # Обновляем надпись с названием открытого словаря
        self.lbl_dct_name.config(text=(
            f'Открыт словарь\n'
            f'"{split_text(
                self.app_data.manager.active.dct.name, 20, to_add_right_spaces=False
            )}"'
        ))

        # TODO: remove try-catch
        # Установка масштаба для окна уведомления об обновлении
        try:
            # TODO: remove global variable
            _0_global_window_last_version.entry_url.configure(
                font=('StdFont', self.app_data.gui_settings.scale)
            )
        except NameError:  # Если окно обновления не открыто
            pass

        self.setup_styles()  # Установка ttk-стилей

    # Нажатие на кнопку "Проверить обновления"
    def check_updates(self):
        global _0_global_window_last_version

        # TODO: remove try-catch
        # Если уведомление об обновлении уже открыто, то закрываем его
        try:
            # TODO: remove global variable
            _0_global_window_last_version.destroy()
        except NameError:
            pass
        # Открываем новое уведомление об обновлении
        _0_global_window_last_version = check_updates(
            self, self.app_data.manager.active.dct, self.app_data,
            self.app_data.global_settings.to_check_for_updates, True
        )

    # Нажатие на кнопку "Сохранить словарь"
    def save(self):
        save_dct(self.app_data.manager.active.dct, self.app_data.manager.active.dct.name)
        PopupMsgW(self, self.app_data, 'Прогресс успешно сохранён').open()
        print('\nПрогресс успешно сохранён')

        self.app_data.manager.active.dct.mark_saved()

    # Нажатие на кнопку "Закрыть программу"
    def close(self):
        save_dct_if_has_progress(
            self, self.app_data.manager.active.dct, self.app_data.manager.active.dct.name
        )
        self.quit()

    # Отключить все кнопки на главном окне
    def disable_all_buttons(self):
        for widget in self.frame_buttons.children.values():
            if isinstance(widget, ttk.Button):
                btn_disable(widget)

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
    def setup_styles(self):
        scale = self.app_data.gui_settings.scale
        theme = self.app_data.gui_settings.theme

        # Стиль label "default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure(
            'Default.TLabel',
            font=('StdFont', scale),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.*'][1][theme],
        )

        # Стиль label "header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure(
            'Header.TLabel',
            font=('StdFont', scale + 5),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.*'][1][theme],
        )

        # Стиль label "logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure(
            'Logo.TLabel',
            font=('Times', scale + 11),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.LOGO'][1][theme],
        )

        # Стиль label "footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure(
            'Footer.TLabel',
            font=('StdFont', scale - 2),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.FOOTER'][1][theme],
        )

        # Стиль label "warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure(
            'Warn.TLabel',
            font=('StdFont', scale),
            background=STYLES['*.BG.*'][1][theme],
            foreground=STYLES['*.FG.WARN'][1][theme],
        )

        # Стиль label "flat light"
        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure(
            'FlatL.TLabel',
            font=('DejaVu Sans Mono', scale + 1),
            background=STYLES['FLAT_BTN.BG.1'][1][theme],
            foreground=STYLES['FLAT_BTN.FG.1'][1][theme],
        )

        # Стиль label "flat dark"
        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure(
            'FlatD.TLabel',
            font=('DejaVu Sans Mono', scale + 1),
            background=STYLES['FLAT_BTN.BG.2'][1][theme],
            foreground=STYLES['FLAT_BTN.FG.2'][1][theme],
        )

        # Стиль entry "default"
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

        # Стиль button "default"
        self.st_btn_default = ttk.Style()
        self.st_btn_default.theme_use('alt')
        self.st_btn_default.configure(
            'Default.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_default.map(
            'Default.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "disabled" (для выключенных "default")
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure(
            'Disabled.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_disabled.map(
            'Disabled.TButton',
            relief=[('active', 'raised'),
                    ('!active', 'raised')],
            background=[
                ('active', STYLES['BTN.BG.DISABL'][1][theme]),
                ('!active', STYLES['BTN.BG.DISABL'][1][theme]),
            ],
            foreground=[
                ('active', STYLES['BTN.FG.DISABL'][1][theme]),
                ('!active', STYLES['BTN.FG.DISABL'][1][theme]),
            ],
        )

        # Стиль button "yes"
        self.st_btn_yes = ttk.Style()
        self.st_btn_yes.theme_use('alt')
        self.st_btn_yes.configure(
            'Yes.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_yes.map(
            'Yes.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "no"
        self.st_btn_no = ttk.Style()
        self.st_btn_no.theme_use('alt')
        self.st_btn_no.configure(
            'No.TButton',
            font=('StdFont', scale + 2),
            borderwidth=1,
        )
        self.st_btn_no.map(
            'No.TButton',
            relief=[('pressed', 'sunken'),
                    ('active', 'flat'),
                    ('!active', 'raised')],
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

        # Стиль button "image"
        self.st_btn_image = ttk.Style()
        self.st_btn_image.theme_use('alt')
        self.st_btn_image.configure(
            'Image.TButton',
            font=('StdFont', scale + 2),
            borderwidth=0,
        )
        self.st_btn_image.map(
            'Image.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль button "flat light"
        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure(
            'FlatL.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note.map(
            'FlatL.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль button "flat dark"
        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure(
            'FlatD.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note.map(
            'FlatD.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль button "flat selected light"
        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure(
            'FlatSelectedL.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note_selected.map(
            'FlatSelectedL.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль button "flat selected dark"
        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure(
            'FlatSelectedD.TButton',
            font=('DejaVu Sans Mono', scale + 1),
            borderwidth=0,
        )
        self.st_btn_note_selected.map(
            'FlatSelectedD.TButton',
            relief=[('pressed', 'flat'),
                    ('active', 'flat'),
                    ('!active', 'flat')],
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

        # Стиль checkbutton "default"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map(
            'Default.TCheckbutton',
            background=[
                ('active', STYLES['CHECK.BG.SEL'][1][theme]),
                ('!active', STYLES['*.BG.*'][1][theme]),
            ],
        )

        # Стиль combobox "default"
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

        # Стиль scrollbar "vertical"
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

        # Стиль notebook "default"
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

        # Стиль вкладок notebook
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

        # Стиль frame "default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure(
            'Default.TFrame',
            borderwidth=1,
            relief=STYLES['FRAME.RELIEF.*'][1][theme],
            background=STYLES['*.BG.*'][1][theme],
            bordercolor=STYLES['*.BORDER_CLR.*'][1][theme],
        )

        # Стиль frame "invis"
        self.st_frame_invis = ttk.Style()
        self.st_frame_invis.theme_use('alt')
        self.st_frame_invis.configure(
            'Invis.TFrame',
            borderwidth=0,
            relief=STYLES['FRAME.RELIEF.*'][1][theme],
            background=STYLES['*.BG.*'][1][theme],
        )

    # Установить фокус
    def set_focus(self):
        self.focus_set()


""" Выполнение программы """


def main():
    global img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group, \
        img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page, img_select_all, \
        img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left, img_arrow_right, img_double_arrow_left, \
        img_double_arrow_right, img_trashcan
    global _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale, \
        _0_global_special_combinations, _0_global_check_register, _0_global_learn_settings, \
        _0_global_session_number, _0_global_search_settings, _0_global_fav_groups, _0_global_has_progress
    global _0_global_learn_session_number, _0_global_window_last_version

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

    dct = Dictionary()
    _0_global_has_progress = False

    print('\nПрограмма запускается...')
    print('\nЗагрузка тем...')
    upload_themes(THEMES)  # Загружаем дополнительные темы
    upload_custom_theme()  # Загружаем пользовательскую тему
    _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale =\
        upload_global_settings()  # Загружаем глобальные настройки
    upload_theme_img(th)  # Загружаем изображения для выбранной темы
    root = MainW(dct)  # Создаём графический интерфейс
    uploaded_save = upload_save(root, dct, _0_global_dct_savename, 'Завершить работу')  # Загружаем словарь
    if not uploaded_save:
        exit(EXIT_DCT_LOAD_FAILED)
    uploaded_save: tuple[str, int, dict[tuple[str, str], str], list[str]]
    _0_global_dct_savename, _0_global_check_register, _0_global_special_combinations, \
        _0_global_fav_groups = uploaded_save
    _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
        upload_local_auto_settings(_0_global_dct_savename)  # Загружаем локальные авто-настройки
    _0_global_window_last_version = check_updates(root, dct, bool(_0_global_show_updates),
                                                  False)  # Проверяем наличие обновлений
    _0_global_learn_session_number = 0
    if ICON_FN in os.listdir(RESOURCES_PATH):
        root.iconphoto(True, tk.PhotoImage(file=ICON_PATH))  # Устанавливаем иконку
    print('\nЗапуск программы прошёл успешно')
    root.mainloop()
    print('\nПрограмма успешно завершилась')


if __name__ == '__main__':
    main()

"""
    Про формы и грам. категории:

    'чашка' - СЛОВО

    'чашка'   - начальная ФОРМА СЛОВА 'чашка'   (ед. число, им. падеж)
    'чашками' -           ФОРМА СЛОВА 'чашка' (множ. число, тв. падеж)

      'ед. число, им. падеж' - ШАБЛОН ФОРМЫ 'чашка'
    'множ. число, тв. падеж' - ШАБЛОН ФОРМЫ 'чашками'

    'число' и 'падеж' - ГРАММАТИЧЕСКИЕ КАТЕГОРИИ

    'ед. число' и 'множ. число' - ЗНАЧЕНИЯ категории 'число'
    'им. падеж' и   'тв. падеж' - ЗНАЧЕНИЯ категории 'падеж'
"""
