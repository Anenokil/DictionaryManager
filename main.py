import os
import random

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

FORMS_SEPARATOR = '@'

"""
    Про формы:

    apple - слово
    apples - форма слова
    число - параметр формы слова
    мн.ч., ед.ч. - значения параметра формы слова
"""


# Ввод
def inp(_text=''):
    return input(_text)


# Вывод
def outp(_text='', _end='\n'):
    print(_text, end=_end)


# Вывести предупреждение о некорректном вводе с указанием ввода
def warn_inp(_text, _input):
    outp(f'[!] {_text}: "{_input}" [!]')


# Вывести другое предупреждение
def warn(_text):
    outp(f'[!] {_text} [!]')


# Вывести предложение специального действия
def spec_action(_text):
    outp(f'{_text} (*)')


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


# Заменить немецкие буквы английскими (для find_matches)
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
def add_frm_param_val(_vals):
    _new_v = inp('\nВведите новое значение параметра: ')
    if _new_v in _vals:
        warn(f'Значение "{_new_v}" уже существует')
    elif _new_v == '':
        warn('Недопустимое значение')
    elif FORMS_SEPARATOR in _new_v:
        warn_inp('Недопустимый символ', FORMS_SEPARATOR)
    else:
        _vals += [_new_v]


# Удалить значение параметра форм
def remove_frm_param_val(_vals, _dct):
    if len(_vals) == 1:
        warn('\nВы не можете удалить единственное значение параметра')
        return
    outp('\nВыберите один из предложенных вариантов')
    for _i in range(len(_vals)):
        outp(f'{_i + 1} - {_vals[_i]}')
    _cmd = inp('Введите номер варианта: ')
    try:
        _index = int(_cmd) - 1
        _val = _vals[_index]
    except (ValueError, TypeError, IndexError):
        warn_inp('Недопустимый номер варианта', _cmd)
    else:
        _cmd = inp('\nВсе формы слов, содержащие это значение, будут удалены! Вы уверены? (+ или -): ')
        if _cmd == '+':
            _vals.pop(_index)
            _dct.remove_forms_with_val(_index, _val)


# Переименовать значение параметра форм
def rename_frm_param_val(_vals, _pos, _dct):
    outp('\nВыберите один из предложенных вариантов')
    for _i in range(len(_vals)):
        outp(f'{_i + 1} - {_vals[_i]}')
    _cmd = inp('Введите номер варианта: ')
    try:
        _index = int(_cmd) - 1
        _val = _vals[_index]
    except (ValueError, TypeError, IndexError):
        warn_inp('Недопустимый номер варианта', _cmd)
    else:
        while True:
            _new_val = inp('\nВведите новое название для значения параметра: ')
            if _new_val not in _vals:
                break
            warn('Значение с таким названием уже есть')
        _dct.rename_forms_with_val(_pos, _val, _new_val)
        _vals[_index] = _new_val


# Выбрать значение одного из параметров формы слова
def choose_frm_param_val(_par, _par_vals):
    while True:
        outp(f'\nВыберите {_par}')
        for _i in range(len(_par_vals)):
            outp(f'{_i + 1} - {_par_vals[_i]}')
        spec_action('Н - Не указывать/Неприменимо')
        spec_action('Д - Добавить новый вариант')
        _cmd = inp().upper()
        if _cmd in ['Н', 'Y']:
            return ''
        elif _cmd in ['Д', 'L']:
            add_frm_param_val(_par_vals)
        else:
            try:
                return _par_vals[int(_cmd) - 1]
            except (ValueError, TypeError, IndexError):
                warn_inp('Недопустимый вариант', _cmd)


# Создать шаблон для новой формы слова
def construct_frm_template(_form_parameters):
    _res = []
    _parameters = list(_form_parameters.keys())
    outp('Выберите параметр')
    for _i in range(len(_parameters)):
        outp(f'{_i + 1} - {_parameters[_i]}')
        _res += ['']
    _void_frm = _res.copy()
    _cmd = inp()

    while True:
        try:
            _index = int(_cmd) - 1
            _par = _parameters[_index]
            _res[_index] = choose_frm_param_val(_par, _form_parameters[_par])
        except (ValueError, TypeError, IndexError):
            warn_inp('Недопустимый вариант', _cmd)

        _is_void = (_res == _void_frm)
        outp()
        if not _is_void:
            outp(f'Текущий шаблон формы: {tpl(_res)}\n')

        outp('Выберите параметр')
        for _i in range(len(_parameters)):
            outp(f'{_i + 1} - {_parameters[_i]}')
        if not _is_void:
            spec_action('З - Закончить с шаблоном и ввести форму слова')

        _cmd = inp()
        if _cmd.upper() in ['З', 'P']:
            if not _is_void:
                break
    return tuple(_res)


# Найти в строке подстроку и выделить её
def find_matches(_wrd, _search_wrd):
    _len = len(_search_wrd)
    if _wrd != _search_wrd:
        _pos = deu_to_eng(_wrd).lower().find(deu_to_eng(_search_wrd).lower())
        if _pos != -1:
            _coded_wrd = code(_wrd)
            _end = _pos + _len
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

    # Напечатать перевод
    def tr_print(self, _end='\n'):
        if self.count_t != 0:
            outp(code(self.tr[0]), _end='')
        for _i in range(1, self.count_t):
            outp(f', {code(self.tr[_i])}', _end='')
        outp(_end, _end='')

    # Напечатать сноски
    def notes_print(self, _tab=0):
        for _i in range(self.count_n):
            outp(' ' * _tab + f'> {code(self.notes[_i])}')

    # Напечатать формы слова
    def frm_print(self, _tab=0):
        for _key in self.forms.keys():
            outp(' ' * _tab + f'[{tpl(_key)}] {code(self.forms[_key])}')

    # Напечатать статистику
    def stat_print(self, _min_good_score_perc, _end='\n'):
        if self.last_att == -1:
            outp('[-:  0%]', _end=_end)
        else:
            _score = '{:.0%}'.format(self.score)
            _tab = ' ' * (4 - len(_score))
            outp(f'[{self.last_att}:{_tab}{_score}]', _end=_end)

    # Служебный метод для print_briefly и print_briefly_with_forms
    def _print_briefly(self, _min_good_score_perc):
        if self.fav:
            outp('(*)', _end=' ')
        else:
            outp('   ', _end=' ')
        self.stat_print(_min_good_score_perc, _end=' ')
        outp(f'{code(self.wrd)}: ', _end='')
        self.tr_print()

    # Напечатать статью - кратко
    def print_briefly(self, _min_good_score_perc):
        self._print_briefly(_min_good_score_perc)
        self.notes_print(_tab=13)

    # Напечатать статью - кратко с формами
    def print_briefly_with_forms(self, _min_good_score_perc):
        self._print_briefly(_min_good_score_perc)
        self.frm_print(_tab=13)
        self.notes_print(_tab=13)

    # Напечатать статью - слово со статистикой
    def print_wrd_with_stat(self, _min_good_score_perc):
        outp(code(self.wrd), _end=' ')
        self.stat_print(_min_good_score_perc)

    # Напечатать статью - перевод со статистикой
    def print_tr_with_stat(self, _min_good_score_perc):
        self.tr_print(_end=' ')
        self.stat_print(_min_good_score_perc)

    # Напечатать статью - перевод с формой и со статистикой
    def print_tr_and_frm_with_stat(self, _frm_key, _min_good_score_perc):
        self.tr_print(_end=' ')
        outp(f'({tpl(_frm_key)})', _end=' ')
        self.stat_print(_min_good_score_perc)

    # Напечатать статью - со всей редактируемой информацией
    def print_editable(self):
        outp(f'       Слово: {code(self.wrd)}')
        outp('     Перевод: ', _end='')
        self.tr_print()
        outp(' Формы слова: ', _end='')
        if self.count_f == 0:
            outp('-')
        else:
            _keys = [_key for _key in self.forms.keys()]
            outp(f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}')
            for _i in range(1, self.count_f):
                outp(f'              [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        outp('      Сноски: ', _end='')
        if self.count_n == 0:
            outp('-')
        else:
            outp(f'> {code(self.notes[0])}')
            for _i in range(1, self.count_n):
                outp(f'              > {code(self.notes[_i])}')
        outp(f'   Избранное: {self.fav}')

    # Напечатать статью - со всей информацией
    def print_all(self):
        outp(f'       Слово: {code(self.wrd)}')
        outp('     Перевод: ', _end='')
        self.tr_print()
        outp(' Формы слова: ', _end='')
        if self.count_f == 0:
            outp('-')
        else:
            _keys = [_key for _key in self.forms.keys()]
            outp(f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}')
            for _i in range(1, self.count_f):
                outp(f'              [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        outp('      Сноски: ', _end='')
        if self.count_n == 0:
            outp('-')
        else:
            outp(f'> {code(self.notes[0])}')
            for _i in range(1, self.count_n):
                outp(f'              > {code(self.notes[_i])}')
        outp(f'   Избранное: {self.fav}')
        if self.last_att == -1:
            outp('  Статистика: 1) Последних неверных ответов: -')
            outp('              2) Доля верных ответов: 0')
        else:
            outp(f'  Статистика: 1) Последних неверных ответов: {self.last_att}')
            outp(f'              2) Доля верных ответов: '
                 f'{self.correct_att}/{self.all_att} = ' + '{:.0%}'.format(self.score))

    # Добавить перевод
    def add_tr(self, _new_tr, _show_msg=True):
        if _new_tr not in self.tr:
            self.tr += [_new_tr]
            self.count_t += 1
        elif _show_msg:
            warn('У этого слова уже есть такой перевод')

    # Добавить сноску
    def add_note(self, _new_note):
        self.notes += [_new_note]
        self.count_n += 1

    # Добавить форму слова
    def add_frm(self, _frm_key, _new_frm, _show_msg=True):
        if _new_frm == '':
            warn('Форма должна содержать хотя бы один символ')
        elif _frm_key not in self.forms.keys():
            self.forms[_frm_key] = _new_frm
            self.count_f += 1
        elif _show_msg:
            warn(f'Слово уже имеет форму с такими параметрами {tpl(_frm_key)}: {self.forms[_frm_key]}')

    # Удалить перевод
    def remove_tr_with_choose(self):
        if self.count_t == 1:
            warn('Вы не можете удалить единственный перевод слова')
            return
        outp('Выберите один из предложенных вариантов')
        for _i in range(self.count_t):
            outp(f'{_i + 1} - {code(self.tr[_i])}')
        _cmd = inp('Введите номер варианта: ')
        try:
            self.tr.pop(int(_cmd))
        except (ValueError, TypeError, IndexError):
            warn_inp('Недопустимый номер варианта', _cmd)
        else:
            self.count_t -= 1

    # Удалить сноску
    def remove_note_with_choose(self):
        outp('Выберите один из предложенных вариантов')
        for _i in range(self.count_n):
            outp(f'{_i + 1} - {code(self.notes[_i])}')
        _cmd = inp('Введите номер варианта: ')
        try:
            self.notes.pop(int(_cmd) - 1)
        except (ValueError, TypeError, IndexError):
            warn_inp('Недопустимый номер варианта', _cmd)
        else:
            self.count_n -= 1

    # Удалить форму слова
    def remove_frm_with_choose(self):
        _keys = [_key for _key in self.forms.keys()]
        outp('Выберите один из предложенных вариантов')
        for _i in range(self.count_f):
            outp(f'{_i + 1} - [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        _cmd = inp('Введите номер варианта: ')
        try:
            _key = _keys[int(_cmd) - 1]
        except (ValueError, TypeError, IndexError):
            warn_inp('Недопустимый номер варианта', _cmd)
        else:
            self.forms.pop(_key)
            self.count_f -= 1

    # Изменить форму слова
    def edit_frm_with_choose(self):
        _keys = [_key for _key in self.forms.keys()]
        outp('Выберите один из предложенных вариантов')
        for _i in range(self.count_f):
            outp(f'{_i + 1} - [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        _cmd = inp('Введите номер варианта: ')
        try:
            _key = _keys[int(_cmd) - 1]
        except (ValueError, TypeError, IndexError):
            warn_inp('Недопустимый номер варианта', _cmd)
        else:
            _new_frm = inp('Введите форму слова: ')
            if _new_frm == '':
                warn('Форма должна содержать хотя бы один символ')
            else:
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


# Угадать слово по переводу
def guess_wrd(_entry, _count_correct, _count_all, _min_good_score_perc):
    outp()
    _entry.print_tr_with_stat(_min_good_score_perc)
    _ans = inp('Введите слово (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _ans == '@':
        _entry.notes_print()
        _ans = inp('Введите слово (# - чтобы закончить): ')
    if _ans == '#':
        outp(f'Ваш результат: {_count_correct}/{_count_all}')
        return 1

    if _ans == _entry.wrd:
        _entry.correct()
        outp('Верно')
        if _entry.fav:
            _fav = inp('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _entry.fav = False
        return 2
    else:
        _entry.incorrect()
        outp(f'Неверно. Правильный ответ: "{_entry.wrd}"')
        if not _entry.fav:
            _fav = inp('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _entry.fav = True
        return 3


# Угадать словоформу по переводу
def guess_form(_entry, _wrd_f, _count_correct, _count_all, _min_good_score_perc):
    outp()
    _entry.print_tr_and_frm_with_stat(_wrd_f, _min_good_score_perc)
    _ans = inp('Введите слово в данной форме (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _ans == '@':
        _entry.notes_print()
        _ans = inp('Введите слово в данной форме (# - чтобы закончить): ')
    if _ans == '#':
        outp(f'Ваш результат: {_count_correct}/{_count_all}')
        return 1

    if _ans == _entry.forms[_wrd_f]:
        _entry.correct()
        outp('Верно')
        if _entry.fav:
            _fav = inp('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _entry.fav = False
        return 2
    else:
        _entry.incorrect()
        outp(f'Неверно. Правильный ответ: "{_entry.forms[_wrd_f]}"')
        if not _entry.fav:
            _fav = inp('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _entry.fav = True
        return 3


# Угадать перевод по слову
def guess_tr(_entry, _count_correct, _count_all, _min_good_score_perc):
    outp()
    _entry.print_wrd_with_stat(_min_good_score_perc)
    _ans = inp('Введите перевод (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _ans == '@':
        _entry.notes_print()
        _ans = inp('Введите перевод (# - чтобы закончить): ')
    if _ans == '#':
        outp(f'Ваш результат: {_count_correct}/{_count_all}')
        return 1

    if _ans in _entry.tr:
        _entry.correct()
        outp('Верно')
        if _entry.fav:
            _fav = inp('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _entry.fav = False
        return 2
    else:
        _entry.incorrect()
        outp(f'Неверно. Правильный ответ: {_entry.tr}')
        if not _entry.fav:
            _fav = inp('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _entry.fav = True
        return 3


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
    elif _n % 10 < 5:
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
    def _print_stat(self):
        _w = set_postfix(self.count_w, ('слово', 'слова', 'слов'))
        _f = set_postfix(self.count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        _t = set_postfix(self.count_t, ('перевод', 'перевода', 'переводов'))
        outp(f'< {self.count_w} {_w} | {self.count_w + self.count_f} {_f} | {self.count_t} {_t} >')

    # Напечатать словарь
    def print(self, _min_good_score_perc):
        for _entry in self.d.values():
            _entry.print_briefly(_min_good_score_perc)
        self._print_stat()

    # Напечатать словарь (со всеми формами)
    def print_with_forms(self, _min_good_score_perc):
        for _entry in self.d.values():
            _entry.print_briefly_with_forms(_min_good_score_perc)
        self._print_stat()

    # Служебный метод для print_fav и print_fav_with_forms
    def _print_stat_fav(self, _count_w, _count_t, _count_f):
        _w = set_postfix(_count_w, ('слово', 'слова', 'слов'))
        _f = set_postfix(_count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        _t = set_postfix(_count_t, ('перевод', 'перевода', 'переводов'))
        outp(f'< {_count_w}/{self.count_w} {_w} | '
             f'{_count_w + _count_f}/{self.count_w + self.count_f} {_f} | '
             f'{_count_t}/{self.count_t} {_t} >')

    # Напечатать словарь (только избранные слова)
    def print_fav(self, _min_good_score_perc):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _entry in self.d.values():
            if _entry.fav:
                _entry.print_briefly(_min_good_score_perc)
                _count_w += 1
                _count_t += _entry.count_t
                _count_f += _entry.count_f
        self._print_stat_fav(_count_w, _count_t, _count_f)

    # Напечатать словарь (только избранные слова, со всеми формами)
    def print_fav_with_forms(self, _min_good_score_perc):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _entry in self.d.values():
            if _entry.fav:
                _entry.print_briefly_with_forms(_min_good_score_perc)
                _count_w += 1
                _count_t += _entry.count_t
                _count_f += _entry.count_f
        self._print_stat_fav(_count_w, _count_t, _count_f)

    # Напечатать статьи, в которых слова содержат данную строку
    def print_words_with_str(self, _search_wrd):
        _is_found = False
        for _key in self.d.keys():
            _wrd = key_to_wrd(_key)
            _res = find_matches(_wrd, _search_wrd)
            if _res != '':
                _is_found = True
                outp(_res)
        if not _is_found:
            outp('Частичных совпадений не найдено')

    # Напечатать статьи, в которых переводы содержат данную строку
    def print_translations_with_str(self, _search_tr):
        _is_found = False
        for _entry in self.d.values():
            _is_first = True
            for _tr in _entry.tr:
                _res = find_matches(_tr, _search_tr)
                if _res != '':
                    _is_found = True
                    if _is_first:
                        _is_first = False
                        outp()
                    else:
                        outp(', ', _end='')
                    outp(_res, _end='')
        outp()
        if not _is_found:
            outp('Частичных совпадений не найдено')

    # Выбрать одну статью из нескольких с одинаковыми словами
    def choose_one_of_similar_entries(self, _wrd):
        if wrd_to_key(_wrd, 1) not in self.d.keys():
            return wrd_to_key(_wrd, 0)
        outp('\nВыберите одну из статей')
        _max_i = MAX_SAME_WORDS - 1
        for _i in range(MAX_SAME_WORDS):
            _key = wrd_to_key(_wrd, _i)
            if _key not in self.d.keys():
                _max_i = _i - 1
                break
            outp(f'\n({_i + 1})')
            self.d[_key].print_all()
        while True:
            _cmd = inp('\nВведите номер варианта: ')
            try:
                _index = int(_cmd) - 1
            except (ValueError, TypeError):
                warn_inp('Недопустимый номер варианта', _cmd)
            else:
                if _index < 0 or _index > _max_i:
                    warn_inp('Недопустимый номер варианта', _cmd)
                else:
                    return wrd_to_key(_wrd, _index)

    # Добавить перевод к статье
    def add_tr(self, _key_or_wrd, _tr, _show_msg=True, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_t -= self.d[_key].count_t
        self.d[_key].add_tr(_tr, _show_msg)
        self.count_t += self.d[_key].count_t

    # Добавить сноску к статье
    def add_note(self, _key_or_wrd, _note, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.d[_key].add_note(_note)

    # Добавить форму слова к статье
    def add_frm(self, _key_or_wrd, _frm_key, _frm, _show_msg=True, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_f -= self.d[_key].count_f
        self.d[_key].add_frm(_frm_key, _frm, _show_msg)
        self.count_f += self.d[_key].count_f

    # Изменить слово в статье
    def edit_wrd(self, _key, _new_wrd):
        if wrd_to_key(_new_wrd, 0) in self.d.keys():  # Если уже есть статья с таким словом
            while True:
                outp('\nСтатья с таким словом уже есть в словаре')
                outp('Что вы хотите сделать?')
                outp('Д - Добавить к существующей статье')
                outp('Н - создать Новую статью')
                spec_action('О - Отмена')
                _cmd = inp().upper()
                if _cmd in ['Д', 'L']:
                    _new_key = self.choose_one_of_similar_entries(_new_wrd)

                    self.count_t -= self.d[_key].count_t
                    self.count_t -= self.d[_new_key].count_t
                    self.count_f -= self.d[_key].count_f
                    self.count_f -= self.d[_new_key].count_f

                    for _tr in self.d[_key].tr:
                        self.d[_new_key].add_tr(_tr, False)
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
                elif _cmd in ['Н', 'Y']:
                    for _i in range(MAX_SAME_WORDS):
                        _new_key = wrd_to_key(_new_wrd, _i)
                        if _new_key not in self.d.keys():
                            self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                                     self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                                     self.d[_key].last_att)
                            self.d.pop(_key)
                            return _new_key
                        _i += 1
                    warn('Слишком много статей с одинаковым словом')
                elif _cmd in ['О', 'J']:
                    return _key
                else:
                    warn_inp('Неизвестная команда', _cmd)
        else:  # Если ещё нет статьи с таким словом
            _new_key = wrd_to_key(_new_wrd, 0)
            self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                     self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                     self.d[_key].last_att)
            self.d.pop(_key)
            return _new_key

    # Изменить форму слова в статье
    def edit_frm_with_choose(self, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.d[_key].edit_frm_with_choose()

    # Удалить перевод в статье
    def remove_tr_with_choose(self, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_t -= self.d[_key].count_t
        self.d[_key].remove_tr_with_choose()
        self.count_t += self.d[_key].count_t

    # Удалить описание в статье
    def remove_note_with_choose(self, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.d[_key].remove_note_with_choose()

    # Удалить форму слова в статье
    def remove_frm_with_choose(self, _key_or_wrd, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        self.count_f -= self.d[_key].count_f
        self.d[_key].remove_frm_with_choose()
        self.count_f += self.d[_key].count_f

    # Добавить статью в словарь (для пользователя)
    def add_entry(self, _wrd, _tr, _show_msg=True):
        if wrd_to_key(_wrd, 0) in self.d.keys():  # Если уже есть статья с таким словом
            while True:
                outp('\nСтатья с таким словом уже есть в словаре')
                outp('Что вы хотите сделать?')
                outp('Д - Добавить к существующей статье')
                outp('Н - создать Новую статью')
                _cmd = inp().upper()
                if _cmd in ['Д', 'L']:
                    _key = self.choose_one_of_similar_entries(_wrd)
                    self.add_tr(_key, _tr, _show_msg, _is_key=True)
                    return _key
                elif _cmd in ['Н', 'Y']:
                    for _i in range(MAX_SAME_WORDS):
                        _key = wrd_to_key(_wrd, _i)
                        if _key not in self.d.keys():
                            self.d[_key] = Entry(_wrd, [_tr])
                            self.count_w += 1
                            self.count_t += 1
                            return _key
                        _i += 1
                    warn('Слишком много статей с одинаковым словом')
                else:
                    warn_inp('Неизвестная команда', _cmd)
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

    # Изменить статью
    def edit_entry(self, _key_or_wrd, _form_parameters, _is_key=False):
        _key = _key_or_wrd if _is_key else self.choose_one_of_similar_entries(_key_or_wrd)
        _has_changes = False
        while True:
            outp()
            self.d[_key].print_editable()
            outp('\nЧто вы хотите сделать?')
            outp('СЛ - изменить СЛово')
            outp('П  - изменить Перевод')
            outp('Ф  - изменить Формы слова')
            outp('СН - изменить СНоски')
            if self.d[_key].fav:
                outp('И  - убрать из Избранного')
            else:
                outp('И  - добавить в Избранное')
            outp('У  - Удалить статью')
            spec_action('Н  - Назад')
            _cmd = inp().upper()
            if _cmd in ['СЛ', 'CK']:
                _new_wrd = inp('\nВведите новое слово: ')
                if _new_wrd == key_to_wrd(_key):
                    warn('Это то же самое слово')
                else:
                    _key = self.edit_wrd(_key, _new_wrd)
                    _has_changes = True
            elif _cmd in ['П', 'G']:
                outp('\nЧто вы хотите сделать?')
                outp('Д - Добавить перевод')
                outp('У - Удалить перевод')
                spec_action('Н - Назад')
                _cmd = inp().upper()
                if _cmd in ['Д', 'L']:
                    _tr = inp('\nВведите перевод: ')
                    if _tr == '':
                        warn('Перевод должен содержать хотя бы один символ')
                        continue
                    self.add_tr(_key, _tr, _is_key=True)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    outp()
                    self.remove_tr_with_choose(_key, _is_key=True)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    warn_inp('Неизвестная команда', _cmd)
            elif _cmd in ['Ф', 'A']:
                outp('\nЧто вы хотите сделать?')
                outp('Д - Добавить форму')
                outp('И - Изменить форму')
                outp('У - Удалить форму')
                spec_action('Н - Назад')
                _cmd = inp().upper()
                if _cmd in ['Д', 'L']:
                    outp()
                    _frm_key = construct_frm_template(_form_parameters)
                    if _frm_key in self.d[_key].forms.keys():
                        warn(f'\nУ слова "{key_to_wrd(_key)}" уже есть форма с такими параметрами')
                    else:
                        _frm = inp('\nВведите форму слова: ')
                        self.add_frm(_key, _frm_key, _frm, _is_key=True)
                        _has_changes = True
                elif _cmd in ['И', 'B']:
                    outp()
                    if self.d[_key].count_f == 0:
                        warn(f'У слова "{key_to_wrd(_key)}" нет других форм')
                        continue
                    self.edit_frm_with_choose(_key, _is_key=True)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    outp()
                    if self.d[_key].count_f == 0:
                        warn(f'У слова "{key_to_wrd(_key)}" нет других форм')
                        continue
                    self.remove_frm_with_choose(_key, _is_key=True)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    warn_inp('Неизвестная команда', _cmd)
            elif _cmd in ['СН', 'CY']:
                outp('\nЧто вы хотите сделать?')
                outp('Д - Добавить сноску')
                outp('У - Удалить сноску')
                spec_action('Н - Назад')
                _cmd = inp().upper()
                if _cmd in ['Д', 'L']:
                    _note = inp('\nВведите сноску: ')
                    self.add_note(_key, _note, _is_key=True)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    outp()
                    if self.d[_key].count_n == 0:
                        warn('В этой статье нет сносок')
                        continue
                    self.remove_note_with_choose(_key, _is_key=True)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    warn_inp('Неизвестная команда', _cmd)
            elif _cmd in ['И', 'B']:
                self.d[_key].fav = not self.d[_key].fav
                _has_changes = True
            elif _cmd in ['У', 'E']:
                _cmd = inp('\nВы уверены, что хотите удалить эту статью? (+ или -): ')
                if _cmd == '+':
                    self.remove_entry(_key, _is_key=True)
                    _has_changes = True
                    break
            elif _cmd in ['Н', 'Y']:
                break
            else:
                warn_inp('Неизвестная команда', _cmd)
        return _has_changes

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

    # Учить слова - все
    def learn(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                if _key not in _used_words:
                    break

            _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова - избранные
    def learn_fav(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w:
                    outp(f'Ваш результат: {_count_correct}/{_count_all}')
                    return
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add(_key)
                    continue
                if _key not in _used_words:
                    break

            _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова - все, сначала сложные
    def learn_hard(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = self.random_hard(_min_good_score_perc)
                if _key not in _used_words:
                    break

            _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (словоформы) - все
    def learn_f(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w + self.count_f:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
                        break
                else:
                    _wrd_f = list(self.d[_key].forms.keys())[_rnd_f]
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_form(self.d[_key], _wrd_f, _count_correct, _count_all, _min_good_score_perc)
                        break

            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add((_key, _wrd_f))
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (словоформы) - избранные
    def learn_f_fav(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w + self.count_f:
                    outp(f'Ваш результат: {_count_correct}/{_count_all}')
                    return
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add((_key, _key))
                    for _frm in self.d[_key].forms.keys():
                        _used_words.add((_key, _frm))
                    continue
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
                        break
                else:
                    _wrd_f = list(self.d[_key].forms.keys())[_rnd_f]
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_form(self.d[_key], _wrd_f, _count_correct, _count_all, _min_good_score_perc)
                        break

            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add((_key, _wrd_f))
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (словоформы) - все, сначала сложные
    def learn_f_hard(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w + self.count_f:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = self.random_hard(_min_good_score_perc)
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_wrd(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
                        break
                else:
                    _wrd_f = list(self.d[_key].forms.keys())[_rnd_f]
                    if (_key, _wrd_f) not in _used_words:
                        _res_code = guess_form(self.d[_key], _wrd_f, _count_correct, _count_all, _min_good_score_perc)
                        break

            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add((_key, _wrd_f))
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (обр.) - все
    def learn_t(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                if _key not in _used_words:
                    break

            _res_code = guess_tr(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (обр.) - избранные
    def learn_t_fav(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w:
                    outp(f'Ваш результат: {_count_correct}/{_count_all}')
                    return
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add(_key)
                    continue
                if _key not in _used_words:
                    break

            _res_code = guess_tr(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

    # Учить слова (обр.) - все, сначала сложные
    def learn_t_hard(self, _min_good_score_perc):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                outp(f'Ваш результат: {_count_correct}/{_count_all}')
                break
            while True:
                _key = self.random_hard(_min_good_score_perc)
                if _key not in _used_words:
                    break

            _res_code = guess_tr(self.d[_key], _count_correct, _count_all, _min_good_score_perc)
            if _res_code == 1:
                break
            elif _res_code == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res_code == 3:
                _count_all += 1

        return True

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
                        self.add_tr(_key, _line[1:], False, _is_key=True)
                    elif _line[0] == 'd':
                        self.add_note(_key, _line[1:], _is_key=True)
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
                                f'м.р.{FORMS_SEPARATOR}ж.р.{FORMS_SEPARATOR}с.р.\n'
                                'Падеж\n'
                                f'им.п.{FORMS_SEPARATOR}род.п.{FORMS_SEPARATOR}дат.п.{FORMS_SEPARATOR}вин.п.\n'
                                'Лицо\n'
                                f'1 л.{FORMS_SEPARATOR}2 л.{FORMS_SEPARATOR}3 л.\n'
                                'Время\n'
                                f'пр.вр.{FORMS_SEPARATOR}н.вр.{FORMS_SEPARATOR}б.вр.')

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
def read_dct(_dct, _filename):
    _filepath = os.path.join(SAVES_PATH, _filename)
    _res_code = _dct.read(_filepath)
    outp()
    if _res_code == 0:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        outp(f'Файл со словарём "{_filename}" открыт')
        return read_local_settings(_filename)
    elif _res_code == 1:  # Если файл отсутствует, то создаётся пустой словарь
        warn(f'Файл "{_filename}" не найден')
        open(_filepath, 'w')
        _dct.read(_filepath)
        outp('Создан и открыт файл с пустым словарём')
        return read_local_settings(_filename)
    elif _res_code == 2:  # Если файл повреждён, то предлагается открыть другой файл
        warn(f'Файл "{_filename}" повреждён или некорректен')
        while True:
            outp('\nХотите открыть другой словарь?')
            outp('О - Открыть другой словарь')
            outp('З - Завершить работу')
            _cmd = inp().upper()
            if _cmd in ['О', 'J']:
                _filename = inp('\nВведите название файла со словарём '
                                '(если он ещё не существует, то будет создан пустой словарь): ')
                with open(SETTINGS_PATH, 'w') as _set_file:
                    _set_file.write(dct_filename)
                _dct = Dictionary()
                read_dct(_dct, _filename)
                break
            elif _cmd in ['З', 'P']:
                exit()
            else:
                warn_inp('Неизвестная команда', _cmd)


# Создать и загрузить пустой словарь
def create_dct(_dct, _filename):
    _filepath = os.path.join(SAVES_PATH, _filename)
    open(_filepath, 'w')
    _dct.read(_filepath)
    outp(f'\nФайл "{_filename}" успешно создан и открыт')
    return read_local_settings(_filename)


# Сохранить словарь и его настройки
def save_all(_dct, _min_good_score_perc, _form_parameters, _filename):
    _filepath = os.path.join(SAVES_PATH, _filename)
    _dct.save(_filepath)
    save_local_settings(_min_good_score_perc, _form_parameters, _filename)


# Предложить сохранение, если были изменения
def save_if_has_changes(_dct, _min_good_score_perc, _form_parameters, _filename):
    _cmd = inp('\nХотите сохранить изменения и свой прогресс? (+ или -): ')
    if _cmd == '+':
        save_all(_dct, _min_good_score_perc, _form_parameters, _filename)
        outp('\nИзменения и прогресс успешно сохранены')


# Добавить параметр словоформ
def add_frm_param(_parameters, _dct):
    _new_p = inp('\nВведите название нового параметр: ')
    if _new_p in _parameters.keys():
        warn(f'Параметр "{_new_p}" уже существует')
    elif _new_p == '':
        warn('Недопустимое название параметра')
    else:
        _dct.add_forms_param()
        _parameters[_new_p] = []
        outp('Необходимо добавить хотя бы одно значение для параметра')
        while not _parameters[_new_p]:
            add_frm_param_val(_parameters[_new_p])


# Удалить параметр словоформ
def remove_frm_param(_parameters, _dct):
    outp('\nВыберите один из предложенных вариантов')
    _keys = [_key for _key in _parameters.keys()]
    for _i in range(len(_keys)):
        outp(f'{_i + 1} - {_keys[_i]}')
    _cmd = inp('Введите номер варианта: ')
    try:
        _index = int(_cmd) - 1
        _key = _keys[_index]
    except (ValueError, TypeError, IndexError):
        warn_inp('Недопустимый номер варианта', _cmd)
    else:
        _cmd = inp('\nВсе формы слов, содержащие этот параметр, будут удалены! Вы уверены? (+ или -): ')
        if _cmd == '+':
            _parameters.pop(_key)
            _dct.remove_forms_param(_index)


# Переименовать параметр словоформ
def rename_frm_param(_parameters, _dct):
    outp('\nВыберите один из предложенных вариантов')
    _keys = [_key for _key in _parameters.keys()]
    for _i in range(len(_keys)):
        outp(f'{_i + 1} - {_keys[_i]}')
    _cmd = inp('Введите номер варианта: ')
    try:
        _index = int(_cmd) - 1
        _key = _keys[_index]
    except (ValueError, TypeError, IndexError):
        warn_inp('Недопустимый номер варианта', _cmd)
    else:
        while True:
            _new_key = inp('\nВведите новое название параметра: ')
            if _new_key not in _parameters:
                break
            warn('Параметр с таким названием уже есть')
        # _dct.rename_forms_param(_index)
        _parameters[_new_key] = _parameters[_key]
        _parameters.pop(_key)


# Открыть настройки словоформ
def forms_settings(_dct, _form_parameters):
    while True:
        outp('\nСуществующие параметры форм:')
        _keys = [_key for _key in _form_parameters.keys()]
        for _i in range(len(_keys)):
            outp(f'{_keys[_i]}')
        outp('\nЧто вы хотите сделать?')
        outp('Д - Добавить параметр форм')
        outp('У - Удалить параметр форм')
        outp('П - Переименовать параметр форм')
        outp('И - Изменить значения параметра форм')
        spec_action('Н - Назад')
        _cmd = inp().upper()
        if _cmd in ['Д', 'L']:
            add_frm_param(_form_parameters, _dct)
        elif _cmd in ['У', 'E']:
            remove_frm_param(_form_parameters, _dct)
        elif _cmd in ['П', 'G']:
            rename_frm_param(_form_parameters, _dct)
        elif _cmd in ['И', 'B']:
            while True:
                outp('\nКакой параметр форм вы хотите изменить?')
                outp('Выберите одно из предложенного')
                _keys = [_key for _key in _form_parameters.keys()]
                for _i in range(len(_keys)):
                    outp(f'{_i + 1} - {_keys[_i]}')
                spec_action('Н - Назад')
                _cmd = inp('Введите номер варианта: ')
                if _cmd.upper() in ['Н', 'Y']:
                    break
                try:
                    _index = int(_cmd) - 1
                    _frm_vals = _form_parameters[_keys[_index]]
                except (ValueError, TypeError, IndexError):
                    warn_inp('Недопустимый номер варианта', _cmd)
                    continue
                while True:
                    outp('\nСуществующие значения параметра:')
                    for _i in range(len(_frm_vals)):
                        outp(f'{_frm_vals[_i]}')
                    outp('\nЧто вы хотите сделать?')
                    outp('Д - Добавить значение параметра')
                    outp('У - Удалить значение параметра')
                    outp('П - Переименовать значение параметра')
                    spec_action('Н - Назад')
                    _cmd = inp().upper()
                    if _cmd in ['Д', 'L']:
                        add_frm_param_val(_frm_vals)
                    elif _cmd in ['У', 'E']:
                        remove_frm_param_val(_frm_vals, _dct)
                    elif _cmd in ['П', 'G']:
                        rename_frm_param_val(_frm_vals, _index, _dct)
                    elif _cmd in ['Н', 'Y']:
                        break
                    else:
                        warn_inp('Неизвестная команда', _cmd)
        elif _cmd in ['Н', 'Y']:
            break
        else:
            warn_inp('Неизвестная команда', _cmd)


# Вывод информации о программе
outp('======================================================================================\n')
outp('                            Anenokil development  presents')
outp('                                  Dictionary  v6.0.4')
outp('                                   30.12.2022  1:11\n')
outp('======================================================================================')

try:  # Открываем файл с названием словаря
    open(SETTINGS_PATH, 'r')
except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
    with open(SETTINGS_PATH, 'w') as set_file:
        set_file.write('words.txt')
with open(SETTINGS_PATH, 'r') as set_file:
    dct_filename = set_file.readline().strip()

dct = Dictionary()
min_good_score_perc, form_parameters = read_dct(dct, dct_filename)  # Загружаем словарь и его настройки

outp('\nМожете использовать эти комбинации для немецких букв: #a = ä, #o = ö, #u = ü, #s = ß (and ## = #)')

has_changes = False
while True:
    outp('\nЧто вы хотите сделать?')
    outp('Н  - Напечатать словарь')
    outp('НИ - Напечатать словарь (только Избранные статьи)')
    outp('Д  - Добавить статью')
    outp('И  - Изменить статью')
    outp('НС - Найти статью по Слову')
    outp('НП - Найти статью по Переводу')
    outp('У  - Учить слова')
    outp('НА - открыть НАстройки')
    outp('С  - Сохранить изменения')
    outp('СЛ - открыть список СЛоварей')
    outp('З  - Завершить работу')
    cmd = inp().upper()
    if cmd in ['Н', 'Y']:
        cmd = inp('\nВыводить все формы слов? (+ или -): ')
        outp()
        if cmd == '+':
            dct.print_with_forms(min_good_score_perc)
        else:
            dct.print(min_good_score_perc)
    elif cmd in ['НИ', 'YB']:
        cmd = inp('\nВыводить все формы слов? (+ или -): ')
        outp()
        if cmd == '+':
            dct.print_fav_with_forms(min_good_score_perc)
        else:
            dct.print_fav(min_good_score_perc)
    elif cmd in ['Д', 'L']:
        wrd = inp('\nВведите слово, которое хотите добавить в словарь: ')
        if wrd == '':
            warn('Слово должно содержать хотя бы один символ')
            continue
        tr = inp('Введите перевод слова: ')
        if tr == '':
            warn('Перевод должен содержать хотя бы один символ')
            continue
        key = dct.add_entry(wrd, tr)
        has_changes = True
        dct.edit_entry(key, form_parameters, _is_key=True)
    elif cmd in ['И', 'B']:
        wrd = inp('\nВведите слово, статью с которым хотите изменить: ')
        if wrd_to_key(wrd, 0) not in dct.d.keys():
            warn(f'Слово "{wrd}" отсутствует в словаре')
            outp('Возможно вы искали:')
            dct.print_words_with_str(wrd)
            continue
        has_changes = dct.edit_entry(wrd, form_parameters) or has_changes
    elif cmd in ['НС', 'YC']:
        search_wrd = inp('\nВведите слово, которое хотите найти: ')

        outp('\nЧастичное совпадение:')
        dct.print_words_with_str(search_wrd)

        outp('\nПолное совпадение:')
        if wrd_to_key(search_wrd, 0) not in dct.d.keys():
            outp(f'Слово "{code(search_wrd)}" отсутствует в словаре')
            continue
        for i in range(MAX_SAME_WORDS):
            key = wrd_to_key(search_wrd, i)
            if key not in dct.d.keys():
                break
            outp()
            dct.d[key].print_all()
    elif cmd in ['НП', 'YG']:
        search_tr = inp('\nВведите перевод слова, которое хотите найти: ')

        outp('\nЧастичное совпадение:', _end='')
        dct.print_translations_with_str(search_tr)

        outp('\nПолное совпадение:')
        is_found = False
        for entry in dct.d.values():
            if search_tr in entry.tr:
                is_found = True
                outp()
                entry.print_all()
        if not is_found:
            outp(f'Слово с переводом "{code(search_tr)}" отсутствует в словаре')
    elif cmd in ['У', 'E']:
        outp('\nВаша общая доля правильных ответов: {:.2%}'.format(dct.count_rating()))
        outp('\nВыберите способ')
        outp('1 - Угадывать слово по переводу')
        outp('2 - Угадывать перевод по слову')
        cmd = inp().upper()
        if cmd == '1':
            outp('\nВыберите способ')
            outp('1 - Со всеми словоформами')
            outp('2 - Только начальные формы')
            cmd = inp().upper()
            if cmd == '1':
                outp('\nВыберите способ')
                outp('В - Все слова')
                outp('С - все слова (в первую очередь Сложные)')
                outp('И - только Избранные слова')
                cmd = inp().upper()
                if cmd in ['В', 'D']:
                    has_changes = dct.learn_f(min_good_score_perc) or has_changes
                elif cmd in ['И', 'B']:
                    has_changes = dct.learn_f_fav(min_good_score_perc) or has_changes
                elif cmd in ['С', 'C']:
                    has_changes = dct.learn_f_hard(min_good_score_perc) or has_changes
                else:
                    warn_inp('Неизвестная команда', cmd)
            elif cmd == '2':
                outp('\nВыберите способ')
                outp('В - Все слова')
                outp('С - все слова (в первую очередь Сложные)')
                outp('И - только Избранные слова')
                cmd = inp().upper()
                if cmd in ['В', 'D']:
                    has_changes = dct.learn(min_good_score_perc) or has_changes
                elif cmd in ['И', 'B']:
                    has_changes = dct.learn_fav(min_good_score_perc) or has_changes
                elif cmd in ['С', 'C']:
                    has_changes = dct.learn_hard(min_good_score_perc) or has_changes
                else:
                    warn_inp('Неизвестная команда', cmd)
            else:
                warn_inp('Неизвестная команда', cmd)
        elif cmd == '2':
            outp('\nВыберите способ')
            outp('В - Все слова')
            outp('С - все слова (в первую очередь Сложные)')
            outp('И - только Избранные слова')
            cmd = inp().upper()
            if cmd in ['В', 'D']:
                has_changes = dct.learn_t(min_good_score_perc) or has_changes
            elif cmd in ['И', 'B']:
                has_changes = dct.learn_t_fav(min_good_score_perc) or has_changes
            elif cmd in ['С', 'C']:
                has_changes = dct.learn_t_hard(min_good_score_perc) or has_changes
            else:
                warn_inp('Неизвестная команда', cmd)
        else:
            warn_inp('Неизвестная команда', cmd)
    elif cmd in ['НА', 'YF']:
        while True:
            outp('\nЧто вы хотите сделать?')
            outp('М - изменить Минимальный приемлемый процент удачных попыток отгадать слово')
            outp('Ф - открыть настройки словоФорм')
            spec_action('Н - Назад')
            cmd = inp().upper()
            if cmd in ['М', 'V']:
                outp(f'\nТекущее значение: {min_good_score_perc}%')
                outp('Статьи, у которых процент угадывания ниже этого значения, помечаются в словаре красным цветом')
                new_val = inp('Введите новое значение: ')
                try:
                    new_val = int(new_val)
                except (ValueError, TypeError):
                    warn_inp('Некорректный ввод', new_val)
                else:
                    if new_val < 0 or new_val > 100:
                        warn_inp('Некорректный ввод', new_val)
                        continue
                    min_good_score_perc = new_val
            elif cmd in ['Ф', 'A']:
                forms_settings(dct, form_parameters)
                has_changes = True
            elif cmd in ['Н', 'Y']:
                break
            else:
                warn_inp('Неизвестная команда', cmd)
    elif cmd in ['С', 'C']:
        save_all(dct, min_good_score_perc, form_parameters, dct_filename)
        outp('\nИзменения и прогресс успешно сохранены')
        has_changes = False
    elif cmd in ['СЛ', 'CK']:
        while True:
            outp('\nСуществующие словари:')
            f_count = 0
            f_list = []
            for filename in os.listdir(SAVES_PATH):
                base_name, ext = os.path.splitext(filename)
                if ext == '.txt':
                    if filename == dct_filename:
                        outp(f'{f_count} - {filename} (ТЕКУЩИЙ)')
                    else:
                        outp(f'{f_count} - {filename}')
                    f_list += [filename]
                    f_count += 1

            outp('\nЧто вы хотите сделать?')
            outp('О - Открыть словарь')
            outp('С - Создать новый словарь')
            outp('П - Переименовать словарь')
            outp('У - Удалить словарь')
            spec_action('Н - Назад')
            cmd = inp().upper()

            if cmd in ['Н', 'Y']:
                break
            elif cmd in ['П', 'G']:
                cmd = inp('\nВведите номер словаря: ')
                try:
                    old_name = f_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    warn_inp('Недопустимый номер варианта', cmd)
                    continue

                new_name = inp('Введите новое название: ')
                if new_name[-4:] != '.txt':
                    new_name += '.txt'
                if new_name == '.txt':
                    warn('Недопустимое название')
                    continue
                if new_name in f_list:
                    warn('Файл с таким названием уже существует')
                    continue

                os.rename(os.path.join(SAVES_PATH, old_name), os.path.join(SAVES_PATH, new_name))
                os.rename(os.path.join(LOCAL_SETTINGS_PATH, old_name), os.path.join(LOCAL_SETTINGS_PATH, new_name))
                if dct_filename == old_name:
                    dct_filename = new_name
                    with open(SETTINGS_PATH, 'w') as set_file:
                        set_file.write(new_name)
                outp(f'\nСловарь "{old_name}" успешно переименован в "{new_name}"')
            elif cmd in ['У', 'E']:
                cmd = inp('\nВведите номер словаря: ')
                try:
                    filename = f_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    warn_inp('Недопустимый номер варианта', cmd)
                    continue
                if filename == dct_filename:
                    warn('Вы не можете удалить словарь, который сейчас открыт')
                    continue

                cmd = inp(f'Вы уверены? Словарь "{filename}" будет безвозвратно удалён! (+ или -): ')
                if cmd == '+':
                    os.remove(os.path.join(SAVES_PATH, filename))
                    os.remove(os.path.join(LOCAL_SETTINGS_PATH, filename))
                    outp(f'\nСловарь "{filename}" успешно удалён')
            elif cmd in ['С', 'C']:
                filename = inp('\nВведите название файла со словарём: ')
                if filename[-4:] != '.txt':
                    filename += '.txt'
                if filename == '.txt':
                    warn('Недопустимое название')
                    continue
                if filename in f_list:
                    warn('Файл с таким названием уже существует')
                    continue

                if has_changes:
                    save_if_has_changes(dct, min_good_score_perc, form_parameters, dct_filename)
                dct_filename = filename
                with open(SETTINGS_PATH, 'w') as set_file:
                    set_file.write(filename)
                dct = Dictionary()
                min_good_score_perc, form_parameters = create_dct(dct, filename)
            elif cmd in ['О', 'J']:
                cmd = inp('\nВведите номер словаря: ')
                try:
                    filename = f_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    warn_inp('Недопустимый номер варианта', cmd)
                    continue

                if has_changes:
                    save_if_has_changes(dct, min_good_score_perc, form_parameters, dct_filename)
                dct_filename = filename
                with open(SETTINGS_PATH, 'w') as set_file:
                    set_file.write(filename)
                dct = Dictionary()
                min_good_score_perc, form_parameters = read_dct(dct, filename)
            else:
                warn_inp('Неизвестная команда', cmd)
    elif cmd in ['З', 'P']:
        if has_changes:
            save_if_has_changes(dct, min_good_score_perc, form_parameters, dct_filename)
        break
    else:
        warn_inp('Неизвестная команда', cmd)
