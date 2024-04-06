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
def check_tr(window_parent, translations: list[str] | tuple[str, ...], new_tr: str, wrd: str) -> bool:
    new_tr = encode_special_combinations(new_tr, _0_global_special_combinations)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations:
        warning(window_parent, f'У слова "{wrd}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность перевода при изменении
def check_tr_edit(window_parent, translations: list[str] | tuple[str, ...], old_tr: str, new_tr: str, wrd: str) -> bool:
    new_tr = encode_special_combinations(new_tr, _0_global_special_combinations)
    if new_tr == '':
        warning(window_parent, 'Перевод должен содержать хотя бы один символ!')
        return False
    if new_tr in translations and new_tr != old_tr:
        warning(window_parent, f'У слова "{wrd}" уже есть такой перевод!')
        return False
    return True


# Проверить корректность фразы
def check_phr(window_parent, phrases: dict[str, list[str]], new_phr: tuple[str, str], wrd: str) -> bool:
    n1 = encode_special_combinations(new_phr[0], _0_global_special_combinations)
    n2 = encode_special_combinations(new_phr[1], _0_global_special_combinations)
    if n1 == '' or n2 == '':
        warning(window_parent, 'Фраза должна содержать хотя бы один символ!')
        return False
    if new_phr[0] in phrases.keys() and new_phr[1] in phrases[new_phr[0]]:
        warning(window_parent, f'Со словом "{wrd}" уже есть такая фраза!')
        return False
    return True


# Проверить корректность фразы при изменении
def check_phr_edit(window_parent, phrases: dict[str, list[str]], old_phr: tuple[str, str], new_phr: tuple[str, str],
                   wrd: str) -> bool:
    n1 = encode_special_combinations(new_phr[0], _0_global_special_combinations)
    n2 = encode_special_combinations(new_phr[1], _0_global_special_combinations)
    if n1 == '' or n2 == '':
        warning(window_parent, 'Фраза должна содержать хотя бы один символ!')
        return False
    if new_phr[0] in phrases.keys() and new_phr[1] in phrases[new_phr[0]] and new_phr != old_phr:
        warning(window_parent, f'Со словом "{wrd}" уже есть такая фраза!')
        return False
    return True


# Проверить корректность сноски
def check_note(window_parent, notes: list[str] | tuple[str, ...], new_note: str, wrd: str) -> bool:
    new_note = encode_special_combinations(new_note, _0_global_special_combinations)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes:
        warning(window_parent, f'У слова "{wrd}" уже есть такая сноска!')
        return False
    return True


# Проверить корректность сноски при изменении
def check_note_edit(window_parent, notes: list[str] | tuple[str, ...], old_note: str, new_note: str, wrd: str) -> bool:
    new_note = encode_special_combinations(new_note, _0_global_special_combinations)
    if new_note == '':
        warning(window_parent, 'Сноска должна содержать хотя бы один символ!')
        return False
    if new_note in notes and new_note != old_note:
        warning(window_parent, f'У слова "{wrd}" уже есть такая сноска!')
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
def check_group_name_edit(window_parent, groups: list[str] | tuple[str, ...], old_group: str, new_group: str) -> bool:
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
def check_ctg_edit(window_parent, categories: list[str] | tuple[str, ...], old_ctg: str, new_ctg: str) -> bool:
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
def check_ctg_val_edit(window_parent, values: list[str] | tuple[str, ...], old_val: str, new_val: str) -> bool:
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
    return ('\n' + ' ' * tab).join((f'[{frm_key_to_str_for_print(key)}] {entry.forms[key]}' for key in frm_keys))


# Вывести переводы фразы
def get_phr_tr(entry: Entry, phr_key: str) -> str:
    return ', '.join(pt for pt in entry.phrases[phr_key])


# Вывести фразы
def get_phrases(entry: Entry, tab: int = 0) -> str:
    return ('\n' + ' ' * tab).join((phr + ' - ' + get_phr_tr(entry, phr) for phr in entry.phrases))


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
def get_entry_percent(entry: Entry) -> str:
    if entry.all_att == 0:  # Если ещё не было попыток
        res = '-'
    else:
        res = '{:.0%}'.format(entry.score)
    return res


# Вывести статистику
def get_entry_stat(entry: Entry) -> str:
    correct_att_in_a_row = get_correct_att_in_a_row(entry)
    percent = get_entry_percent(entry)
    tab_correct = ' ' * (3 - len(str(correct_att_in_a_row)))
    tab_percent = ' ' * (4 - len(percent))
    res = f'[{tab_correct}{correct_att_in_a_row}:{tab_percent}{percent}]'
    return res


# Служебная функция для get_entry_info_briefly и get_entry_info_briefly_with_forms
def _get_entry_info_briefly(entry: Entry) -> str:
    if entry.fav:
        res = '(*)'
    else:
        res = '   '
    res += f' {get_entry_stat(entry)} {entry.wrd}: {get_tr(entry)}'
    return res


# Вывести статью - кратко
def get_entry_info_briefly(entry: Entry, len_str: int) -> str:
    return split_text(_get_entry_info_briefly(entry), len_str, tab=15)


# Вывести статью - подробно
def get_entry_info_detailed(entry: Entry, len_str: int) -> str:
    res = _get_entry_info_briefly(entry)
    if entry.count_f != 0:
        res += f'\n  Формы слова: {get_forms(entry, tab=15)}'
    if entry.phrases.keys():
        res += f'\n        Фразы: {get_phrases(entry, tab=15)}'
    if entry.count_n != 0:
        res += f'\n       Сноски: {get_notes(entry, tab=15)}'
    if entry.groups:
        res += f'\n       Группы: {get_groups(entry)}'
    return split_text(res, len_str, tab=15)


# Вывести статью - со всей информацией
def get_all_entry_info(entry: Entry, len_str: int, tab: int = 0) -> str:
    res  = f'      Слово: {entry.wrd}\n'
    res += f'    Перевод: {get_tr(entry)}\n'

    res += f'Формы слова: '
    if entry.count_f == 0:
        res += '-\n'
    else:
        keys = [key for key in entry.forms.keys()]
        res += f'[{frm_key_to_str_for_print(keys[0])}] {entry.forms[keys[0]]}\n'
        for i in range(1, entry.count_f):
            res += f'             [{frm_key_to_str_for_print(keys[i])}] {entry.forms[keys[i]]}\n'

    res += '      Фразы: '
    if entry.count_p == 0:
        res += '-'
    else:
        res += get_phrases(entry, tab=13)

    res += '\n     Сноски: '
    if entry.count_n == 0:
        res += '-'
    else:
        res += get_notes(entry, tab=13)

    res += '\n  Избранное: '
    if entry.fav:
        res += '+'
    else:
        res += '-'

    res += f'\n     Группы: {get_groups(entry)}\n'

    if entry.all_att == 0:  # Если ещё не было попыток
        res += ' Статистика: 1) Верных ответов подряд: -\n'
        res += '             2) Доля верных ответов: -'
    else:
        res += f' Статистика: 1) Верных ответов подряд: {entry.correct_att_in_a_row}\n'
        res += f'             2) Доля верных ответов: '
        res += f'{entry.correct_att}/{entry.all_att} = ' + '{:.0%}'.format(entry.score)

    return split_text(res, len_str, tab=tab)


# Вывести слово со статистикой
def get_wrd_with_stat(entry: Entry) -> str:
    res = f'{entry.wrd} {get_entry_stat(entry)}'
    return res


# Вывести перевод со статистикой
def get_tr_with_stat(entry: Entry) -> str:
    res = f'{get_tr(entry)} {get_entry_stat(entry)}'
    return res


# Вывести перевод со словоформой и со статистикой
def get_tr_and_frm_with_stat(entry: Entry, frm_key: FrmKey | list[str]) -> str:
    res = f'{get_tr(entry)} ({frm_key_to_str_for_print(frm_key)}) {get_entry_stat(entry)}'
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
def dct_info(count_w: int, count_t: int, count_f: int) -> str:
    w = set_postfix(count_w, ('слово', 'слова', 'слов'))
    f = set_postfix(count_w + count_f, ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(count_t, ('перевод', 'перевода', 'переводов'))
    return f'[ {count_w} {w} | {count_w + count_f} {f} | {count_t} {t} ]'


# Вывести информацию о количестве избранных статей в словаре
def dct_info_fav(count_w: tuple[int, int], count_t: tuple[int, int], count_f: tuple[int, int]) -> str:
    w = set_postfix(count_w[0], ('слово', 'слова', 'слов'))
    f = set_postfix(count_w[0] + count_f[0], ('словоформа', 'словоформы', 'словоформ'))
    t = set_postfix(count_t[0], ('перевод', 'перевода', 'переводов'))
    return f'[ {count_w[0]}/{count_w[1]} {w} '\
           f'| {count_w[0] + count_f[0]}/{count_w[1] + count_f[1]} {f} '\
           f'| {count_t[0]}/{count_t[1]} {t} ]'


""" Вспомогательные функции """


# Преобразовать специальную комбинацию в читаемый вид (для отображения в настройках)
def special_combination(key: tuple[str, str]) -> str:
    value = _0_global_special_combinations[key]
    return f'{key[0]}{key[1]} -> {value}'


# Преобразовать в тексте специальные комбинации в соответствующие символы
def encode_special_combinations(text: str, special_combinations: dict[tuple[str, str], str]) -> str:
    encoded_text = ''

    opening_symbol = None  # Встречен ли открывающий символ специальной комбинации
    for symbol in text:
        if opening_symbol:
            if (opening_symbol, symbol) in special_combinations.keys():  # Если есть такая комбинация
                encoded_text += special_combinations[(opening_symbol, symbol)]
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
            transformations += (['ä'], ['Ä'], ['ë'], ['Ë'], ['ö'], ['Ö'], ['ü'], ['Ü'], ['ß', ''], ['ẞ', ''])[pos]
        else:
            converted_text += symbol
            transformations += [symbol]

    return converted_text.lower(), transformations


# Найти в строке подстроку и выделить её (только частичные совпадения)
def find_and_highlight(target_wrd: str, search_wrd: str) -> str:
    if target_wrd == search_wrd:  # Полное совпадение не учитывается
        return ''

    target_wrd = encode_special_combinations(target_wrd, _0_global_special_combinations)
    search_wrd = encode_special_combinations(search_wrd, _0_global_special_combinations)

    target_simpl, target_arr = simplify(target_wrd)
    search_simpl, search_arr = simplify(search_wrd)

    pos = target_simpl.find(search_simpl)
    if pos != -1:
        search_len = len(encode_special_combinations(search_simpl, _0_global_special_combinations))
        end_pos = pos + search_len
        if search_wrd == '':  # Если искомая подстрока пустая, то она не выделяется
            res = target_wrd
        else:
            res = ''.join((s for s in target_arr[:pos] + ['['] +
                           target_arr[pos:end_pos] + [']'] + target_arr[end_pos:]))
        return res
    return ''


# Выбрать случайное слово с учётом сложности
def random_smart(dct: Dictionary, pool: set[tuple[DctKey, FrmKey | None, str | None]]
                 ) -> tuple[DctKey, FrmKey | None, str | None]:
    summ = 0
    for (key, frm, phr) in pool:
        entry = dct.d[key]
        score = (100 - round(100 * entry.score)) + 1
        score += 100 // (entry.all_att + 1)
        summ += round(score)

    r = random.randint(1, summ)
    for (key, frm, phr) in pool:
        entry = dct.d[key]
        score = (100 - round(100 * entry.score)) + 1
        score += 100 // (entry.all_att + 1)
        r -= round(score)
        if r <= 0:
            return key, frm, phr


# Разделить строку на слова
def split_line(line: str) -> list[str, str]:
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
def split_text(text: str, max_str_len: int, tab: int = 0, add_right_spaces: bool = True) -> str:
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
def choose_one_of_similar_entries(dct: Dictionary, window_parent, wrd: str):
    if wrd_to_key(wrd, 1) not in dct.d.keys():  # Если статья только одна, то возвращает её ключ
        return wrd_to_key(wrd, 0)
    window_entries = ChooseOneOfSimilarEntriesW(window_parent, wrd)
    answer = window_entries.open()
    if not answer:
        return None
    return answer


# Изменить слово в статье
def edit_wrd_with_choose(dct: Dictionary, window_parent, key: DctKey, new_wrd: str) -> DctKey | None:
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
            new_key = dct.add_entry(new_wrd, dct.d[key].tr, dct.d[key].forms, dct.d[key].phrases, dct.d[key].notes,
                                    dct.d[key].groups, dct.d[key].fav, dct.d[key].all_att, dct.d[key].correct_att,
                                    dct.d[key].correct_att_in_a_row, dct.d[key].latest_answer_date)
            dct.delete_entry(key)
            return new_key
        else:
            return key
    else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
        new_key = dct.add_entry(new_wrd, dct.d[key].tr, dct.d[key].forms, dct.d[key].phrases, dct.d[key].notes,
                                dct.d[key].groups, dct.d[key].fav, dct.d[key].all_att, dct.d[key].correct_att,
                                dct.d[key].correct_att_in_a_row, dct.d[key].latest_answer_date)
        dct.delete_entry(key)
        return new_key


# Добавить статью в словарь (для пользователя)
def add_entry_with_choose(dct: Dictionary, window_parent, wrd: str, tr: str) -> DctKey | None:
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
def add_ctg(window_parent, dct: Dictionary) -> bool:
    # Ввод названия новой категории
    window_ctg = PopupEntryW(window_parent, 'Введите название новой категории',
                             check_answer_function=lambda wnd, val: check_ctg(wnd, tuple(dct.ctg.keys()), val))
    closed, new_ctg = window_ctg.open()
    if closed:
        return False
    new_ctg = encode_special_combinations(new_ctg, _0_global_special_combinations)

    # Ввод первого значения категории
    window_val = PopupEntryW(window_parent, 'Необходимо добавить хотя бы одно значение для категории',
                             check_answer_function=lambda wnd, val: check_ctg_val(wnd, (), val))
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
    window_entry = PopupEntryW(window_parent, 'Введите новое название категории', default_value=old_ctg_name,
                               check_answer_function=lambda wnd, val:
                               check_ctg_edit(wnd, tuple(dct.ctg.keys()), old_ctg_name, val))
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
    window_dia = PopupDialogueW(window_parent, f'Все словоформы, содержащие категорию {ctg_name}, будут удалены!\n'
                                               f'Хотите продолжить?')  # Подтверждение действия
    answer = window_dia.open()
    if not answer:
        return False

    # Обновление категорий
    dct.delete_ctg(ctg_name)
    return True


# Добавить значение категории
def add_ctg_val(window_parent, dct: Dictionary, ctg_name: str, values: list[str] | tuple[str, ...]) -> bool:
    # Ввод нового значения
    window_entry = PopupEntryW(window_parent, 'Введите новое значение категории',
                               check_answer_function=lambda wnd, val: check_ctg_val(wnd, values, val))
    closed, new_val = window_entry.open()
    if closed:
        return False

    new_val = encode_special_combinations(new_val, _0_global_special_combinations)
    dct.add_ctg_val(ctg_name, new_val)
    return True


# Переименовать значение категории
def rename_ctg_val(window_parent, dct: Dictionary, ctg_name: str, old_ctg_val: str) -> bool:
    # Ввод нового значения
    window_entry = PopupEntryW(window_parent, 'Введите новое название значения', default_value=old_ctg_val,
                               check_answer_function=lambda wnd, val:
                               check_ctg_val_edit(wnd, dct.ctg[ctg_name], old_ctg_val, val))
    closed, new_ctg_val = window_entry.open()
    if closed:
        return False
    new_ctg_val = encode_special_combinations(new_ctg_val, _0_global_special_combinations)
    if new_ctg_val == old_ctg_val:
        return False

    # Переименовывание значения во всех словоформах, его содержащих
    dct.rename_ctg_val(ctg_name, old_ctg_val, new_ctg_val)
    return True


# Удалить значение категории
def delete_ctg_val(window_parent, dct: Dictionary, ctg_name: str, ctg_val: str) -> bool:
    window_dia = PopupDialogueW(window_parent, f'Все словоформы, содержащие значение {ctg_val}, будут удалены!\n'
                                               f'Хотите продолжить?')  # Подтверждение действия
    answer = window_dia.open()
    if not answer:
        return False

    # Удаление всех словоформ, содержащих это значение категории
    dct.delete_ctg_val(ctg_name, ctg_val)
    return True


# Есть ли слово в строке
def wrd_in_line(line: str, wrd: str) -> bool:
    words = re.split(r'[.,;:!? \n()\[\]{}]', line)
    words = [w for w in words if w != '']
    return wrd in words


# Поиск статей в словаре
def search_entries(dct: Dictionary, dct_keys: tuple[DctKey, ...], query: str,
                   search_wrd: bool, search_tr: bool, search_frm: bool, search_phr: bool, search_nt: bool) -> list[set]:
    query_l = query.lower()
    query_s = simplify(query)[0].replace('ё', 'е')
    results = [set() for _ in range(9)]
    for key in dct_keys:
        entry = dct.d[key]

        # Все фразы и переводы фраз для данной статьи
        phrases = list(entry.phrases.keys())
        for phr_key in entry.phrases.keys():
            for phr_tr in entry.phrases[phr_key]:
                phrases += [phr_tr]

        if search_wrd and query == entry.wrd or\
           search_tr  and query in entry.tr or\
           search_frm and query in entry.forms.values() or\
           search_phr and query in phrases or\
           search_nt  and query in entry.notes:
            results[0].add(key)
        elif search_wrd and query_l == entry.wrd.lower() or\
             search_tr  and query_l in [ tr.lower() for tr  in entry.tr] or\
             search_frm and query_l in [frm.lower() for frm in entry.forms.values()] or\
             search_phr and query_l in [phr.lower() for phr in phrases] or\
             search_nt  and query_l in [ nt.lower() for nt  in entry.notes]:
            results[1].add(key)
        elif search_wrd and query_s == simplify(entry.wrd)[0].replace('ё', 'е') or\
             search_tr  and query_s in [simplify( tr)[0].replace('ё', 'е') for tr  in entry.tr] or\
             search_frm and query_s in [simplify(frm)[0].replace('ё', 'е') for frm in entry.forms.values()] or\
             search_phr and query_s in [simplify(phr)[0].replace('ё', 'е') for phr in phrases] or\
             search_nt  and query_s in [simplify( nt)[0].replace('ё', 'е') for nt  in entry.notes]:
            results[2].add(key)

        elif search_wrd and wrd_in_line(entry.wrd, query) or\
             search_tr  and True in [wrd_in_line( tr, query) for tr  in entry.tr] or\
             search_frm and True in [wrd_in_line(frm, query) for frm in entry.forms.values()] or\
             search_phr and True in [wrd_in_line(phr, query) for phr in phrases] or\
             search_nt  and True in [wrd_in_line( nt, query) for nt  in entry.notes]:
            results[3].add(key)
        elif search_wrd and wrd_in_line(entry.wrd.lower(), query_l) or\
             search_tr  and True in [wrd_in_line( tr.lower(), query_l) for tr  in entry.tr] or\
             search_frm and True in [wrd_in_line(frm.lower(), query_l) for frm in entry.forms.values()] or\
             search_phr and True in [wrd_in_line(phr.lower(), query_l) for phr in phrases] or\
             search_nt  and True in [wrd_in_line( nt.lower(), query_l) for nt  in entry.notes]:
            results[4].add(key)
        elif search_wrd and wrd_in_line(simplify(entry.wrd)[0].replace('ё', 'е'), query_s) or\
             search_tr  and True in [wrd_in_line(simplify( tr)[0].replace('ё', 'е'), query_s) for tr  in entry.tr] or\
             search_frm and True in [wrd_in_line(simplify(frm)[0].replace('ё', 'е'), query_s) for frm in entry.forms.values()] or\
             search_phr and True in [wrd_in_line(simplify(phr)[0].replace('ё', 'е'), query_s) for phr in phrases] or\
             search_nt  and True in [wrd_in_line(simplify( nt)[0].replace('ё', 'е'), query_s) for nt  in entry.notes]:
            results[5].add(key)

        elif search_wrd and query in entry.wrd or\
             search_tr  and True in [query in tr  for tr  in entry.tr] or\
             search_frm and True in [query in frm for frm in entry.forms.values()] or\
             search_phr and True in [query in phr for phr in phrases] or\
             search_nt  and True in [query in nt  for nt  in entry.notes]:
            results[6].add(key)
        elif search_wrd and query_l in entry.wrd.lower() or\
             search_tr  and True in [query_l in  tr.lower() for tr  in entry.tr] or\
             search_frm and True in [query_l in frm.lower() for frm in entry.forms.values()] or\
             search_phr and True in [query_l in phr.lower() for phr in phrases] or\
             search_nt  and True in [query_l in  nt.lower() for nt  in entry.notes]:
            results[7].add(key)
        elif search_wrd and query_s in simplify(entry.wrd)[0].replace('ё', 'е') or\
             search_tr  and True in [query_s in simplify( tr)[0].replace('ё', 'е') for tr  in entry.tr] or\
             search_frm and True in [query_s in simplify(frm)[0].replace('ё', 'е') for frm in entry.forms.values()] or\
             search_phr and True in [query_s in simplify(phr)[0].replace('ё', 'е') for phr in phrases] or\
             search_nt  and True in [query_s in simplify( nt)[0].replace('ё', 'е') for nt  in entry.notes]:
            results[8].add(key)
    return results


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

STYLES_FN = 'styles.txt'  # Название файла стилей темы
RET_TH_OK = 0  # Загрузка темы прошла успешно
RET_TH_OLD = 1  # Версия темы не соответствует требуемой


# Установить в качестве пользовательской темы тему по умолчанию
def create_default_custom_theme():
    styles_path = os.path.join(CUSTOM_THEME_PATH, STYLES_FN)
    with open(styles_path, 'w', encoding='utf-8') as styles_file:
        styles_file.write(f'{REQUIRED_THEME_VERSION}\n'
                          f'1')
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
            print(f'Тема устарела. Идёт обновление с версии {theme_version} до версии {REQUIRED_THEME_VERSION}')
            upgrade_theme(styles_path)
        else:
            return RET_TH_OLD
    with open(styles_path, 'r', encoding='utf-8') as styles_file:
        styles_file.readline().strip()  # Версия темы
        styles_file.readline().strip()  # Переменная обновлений
        # Сначала устанавливаем значения по умолчанию
        for key in STYLES.keys():
            STYLES[key][1][theme_name] = STYLES[key][1][DEFAULT_TH]
        # Далее устанавливаем заданные значения
        while True:
            line = styles_file.readline().strip()
            data = [v for v in re.split(' |=|//', line) if v != '']  # После // идут комментарии
            if not data:  # Если настройки стилей закончились, выходим из цикла
                break
            key = data[0].strip()
            if key not in STYLES.keys():  # Если считанный ключ отсутствует в текущей версии тем, то пропускаем его
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
        try:
            ret = upload_one_theme(theme_dir_path, theme_name)
        except Exception as exc:
            print(f'Не удалось загрузить тему "{theme_name}" из-за ошибки: {exc}')
        else:
            if ret == RET_TH_OK:
                print(f'Тема "{theme_name}" успешно загружена')
                if theme_name not in themes:  # Добавляем название новой темы
                    themes += [theme_name]
            elif ret == RET_TH_OLD:
                print(f'Не удалось загрузить тему "{theme_name}", т. к. её версия не соответствует требуемой! '
                      f'Актуальные темы можно загрузить здесь: {URL_RELEASES}')


# Загрузить пользовательскую тему
def upload_custom_theme(to_print=True):
    if STYLES_FN not in os.listdir(CUSTOM_THEME_PATH):
        create_default_custom_theme()
        return
    try:
        ret = upload_one_theme(CUSTOM_THEME_PATH, CUSTOM_TH)
    except Exception as exc:
        print(f'Не удалось загрузить пользовательскую тему из-за ошибки: {exc}')
    else:
        if ret == RET_TH_OK and to_print:
            print(f'Пользовательская тема успешно загружена')
        elif ret == RET_TH_OLD:
            print(f'Не удалось загрузить пользовательскую тему, т. к. её версия не соответствует требуемой!')


# Загрузить изображения для выбранной темы
def upload_theme_img(theme: str):
    global img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group,\
        img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page, img_select_all,\
        img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left, img_arrow_right, img_double_arrow_left,\
        img_double_arrow_right, img_trashcan

    if theme == CUSTOM_TH:
        theme_dir = CUSTOM_THEME_PATH
    else:
        theme_dir = os.path.join(ADDITIONAL_THEMES_PATH, theme)

    images = [img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group,
              img_remove_from_group, img_edit, img_add, img_delete, img_select_page, img_unselect_page,
              img_select_all, img_unselect_all, img_print_out, img_redo, img_undo, img_arrow_left, img_arrow_right,
              img_double_arrow_left, img_double_arrow_right, img_trashcan]

    for i in range(len(images)):
        file_name = f'{IMG_NAMES[i]}.png'
        if file_name in os.listdir(theme_dir):
            images[i] = os.path.join(theme_dir, file_name)
        else:
            images[i] = os.path.join(IMAGES_PATH, file_name)

    img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav, img_add_to_group, img_remove_from_group,\
        img_edit, img_add, img_delete, img_select_page, img_unselect_page, img_select_all, img_unselect_all,\
        img_print_out, img_redo, img_undo, img_arrow_left, img_arrow_right,\
        img_double_arrow_left, img_double_arrow_right, img_trashcan = images


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
        show_updates = int(global_settings_file.readline().strip())
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
def save_local_settings(check_register: int, special_combinations: dict[tuple[str, str], str],
                        categories: dict[str, list[str]], groups: list[str], fav_groups: list[str], savename: str):
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
        search_settings = tuple(int(el) for el in local_auto_settings_file.readline().strip().split())
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
def save_local_auto_settings(session_number: int, search_settings: tuple[int, int, int, int, int, int, int, int],
                             learn_settings: list[int, int, int, int, int], savename: str):
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
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale)
        save_local_settings(_0_global_check_register, _0_global_special_combinations, _0_global_dct.ctg,
                            _0_global_dct.groups, _0_global_fav_groups, _0_global_dct_savename)
        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)
        PopupMsgW(window_parent, 'Настройки успешно сохранены').open()
        print('\nНастройки успешно сохранены')


# Создать и загрузить пустой словарь
def create_dct(dct: Dictionary, savename: str):
    folder_path = os.path.join(SAVES_PATH, savename)
    filepath = os.path.join(folder_path, DICTIONARY_SAVE_FN)
    os.mkdir(folder_path)
    open(filepath, 'w', encoding='utf-8').write(f'v{SAVES_VERSION}\n')
    dct.read(filepath, 0)


# Сохранить словарь
def save_dct(dct: Dictionary, savename: str):
    filepath = os.path.join(SAVES_PATH, savename, DICTIONARY_SAVE_FN)
    dct.save(filepath, SAVES_VERSION)


# Предложить сохранение словаря, если есть изменения
def save_dct_if_has_progress(window_parent, dct: Dictionary, savename: str, has_progress: bool):
    if has_progress:
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
        check_register, special_combinations, dct.ctg, dct.groups, fav_groups = upload_local_settings(savename)
        upgrade_dct_save(save_file_path, lambda line: encode_special_combinations(line, special_combinations))  # Если требуется, сохранение обновляется
        dct.read(save_file_path, len(dct.ctg))  # Загрузка словаря
    except FileNotFoundError:  # Если сохранение не найдено, то создаётся пустой словарь
        print(f'\nСловарь "{savename}" не найден!')
        create_dct(dct, savename)
        check_register, special_combinations, dct.ctg, dct.groups, fav_groups = upload_local_settings(savename)
        print('Создан и загружен пустой словарь')
        return savename, check_register, special_combinations, fav_groups
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
def bind_keypress(event, keys_and_cmd: list[tuple[str, any]], latin: bool = True):
    for (key, cmd) in keys_and_cmd:
        if event.keycode == ord(key):
            if latin or event.keysym.lower() != key.lower():
                cmd()


# Привязать Control + A, C, V, X
def bind_ctrl_acvx(widget):
    widget.bind('<Control-KeyPress>',
                lambda key: bind_keypress(key, [('A', lambda: key.widget.event_generate('<<SelectAll>>')),
                                                ('C', lambda: key.widget.event_generate('<<Copy>>')),
                                                ('V', lambda: key.widget.event_generate('<<Paste>>')),
                                                ('X', lambda: key.widget.event_generate('<<Cut>>'))],
                                          False))


# Вывести сообщение с предупреждением
def warning(window_parent, msg: str):
    PopupMsgW(window_parent, msg, tab=0, title='Warning').open()


# Выключить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_disable(btn: ttk.Button):
    btn.configure(command='', style='Disabled.TButton')


# Включить кнопку (т. к. в ttk нельзя убрать уродливую тень текста на выключенных кнопках, пришлось делать по-своему)
def btn_enable(btn: ttk.Button, command, style='Default'):
    btn.configure(command=command, style=f'{style}.TButton')


# Установить изображение на кнопку
# Если изображение отсутствует, его замещает текст
def set_image(btn: ttk.Button, img: tk.PhotoImage, img_name: str, text_if_no_img: str,
              compound: typing.Literal['none', 'image', 'text', 'left', 'right', 'top', 'bottom', 'center'] = 'image'):
    try:
        img.configure(file=img_name)
    except:
        btn.configure(text=text_if_no_img, compound='text', style='Default.TButton')
    else:
        btn.configure(image=img, compound=compound, style='Image.TButton')


""" Графический интерфейс - функции валидации """


# Ввод только целых чисел от 0 до max_val
def validate_int_min_max(value: str, min_val: int, max_val: int) -> bool:
    return value == '' or value.isnumeric() and min_val <= int(value) <= max_val


# Ввод только целых чисел от 0 до 100
def validate_percent(value: str) -> bool:
    return validate_int_min_max(value, 0, 100)


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
    def __init__(self, parent, height: int, width: int, scrollbar_position: typing.Literal['left', 'right'] = 'right'):
        super().__init__(parent)

        if scrollbar_position == 'right':
            canvas_position: typing.Literal['left', 'right'] = 'left'
        else:
            canvas_position: typing.Literal['left', 'right'] = 'right'

        self.canvas = tk.Canvas(self, bg=STYLES['FLAT_BTN.BG.2'][1][th], bd=0, highlightthickness=0, height=height, width=width)
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
    def __init__(self, parent, msg: str, btn_text='Ясно', msg_max_width=60, tab=5,
                 msg_justify: typing.Literal['left', 'center', 'right'] = 'center', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.closed = True  # Закрыто ли окно крестиком

        self.lbl_msg = ttk.Label(self, text=split_text(msg, msg_max_width, tab=tab, add_right_spaces=False),
                                 justify=msg_justify, style='Default.TLabel')
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

        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
    def __init__(self, parent, msg='Введите строку', btn_text='Подтвердить',
                 entry_width=45, default_value='', validate_function=None,
                 check_answer_function=None, if_correct_function=None, if_incorrect_function=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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

        bind_ctrl_acvx(self.entry_inp)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_text.get()


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values: list[str] | tuple[str, ...], msg='Выберите один из вариантов',
                 btn_text='Подтвердить', combo_width=40, default_value=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.closed = True  # Закрыто ли окно крестиком

        self.var_answer = tk.StringVar(value=default_value)

        self.lbl_msg = ttk.Label(self, text=split_text(msg, 45, add_right_spaces=False), justify='center',
                                 style='Default.TLabel')
        self.combo_vals = ttk.Combobox(self, textvariable=self.var_answer, values=values,
                                       width=combo_width, state='readonly',
                                       font=('DejaVu Sans Mono', _0_global_scale), style='Default.TCombobox')
        self.btn_ok = ttk.Button(self, text=btn_text, command=self.ok, takefocus=False, style='Yes.TButton')

        self.lbl_msg.grid(   row=0, padx=6, pady=(4, 1))
        self.combo_vals.grid(row=1, padx=6, pady=1)
        self.btn_ok.grid(    row=2, padx=6, pady=4)

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
    def __init__(self, parent, img_name: str, msg: str, btn_text='Ясно', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Выбор режима')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.res: tuple[str, str, str, str, str] | None = None
        self.group_vals = [ALL_GROUPS] + _0_global_dct.groups

        self.var_method = tk.StringVar(value=LEARN_VALUES_METHOD[_0_global_learn_settings[0]])  # Метод учёбы
        self.var_group = tk.StringVar(value=self.group_vals[_0_global_learn_settings[1]])  # Группа слов
        self.var_words = tk.StringVar(value=LEARN_VALUES_WORDS[_0_global_learn_settings[2]])  # Способ набора слов
        self.var_forms = tk.StringVar(value=LEARN_VALUES_FORMS[_0_global_learn_settings[3]])  # Способ набора словоформ
        self.var_order = tk.StringVar(value=LEARN_VALUES_ORDER[_0_global_learn_settings[4]])  # Порядок следования слов

        self.lbl_header = ttk.Label(self, text='Выберите способ учёбы', style='Default.TLabel')
        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_method = ttk.Label(self.frame_main, text='Метод:', style='Default.TLabel')
        self.combo_method = ttk.Combobox(self.frame_main, textvariable=self.var_method, values=LEARN_VALUES_METHOD,
                                         validate='focusin', width=30, state='readonly', style='Default.TCombobox',
                                         font=('DejaVu Sans Mono', _0_global_scale))
        #
        self.lbl_group = ttk.Label(self.frame_main, text='Группа:', style='Default.TLabel')
        self.combo_group = ttk.Combobox(self.frame_main, textvariable=self.var_group,
                                        values=self.group_vals, width=30, state='readonly', style='Default.TCombobox',
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
        self.lbl_method.grid(  row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.combo_method.grid(row=0, column=1, padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_group.grid(   row=1, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_group.grid( row=1, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_words.grid(   row=2, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_words.grid( row=2, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_forms.grid(   row=3, column=0, padx=(6, 1), pady=(0, 3), sticky='E')
        self.combo_forms.grid( row=3, column=1, padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_order.grid(   row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.combo_order.grid( row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.btn_start.grid(row=2, column=0, padx=6, pady=(0, 6))

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
        global _0_global_learn_settings

        method = self.var_method.get()
        group = self.var_group.get()
        words = self.var_words.get()
        if method == LEARN_VALUES_METHOD[0]:
            forms = self.var_forms.get()
        else:
            forms = LEARN_VALUES_FORMS[0]
        order = self.var_order.get()
        self.res = (method, group, words, forms, order)
        _0_global_learn_settings = [LEARN_VALUES_METHOD.index(method),
                                    self.group_vals.index(group),
                                    LEARN_VALUES_WORDS.index(words),
                                    LEARN_VALUES_FORMS.index(forms),
                                    LEARN_VALUES_ORDER.index(order)]

        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)

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

        return self.res


# Окно с сообщением о неверном ответе (для слов, не находящихся в избранном)
class IncorrectAnswerW(tk.Toplevel):
    def __init__(self, parent, user_answer: str, correct_answer: str, with_typo: bool):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Неверно')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
    def __init__(self, parent, search_only_fav: bool, search_only_full: bool, search_wrd: bool, search_tr: bool,
                 search_frm: bool, search_phr: bool, search_nt: bool, search_group: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Параметры поиска')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.group_vals = [ALL_GROUPS] + _0_global_dct.groups

        self.var_search_only_fav = tk.BooleanVar(value=search_only_fav)
        self.var_search_only_full = tk.BooleanVar(value=search_only_full)
        self.var_search_wrd = tk.BooleanVar(value=search_wrd)
        self.var_search_tr = tk.BooleanVar(value=search_tr)
        self.var_search_frm = tk.BooleanVar(value=search_frm)
        self.var_search_phr = tk.BooleanVar(value=search_phr)
        self.var_search_nt = tk.BooleanVar(value=search_nt)
        self.var_search_group = tk.StringVar(value=search_group)

        self.lbl_search_only_fav = ttk.Label(self, text='Искать только среди избранных статей:', style='Default.TLabel')
        self.check_search_only_fav = ttk.Checkbutton(self, variable=self.var_search_only_fav,
                                                     style='Default.TCheckbutton')
        self.lbl_search_only_full = ttk.Label(self, text='Искать слово целиком:', style='Default.TLabel')
        self.check_search_only_full = ttk.Checkbutton(self, variable=self.var_search_only_full,
                                                      style='Default.TCheckbutton')
        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_search_wrd = ttk.Label(self.frame_main, text='Искать среди слов:', style='Default.TLabel')
        self.check_search_wrd = ttk.Checkbutton(self.frame_main, variable=self.var_search_wrd,
                                                style='Default.TCheckbutton')
        self.lbl_search_tr = ttk.Label(self.frame_main, text='Искать среди переводов:', style='Default.TLabel')
        self.check_search_tr = ttk.Checkbutton(self.frame_main, variable=self.var_search_tr,
                                               style='Default.TCheckbutton')
        self.lbl_search_frm = ttk.Label(self.frame_main, text='Искать среди словоформ:', style='Default.TLabel')
        self.check_search_frm = ttk.Checkbutton(self.frame_main, variable=self.var_search_frm,
                                                style='Default.TCheckbutton')
        self.lbl_search_phr = ttk.Label(self.frame_main, text='Искать среди фраз:', style='Default.TLabel')
        self.check_search_phr = ttk.Checkbutton(self.frame_main, variable=self.var_search_phr,
                                                style='Default.TCheckbutton')
        self.lbl_search_nt = ttk.Label(self.frame_main, text='Искать среди сносок:', style='Default.TLabel')
        self.check_search_nt = ttk.Checkbutton(self.frame_main, variable=self.var_search_nt,
                                               style='Default.TCheckbutton')
        # }
        self.frame_group = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.lbl_search_group = ttk.Label(self.frame_group, text='Группа:', style='Default.TLabel')
        self.combo_search_group = ttk.Combobox(self.frame_group, textvariable=self.var_search_group,
                                               values=[ALL_GROUPS] + _0_global_dct.groups, width=26, state='readonly',
                                               style='Default.TCombobox', font=('DejaVu Sans Mono', _0_global_scale))
        # }

        self.lbl_search_only_fav.grid(   row=0, column=0,               padx=(6, 1), pady=6,      sticky='E')
        self.check_search_only_fav.grid( row=0, column=1,               padx=(0, 6), pady=6,      sticky='W')
        self.lbl_search_only_full.grid(  row=1, column=0,               padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_only_full.grid(row=1, column=1,               padx=(0, 6), pady=(0, 6), sticky='W')
        self.frame_main.grid(            row=2, column=0, columnspan=2, padx=6,      pady=6)
        # {
        self.lbl_search_wrd.grid(  row=0, column=0, padx=(6, 1), pady=6,      sticky='E')
        self.check_search_wrd.grid(row=0, column=1, padx=(0, 6), pady=6,      sticky='W')
        self.lbl_search_tr.grid(   row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_tr.grid( row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_frm.grid(  row=2, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_frm.grid(row=2, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_phr.grid(  row=3, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_phr.grid(row=3, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_search_nt.grid(   row=4, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_search_nt.grid( row=4, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        # }
        self.frame_group.grid(row=3, column=0, columnspan=2, padx=6, pady=6)
        # {
        self.lbl_search_group.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.combo_search_group.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        # }

    # Установить фокус
    def set_focus(self):
        self.focus_set()

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

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
                                     int(self.var_search_phr.get()),
                                     int(self.var_search_nt.get()),
                                     self.group_vals.index(self.var_search_group.get()))
        save_local_auto_settings(_0_global_session_number, _0_global_search_settings, _0_global_learn_settings,
                                 _0_global_dct_savename)

        return self.var_search_only_fav.get(), self.var_search_only_full.get(), self.var_search_wrd.get(),\
            self.var_search_tr.get(), self.var_search_frm.get(), self.var_search_phr.get(), self.var_search_nt.get(),\
            self.var_search_group.get()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseOneOfSimilarEntriesW(tk.Toplevel):
    def __init__(self, parent, query: str):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Найдено несколько схожих статей')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
    def choose_entry(self, key: DctKey):
        self.answer = key
        self.destroy()

    # Вывод вариантов
    def print(self):
        # Вывод вариантов
        keys = [key for key in _0_global_dct.d.keys() if key[0] == self.search_wrd]
        for i in range(len(keys)):
            key = keys[i]
            self.widgets_wrd += [ttk.Button(self.scrolled_frame_wrd.frame_canvas,
                                            text=get_all_entry_info(_0_global_dct.d[key], 75, 13),
                                            command=lambda key=key: self.choose_entry(key),
                                            takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')]

        # Расположение виджетов
        for i in range(len(self.widgets_wrd)):
            self.widgets_wrd[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')

        self.scrolled_frame_wrd.canvas.yview_moveto(0.0)

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
    def __init__(self, parent, title, default_value=('', ''), check_answer_function=None):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - {title}')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.closed = True  # Закрыто ли окно крестиком
        self.check_answer_function = check_answer_function  # Функция, проверяющая корректность ответа

        self.var_phr = tk.StringVar(value=default_value[0])
        self.var_tr = tk.StringVar(value=default_value[1])

        self.lbl_phr = ttk.Label(self, text='Фраза:', style='Default.TLabel')
        self.entry_phr = ttk.Entry(self, textvariable=self.var_phr, width=45, validate='all',
                                   style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_tr = ttk.Label(self, text='Перевод:', style='Default.TLabel')
        self.entry_tr = ttk.Entry(self, textvariable=self.var_tr, width=45, validate='all',
                                  style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_ok = ttk.Button(self, text='Готово', command=self.ok, takefocus=False, style='Default.TButton')

        self.lbl_phr.grid(  row=0, column=0,     padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_phr.grid(row=0, column=1,     padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr.grid(   row=1, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr.grid( row=1, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.btn_ok.grid(   row=3, columnspan=2, padx=6,      pady=(0, 6))

        self.entry_phr.bind('<Down>', lambda event: self.entry_tr.focus_set())
        self.entry_tr.bind('<Up>', lambda event: self.entry_phr.focus_set())

        self.entry_phr.icursor(len(self.var_phr.get()))

    # Добавление фразы
    def ok(self):
        global _0_global_has_progress

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

        bind_ctrl_acvx(self.entry_phr)
        bind_ctrl_acvx(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed, self.var_phr.get(), self.var_tr.get()


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, key: DctKey):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Изменение статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.dct_key = key
        self.line_width = 35
        self.max_height_w = 3
        self.max_height_t = 4
        self.max_height_f = 4
        self.max_height_p = 3
        self.max_height_n = 3
        self.max_height_g = 3

        self.var_fav = tk.BooleanVar(value=_0_global_dct.d[key].fav)

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

        self.frame_main = ttk.Frame(self, style='Default.TFrame')
        # {
        self.lbl_wrd = ttk.Label(self.frame_main, text='Слово:', style='Default.TLabel')
        self.scrollbar_wrd = ttk.Scrollbar(self.frame_main, style='Vertical.TScrollbar')
        self.txt_wrd = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_wrd.set,
                               font=('DejaVu Sans Mono', _0_global_scale + 1), relief='solid', bg=STYLES['*.BG.ENTRY'][1][th],
                               fg=STYLES['*.FG.*'][1][th], selectbackground=STYLES['*.BG.SEL'][1][th], selectforeground=STYLES['*.FG.SEL'][1][th],
                               highlightbackground=STYLES['*.BORDER_CLR.*'][1][th])
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
        self.lbl_frm = ttk.Label(self.frame_main, text='Формы слова:', style='Default.TLabel')
        self.scrolled_frame_frm = ScrollFrame(self.frame_main,
                                              SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                              SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_frm_add = ttk.Button(self.frame_main, command=self.frm_add, width=2, takefocus=False)
        set_image(self.btn_frm_add, self.img_add, img_add, '+')
        if self.btn_frm_add['style'] == 'Image.TButton':
            self.tip_btn_frm_add = ttip.Hovertip(self.btn_frm_add, 'Добавить словоформу', hover_delay=500)
        #
        self.lbl_phrases = ttk.Label(self.frame_main, text='Фразы:', style='Default.TLabel')
        self.scrolled_frame_phr = ScrollFrame(self.frame_main,
                                              SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                              SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_phrase_add = ttk.Button(self.frame_main, command=self.phrase_add, width=2, takefocus=False)
        set_image(self.btn_phrase_add, self.img_add, img_add, '+')
        if self.btn_phrase_add['style'] == 'Image.TButton':
            self.tip_btn_phrase_add = ttip.Hovertip(self.btn_phrase_add, 'Добавить фразу', hover_delay=500)
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
        self.lbl_gr = ttk.Label(self.frame_main, text='Группы:', style='Default.TLabel')
        self.scrolled_frame_gr = ScrollFrame(self.frame_main,
                                             SCALE_SMALL_FRAME_HEIGHT_SHORT[_0_global_scale - SCALE_MIN],
                                             SCALE_SMALL_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.btn_gr_add = ttk.Button(self.frame_main, command=self.gr_add, width=2, takefocus=False)
        set_image(self.btn_gr_add, self.img_add, img_add, '+')
        if self.btn_gr_add['style'] == 'Image.TButton':
            self.tip_btn_gr_add = ttip.Hovertip(self.btn_gr_add, 'Добавить группу', hover_delay=500)
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
        self.lbl_frm.grid(           row=2, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_frm.grid(row=2, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_frm_add.grid(       row=2, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_phrases.grid(       row=3, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_phr.grid(row=3, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_phrase_add.grid(    row=3, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_notes.grid(        row=4, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_nt.grid(row=4, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_note_add.grid(     row=4, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_gr.grid(           row=5, column=0,               padx=(6, 1), pady=(0, 3), sticky='E')
        self.scrolled_frame_gr.grid(row=5, column=1, columnspan=2, padx=(0, 1), pady=(0, 3), sticky='WE')
        self.btn_gr_add.grid(       row=5, column=3,               padx=(3, 6), pady=(0, 3), sticky='W')
        #
        self.lbl_fav.grid(  row=6, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_fav.grid(row=6, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
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
        new_wrd = encode_special_combinations(new_wrd, _0_global_special_combinations)
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
        tr = encode_special_combinations(tr, _0_global_special_combinations)

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
        new_tr = encode_special_combinations(new_tr, _0_global_special_combinations)

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

    # Добавить словоформу
    def frm_add(self):
        global _0_global_has_progress

        if not _0_global_dct.ctg:
            warning(self, 'Отсутствуют категории слов!\n'
                          'Чтобы их добавить, перейдите в\n'
                          'Настройки/Настройки открытого словаря/Грамматические категории')
            return

        window_form = AddFormW(self, self.dct_key, combo_width=combobox_width(tuple(_0_global_dct.ctg.keys()),
                                                                              5, 100))  # Создание словоформы
        frm_key, frm = window_form.open()
        if not frm_key:
            return
        frm = encode_special_combinations(frm, _0_global_special_combinations)

        _0_global_dct.add_frm(self.dct_key, frm_key, frm)

        _0_global_has_progress = True
        self.refresh(False)

    # Изменить словоформу
    def frm_edt(self, frm_key: FrmKey):
        global _0_global_has_progress

        window_entry = PopupEntryW(self, 'Введите новую форму слова',
                                   default_value=_0_global_dct.d[self.dct_key].forms[frm_key],
                                   check_answer_function=lambda wnd, val:
                                   check_not_void(wnd, val, 'Словоформа должна содержать хотя бы один символ!'))
        closed, new_frm = window_entry.open()
        if closed:
            return
        new_frm = encode_special_combinations(new_frm, _0_global_special_combinations)

        _0_global_dct.d[self.dct_key].forms[frm_key] = new_frm

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить словоформу
    def frm_del(self, frm_key: FrmKey):
        global _0_global_has_progress

        _0_global_dct.delete_frm(self.dct_key, frm_key)

        _0_global_has_progress = True
        self.refresh(False)

    # Добавить фразу
    def phrase_add(self):
        global _0_global_has_progress

        window = AddPhraseW(self, 'Добавление фразы',
                            check_answer_function=lambda wnd, val:
                            check_phr(wnd, _0_global_dct.d[self.dct_key].phrases, val, key_to_wrd(self.dct_key)))
        closed, phr, phr_tr = window.open()
        if closed:
            return
        phr = encode_special_combinations(phr, _0_global_special_combinations)
        phr_tr = encode_special_combinations(phr_tr, _0_global_special_combinations)

        _0_global_dct.add_phrase(self.dct_key, phr, phr_tr)

        _0_global_has_progress = True
        self.refresh(False)

    # Изменить фразу
    def phrase_edt(self, p: tuple[str, str]):
        global _0_global_has_progress

        phr, phr_tr = p

        window = AddPhraseW(self, 'Изменение фразы', default_value=(phr, phr_tr),
                            check_answer_function=lambda wnd, val:
                            check_phr_edit(wnd, _0_global_dct.d[self.dct_key].phrases, (phr, phr_tr), val,
                                           key_to_wrd(self.dct_key)))
        closed, new_phr, new_phr_tr = window.open()
        if closed:
            return
        new_phr = encode_special_combinations(new_phr, _0_global_special_combinations)
        new_phr_tr = encode_special_combinations(new_phr_tr, _0_global_special_combinations)

        _0_global_dct.delete_phrase(self.dct_key, phr, phr_tr)
        _0_global_dct.add_phrase(self.dct_key, new_phr, new_phr_tr)

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить фразу
    def phrase_del(self, p: tuple[str, str]):
        global _0_global_has_progress

        phr, phr_tr = p
        _0_global_dct.delete_phrase(self.dct_key, phr, phr_tr)

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
        note = encode_special_combinations(note, _0_global_special_combinations)

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
        new_note = encode_special_combinations(new_note, _0_global_special_combinations)

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

    # Добавить группу
    def gr_add(self):
        global _0_global_has_progress

        if not _0_global_dct.groups:
            warning(self, 'Отсутствуют группы!\n'
                          'Чтобы их добавить, перейдите в\n'
                          'Настройки/Настройки открытого словаря/Группы')
            return
        values = [group for group in _0_global_dct.groups if group not in _0_global_dct.d[self.dct_key].groups]
        if not values:
            warning(self, 'Статья уже добавлена во все группы')
            return

        window_group = PopupChooseW(self, values, 'Выберите группу', default_value=values[0])
        closed, group = window_group.open()
        if closed:
            return
        group = encode_special_combinations(group, _0_global_special_combinations)

        _0_global_dct.add_entries_to_group(group, [self.dct_key])

        _0_global_has_progress = True
        self.refresh(False)

    # Удалить группу
    def gr_del(self, group: str):
        global _0_global_has_progress

        _0_global_dct.remove_entries_from_group(group, [self.dct_key])

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

    # Закрыть окно
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
        for btn in self.tr_buttons + self.nt_buttons + self.phr_buttons + self.frm_buttons + self.gr_buttons:
            btn.destroy()
        # Удаляем старые фреймы
        for fr in self.tr_frames + self.nt_frames + self.phr_frames + self.frm_frames + self.gr_frames:
            fr.unbind('<Enter>')
            fr.unbind('<Control-D>')
            fr.unbind('<Control-d>')
            fr.unbind('<Leave>')
            fr.destroy()

        # Выбираем содержимое
        self.translations = [tr for tr in _0_global_dct.d[self.dct_key].tr]
        self.notes = [nt for nt in _0_global_dct.d[self.dct_key].notes]
        self.phrases = []
        for phr in _0_global_dct.d[self.dct_key].phrases.keys():
            for pt in _0_global_dct.d[self.dct_key].phrases[phr]:
                self.phrases += [(phr, pt)]
        self.forms = [frm for frm in _0_global_dct.d[self.dct_key].forms.keys()]
        self.groups = [gr for gr in _0_global_dct.d[self.dct_key].groups]
        tr_count = len(self.translations)
        nt_count = len(self.notes)
        phr_count = len(self.phrases)
        frm_count = len(self.forms)
        gr_count = len(self.groups)

        # Создаём новые фреймы
        self.tr_frames = tuple([ttk.Frame(self.scrolled_frame_tr.frame_canvas, style='Invis.TFrame')
                                for i in range(tr_count)])
        self.nt_frames = tuple([ttk.Frame(self.scrolled_frame_nt.frame_canvas, style='Invis.TFrame')
                                for i in range(nt_count)])
        self.phr_frames = tuple([ttk.Frame(self.scrolled_frame_phr.frame_canvas, style='Invis.TFrame')
                                 for i in range(phr_count)])
        self.frm_frames = tuple([ttk.Frame(self.scrolled_frame_frm.frame_canvas, style='Invis.TFrame')
                                 for i in range(frm_count)])
        self.gr_frames = tuple([ttk.Frame(self.scrolled_frame_gr.frame_canvas, style='Invis.TFrame')
                                for i in range(gr_count)])
        # Создаём новые кнопки
        self.tr_buttons = [ttk.Button(self.tr_frames[i], command=lambda i=i: self.tr_edt(self.translations[i]),
                                      takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                           for i in range(tr_count)]
        self.nt_buttons = [ttk.Button(self.nt_frames[i], command=lambda i=i: self.note_edt(self.notes[i]),
                                      takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                           for i in range(nt_count)]
        self.phr_buttons = [ttk.Button(self.phr_frames[i], command=lambda i=i: self.phrase_edt(self.phrases[i]),
                                       takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                            for i in range(phr_count)]
        self.frm_buttons = [ttk.Button(self.frm_frames[i], command=lambda i=i: self.frm_edt(self.forms[i]),
                                       takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                            for i in range(frm_count)]
        self.gr_buttons = [ttk.Button(self.gr_frames[i], takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                           for i in range(gr_count)]
        # Выводим текст на кнопки
        for i in range(tr_count):
            tr = self.translations[i]
            self.tr_buttons[i].configure(text=split_text(tr, 35))
        for i in range(nt_count):
            nt = self.notes[i]
            self.nt_buttons[i].configure(text=split_text(nt, 35))
        for i in range(phr_count):
            phr = self.phrases[i][0]
            phr_tr = self.phrases[i][1]
            self.phr_buttons[i].configure(text=split_text(f'{phr} - {phr_tr}', 35))
        for i in range(frm_count):
            frm = self.forms[i]
            text = f'[{frm_key_to_str_for_print(frm)}] {_0_global_dct.d[self.dct_key].forms[frm]}'
            self.frm_buttons[i].configure(text=split_text(text, 35))
        for i in range(gr_count):
            gr = self.groups[i]
            self.gr_buttons[i].configure(text=split_text(gr, 35))
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
        for i in range(phr_count):
            self.phr_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.phr_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        for i in range(frm_count):
            self.frm_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.frm_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        for i in range(gr_count):
            self.gr_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.gr_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }
        # Привязываем события
        for i in range(tr_count):
            self.tr_frames[i].bind('<Enter>', lambda event, i=i: self.tr_frames[i].focus_set())
            self.tr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.tr_frames[i].bind('<Control-KeyPress>',
                                   lambda key, i=i:
                                   bind_keypress(key, [('D', lambda: self.tr_del(self.translations[i]))]))
        for i in range(nt_count):
            self.nt_frames[i].bind('<Enter>', lambda event, i=i: self.nt_frames[i].focus_set())
            self.nt_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.nt_frames[i].bind('<Control-KeyPress>',
                                   lambda key, i=i:
                                   bind_keypress(key, [('D', lambda: self.note_del(self.notes[i]))]))
        for i in range(phr_count):
            self.phr_frames[i].bind('<Enter>', lambda event, i=i: self.phr_frames[i].focus_set())
            self.phr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.phr_frames[i].bind('<Control-KeyPress>',
                                    lambda key, i=i:
                                    bind_keypress(key, [('D', lambda: self.phrase_del(self.phrases[i]))]))
        for i in range(frm_count):
            self.frm_frames[i].bind('<Enter>', lambda event, i=i: self.frm_frames[i].focus_set())
            self.frm_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frm_frames[i].bind('<Control-KeyPress>',
                                    lambda key, i=i:
                                    bind_keypress(key, [('D', lambda: self.frm_del(self.forms[i]))]))
        for i in range(gr_count):
            self.gr_frames[i].bind('<Enter>', lambda event, i=i: self.gr_frames[i].focus_set())
            self.gr_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.gr_frames[i].bind('<Control-KeyPress>',
                                   lambda key, i=i:
                                   bind_keypress(key, [('D', lambda: self.gr_del(self.groups[i]))]))
        # Изменяем высоту полей
        self.scrolled_frame_tr.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                             for btn in self.tr_buttons]),
                                                        self.max_height_t)) *
                                             SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_nt.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                             for btn in self.nt_buttons]),
                                                        self.max_height_n)) *
                                             SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_phr.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                              for btn in self.phr_buttons]),
                                                         self.max_height_p)) *
                                              SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_frm.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                              for btn in self.frm_buttons]),
                                                         self.max_height_f)) *
                                              SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])
        self.scrolled_frame_gr.resize(height=max(1, min(sum([field_height(btn['text'], 35)
                                                             for btn in self.gr_buttons]),
                                                        self.max_height_g)) *
                                             SCALE_FRAME_HEIGHT_ONE_LINE[_0_global_scale - SCALE_MIN])

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame_tr.canvas.yview_moveto(0.0)
            self.scrolled_frame_nt.canvas.yview_moveto(0.0)
            self.scrolled_frame_phr.canvas.yview_moveto(0.0)
            self.scrolled_frame_frm.canvas.yview_moveto(0.0)
            self.scrolled_frame_gr.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы изменить поле, наведите на него мышку и нажмите ЛКМ\n'
                        '* Чтобы удалить поле, наведите на него мышку и нажмите Ctrl+D\n\n'
                        'Фразы: Сюда вы можете записать любые фразы с этим словом, как пример его употребления\n'
                        'Сноски: Здесь вы можете указать любые факты об этом слове, которые посчитаете нужными\n'
                        'Группы: Вы можете объединять слова, чтобы учить их группами\n',
                  msg_justify='left').open()

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
    def __init__(self, parent, key: DctKey, combo_width=20):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.closed = True  # Закрыто ли окно крестиком
        self.categories = list(_0_global_dct.ctg.keys())  # Список категорий
        self.ctg_values = list(_0_global_dct.ctg[self.categories[0]])  # Список значений выбранной категории
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
        self.ctg_values = list(_0_global_dct.ctg[self.var_ctg.get()])
        self.var_val = tk.StringVar(value=self.ctg_values[0])
        self.combo_val.configure(textvariable=self.var_val, values=self.ctg_values,
                                 width=combobox_width(self.ctg_values, 5, 100))

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_form.focus_set()

        bind_ctrl_acvx(self.entry_form)
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
        if tuple(self.template) in _0_global_dct.d[self.key].forms.keys():
            return None, None
        return tuple(self.template), self.var_form.get()


# Окно настроек грамматических категорий
class CategoriesSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
        self.has_changes = add_ctg(self, _0_global_dct) or self.has_changes
        self.print_categories(False)

    # Переименовать категорию
    def rename(self, ctg_key: str):
        self.has_changes = rename_ctg(self, _0_global_dct, ctg_key) or self.has_changes
        self.print_categories(False)

    # Удалить категорию
    def delete(self, ctg_key: str):
        self.has_changes = delete_ctg(self, _0_global_dct, ctg_key) or self.has_changes
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
        self.categories = list(_0_global_dct.ctg.keys())
        categories_count = len(self.categories)

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(categories_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.values(self.categories[i]),
                                   takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                        for i in range(categories_count)]
        for i in range(categories_count):
            # Выводим текст на кнопки
            ctg = self.categories[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))

            # Расставляем элементы
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-KeyPress>',
                                lambda key, i=i: bind_keypress(key, [('R', lambda: self.rename(self.categories[i])),
                                                                     ('D', lambda: self.delete(self.categories[i]))]))

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

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.has_changes = False

        self.img_about = tk.PhotoImage()

        self.groups = []
        self.frames = []
        self.buttons = []
        self.tips = []

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
        group = encode_special_combinations(group, _0_global_special_combinations)
        _0_global_dct.add_group(group)

        self.print_groups(False)
        self.has_changes = True

    # Переименовать группу
    def rename(self, group_old: str):
        global _0_global_fav_groups, _0_global_learn_settings

        window = PopupEntryW(self, 'Введите новое название группы', default_value=group_old,
                             check_answer_function=lambda wnd, val:
                             check_group_name_edit(wnd, _0_global_dct.groups, group_old, val))
        closed, group_new = window.open()
        if closed:
            return
        group_new = encode_special_combinations(group_new, _0_global_special_combinations)

        if _0_global_dct.groups.index(group_old) + 1 == _0_global_learn_settings[1]:
            _0_global_learn_settings[1] = len(_0_global_dct.groups)
        elif _0_global_dct.groups.index(group_old) + 1 < _0_global_learn_settings[1]:
            _0_global_learn_settings[1] -= 1
        _0_global_dct.rename_group(group_old, group_new)
        if group_old in _0_global_fav_groups:
            _0_global_fav_groups.remove(group_old)
            _0_global_fav_groups += [group_new]

        self.print_groups(False)
        self.has_changes = True

    # Удалить группу
    def delete(self, group: str):
        global _0_global_fav_groups, _0_global_learn_settings

        group_size = _0_global_dct.count_entries_in_group(group)[0]
        if group_size != 0:
            tmp = set_postfix(group_size, ('слово будет убрано', 'слова будут убраны', 'слов будут убраны'))
            window_dia = PopupDialogueW(self, f'{group_size} {tmp} из группы "{group}", а сама группа будет удалена!\n'
                                              f'Хотите продолжить?')
            answer = window_dia.open()
            if not answer:
                return

        if _0_global_dct.groups.index(group) + 1 == _0_global_learn_settings[1]:
            _0_global_learn_settings[1] = 0
        elif _0_global_dct.groups.index(group) + 1 < _0_global_learn_settings[1]:
            _0_global_learn_settings[1] -= 1
        _0_global_dct.delete_group(group)
        if group in _0_global_fav_groups:
            _0_global_fav_groups.remove(group)

        self.print_groups(False)
        self.has_changes = True

    # Добавить группу в избранное
    def fav(self, group: str):
        global _0_global_fav_groups

        if group in _0_global_fav_groups:
            _0_global_fav_groups.remove(group)
        else:
            _0_global_fav_groups += [group]

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
        self.groups = list(_0_global_dct.groups)
        groups_count = len(self.groups)

        # Создаём новые фреймы
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(groups_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i], command=lambda i=i: self.rename(self.groups[i]),
                                   takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                        for i in range(groups_count)]
        # Создаём новые подсказки
        self.tips = [ttip.Hovertip(self.buttons[i],
                                   f'Статей в группе: {_0_global_dct.count_entries_in_group(self.groups[i])[0]}',
                                   hover_delay=500)
                     for i in range(groups_count)]
        for i in range(groups_count):
            # Выводим текст на кнопки
            group = self.groups[i]
            if group in _0_global_fav_groups:
                self.buttons[i].configure(text=split_text(f'{group} (*)', 35))
            else:
                self.buttons[i].configure(text=split_text(f'{group}', 35))

            # Расставляем элементы
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-KeyPress>',
                                lambda key, i=i: bind_keypress(key, [('R', lambda: self.rename(self.groups[i])),
                                                                     ('D', lambda: self.delete(self.groups[i])),
                                                                     ('F', lambda: self.fav(self.groups[i]))]))

        # Если требуется, прокручиваем вверх
        if move_scroll:
            self.scrolled_frame.canvas.yview_moveto(0.0)

    # Справка об окне (срабатывает при нажатии на кнопку)
    def about_window(self):
        PopupMsgW(self, '* Чтобы переименовать группу, наведите на неё мышку и нажмите ЛКМ или Ctrl+R\n'
                        '* Чтобы удалить группу, наведите на неё мышку и нажмите Ctrl+D\n'
                        '* Чтобы все новые статьи автоматически добавлялись в группу, '
                        'наведите на эту группу мышку и нажмите Ctrl+F',
                  msg_justify='left').open()

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
    def __init__(self, parent, ctg_key: str):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.parent = parent
        self.ctg_key = ctg_key  # Название изменяемой категории
        self.ctg_values = _0_global_dct.ctg[self.ctg_key]  # Значения изменяемой категории
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
        self.has_changes = add_ctg_val(self, _0_global_dct, self.ctg_key, self.ctg_values) or self.has_changes
        self.print_ctg_values(False)

    # Переименовать значение категории
    def rename(self, val: str):
        self.has_changes = rename_ctg_val(self, _0_global_dct, self.ctg_key, val) or self.has_changes
        self.print_ctg_values(False)

    # Удалить значение категории
    def delete(self, val: str):
        self.has_changes = delete_ctg_val(self, _0_global_dct, self.ctg_key, val) or self.has_changes
        self.print_ctg_values(False)
        if self.ctg_key not in _0_global_dct.ctg:
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
        self.frames = [ttk.Frame(self.scrolled_frame.frame_canvas, style='Invis.TFrame')
                       for i in range(categories_count)]
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.rename(self.values[i]),
                                   takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                        for i in range(categories_count)]
        for i in range(categories_count):
            # Выводим текст на кнопки
            ctg = self.values[i]
            self.buttons[i].configure(text=split_text(f'{ctg}', 35))

            # Расставляем элементы
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-KeyPress>',
                                lambda key, i=i: bind_keypress(key, [('R', lambda: self.rename(self.values[i])),
                                                                     ('D', lambda: self.delete(self.values[i]))]))

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

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
                                       text=split_text('## -> #, %% -> % и т. д.', 35), style='FlatL.TLabel')])
        # Создаём новые кнопки
        self.buttons = [ttk.Button(self.frames[i],
                                   command=lambda i=i: self.edit(self.combinations[i]),
                                   takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                        for i in range(combinations_count)]
        for i in range(combinations_count):
            # Выводим текст на кнопки
            cmb = self.combinations[i]
            self.buttons[i].configure(text=split_text(special_combination(cmb), 35))

            # Расставляем элементы
            self.frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.frames[i].bind('<Enter>', lambda event, i=i: self.frames[i].focus_set())
            self.frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.frames[i].bind('<Control-KeyPress>',
                                lambda key, i=i: bind_keypress(key, [('E', lambda: self.edit(self.combinations[i])),
                                                                     ('D', lambda: self.delete(self.combinations[i]))]))

        self.frames[combinations_count].grid(row=combinations_count, column=0, padx=0, pady=0, sticky='WE')

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

        self.bind('<Return>', lambda event: self.destroy())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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

        bind_ctrl_acvx(self.entry_val)
        bind_ctrl_acvx(self.entry_key_symbol)
        self.bind('<Return>', lambda event: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.style_keys = list(STYLES.keys())

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
                       for _ in range(len(self.style_keys))]
        self.buttons = [tk.Button(self.scrolled_frame.frame_canvas, relief='solid', overrelief='raised',
                                  borderwidth=1, width=18, takefocus=False)
                        for i in range(len(self.style_keys))]
        # Получается по 2 лишних экземпляра каждого виджета (но пусть будет так)

        for i in range(len(self.style_keys)):
            st_key = self.style_keys[i]
            if st_key not in ('FRAME.RELIEF.*', 'TXT.RELIEF.*'):
                self.labels[i].configure(text=f'{STYLES[st_key][0]}:')
                self.buttons[i].configure(command=lambda i=i: self.choose_color(i))

                self.labels[i].grid( row=i, column=0, padx=(6, 1), sticky='E')
                self.buttons[i].grid(row=i, column=1, padx=(0, 6), sticky='W')
                if i == 0:
                    self.labels[i].grid(pady=(6, 3))
                    self.buttons[i].grid(pady=(6, 3))
                elif i == len(self.style_keys) - 1:
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

        self.vcmd_relief_frame = (self.register(lambda value: _choose_relief('FRAME.RELIEF.*', value)), '%P')
        self.vcmd_relief_text = (self.register(lambda value: _choose_relief('TXT.RELIEF.*', value)), '%P')

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
        for i in range(len(self.style_keys)):
            st_key = self.style_keys[i]
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
        st_key = self.style_keys[n]
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
            for el in self.style_keys:
                file.write(f'\n{el} = {self.custom_styles[el]}')

        if self.dir_with_images != CUSTOM_THEME_PATH:
            images = [img_about_typo, img_about, img_ok, img_cancel, img_fav, img_unfav,
                      img_add_to_group, img_remove_from_group, img_edit, img_add, img_delete, img_select_page,
                      img_unselect_page, img_select_all, img_unselect_all, img_print_out, img_redo, img_undo,
                      img_arrow_left, img_arrow_right, img_double_arrow_left, img_double_arrow_right, img_trashcan]
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
                for i in range(len(self.style_keys)):
                    el = self.style_keys[i]

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
                    i = self.style_keys.index(el)
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
                for i in range(len(self.style_keys)):
                    el = self.style_keys[i]

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
                    i = self.style_keys.index(el)
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
                    self.buttons[i].config(bg=self.custom_styles[key], activebackground=self.custom_styles[key])
                i += 1

        self.set_demo_styles()

    # Обновить стили в демонстрации
    def set_demo_styles(self):
        self.custom_styles['FRAME.RELIEF.*'] = self.var_relief_frame.get()
        self.custom_styles['TXT.RELIEF.*'] = self.var_relief_text.get()

        self.txt_demo.config(relief=self.custom_styles['TXT.RELIEF.*'],
                             bg=self.custom_styles['*.BG.ENTRY'],
                             fg=self.custom_styles['*.FG.*'],
                             selectbackground=self.custom_styles['*.BG.SEL'],
                             selectforeground=self.custom_styles['*.FG.SEL'],
                             highlightbackground=self.custom_styles['*.BORDER_CLR.*'])

        # Стиль label "demo default"
        self.st_lbl_default = ttk.Style()
        self.st_lbl_default.theme_use('alt')
        self.st_lbl_default.configure('DemoDefault.TLabel',
                                      font=('StdFont', _0_global_scale),
                                      background=self.custom_styles['*.BG.*'],
                                      foreground=self.custom_styles['*.FG.*'])

        # Стиль label "demo header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('DemoHeader.TLabel',
                                     font=('StdFont', _0_global_scale + 5),
                                     background=self.custom_styles['*.BG.*'],
                                     foreground=self.custom_styles['*.FG.*'])

        # Стиль label "demo logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('DemoLogo.TLabel',
                                   font=('Times', _0_global_scale + 11),
                                   background=self.custom_styles['*.BG.*'],
                                   foreground=self.custom_styles['*.FG.LOGO'])

        # Стиль label "demo footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('DemoFooter.TLabel',
                                     font=('StdFont', _0_global_scale - 2),
                                     background=self.custom_styles['*.BG.*'],
                                     foreground=self.custom_styles['*.FG.FOOTER'])

        # Стиль label "demo warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('DemoWarn.TLabel',
                                   font=('StdFont', _0_global_scale),
                                   background=self.custom_styles['*.BG.*'],
                                   foreground=self.custom_styles['*.FG.WARN'])

        # Стиль entry "demo"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('DemoDefault.TEntry',
                                font=('StdFont', _0_global_scale))
        self.st_entry.map('DemoDefault.TEntry',
                          fieldbackground=[('readonly', self.custom_styles['*.BG.*']),
                                           ('!readonly', self.custom_styles['*.BG.ENTRY'])],
                          foreground=[('readonly', self.custom_styles['*.FG.*']),
                                      ('!readonly', self.custom_styles['*.FG.ENTRY'])],
                          selectbackground=[('readonly', self.custom_styles['*.BG.SEL']),
                                            ('!readonly', self.custom_styles['*.BG.SEL'])],
                          selectforeground=[('readonly', self.custom_styles['*.FG.SEL']),
                                            ('!readonly', self.custom_styles['*.FG.SEL'])])

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
                                background=[('pressed', self.custom_styles['BTN.BG.ACT']),
                                            ('active', self.custom_styles['BTN.BG.*']),
                                            ('!active', self.custom_styles['BTN.BG.*'])],
                                foreground=[('pressed', self.custom_styles['*.FG.*']),
                                            ('active', self.custom_styles['*.FG.*']),
                                            ('!active', self.custom_styles['*.FG.*'])])

        # Стиль button "demo disabled"
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure('DemoDisabled.TButton',
                                       font=('StdFont', _0_global_scale + 2),
                                       borderwidth=1)
        self.st_btn_disabled.map('DemoDisabled.TButton',
                                 relief=[('active', 'raised'),
                                         ('!active', 'raised')],
                                 background=[('active', self.custom_styles['BTN.BG.DISABL']),
                                             ('!active', self.custom_styles['BTN.BG.DISABL'])],
                                 foreground=[('active', self.custom_styles['BTN.FG.DISABL']),
                                             ('!active', self.custom_styles['BTN.FG.DISABL'])])

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
                            background=[('pressed', self.custom_styles['BTN.BG.Y_ACT']),
                                        ('active', self.custom_styles['BTN.BG.Y']),
                                        ('!active', self.custom_styles['BTN.BG.Y'])],
                            foreground=[('pressed', self.custom_styles['*.FG.*']),
                                        ('active', self.custom_styles['*.FG.*']),
                                        ('!active', self.custom_styles['*.FG.*'])])

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
                           background=[('pressed', self.custom_styles['BTN.BG.N_ACT']),
                                       ('active', self.custom_styles['BTN.BG.N']),
                                       ('!active', self.custom_styles['BTN.BG.N'])],
                           foreground=[('pressed', self.custom_styles['*.FG.*']),
                                       ('active', self.custom_styles['*.FG.*']),
                                       ('!active', self.custom_styles['*.FG.*'])])

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
                              background=[('pressed', self.custom_styles['BTN.BG.IMG_ACT']),
                                          ('active', self.custom_styles['BTN.BG.IMG_HOV']),
                                          ('!active', self.custom_styles['*.BG.*'])],
                              foreground=[('pressed', self.custom_styles['*.FG.*']),
                                          ('active', self.custom_styles['*.FG.*']),
                                          ('!active', self.custom_styles['*.FG.*'])])

        # Стиль checkbutton "demo"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map('DemoDefault.TCheckbutton',
                          background=[('active', self.custom_styles['CHECK.BG.SEL']),
                                      ('!active', self.custom_styles['*.BG.*'])])

        # Стиль frame "demo default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure('DemoDefault.TFrame',
                                        borderwidth=1,
                                        relief=self.custom_styles['FRAME.RELIEF.*'],
                                        background=self.custom_styles['*.BG.*'],
                                        bordercolor=self.custom_styles['*.BORDER_CLR.*'])

        # Стиль frame "window"
        self.st_frame_window = ttk.Style()
        self.st_frame_window.theme_use('alt')
        self.st_frame_window.configure('Window.TFrame',
                                       borderwidth=1,
                                       relief='groove',
                                       background=self.custom_styles['*.BG.*'],
                                       bordercolor='#888888')

        # Стиль scrollbar "vertical"
        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map('Demo.Vertical.TScrollbar',
                            troughcolor=[('disabled', self.custom_styles['*.BG.*']),
                                         ('pressed', self.custom_styles['SCROLL.BG.ACT']),
                                         ('!pressed', self.custom_styles['SCROLL.BG.*'])],
                            background=[('disabled', self.custom_styles['*.BG.*']),
                                        ('pressed', self.custom_styles['SCROLL.FG.ACT']),
                                        ('!pressed', self.custom_styles['SCROLL.FG.*'])])

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

        self.bind('<Escape>', lambda event: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()


""" Графический интерфейс - основные окна """


# Окно изучения слов
class LearnW(tk.Toplevel):
    def __init__(self, parent, parameters: tuple[str, str, str, str, str]):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Учёба')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.current_key = None  # Текущее слово
        self.current_form = None  # Текущая форма (если начальная, то None)
        self.current_phrase = None  # Текущая фраза
        self.homonyms = []  # Омонимы к текущему слову
        self.count_all = 0  # Счётчик всех ответов
        self.count_correct = 0  # Счётчик верных ответов
        self.learn_method = parameters[0]  # Метод учёбы
        self.group = parameters[1]  # Группа, из которой берутся слова
        self.words = parameters[2]  # Способ набора слов
        self.forms = parameters[3]  # Способ набора словоформ
        self.order = parameters[4]  # Порядок следования слов
        self.pool = set()  # Набор слов для изучения

        self.create_pool()  # Формируем пул слов, которые будут использоваться при учёбе

        self.len_of_pool = len(self.pool)  # Количество изучаемых слов

        self.var_input = tk.StringVar()

        self.lbl_global_rating = ttk.Label(self, text=f'Ваш общий рейтинг по словарю: {self.get_percent()}',
                                           style='Default.TLabel')
        self.lbl_count = ttk.Label(self, text=f'Отвечено: 0/{self.len_of_pool}', style='Default.TLabel')
        self.scrollbar = ttk.Scrollbar(self, style='Vertical.TScrollbar')
        self.txt_dct = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set,
                               font=('StdFont', _0_global_scale), bg=STYLES['*.BG.ENTRY'][1][th], fg=STYLES['*.FG.*'][1][th],
                               selectbackground=STYLES['*.BG.SEL'][1][th], selectforeground=STYLES['*.FG.SEL'][1][th],
                               relief=STYLES['TXT.RELIEF.*'][1][th], highlightbackground=STYLES['*.BORDER_CLR.*'][1][th])
        self.scrollbar.config(command=self.txt_dct.yview)
        self.frame_main = ttk.Frame(self, style='Invis.TFrame')
        # {
        self.btn_input = ttk.Button(self.frame_main, text='Ввод', command=self.input, width=6,
                                    takefocus=False, style='Default.TButton')
        self.entry_input = ttk.Entry(self.frame_main, textvariable=self.var_input, width=36,
                                     style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_show_entry = ttk.Button(self.frame_main, text='Слово и перевод', command=self.show_entry, width=15,
                                         takefocus=False, style='Default.TButton')
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
        self.btn_input.grid(  row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        if self.learn_method in LEARN_VALUES_METHOD[2:4]:
            self.btn_show_entry.grid(row=0, column=2, padx=0, pady=0, sticky='W')
        else:
            self.btn_show_notes.grid(   row=0, column=2, padx=(0, 3), pady=0, sticky='W')
            self.btn_show_homonyms.grid(row=0, column=3, padx=0,      pady=0, sticky='W')
        # }
        self.btn_stop.grid(row=4, columnspan=2, padx=6, pady=6)

        self.tip_btn_show_entry = ttip.Hovertip(self.btn_show_entry, 'Посмотреть само слово и его перевод\n'
                                                                     'Control-W',
                                                hover_delay=700)
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
        elif self.learn_method == LEARN_VALUES_METHOD[2]:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите фразу', hover_delay=1000)
        elif self.learn_method == LEARN_VALUES_METHOD[3]:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите перевод', hover_delay=1000)
        else:
            self.tip_entry = ttip.Hovertip(self.entry_input, 'Введите артикль', hover_delay=1000)

        self.choose()

        if self.current_key:
            entry = _0_global_dct.d[self.current_key]
            if entry.count_n == 0 or self.learn_method in LEARN_VALUES_METHOD[2:4]:
                btn_disable(self.btn_show_notes)
            if not self.homonyms or self.learn_method in LEARN_VALUES_METHOD[2:4]:
                btn_disable(self.btn_show_homonyms)
            if self.learn_method not in LEARN_VALUES_METHOD[2:4]:
                btn_disable(self.btn_show_entry)

    # Печать в журнал
    def outp(self, msg='', end='\n'):
        self.txt_dct['state'] = 'normal'
        self.txt_dct.insert(tk.END, f'{msg}{end}')
        self.txt_dct.yview_moveto(1.0)
        self.txt_dct['state'] = 'disabled'

    # Получить глобальный процент угадываний
    def get_percent(self):
        num, den = _0_global_dct.count_rating()
        if den == 0:
            percent = 0
        else:
            percent = num / den * 100
        percent = format(percent, '.1f')
        return f'{num} / {den} = {percent}%'

    # Формируем пул слов, которые будут использоваться при учёбе
    def create_pool(self):
        if self.learn_method == LEARN_VALUES_METHOD[4]:  # Если надо, оставляем только слова с der/die/das
            all_keys = []
            for key in _0_global_dct.d.keys():
                wrd = _0_global_dct.d[key].wrd
                if len(wrd) > 4 and wrd[0:4].lower() in ('der ', 'die ', 'das '):
                    all_keys += [key]
        else:
            all_keys = list(_0_global_dct.d.keys())
        # Если надо, оставляем только слова из нужной группы
        if self.group != ALL_GROUPS:
            all_keys = [key for key in all_keys if self.group in _0_global_dct.d[key].groups]
        # Если надо, оставляем только слова, у которых есть словоформы
        if self.forms == LEARN_VALUES_FORMS[2]:
            all_keys = [key for key in all_keys if _0_global_dct.d[key].count_f != 0]

        if self.words == LEARN_VALUES_WORDS[0]:  # Учить все слова
            selected_keys = all_keys
        elif self.words == LEARN_VALUES_WORDS[1]:  # Учить преимущественно избранные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].fav]

            # Помимо всех избранных слов (пусть их количество N) добавим N // 4 остальных слов
            # Выберем их из самых давно не отвечаемых слов

            # Отбираем слова, не являющиеся избранными
            unfav_keys = [k for k in all_keys if not _0_global_dct.d[k].fav]
            # Сортируем по давности ответа
            unfav_keys.sort(key=lambda k: _0_global_dct.d[k].latest_answer_date)
            # Находим N // 4
            count_unfav_keys = min(len(unfav_keys), _0_global_dct.count_fav_entries()[0] // 4)
            # Находим S - номер самой недавней сессии среди N // 4 самых старых слов
            latest_date = _0_global_dct.d[unfav_keys[count_unfav_keys - 1]].latest_answer_date
            # Оставляем только слова с номером сессии <= S
            unfav_keys = [k for k in unfav_keys if _0_global_dct.d[k].latest_answer_date[0:2] <= latest_date[0:2]]
            # Перемешиваем их
            random.shuffle(unfav_keys)
            # И выбираем из них N // 4 слов
            for i in range(count_unfav_keys):
                selected_keys += [unfav_keys[i]]
        elif self.words == LEARN_VALUES_WORDS[2]:  # Учить только избранные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].fav]
        elif self.words == LEARN_VALUES_WORDS[3]:  # Учить только неотвеченные слова
            selected_keys = [key for key in all_keys if _0_global_dct.d[key].correct_att == 0]
        elif self.words == LEARN_VALUES_WORDS[4]:  # Учить 10 случайных слов
            selected_keys = random.sample(all_keys, min(len(all_keys), 10))
        else:  # Учить 10 случайных избранных слов
            all_keys = [key for key in all_keys if _0_global_dct.d[key].fav]
            selected_keys = random.sample(all_keys, min(len(all_keys), 10))

        selected_forms = []
        if self.forms == LEARN_VALUES_FORMS[0]:
            for key in selected_keys:
                selected_forms += [(key, None)]
        elif self.forms == LEARN_VALUES_FORMS[1]:
            for key in selected_keys:
                forms = tuple([None]) + tuple(_0_global_dct.d[key].forms.keys())
                selected_forms += [(key, random.choice(forms))]
        elif self.forms == LEARN_VALUES_FORMS[2]:
            for key in selected_keys:
                for frm in _0_global_dct.d[key].forms.keys():
                    selected_forms += [(key, frm)]
        else:
            for key in selected_keys:
                selected_forms += [(key, None)]
                for frm in _0_global_dct.d[key].forms.keys():
                    selected_forms += [(key, frm)]

        selected_phrases = []
        if self.learn_method in LEARN_VALUES_METHOD[2:4]:
            for (key, frm) in selected_forms:
                for phr in _0_global_dct.d[key].phrases.keys():
                    selected_phrases += [(key, frm, phr)]
        else:
            for (key, frm) in selected_forms:
                selected_phrases += [(key, frm, None)]

        self.pool = set(selected_phrases)

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
            self.current_key, self.current_form, self.current_phrase = random.choice(tuple(self.pool))
        else:
            self.current_key, self.current_form, self.current_phrase = random_smart(_0_global_dct, self.pool)

        # Вывод слова в журнал
        if self.learn_method == LEARN_VALUES_METHOD[0]:
            if self.forms and self.current_form:
                self.outp(get_tr_and_frm_with_stat(_0_global_dct.d[self.current_key], self.current_form))
            else:
                self.outp(get_tr_with_stat(_0_global_dct.d[self.current_key]))
        elif self.learn_method == LEARN_VALUES_METHOD[1]:
            self.outp(get_wrd_with_stat(_0_global_dct.d[self.current_key]))
        elif self.learn_method == LEARN_VALUES_METHOD[2]:
            self.outp(get_phr_tr_with_stat(_0_global_dct.d[self.current_key], self.current_phrase))
        elif self.learn_method == LEARN_VALUES_METHOD[3]:
            self.outp(get_phr_with_stat(_0_global_dct.d[self.current_key], self.current_phrase))
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
        elif self.learn_method == LEARN_VALUES_METHOD[4]:
            ans = _0_global_dct.d[self.current_key].wrd
            self.homonyms = []
            for key in _0_global_dct.d.keys():
                if key != self.current_key:
                    wrd = _0_global_dct.d[key].wrd
                    if len(wrd) > 4 and wrd[0:4].lower() in ('der ', 'die ', 'das ') and wrd[4:] == ans[4:]:
                        self.homonyms += [key]

    # Нажатие на кнопку "Ввод"
    # Ввод ответа и переход к следующему слову
    def input(self):
        # Вывод в журнал пользовательского ответа
        answer = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations)
        if answer != '':
            self.outp(answer)

        # Проверка пользовательского ответа
        if self.learn_method == LEARN_VALUES_METHOD[1]:
            self.check_tr()
        elif self.learn_method == LEARN_VALUES_METHOD[2]:
            self.check_phrase()
        elif self.learn_method == LEARN_VALUES_METHOD[3]:
            self.check_phrase_tr()
        elif self.learn_method == LEARN_VALUES_METHOD[4]:
            self.check_article()
        elif self.forms and self.current_form:
            self.check_form()
        else:
            self.check_wrd()

        # Выбор нового слова для угадывания
        self.choose()

        # Обновление кнопки "Посмотреть слово и перевод"
        if self.learn_method in LEARN_VALUES_METHOD[2:4]:
            btn_enable(self.btn_show_entry, self.show_entry)
        # Обновление кнопки "Посмотреть сноски"
        entry = _0_global_dct.d[self.current_key]
        if entry.count_n == 0 or self.learn_method in LEARN_VALUES_METHOD[2:4]:
            btn_disable(self.btn_show_notes)
        else:
            btn_enable(self.btn_show_notes, self.show_notes)
        # Обновление кнопки "Посмотреть омонимы"
        if not self.homonyms or self.learn_method in LEARN_VALUES_METHOD[2:4]:
            btn_disable(self.btn_show_homonyms)
        else:
            btn_enable(self.btn_show_homonyms, self.show_homonyms)
        # Очистка поля ввода
        self.entry_input.delete(0, tk.END)
        # Обновление отображаемого рейтинга
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {self.get_percent()}'
        self.lbl_count['text'] = f'Отвечено: {self.count_correct}/{self.len_of_pool}'

    # Нажатие на кнопку "Посмотреть слово и перевод"
    # Просмотр слова с переводом
    def show_entry(self):
        entry = _0_global_dct.d[self.current_key]
        self.outp(f'Слово: {entry.wrd}\n'
                  f'Перевод: {get_tr(entry)}')
        btn_disable(self.btn_show_entry)

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
        self.outp('Омонимы:')
        for key in self.homonyms:
            self.outp('> ' + _0_global_dct.d[key].wrd + ': ' + get_tr(_0_global_dct.d[key]))
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
    def check_answer(self, correct_answer: str, is_correct: bool, current_key: DctKey):
        entry = _0_global_dct.d[current_key]
        if is_correct:
            entry.correct((_0_global_session_number, _0_global_learn_session_number, self.count_all))
            self.outp('Верно\n')
            if entry.fav:
                window = PopupDialogueW(self, 'Верно.\n'
                                              'Оставить слово в избранном?',
                                        'Да', 'Нет', val_on_close=True)
                ttip.Hovertip(window.btn_right, 'Alt+N', hover_delay=700)
                window.bind('<Alt-KeyPress>', lambda key: bind_keypress(key, [('N', window.btn_right.invoke)]))
                answer = window.open()
                if not answer:
                    entry.fav = False
            self.count_all += 1
            self.count_correct += 1
            self.pool.remove((current_key, self.current_form, self.current_phrase))
        else:
            self.outp(f'Неверно. Правильный ответ: "{correct_answer}"\n')
            if entry.fav:
                if bool(_0_global_with_typo):
                    window = PopupDialogueW(self,
                                            msg=f'Неверно.\n'
                                                f'Ваш ответ: {encode_special_combinations(self.entry_input.get(), _0_global_special_combinations)}\n'
                                                f'Правильный ответ: {correct_answer}',
                                            btn_left_text='Ясно', btn_right_text='Просто опечатка',
                                            st_left='Default', st_right='Default',
                                            val_left='ok', val_right='typo')
                    ttip.Hovertip(window.btn_right, 'Не засчитывать ошибку\n'
                                                    'Tab',
                                  hover_delay=700)
                    window.bind('<Tab>', lambda event: window.btn_right.invoke())
                    answer = window.open()
                    if answer != 'typo':
                        entry.incorrect((_0_global_session_number, _0_global_learn_session_number, self.count_all))
                        self.count_all += 1
                else:
                    entry.incorrect((_0_global_session_number, _0_global_learn_session_number, self.count_all))
                    self.count_all += 1
            else:
                window = IncorrectAnswerW(self, encode_special_combinations(self.entry_input.get(),
                                                                            _0_global_special_combinations),
                                          correct_answer, bool(_0_global_with_typo))
                answer = window.open()
                if answer != 'typo':
                    entry.incorrect((_0_global_session_number, _0_global_learn_session_number, self.count_all))
                    self.count_all += 1
                if answer == 'yes':
                    entry.fav = True

    # Проверка введённого слова
    def check_wrd(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(),
                                                     _0_global_special_combinations) == entry.wrd
        else:
            is_correct = encode_special_combinations(self.entry_input.get(),
                                                     _0_global_special_combinations).lower() == entry.wrd.lower()
        self.check_answer(entry.wrd, is_correct, self.current_key)

    # Проверка введённой словоформы
    def check_form(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations) ==\
                         entry.forms[self.current_form]
        else:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations).lower() ==\
                         entry.forms[self.current_form].lower()
        self.check_answer(entry.forms[self.current_form], is_correct, self.current_key)

    # Проверка введённого перевода слова
    def check_tr(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations) in entry.tr
        else:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations).lower() in\
                         (tr.lower() for tr in entry.tr)
        self.check_answer(frm_key_to_str_for_print(entry.tr), is_correct, self.current_key)

    # Проверка введённой фразы
    def check_phrase(self):
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations) ==\
                         self.current_phrase
        else:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations).lower() ==\
                         self.current_phrase.lower()
        self.check_answer(self.current_phrase, is_correct, self.current_key)

    # Проверка введённого перевода фразы
    def check_phrase_tr(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations) in\
                         entry.phrases[self.current_phrase]
        else:
            is_correct = encode_special_combinations(self.entry_input.get(), _0_global_special_combinations).lower() in\
                         (pt.lower() for pt in entry.phrases[self.current_phrase])
        self.check_answer(get_phr_tr(entry, self.current_phrase), is_correct, self.current_key)

    # Проверка введённого артикля
    def check_article(self):
        entry = _0_global_dct.d[self.current_key]
        if _0_global_check_register:
            is_correct = encode_special_combinations(self.entry_input.get(),
                                                     _0_global_special_combinations) == entry.wrd[0:3]
        else:
            is_correct = encode_special_combinations(self.entry_input.get(),
                                                     _0_global_special_combinations).lower() == entry.wrd[0:3].lower()
        self.check_answer(entry.wrd[0:3], is_correct, self.current_key)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_input.focus_set()

        bind_ctrl_acvx(self.entry_input)
        self.bind('<Return>', lambda event: self.btn_input.invoke())
        self.bind('<Control-KeyPress>', lambda key: bind_keypress(key, [('N', lambda: self.btn_show_notes.invoke()),
                                                                        ('O', lambda: self.btn_show_homonyms.invoke()),
                                                                        ('W', lambda: self.btn_show_entry.invoke())]))

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
        self.title(f'{PROGRAM_NAME} - Словарь "{_0_global_dct_savename}"')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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

        self.group_vals = [ALL_GROUPS] + _0_global_dct.groups

        # Параметры поиска
        self.search_only_fav = bool(_0_global_search_settings[0])
        self.search_only_full = bool(_0_global_search_settings[1])
        self.search_wrd = bool(_0_global_search_settings[2])
        self.search_tr = bool(_0_global_search_settings[3])
        self.search_frm = bool(_0_global_search_settings[4])
        self.search_phr = bool(_0_global_search_settings[5])
        self.search_nt = bool(_0_global_search_settings[6])
        self.search_group = self.group_vals[_0_global_search_settings[7]]

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

        def print_validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.print_count_pages)
            if res and value != '' and int(value) != self.print_current_page:
                self.print_go_to_page_with_number(int(value))
            return res
        self.vcmd_print_page = (self.register(print_validate_and_goto_page_number), '%P')

        def validate_and_goto_page_number(value: str):
            res = validate_int_min_max(value, 1, self.search_count_pages)
            if res and value != '' and int(value) != self.search_current_page:
                self.search_go_to_page_with_number(int(value))
            return res
        self.vcmd_page = (self.register(validate_and_goto_page_number), '%P')

        self.tabs = ttk.Notebook(self, style='Default.TNotebook')
        self.tab_print = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.tabs.add(self.tab_print, text='Просмотр словаря')
        # {
        self.frame_print_menu = ttk.Frame(self.tab_print, style='Invis.TFrame')
        # { {
        self.frame_print_header = ttk.Frame(self.frame_print_menu, style='Invis.TFrame')
        # { { {
        self.btn_print_about_window = ttk.Button(self.frame_print_header, command=self.about_window, width=2,
                                                 takefocus=False)
        set_image(self.btn_print_about_window, self.img_about, img_about, '?')
        self.btn_print_print_out = ttk.Button(self.frame_print_header, command=self.print_out, takefocus=False)
        set_image(self.btn_print_print_out, self.img_print_out, img_print_out, 'Распечатать')
        self.frame_print_parameters = ttk.Frame(self.frame_print_header, style='Default.TFrame')
        # { { { {
        self.lbl_print_fav = ttk.Label(self.frame_print_parameters, text='Только избр.:', style='Default.TLabel')
        self.check_print_fav = ttk.Checkbutton(self.frame_print_parameters, variable=self.var_print_fav,
                                               command=lambda: self.print_go_to_first_page(True),
                                               style='Default.TCheckbutton')
        self.lbl_print_group = ttk.Label(self.frame_print_parameters, text='Группа:', style='Default.TLabel')
        self.combo_print_group = ttk.Combobox(self.frame_print_parameters, textvariable=self.var_print_group,
                                              values=[ALL_GROUPS] + _0_global_dct.groups, width=28, state='readonly',
                                              style='Default.TCombobox', font=('DejaVu Sans Mono', _0_global_scale))
        self.lbl_print_briefly = ttk.Label(self.frame_print_parameters, text='Кратко:', style='Default.TLabel')
        self.check_print_briefly = ttk.Checkbutton(self.frame_print_parameters, variable=self.var_print_briefly,
                                                   command=lambda: self.print_print(True), style='Default.TCheckbutton')
        self.lbl_print_order = ttk.Label(self.frame_print_parameters, text='Порядок:', style='Default.TLabel')
        self.combo_print_order = ttk.Combobox(self.frame_print_parameters, textvariable=self.var_print_order, width=28,
                                              values=PRINT_VALUES_ORDER, state='readonly', style='Default.TCombobox',
                                              font=('DejaVu Sans Mono', _0_global_scale))
        # } } } }
        # } } }
        self.frame_print_buttons_for_selected = ttk.Frame(self.frame_print_menu, style='Default.TFrame')
        # { { {
        self.btn_print_fav = ttk.Button(self.frame_print_buttons_for_selected,
                                        command=lambda: self.fav_selected(self.print_selected_keys), width=3,
                                        takefocus=False)
        set_image(self.btn_print_fav, self.img_fav, img_fav, '*+')
        self.btn_print_unfav = ttk.Button(self.frame_print_buttons_for_selected,
                                          command=lambda: self.unfav_selected(self.print_selected_keys), width=3,
                                          takefocus=False)
        set_image(self.btn_print_unfav, self.img_unfav, img_unfav, '*-')
        self.btn_print_add_to_group = ttk.Button(self.frame_print_buttons_for_selected,
                                                 command=lambda: self.add_selected_to_group(self.print_selected_keys),
                                                 width=3, takefocus=False)
        set_image(self.btn_print_add_to_group, self.img_add_to_group, img_add_to_group, 'G+')
        self.btn_print_remove_from_group = ttk.Button(self.frame_print_buttons_for_selected,
                                                      command=lambda:
                                                      self.remove_selected_from_group(self.print_selected_keys),
                                                      width=3, takefocus=False)
        set_image(self.btn_print_remove_from_group, self.img_remove_from_group, img_remove_from_group, 'G-')
        self.btn_print_delete = ttk.Button(self.frame_print_buttons_for_selected,
                                           command=lambda: self.delete_selected(self.print_selected_keys), width=3,
                                           takefocus=False)
        set_image(self.btn_print_delete, self.img_delete, img_trashcan, 'DEL')
        # } } }
        self.frame_print_selection_buttons = ttk.Frame(self.frame_print_menu, style='Default.TFrame')
        # { { {
        self.btn_print_select_page = ttk.Button(self.frame_print_selection_buttons, command=self.print_select_page,
                                                width=3, takefocus=False)
        set_image(self.btn_print_select_page, self.img_select_page, img_select_page, '[X]')
        self.btn_print_unselect_page = ttk.Button(self.frame_print_selection_buttons, command=self.print_unselect_page,
                                                  width=3, takefocus=False)
        set_image(self.btn_print_unselect_page, self.img_unselect_page, img_unselect_page, '[ ]')
        self.btn_print_select_all = ttk.Button(self.frame_print_selection_buttons, command=self.print_select_all,
                                               width=3, takefocus=False)
        set_image(self.btn_print_select_all, self.img_select_all, img_select_all, '[X]')
        self.btn_print_unselect_all = ttk.Button(self.frame_print_selection_buttons, command=self.print_unselect_all,
                                                 width=3, takefocus=False)
        set_image(self.btn_print_unselect_all, self.img_unselect_all, img_unselect_all, '[ ]')
        # } } }
        self.lbl_print_info = ttk.Label(self.frame_print_menu, textvariable=self.var_print_info, style='Default.TLabel')
        self.lbl_print_info_selected = ttk.Label(self.frame_print_menu, textvariable=self.var_print_info_selected,
                                                 justify='left', style='Default.TLabel')
        # } }
        self.frame_print_main = ttk.Frame(self.tab_print, style='Invis.TFrame')
        # { {
        self.scrolled_frame_print = ScrollFrame(self.frame_print_main,
                                                SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                                SCALE_DEFAULT_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.frame_print_page_buttons = ttk.Frame(self.frame_print_main, style='Invis.TFrame')
        # { { {
        self.btn_print_first_page = ttk.Button(self.frame_print_page_buttons, command=self.print_go_to_first_page,
                                               width=2, takefocus=False)
        set_image(self.btn_print_first_page, self.img_double_arrow_left, img_double_arrow_left, '<<')
        self.btn_print_prev_page = ttk.Button(self.frame_print_page_buttons, command=self.print_go_to_prev_page,
                                              width=2, takefocus=False)
        set_image(self.btn_print_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self.frame_print_current_page = ttk.Frame(self.frame_print_page_buttons, style='Invis.TFrame')
        # { { { {
        self.lbl_print_current_page_1 = ttk.Label(self.frame_print_current_page, text='Страница',
                                                  style='Default.TLabel')
        self.entry_print_current_page = ttk.Entry(self.frame_print_current_page,
                                                  textvariable=self.var_print_current_page,
                                                  validate='key', validatecommand=self.vcmd_print_page,
                                                  justify='center', width=3,
                                                  style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_print_current_page_2 = ttk.Label(self.frame_print_current_page, text='из 1', style='Default.TLabel')
        # } } } }
        self.btn_print_next_page = ttk.Button(self.frame_print_page_buttons, command=self.print_go_to_next_page,
                                              width=2, takefocus=False)
        set_image(self.btn_print_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_print_last_page = ttk.Button(self.frame_print_page_buttons, command=self.print_go_to_last_page,
                                              width=2, takefocus=False)
        set_image(self.btn_print_last_page, self.img_double_arrow_right, img_double_arrow_right, '>>')
        # } } }
        # } }
        # }

        self.tab_search = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.tabs.add(self.tab_search, text='Поиск')
        # {
        self.frame_search_header = ttk.Frame(self.tab_search, style='Invis.TFrame')
        # { {
        self.frame_search_query = ttk.Frame(self.frame_search_header, style='Default.TFrame')
        # { { {
        self.btn_search_search_settings = ttk.Button(self.frame_search_query, command=self.search_settings, width=9,
                                                     takefocus=False)
        set_image(self.btn_search_search_settings, self.img_settings, img_edit, 'Настройки')
        self.entry_search_query = ttk.Entry(self.frame_search_query, textvariable=self.var_search_query, width=50,
                                            style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.btn_search_search = ttk.Button(self.frame_search_query, text='Поиск',
                                            command=lambda: self.search_go_to_first_page(True),
                                            width=6, takefocus=False, style='Default.TButton')
        # } } }
        self.frame_search_selection_buttons = ttk.Frame(self.frame_search_header, style='Default.TFrame')
        # { { {
        self.btn_search_select_page = ttk.Button(self.frame_search_selection_buttons, command=self.search_select_page,
                                                 width=3, takefocus=False)
        set_image(self.btn_search_select_page, self.img_select_page, img_select_page, '[X]')
        self.btn_search_unselect_page = ttk.Button(self.frame_search_selection_buttons,
                                                   command=self.search_unselect_page, width=3, takefocus=False)
        set_image(self.btn_search_unselect_page, self.img_unselect_page, img_unselect_page, '[ ]')
        self.btn_search_select_all = ttk.Button(self.frame_search_selection_buttons, command=self.search_select_all,
                                                width=3, takefocus=False)
        set_image(self.btn_search_select_all, self.img_select_all, img_select_all, '[X]')
        self.btn_search_unselect_all = ttk.Button(self.frame_search_selection_buttons, command=self.search_unselect_all,
                                                  width=3, takefocus=False)
        set_image(self.btn_search_unselect_all, self.img_unselect_all, img_unselect_all, '[ ]')
        # } } }
        self.frame_search_info = ttk.Frame(self.frame_search_header, style='Invis.TFrame')
        # { { {
        self.btn_search_about_window = ttk.Button(self.frame_search_info, command=self.about_window, width=2,
                                                  takefocus=False)
        set_image(self.btn_search_about_window, self.img_about, img_about, '?')
        self.lbl_search_info = ttk.Label(self.frame_search_info, textvariable=self.var_search_info,
                                         style='Default.TLabel')
        # } } }
        self.lbl_search_info_selected = ttk.Label(self.frame_search_header, textvariable=self.var_search_info_selected,
                                                  style='Default.TLabel')
        self.frame_search_buttons_for_selected = ttk.Frame(self.frame_search_header, style='Default.TFrame')
        # { { {
        self.btn_search_fav = ttk.Button(self.frame_search_buttons_for_selected,
                                         command=lambda: self.fav_selected(self.search_selected_keys),
                                         width=3, takefocus=False)
        set_image(self.btn_search_fav, self.img_fav, img_fav, '*+')
        self.btn_search_unfav = ttk.Button(self.frame_search_buttons_for_selected,
                                           command=lambda: self.unfav_selected(self.search_selected_keys),
                                           width=3, takefocus=False)
        set_image(self.btn_search_unfav, self.img_unfav, img_unfav, '*-')
        self.btn_search_add_to_group = ttk.Button(self.frame_search_buttons_for_selected,
                                                  command=lambda: self.add_selected_to_group(self.search_selected_keys),
                                                  width=3, takefocus=False)
        set_image(self.btn_search_add_to_group, self.img_add_to_group, img_add_to_group, 'G+')
        self.btn_search_remove_from_group = ttk.Button(self.frame_search_buttons_for_selected,
                                                       command=lambda:
                                                       self.remove_selected_from_group(self.search_selected_keys),
                                                       width=3, takefocus=False)
        set_image(self.btn_search_remove_from_group, self.img_remove_from_group, img_remove_from_group, 'G-')
        self.btn_search_delete = ttk.Button(self.frame_search_buttons_for_selected,
                                            command=lambda: self.delete_selected(self.search_selected_keys),
                                            width=3, takefocus=False)
        set_image(self.btn_search_delete, self.img_delete, img_trashcan, 'DEL')
        # } } }
        # } }
        self.frame_search_main = ttk.Frame(self.tab_search, style='Invis.TFrame')
        # { {
        self.scrolled_frame_search = ScrollFrame(self.frame_search_main,
                                                 SCALE_DEFAULT_FRAME_HEIGHT[_0_global_scale - SCALE_MIN],
                                                 SCALE_DEFAULT_FRAME_WIDTH[_0_global_scale - SCALE_MIN])
        self.frame_search_page_buttons = ttk.Frame(self.frame_search_main, style='Invis.TFrame')
        # { { {
        self.btn_search_first_page = ttk.Button(self.frame_search_page_buttons, command=self.search_go_to_first_page,
                                                width=2, takefocus=False)
        set_image(self.btn_search_first_page, self.img_double_arrow_left, img_double_arrow_left, '<<')
        self.btn_search_prev_page = ttk.Button(self.frame_search_page_buttons, command=self.search_go_to_prev_page,
                                               width=2, takefocus=False)
        set_image(self.btn_search_prev_page, self.img_arrow_left, img_arrow_left, '<')
        self.frame_search_current_page = ttk.Frame(self.frame_search_page_buttons, style='Invis.TFrame')
        # { { { {
        self.lbl_search_current_page_1 = ttk.Label(self.frame_search_current_page, text='Страница',
                                                   style='Default.TLabel')
        self.entry_search_current_page = ttk.Entry(self.frame_search_current_page,
                                                   textvariable=self.var_search_current_page, justify='center',
                                                   validate='key', validatecommand=self.vcmd_page, width=3,
                                                   style='Default.TEntry', font=('StdFont', _0_global_scale))
        self.lbl_search_current_page_2 = ttk.Label(self.frame_search_current_page, text='из 1', style='Default.TLabel')
        # } } } }
        self.btn_search_next_page = ttk.Button(self.frame_search_page_buttons, command=self.search_go_to_next_page,
                                               width=2, takefocus=False)
        set_image(self.btn_search_next_page, self.img_arrow_right, img_arrow_right, '>')
        self.btn_search_last_page = ttk.Button(self.frame_search_page_buttons, command=self.search_go_to_last_page,
                                               width=2, takefocus=False)
        set_image(self.btn_search_last_page, self.img_double_arrow_right, img_double_arrow_right, '>>')
        # } } }
        # } }
        # }

        self.tab_add = ttk.Frame(self.tabs, style='Invis.TFrame')
        self.tabs.add(self.tab_add, text='Добавить запись в словарь')

        self.tabs.grid(row=0, column=0, padx=0, pady=0)
        # {
        self.frame_print_menu.grid(row=0, column=0, padx=6, pady=(6, 0), sticky='W')
        # { {
        self.frame_print_header.grid(row=0, rowspan=2, column=0, padx=0, pady=0)
        # { { {
        self.btn_print_about_window.grid(row=0,            column=0, padx=0,      pady=0)
        self.btn_print_print_out.grid(   row=1,            column=0, padx=0,      pady=0)
        self.frame_print_parameters.grid(row=0, rowspan=2, column=1, padx=(6, 0), pady=0)
        # { { { {
        self.lbl_print_fav.grid(      row=0, column=0, padx=(6, 1), pady=6,      sticky='E')
        self.check_print_fav.grid(    row=0, column=1, padx=(0, 6), pady=6,      sticky='W')
        self.lbl_print_group.grid(    row=0, column=2, padx=(0, 1), pady=6,      sticky='E')
        self.combo_print_group.grid(  row=0, column=3, padx=(0, 6), pady=6,      sticky='W')
        self.lbl_print_briefly.grid(  row=1, column=0, padx=(6, 1), pady=(0, 6), sticky='E')
        self.check_print_briefly.grid(row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='W')
        self.lbl_print_order.grid(    row=1, column=2, padx=(0, 1), pady=(0, 6), sticky='E')
        self.combo_print_order.grid(  row=1, column=3, padx=(0, 6), pady=(0, 6), sticky='W')
        # } } } }
        # } } }
        # self.frame_print_buttons_for_selected
        # { { {
        self.btn_print_fav.grid(              row=0, column=0)
        self.btn_print_unfav.grid(            row=0, column=1)
        self.btn_print_add_to_group.grid(     row=0, column=2)
        self.btn_print_remove_from_group.grid(row=0, column=3)
        self.btn_print_delete.grid(           row=0, column=4)
        # } } }
        self.frame_print_selection_buttons.grid(row=1, column=1, padx=(6, 0), pady=0, sticky='WS')
        # { { {
        self.btn_print_select_page.grid(  row=0, column=0)
        self.btn_print_unselect_page.grid(row=0, column=1)
        self.btn_print_select_all.grid(   row=0, column=2)
        self.btn_print_unselect_all.grid( row=0, column=3)
        # } } }
        self.lbl_print_info.grid(         row=2, column=0, padx=0,      pady=0)
        self.lbl_print_info_selected.grid(row=2, column=1, padx=(6, 0), pady=0, sticky='W')
        # } }
        self.frame_print_main.grid(row=1, column=0, padx=6, pady=6)
        # { {
        self.scrolled_frame_print.grid(    row=0, column=0, padx=0, pady=(0, 6))
        self.frame_print_page_buttons.grid(row=1, column=0, padx=0, pady=0)
        # { { {
        self.btn_print_first_page.grid(    row=0, column=0, padx=3, pady=0)
        self.btn_print_prev_page.grid(     row=0, column=1, padx=3, pady=0)
        self.frame_print_current_page.grid(row=0, column=2, padx=3, pady=0)
        # { { { {
        self.lbl_print_current_page_1.grid(row=0, column=0, padx=0, pady=0)
        self.entry_print_current_page.grid(row=0, column=1, padx=3, pady=0)
        self.lbl_print_current_page_2.grid(row=0, column=2, padx=0, pady=0)
        # } } } }
        self.btn_print_next_page.grid(row=0, column=3, padx=3, pady=0)
        self.btn_print_last_page.grid(row=0, column=4, padx=3, pady=0)
        # } } }
        # } }
        # }

        # {
        self.frame_search_header.grid(row=0, column=0, padx=6, pady=(6, 0), sticky='W')
        # { {
        self.frame_search_query.grid(row=0, column=0, columnspan=2, padx=0, pady=(0, 6))
        # { { {
        self.btn_search_search_settings.grid(row=0, column=0, padx=(6, 3), pady=6)
        self.entry_search_query.grid(        row=0, column=1, padx=(0, 1), pady=6)
        self.btn_search_search.grid(         row=0, column=2, padx=(0, 6), pady=6)
        # } } }
        self.frame_search_selection_buttons.grid(row=0, column=2, padx=(6, 0), pady=(0, 6), sticky='WS')
        # { { {
        self.btn_search_select_page.grid(  row=0, column=0)
        self.btn_search_unselect_page.grid(row=0, column=1)
        self.btn_search_select_all.grid(   row=0, column=2)
        self.btn_search_unselect_all.grid( row=0, column=3)
        # } } }
        self.frame_search_info.grid(row=1, column=0, padx=(6, 0), pady=0, sticky='W')
        # { { {
        self.btn_search_about_window.grid(row=0, column=0, padx=0, pady=0)
        self.lbl_search_info.grid(        row=0, column=1, padx=0, pady=0)
        # } } }
        self.lbl_search_info_selected.grid(row=1, column=1, padx=0, pady=0, sticky='E')
        # self.frame_search_buttons_for_selected
        # { { {
        self.btn_search_fav.grid(              row=0, column=0)
        self.btn_search_unfav.grid(            row=0, column=1)
        self.btn_search_add_to_group.grid(     row=0, column=2)
        self.btn_search_remove_from_group.grid(row=0, column=3)
        self.btn_search_delete.grid(           row=0, column=4)
        # } } }
        # } }
        self.frame_search_main.grid(row=1, column=0, padx=6, pady=6)
        # { {
        self.scrolled_frame_search.grid(    row=0, column=0, padx=0, pady=(0, 6))
        self.frame_search_page_buttons.grid(row=1, column=0, padx=0, pady=0)
        # { { {
        self.btn_search_first_page.grid(    row=0, column=0, padx=3, pady=0)
        self.btn_search_prev_page.grid(     row=0, column=1, padx=3, pady=0)
        self.frame_search_current_page.grid(row=0, column=2, padx=3, pady=0)
        # { { { {
        self.lbl_search_current_page_1.grid(row=0, column=0, padx=0, pady=0)
        self.entry_search_current_page.grid(row=0, column=1, padx=3, pady=0)
        self.lbl_search_current_page_2.grid(row=0, column=2, padx=0, pady=0)
        # } } } }
        self.btn_search_next_page.grid(row=0, column=3, padx=3, pady=0)
        self.btn_search_last_page.grid(row=0, column=4, padx=3, pady=0)
        # } } }
        # } }
        # }

        self.tip_btn_about_window = ttip.Hovertip(self.btn_print_about_window, 'Справка', hover_delay=450)
        self.tip_btn_print_out = ttip.Hovertip(self.btn_print_print_out, 'Распечатать словарь в файл', hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(self.btn_print_fav, 'Добавить выделенные статьи в избранное\n'
                                                       'Alt+F',
                                         hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(self.btn_print_unfav, 'Убрать выделенные статьи из избранного\n'
                                                           'Alt+Shift+F',
                                           hover_delay=450)
        self.tip_btn_add_to_group = ttip.Hovertip(self.btn_print_add_to_group, 'Добавить выделенные статьи в группу\n'
                                                                         'Alt+G',
                                                  hover_delay=450)
        self.tip_btn_remove_from_group = ttip.Hovertip(self.btn_print_remove_from_group,
                                                       'Убрать выделенные статьи из группы\n'
                                                       'Alt+Shift+G',
                                                       hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(self.btn_print_delete, 'Удалить выделенные статьи\n'
                                                             'Alt+D',
                                            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(self.btn_print_select_page, 'Выделить все статьи на текущей странице\n'
                                                                       'Alt+P',
                                                 hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(self.btn_print_unselect_page,
                                                   'Снять выделение со всех статей на текущей странице\n'
                                                   'Alt+Shift+P',
                                                   hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(self.btn_print_select_all, 'Выделить все статьи\n'
                                                                     'Alt+A',
                                                hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(self.btn_print_unselect_all, 'Снять выделение со всех статей\n'
                                                                         'Alt+Shift+A',
                                                  hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(self.btn_print_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(self.btn_print_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(self.btn_print_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(self.btn_print_last_page, 'В конец', hover_delay=650)
        #
        self.tip_btn_about_window = ttip.Hovertip(self.btn_search_about_window, 'Справка', hover_delay=450)
        self.tip_btn_search_settings = ttip.Hovertip(self.btn_search_search_settings, 'Параметры поиска',
                                                     hover_delay=450)
        self.tip_btn_fav = ttip.Hovertip(self.btn_search_fav, 'Добавить выделенные статьи в избранное\n'
                                                       'Alt+F',
                                         hover_delay=450)
        self.tip_btn_unfav = ttip.Hovertip(self.btn_search_unfav, 'Убрать выделенные статьи из избранного\n'
                                                           'Alt+Shift+F',
                                           hover_delay=450)
        self.tip_btn_add_to_group = ttip.Hovertip(self.btn_search_add_to_group, 'Добавить выделенные статьи в группу\n'
                                                                         'Alt+G',
                                                  hover_delay=450)
        self.tip_btn_remove_from_group = ttip.Hovertip(self.btn_search_remove_from_group,
                                                       'Убрать выделенные статьи из группы\n'
                                                       'Alt+Shift+G',
                                                       hover_delay=450)
        self.tip_btn_delete = ttip.Hovertip(self.btn_search_delete, 'Удалить выделенные статьи\n'
                                                             'Alt+D',
                                            hover_delay=450)
        self.tip_btn_select_page = ttip.Hovertip(self.btn_search_select_page, 'Выделить все статьи на текущей странице\n'
                                                                       'Alt+P',
                                                 hover_delay=450)
        self.tip_btn_unselect_page = ttip.Hovertip(self.btn_search_unselect_page,
                                                   'Снять выделение со всех статей на текущей странице\n'
                                                   'Alt+Shift+P',
                                                   hover_delay=450)
        self.tip_btn_select_all = ttip.Hovertip(self.btn_search_select_all, 'Выделить все статьи\n'
                                                                     'Alt+A',
                                                hover_delay=450)
        self.tip_btn_unselect_all = ttip.Hovertip(self.btn_search_unselect_all, 'Снять выделение со всех статей\n'
                                                                         'Alt+Shift+A',
                                                  hover_delay=450)
        self.tip_btn_first_page = ttip.Hovertip(self.btn_search_first_page, 'В начало', hover_delay=650)
        self.tip_btn_prev_page = ttip.Hovertip(self.btn_search_prev_page, 'На предыдущую страницу', hover_delay=650)
        self.tip_btn_next_page = ttip.Hovertip(self.btn_search_next_page, 'На следующую страницу', hover_delay=650)
        self.tip_btn_last_page = ttip.Hovertip(self.btn_search_last_page, 'В конец', hover_delay=650)

        self.combo_print_order.bind('<<ComboboxSelected>>', lambda event: self.print_print(False))
        self.combo_print_group.bind('<<ComboboxSelected>>', lambda event: self.print_go_to_first_page(True))

        self.print_print(True)  # Выводим статьи
        self.search_print(True)  # Выводим статьи

    # Нажатие на кнопку "Распечатать словарь в файл"
    def print_out(self):
        folder = askdirectory(initialdir=MAIN_PATH, title='В какую папку сохранить файл?')
        if not folder:
            return
        filename = f'Распечатка_{_0_global_dct_savename}.txt'
        _0_global_dct.print_out(os.path.join(folder, filename))

    # Нажатие на кнопку "Настройки поиска"
    def search_settings(self):
        window = SearchSettingsW(self, self.search_only_fav, self.search_only_full, self.search_wrd, self.search_tr,
                                 self.search_frm, self.search_phr, self.search_nt, self.search_group)
        self.search_only_fav, self.search_only_full, self.search_wrd, self.search_tr, self.search_frm, self.search_phr,\
            self.search_nt, self.search_group = window.open()

    # Изменить статью
    def edit_entry(self, key: DctKey):
        EditW(self, key).open()

        self.search_print(False)
        self.print_print(False)

    # Вывести информацию о количестве статей (1)
    def print_print_info(self):
        group = self.var_print_group.get()
        if group == ALL_GROUPS:
            if self.var_print_fav.get():
                w, t, f = _0_global_dct.count_fav_entries()
                info = dct_info_fav((w, _0_global_dct.count_w), (t, _0_global_dct.count_t), (f, _0_global_dct.count_f))
            else:
                info = dct_info(_0_global_dct.count_w, _0_global_dct.count_t, _0_global_dct.count_f)
        else:
            if self.var_print_fav.get():
                w1, t1, f1 = _0_global_dct.count_fav_entries(group)
                w2, t2, f2 = _0_global_dct.count_entries_in_group(group)
                info = dct_info_fav((w1, w2), (t1, t2), (f1, f2))
            else:
                w, t, f = _0_global_dct.count_entries_in_group(group)
                info = dct_info(w, t, f)
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
                self.print_keys = [key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].fav]
            else:
                self.print_keys = [key for key in _0_global_dct.d.keys()
                                   if _0_global_dct.d[key].fav and group in _0_global_dct.d[key].groups]
        else:
            if group == ALL_GROUPS:
                self.print_keys = [key for key in _0_global_dct.d.keys()]
            else:
                self.print_keys = [key for key in _0_global_dct.d.keys() if group in _0_global_dct.d[key].groups]
        self.print_selected_keys = [key for key in self.print_selected_keys if key in self.print_keys]
        if not self.print_selected_keys:
            self.frame_print_buttons_for_selected.grid_remove()
        # Сортируем статьи
        if self.var_print_order.get() == PRINT_VALUES_ORDER[1]:
            self.print_keys.reverse()
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[2]:
            """
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].score, _0_global_dct.d[k].correct_att_in_a_row))
            """
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].score,
                                                _0_global_dct.d[k].correct_att_in_a_row /
                                                (1 + len(_0_global_dct.d[k].forms.keys()) +
                                                 len(_0_global_dct.d[k].phrases.keys())),
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[3]:
            """
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].score, _0_global_dct.d[k].correct_att_in_a_row),
                                     reverse=True)
            """
            self.print_keys.sort(key=lambda k: (-_0_global_dct.d[k].score,
                                                -_0_global_dct.d[k].correct_att_in_a_row /
                                                (1 + len(_0_global_dct.d[k].forms.keys()) +
                                                 len(_0_global_dct.d[k].phrases.keys())),
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[4]:
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].latest_answer_date,
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[5]:
            self.print_keys.sort(key=lambda k: ([-val for val in _0_global_dct.d[k].latest_answer_date],
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[6]:
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[7]:
            self.print_keys.sort(key=lambda k: (_0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd), reverse=True)
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[8]:
            self.print_keys.sort(key=lambda k: (len(_0_global_dct.d[k].wrd),
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        elif self.var_print_order.get() == PRINT_VALUES_ORDER[9]:
            self.print_keys.sort(key=lambda k: (-len(_0_global_dct.d[k].wrd),
                                                _0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        # Выводим информацию о количестве статей
        self.print_print_info()

        # Вычисляем значения некоторых количественных переменных
        self.print_count_elements = len(self.print_keys)
        if self.print_count_elements == 0:
            self.print_count_pages = 1
        else:
            self.print_count_pages = math.ceil(self.print_count_elements / self.print_max_elements_on_page)
        if self.print_current_page > self.print_count_pages:
            self.print_current_page = self.print_count_pages
            self.print_start_index = (self.print_count_pages - 1) * self.print_max_elements_on_page
        if self.print_current_page == self.print_count_pages:
            if self.print_count_elements % self.print_max_elements_on_page == 0 and self.print_count_elements != 0:
                self.print_count_elements_on_page = self.print_max_elements_on_page
            else:
                self.print_count_elements_on_page = self.print_count_elements % self.print_max_elements_on_page
        else:
            self.print_count_elements_on_page = self.print_max_elements_on_page
        # Выводим номер страницы
        self.var_print_current_page.set(str(self.print_current_page))
        self.entry_print_current_page.icursor(len(str(self.print_current_page)))
        self.lbl_print_current_page_2.configure(text=f'из {self.print_count_pages}')

        # Создаём новые фреймы
        self.print_frames = [ttk.Frame(self.scrolled_frame_print.frame_canvas, style='Invis.TFrame')
                             for i in range(self.print_count_elements_on_page)]
        # Создаём новые кнопки
        self.print_buttons = [ttk.Button(self.print_frames[i],
                                         command=lambda i=i: self.edit_entry(self.print_keys[self.print_start_index + i]),
                                         takefocus=False,
                                         style=('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                                               if self.print_keys[self.print_start_index + i] in self.print_selected_keys
                                               else ('FlatD.TButton' if i % 2 else 'FlatL.TButton'))
                              for i in range(self.print_count_elements_on_page)]
        # Создаём подсказки
        self.print_tips = [ttip.Hovertip(self.print_buttons[i],
                                         f'Верных ответов подряд: '
                                         f'{get_correct_att_in_a_row(_0_global_dct.d[self.print_keys[self.print_start_index + i]])}\n'
                                         f'Доля верных ответов: '
                                         f'{get_entry_percent(_0_global_dct.d[self.print_keys[self.print_start_index + i]])}',
                                         hover_delay=666)
                           for i in range(self.print_count_elements_on_page)]
        # Выводим текст на кнопки
        if self.var_print_briefly.get():
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))
        else:
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(text=get_entry_info_detailed(_0_global_dct.d[key], 75))

        for i in range(self.print_count_elements_on_page):
            # Расставляем элементы
            self.print_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.print_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.print_frames[i].bind('<Enter>', lambda event, i=i: self.print_frames[i].focus_set())
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
        if self.search_only_fav:
            keys = [key for key in _0_global_dct.d.keys() if _0_global_dct.d[key].fav]
        else:
            keys = [key for key in _0_global_dct.d.keys()]
        # Если нужно, оставляем только одну группу
        if self.search_group != ALL_GROUPS:
            keys = [key for key in keys if self.search_group in _0_global_dct.d[key].groups]
        # Среди оставшихся ищем статьи, содержащие искомый текст
        results = search_entries(_0_global_dct, tuple(keys), self.var_search_query.get(),
                                 self.search_wrd, self.search_tr, self.search_frm, self.search_phr, self.search_nt)
        # Объединяем результаты в один список
        self.search_keys = []
        for i in range(6 if self.search_only_full else 9):
            self.search_keys += sorted(list(results[i]),
                                       key=lambda k: (_0_global_dct.d[k].wrd.lower(), _0_global_dct.d[k].wrd))
        # Из выделенных статей оставляем, только удовлетворяющие поисковому запросу
        self.search_selected_keys = [key for key in self.search_selected_keys if key in self.search_keys]
        # Если выделенных статей нет, убираем связанные с ними кнопки
        if not self.search_selected_keys:
            self.frame_search_buttons_for_selected.grid_remove()

        # Вычисляем значения некоторых количественных переменных
        self.search_count_elements = len(self.search_keys)
        if self.search_count_elements == 0:
            self.search_count_pages = 1
        else:
            self.search_count_pages = math.ceil(self.search_count_elements / self.search_max_elements_on_page)
        if self.search_current_page > self.search_count_pages:
            self.search_current_page = self.search_count_pages
            self.search_start_index = (self.search_count_pages - 1) * self.search_max_elements_on_page
        if self.search_current_page == self.search_count_pages:
            if self.search_count_elements % self.search_max_elements_on_page == 0 and self.search_count_elements != 0:
                self.search_count_elements_on_page = self.search_max_elements_on_page
            else:
                self.search_count_elements_on_page = self.search_count_elements % self.search_max_elements_on_page
        else:
            self.search_count_elements_on_page = self.search_max_elements_on_page
        # Выводим информацию о количестве статей
        self.search_print_info()
        # Выводим номер страницы
        self.var_search_current_page.set(str(self.search_current_page))
        self.entry_search_current_page.icursor(len(str(self.search_current_page)))
        self.lbl_search_current_page_2.configure(text=f'из {self.search_count_pages}')

        # Создаём новые фреймы
        self.search_frames = [ttk.Frame(self.scrolled_frame_search.frame_canvas, style='Invis.TFrame')
                              for i in range(self.search_count_elements_on_page)]
        # Создаём новые кнопки
        self.search_buttons = [ttk.Button(self.search_frames[i],
                                          command=lambda i=i: self.edit_entry(self.search_keys[self.search_start_index + i]),
                                          takefocus=False,
                                          style=('FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
                                                if self.search_keys[self.search_start_index + i] in self.search_selected_keys
                                                else ('FlatD.TButton' if i % 2 else 'FlatL.TButton'))
                               for i in range(self.search_count_elements_on_page)]

        for i in range(self.search_count_elements_on_page):
            # Выводим текст на кнопки
            self.search_buttons[i].configure(text=get_all_entry_info(_0_global_dct.d[self.search_keys[self.search_start_index + i]], 75, 13))

            # Расставляем элементы
            self.search_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.search_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.search_frames[i].bind('<Enter>', lambda event, i=i: self.search_frames[i].focus_set())
            self.search_frames[i].bind('<Leave>', lambda event, i=i: self.entry_search_query.focus_set())
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
            self.print_buttons[index].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))
        else:
            key = self.print_keys[self.print_start_index + index]
            self.print_buttons[index].configure(text=get_entry_info_detailed(_0_global_dct.d[key], 75))

        # Выводим информацию о количестве статей
        self.print_print_info()

    # Обновить одну из кнопок журнала (2)
    def search_refresh_one_button(self, index: int, key: DctKey):
        # Выводим текст на кнопку
        self.search_buttons[index].configure(text=get_all_entry_info(_0_global_dct.d[key], 75, 13))

        # Выводим информацию о количестве статей
        self.search_print_info()

    # Обновить все кнопки журнала (1)
    def print_refresh_all_buttons(self):
        # Выводим текст на кнопки
        if self.var_print_briefly.get():
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(text=get_entry_info_briefly(_0_global_dct.d[key], 75))
        else:
            for i in range(self.print_count_elements_on_page):
                key = self.print_keys[self.print_start_index + i]
                self.print_buttons[i].configure(text=get_entry_info_detailed(_0_global_dct.d[key], 75))

    # Обновить все кнопки журнала (2)
    def search_refresh_all_buttons(self):
        # Выводим текст на кнопки
        for i in range(self.search_count_elements_on_page):
            key = self.search_keys[self.search_start_index + i]
            self.search_buttons[i].configure(text=get_all_entry_info(_0_global_dct.d[key], 75, 13))

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
    def print_go_to_first_page(self, to_reset_selected_keys=False):
        if to_reset_selected_keys:
            self.print_selected_keys = []
            self.frame_print_buttons_for_selected.grid_remove()
        self.print_go_to_page_with_number(1)

    # Перейти на первую страницу (2)
    def search_go_to_first_page(self, to_reset_selected_keys=False):
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
            self.print_buttons[index].configure(style='FlatD.TButton' if index % 2 else 'FlatL.TButton')
            if not self.print_selected_keys:
                self.frame_print_buttons_for_selected.grid_remove()
        else:
            self.print_selected_keys += [key]
            self.print_buttons[index].configure(style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton')
            self.frame_print_buttons_for_selected.grid(row=0, column=1, padx=(6, 0), pady=0, sticky='WS')
        self.print_print_info()

    # Выделить одну статью (или убрать выделение) (2)
    def search_select_one(self, index: int):
        key = self.search_keys[self.search_start_index + index]
        if key in self.search_selected_keys:
            self.search_selected_keys.remove(key)
            self.search_buttons[index].configure(style='FlatD.TButton' if index % 2 else 'FlatL.TButton')
            if not self.search_selected_keys:
                self.frame_search_buttons_for_selected.grid_remove()
        else:
            self.search_selected_keys += [key]
            self.search_buttons[index].configure(style='FlatSelectedD.TButton' if index % 2 else 'FlatSelectedL.TButton')
            self.frame_search_buttons_for_selected.grid(row=1, column=2, padx=(6, 0), pady=0, sticky='W')
        self.search_print_info()

    # Выделить все статьи на странице (1)
    def print_select_page(self):
        for i in range(self.print_count_elements_on_page):
            key = self.print_keys[self.print_start_index + i]
            if key not in self.print_selected_keys:
                self.print_selected_keys += [key]
            btn = self.print_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_print_buttons_for_selected.grid(row=0, column=1, padx=(6, 0), pady=0, sticky='WS')
        self.print_print_info()

    # Выделить все статьи на странице (2)
    def search_select_page(self):
        for i in range(self.search_count_elements_on_page):
            key = self.search_keys[self.search_start_index + i]
            if key not in self.search_selected_keys:
                self.search_selected_keys += [key]
            btn = self.search_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_search_buttons_for_selected.grid(row=1, column=2, padx=(6, 0), pady=0, sticky='W')
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
        self.frame_print_buttons_for_selected.grid(row=0, column=1, padx=(6, 0), pady=0, sticky='WS')
        self.print_print_info()

    # Выделить все статьи (2)
    def search_select_all(self):
        self.search_selected_keys = list(self.search_keys)
        for i in range(len(self.search_buttons)):
            btn = self.search_buttons[i]
            btn.configure(style='FlatSelectedD.TButton' if i % 2 else 'FlatSelectedL.TButton')
        self.frame_search_buttons_for_selected.grid(row=1, column=2, padx=(6, 0), pady=0, sticky='W')
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
    def fav_selected(self, keys: list[DctKey]):
        global _0_global_has_progress

        if not keys:
            return

        _0_global_dct.fav_entries(tuple(keys))

        self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

        _0_global_has_progress = True

    # Убрать выделенные статьи из избранного
    def unfav_selected(self, keys: list[DctKey]):
        global _0_global_has_progress

        if not keys:
            return

        _0_global_dct.unfav_entries(tuple(keys))

        self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

        _0_global_has_progress = True

    # Добавить выделенные статьи в группу
    def add_selected_to_group(self, keys: list[DctKey]):
        global _0_global_has_progress

        if not keys:
            return
        if not _0_global_dct.groups:
            PopupMsgW(self, 'Не найдено ни одной группы!').open()
            return

        sets = [_0_global_dct.d[key].groups for key in keys]
        values_intersec = set.intersection(*sets)
        values = [gr for gr in _0_global_dct.groups if gr not in values_intersec]
        if not values:
            PopupMsgW(self, 'Выделенные статьи уже состоят во всех группах!').open()
            return
        window_groups = PopupChooseW(self, msg='Выберите группу, в которую хотите добавить выбранные слова:',
                                     values=values, default_value=_0_global_dct.groups[0])
        closed, group = window_groups.open()
        if closed:
            return
        _0_global_dct.add_entries_to_group(group, tuple(keys))

        if group == self.var_print_group.get():
            self.print_print(True)
        else:
            self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

        _0_global_has_progress = True

    # Убрать выделенные статьи из группы
    def remove_selected_from_group(self, keys: list[DctKey]):
        global _0_global_has_progress

        if not keys:
            return
        if not _0_global_dct.groups:
            PopupMsgW(self, 'Не найдено ни одной группы!').open()
            return

        values = []
        for key in keys:
            for gr in _0_global_dct.d[key].groups:
                if gr not in values:
                    values += [gr]
        if not values:
            PopupMsgW(self, 'Выделенные статьи не состоят ни в каких группах!').open()
            return
        if self.var_print_group.get() == ALL_GROUPS or self.tabs.index(self.tabs.select()) == 1:
            default_value = values[0]
        else:
            default_value = self.var_print_group.get()
        window_groups = PopupChooseW(self, msg='Выберите группу, из которой хотите убрать выбранные слова:',
                                     values=values, default_value=default_value)
        closed, group = window_groups.open()
        if closed:
            return
        _0_global_dct.remove_entries_from_group(group, tuple(keys))

        if group == self.var_print_group.get():
            self.print_print(True)
        else:
            self.print_refresh_all_buttons()
        self.search_refresh_all_buttons()

        _0_global_has_progress = True

    # Удалить выделенные статьи
    def delete_selected(self, keys: list[DctKey]):
        global _0_global_has_progress

        if not keys:
            return

        count_selected = len(keys)
        tmp = set_postfix(count_selected, ('статью', 'статьи', 'статей'))
        window = PopupDialogueW(self, f'Вы действительно хотите удалить {count_selected} {tmp}?',
                                set_enter_on_btn='none')
        answer = window.open()
        if not answer:
            return

        for key in keys:
            _0_global_dct.delete_entry(key)

        self.print_print(True)
        self.search_print(True)

        _0_global_has_progress = True

    # Справка об окне
    def about_window(self):
        PopupMsgW(self, '* Чтобы прокрутить в самый низ, нажмите Ctrl+D или DOWN\n'
                        '* Чтобы прокрутить в самый верх, нажмите Ctrl+U или UP\n'
                        '* Чтобы выделить статью, наведите на неё мышку и нажмите ПКМ',
                  msg_justify='left').open()

    # Нажатие на кнопку "Добавить запись в словарь"
    def add_entry(self):
        key = AddW(self).open()
        if not key:
            return
        EditW(self, key).open()

        self.search_print(False)
        self.print_print(False)

    # Установить фокус (вкладка "Просмотр словаря")
    def set_focus_print(self):
        self.focus_set()

        self.unbind('<Return>')
        self.unbind('<Key>')

        self.bind('<Up>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(0.0))
        self.bind('<Down>', lambda event: self.scrolled_frame_print.canvas.yview_moveto(1.0))
        self.bind('<Control-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('U', lambda: self.scrolled_frame_print.canvas.yview_moveto(0.0)),
                                             ('D', lambda: self.scrolled_frame_print.canvas.yview_moveto(1.0))]))
        self.bind('<Alt-Shift-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('P', lambda: self.print_unselect_page()),
                                             ('A', lambda: self.print_unselect_all()),
                                             ('G', lambda: self.remove_selected_from_group(self.print_selected_keys)),
                                             ('F', lambda: self.unfav_selected(self.print_selected_keys))]))
        self.bind('<Alt-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('P', lambda: self.print_select_page()),
                                             ('A', lambda: self.print_select_all()),
                                             ('G', lambda: self.add_selected_to_group(self.print_selected_keys)),
                                             ('F', lambda: self.fav_selected(self.print_selected_keys)),
                                             ('D', lambda: self.delete_selected(self.print_selected_keys))]))

    # Установить фокус (вкладка "Поиск")
    def set_focus_search(self):
        self.entry_search_query.focus_set()

        bind_ctrl_acvx(self.entry_search_query)
        self.bind('<Return>', lambda event: self.btn_search_search.invoke())
        self.bind('<Key>', lambda event: self.entry_search_query.focus_set())
        self.bind('<Up>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(0.0))
        self.bind('<Down>', lambda event: self.scrolled_frame_search.canvas.yview_moveto(1.0))
        self.bind('<Control-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('U', lambda: self.scrolled_frame_search.canvas.yview_moveto(0.0)),
                                             ('D', lambda: self.scrolled_frame_search.canvas.yview_moveto(1.0))]))
        self.bind('<Alt-Shift-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('P', lambda: self.search_unselect_page()),
                                             ('A', lambda: self.search_unselect_all()),
                                             ('G', lambda: self.remove_selected_from_group(self.search_selected_keys)),
                                             ('F', lambda: self.unfav_selected(self.search_selected_keys))]))
        self.bind('<Alt-KeyPress>',
                  lambda key: bind_keypress(key,
                                            [('P', lambda: self.search_select_page()),
                                             ('A', lambda: self.search_select_all()),
                                             ('G', lambda: self.add_selected_to_group(self.search_selected_keys)),
                                             ('F', lambda: self.fav_selected(self.search_selected_keys)),
                                             ('D', lambda: self.delete_selected(self.search_selected_keys))]))

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

    def open(self, tab: typing.Literal['print', 'search'] = 'print'):
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
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Добавление статьи')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
            value_wrd = encode_special_combinations(value_wrd, _0_global_special_combinations)
            value_tr = encode_special_combinations(value_tr, _0_global_special_combinations)

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

        self.dct_key = add_entry_with_choose(_0_global_dct, self,
                                             encode_special_combinations(self.var_wrd.get(),
                                                                         _0_global_special_combinations),
                                             encode_special_combinations(self.var_tr.get(),
                                                                         _0_global_special_combinations))
        if not self.dct_key:
            return
        _0_global_dct.d[self.dct_key].fav = self.var_fav.get()
        for group in _0_global_fav_groups:
            _0_global_dct.d[self.dct_key].add_to_group(group)

        _0_global_has_progress = True
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_wrd.focus_set()

        bind_ctrl_acvx(self.entry_wrd)
        bind_ctrl_acvx(self.entry_tr)
        self.bind('<Return>', lambda event: self.btn_add.invoke())
        self.bind('<Escape>', lambda event: self.destroy())

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
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

        self.parent = parent
        self.current_tab = 1  # Текущая вкладка (1 или 2)
        self.has_ctg_changes = False
        self.has_groups_changes = False
        self.has_spec_comb_changes = False
        self.backup_dct = copy.deepcopy(_0_global_dct)
        self.backup_scale = _0_global_scale

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
        self.tabs.add(self.tab_local, text='Настройки открытого словаря')
        # {
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
        self.btn_groups = ttk.Button(self.tab_local, text='Группы', command=self.groups_settings,
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

        self.tip_btn_about_typo = ttip.Hovertip(self.btn_about_typo, 'Справка', hover_delay=450)
        self.tip_btn_about_dcts = ttip.Hovertip(self.btn_about_dcts, 'Справка', hover_delay=450)

        self.print_dct_list(True)
        self.refresh_scale_buttons()

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
        global _0_global_dct, _0_global_dct_savename, _0_global_special_combinations, _0_global_check_register,\
            _0_global_has_progress, _0_global_session_number, _0_global_search_settings, _0_global_learn_settings

        if savename == _0_global_dct_savename:
            return

        # Если есть прогресс, то предлагается его сохранить
        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, _0_global_dct_savename, _0_global_has_progress)

        _0_global_dct = Dictionary()
        res = upload_save(self, _0_global_dct, savename, 'Отмена')
        if not res:
            self.destroy()  # Если была попытка открыть повреждённый словарь, то при сохранении настроек, текущий словарь стёрся бы
            return
        _0_global_dct_savename, _0_global_check_register, _0_global_special_combinations, _0_global_fav_groups = res
        _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
            upload_local_auto_settings(_0_global_dct_savename)
        save_dct_name()

        self.backup_dct = copy.deepcopy(_0_global_dct)

        # Обновляем надписи с названием открытого словаря
        self.refresh_open_dct_name(_0_global_dct_savename)

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

        self.print_dct_list(False)

    # Создать словарь (срабатывает при нажатии на кнопку)
    def dct_create(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_special_combinations, _0_global_check_register,\
            _0_global_has_progress, _0_global_session_number, _0_global_search_settings, _0_global_learn_settings,\
            _0_global_fav_groups

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
        _0_global_check_register, _0_global_special_combinations, _0_global_dct.ctg, _0_global_dct.groups,\
            _0_global_fav_groups = upload_local_settings(savename)
        _0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
            upload_local_auto_settings(savename)
        _0_global_dct_savename = savename
        save_dct_name()

        print(f'\nСловарь "{savename}" успешно создан и открыт')

        self.backup_dct = copy.deepcopy(_0_global_dct)

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
        upload_custom_theme(False)
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

        # Установка масштаба для окна уведомления об обновлении
        try:
            _0_global_window_last_version.entry_url.configure(font=('StdFont', _0_global_scale))
        except:  # Если окно обновления не открыто
            pass

        self.refresh_scale_buttons()

    # Сохранить настройки (срабатывает при нажатии на кнопку)
    def save(self):
        global _0_global_check_register, _0_global_show_updates, _0_global_with_typo, _0_global_has_progress

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
        self.backup_scale = _0_global_scale

        # Сохранение настроек в файлы
        save_local_settings(_0_global_check_register, _0_global_special_combinations, _0_global_dct.ctg,
                            _0_global_dct.groups, _0_global_fav_groups, _0_global_dct_savename)
        save_global_settings(_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale)
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
                                        takefocus=False, style='FlatD.TButton' if i % 2 else 'FlatL.TButton')
                             for i in range(dcts_count)]
        for i in range(dcts_count):
            # Выводим текст на кнопки
            savename = self.dcts_savenames[i]
            if savename == _0_global_dct_savename:
                self.dcts_buttons[i].configure(text=split_text(f'{savename} (ОТКРЫТ)', 35))
            else:
                self.dcts_buttons[i].configure(text=split_text(f'{savename}', 35))

            # Расставляем элементы
            self.dcts_frames[i].grid(row=i, column=0, padx=0, pady=0, sticky='WE')
            # {
            self.dcts_buttons[i].grid(row=0, column=0, padx=0, pady=0, sticky='WE')
            # }

            # Привязываем события
            self.dcts_frames[i].bind('<Enter>', lambda event, i=i: self.dcts_frames[i].focus_set())
            self.dcts_frames[i].bind('<Leave>', lambda event: self.focus_set())
            self.dcts_frames[i].bind('<Control-KeyPress>',
                                     lambda key, i=i:
                                     bind_keypress(key, [('R', lambda: self.dct_rename(self.dcts_savenames[i])),
                                                         ('D', lambda: self.dct_delete(self.dcts_savenames[i])),
                                                         ('E', lambda: self.dct_export(self.dcts_savenames[i]))]))

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
        self.var_check_register.set(bool(_0_global_check_register))
        self.print_dct_list(False)

    # Установить выбранную тему
    def set_theme(self):
        global th

        th = self.var_theme.get()

        self.parent.set_ttk_styles()  # Установка ttk-стилей
        upload_theme_img(th)  # Загрузка изображений темы

        # Установка изображений
        set_image(self.btn_about_typo, self.img_about, img_about, '?')
        set_image(self.btn_about_dcts, self.img_about, img_about, '?')
        set_image(self.btn_scale_plus, self.img_plus, img_add, '+')
        set_image(self.btn_scale_minus, self.img_minus, img_delete, '-')

        # Установка некоторых стилей для окна настроек
        self.configure(bg=STYLES['*.BG.*'][1][th])
        self.scrolled_frame_dcts.canvas.configure(bg=STYLES['*.BG.ENTRY'][1][th])

        # Установка фона для главного окна
        self.parent.configure(bg=STYLES['*.BG.*'][1][th])

        # Установка фона для окна уведомления об обновлении
        try:
            _0_global_window_last_version.configure(bg=STYLES['*.BG.*'][1][th])
        except:  # Если окно обновления не открыто
            pass

    # Были ли изменения локальных настроек
    def has_local_changes(self):
        return self.has_ctg_changes or\
            self.has_groups_changes or\
            self.has_spec_comb_changes or\
            int(self.var_check_register.get()) != _0_global_check_register

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

        self.bind('<Escape>', lambda event: self.btn_close.invoke())
        self.tabs.bind('<<NotebookTabChanged>>', lambda event: self.resize_tabs())

    def open(self):
        global _0_global_dct

        self.set_focus()

        self.grab_set()
        self.wait_window()

        _0_global_dct = copy.deepcopy(self.backup_dct)


# Окно уведомления о выходе новой версии
class NewVersionAvailableW(tk.Toplevel):
    def __init__(self, parent, last_version: str):
        super().__init__(parent)
        self.title('Доступна новая версия')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])
        toplevel_geometry(parent, self)

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
            # Получаем список обновляемых файлов
            update_files = [fn.strip() for fn in open(f'{NEW_VERSION_DIR}/{UPDATE_FILES}', 'r').readlines()]
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
            exit(EXIT_UPDATE)


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=STYLES['*.BG.*'][1][th])

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
        self.btn_search = ttk.Button(self.frame_buttons, text='Поиск', command=self.search,
                                     takefocus=False, style='Default.TButton')
        self.btn_add = ttk.Button(self.frame_buttons, text='Добавить запись в словарь', command=self.add,
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

    # Нажатие на кнопку "Учить слова"
    def learn(self):
        self.disable_all_buttons()

        res = ChooseLearnModeW(self).open()
        if not res:
            self.enable_all_buttons()
            return
        LearnW(self, res).open()

        self.enable_all_buttons()

    # Нажатие на кнопку "Просмотреть словарь"
    def print(self):
        self.disable_all_buttons()
        PrintW(self).open()
        self.enable_all_buttons()

    # Нажатие на кнопку "Поиск"
    def search(self):
        self.disable_all_buttons()
        PrintW(self).open(tab='search')
        self.enable_all_buttons()

    # Нажатие на кнопку "Добавить запись в словарь"
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
            _0_global_special_combinations, _0_global_check_register, _0_global_learn_settings,\
            _0_global_session_number, _0_global_search_settings, _0_global_fav_groups

        self.disable_all_buttons()
        SettingsW(self).open()
        self.enable_all_buttons()

        # Обновляем глобальные настройки
        _0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale =\
            upload_global_settings()
        # Обновляем локальные настройки
        _0_global_check_register, _0_global_special_combinations, _0_global_dct.ctg, _0_global_dct.groups,\
            _0_global_fav_groups = upload_local_settings(_0_global_dct_savename)
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
                                      background=STYLES['*.BG.*'][1][th],
                                      foreground=STYLES['*.FG.*'][1][th])

        # Стиль label "header"
        self.st_lbl_header = ttk.Style()
        self.st_lbl_header.theme_use('alt')
        self.st_lbl_header.configure('Header.TLabel',
                                     font=('StdFont', _0_global_scale + 5),
                                     background=STYLES['*.BG.*'][1][th],
                                     foreground=STYLES['*.FG.*'][1][th])

        # Стиль label "logo"
        self.st_lbl_logo = ttk.Style()
        self.st_lbl_logo.theme_use('alt')
        self.st_lbl_logo.configure('Logo.TLabel',
                                   font=('Times', _0_global_scale + 11),
                                   background=STYLES['*.BG.*'][1][th],
                                   foreground=STYLES['*.FG.LOGO'][1][th])

        # Стиль label "footer"
        self.st_lbl_footer = ttk.Style()
        self.st_lbl_footer.theme_use('alt')
        self.st_lbl_footer.configure('Footer.TLabel',
                                     font=('StdFont', _0_global_scale - 2),
                                     background=STYLES['*.BG.*'][1][th],
                                     foreground=STYLES['*.FG.FOOTER'][1][th])

        # Стиль label "warn"
        self.st_lbl_warn = ttk.Style()
        self.st_lbl_warn.theme_use('alt')
        self.st_lbl_warn.configure('Warn.TLabel',
                                   font=('StdFont', _0_global_scale),
                                   background=STYLES['*.BG.*'][1][th],
                                   foreground=STYLES['*.FG.WARN'][1][th])

        # Стиль label "flat light"
        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure('FlatL.TLabel',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   background=STYLES['FLAT_BTN.BG.1'][1][th],
                                   foreground=STYLES['FLAT_BTN.FG.1'][1][th])

        # Стиль label "flat dark"
        self.st_lbl_note = ttk.Style()
        self.st_lbl_note.theme_use('alt')
        self.st_lbl_note.configure('FlatD.TLabel',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   background=STYLES['FLAT_BTN.BG.2'][1][th],
                                   foreground=STYLES['FLAT_BTN.FG.2'][1][th])

        # Стиль entry "default"
        self.st_entry = ttk.Style()
        self.st_entry.theme_use('alt')
        self.st_entry.configure('Default.TEntry',
                                font=('StdFont', _0_global_scale))
        self.st_entry.map('Default.TEntry',
                          fieldbackground=[('readonly', STYLES['*.BG.*'][1][th]),
                                           ('!readonly', STYLES['*.BG.ENTRY'][1][th])],
                          foreground=[('readonly', STYLES['*.FG.*'][1][th]),
                                      ('!readonly', STYLES['*.FG.ENTRY'][1][th])],
                          selectbackground=[('readonly', STYLES['*.BG.SEL'][1][th]),
                                            ('!readonly', STYLES['*.BG.SEL'][1][th])],
                          selectforeground=[('readonly', STYLES['*.FG.SEL'][1][th]),
                                            ('!readonly', STYLES['*.FG.SEL'][1][th])])

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
                                background=[('pressed', STYLES['BTN.BG.ACT'][1][th]),
                                            ('active', STYLES['BTN.BG.*'][1][th]),
                                            ('!active', STYLES['BTN.BG.*'][1][th])],
                                foreground=[('pressed', STYLES['*.FG.*'][1][th]),
                                            ('active', STYLES['*.FG.*'][1][th]),
                                            ('!active', STYLES['*.FG.*'][1][th])])

        # Стиль button "disabled" (для выключенных "default")
        self.st_btn_disabled = ttk.Style()
        self.st_btn_disabled.theme_use('alt')
        self.st_btn_disabled.configure('Disabled.TButton',
                                       font=('StdFont', _0_global_scale + 2),
                                       borderwidth=1)
        self.st_btn_disabled.map('Disabled.TButton',
                                 relief=[('active', 'raised'),
                                         ('!active', 'raised')],
                                 background=[('active', STYLES['BTN.BG.DISABL'][1][th]),
                                             ('!active', STYLES['BTN.BG.DISABL'][1][th])],
                                 foreground=[('active', STYLES['BTN.FG.DISABL'][1][th]),
                                             ('!active', STYLES['BTN.FG.DISABL'][1][th])])

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
                            background=[('pressed', STYLES['BTN.BG.Y_ACT'][1][th]),
                                        ('active', STYLES['BTN.BG.Y'][1][th]),
                                        ('!active', STYLES['BTN.BG.Y'][1][th])],
                            foreground=[('pressed', STYLES['*.FG.*'][1][th]),
                                        ('active', STYLES['*.FG.*'][1][th]),
                                        ('!active', STYLES['*.FG.*'][1][th])])

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
                           background=[('pressed', STYLES['BTN.BG.N_ACT'][1][th]),
                                       ('active', STYLES['BTN.BG.N'][1][th]),
                                       ('!active', STYLES['BTN.BG.N'][1][th])],
                           foreground=[('pressed', STYLES['*.FG.*'][1][th]),
                                       ('active', STYLES['*.FG.*'][1][th]),
                                       ('!active', STYLES['*.FG.*'][1][th])])

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
                              background=[('pressed', STYLES['BTN.BG.IMG_ACT'][1][th]),
                                          ('active', STYLES['BTN.BG.IMG_HOV'][1][th]),
                                          ('!active', STYLES['*.BG.*'][1][th])],
                              foreground=[('pressed', STYLES['*.FG.*'][1][th]),
                                          ('active', STYLES['*.FG.*'][1][th]),
                                          ('!active', STYLES['*.FG.*'][1][th])])

        # Стиль button "flat light"
        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure('FlatL.TButton',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   borderwidth=0)
        self.st_btn_note.map('FlatL.TButton',
                             relief=[('pressed', 'flat'),
                                     ('active', 'flat'),
                                     ('!active', 'flat')],
                             background=[('pressed', STYLES['FLAT_BTN.BG.ACT'][1][th]),
                                         ('active', STYLES['FLAT_BTN.BG.HOV'][1][th]),
                                         ('!active', STYLES['FLAT_BTN.BG.1'][1][th])],
                             foreground=[('pressed', STYLES['FLAT_BTN.FG.ACT'][1][th]),
                                         ('active', STYLES['FLAT_BTN.FG.HOV'][1][th]),
                                         ('!active', STYLES['FLAT_BTN.FG.1'][1][th])])

        # Стиль button "flat dark"
        self.st_btn_note = ttk.Style()
        self.st_btn_note.theme_use('alt')
        self.st_btn_note.configure('FlatD.TButton',
                                   font=('DejaVu Sans Mono', _0_global_scale + 1),
                                   borderwidth=0)
        self.st_btn_note.map('FlatD.TButton',
                             relief=[('pressed', 'flat'),
                                     ('active', 'flat'),
                                     ('!active', 'flat')],
                             background=[('pressed', STYLES['FLAT_BTN.BG.ACT'][1][th]),
                                         ('active', STYLES['FLAT_BTN.BG.HOV'][1][th]),
                                         ('!active', STYLES['FLAT_BTN.BG.2'][1][th])],
                             foreground=[('pressed', STYLES['FLAT_BTN.FG.ACT'][1][th]),
                                         ('active', STYLES['FLAT_BTN.FG.HOV'][1][th]),
                                         ('!active', STYLES['FLAT_BTN.FG.2'][1][th])])

        # Стиль button "flat selected light"
        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure('FlatSelectedL.TButton',
                                            font=('DejaVu Sans Mono', _0_global_scale + 1),
                                            borderwidth=0)
        self.st_btn_note_selected.map('FlatSelectedL.TButton',
                                      relief=[('pressed', 'flat'),
                                              ('active', 'flat'),
                                              ('!active', 'flat')],
                                      background=[('pressed', STYLES['FLAT_BTN.BG.SEL_ACT'][1][th]),
                                                  ('active', STYLES['FLAT_BTN.BG.SEL_HOV'][1][th]),
                                                  ('!active', STYLES['FLAT_BTN.BG.SEL_1'][1][th])],
                                      foreground=[('pressed', STYLES['FLAT_BTN.FG.SEL_ACT'][1][th]),
                                                  ('active', STYLES['FLAT_BTN.FG.SEL_HOV'][1][th]),
                                                  ('!active', STYLES['FLAT_BTN.FG.SEL_1'][1][th])])

        # Стиль button "flat selected dark"
        self.st_btn_note_selected = ttk.Style()
        self.st_btn_note_selected.theme_use('alt')
        self.st_btn_note_selected.configure('FlatSelectedD.TButton',
                                            font=('DejaVu Sans Mono', _0_global_scale + 1),
                                            borderwidth=0)
        self.st_btn_note_selected.map('FlatSelectedD.TButton',
                                      relief=[('pressed', 'flat'),
                                              ('active', 'flat'),
                                              ('!active', 'flat')],
                                      background=[('pressed', STYLES['FLAT_BTN.BG.SEL_ACT'][1][th]),
                                                  ('active', STYLES['FLAT_BTN.BG.SEL_HOV'][1][th]),
                                                  ('!active', STYLES['FLAT_BTN.BG.SEL_2'][1][th])],
                                      foreground=[('pressed', STYLES['FLAT_BTN.FG.SEL_ACT'][1][th]),
                                                  ('active', STYLES['FLAT_BTN.FG.SEL_HOV'][1][th]),
                                                  ('!active', STYLES['FLAT_BTN.FG.SEL_2'][1][th])])

        # Стиль checkbutton "default"
        self.st_check = ttk.Style()
        self.st_check.theme_use('alt')
        self.st_check.map('Default.TCheckbutton',
                          background=[('active', STYLES['CHECK.BG.SEL'][1][th]),
                                      ('!active', STYLES['*.BG.*'][1][th])])

        # Стиль combobox "default"
        self.st_combo = ttk.Style()
        self.st_combo.theme_use('alt')
        self.st_combo.configure('Default.TCombobox',
                                font=('DejaVu Sans Mono', _0_global_scale))
        self.st_combo.map('Default.TCombobox',
                          background=[('readonly', STYLES['BTN.BG.*'][1][th]),
                                      ('!readonly', STYLES['BTN.BG.*'][1][th])],
                          fieldbackground=[('readonly', STYLES['*.BG.ENTRY'][1][th]),
                                           ('!readonly', STYLES['*.BG.ENTRY'][1][th])],
                          selectbackground=[('readonly', STYLES['*.BG.ENTRY'][1][th]),
                                            ('!readonly', STYLES['*.BG.ENTRY'][1][th])],
                          highlightbackground=[('readonly', STYLES['*.BORDER_CLR.*'][1][th]),
                                               ('!readonly', STYLES['*.BORDER_CLR.*'][1][th])],
                          foreground=[('readonly', STYLES['*.FG.*'][1][th]),
                                      ('!readonly', STYLES['*.FG.*'][1][th])],
                          selectforeground=[('readonly', STYLES['*.FG.*'][1][th]),
                                            ('!readonly', STYLES['*.FG.*'][1][th])])

        # Стиль всплывающего списка combobox
        self.option_add('*TCombobox*Listbox*Font', ('DejaVu Sans Mono', _0_global_scale))
        self.option_add('*TCombobox*Listbox*Background', STYLES['*.BG.ENTRY'][1][th])
        self.option_add('*TCombobox*Listbox*Foreground', STYLES['*.FG.*'][1][th])
        self.option_add('*TCombobox*Listbox*selectBackground', STYLES['*.BG.SEL'][1][th])
        self.option_add('*TCombobox*Listbox*selectForeground', STYLES['*.FG.SEL'][1][th])

        # Стиль scrollbar "vertical"
        self.st_vscroll = ttk.Style()
        self.st_vscroll.theme_use('alt')
        self.st_vscroll.map('Vertical.TScrollbar',
                            troughcolor=[('disabled', STYLES['*.BG.*'][1][th]),
                                         ('pressed', STYLES['SCROLL.BG.ACT'][1][th]),
                                         ('!pressed', STYLES['SCROLL.BG.*'][1][th])],
                            background=[('disabled', STYLES['*.BG.*'][1][th]),
                                        ('pressed', STYLES['SCROLL.FG.ACT'][1][th]),
                                        ('!pressed', STYLES['SCROLL.FG.*'][1][th])])

        # Стиль notebook "default"
        self.st_note = ttk.Style()
        self.st_note.theme_use('alt')
        self.st_note.configure('Default.TNotebook',
                               font=('StdFont', _0_global_scale))
        self.st_note.map('Default.TNotebook',
                         troughcolor=[('active', STYLES['*.BG.*'][1][th]),
                                      ('!active', STYLES['*.BG.*'][1][th])],
                         background=[('selected', STYLES['BTN.BG.ACT'][1][th]),
                                     ('!selected', STYLES['*.BG.*'][1][th])])

        # Стиль вкладок notebook
        self.st_note.configure('TNotebook.Tab',
                               font=('StdFont', _0_global_scale))
        self.st_note.map('TNotebook.Tab',
                         background=[('selected', STYLES['TAB.BG.SEL'][1][th]),
                                     ('!selected', STYLES['TAB.BG.*'][1][th])],
                         foreground=[('selected', STYLES['TAB.FG.SEL'][1][th]),
                                     ('!selected', STYLES['TAB.FG.*'][1][th])])

        # Стиль frame "default"
        self.st_frame_default = ttk.Style()
        self.st_frame_default.theme_use('alt')
        self.st_frame_default.configure('Default.TFrame',
                                        borderwidth=1,
                                        relief=STYLES['FRAME.RELIEF.*'][1][th],
                                        background=STYLES['*.BG.*'][1][th],
                                        bordercolor=STYLES['*.BORDER_CLR.*'][1][th])

        # Стиль frame "invis"
        self.st_frame_invis = ttk.Style()
        self.st_frame_invis.theme_use('alt')
        self.st_frame_invis.configure('Invis.TFrame',
                                      borderwidth=0,
                                      relief=STYLES['FRAME.RELIEF.*'][1][th],
                                      background=STYLES['*.BG.*'][1][th])

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

print('\nПрограмма запускается...')
print('\nЗагрузка тем...')
upload_themes(THEMES)  # Загружаем дополнительные темы
upload_custom_theme()  # Загружаем пользовательскую тему
_0_global_dct_savename, _0_global_show_updates, _0_global_with_typo, th, _0_global_scale =\
    upload_global_settings()  # Загружаем глобальные настройки
upload_theme_img(th)  # Загружаем изображения для выбранной темы
root = MainW()  # Создаём графический интерфейс
uploaded_save = upload_save(root, _0_global_dct, _0_global_dct_savename, 'Завершить работу')  # Загружаем словарь
if not uploaded_save:
    exit(EXIT_DCT_LOAD_FAILED)
uploaded_save: tuple[str, int, dict[tuple[str, str], str], list[str]]
_0_global_dct_savename, _0_global_check_register, _0_global_special_combinations, _0_global_fav_groups = uploaded_save
_0_global_session_number, _0_global_search_settings, _0_global_learn_settings =\
    upload_local_auto_settings(_0_global_dct_savename)  # Загружаем локальные авто-настройки
_0_global_window_last_version = check_updates(root, bool(_0_global_show_updates), False)  # Проверяем наличие обновлений
_0_global_learn_session_number = 0
if ICON_FN in os.listdir(RESOURCES_PATH):
    root.iconphoto(True, tk.PhotoImage(file=ICON_PATH))  # Устанавливаем иконку
print('\nЗапуск программы прошёл успешно')
root.mainloop()
print('\nПрограмма успешно завершилась')

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
