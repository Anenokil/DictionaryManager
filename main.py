import os
import random
import math
import sys
if sys.version_info[0] == 3:
    import tkinter as tk
    import tkinter.ttk as ttk
else:
    import Tkinter as tk
    import Tkinter.ttk as ttk

PROGRAM_NAME = 'Dictionary'
PROGRAM_VERSION = 'v7.0.0-PRE_33'
PROGRAM_DATE = '13.1.2023 0:19 (UTC+5)'

""" Стили """

# Все: bg
# Все, кроме frame: fg
# Все, кроме текста: border
# Frame: relief
# Кнопки: activebackground
# Entry: selectbackground, highlightcolor

ST_BG          = {'light': '#EEEEEE', 'dark': '#222222', 'infernal': '#DD1515'}  # bg или background
ST_BG_FIELDS   = {'light': '#FFFFFF', 'dark': '#171717', 'infernal': '#CCCCCC'}  # bg
#ST_BG_ERR      = {'light': '#EE6666', 'dark': '#773333', 'infernal': '#FF0000'}  # bg

ST_BORDER      = {'light': '#222222', 'dark': '#111111', 'infernal': '#330000'}  # highlightbackground
ST_RELIEF      = {'light': 'groove',  'dark': 'solid',   'infernal': 'groove' }  # relief

ST_SELECT      = {'light': '#BBBBBB', 'dark': '#444444', 'infernal': '#FF5500'}  # selectbackground
ST_HIGHLIGHT   = {'light': '#00DD00', 'dark': '#007700', 'infernal': '#EEEEEE'}  # highlightcolor

ST_BTN         = {'light': '#D0D0D0', 'dark': '#202020', 'infernal': '#DD2020'}  # bg
ST_BTN_SELECT  = {'light': '#BABABA', 'dark': '#272727', 'infernal': '#DD5020'}  # activebackground
ST_BTNY        = {'light': '#88DD88', 'dark': '#446F44', 'infernal': '#CC6633'}  # bg
ST_BTNY_SELECT = {'light': '#77CC77', 'dark': '#558055', 'infernal': '#CC9633'}  # activebackground
ST_BTNN        = {'light': '#FF6666', 'dark': '#803333', 'infernal': '#CD0000'}  # bg
ST_BTNN_SELECT = {'light': '#EE5555', 'dark': '#904444', 'infernal': '#CD3000'}  # activebackground

ST_FG_TEXT     = {'light': '#222222', 'dark': '#979797', 'infernal': '#000000'}  # fg или foreground
ST_FG_LOGO     = {'light': '#FF7200', 'dark': '#803600', 'infernal': '#FF7200'}  # fg
ST_FG_FOOTER   = {'light': '#666666', 'dark': '#666666', 'infernal': '#222222'}  # fg

st = 'light'

""" Папки и файлы """

RESOURCES_DIR = 'resources'
SAVES_DIR = 'saves'
SAVES_PATH = os.path.join(RESOURCES_DIR, SAVES_DIR)
SETTINGS_FN = 'settings.txt'
SETTINGS_PATH = os.path.join(RESOURCES_DIR, SETTINGS_FN)
LOCAL_SETTINGS_DIR = 'local_settings'
LOCAL_SETTINGS_PATH = os.path.join(RESOURCES_DIR, LOCAL_SETTINGS_DIR)

if RESOURCES_DIR not in os.listdir(os.curdir):
    os.mkdir(RESOURCES_DIR)
if SAVES_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(SAVES_PATH)
if LOCAL_SETTINGS_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(LOCAL_SETTINGS_PATH)

""" Другое """

FORMS_SEPARATOR = '@'

VALUES_ORDER = ('Угадывать слово по переводу', 'Угадывать перевод по слову')
VALUES_WORDS = ('Все слова', 'Чаще сложные', 'Только избранные')

"""
    Про формы:
    
    'чашка' - СЛОВО

    'чашка'   - начальная ФОРМА СЛОВА 'чашка'   (ед. число, им. падеж)
    'чашками' -           ФОРМА СЛОВА 'чашка' (множ. число, тв. падеж)
    
      'ед. число, им. падеж' - ШАБЛОН ФОРМЫ 'чашка'
    'множ. число, тв. падеж' - ШАБЛОН ФОРМЫ 'чашками'
    
    'число' и 'падеж' - ПАРАМЕТРЫ форм
    
    'ед. число' и 'множ. число' - ЗНАЧЕНИЯ ПАРАМЕТРА 'число'
    'им. падеж' и   'тв. падеж' - ЗНАЧЕНИЯ ПАРАМЕТРА 'падеж'
"""


# Количество строк, необходимых для записи текста, при данной длине строки
def height(_text, _len_str):
    _parts = _text.split('\n')
    return sum(math.ceil(len(_part) / _len_str) for _part in _parts)


# Вывод
def outp(_dst, _text='', _end='\n', _mode=tk.INSERT):
    _dst.insert(_mode, _text + _end)


# Добавить немецкие буквы
def code(_str):
    _str = _str.replace('##', '1ä')
    _str = _str.replace('#a', '2ä')

    _str = _str.replace('#A', 'Ä')
    _str = _str.replace('#o', 'ö')
    _str = _str.replace('#O', 'Ö')
    _str = _str.replace('#u', 'ü')
    _str = _str.replace('#U', 'Ü')
    _str = _str.replace('#s', 'ß')
    _str = _str.replace('#S', 'ẞ')

    _str = _str.replace('1ä', '#')
    _str = _str.replace('2ä', 'ä')
    return _str


# Заменить немецкие буквы английскими (для find_and_highlight)
def deu_to_eng(_str):
    _str = _str.replace('##', '1ä')
    _str = _str.replace('ss', '2ä')
    _str = _str.replace('sS', '2ä')
    _str = _str.replace('SS', '3ä')
    _str = _str.replace('Ss', '3ä')

    _str = _str.replace('#a', 'a')
    _str = _str.replace('#A', 'A')
    _str = _str.replace('#o', 'o')
    _str = _str.replace('#O', 'O')
    _str = _str.replace('#u', 'u')
    _str = _str.replace('#U', 'U')
    _str = _str.replace('#s', 's')
    _str = _str.replace('#S', 'S')

    _str = _str.replace('1ä', '#')
    _str = _str.replace('2ä', 's')
    _str = _str.replace('3ä', 'S')
    return _str


# Перевести кортеж в строку (для вывода на экран)
def tpl(_tuple):
    _res = ''
    _is_first = True
    for _i in range(len(_tuple)):
        if _tuple[_i] != '':
            if _is_first:
                _res += f'{_tuple[_i]}'
                _is_first = False
            else:
                _res += f', {_tuple[_i]}'
    return _res


# Перевести кортеж в строку (для сохранения в файл)
def code_tpl(_tuple, _separator=FORMS_SEPARATOR):
    _res = ''
    if len(_tuple) != 0:
        _res += _tuple[0]
    for _i in range(1, len(_tuple)):
        _res += f'{_separator}{_tuple[_i]}'
    return _res


# Перевести строку в кортеж (для чтения из файла)
def decode_tpl(_str, _separator=FORMS_SEPARATOR):
    return tuple(_str.split(_separator))


# Добавить значение параметра форм
def add_frm_param_val(_window, _vals, _text='Введите новое значение параметра'):
    window = PopupEntryW(_window, _text)
    _new_v = window.open()
    if _new_v in _vals:
        PopupMsgW(_window, f'Значение "{_new_v}" уже существует', title='Warning').open()
    elif _new_v == '':
        PopupMsgW(_window, 'Недопустимое значение', title='Warning').open()
    elif FORMS_SEPARATOR in _new_v:
        PopupMsgW(_window, f'Недопустимый символ: {FORMS_SEPARATOR}', title='Warning').open()
    else:
        _vals += [_new_v]


# Удалить значение параметра форм
def delete_frm_param_val(_window, _vals, _dct):
    _val = PopupChooseW(_window, _vals).open()
    if _val == '':
        return
    _window_dia = PopupDialogueW(_window, 'Все формы слов, содержащие это значение, будут удалены!\nВы уверены?')
    _answer = _window_dia.open()
    if _answer:
        _index = _vals.index(_val)
        _vals.pop(_index)
        _dct.remove_forms_with_val(_index, _val)


# Переименовать значение параметра форм
def rename_frm_param_val(_window, _vals, _pos, _dct):
    _val = PopupChooseW(_window, _vals).open()
    if _val == '':
        return
    while True:
        _new_val = PopupEntryW(_window, 'Введите новое название для значения параметра').open()
        if _new_val == '':
            PopupMsgW(_window, 'Недопустимое название значения', title='Warning').open()
            continue
        if _new_val in _vals:
            PopupMsgW(_window, 'Значение с таким названием уже есть', title='Warning').open()
            continue
        break
    _dct.rename_forms_with_val(_pos, _val, _new_val)
    _index = _vals.index(_val)
    _vals[_index] = _new_val


# Найти в строке подстроку и выделить её
def find_and_highlight(_wrd, _search_wrd):
    _len = len(_search_wrd)
    if _wrd != _search_wrd:
        _pos = deu_to_eng(_wrd).lower().find(deu_to_eng(_search_wrd).lower())
        if _pos != -1:
            _coded_wrd = code(_wrd)
            _end = _pos + _len
            if _search_wrd == '':
                _res = f'{_coded_wrd}'
            else:
                _res = f'{_coded_wrd[:_pos]}[{_coded_wrd[_pos:_end]}]{_coded_wrd[_end:]}'
            return _res
    return ''


class Entry(object):
    # self.wrd - слово
    # self.tr - переводы
    # self.notes - сноски
    # self.forms - формы слова
    # self.count_t - количество переводов
    # self.count_n - количество сносок
    # self.count_f - количество форм слова
    # self.fav - избранное
    # self.all_att - количество всех попыток
    # self.correct_att - количество удачных попыток
    # self.score - доля удачных попыток
    # self.last_att - количество последних неудачных попыток (-1 - значит ещё не было попыток)
    def __init__(self, _wrd, _tr, _notes=None, _forms=None, _fav=False, _all_att=0, _correct_att=0, _last_att=-1):
        self.wrd = _wrd
        self.tr = _tr.copy() if (type(_tr) == list) else [_tr]
        if _notes is None:
            self.notes = []
        elif type(_notes) == list:
            self.notes = _notes.copy()
        else:
            self.notes = [_notes]
        self.forms = {}
        if type(_forms) == dict:
            self.forms = dict(_forms.copy())
        self.count_t = len(self.tr)
        self.count_n = len(self.notes)
        self.count_f = len(self.forms)
        self.fav = _fav
        self.all_att = _all_att
        self.correct_att = _correct_att
        self.score = _correct_att / _all_att if (_all_att != 0) else 0
        self.last_att = _last_att

    # Записать переводы в строку
    def tr_to_str(self):
        _res = ''
        if self.count_t != 0:
            _res += f'> {code(self.tr[0])}'
        for _i in range(1, self.count_t):
            _res += f'\n> {code(self.tr[_i])}'
        return _res

    # Записать сноски в строку
    def notes_to_str(self):
        _res = ''
        if self.count_n != 0:
            _res += f'> {code(self.notes[0])}'
        for _i in range(1, self.count_n):
            _res += f'\n> {code(self.notes[_i])}'
        return _res

    # Записать формы в строку
    def frm_to_str(self):
        _keys = list(self.forms.keys())
        _res = ''
        if self.count_f != 0:
            _res += f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}'
        for _i in range(1, self.count_f):
            _res += f'\n[{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}'
        return _res

    # Напечатать перевод
    def tr_print(self, _output_widget, _end='\n'):
        if self.count_t != 0:
            outp(_output_widget, code(self.tr[0]), _end='')
        for _i in range(1, self.count_t):
            outp(_output_widget, f', {code(self.tr[_i])}', _end='')
        outp(_output_widget, '', _end=_end)

    # Напечатать сноски
    def notes_print(self, _output_widget, _tab=0):
        for _i in range(self.count_n):
            outp(_output_widget, ' ' * _tab + f'> {code(self.notes[_i])}')

    # Напечатать формы слова
    def frm_print(self, _output_widget, _tab=0):
        for _key in self.forms.keys():
            outp(_output_widget, ' ' * _tab + f'[{tpl(_key)}] {code(self.forms[_key])}')

    # Напечатать статистику
    def stat_print(self, _output_widget, _min_good_score_perc, _end='\n'):
        if self.last_att == -1:
            outp(_output_widget, '[-:  0%]', _end=_end)
        else:
            _score = '{:.0%}'.format(self.score)
            _tab = ' ' * (4 - len(_score))
            outp(_output_widget, f'[{self.last_att}:{_tab}{_score}]', _end=_end)

    # Служебный метод для print_briefly и print_briefly_with_forms
    def _print_briefly(self, _output_widget, _min_good_score_perc):
        if self.fav:
            outp(_output_widget, '(*)', _end=' ')
        else:
            outp(_output_widget, '   ', _end=' ')
        self.stat_print(_output_widget, _min_good_score_perc, _end=' ')
        outp(_output_widget, f'{code(self.wrd)}: ', _end='')
        self.tr_print(_output_widget)

    # Напечатать статью - кратко
    def print_briefly(self, _output_widget, _min_good_score_perc):
        self._print_briefly(_output_widget, _min_good_score_perc)
        self.notes_print(_output_widget, _tab=13)

    # Напечатать статью - кратко с формами
    def print_briefly_with_forms(self, _output_widget, _min_good_score_perc):
        self._print_briefly(_output_widget, _min_good_score_perc)
        self.frm_print(_output_widget, _tab=13)
        self.notes_print(_output_widget, _tab=13)

    # Напечатать статью - слово со статистикой
    def print_wrd_with_stat(self, _output_widget, _min_good_score_perc):
        outp(_output_widget, code(self.wrd), _end=' ')
        self.stat_print(_output_widget, _min_good_score_perc)

    # Напечатать статью - перевод со статистикой
    def print_tr_with_stat(self, _output_widget, _min_good_score_perc):
        self.tr_print(_output_widget, _end=' ')
        self.stat_print(_output_widget, _min_good_score_perc)

    # Напечатать статью - перевод с формой и со статистикой
    def print_tr_and_frm_with_stat(self, _output_widget, _frm_key, _min_good_score_perc):
        self.tr_print(_output_widget, _end=' ')
        outp(_output_widget, f'({tpl(_frm_key)})', _end=' ')
        self.stat_print(_output_widget, _min_good_score_perc)

    # Напечатать статью - со всей информацией
    def print_all(self, _output_widget):
        outp(_output_widget, f'       Слово: {code(self.wrd)}')
        outp(_output_widget, '     Перевод: ', _end='')
        self.tr_print(_output_widget)
        outp(_output_widget, ' Формы слова: ', _end='')
        if self.count_f == 0:
            outp(_output_widget, '-')
        else:
            _keys = [_key for _key in self.forms.keys()]
            outp(_output_widget, f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}')
            for _i in range(1, self.count_f):
                outp(_output_widget, f'              [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        outp(_output_widget, '      Сноски: ', _end='')
        if self.count_n == 0:
            outp(_output_widget, '-')
        else:
            outp(_output_widget, f'> {code(self.notes[0])}')
            for _i in range(1, self.count_n):
                outp(_output_widget, f'              > {code(self.notes[_i])}')
        outp(_output_widget, f'   Избранное: {self.fav}')
        if self.last_att == -1:
            outp(_output_widget, '  Статистика: 1) Последних неверных ответов: -')
            outp(_output_widget, '              2) Доля верных ответов: 0')
        else:
            outp(_output_widget, f'  Статистика: 1) Последних неверных ответов: {self.last_att}')
            outp(_output_widget, f'              2) Доля верных ответов: '
                 f'{self.correct_att}/{self.all_att} = ' + '{:.0%}'.format(self.score))

    # Добавить перевод
    def add_tr(self, _new_tr, _window=None):
        if _new_tr not in self.tr:
            self.tr += [_new_tr]
            self.count_t += 1
        elif _window:
            PopupMsgW(_window, 'У этого слова уже есть такой перевод', title='Warning')

    # Добавить сноску
    def add_note(self, _new_note):
        self.notes += [_new_note]
        self.count_n += 1

    # Добавить форму слова
    def add_frm(self, _frm_key, _new_frm, _window=None):
        if _new_frm == '':
            PopupMsgW(_window, 'Форма должна содержать хотя бы один символ', title='Warning')
        elif _frm_key not in self.forms.keys():
            self.forms[_frm_key] = _new_frm
            self.count_f += 1
        elif _window:
            PopupMsgW(_window, f'Слово уже имеет форму с такими параметрами {tpl(_frm_key)}: {self.forms[_frm_key]}', title='Warning')

    # Удалить форму слова
    def remove_frm_with_choose(self, _window):
        _keys = [_key for _key in self.forms.keys()]
        _variants = [f'[{tpl(_key)}] {code(self.forms[_key])}' for _key in _keys]

        _window_choose = PopupChooseW(_window, _variants, 'Выберите форму, которую хотите удалить')
        _answer = _window_choose.open()
        if _answer == '':
            return
        _index = _variants.index(_answer)
        _key = _keys[_index]
        self.forms.pop(_key)
        self.count_f -= 1

    # Изменить форму слова
    def edit_frm_with_choose(self, _window):
        _keys = [_key for _key in self.forms.keys()]
        _variants = [f'[{tpl(_key)}] {code(self.forms[_key])}' for _key in _keys]

        _window_choose = PopupChooseW(_window, _variants, 'Выберите форму, которую хотите изменить')
        _answer = _window_choose.open()
        if _answer == '':
            return
        _index = _variants.index(_answer)
        _key = _keys[_index]

        _window_entry = PopupEntryW(_window, 'Введите форму слова')
        _new_frm = _window_entry.open()
        if _new_frm == '':
            PopupMsgW(_window, 'Форма должна содержать хотя бы один символ', title='Warning')
            return
        self.forms[_key] = _new_frm

    # Объединить статистику при объединении двух статей
    def merge_stat(self, _all_att, _correct_att, _last_att):
        self.all_att += _all_att
        self.correct_att += _correct_att
        self.score = self.correct_att / self.all_att if (self.all_att != 0) else 0
        self.last_att += _last_att

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

    # Удалить данное значение параметра у всех форм слова
    def remove_forms_with_val(self, _pos, _frm_val):
        _to_remove = []
        for _key in self.forms.keys():
            if _key[_pos] == _frm_val:
                _to_remove += [_key]
                self.count_f -= 1
        for _key in _to_remove:
            self.forms.pop(_key)

    # Переименовать данное значение параметра у всех форм слова
    def rename_forms_with_val(self, _pos, _frm_val, _new_frm_val):
        _to_rename = []
        for _key in self.forms.keys():
            if _key[_pos] == _frm_val:
                _to_rename += [_key]
        for _key in _to_rename:
            _lst = list(_key)
            _lst[_pos] = _new_frm_val
            _lst = tuple(_lst)
            self.forms[_lst] = self.forms[_key]
            self.forms.pop(_key)

    # Добавить данный параметр ко всем формам слова
    def add_forms_param(self):
        _keys = list(self.forms.keys())
        for _key in _keys:
            _new_key = list(_key)
            _new_key += ['']
            _new_key = tuple(_new_key)
            self.forms[_new_key] = self.forms[_key]
            self.forms.pop(_key)

    # Удалить данный параметр у всех форм слова
    def remove_forms_param(self, _pos):
        _to_remove = []
        _to_edit = []
        for _key in self.forms.keys():
            if _key[_pos] != '':
                _to_remove += [_key]
                self.count_f -= 1
            else:
                _to_edit += [_key]
        for _key in _to_edit:
            _new_key = list(_key)
            _new_key.pop(_pos)
            _new_key = tuple(_new_key)
            self.forms[_new_key] = self.forms[_key]
            self.forms.pop(_key)
        for _key in _to_remove:
            self.forms.pop(_key)

    # Переименовать данный параметр у всех форм слова
    """ def rename_forms_param(self, _pos): """

    # Сохранить статью в файл
    def save(self, _file):
        _file.write(f'w{self.wrd}\n')
        _file.write(f'{self.all_att}#{self.correct_att}#{self.last_att}\n')
        _file.write(f'{self.tr[0]}\n')
        for _i in range(1, self.count_t):
            _file.write(f't{self.tr[_i]}\n')
        for _note in self.notes:
            _file.write(f'd{_note}\n')
        for _frm_key in self.forms.keys():
            _file.write(f'f{code_tpl(_frm_key)}\n{self.forms[_frm_key]}\n')
        if self.fav:
            _file.write('*\n')


MAX_SAME_WORDS = 100  # Максимальное количество статей с одинаковым словом


# Перевести слово из статьи в ключ для словаря
def wrd_to_key(_wrd, _num):
    return str(_num // 10) + str(_num % 10) + _wrd


# Перевести ключ для словаря в слово из статьи
def key_to_wrd(_key):
    return _key[2:]


# Выбрать окончание слова в зависимости от количественного числительного
def set_postfix(_n, _wrd_forms):
    if 5 <= _n % 100 <= 20:
        return _wrd_forms[2]
    elif _n % 10 == 1:
        return _wrd_forms[0]
    elif 1 < _n % 10 < 5:
        return _wrd_forms[1]
    else:
        return _wrd_forms[2]


class Dictionary(object):
    # self.d - сам словарь
    # self.count_w - количество статей (слов) в словаре
    # self.count_t - количество переводов в словаре
    # self.count_f - количество неначальных словоформ в словаре
    def __init__(self):
        self.d = {}
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0

    # Служебный метод для print и print_with_forms
    def _print_stat(self, _output_widget):
        _w = set_postfix(self.count_w, ('слово', 'слова', 'слов'))
        _f = set_postfix(self.count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        _t = set_postfix(self.count_t, ('перевод', 'перевода', 'переводов'))
        outp(_output_widget, f'\n< {self.count_w} {_w} | {self.count_w + self.count_f} {_f} | {self.count_t} {_t} >')

    # Напечатать словарь
    def print(self, _output_widget, _min_good_score_perc):
        for _entry in self.d.values():
            _entry.print_briefly(_output_widget, _min_good_score_perc)
        self._print_stat(_output_widget)

    # Напечатать словарь (со всеми формами)
    def print_with_forms(self, _output_widget, _min_good_score_perc):
        for _entry in self.d.values():
            _entry.print_briefly_with_forms(_output_widget, _min_good_score_perc)
        self._print_stat(_output_widget)

    # Служебный метод для print_fav и print_fav_with_forms
    def _print_stat_fav(self, _output_widget, _count_w, _count_t, _count_f):
        _w = set_postfix(_count_w, ('слово', 'слова', 'слов'))
        _f = set_postfix(_count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        _t = set_postfix(_count_t, ('перевод', 'перевода', 'переводов'))
        outp(_output_widget,
             f'\n< {_count_w}/{self.count_w} {_w} | '
             f'{_count_w + _count_f}/{self.count_w + self.count_f} {_f} | '
             f'{_count_t}/{self.count_t} {_t} >')

    # Напечатать словарь (только избранные слова)
    def print_fav(self, _output_widget, _min_good_score_perc):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _entry in self.d.values():
            if _entry.fav:
                _entry.print_briefly(_output_widget, _min_good_score_perc)
                _count_w += 1
                _count_t += _entry.count_t
                _count_f += _entry.count_f
        self._print_stat_fav(_output_widget, _count_w, _count_t, _count_f)

    # Напечатать словарь (только избранные слова, со всеми формами)
    def print_fav_with_forms(self, _output_widget, _min_good_score_perc):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _entry in self.d.values():
            if _entry.fav:
                _entry.print_briefly_with_forms(_output_widget, _min_good_score_perc)
                _count_w += 1
                _count_t += _entry.count_t
                _count_f += _entry.count_f
        self._print_stat_fav(_output_widget, _count_w, _count_t, _count_f)

    # Напечатать статьи, в которых слова содержат данную строку
    def print_words_with_str(self, _output_widget, _search_wrd):
        _is_found = False
        for _key in self.d.keys():
            _wrd = key_to_wrd(_key)
            _res = find_and_highlight(_wrd, _search_wrd)
            if _res != '':
                _is_found = True
                outp(_output_widget, _res)
        if not _is_found:
            outp(_output_widget, 'Частичных совпадений не найдено')

    # Напечатать статьи, в которых переводы содержат данную строку
    def print_translations_with_str(self, _output_widget, _search_tr):
        _is_found = False
        for _entry in self.d.values():
            _is_first = True
            for _tr in _entry.tr:
                _res = find_and_highlight(_tr, _search_tr)
                if _res != '':
                    if _is_first:
                        _is_first = False
                        if _is_found:
                            outp(_output_widget)
                    else:
                        outp(_output_widget, ', ', _end='')
                    _is_found = True
                    outp(_output_widget, _res, _end='')
        if not _is_found:
            outp(_output_widget, 'Частичных совпадений не найдено')
        else:
            outp(_output_widget)

    # Выбрать одну статью из нескольких с одинаковыми словами
    def choose_one_of_similar_entries(self, _window, _wrd):
        if wrd_to_key(_wrd, 1) not in self.d.keys():
            return wrd_to_key(_wrd, 0)
        _window_note = ChooseNoteW(_window, _wrd)
        _answer = _window_note.open()
        return _answer

    # Добавить перевод к статье
    def add_tr(self, _key_or_wrd, _tr, _window=None, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_window, _key_or_wrd)
        self.count_t -= self.d[_key].count_t
        self.d[_key].add_tr(_tr, _window=_window)
        self.count_t += self.d[_key].count_t

    # Добавить сноску к статье
    def add_note(self, _key, _note):
        self.d[_key].add_note(_note)

    # Добавить форму слова к статье
    def add_frm(self, _key_or_wrd, _frm_key, _frm, _window=None, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_window, _key_or_wrd)
        self.count_f -= self.d[_key].count_f
        self.d[_key].add_frm(_frm_key, _frm, _window=_window)
        self.count_f += self.d[_key].count_f

    # Изменить слово в статье
    def edit_wrd(self, _window, _key, _new_wrd):
        if wrd_to_key(_new_wrd, 0) in self.d.keys():  # Если уже есть статья с таким словом

            window = PopupDialogueW(_window, 'Статья с таким словом уже есть в словаре\nЧто вы хотите сделать?',
                                    'Добавить к существующей статье', 'Создать новую статью',
                                    st_left='std', st_right='std', val_left='l', val_right='r', val_initial='i')
            _answer = window.open()
            if _answer == 'l':
                _new_key = self.choose_one_of_similar_entries(_window, _new_wrd)

                self.count_t -= self.d[_key].count_t
                self.count_t -= self.d[_new_key].count_t
                self.count_f -= self.d[_key].count_f
                self.count_f -= self.d[_new_key].count_f

                for _tr in self.d[_key].tr:
                    self.d[_new_key].add_tr(_tr)
                for _note in self.d[_key].notes:
                    self.d[_new_key].add_note(_note)
                for _frm_key in self.d[_key].forms.keys():
                    _frm = self.d[_key].forms[_frm_key]
                    self.d[_new_key].add_form(_frm_key, _frm, False)
                if self.d[_key].fav:
                    self.d[_new_key].fav = True
                self.d[_new_key].merge_stat(self.d[_key].all_att, self.d[_key].correct_att, self.d[_key].last_att)

                self.count_w -= 1
                self.count_t += self.d[_new_key].count_t
                self.count_f += self.d[_new_key].count_f

                self.d.pop(_key)
                return _new_key
            elif _answer == 'r':
                for _i in range(MAX_SAME_WORDS):
                    _new_key = wrd_to_key(_new_wrd, _i)
                    if _new_key not in self.d.keys():
                        self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                                 self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                                 self.d[_key].last_att)
                        self.d.pop(_key)
                        return _new_key
                    _i += 1
                PopupMsgW(_window, 'Слишком много статей с одинаковым словом', title='Warning')
            else:
                return None
        else:  # Если ещё нет статьи с таким словом
            _new_key = wrd_to_key(_new_wrd, 0)
            self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                     self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                     self.d[_key].last_att)
            self.d.pop(_key)
            return _new_key

    # Изменить форму слова в статье
    def edit_frm_with_choose(self, _window, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.d[_key].edit_frm_with_choose(_window)

    # Удалить перевод в статье
    def remove_tr_with_choose(self, _window, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_window, _key_or_wrd)
        self.count_t -= self.d[_key].count_t
        _window_choose = PopupChooseW(_window, self.d[_key].tr, 'Выберите, какой перевод хотите удалить')
        _cmd = _window_choose.open()
        if not _cmd:
            return
        self.d[_key].tr.remove(_cmd)
        self.d[_key].count_t -= 1
        self.count_t += self.d[_key].count_t

    # Удалить описание в статье
    def remove_note_with_choose(self, _window, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_window, _key_or_wrd)
        _window_choose = PopupChooseW(_window, self.d[_key].notes, 'Выберите, какую сноску хотите удалить')
        _cmd = _window_choose.open()
        if not _cmd:
            return
        self.d[_key].notes.remove(_cmd)
        self.d[_key].count_n -= 1

    # Удалить форму слова в статье
    def remove_frm_with_choose(self, _window, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_f -= self.d[_key].count_f
        self.d[_key].remove_frm_with_choose(_window)
        self.count_f += self.d[_key].count_f

    # Добавить статью в словарь (для пользователя)
    def add_entry(self, _window, _wrd, _tr):
        if wrd_to_key(_wrd, 0) in self.d.keys():  # Если уже есть статья с таким словом
            while True:
                window = PopupDialogueW(_window, 'Статья с таким словом уже есть в словаре\nЧто вы хотите сделать?',
                                        'Добавить к существующей статье', 'Создать новую статью',
                                        st_left='std', st_right='std', val_left='l', val_right='r', val_initial='i')
                _answer = window.open()
                if _answer == 'l':
                    _key = self.choose_one_of_similar_entries(_window, _wrd)
                    self.add_tr(_key, _tr, _window=_window, _is_key=True)
                    return _key
                elif _answer == 'r':
                    for _i in range(MAX_SAME_WORDS):
                        _key = wrd_to_key(_wrd, _i)
                        if _key not in self.d.keys():
                            self.d[_key] = Entry(_wrd, [_tr])
                            self.count_w += 1
                            self.count_t += 1
                            return _key
                        _i += 1
                    PopupMsgW(_window, 'Слишком много статей с одинаковым словом', title='Warning')
                else:
                    return None
        else:  # Если ещё нет статьи с таким словом
            _key = wrd_to_key(_wrd, 0)
            self.d[_key] = Entry(_wrd, [_tr])
            self.count_w += 1
            self.count_t += 1
            return _key

    # Добавить статью в словарь (при чтении файла)
    def load_entry(self, _wrd, _tr, _all_att, _correct_att, _last_att):
        for _i in range(MAX_SAME_WORDS):
            _key = wrd_to_key(_wrd, _i)
            if _key not in self.d.keys():
                self.d[_key] = Entry(_wrd, [_tr], _all_att=_all_att, _correct_att=_correct_att, _last_att=_last_att)
                self.count_w += 1
                self.count_t += 1
                return _key
            _i += 1

    # Удалить статью
    def remove_entry(self, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_w -= 1
        self.count_t -= self.d[_key].count_t
        self.count_f -= self.d[_key].count_f
        self.d.pop(_key)

    # Удалить данное значение параметра у всех форм
    def remove_forms_with_val(self, _pos, _frm_val):
        for _entry in self.d.values():
            self.count_f -= _entry.count_f
            _entry.remove_forms_with_val(_pos, _frm_val)
            self.count_f += _entry.count_f

    # Переименовать данное значение параметра у всех форм
    def rename_forms_with_val(self, _pos, _frm_val, _new_frm_val):
        for _entry in self.d.values():
            _entry.rename_forms_with_val(_pos, _frm_val, _new_frm_val)

    # Добавить данный параметр ко всем словоформам
    def add_forms_param(self):
        for _entry in self.d.values():
            _entry.add_forms_param()

    # Удалить данный параметр у всех словоформ
    def remove_forms_param(self, _pos):
        for _entry in self.d.values():
            self.count_f -= _entry.count_f
            _entry.remove_forms_param(_pos)
            self.count_f += _entry.count_f

    # Переименовать данный параметр у всех словоформ
    """def rename_forms_param(self, _pos):
        for _entry in self.d.values():
            _entry.rename_frm_param(_pos)"""

    # Подсчитать среднюю долю правильных ответов
    def count_rating(self):
        _sum_num = 0
        _sum_den = 0
        for _entry in self.d.values():
            _sum_num += _entry.correct_att
            _sum_den += _entry.all_att
        if _sum_den == 0:
            return 0
        return _sum_num / _sum_den

    # Выбор случайного слова с учётом сложности
    def random_hard(self, _min_good_score_perc):
        _sum = 0
        for _entry in self.d.values():
            _sum += (100 - round(100 * _entry.score)) * 7 + 1
            if _entry.all_att < 5:
                _sum += (5 - _entry.all_att) * 20
            if 100 * _entry.score < _min_good_score_perc:
                _sum += 100
        _r = random.randint(1, _sum)

        for _key in self.d.keys():
            _r -= (100 - round(100 * self.d[_key].score)) * 7 + 1
            if self.d[_key].all_att < 5:
                _r -= (5 - self.d[_key].all_att) * 20
            if 100 * self.d[_key].score < _min_good_score_perc:
                _r -= 100
            if _r <= 0:
                return _key

    # Сохранить словарь в файл
    def save(self, _filename):
        with open(_filename, 'w') as _file:
            for _entry in self.d.values():
                _entry.save(_file)

    # Прочитать словарь из файла
    def read(self, _filename):
        try:
            with open(_filename, 'r') as _file:
                while True:
                    _line = _file.readline().strip()
                    if not _line:
                        break
                    elif _line[0] == 'w':
                        _wrd = _line[1:]
                        _all_att, _correct_att, _last_att = (int(_i) for _i in _file.readline().strip().split('#'))
                        _tr = _file.readline().strip()
                        _key = self.load_entry(_wrd, _tr, _all_att, _correct_att, _last_att)
                    elif _line[0] == 't':
                        self.add_tr(_key, _line[1:], _is_key=True)
                    elif _line[0] == 'd':
                        self.add_note(_key, _line[1:])
                    elif _line[0] == 'f':
                        _frm_key = decode_tpl(_line[1:])
                        self.add_frm(_key, _frm_key, _file.readline().strip(), _is_key=True)
                    elif _line[0] == '*':
                        self.d[_key].fav = True
            return 0
        except FileNotFoundError:
            return 1
        except (ValueError, TypeError):
            return 2
        except Exception:
            return 3


# Загрузить настройки словаря из файла
def read_local_settings(_filename):
    _local_settings_fn = os.path.join(LOCAL_SETTINGS_PATH, _filename)
    try:  # Проверка наличия файла
        open(_local_settings_fn, 'r')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(_local_settings_fn, 'w') as _loc_set_file:
            _loc_set_file.write('67\n'
                                'Число\n'
                                f'ед.ч.{FORMS_SEPARATOR}мн.ч.\n'
                                'Род\n'
                                f'м.р.{FORMS_SEPARATOR}ж.р.{FORMS_SEPARATOR}ср.р.\n'
                                'Падеж\n'
                                f'им.п.{FORMS_SEPARATOR}род.п.{FORMS_SEPARATOR}дат.п.{FORMS_SEPARATOR}вин.п.\n'
                                'Лицо\n'
                                f'1 л.{FORMS_SEPARATOR}2 л.{FORMS_SEPARATOR}3 л.\n'
                                'Время\n'
                                f'пр.вр.{FORMS_SEPARATOR}н.вр.{FORMS_SEPARATOR}буд.вр.')

    _form_parameters = {}
    with open(_local_settings_fn, 'r') as _loc_set_file:
        _min_good_score_perc = int(_loc_set_file.readline().strip())
        while True:
            _key = _loc_set_file.readline().strip()
            if not _key:
                break
            _value = _loc_set_file.readline().strip().split(FORMS_SEPARATOR)
            _form_parameters[_key] = _value
    return _min_good_score_perc, _form_parameters


# Сохранить настройки словаря
def save_local_settings(_min_good_score_perc, _form_parameters, _filename):
    _local_settings_fn = os.path.join(LOCAL_SETTINGS_PATH, _filename)
    with open(_local_settings_fn, 'w') as _loc_set_file:
        _loc_set_file.write(f'{_min_good_score_perc}\n')
        for _key in _form_parameters.keys():
            _loc_set_file.write(f'{_key}\n')
            _loc_set_file.write(_form_parameters[_key][0])
            for _i in range(1, len(_form_parameters[_key])):
                _loc_set_file.write(f'{FORMS_SEPARATOR}{_form_parameters[_key][_i]}')
            _loc_set_file.write('\n')


# Загрузить словарь и его настройки из файлов
def read_dct(_window, _dct, _savename):
    global dct_savename

    _filename = f'{_savename}.txt'
    _filepath = os.path.join(SAVES_PATH, _filename)
    _res_code = _dct.read(_filepath)
    if _res_code == 0:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'\nСловарь "{_savename}" успешно открыт')
        return read_local_settings(_filename)
    elif _res_code == 1:  # Если файл отсутствует, то создаётся пустой словарь
        print(f'\nСловарь "{_savename}" не найден!')
        open(_filepath, 'w')
        _dct.read(_filepath)
        print('Создан и загружен пустой словарь')
        return read_local_settings(_filename)
    else:  # Если файл повреждён, то предлагается открыть другой файл
        print(f'\nФайл со словарём "{_savename}" повреждён или некорректен!')
        _window_dia = PopupDialogueW(_window, f'Файл со словарём "{_savename}" повреждён или некорректен!\n'
                                              f'Хотите открыть другой словарь?', 'Да', 'Завершить работу',
                                     val_left='l', val_right='r', val_initial='i')
        _answer = _window_dia.open()
        if _answer == 'l':
            _window_entry = PopupEntryW(_window, 'Введите название словаря\n'
                                                 '(если он ещё не существует, то будет создан пустой словарь)')
            dct_savename = _window_entry.open()
            with open(SETTINGS_PATH, 'w') as _settings_file:
                _settings_file.write(dct_savename)
            _dct = Dictionary()
            return read_dct(_window, _dct, dct_savename)
        else:
            exit()


# Создать и загрузить пустой словарь
def create_dct(_dct, _savename):
    _filename = f'{_savename}.txt'
    _filepath = os.path.join(SAVES_PATH, _filename)
    open(_filepath, 'w')
    _dct.read(_filepath)
    print(f'\nСловарь "{_savename}" успешно создан и открыт')
    return read_local_settings(_filename)


# Сохранить словарь и его настройки
def save_all(_dct, _min_good_score_perc, _form_parameters, _filename):
    _filepath = os.path.join(SAVES_PATH, _filename)
    _dct.save(_filepath)
    save_local_settings(_min_good_score_perc, _form_parameters, _filename)


# Предложить сохранение, если были изменения
def save_if_has_changes(_window, _dct, _min_good_score_perc, _form_parameters, _filename):
    _window_dia = PopupDialogueW(_window, 'Хотите сохранить изменения и свой прогресс?', 'Да', 'Нет')
    _answer = _window_dia.open()
    if _answer:
        save_all(_dct, _min_good_score_perc, _form_parameters, _filename)
        PopupMsgW(_window, 'Изменения и прогресс успешно сохранены')
        print('\nИзменения и прогресс успешно сохранены')


# Добавить параметр словоформ
def add_frm_param(_window, _parameters, _dct):
    window = EnterFormParameterNameW(_window, _parameters.keys())
    _name_is_correct, _new_p = window.open()
    if not _name_is_correct:
        return
    _dct.add_forms_param()
    _parameters[_new_p] = []
    while not _parameters[_new_p]:
        add_frm_param_val(_window, _parameters[_new_p], 'Необходимо добавить хотя бы одно значение для параметра')


# Удалить параметр словоформ
def remove_frm_param(_window, _parameters, _dct):
    _keys = [_key for _key in _parameters.keys()]
    _key = PopupChooseW(_window, _keys, btn_text='Удалить').open()
    if _key == '':
        return
    _window = PopupDialogueW(_window, 'Все формы слов, содержащие этот параметр, будут удалены!\nВы уверены?')
    _answer = _window.open()
    if _answer:
        _pos = _keys.index(_key)
        _parameters.pop(_key)
        _dct.remove_forms_param(_pos)


# Переименовать параметр словоформ
def rename_frm_param(_window, _parameters, _dct):
    _keys = [_key for _key in _parameters.keys()]
    _key = PopupChooseW(_window, _keys, btn_text='Переименовать').open()
    if _key == '':
        return
    while True:
        _new_key = PopupEntryW(_window, 'Введите новое название параметра').open()
        if _new_key == '':
            PopupMsgW(_window, 'Недопустимое название параметра', title='Warning').open()
            continue
        if _new_key in _parameters:
            PopupMsgW(_window, 'Параметр с таким названием уже есть', title='Warning').open()
            continue
        break
    # _dct.rename_forms_param(_index)
    _parameters[_new_key] = _parameters[_key]
    _parameters.pop(_key)


# Ввод только целых чисел от 0 до max
def validate_int_max(value, max):
    return value == '' or value.isnumeric() and int(value) <= max


# Ввод только целых чисел от 0 до 100
def validate_percent(value):
    return validate_int_max(value, 100)


# При выборе второго способа учёбы, нельзя добавить словоформы
def validate_order_and_forms(value, check_forms):
    print(value)
    if value == VALUES_ORDER[1]:
        check_forms['state'] = 'disabled'
    else:
        check_forms['state'] = 'normal'
    return True


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg, btn_text='Ясно', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[st])

        tk.Label( self, text=msg,      bg=ST_BG[st],  fg=ST_FG_TEXT[st]).grid(row=0, column=0, padx=6, pady=4)
        tk.Button(self, text=btn_text, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st], command=self.destroy).grid(row=1, column=0, padx=6, pady=4)

    def open(self):
        self.grab_set()
        self.wait_window()


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Вы уверены?', btn_left='Да', btn_right='Отмена', st_left='yes', st_right='no', val_left=True, val_right=False, val_initial=False, title=PROGRAM_NAME):
        ALLOWED_ST_VALUES = ['std', 'yes', 'no']
        assert st_left  in ALLOWED_ST_VALUES, f'Bad value: st_left\nAllowed values: {ALLOWED_ST_VALUES}'
        assert st_right in ALLOWED_ST_VALUES, f'Bad value: st_right\nAllowed values: {ALLOWED_ST_VALUES}'

        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[st])

        self.answer = val_initial
        self.val_left  = val_left
        self.val_right = val_right

        if st_left == 'std':
            self.left_bg = ST_BTN[st]
            self.left_activebackground = ST_BTN_SELECT[st]
        elif st_left == 'yes':
            self.left_bg = ST_BTNY[st]
            self.left_activebackground = ST_BTNY_SELECT[st]
        elif st_left == 'no':
            self.left_bg = ST_BTNN[st]
            self.left_activebackground = ST_BTNN_SELECT[st]

        if st_right == 'std':
            self.right_bg = ST_BTN[st]
            self.right_activebackground = ST_BTN_SELECT[st]
        elif st_right == 'yes':
            self.right_bg = ST_BTNY[st]
            self.right_activebackground = ST_BTNY_SELECT[st]
        elif st_right == 'no':
            self.right_bg = ST_BTNN[st]
            self.right_activebackground = ST_BTNN_SELECT[st]

        tk.Label( self, text=msg,                           bg=ST_BG[st],     fg=ST_FG_TEXT[st]).grid(row=0, columnspan=2, padx=6, pady=4)
        tk.Button(self, text=btn_left,  command=self.left,  bg=self.left_bg,  fg=ST_FG_TEXT[st], activebackground=self.left_activebackground,  highlightbackground=ST_BORDER[st]).grid(row=1, column=0, padx=(6, 10), pady=4, sticky='E')
        tk.Button(self, text=btn_right, command=self.right, bg=self.right_bg, fg=ST_FG_TEXT[st], activebackground=self.right_activebackground, highlightbackground=ST_BORDER[st]).grid(row=1, column=1, padx=(10, 6), pady=4, sticky='W')

    # Нажатие на левую кнопку
    def left(self):
        self.answer = self.val_left
        self.destroy()

    # Нажатие на правую кнопку
    def right(self):
        self.answer = self.val_right
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.answer


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values, msg='Выберите один из вариантов', btn_text='Подтвердить', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[st])

        self.var_answer = tk.StringVar()

        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])

        tk.Label(self, text=msg, bg=ST_BG[st], fg=ST_FG_TEXT[st]).grid(row=0, padx=6, pady=(4, 1))
        ttk.Combobox(self, textvariable=self.var_answer, style='.TCombobox', values=values, state='readonly').grid(row=1, padx=6, pady=1)
        tk.Button(self, text=btn_text, bg=ST_BTNY[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNY_SELECT[st], highlightbackground=ST_BORDER[st], command=self.destroy).grid(row=2, padx=6, pady=4)

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.var_answer.get()


# Всплывающее окно с полем ввода и кнопкой
class PopupEntryW(tk.Toplevel):
    def __init__(self, parent, msg='Введите строку', btn_text='Подтвердить', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[st])

        self.var_text = tk.StringVar()

        tk.Label(self, text=f'{msg}:', bg=ST_BG[st], fg=ST_FG_TEXT[st]).grid(row=0, column=0, padx=(6, 1), pady=(6, 0))
        tk.Entry(self, textvariable=self.var_text, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], selectbackground=ST_SELECT[st], highlightcolor=ST_HIGHLIGHT[st]).grid(row=0, column=1, padx=(0, 6), pady=(6, 0))
        tk.Button(self, text=btn_text, command=self.destroy, bg=ST_BTNY[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNY_SELECT[st], highlightbackground=ST_BORDER[st]).grid(row=1, columnspan=2, padx=6, pady=6)

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.var_text.get()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseNoteW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME}')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.max = -1
        self.wrd = wrd
        self.answer = wrd_to_key(self.wrd, 0)

        self.var_input = tk.StringVar()

        self.vcmd_max = (self.register(lambda value: validate_int_max(value, self.max)), '%P')

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_input   = tk.Label( self.frame_main, text='Выберите одну из статей:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.entry_input = tk.Entry( self.frame_main, textvariable=self.var_input, width=5, relief='solid', validate='key', vcmd=self.vcmd_max, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.btn_choose  = tk.Button(self.frame_main, text='Выбор', command=self.choose, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # }
        self.scrollbar   = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_words  = tk.Text(     self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])

        self.frame_main.grid( row=0, columnspan=2, padx=6, pady=6)
        # {
        self.lbl_input.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.btn_choose.grid( row=0, column=2, padx=6,      pady=6)
        # }
        self.text_words.grid( row=1, column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(  row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')

        self.scrollbar.config(command=self.text_words.yview)

        self.print_variants()

    # Вывести варианты статей
    def print_variants(self):
        self.text_words['state'] = 'normal'
        self.max = MAX_SAME_WORDS - 1
        for _i in range(MAX_SAME_WORDS):
            _key = wrd_to_key(self.wrd, _i)
            if _key not in dct.d.keys():
                self.max = _i - 1
                break
            outp(self.text_words, f'\n({_i})')
            dct.d[_key].print_all(self.text_words)
        self.text_words['state'] = 'disabled'

    # Выбор одной статьи из нескольких
    def choose(self):
        _input = self.var_input.get()
        if _input != "":
            _index = int(_input)
            self.answer = wrd_to_key(self.wrd, _index)
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.answer


# Всплывающее окно для ввода названия сохранения словаря
class EnterSaveNameW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.name_is_correct = False

        self.var_name = tk.StringVar()

        tk.Label(self, text='Введите название файла со словарём', bg=ST_BG[st], fg=ST_FG_TEXT[st]).grid(row=0, padx=6, pady=(4, 1))
        tk.Entry(self, textvariable=self.var_name, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], selectbackground=ST_SELECT[st], highlightcolor=ST_HIGHLIGHT[st]).grid(row=1, padx=6, pady=1)
        tk.Button(self, text='Подтвердить', bg=ST_BTNY[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNY_SELECT[st], highlightbackground=ST_BORDER[st], command=self.check_and_return).grid(row=2, padx=6, pady=4)

    def check_and_return(self):
        savename = self.var_name.get()
        if savename == '':
            PopupMsgW(self, 'Недопустимое название', title='Warning')
            return
        if f'{savename}.txt' in os.listdir(SAVES_PATH):  # Если уже есть сохранение с таким названием
            PopupMsgW(self, 'Файл с таким названием уже существует', title='Warning')
            return
        self.name_is_correct = True
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.name_is_correct, self.var_name.get()


# Всплывающее окно для ввода названия параметра словоформ
class EnterFormParameterNameW(tk.Toplevel):
    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.name_is_correct = False
        self.parameters = parameters

        self.var_name = tk.StringVar()

        tk.Label( self, text='Введите название нового параметра', bg=ST_BG[st], fg=ST_FG_TEXT[st]).grid(row=0, padx=6, pady=(4, 1))
        tk.Entry( self, textvariable=self.var_name, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], selectbackground=ST_SELECT[st], highlightcolor=ST_HIGHLIGHT[st]).grid(row=1, padx=6, pady=1)
        tk.Button(self, text='Подтвердить', bg=ST_BTNY[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNY_SELECT[st], highlightbackground=ST_BORDER[st], command=self.check_and_return).grid(row=2, padx=6, pady=4)

    def check_and_return(self):
        par_name = self.var_name.get()
        if par_name == '':
            PopupMsgW(self, 'Недопустимое название параметра', title='Warning')
            return
        if par_name in self.parameters:  # Если уже есть параметр с таким названием
            PopupMsgW(self, f'Параметр "{par_name}" уже существует', title='Warning')
            return
        self.name_is_correct = True
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.name_is_correct, self.var_name.get()


# Окно выбора значения параметра шаблона словоформы
class FormParValW(tk.Toplevel):
    def __init__(self, parent, par_name, par_vals):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.res = ''
        self.vals = par_vals
        self.var_par = tk.StringVar()

        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])

        self.lbl_choose = tk.Label(    self, text=f'Задайте значение параметра "{par_name}"', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.combo      = ttk.Combobox(self, textvariable=self.var_par, style='.TCombobox', values=self.vals, state='readonly')
        self.btn_choose = tk.Button(   self, text='Задать', command=self.choose, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_none   = tk.Button(   self, text='Не указывать/неприменимо', command=self.set_none, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_new    = tk.Button(   self, text='Добавить вариант', command=self.new_val, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])

        self.lbl_choose.grid(row=0, column=0,     padx=(6, 1), pady=(6, 3))
        self.combo.grid(     row=0, column=1,     padx=(0, 1), pady=(6, 3))
        self.btn_choose.grid(row=0, column=2,     padx=(0, 6), pady=(6, 3))
        self.btn_none.grid(  row=1, columnspan=3, padx=6,      pady=3)
        self.btn_new.grid(   row=2, columnspan=3, padx=6,      pady=(3, 6))

    # Выбрать параметр и задать ему значение
    def choose(self):
        self.res = self.var_par.get()
        self.destroy()

    # Сбросить значение параметра
    def set_none(self):
        self.res = ''
        self.destroy()

    # Добавить новое значение параметра
    def new_val(self):
        add_frm_param_val(self, self.vals)
        self.combo['values'] = self.vals

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.res


# Окно создания шаблона словоформы
class FormTemplateW(tk.Toplevel):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.parameters = list(form_parameters.keys())
        self.par_values = []
        for _i in range(len(self.parameters)):
            self.par_values += ['']
        self.void_frm = self.par_values.copy()
        self.key = key

        self.var_template = tk.StringVar(value='Текущий шаблон формы: ""')
        self.var_par = tk.StringVar()

        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])

        self.lbl_template = tk.Label(    self, textvariable=self.var_template, bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.lbl_choose   = tk.Label(    self, text='Выберите параметр', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.combo        = ttk.Combobox(self, textvariable=self.var_par, style='.TCombobox', values=self.parameters, state='readonly')
        self.btn_choose   = tk.Button(   self, text='Задать значение', command=self.choose, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_done     = tk.Button(   self, text='Закончить с шаблоном и ввести форму слова', command=self.done, state='disabled', bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])

        self.lbl_template.grid(row=0, columnspan=3, padx=6,      pady=(6, 1))
        self.lbl_choose.grid(  row=1, column=0,     padx=(6, 1), pady=(6, 1))
        self.combo.grid(       row=1, column=1,     padx=(0, 1), pady=1)
        self.btn_choose.grid(  row=1, column=2,     padx=(0, 6), pady=1)
        self.btn_done.grid(    row=2, columnspan=3, padx=(0, 6), pady=6)

    # Выбрать параметр и задать ему значение
    def choose(self):
        par = self.var_par.get()
        index = self.parameters.index(par)

        window = FormParValW(self, par, form_parameters[par])
        self.par_values[index] = window.open()

        self.var_template.set(f'Текущий шаблон формы: "{tpl(self.par_values)}"')

        if self.par_values == self.void_frm:
            self.btn_done['state'] = 'disabled'
        else:
            self.btn_done['state'] = 'normal'

    # Закончить с шаблоном
    def done(self):
        if tuple(self.par_values) in dct.d[self.key].forms.keys():
            PopupMsgW(self, f'\nУ слова "{key_to_wrd(self.key)}" уже есть форма с таким шаблоном', title='Warning')
            return
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        if self.par_values == self.void_frm:
            return None
        if tuple(self.par_values) in dct.d[self.key].forms.keys():
            return None
        return tuple(self.par_values)


# Окно поиска статей
class SearchW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Search')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.var_wrd = tk.StringVar(value=wrd)

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_input   = tk.Label(self.frame_main, text='Введите запрос:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.entry_input = tk.Entry(self.frame_main, textvariable=self.var_wrd, width=60, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.btn_search = tk.Button(self.frame_main, text='Поиск', command=self.search, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # }
        self.lbl_wrd       = tk.Label(self, text='Поиск по слову', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_wrd = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_wrd      = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_wrd.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.lbl_tr        = tk.Label(self, text='Поиск по переводу', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_tr  = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_tr       = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_tr.set,  bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])

        self.frame_main.grid(row=0, columnspan=4, padx=6, pady=(6, 4))
        # {
        self.lbl_input.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.btn_search.grid( row=0, column=2, padx=6,      pady=6)
        # }
        self.lbl_wrd.grid(      row=1, column=0, columnspan=2, padx=(6, 3), pady=(0, 3))
        self.lbl_tr.grid(       row=1, column=2, columnspan=2, padx=(3, 6), pady=(0, 3))
        self.text_wrd.grid(     row=2, column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar_wrd.grid(row=2, column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.text_tr.grid(      row=2, column=2, padx=(0, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar_tr.grid( row=2, column=3, padx=(0, 6), pady=(0, 6), sticky='NSW')

        self.scrollbar_wrd.config(command=self.text_wrd.yview)
        self.scrollbar_tr.config( command=self.text_tr.yview)

    # Поиск статей
    def search(self):
        # Поиск по слову
        search_wrd = self.var_wrd.get()

        self.text_wrd['state'] = 'normal'
        self.text_wrd.delete(1.0, tk.END)

        outp(self.text_wrd, 'Частичное совпадение:')
        dct.print_words_with_str(self.text_wrd, search_wrd)

        outp(self.text_wrd, '\nПолное совпадение:')
        if wrd_to_key(search_wrd, 0) not in dct.d.keys():
            outp(self.text_wrd, f'Слово "{code(search_wrd)}" отсутствует в словаре', _end='')
        else:
            for i in range(MAX_SAME_WORDS):
                key = wrd_to_key(search_wrd, i)
                if key not in dct.d.keys():
                    break
                outp(self.text_wrd)
                dct.d[key].print_all(self.text_wrd)

        self.text_wrd['state'] = 'disabled'

        # Поиск по переводу
        search_tr = self.var_wrd.get()

        self.text_tr['state'] = 'normal'
        self.text_tr.delete(1.0, tk.END)

        outp(self.text_tr, 'Частичное совпадение:')
        dct.print_translations_with_str(self.text_tr, search_tr)

        outp(self.text_tr, '\nПолное совпадение:')
        is_found = False
        for entry in dct.d.values():
            if search_tr in entry.tr:
                is_found = True
                outp(self.text_tr)
                entry.print_all(self.text_tr)
        if not is_found:
            outp(self.text_tr, f'Слово с переводом "{code(search_tr)}" отсутствует в словаре', _end='')

        self.text_tr['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно вывода похожих статей для редактирования
class ParticularMatchesW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Similar')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.var_wrd = tk.StringVar(value=wrd)

        self.lbl_header    = tk.Label(self, text=f'Слово "{wrd}" отсутствует в словаре\nВозможно вы искали:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.lbl_wrd       = tk.Label(self, text=f'Слова, содержащие "{wrd}"', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_wrd = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_wrd      = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_wrd.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.lbl_tr        = tk.Label(self, text=f'Переводы, содержащие "{wrd}"', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_tr  = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_tr       = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_tr.set,  bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])

        self.lbl_header.grid(   row=0, column=0, columnspan=4, padx=6,      pady=(6, 3))
        self.lbl_wrd.grid(      row=1, column=0, columnspan=2, padx=(6, 3), pady=(0, 3))
        self.lbl_tr.grid(       row=1, column=2, columnspan=2, padx=(3, 6), pady=(0, 3))
        self.text_wrd.grid(     row=2, column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar_wrd.grid(row=2, column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.text_tr.grid(      row=2, column=2,               padx=(0, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar_tr.grid( row=2, column=3,               padx=(0, 6), pady=(0, 6), sticky='NSW')

        self.scrollbar_wrd.config(command=self.text_wrd.yview)
        self.scrollbar_tr.config( command=self.text_tr.yview)

        self.search()

    # Поиск статей
    def search(self):
        # Поиск по слову
        search_wrd = self.var_wrd.get()

        self.text_wrd['state'] = 'normal'
        self.text_wrd.delete(1.0, tk.END)

        dct.print_words_with_str(self.text_wrd, search_wrd)

        self.text_wrd['state'] = 'disabled'

        # Поиск по переводу
        search_tr = self.var_wrd.get()

        self.text_tr['state'] = 'normal'
        self.text_tr.delete(1.0, tk.END)

        dct.print_translations_with_str(self.text_tr, search_tr)

        self.text_tr['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно настроек словоформ
class FormsSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.var_par = tk.StringVar()

        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])

        self.lbl_form_par  = tk.Label(     self, text='Существующие параметры форм:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar     = tk.Scrollbar( self, bg=ST_BG[st])
        self.text_form_par = tk.Text(      self, width=20, height=10, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.frame_buttons = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.btn_add    = tk.Button(self.frame_buttons, text='Добавить параметр форм',           command=self.add,    bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_delete = tk.Button(self.frame_buttons, text='Удалить параметр форм',            command=self.delete, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_rename = tk.Button(self.frame_buttons, text='Переименовать параметр форм',      command=self.rename, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_values = tk.Button(self.frame_buttons, text='Изменить значения параметра форм', command=self.values, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        # }

        self.lbl_form_par.grid( row=0,            column=0, columnspan=2, padx=6,      pady=(6, 0))
        self.text_form_par.grid(row=1,            column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(    row=1,            column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(row=0, rowspan=2, column=2,               padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_delete.grid(row=1, padx=6, pady=3)
        self.btn_rename.grid(row=2, padx=6, pady=3)
        self.btn_values.grid(row=3, padx=6, pady=(3, 6))
        # }

        self.scrollbar.config(command=self.text_form_par.yview)

        self.refresh()

    # Добавить параметр
    def add(self):
        add_frm_param(self, form_parameters, dct)
        self.refresh()

    # Удалить параметр
    def delete(self):
        remove_frm_param(self, form_parameters, dct)
        self.refresh()

    # Переименовать параметр
    def rename(self):
        rename_frm_param(self, form_parameters, dct)
        self.refresh()

    # Изменить значения параметра
    def values(self):
        _keys = [_key for _key in form_parameters.keys()]
        _key = PopupChooseW(self, _keys, 'Какой параметр форм вы хотите изменить?').open()
        if _key == '':
            return
        FormsParameterSettingsW(self, _key).open()

    # Напечатать существующие параметры форм
    def print_form_par_list(self):
        self.text_form_par['state'] = 'normal'
        self.text_form_par.delete(1.0, tk.END)
        for key in form_parameters.keys():
            self.text_form_par.insert(tk.INSERT, f'{key}\n')
        self.text_form_par['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_form_par_list()
        if form_parameters:
            self.btn_delete['state'] = 'normal'
            self.btn_rename['state'] = 'normal'
            self.btn_values['state'] = 'normal'
        else:
            self.btn_delete['state'] = 'disabled'
            self.btn_rename['state'] = 'disabled'
            self.btn_values['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно настроек параметра словоформ
class FormsParameterSettingsW(tk.Toplevel):
    def __init__(self, parent, parameter):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[st])

        self.parameter = parameter
        self.par_vals = form_parameters[self.parameter]

        self.var_par = tk.StringVar()

        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])

        self.lbl_par_val   = tk.Label(     self, text=f'Существующие значения параметра "{parameter}":', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar     = tk.Scrollbar( self, bg=ST_BG[st])
        self.text_par_val  = tk.Text(      self, width=20, height=10, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.frame_buttons = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.btn_add    = tk.Button(self.frame_buttons, text='Добавить значение параметра',      command=self.add,    bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_delete = tk.Button(self.frame_buttons, text='Удалить значение параметра',       command=self.delete, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_rename = tk.Button(self.frame_buttons, text='Переименовать значение параметра', command=self.rename, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        # }

        self.lbl_par_val.grid(  row=0,            column=0, columnspan=2, padx=6,      pady=(6, 0))
        self.text_par_val.grid( row=1,            column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(    row=1,            column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(row=0, rowspan=2, column=2,               padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_delete.grid(row=1, padx=6, pady=3)
        self.btn_rename.grid(row=2, padx=6, pady=3)
        # }

        self.scrollbar.config(command=self.text_par_val.yview)

        self.refresh()

    # Добавить значение параметра
    def add(self):
        add_frm_param_val(self, self.par_vals)
        self.refresh()

    # Удалить значение параметра
    def delete(self):
        delete_frm_param_val(self, self.par_vals, dct)
        self.refresh()

    # Переименовать значение параметра
    def rename(self):
        _index = tuple(form_parameters).index(self.parameter)
        rename_frm_param_val(self, self.par_vals, _index, dct)
        self.refresh()

    # Напечатать существующие параметры форм
    def print_par_val_list(self):
        self.text_par_val['state'] = 'normal'
        self.text_par_val.delete(1.0, tk.END)
        for key in self.par_vals:
            self.text_par_val.insert(tk.INSERT, f'{key}\n')
        self.text_par_val['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_par_val_list()
        if len(self.par_vals) == 1:
            self.btn_delete['state'] = 'disabled'
        else:
            self.btn_delete['state'] = 'normal'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно добавления статьи
class AddW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Add an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.key = None

        self.var_wrd = tk.StringVar(value=wrd)
        self.var_tr  = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[st])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[st])])

        self.lbl_wrd   = tk.Label( self, text='Введите слово:',   bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.entry_wrd = tk.Entry( self, textvariable=self.var_wrd, width=60, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.lbl_tr    = tk.Label( self, text='Введите перевод:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.entry_tr  = tk.Entry( self, textvariable=self.var_tr,  width=60, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.lbl_fav   = tk.Label( self, text='Избранное:',       bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.check_fav = ttk.Checkbutton(self, variable=self.var_fav, style='.TCheckbutton')
        self.btn_add   = tk.Button(self, text='Добавить', command=self.add, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])

        self.lbl_wrd.grid(  row=0, column=0,     padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_wrd.grid(row=0, column=1,     padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr.grid(   row=1, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr.grid( row=1, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_fav.grid(  row=2, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.check_fav.grid(row=2, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.btn_add.grid(  row=3, columnspan=2, padx=6,      pady=(0, 6))

    # Добавление статьи
    def add(self):
        global has_changes

        if self.var_wrd.get() == '':
            PopupMsgW(self, 'Слово должно содержать хотя бы один символ', title='Warning')
            return
        if self.var_tr.get() == '':
            PopupMsgW(self, 'Перевод должен содержать хотя бы один символ', title='Warning')
            return

        self.key = dct.add_entry(self, self.var_wrd.get(), self.var_tr.get())
        if not self.key:
            return
        dct.d[self.key].fav = self.var_fav.get()

        has_changes = True
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.key


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Edit an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.key = key
        self.line_width = 35
        self.max_height = 5
        self.height_w = max(min(height(dct.d[key].wrd,            self.line_width), self.max_height), 1)
        self.height_t =     min(height(dct.d[key].tr_to_str(),    self.line_width), self.max_height)
        self.height_n =     min(height(dct.d[key].notes_to_str(), self.line_width), self.max_height)
        self.height_f =     min(height(dct.d[key].frm_to_str(),   self.line_width), self.max_height)

        self.var_wrd = tk.StringVar(value=dct.d[key].wrd)
        self.var_fav = tk.BooleanVar(value=dct.d[key].fav)

        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[st])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[st])])

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_wrd       = tk.Label(    self.frame_main, text='Слово:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_wrd = tk.Scrollbar(self.frame_main, bg=ST_BG[st])
        self.txt_wrd       = tk.Text(     self.frame_main, width=self.line_width, height=self.height_w, yscrollcommand=self.scrollbar_wrd.set, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.txt_wrd.insert(tk.INSERT, dct.d[key].wrd)
        self.txt_wrd['state'] = 'disabled'
        self.scrollbar_wrd.config(command=self.txt_wrd.yview)
        self.btn_wrd_edt   = tk.Button(self.frame_main, text='изм.', command=self.wrd_edt, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])

        self.lbl_tr        = tk.Label(    self.frame_main, text='Перевод:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_tr  = tk.Scrollbar(self.frame_main, bg=ST_BG[st])
        self.txt_tr        = tk.Text(     self.frame_main, width=self.line_width, height=self.height_t, yscrollcommand=self.scrollbar_tr.set, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.txt_tr.insert(tk.INSERT, dct.d[key].tr_to_str())
        self.txt_tr['state'] = 'disabled'
        self.scrollbar_tr.config(command=self.txt_tr.yview)
        self.frame_btns_tr = tk.Frame(self.frame_main, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.btn_tr_add = tk.Button(self.frame_btns_tr, text='+', command=self.tr_add, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.btn_tr_del = tk.Button(self.frame_btns_tr, text='-', command=self.tr_del, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # } }

        self.lbl_notes       = tk.Label(    self.frame_main, text='Сноски:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_notes = tk.Scrollbar(self.frame_main, bg=ST_BG[st])
        self.txt_notes       = tk.Text(     self.frame_main, width=self.line_width, height=self.height_n, yscrollcommand=self.scrollbar_notes.set, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.txt_notes.insert(tk.INSERT, dct.d[key].notes_to_str())
        self.txt_notes['state'] = 'disabled'
        self.scrollbar_notes.config(command=self.txt_notes.yview)
        self.frame_btns_notes = tk.Frame(self.frame_main, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.btn_notes_add = tk.Button(self.frame_btns_notes, text='+', command=self.notes_add, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.btn_notes_del = tk.Button(self.frame_btns_notes, text='-', command=self.notes_del, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # } }

        self.lbl_frm       = tk.Label(    self.frame_main, text='Формы слова:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar_frm = tk.Scrollbar(self.frame_main, bg=ST_BG[st])
        self.txt_frm       = tk.Text(     self.frame_main, width=self.line_width, height=self.height_f, yscrollcommand=self.scrollbar_frm.set, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.txt_frm.insert(tk.INSERT, dct.d[key].frm_to_str())
        self.txt_frm['state'] = 'disabled'
        self.scrollbar_frm.config(command=self.txt_frm.yview)
        self.frame_btns_frm = tk.Frame(self.frame_main, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.btn_frm_add = tk.Button(self.frame_btns_frm, text='+',    command=self.frm_add, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.btn_frm_del = tk.Button(self.frame_btns_frm, text='-',    command=self.frm_del, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.btn_frm_edt = tk.Button(self.frame_btns_frm, text='изм.', command=self.frm_edt, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # } }

        self.lbl_fav   = tk.Label(       self.frame_main, text='Избранное:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.check_fav = ttk.Checkbutton(self.frame_main, variable=self.var_fav, command=self.set_fav, style='.TCheckbutton')
        # }
        self.btn_back   = tk.Button(self, text='Закончить',      command=self.back,   bg=ST_BTN[st],  fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.btn_delete = tk.Button(self, text='Удалить статью', command=self.delete, bg=ST_BTNN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTNN_SELECT[st])

        self.frame_main.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        # {
        self.lbl_wrd.grid(      row=0, column=0, padx=(6, 1), pady=(6, 3), sticky='E')
        self.txt_wrd.grid(      row=0, column=1, padx=(0, 1), pady=(6, 3), sticky='W')
        self.scrollbar_wrd.grid(row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.btn_wrd_edt.grid(  row=0, column=3, padx=(3, 6), pady=(6, 3), sticky='W')

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
        self.btn_notes_add.grid(row=0, column=0, padx=(0, 1), pady=0)
        self.btn_notes_del.grid(row=0, column=1, padx=(1, 0), pady=0)
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

        if dct.d[key].count_t < 2:
            self.btn_tr_del.grid_remove()
        if dct.d[key].count_n < 1:
            self.btn_notes_del.grid_remove()
        if dct.d[key].count_f < 1:
            self.btn_frm_del.grid_remove()
            self.btn_frm_edt.grid_remove()

        if self.height_w < self.max_height:
            self.scrollbar_wrd.grid_remove()
        if self.height_t < self.max_height:
            self.scrollbar_tr.grid_remove()
        if self.height_n < self.max_height:
            self.scrollbar_notes.grid_remove()
        if self.height_f < self.max_height:
            self.scrollbar_frm.grid_remove()

    # Обновить поля
    def refresh(self):
        self.height_w = max(min(height(dct.d[self.key].wrd,            self.line_width), self.max_height), 1)
        self.height_t =     min(height(dct.d[self.key].tr_to_str(),    self.line_width), self.max_height)
        self.height_n =     min(height(dct.d[self.key].notes_to_str(), self.line_width), self.max_height)
        self.height_f =     min(height(dct.d[self.key].frm_to_str(),   self.line_width), self.max_height)

        self.txt_wrd  ['height'] = self.height_w
        self.txt_tr   ['height'] = self.height_t
        self.txt_notes['height'] = self.height_n
        self.txt_frm  ['height'] = self.height_f

        self.txt_wrd['state'] = 'normal'
        self.txt_wrd.delete(1.0, tk.END)
        self.txt_wrd.insert(tk.INSERT, dct.d[self.key].wrd)
        self.txt_wrd['state'] = 'disabled'

        self.txt_tr['state'] = 'normal'
        self.txt_tr.delete(1.0, tk.END)
        self.txt_tr.insert(tk.INSERT, dct.d[self.key].tr_to_str())
        self.txt_tr['state'] = 'disabled'

        self.txt_notes['state'] = 'normal'
        self.txt_notes.delete(1.0, tk.END)
        self.txt_notes.insert(tk.INSERT, dct.d[self.key].notes_to_str())
        self.txt_notes['state'] = 'disabled'

        self.txt_frm['state'] = 'normal'
        self.txt_frm.delete(1.0, tk.END)
        self.txt_frm.insert(tk.INSERT, dct.d[self.key].frm_to_str())
        self.txt_frm['state'] = 'disabled'

        self.btn_tr_del.grid(     row=0, column=1, padx=(1, 0), pady=0)
        self.btn_notes_del.grid(  row=0, column=1, padx=(1, 0), pady=0)
        self.btn_frm_del.grid(    row=0, column=1, padx=(1, 1), pady=0)
        self.btn_frm_edt.grid(    row=0, column=2, padx=(1, 0), pady=0)
        self.scrollbar_wrd.grid(  row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.scrollbar_tr.grid(   row=1, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_notes.grid(row=2, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_frm.grid(  row=3, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')

        if dct.d[self.key].count_t < 2:
            self.btn_tr_del.grid_remove()
        if dct.d[self.key].count_n < 1:
            self.btn_notes_del.grid_remove()
        if dct.d[self.key].count_f < 1:
            self.btn_frm_del.grid_remove()
            self.btn_frm_edt.grid_remove()

        if self.height_w < self.max_height:
            self.scrollbar_wrd.grid_remove()
        if self.height_t < self.max_height:
            self.scrollbar_tr.grid_remove()
        if self.height_n < self.max_height:
            self.scrollbar_notes.grid_remove()
        if self.height_f < self.max_height:
            self.scrollbar_frm.grid_remove()

    # Изменить слово
    def wrd_edt(self):
        global has_changes

        window = PopupEntryW(self, 'Введите новое слово')
        new_wrd = window.open()
        if new_wrd == '':
            PopupMsgW(self, 'Слово должно содержать хотя бы один символ', title='Warning')
            return
        if new_wrd == key_to_wrd(self.key):
            PopupMsgW(self, 'Это то же самое слово', title='Warning')
            return
        self.key = dct.edit_wrd(self, self.key, new_wrd)
        has_changes = True

        self.refresh()

    # Добавить перевод
    def tr_add(self):
        global has_changes

        window = PopupEntryW(self, 'Введите новый перевод')
        tr = window.open()
        if tr == '':
            PopupMsgW(self, 'Перевод должен содержать хотя бы один символ', title='Warning')
            return
        if tr in dct.d[self.key].tr:
            PopupMsgW(self, f'У слова "{dct.d[self.key].wrd}" уже есть такой перевод', title='Warning')
            return
        dct.add_tr(self.key, tr, _window=self, _is_key=True)
        has_changes = True

        self.refresh()

    # Удалить перевод
    def tr_del(self):
        global has_changes

        dct.remove_tr_with_choose(self, self.key, _is_key=True)
        has_changes = True

        self.refresh()

    # Добавить сноску
    def notes_add(self):
        global has_changes

        window = PopupEntryW(self, 'Введите сноску')
        note = window.open()
        if note == '':
            PopupMsgW(self, 'Сноска должна содержать хотя бы один символ', title='Warning')
            return
        if note in dct.d[self.key].notes:
            PopupMsgW(self, f'У слова "{dct.d[self.key].wrd}" уже есть такая сноска', title='Warning')
            return
        dct.add_note(self.key, note)
        has_changes = True

        self.refresh()

    # Удалить сноску
    def notes_del(self):
        global has_changes

        dct.remove_note_with_choose(self, self.key, _is_key=True)
        has_changes = True

        self.refresh()

    # Добавить словоформу
    def frm_add(self):
        global has_changes

        if not form_parameters:
            PopupMsgW(self, 'Отсутствуют параметры форм!\n'
                            'Чтобы добавить, перейдите в\n'
                            'Настройки/Настройки словаря/Настройки словоформ').open()
            return

        window_template = FormTemplateW(self, self.key)
        frm_key = window_template.open()
        if not frm_key:
            return
        window_form = PopupEntryW(self, 'Введите форму слова')
        frm = window_form.open()
        dct.add_frm(self.key, frm_key, frm, _window=self, _is_key=True)
        has_changes = True

        self.refresh()

    # Удалить словоформу
    def frm_del(self):
        global has_changes

        dct.remove_frm_with_choose(self, self.key, _is_key=True)
        has_changes = True

        self.refresh()

    # Изменить словоформу
    def frm_edt(self):
        global has_changes

        dct.edit_frm_with_choose(self, self.key, _is_key=True)
        has_changes = True

        self.refresh()

    # Добавить в избранное/убрать из избранного
    def set_fav(self):
        dct.d[self.key].fav = self.var_fav.get()

    # Закрыть настройки
    def back(self):
        self.destroy()

    # Удалить статью
    def delete(self):
        global has_changes

        window = PopupDialogueW(self, 'Вы уверены, что хотите удалить эту статью?')
        answer = window.open()
        if answer:
            dct.remove_entry(self.key, _is_key=True)
            has_changes = True
            self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно печати словаря
class PrintW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Print')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.var_fav   = tk.BooleanVar(value=False)
        self.var_forms = tk.BooleanVar(value=True)

        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[st])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[st])])

        self.lbl_dct_name = tk.Label(self, text=f'Открыт словарь "{dct_savename}"', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.frame_main = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_fav     = tk.Label(self.frame_main, text='Только избранные:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.lbl_forms   = tk.Label(self.frame_main, text='Все формы:',        bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.check_fav   = ttk.Checkbutton(self.frame_main, variable=self.var_fav,   style='.TCheckbutton')
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, style='.TCheckbutton')
        self.btn_print   = tk.Button(self.frame_main, text='Печать', command=self.print, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # }
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_dct  = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.scrollbar.config(command=self.text_dct.yview)

        self.lbl_dct_name.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        self.frame_main.grid(  row=1, columnspan=2, padx=6, pady=(0, 4))
        # {
        self.lbl_fav.grid(    row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_fav.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_forms.grid(  row=0, column=2, padx=(6, 1), pady=6, sticky='E')
        self.check_forms.grid(row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        self.btn_print.grid(  row=0, column=4, padx=6,      pady=6)
        # }
        self.text_dct.grid( row=2, column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(row=2, column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')

        self.print()

    # Напечатать словарь
    def print(self):
        self.text_dct['state'] = 'normal'
        self.text_dct.delete(1.0, tk.END)
        if self.var_fav.get():
            if self.var_forms.get():
                dct.print_fav_with_forms(self.text_dct, min_good_score_perc)
            else:
                dct.print_fav(self.text_dct, min_good_score_perc)
        else:
            if self.var_forms.get():
                dct.print_with_forms(self.text_dct, min_good_score_perc)
            else:
                dct.print(self.text_dct, min_good_score_perc)
        self.text_dct.yview_moveto(1.0)
        self.text_dct['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно выбора режима перед изучением слов
class ChooseLearnModeW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Learn')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.res = None

        self.var_order = tk.StringVar(value=VALUES_ORDER[0])
        self.var_forms = tk.BooleanVar(value=True)
        self.var_words = tk.StringVar(value=VALUES_WORDS[0])

        # Стили для некоторых настроек
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[st], foreground=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[st])], foreground=[('readonly', ST_FG_TEXT[st])], highlightbackground=[('readonly', ST_BORDER[st])])
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[st])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[st])])

        self.lbl_header = tk.Label(self, text='Выберите способ учёбы', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.frame_main = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_order = tk.Label(self.frame_main, text='Метод:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.combo_order = ttk.Combobox(self.frame_main, textvariable=self.var_order, values=VALUES_ORDER, validate='focusin', width=30, state='readonly', style='.TCombobox')
        self.lbl_forms = tk.Label(self.frame_main, text='Все словоформы:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, style='.TCheckbutton')
        self.lbl_words = tk.Label(self.frame_main, text='Подбор слов:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.combo_words = ttk.Combobox(self.frame_main, textvariable=self.var_words, values=VALUES_WORDS, width=30, state='readonly', style='.TCombobox')
        # }
        self.btn_start = tk.Button(self, text='Учить', command=self.start, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])

        self.lbl_header.grid( row=0, column=0, padx=6, pady=(6, 3))
        self.frame_main.grid( row=1, column=0, padx=6, pady=(0, 3))
        # {
        self.lbl_order.grid(  row=1, column=0, padx=(3, 1), pady=(3, 3), sticky='E')
        self.combo_order.grid(row=1, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        self.lbl_forms.grid(  row=2, column=0, padx=(3, 1), pady=(0, 3), sticky='E')
        self.check_forms.grid(row=2, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        self.lbl_words.grid(  row=3, column=0, padx=(3, 1), pady=(0, 3), sticky='E')
        self.combo_words.grid(row=3, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        # }
        self.btn_start.grid(  row=2, column=0, padx=6, pady=(0, 6))

        self.vcmd_order = (self.register(lambda value: validate_order_and_forms(value, self.check_forms)), '%P')
        self.combo_order['validatecommand'] = self.vcmd_order

    # Учить слова
    def start(self):
        order = self.var_order.get()
        forms = self.var_forms.get()
        words = self.var_words.get()
        self.res = (order, forms, words)
        self.destroy()

    def open(self):
        self.grab_set()
        self.wait_window()
        return self.res


# Окно изучения слов
class LearnW(tk.Toplevel):
    def __init__(self, parent, conf):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Learn')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.current_key = None
        self.current_form = None
        self.rnd_f = None
        self.count_all = 0
        self.count_correct = 0
        self.used_words = set()
        self.conf = conf

        self.var_input = tk.StringVar()

        self.lbl_global_rating = tk.Label(self, text=f'Ваш общий рейтинг по словарю: {round(dct.count_rating() * 100)}%', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[st])
        self.text_dct = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.scrollbar.config(command=self.text_dct.yview)
        self.frame_main = tk.Frame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.btn_input = tk.Button(self.frame_main, text='Ввод', command=self.input, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        self.entry_input = tk.Entry(self.frame_main, textvariable=self.var_input, width=50, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.btn_notes = tk.Button(self.frame_main, text='Посмотреть сноски', command=self.notes, bg=ST_BTN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTN_SELECT[st])
        # } }
        self.btn_stop  = tk.Button(self, text='Закончить', command=self.stop, bg=ST_BTNN[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], activebackground=ST_BTNN_SELECT[st])

        self.lbl_global_rating.grid(row=0, columnspan=2, padx=6,      pady=6)
        self.text_dct.grid(         row=1, column=0,     padx=(6, 0), pady=6, sticky='NSEW')
        self.scrollbar.grid(        row=1, column=1,     padx=(0, 6), pady=6, sticky='NSW')
        self.frame_main.grid(       row=2, columnspan=2, padx=6,      pady=6)
        # { {
        self.btn_input.grid(  row=0, column=0, padx=(0, 3), pady=0, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 3), pady=0, sticky='W')
        self.btn_notes.grid(  row=0, column=2, padx=0,      pady=0, sticky='W')
        # } }
        self.btn_stop.grid(row=3, columnspan=2, padx=6, pady=6)

        self.start()

    # Печать в текстовое поле
    def outp(self, msg='', end='\n'):
        self.text_dct['state'] = 'normal'
        self.text_dct.insert(tk.END, msg + end)
        self.text_dct.yview_moveto(1.0)
        self.text_dct['state'] = 'disabled'

    # Учить слова
    def start(self):
        global has_changes

        order = self.conf[0]
        forms = self.conf[1]
        words = self.conf[2]

        if order == VALUES_ORDER[0]:
            if forms:
                if words == VALUES_WORDS[0]:
                    has_changes = self.choose_f(dct, min_good_score_perc) or has_changes
                elif words == VALUES_WORDS[1]:
                    has_changes = self.choose_f_hard(dct, min_good_score_perc) or has_changes
                else:
                    has_changes = self.choose_f_fav(dct, min_good_score_perc) or has_changes
            else:
                if words == VALUES_WORDS[0]:
                    has_changes = self.choose(dct, min_good_score_perc) or has_changes
                elif words == VALUES_WORDS[1]:
                    has_changes = self.choose_hard(dct, min_good_score_perc) or has_changes
                else:
                    has_changes = self.choose_fav(dct, min_good_score_perc) or has_changes
        else:
            if words == VALUES_WORDS[0]:
                has_changes = self.choose_t(dct, min_good_score_perc) or has_changes
            elif words == VALUES_WORDS[1]:
                has_changes = self.choose_t_hard(dct, min_good_score_perc) or has_changes
            else:
                has_changes = self.choose_t_fav(dct, min_good_score_perc) or has_changes

    # Ввод ответа
    def input(self):
        global has_changes

        order = self.conf[0]
        forms = self.conf[1]
        words = self.conf[2]

        if order == VALUES_ORDER[1]:
            self.check_tr()
        elif forms and self.rnd_f != -1:
            self.check_form()
        else:
            self.check_wrd()

        if order == VALUES_ORDER[0]:
            if forms:
                if words == VALUES_WORDS[0]:
                    has_changes = self.choose_f(dct, min_good_score_perc) or has_changes
                elif words == VALUES_WORDS[1]:
                    has_changes = self.choose_f_hard(dct, min_good_score_perc) or has_changes
                else:
                    has_changes = self.choose_f_fav(dct, min_good_score_perc) or has_changes
            else:
                if words == VALUES_WORDS[0]:
                    has_changes = self.choose(dct, min_good_score_perc) or has_changes
                elif words == VALUES_WORDS[1]:
                    has_changes = self.choose_hard(dct, min_good_score_perc) or has_changes
                else:
                    has_changes = self.choose_fav(dct, min_good_score_perc) or has_changes
        else:
            if words == VALUES_WORDS[0]:
                has_changes = self.choose_t(dct, min_good_score_perc) or has_changes
            elif words == VALUES_WORDS[1]:
                has_changes = self.choose_t_hard(dct, min_good_score_perc) or has_changes
            else:
                has_changes = self.choose_t_fav(dct, min_good_score_perc) or has_changes

        self.btn_notes['state'] = 'normal'
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {round(dct.count_rating() * 100)}%'

    # Просмотр сносок
    def notes(self):
        self.text_dct['state'] = 'normal'
        entry = dct.d[self.current_key]
        entry.notes_print(self.text_dct)
        self.text_dct.yview_moveto(1.0)
        self.text_dct['state'] = 'disabled'
        self.btn_notes['state'] = 'disabled'

    # Завершение учёбы
    def stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()

        if len(self.used_words) == dct.count_w:
            PopupMsgW(self, f'Ваш результат: {self.count_correct}/{self.count_all}')
        self.outp(f'\nВаш результат: {self.count_correct}/{self.count_all}')

    # Проверка введённого слова
    def check_wrd(self):
        entry = dct.d[self.current_key]
        if self.entry_input.get() == entry.wrd:
            entry.correct()
            self.outp('Верно\n')
            if entry.fav:
                window= PopupDialogueW(self, 'Оставить слово в избранном?', 'Да', 'Нет')
                answer = window.open()
                if not answer:
                    entry.fav = False
            self.count_all += 1
            self.count_correct += 1
            self.used_words.add(self.current_key)
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{entry.wrd}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Добавить слово в избранное?', 'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Проверка введённой словоформы
    def check_form(self):
        entry = dct.d[self.current_key]
        if self.entry_input.get() == entry.forms[self.current_form]:
            entry.correct()
            self.outp('Верно\n')
            if entry.fav:
                window = PopupDialogueW(self, 'Оставить слово в избранном?', 'Да', 'Нет')
                answer = window.open()
                if not answer:
                    entry.fav = False
            self.count_all += 1
            self.count_correct += 1
            self.used_words.add((self.current_key, self.current_form))
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{entry.forms[self.current_form]}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Добавить слово в избранное?', 'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Проверка введённого перевода
    def check_tr(self):
        entry = dct.d[self.current_key]
        if self.entry_input.get() in entry.tr:
            entry.correct()
            self.outp('Верно\n')
            if entry.fav:
                window = PopupDialogueW(self, 'Оставить слово в избранном?', 'Да', 'Нет')
                answer = window.open()
                if not answer:
                    entry.fav = False
            self.count_all += 1
            self.count_correct += 1
            self.used_words.add(self.current_key)
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{entry.tr}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Добавить слово в избранное?', 'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Выбор слова - все
    def choose(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(_dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите слово')

        return True

    # Выбор слова - избранные
    def choose_fav(self, _dct, _min_good_score_perc):
        while True:
            if len(self.used_words) == _dct.count_w:
                self.stop()
                return
            self.current_key = random.choice(list(_dct.d.keys()))
            if not _dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                continue
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите слово')

        return True

    # Выбор слова - все, сначала сложные
    def choose_hard(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = _dct.random_hard(_min_good_score_perc)
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите слово')

        return True

    # Выбор словоформы - все
    def choose_f(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w + _dct.count_f:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(_dct.d.keys()))
            self.rnd_f = random.randint(-1, _dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово')
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово в данной форме')
                    break

        return True

    # Выбор словоформы - избранные
    def choose_f_fav(self, _dct, _min_good_score_perc):
        while True:
            if len(self.used_words) == _dct.count_w + _dct.count_f:
                self.stop()
                return
            self.current_key = random.choice(list(_dct.d.keys()))
            if not _dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                for frm in _dct.d[self.current_key].forms.keys():
                    self.used_words.add((self.current_key, frm))
                continue
            self.rnd_f = random.randint(-1, _dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово')
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово в данной форме')
                    break

        return True

    # Выбор словоформы - все, сначала сложные
    def choose_f_hard(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w + _dct.count_f:
            self.stop()
            return
        while True:
            self.current_key = _dct.random_hard(_min_good_score_perc)
            self.rnd_f = random.randint(-1, _dct.d[self.current_key].count_f - 1)
            if self.rnd_f == -1:
                self.current_form = self.current_key
                if self.current_key not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово')
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form, _min_good_score_perc)
                    self.text_dct['state'] = 'disabled'
                    self.outp('Введите слово в данной форме')
                    break

        return True

    # Выбор перевода - все
    def choose_t(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(_dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите перевод')

        return True

    # Выбор перевода - избранные
    def choose_t_fav(self, _dct, _min_good_score_perc):
        while True:
            if len(self.used_words) == _dct.count_w:
                self.stop()
                return
            self.current_key = random.choice(list(_dct.d.keys()))
            if not _dct.d[self.current_key].fav:
                self.used_words.add(self.current_key)
                continue
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите перевод')

        return True

    # Выбор перевода - все, сначала сложные
    def choose_t_hard(self, _dct, _min_good_score_perc):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = _dct.random_hard(_min_good_score_perc)
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct, _min_good_score_perc)
        self.text_dct['state'] = 'disabled'
        self.outp('Введите перевод')

        return True

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Settings')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.var_MGSP = tk.StringVar(value=str(min_good_score_perc))

        self.vcmd = (self.register(validate_percent), '%P')

        self.tabs = ttk.Notebook(self)
        self.tab_local = ttk.Frame(self.tabs)
        self.lbl_dct_name = tk.Label(self, text=f'Открыт словарь "{dct_savename}"', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.tabs.add(self.tab_local, text='Настройки словаря')
        # {
        self.frame_MGSP = tk.LabelFrame(self.tab_local, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.lbl_MGSP   = tk.Label( self.frame_MGSP, text='Минимальный приемлемый процент угадываний слова:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.entry_MGSP = tk.Entry( self.frame_MGSP, textvariable=self.var_MGSP, width=5, relief='solid', validate='key', vcmd=self.vcmd, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.btn_MGSP   = tk.Button(self.frame_MGSP, text='Принять', command=self.set_MGSP, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.lbl_MGSP_2 = tk.Label( self.frame_MGSP, text='Статьи, у которых процент угадывания ниже этого значения, будут считаться более сложными', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        # } }
        self.btn_forms  = tk.Button(self.tab_local, text='Настройки словоформ', command=self.forms,  bg=ST_BTN[st],  fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        # }
        self.tab_global = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_global, text='Настройки программы')
        # {
        self.lbl_dcts          = tk.Label(     self.tab_global, text='Существующие словари:', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.scrollbar         = tk.Scrollbar( self.tab_global, bg=ST_BG[st])
        self.text_dcts         = tk.Text(      self.tab_global, width=20, height=10, state='disabled', yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        self.frame_dct_buttons = tk.LabelFrame(self.tab_global, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # { {
        self.btn_dct_open   = tk.Button(self.frame_dct_buttons, text='Открыть словарь',       command=self.dct_open,   bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_dct_create = tk.Button(self.frame_dct_buttons, text='Создать словарь',       command=self.dct_create, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_dct_rename = tk.Button(self.frame_dct_buttons, text='Переименовать словарь', command=self.dct_rename, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_dct_delete = tk.Button(self.frame_dct_buttons, text='Удалить словарь',       command=self.dct_delete, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        # } }
        # Настройки стилей
        # }

        self.lbl_dct_name.grid(row=0, padx=6, pady=(6, 0))
        self.tabs.grid(        row=1, padx=6, pady=(0, 6))
        #
        self.frame_MGSP.grid(row=0, padx=6, pady=6, sticky='E')
        # {
        self.lbl_MGSP.grid(  row=0, column=0,     padx=(6, 1), pady=6,      sticky='E')
        self.entry_MGSP.grid(row=0, column=1,     padx=(0, 1), pady=6,      sticky='W')
        self.btn_MGSP.grid(  row=0, column=2,     padx=(0, 6), pady=6,      sticky='W')
        self.lbl_MGSP_2.grid(row=1, columnspan=3, padx=6,      pady=(0, 6))
        # }
        self.btn_forms.grid(row=1, padx=6, pady=(0, 6))
        #
        self.lbl_dcts.grid(         row=0,            column=0, columnspan=2, padx=6,      pady=(6, 0))
        self.text_dcts.grid(        row=1,            column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(        row=1,            column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_dct_buttons.grid(row=0, rowspan=2, column=2,               padx=6,      pady=6)
        # {
        self.btn_dct_open.grid(  row=0, column=2, padx=6, pady=6)
        self.btn_dct_create.grid(row=0, column=3, padx=6, pady=6)
        self.btn_dct_rename.grid(row=1, column=2, padx=6, pady=6)
        self.btn_dct_delete.grid(row=1, column=3, padx=6, pady=6)
        # }

        self.scrollbar.config(command=self.text_dcts.yview)

        self.print_dct_list()

    # Изменить значение MGSP
    def set_MGSP(self):
        global has_changes, min_good_score_perc

        val = self.var_MGSP.get()
        if val == '':
            min_good_score_perc = 0
        else:
            min_good_score_perc = int(val)
        has_changes = True

    # Настройки словоформ
    def forms(self):
        global has_changes

        FormsSettingsW(self).open()
        has_changes = True

    # Открыть словарь
    def dct_open(self):
        global dct, dct_savename, min_good_score_perc, form_parameters, has_changes

        saves_count = 0
        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                saves_list += [base_name]
                saves_count += 1
        if saves_count == 0:  # Если нет сохранённых словарей
            PopupMsgW(self, 'Нет других сохранённых словарей', title='Warning')
            return

        window = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите открыть')
        savename = window.open()
        if savename == '':
            return

        if has_changes:
            save_if_has_changes(self, dct, min_good_score_perc, form_parameters, dct_filename())

        dct_savename = savename
        with open(SETTINGS_PATH, 'w') as settings_file:
            settings_file.write(savename)
        dct = Dictionary()
        min_good_score_perc, form_parameters = read_dct(self, dct, savename)

        self.lbl_dct_name['text'] = f'Открыт словарь "{savename}"'
        has_changes = False

        self.print_dct_list()

    # Создать словарь
    def dct_create(self):
        global dct, dct_savename, min_good_score_perc, form_parameters, has_changes

        window = EnterSaveNameW(self)
        filename_is_correct, savename = window.open()
        if not filename_is_correct:
            return

        if has_changes:
            save_if_has_changes(self, dct, min_good_score_perc, form_parameters, dct_filename())
        dct_savename = savename
        with open(SETTINGS_PATH, 'w') as settings_file:
            settings_file.write(savename)
        dct = Dictionary()
        min_good_score_perc, form_parameters = create_dct(dct, savename)

        self.lbl_dct_name['text'] = f'Открыт словарь "{savename}"'
        has_changes = False

        self.print_dct_list()

    # Переименовать словарь
    def dct_rename(self):
        global dct_savename

        saves_count = 0
        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                saves_list += [base_name]
                saves_count += 1
        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите переименовать')
        old_savename = window_choose.open()
        old_filename = f'{old_savename}.txt'
        if old_savename == '':
            return

        window_rename = EnterSaveNameW(self)
        new_name_is_correct, new_savename = window_rename.open()
        new_filename = f'{new_savename}.txt'
        if not new_name_is_correct:
            return

        os.rename(os.path.join(SAVES_PATH, old_filename), os.path.join(SAVES_PATH, new_filename))
        os.rename(os.path.join(LOCAL_SETTINGS_PATH, old_filename), os.path.join(LOCAL_SETTINGS_PATH, new_filename))
        if dct_savename == old_savename:
            dct_savename = new_savename
            with open(SETTINGS_PATH, 'w') as set_file:
                set_file.write(new_savename)
            self.lbl_dct_name['text'] = f'Открыт словарь "{new_savename}"'
        print(f'Словарь "{old_savename}" успешно переименован в "{new_savename}"')

        self.print_dct_list()

    # Удалить словарь
    def dct_delete(self):
        saves_count = 0
        saves_list = []
        for filename in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(filename)
            if ext == '.txt':
                saves_list += [base_name]
                saves_count += 1
        if saves_count == 0:  # Если нет сохранённых словарей
            PopupMsgW(self, 'Нет других сохранённых словарей', title='Warning')
            return

        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите удалить')
        savename = window_choose.open()
        filename = f'{savename}.txt'
        if savename == '':
            return
        if savename == dct_savename:
            PopupMsgW(self, 'Вы не можете удалить словарь, который сейчас открыт', title='Warning')
            return

        window_confirm = PopupDialogueW(self, f'Словарь "{savename}" будет безвозвратно удалён!\nВы уверены?')
        answer = window_confirm.open()
        if not answer:
            return
        os.remove(os.path.join(SAVES_PATH, filename))
        os.remove(os.path.join(LOCAL_SETTINGS_PATH, filename))
        PopupMsgW(self, f'Словарь "{savename}" успешно удалён')

        self.print_dct_list()

    # Вывод существующих словарей
    def print_dct_list(self):
        self.text_dcts['state'] = 'normal'
        self.text_dcts.delete(1.0, tk.END)
        for filename in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(filename)
            if ext == '.txt':
                if filename == dct_filename():
                    self.text_dcts.insert(tk.INSERT, f'"{base_name}" (ОТКРЫТ)\n')
                else:
                    self.text_dcts.insert(tk.INSERT, f'"{base_name}"\n')
        self.text_dcts['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[st])

        self.var_word = tk.StringVar(value='')

        self.frame_head = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.lbl_header1 = tk.Label(self.frame_head, text='Anenokil development presents', font='StdFont 15', bg=ST_BG[st], fg=ST_FG_TEXT[st])
        self.lbl_header2 = tk.Label(self.frame_head, text=PROGRAM_NAME,                    font='Times 21',   bg=ST_BG[st], fg=ST_FG_LOGO[st])
        # }
        self.btn_print = tk.Button(self, text='Напечатать словарь', font='StdFont 12', command=self.print, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_learn = tk.Button(self, text='Учить слова',        font='StdFont 12', command=self.learn, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.frame_word = tk.LabelFrame(self, bg=ST_BG[st], highlightbackground=ST_BORDER[st], relief=ST_RELIEF[st])
        # {
        self.entry_word = tk.Entry(self.frame_word, textvariable=self.var_word, width=30, relief='solid', bg=ST_BG_FIELDS[st], fg=ST_FG_TEXT[st], highlightbackground=ST_BORDER[st], highlightcolor=ST_HIGHLIGHT[st], selectbackground=ST_SELECT[st])
        self.btn_search = tk.Button(self.frame_word, text='Найти статью',    font='StdFont 12', command=self.search, bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_edit   = tk.Button(self.frame_word, text='Изменить статью', font='StdFont 12', command=self.edit,   bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_add    = tk.Button(self.frame_word, text='Добавить статью', font='StdFont 12', command=self.add,    bg=ST_BTN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st], highlightbackground=ST_BORDER[st])
        # }
        self.btn_settings = tk.Button(self, text='Настройки',                      font='StdFont 12', command=self.settings, bg=ST_BTN[st],  fg=ST_FG_TEXT[st], activebackground=ST_BTN_SELECT[st],  highlightbackground=ST_BORDER[st])
        self.btn_save     = tk.Button(self, text='Сохранить изменения и прогресс', font='StdFont 12', command=self.save,     bg=ST_BTNY[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNY_SELECT[st], highlightbackground=ST_BORDER[st])
        self.btn_close    = tk.Button(self, text='Закрыть программу',              font='StdFont 12', command=self.close,    bg=ST_BTNN[st], fg=ST_FG_TEXT[st], activebackground=ST_BTNN_SELECT[st], highlightbackground=ST_BORDER[st])

        self.lbl_footer = tk.Label(self, text=f'{PROGRAM_VERSION} - {PROGRAM_DATE}', font='StdFont 8', bg=ST_BG[st], fg=ST_FG_FOOTER[st])

        self.frame_head.grid(row=0, padx=6, pady=4)
        # {
        self.lbl_header1.grid(row=0, padx=7, pady=(7, 0))
        self.lbl_header2.grid(row=1, padx=7, pady=(0, 7))
        # }
        self.btn_print.grid( row=1, pady=5)
        self.btn_learn.grid( row=2, pady=5)
        self.frame_word.grid(row=3, padx=6, pady=5)
        # {
        self.entry_word.grid(row=0, padx=3, pady=(5, 0))
        self.btn_search.grid(row=1, padx=3, pady=(5, 0))
        self.btn_edit.grid(  row=2, padx=3, pady=(5, 0))
        self.btn_add.grid(   row=3, padx=3, pady=5)
        # }
        self.btn_settings.grid(row=4, pady=5)
        self.btn_save.grid(    row=5, pady=5)
        self.btn_close.grid(   row=6, pady=5)

        self.lbl_footer.grid(row=7, padx=7, pady=(0, 3), sticky='S')

    # Поиск статьи
    def search(self):
        wrd = self.var_word.get()
        SearchW(self, wrd).open()

    # Добавление статьи
    def add(self):
        wrd = self.var_word.get()
        key = AddW(self, wrd).open()
        if not key:
            return
        EditW(self, key).open()

    # Изменение статьи
    def edit(self):
        wrd = self.var_word.get()
        if wrd_to_key(wrd, 0) not in dct.d.keys():
            ParticularMatchesW(self, wrd).open()
            return
        key = dct.choose_one_of_similar_entries(self, wrd)
        EditW(self, key).open()

    # Печать словаря
    def print(self):
        PrintW(self).open()

    # Учить слова
    def learn(self):
        res = ChooseLearnModeW(self).open()
        if not res:
            return
        LearnW(self, res).open()

    # Открыть настройки
    def settings(self):
        SettingsW(self).open()

    # Сохранить изменения
    def save(self):
        global has_changes

        save_all(dct, min_good_score_perc, form_parameters, dct_filename())
        PopupMsgW(self, 'Изменения и прогресс успешно сохранены')
        print('\nИзменения и прогресс успешно сохранены')

        has_changes = False

    # Закрытие программы
    def close(self):
        if has_changes:
            save_if_has_changes(self, dct, min_good_score_perc, form_parameters, dct_filename())
        self.quit()


# Вывод информации о программе
print( '======================================================================================\n')
print( '                            Anenokil development  presents')
print(f'                               {PROGRAM_NAME} {PROGRAM_VERSION}')
print(f'                                {PROGRAM_DATE}\n')
print( '======================================================================================')

try:  # Открываем файл с названием словаря
    open(SETTINGS_PATH, 'r')
except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
    with open(SETTINGS_PATH, 'w') as set_file:
        set_file.write('words.txt')
with open(SETTINGS_PATH, 'r') as set_file:
    dct_savename = set_file.readline().strip()


# Получить название файла с открытым словарём
def dct_filename():
    return f'{dct_savename}.txt'


dct = Dictionary()
has_changes = False
root = MainW()
min_good_score_perc, form_parameters = read_dct(root, dct, dct_savename)  # Загружаем словарь и его настройки
print('\nМожете использовать эти комбинации для немецких букв: #a -> ä, #o -> ö, #u -> ü, #s -> ß (и ## -> #)')
root.mainloop()

# строка 56 - добавить выбор стилей
# Попробовать tk.ScrolledText
# при поиске перевода выводить слово
# добавить изменение статьи по переводу
# добавить комментарии
# PopupMsgW.open() где надо а где нет
# PopupEntryW и другие: onClose
# сделать покрасивее поле выбора нового словаря при ошибке загрузки
# проверить корректность работы переименовывания значения параметра формы слова
