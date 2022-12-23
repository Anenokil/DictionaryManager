import random
import os
from colorama import Fore, Style
import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

RESOURCES_DIR = 'resources'
SAVES_DIR = os.path.join(RESOURCES_DIR, 'saves')
SETTINGS_FN = os.path.join(RESOURCES_DIR, 'settings.txt')
LOCAL_SETTINGS_DIR = os.path.join(RESOURCES_DIR, 'local_settings')
FORMS_SEPARATOR = '@'

"""
    Про формы:
    
    apple - слово
    apples - форма слова
    число - параметр формы слова
    мн.ч., ед.ч. - значения параметра формы слова
"""


# Вывести сообщение о некорректном вводе
def allert_inp(_text, _input):
    print(f'{Fore.RED}{_text}: "{_input}"{Style.RESET_ALL}')


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


# Перевести строку в кортеж
def decode_tpl(_str, _separator=FORMS_SEPARATOR):
    return tuple(_str.split(_separator))


# Добавить значение параметра форм
def add_frm_val(_frm_list):
    _new_f = input('\nВведите новое значение параметра: ')
    if _new_f in _frm_list:
        print(f'{Fore.RED}Значение "{_new_f}" уже существует{Style.RESET_ALL}')
    elif _new_f == '':
        print(f'{Fore.RED}Недопустимое значение{Style.RESET_ALL}')
    elif FORMS_SEPARATOR in _new_f:
        allert_inp('Недопустимый символ', FORMS_SEPARATOR)
    else:
        _frm_list += [_new_f]


# Удалить значение параметра форм
def remove_frm_val(_frm_list, _dct):
    if len(_frm_list) == 1:
        print(f'\n{Fore.RED}Вы не можете удалить единственное значение параметра{Style.RESET_ALL}')
        return
    print('\nВыберите один из предложенных вариантов')
    for _i in range(len(_frm_list)):
        print(f'{_i} - {_frm_list[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _index = int(_index)
        _frm_val = _frm_list[_index]
    except (ValueError, TypeError, IndexError):
        allert_inp('Недопустимый номер варианта', _index)
    else:
        _cmd = input('\nВсе формы слов, содержащие это значение, будут удалены! Вы уверены? (+ или -): ')
        if _cmd == '+':
            _frm_list.pop(_index)
        _dct.remove_forms_with_val(_index, _frm_val)


# Переименовать значение параметра форм
def rename_frm_val(_frm_list, _dct):
    print('\nВыберите один из предложенных вариантов')
    for _i in range(len(_frm_list)):
        print(f'{_i} - {_frm_list[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _index = int(_index)
        _frm_val = _frm_list[_index]
    except (ValueError, TypeError, IndexError):
        allert_inp('Недопустимый номер варианта', _index)
    else:
        while True:
            _new_frm_val = input('\nВведите новое название для значения параметра: ')
            if _new_frm_val not in _frm_list:
                break
            print(f'{Fore.RED}Значение с таким названием уже есть{Style.RESET_ALL}')
        _dct.rename_forms_with_val(_index, _frm_val, _new_frm_val)
        _frm_list[_index] = _new_frm_val


# Добавить параметр форм
def add_frm_param(_frm_parameters):
    _new_p = input('\nВведите новый параметр: ')
    if _new_p in _frm_parameters.keys():
        print(f'{Fore.RED}Параметр "{_new_p}" уже существует{Style.RESET_ALL}')
    elif _new_p == '':
        print(f'{Fore.RED}Недопустимый параметр{Style.RESET_ALL}')
    else:
        _frm_parameters[_new_p] = []
        print('Необходимо добавить хотя бы одно значение для параметра')
        while _frm_parameters[_new_p] == []:
            add_frm_val(_frm_parameters[_new_p])


# Удалить параметр форм
def remove_frm_param(_frm_parameters, _dct):
    print('\nВыберите один из предложенных вариантов')
    _keys = [_key for _key in _frm_parameters.keys()]
    for _i in range(len(_keys)):
        print(f'{_i} - {_keys[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _index = int(_index)
        _key = _keys[_index]
    except (ValueError, TypeError, IndexError):
        allert_inp('Недопустимый номер варианта', _index)
    else:
        _cmd = input('\nВсе формы слов, содержащие этот параметр, будут удалены! Вы уверены? (+ или -): ')
        if _cmd == '+':
            _frm_parameters.pop(_key)
        _dct.remove_forms_with_param(_index)


# Переименовать параметр форм
def rename_frm_param(_frm_parameters, _dct):
    print('\nВыберите один из предложенных вариантов')
    _keys = [_key for _key in _frm_parameters.keys()]
    for _i in range(len(_keys)):
        print(f'{_i} - {_keys[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _index = int(_index)
        _key = _keys[_index]
    except (ValueError, TypeError, IndexError):
        allert_inp('Недопустимый номер варианта', _index)
    else:
        while True:
            _new_key = input('\nВведите новое название параметра: ')
            if _new_key not in _frm_parameters:
                break
            print(f'{Fore.RED}Параметр с таким названием уже есть{Style.RESET_ALL}')
        # _dct.rename_forms_with_param(_index, _new_frm_parameters)
        _frm_parameters[_new_key] = _frm_parameters[_key]
        _frm_parameters.pop(_key)


# Выбрать значение одного из параметров формы слова
def choose_frm_param(_frm_name, _frm_list):
    while True:
        print(f'\nВыберите {_frm_name}')
        for _i in range(len(_frm_list)):
            print(f'{_i} - {_frm_list[_i]}')
        print(f'{Fore.YELLOW}Н - Не указывать/Неприменимо{Style.RESET_ALL}')
        print(f'{Fore.YELLOW}Д - Добавить новый вариант{Style.RESET_ALL}')
        _cmd = input().upper()
        if _cmd in ['Н', 'Y']:
            return ''
        elif _cmd in ['Д', 'L']:
            add_frm_val(_frm_list)
        else:
            try:
                return _frm_list[int(_cmd)]
            except (ValueError, TypeError, IndexError):
                allert_inp('Недопустимый вариант', _cmd)


# Выбрать параметр формы слова
def choose_frm_type():
    _res = []
    _keys = list(form_parameters.keys())
    print('Выберите параметр')
    for _i in range(len(_keys)):
        print(f'{_i} - {_keys[_i]}')
        _res += ['']
    _res_void = tuple(_res)
    _index = input()

    while True:
        try:
            _index = int(_index)
            _key = _keys[_index]
            _res[_index] = choose_frm_param(_key, form_parameters[_key])
        except (ValueError, TypeError, IndexError):
            allert_inp('Недопустимый вариант', _index)

        _is_void = _res == list(_res_void)
        print()
        if not _is_void:
            print(f'{Fore.MAGENTA}Шаблон формы: {tpl(_res)}{Style.RESET_ALL}\n')

        print('Выберите параметр')
        for _i in range(len(_keys)):
            print(f'{_i} - {_keys[_i]}')
        if not _is_void:
            print(f'{Fore.YELLOW}З - Закончить с шаблоном и ввести форму слова{Style.RESET_ALL}')

        _index = input()
        if _index.upper() in ['З', 'P']:
            if not _is_void:
                break
    return tuple(_res)


class Note(object):
    # self.wrd - слово
    # self.tr - список переводов
    # self.dsc - список сносок
    # self.forms - формы слова
    # self.count_t - количество переводов
    # self.count_d - количество сносок
    # self.count_f - количество форм слова
    # self.fav - избранное
    # self.all_tries - количество всех попыток
    # self.correct_tries - количество удачных попыток
    # self.percent - процент удачных попыток
    # self.last_tries - количество последних неудачных попыток (-1 - значит ещё не было попыток)
    def __init__(self, _wrd, _tr, _dsc=None, _fav=False, _all_tries=0, _correct_tries=0, _last_tries=-1):
        self.wrd = _wrd
        self.tr = _tr if type(_tr) == list else [_tr]
        if _dsc is None:
            self.dsc = []
        elif type(_dsc) == list:
            self.dsc = _dsc
        else:
            self.dsc = [_dsc]
        self.forms = {}
        self.count_t = len(self.tr)
        self.count_d = len(self.dsc)
        self.count_f = 0
        self.fav = _fav
        self.all_tries = _all_tries
        self.correct_tries = _correct_tries
        if _all_tries:
            self.percent = _correct_tries / _all_tries
        else:
            self.percent = 0
        self.last_tries = _last_tries

    """ Напечатать перевод """
    def tr_print(self, _end='\n'):
        if self.count_t != 0:
            print(code(self.tr[0]), end='')
        for _i in range(1, self.count_t):
            print(f', {code(self.tr[_i])}', end='')
        print(_end, end='')

    """ Напечатать сноски """
    def dsc_print(self, _tab=0):
        for _i in range(self.count_d):
            print(' ' * _tab + f'> {code(self.dsc[_i])}')

    """ Напечатать формы слова """
    def frm_print(self, _tab=0):
        for _key in self.forms.keys():
            print(' ' * _tab + f'[{tpl(_key)}] {code(self.forms[_key])}')

    """ Напечатать статистику """
    def stat_print(self, _end='\n'):
        print(Fore.CYAN, end='')
        if self.last_tries == -1:
            print('[-:  0%]', end=_end)
        else:
            _perc = '{:.0%}'.format(self.percent)
            _tab = ' ' * (4 - len(_perc))
            print(f'[{self.last_tries}:{_tab}{_perc}]', end=_end)
        print(Style.RESET_ALL, end='')

    """ Служебная функция для print_briefly и print_briefly_with_forms """
    def _print_briefly(self):
        if self.fav:
            print(f'{Fore.MAGENTA}(*){Style.RESET_ALL}', end=' ')
        else:
            print('   ', end=' ')
        self.stat_print(_end=' ')
        print(code(self.wrd) + Fore.RED + ': ' + Style.RESET_ALL, end='')
        self.tr_print()

    """ Напечатать запись - кратко """
    def print_briefly(self):
        self._print_briefly()
        self.dsc_print(_tab=13)

    """ Напечатать запись - кратко с формами """
    def print_briefly_with_forms(self):
        self._print_briefly()
        self.frm_print(_tab=13)
        self.dsc_print(_tab=13)

    """ Напечатать запись - слово со статистикой """
    def print_wrd_with_stat(self):
        print(code(self.wrd), end=' ')
        self.stat_print()

    """ Напечатать запись - перевод со статистикой """
    def print_tr_with_stat(self):
        self.tr_print(_end=' ')
        self.stat_print()

    """ Напечатать запись - перевод с формой и со статистикой """
    def print_tr_and_frm_with_stat(self, _frm_type):
        self.tr_print(_end=' ')
        print(f'({tpl(_frm_type)})', end=' ')
        self.stat_print()

    """ Напечатать запись со всей редактируемой информацией """
    def print_edit(self):
        print(f'       Слово: {code(self.wrd)}')
        print('     Перевод: ', end='')
        self.tr_print()
        print(' Формы слова: ', end='')
        if self.count_f == 0:
            print('-')
        else:
            _keys = [_key for _key in self.forms.keys()]
            print(f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}')
            for _i in range(1, self.count_f):
                print(f'              [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        print('      Сноски: ', end='')
        if self.count_d == 0:
            print('-')
        else:
            print(f'> {code(self.dsc[0])}')
            for _i in range(1, self.count_d):
                print(f'              > {code(self.dsc[_i])}')
        print(f'   Избранное: {self.fav}')

    """ Напечатать запись со всей информацией """
    def print_all(self):
        print(f'       Слово: {code(self.wrd)}')
        print('     Перевод: ', end='')
        self.tr_print()
        print(' Формы слова: ', end='')
        if self.count_f == 0:
            print('-')
        else:
            _keys = [_key for _key in self.forms.keys()]
            print(f'[{tpl(_keys[0])}] {code(self.forms[_keys[0]])}')
            for _i in range(1, self.count_f):
                print(f'              [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        print('      Сноски: ', end='')
        if self.count_d == 0:
            print('-')
        else:
            print(f'> {code(self.dsc[0])}')
            for _i in range(1, self.count_d):
                print(f'              > {code(self.dsc[_i])}')
        print(f'   Избранное: {self.fav}')
        if self.last_tries == -1:
            print(f'  Статистика: 1) Последних неверных ответов: -')
            print(f'              2) Доля верных ответов: 0')
        else:
            print(f'  Статистика: 1) Последних неверных ответов: {self.last_tries}')
            print(f'              2) Доля верных ответов: {self.correct_tries}/{self.all_tries} = ' + '{:.0%}'.format(self.percent))

    """ Добавить перевод """
    def add_tr(self, _new_tr, _show_msg=True):
        if _new_tr not in self.tr:
            self.tr += [_new_tr]
            self.count_t += 1
        elif _show_msg:
            print(f'{Fore.RED}У этого слова уже есть такой перевод{Style.RESET_ALL}')

    """ Добавить сноску """
    def add_dsc(self, _new_dsc):
        self.dsc += [_new_dsc]
        self.count_d += 1

    """ Добавить форму слова """
    def add_frm(self, _frm_type, _new_frm, _show_msg=True):
        if _frm_type not in self.forms.keys():
            self.forms[_frm_type] = _new_frm
            self.count_f += 1
        elif _show_msg:
            print(f'{Fore.RED}Слово уже имеет форму {tpl(_frm_type)}: {self.forms[_frm_type]}{Style.RESET_ALL}')

    """ Добавить статистику """
    def add_stat(self, _all_tries, _correct_tries, _last_tries):
        self.all_tries = _all_tries
        self.correct_tries = _correct_tries
        if _all_tries:
            self.percent = _correct_tries / _all_tries
        else:
            self.percent = 0
        self.last_tries = _last_tries

    """ Объединить статистику при объединении двух записей """
    def merge_stat(self, _all_tries, _correct_tries, _last_tries):
        self.all_tries += _all_tries
        self.correct_tries += _correct_tries
        if self.all_tries:
            self.percent = self.correct_tries / self.all_tries
        else:
            self.percent = 0
        self.last_tries += _last_tries

    """ Обнулить счётчик, если верная попытка """
    def correct_try(self):
        self.all_tries += 1
        self.correct_tries += 1
        self.percent = self.correct_tries / self.all_tries
        self.last_tries = 0

    """ Увеличить счётчик, если неверная попытка """
    def incorrect_try(self):
        self.all_tries += 1
        self.percent = self.correct_tries / self.all_tries
        if self.last_tries == -1:
            self.last_tries = 1
        else:
            self.last_tries += 1

    """ Удалить перевод """
    def remove_tr(self):
        if self.count_t == 1:
            print(f'{Fore.RED}Вы не можете удалить единственный перевод слова{Style.RESET_ALL}')
            return
        print('Выберите один из предложенных вариантов')
        for _i in range(self.count_t):
            print(f'{_i} - {code(self.tr[_i])}')
        _index = input('Введите номер варианта: ')
        try:
            _index = int(_index)
            self.tr.pop(_index)
        except (ValueError, IndexError):
            allert_inp('Недопустимый номер варианта', _index)
        else:
            self.count_t -= 1

    """ Удалить сноску """
    def remove_dsc(self):
        print('Выберите один из предложенных вариантов')
        for _i in range(self.count_d):
            print(f'{_i} - {code(self.dsc[_i])}')
        _index = input('Введите номер варианта: ')
        try:
            _index = int(_index)
            self.dsc.pop(_index)
        except (ValueError, IndexError):
            allert_inp('Недопустимый номер варианта', _index)
        else:
            self.count_d -= 1

    """ Удалить форму слова """
    def remove_frm_with_choose(self):
        _keys = [_key for _key in self.forms.keys()]
        print('Выберите один из предложенных вариантов')
        for _i in range(self.count_f):
            print(f'{_i} - [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        _index = input('Введите номер варианта: ')
        try:
            _index = int(_index)
            self.forms.pop(_keys[_index])
        except (ValueError, IndexError):
            allert_inp('Недопустимый номер варианта', _index)
        else:
            self.count_f -= 1

    """ Удалить все формы слова, содержащие данное значение """
    def remove_frm_with_val(self, _pos, _frm_val):
        _to_remove = []
        for _frm in self.forms.keys():
            if _frm[_pos] == _frm_val:
                _to_remove += [_frm]
                self.count_f -= 1
        for _el in _to_remove:
            self.forms.pop(_el)

    """ Переименовать все формы слова, содержащие данное значение """
    def rename_frm_with_val(self, _pos, _frm_val, _new_frm_val):
        _to_rename = []
        for _frm in self.forms.keys():
            if _frm[_pos] == _frm_val:
                _to_rename += [_frm]
        for _el in _to_rename:
            _lst = list(_el)
            _lst[_pos] = _new_frm_val
            _lst = tuple(_lst)
            self.forms[_lst] = self.forms[_el]
            self.forms.pop(_el)

    """ Удалить все формы слова, содержащие данный параметр """
    def remove_frm_with_param(self, _pos):
        _to_remove = []
        for _frm in self.forms.keys():
            if _frm[_pos] != '':
                _to_remove += [_frm]
                self.count_f -= 1
        for _el in _to_remove:
            self.forms.pop(_el)

    """ Сохранить запись в файл """
    def save(self, _file):
        _file.write(f'w{self.wrd}\n')
        _file.write(f'{str(self.all_tries)}\n')
        _file.write(f'{str(self.correct_tries)}\n')
        _file.write(f'{str(self.last_tries)}\n')
        _file.write(f'{self.tr[0]}\n')
        for _i in range(1, self.count_t):
            _file.write(f't{self.tr[_i]}\n')
        for _dsc in self.dsc:
            _file.write(f'd{_dsc}\n')
        for _frm_type in self.forms.keys():
            _file.write(f'f{code_tpl(_frm_type)}\n{self.forms[_frm_type]}\n')
        if self.fav:
            _file.write('*\n')


# Угадать слово по переводу
def guess_wrd(_note, _count_correct, _count_all):
    print()
    _note.print_tr_with_stat()
    _wrd_ans = input(f'Введите слово {Fore.YELLOW}(# - чтобы закончить, @ - чтобы посмотреть сноски){Style.RESET_ALL}: ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input(f'Введите слово {Fore.YELLOW}(# - чтобы закончить){Style.RESET_ALL}: ')
    if _wrd_ans == '#':
        print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
        return 1

    if _wrd_ans == _note.wrd:
        _note.correct_try()
        print(f'{Fore.GREEN}Верно{Style.RESET_ALL}')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'{Fore.RED}Неверно. Правильный ответ: "{_note.wrd}"{Style.RESET_ALL}')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


# Угадать словоформу по переводу
def guess_wrd_f(_note, _wrd_f, _count_correct, _count_all):
    print()
    _note.print_tr_and_frm_with_stat(_wrd_f)
    _wrd_ans = input(f'Введите слово в данной форме {Fore.YELLOW}(# - чтобы закончить, @ - чтобы посмотреть сноски){Style.RESET_ALL}: ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input(f'Введите слово в данной форме {Fore.YELLOW}(# - чтобы закончить){Style.RESET_ALL}: ')
    if _wrd_ans == '#':
        print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
        return 1

    if _wrd_ans == _note.forms[_wrd_f]:
        _note.correct_try()
        print(f'{Fore.GREEN}Верно{Style.RESET_ALL}')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'{Fore.RED}Неверно. Правильный ответ: "{_note.wrd}"{Style.RESET_ALL}')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


# Угадать перевод по слову
def guess_tr(_note, _count_correct, _count_all):
    print()
    _note.print_wrd_with_stat()
    _wrd_ans = input(f'Введите перевод {Fore.YELLOW}(# - чтобы закончить, @ - чтобы посмотреть сноски){Style.RESET_ALL}: ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input(f'Введите перевод {Fore.YELLOW}(# - чтобы закончить){Style.RESET_ALL}: ')
    if _wrd_ans == '#':
        print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
        return 1

    if _wrd_ans in _note.tr:
        _note.correct_try()
        print(f'{Fore.GREEN}Верно{Style.RESET_ALL}')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'{Fore.RED}Неверно. Правильный ответ: {_note.tr}{Style.RESET_ALL}')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


MAX_SIMILAR_WORDS = 100


# Превратить слово из статьи в ключ для словаря
def wrd_to_key(_wrd, _num):
    return str(_num // 10) + str(_num % 10) + _wrd


# Превратить ключ для словаря в слово из статьи
def key_to_wrd(_key):
    return _key[3:]


class Dictionary(object):
    # self.d - сам словарь
    # self.count_w - количество записей в словаре
    # self.count_t - количество переводов в словаре
    # self.count_f - количество неначальных словоформ в словаре
    def __init__(self):
        self.d = {}
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0

    """ Напечатать словарь """
    def print(self):
        for _note in self.d.values():
            _note.print_briefly()
        print(f'{Fore.YELLOW}< {self.count_w} сл. | {self.count_w + self.count_f} словоформ. | {self.count_t} перев. >{Style.RESET_ALL}')

    """ Напечатать словарь (со всеми формами) """
    def print_with_forms(self):
        for _note in self.d.values():
            _note.print_briefly_with_forms()
        print(f'{Fore.YELLOW}< {self.count_w} сл. | {self.count_w + self.count_f} словоформ. | {self.count_t} перев. >{Style.RESET_ALL}')

    """ Напечатать словарь (только избранные слова) """
    def print_fav(self):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _note in self.d.values():
            if _note.fav:
                _note.print_briefly()
                _count_w += 1
                _count_t += _note.count_t
                _count_f += _note.count_f
        print(f'{Fore.YELLOW}< {_count_w}/{self.count_w} сл. | {_count_w + _count_f}/{self.count_w + self.count_f} словоформ. | {_count_t}/{self.count_t} перев. >{Style.RESET_ALL}')

    """ Напечатать словарь (только избранные слова, со всеми формами) """
    def print_fav_with_forms(self):
        _count_w = 0
        _count_t = 0
        _count_f = 0
        for _note in self.d.values():
            if _note.fav:
                _note.print_briefly_with_forms()
                _count_w += 1
                _count_t += _note.count_t
                _count_f += _note.count_f
        print(f'{Fore.YELLOW}< {_count_w}/{self.count_w} сл. | {_count_w + _count_f}/{self.count_w + self.count_f} словоформ. | {_count_t}/{self.count_t} перев. >{Style.RESET_ALL}')

    """ Подсчитать среднюю долю правильных ответов """
    def count_rating(self):
        _sum_num = 0
        _sum_den = 0
        for _note in self.d.values():
            _sum_num += _note.correct_tries
            _sum_den += _note.all_tries
        if _sum_den == 0:
            return 0
        return _sum_num / _sum_den

    """ Выбрать одну статью из нескольки с одинаковыми словами """
    def choose_one_of_similar(self, _wrd):
        if wrd_to_key(_wrd, 1) not in self.d.keys():
            return wrd_to_key(_wrd, 0)
        print('\nВыберите одну из статей')
        for _i in range(MAX_SIMILAR_WORDS):
            _key = wrd_to_key(_wrd, _i)
            if _key not in self.d.keys():
                break
            print(f'\n({_i})')
            self.d[_key].print_all()
        while True:
            _index = input('\nВведите номер варианта: ')
            try:
                return wrd_to_key(_wrd, int(_index))
            except (ValueError, TypeError):
                allert_inp('Недопустимый номер варианта', _index)

    """ Добавить запись в словарь (при чтении сохранения) """
    def add_note(self, _wrd, _tr, _all_tries, _correct_tries, _last_tries):
        for _i in range(MAX_SIMILAR_WORDS):
            if wrd_to_key(_wrd, _i) not in self.d.keys():
                _key = wrd_to_key(_wrd, _i)
                self.d[_key] = Note(_wrd, [_tr], _all_tries=_all_tries, _correct_tries=_correct_tries, _last_tries=_last_tries)
                self.count_w += 1
                self.count_t += 1
                return _key
            _i += 1

    """ Добавить запись в словарь (для пользователя) """
    def add_val(self, _wrd, _tr, _show_msg=True):
        if wrd_to_key(_wrd, 0) in self.d.keys():
            while True:
                print(f'\n{Fore.YELLOW}Статья с таким словом уже есть в словаре{Style.RESET_ALL}')
                print('Что вы хотите сделать?')
                print('Д - Добавить к существующей статье')
                print('Н - создать Новую статью')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    _key = self.choose_one_of_similar(_wrd)
                    self.add_tr(_key, _tr, _show_msg, _transform=False)
                    return _key
                elif _cmd in ['Н', 'Y']:
                    for _i in range(MAX_SIMILAR_WORDS):
                        _key = wrd_to_key(_wrd, _i)
                        if _key not in self.d.keys():
                            self.d[_key] = Note(_wrd, [_tr])
                            self.count_w += 1
                            self.count_t += 1
                            return _key
                        _i += 1
                else:
                    allert_inp('Неизвестная команда', _cmd)
        else:
            _key = wrd_to_key(_wrd, 0)
            self.d[_key] = Note(_wrd, [_tr])
            self.count_w += 1
            self.count_t += 1
            return _key

    """ Изменить слово """
    def edit_wrd(self, _key, _new_key):
        if _new_key in self.d.keys():
            self.count_t -= self.d[_key].count_t
            self.count_t -= self.d[_new_key].count_t
            for _tr in self.d[_key].tr:
                self.d[_new_key].add_tr(_tr, False)
            for _dsc in self.d[_key].dsc:
                self.add_dsc(_new_key, _dsc)
            self.count_t += self.d[_new_key].count_t
            self.count_w -= 1
            if self.d[_key].fav:
                self.d[_new_key].fav = True
            self.d[_new_key].merge_stat(self.d[_key].all_tries, self.d[_key].correct_tries, self.d[_key].last_tries)
        else:
            self.d[_new_key] = Note(key_to_wrd(_new_key), self.d[_key].tr, self.d[_key].dsc, self.d[_key].fav,
                                    self.d[_key].all_tries, self.d[_key].correct_tries, self.d[_key].last_tries)
        self.d.pop(_key)

    """ Добавить перевод к записи в словаре """
    def add_tr(self, _wrd, _tr, _show_msg=True, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.count_t -= self.d[_wrd].count_t
        self.d[_wrd].add_tr(_tr, _show_msg)
        self.count_t += self.d[_wrd].count_t

    """ Добавить сноску к записи в словаре """
    def add_dsc(self, _wrd, _dsc, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.d[_wrd].add_dsc(_dsc)

    """ Добавить форму слова к записи в словаре """
    def add_frm(self, _wrd, _frm_type, _frm, _show_msg=True, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.count_f -= self.d[_wrd].count_f
        self.d[_wrd].add_frm(_frm_type, _frm, _show_msg)
        self.count_f += self.d[_wrd].count_f

    """ Удалить перевод из словаря """
    def remove_tr(self, _wrd, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.count_t -= self.d[_wrd].count_t
        self.d[_wrd].remove_tr()
        self.count_t += self.d[_wrd].count_t

    """ Удалить описание из словаря """
    def remove_dsc(self, _wrd, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.d[_wrd].remove_dsc()

    """ Удалить форму слова из словаря """
    def remove_frm_with_choose(self, _wrd, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.count_f -= self.d[_wrd].count_f
        self.d[_wrd].remove_frm_with_choose()
        self.count_f += self.d[_wrd].count_f

    """ Удалить все формы, содержащие данное значение """
    def remove_forms_with_val(self, _pos, _frm_val):
        for _note in self.d.values():
            self.count_f -= _note.count_f
            _note.remove_frm_with_val(_pos, _frm_val)
            self.count_f += _note.count_f

    """ Переименовать все формы, содержащие данное значение """
    def rename_forms_with_val(self, _pos, _frm_val, _new_frm_val):
        for _note in self.d.values():
            _note.rename_frm_with_val(_pos, _frm_val, _new_frm_val)

    """ Удалить все формы, содержащие данный параметр """
    def remove_forms_with_param(self, _pos):
        for _note in self.d.values():
            self.count_f -= _note.count_f
            _note.remove_frm_with_param(_pos)
            self.count_f += _note.count_f

    """ Удалить запись из словаря """
    def remove_note(self, _wrd, _transform=True):
        self.count_w -= 1
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        self.count_t -= self.d[_wrd].count_t
        self.count_f -= self.d[_wrd].count_f
        self.d.pop(_wrd)

    """ Сохранить словарь в файл """
    def save(self, _filename):
        with open(_filename, 'w') as _file:
            for _note in self.d.values():
                _note.save(_file)

    """ Прочитать словарь из файла """
    def read(self, _filename):
        try:
            with open(_filename, 'r') as _file:
                while True:
                    _line = _file.readline().strip()
                    if not _line:
                        break
                    elif _line[0] == 'w':
                        _wrd = _line[1:]
                        _all_tries = int(_file.readline().strip())
                        _correct_tries = int(_file.readline().strip())
                        _last_tries = int(_file.readline().strip())
                        _tr = _file.readline().strip()
                        _key = self.add_note(_wrd, _tr, _all_tries, _correct_tries, _last_tries)
                    elif _line[0] == 't':
                        self.add_tr(_key, _line[1:], False, _transform=False)
                    elif _line[0] == 'd':
                        self.add_dsc(_key, _line[1:], _transform=False)
                    elif _line[0] == 'f':
                        _frm_type = decode_tpl(_line[1:])
                        self.add_frm(_key, _frm_type, _file.readline().strip(), _transform=False)
                    elif _line[0] == '*':
                        self.d[_key].fav = True
            return 0
        except FileNotFoundError:
            return 1
        except (ValueError, TypeError):
            return 2

    """ Изменить запись в словаре """
    def edit_note(self, _wrd, _transform=True):
        if _transform:
            _wrd = self.choose_one_of_similar(_wrd)
        _has_changes = False
        while True:
            print()
            self.d[_wrd].print_edit()
            print('\nЧто вы хотите сделать?')
            print('СЛ - изменить СЛово')
            print('П  - изменить Перевод')
            print('Ф  - изменить Формы слова')
            print('СН - изменить СНоски')
            if self.d[_wrd].fav:
                print('И  - убрать из Избранного')
            else:
                print('И  - добавить в Избранное')
            print('У  - Удалить запись')
            print(f'{Fore.YELLOW}Н  - вернуться Назад{Style.RESET_ALL}')
            _cmd = input().upper()
            if _cmd in ['СЛ', 'CK']:
                _new_wrd = input('\nВведите новое слово: ')
                _new_wrd = self.choose_one_of_similar(_new_wrd)
                self.edit_wrd(_wrd, _new_wrd)
                _wrd = _new_wrd
                _has_changes = True
            elif _cmd in ['П', 'G']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить перевод')
                print('У - Удалить перевод')
                print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    _tr = input('\nВведите перевод: ')
                    if _tr == '':
                        print(f'{Fore.RED}Перевод не может быть пустым{Style.RESET_ALL}')
                        continue
                    self.add_tr(_wrd, _tr, _transform=False)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    self.remove_tr(_wrd, _transform=False)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    print(f'Неизвестная команда: "{_cmd}"')
            elif _cmd in ['Ф', 'A']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить форму')
                print('У - Удалить форму')
                print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    print()
                    _frm_type = choose_frm_type()
                    if _frm_type in self.d[_wrd].forms.keys():
                        print(f'\n{Fore.RED}У слова "{_wrd}" уже есть такая форма{Style.RESET_ALL}')
                    else:
                        _frm = input('\nВведите форму слова: ')
                        self.add_frm(_wrd, _frm_type, _frm, _transform=False)
                        _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    if self.d[_wrd].count_f == 0:
                        print(f'{Fore.RED}У этого слова нет других форм{Style.RESET_ALL}')
                        continue
                    self.remove_frm_with_choose(_wrd, _transform=False)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    print(f'Неизвестная команда: "{_cmd}"')
            elif _cmd in ['СН', 'CY']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить сноску')
                print('У - Удалить сноску')
                print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    _dsc = input('\nВведите сноску: ')
                    self.add_dsc(_wrd, _dsc, _transform=False)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    if self.d[_wrd].count_d == 0:
                        print(f'{Fore.RED}В этой статье нет сносок{Style.RESET_ALL}')
                        continue
                    self.remove_dsc(_wrd, _transform=False)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    allert_inp('Неизвестная команда', _cmd)
            elif _cmd in ['И', 'B']:
                self.d[_wrd].fav = not self.d[_wrd].fav
                _has_changes = True
            elif _cmd in ['У', 'E']:
                _cmd = input('\nВы уверены, что хотите удалить эту запись? (+ или -): ')
                if _cmd == '+':
                    self.remove_note(_wrd, _transform=False)
                    _has_changes = True
                    break
            elif _cmd in ['Н', 'Y']:
                break
            else:
                allert_inp('Неизвестная команда', _cmd)
        return _has_changes

    """ Выбор случайного слова с учётом сложности """
    def random_hard(self):
        _sum = 0
        for _note in self.d.values():
            _sum += (100 - round(100 * _note.percent)) * 5 + 1
            if _note.all_tries < 5:
                _sum += (5 - _note.all_tries) * 40
        _r = random.randint(1, _sum)

        for _key in self.d.keys():
            _r -= (100 - round(100 * self.d[_key].percent)) * 5 + 1
            if self.d[_key].all_tries < 5:
                _r -= (5 - self.d[_key].all_tries) * 40
            if _r <= 0:
                return _key

    """ Учить слова - все """
    def learn(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                if _key not in _used_words:
                    break

            _res = guess_wrd(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова - избранные """
    def learn_fav(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w:
                    print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                    return None
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add(_key)
                    continue
                if _key not in _used_words:
                    break

            _res = guess_wrd(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова - все, сначала сложные """
    def learn_hard(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = self.random_hard()
                if _key not in _used_words:
                    break

            _res = guess_wrd(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (словоформы) - все """
    def learn_f(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w + self.count_f:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_key], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_key].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_key], _wrd_f, _count_correct, _count_all)
                        break

            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd_f)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (словоформы) - избранные """
    def learn_f_fav(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w + self.count_f:
                    print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                    return None
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add(_key)
                    for _frm in self.d[_key].forms.keys():
                        _used_words.add(_frm)
                    continue
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_key], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_key].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_key], _wrd_f, _count_correct, _count_all)
                        break

            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd_f)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (словоформы) - все, сначала сложные """
    def learn_f_hard(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w + self.count_f:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = self.random_hard()
                _rnd_f = random.randint(-1, self.d[_key].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _key
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_key], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_key].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_key], _wrd_f, _count_correct, _count_all)
                        break

            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd_f)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (обр.) - все """
    def learn_t(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = random.choice(list(self.d.keys()))
                if _key not in _used_words:
                    break

            _res = guess_tr(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (обр.) - избранные """
    def learn_t_fav(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            while True:
                if len(_used_words) == self.count_w:
                    print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                    return None
                _key = random.choice(list(self.d.keys()))
                if not self.d[_key].fav:
                    _used_words.add(_key)
                    continue
                if _key not in _used_words:
                    break

            _res = guess_tr(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True

    """ Учить слова (обр.) - все, сначала сложные """
    def learn_t_hard(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                print(f'{Fore.MAGENTA}Ваш результат: {_count_correct}/{_count_all}{Style.RESET_ALL}')
                break
            while True:
                _key = self.random_hard()
                if _key not in _used_words:
                    break

            _res = guess_tr(self.d[_key], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_key)
            elif _res == 3:
                _count_all += 1

        return True


# Прочитать файл с настройками словаря
def read_local_settings(_filename):
    _local_settings_fn = os.path.join(LOCAL_SETTINGS_DIR, _filename)
    try:
        open(_local_settings_fn, 'r')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(_local_settings_fn, 'w') as _locSetF:
            _locSetF.write('Число\n'
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
    with open(_local_settings_fn, 'r') as _locSetF:
        while True:
            _key = _locSetF.readline().strip()
            if not _key:
                break
            _value = _locSetF.readline().strip().split(FORMS_SEPARATOR)
            _form_parameters[_key] = _value
    return _form_parameters


# Сохранить настройки словаря
def save_local_settings(_form_parameters, _filename):
    _local_settings_fn = os.path.join(LOCAL_SETTINGS_DIR, _filename)
    with open(_local_settings_fn, 'w') as _locSetF:
        for _key in _form_parameters.keys():
            _locSetF.write(f'{_key}\n')
            if len(_form_parameters[_key]) != 0:
                _locSetF.write(_form_parameters[_key][0])
            for _i in range(1, len(_form_parameters[_key])):
                _locSetF.write(f'{FORMS_SEPARATOR}{_form_parameters[_key][_i]}')
            _locSetF.write('\n')


# Прочитать словарь и его настройки из файлов
def read_dct(_dct, _filename):
    _filepath = os.path.join(SAVES_DIR, _filename)
    _res_code = _dct.read(_filepath)
    print()
    if _res_code == 0:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'Файл со словарём {Fore.YELLOW}"{_filename}"{Style.RESET_ALL} открыт')
        return read_local_settings(_filename)
    elif _res_code == 1:  # Если файл отсутствует, то создаётся пустой словарь
        print(f'{Fore.RED}Файл "{_filename}" не найден{Style.RESET_ALL}')
        open(_filepath, 'w')
        _dct.read(_filepath)
        print('Создан файл с пустым словарём')
        return read_local_settings(_filename)
    elif _res_code == 2:  # Если файл повреждён, то предлагается открыть другой файл
        print(f'{Fore.RED}Файл "{_filename}" повреждён или некорректен{Style.RESET_ALL}')
        while True:
            print('\nХотите открыть другой словарь?')
            print('О - Открыть другой словарь')
            print('З - Завершить работу')
            _cmd = input().upper()
            if _cmd in ['О', 'J']:
                _filename = input('\nВведите название файла со словарём (если он ещё не существует, то будет создан пустой словарь): ')
                with open(SETTINGS_FN, 'w') as _setF:
                    _setF.write(dct_filename)
                _dct = Dictionary()
                read_dct(_dct, _filename)
                break
            elif _cmd in ['З', 'P']:
                exit()
            else:
                allert_inp('Неизвестная команда', _cmd)


# Создать и прочитать словарь и его настройки
def create_dct(_dct, _filename):
    _filepath = os.path.join(SAVES_DIR, _filename)
    open(_filepath, 'w')
    _dct.read(_filepath)
    print(f'\nФайл "{_filename}" успешно создан и открыт')
    return read_local_settings(_filename)


# Сохранить словарь и его настройки
def save_dct(_dct, _form_parameters, _filename):
    _filepath = os.path.join(SAVES_DIR, _filename)
    _dct.save(_filepath)
    save_local_settings(_form_parameters, _filename)


# Настройки форм слов
def forms_settings(_dct, _form_parameters):
    while True:
        print('\nСуществующие параметры форм:')
        _keys = [_key for _key in _form_parameters.keys()]
        for _i in range(len(_keys)):
            print(f'{_keys[_i]}')
        print('\nЧто вы хотите сделать?')
        print('Д - Добавить параметр форм')
        print('У - Удалить параметр форм')
        print('П - Переименовать параметр форм')
        print('И - Изменить значения параметра форм')
        print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
        _cmd = input().upper()
        if _cmd in ['Д', 'L']:
            add_frm_param(_form_parameters)
        elif _cmd in ['У', 'E']:
            remove_frm_param(_form_parameters, _dct)
        elif _cmd in ['П', 'G']:
            rename_frm_param(_form_parameters, _dct)
        elif _cmd in ['И', 'B']:
            while True:
                print('\nКакой параметр форм вы хотите изменить?')
                print('Выберите одно из предложенного')
                _keys = [_key for _key in _form_parameters.keys()]
                for _i in range(len(_keys)):
                    print(f'{_i} - {_keys[_i]}')
                print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
                _index = input('Введите номер варианта: ')
                if _index.upper() in ['Н', 'Y']:
                    break
                try:
                    _index = int(_index)
                    _frm_list = _form_parameters[_keys[_index]]
                except (ValueError, IndexError):
                    allert_inp('Недопустимый номер варианта', _index)
                    continue
                while True:
                    print('\nСуществующие значения параметра:')
                    for _i in range(len(_frm_list)):
                        print(f'{_frm_list[_i]}')
                    print('\nЧто вы хотите сделать?')
                    print('Д - Добавить значение параметра')
                    print('У - Удалить значение параметра')
                    print('П - Переименовать значение параметра')
                    print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
                    _cmd = input().upper()
                    if _cmd in ['Д', 'L']:
                        add_frm_val(_frm_list)
                    elif _cmd in ['У', 'E']:
                        remove_frm_val(_frm_list, _dct)
                    elif _cmd in ['П', 'G']:
                        rename_frm_val(_frm_list, _dct)
                    elif _cmd in ['Н', 'Y']:
                        break
                    else:
                        allert_inp('Неизвестная команда', _cmd)
        elif _cmd in ['Н', 'Y']:
            break
        else:
            allert_inp('Неизвестная команда', _cmd)


# Вывод информации о программе
print('======================================================================================\n')
print(f'                            {Fore.RED}Anenokil development{Style.RESET_ALL}  presents')
print(f'                               {Fore.CYAN}Dictionary{Style.RESET_ALL}  v6.0.0_PRE-9')
print('                                   23.12.2022 21:03\n')
print('======================================================================================')

try:  # Открываем файл с названием словаря
    open(SETTINGS_FN, 'r')
except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
    with open(SETTINGS_FN, 'w') as setF:
        setF.write('words.txt')
with open(SETTINGS_FN, 'r') as setF:
    dct_filename = setF.readline().strip()

dct = Dictionary()
form_parameters = read_dct(dct, dct_filename)  # Загружаем словарь и его настройки

print(f'\nИспользуйте эти комбинации для немецких букв: '
      f'{Fore.YELLOW}#a = ä{Style.RESET_ALL}, '
      f'{Fore.YELLOW}#o = ö{Style.RESET_ALL}, '
      f'{Fore.YELLOW}#u = ü{Style.RESET_ALL}, '
      f'{Fore.YELLOW}#s = ß{Style.RESET_ALL}')

has_changes = False
while True:
    print('\nЧто вы хотите сделать?')
    print('Н  - Напечатать словарь')
    print('НИ - Напечатать словарь (только Избранные статьи)')
    print('Д  - Добавить статью')
    print('И  - Изменить статью')
    print('НС - Найти статью по Слову')
    print('НП - Найти статью по Переводу')
    print('У  - Учить слова')
    print('Ф  - открыть настройки словоФорм')
    print('С  - Сохранить изменения')
    print('СЛ - открыть список СЛоварей')
    print('З  - Завершить работу')
    cmd = input().upper()
    if cmd in ['Н', 'Y']:
        cmd = input('\nВыводить все формы слов? (+ или -): ')
        if cmd == '+':
            dct.print_with_forms()
        else:
            dct.print()
    elif cmd in ['НИ', 'YB']:
        cmd = input('\nВыводить все формы слов? (+ или -): ')
        if cmd == '+':
            dct.print_fav_with_forms()
        else:
            dct.print_fav()
    elif cmd in ['Д', 'L']:
        wrd = input('\nВведите слово, которое хотите добавить в словарь: ')
        if wrd == '':
            print(f'{Fore.RED}Слово не может быть пустым{Style.RESET_ALL}')
            continue
        tr = input('Введите перевод слова: ')
        if tr == '':
            print(f'{Fore.RED}Перевод не может быть пустым{Style.RESET_ALL}')
            continue
        key = dct.add_val(wrd, tr)

        cmd = input('Хотите добавить сноску? (+ или -): ')
        if cmd == '+':
            dsc = input('Введите сноску: ')
            dct.add_dsc(key, dsc, _transform=False)

        fav = input('Хотите добавить статью в избранное? (+ или -): ')
        if fav == '+':
            dct.d[key].fav = True

        has_changes = True
        dct.edit_note(key, _transform=False)
    elif cmd in ['И', 'B']:
        wrd = input('\nВведите слово, статью с которым хотите изменить: ')
        if wrd_to_key(wrd, 0) not in dct.d.keys():
            print(f'{Fore.RED}Слово "{wrd}" отсутствует в словаре{Style.RESET_ALL}')
            continue
        has_changes = dct.edit_note(wrd)
    elif cmd in ['НС', 'YC']:
        wrd = input('\nВведите слово, которое хотите найти: ')
        if wrd_to_key(wrd, 0) not in dct.d.keys():
            print(f'{Fore.RED}Слово "{wrd}" отсутствует в словаре{Style.RESET_ALL}')
            continue
        for i in range(MAX_SIMILAR_WORDS):
            key = wrd_to_key(wrd, i)
            if key not in dct.d.keys():
                break
            print()
            dct.d[key].print_all()
    elif cmd in ['НП', 'YG']:
        tr = input('\nВведите перевод слова, которое хотите найти: ')
        isFound = False
        for key in dct.d.keys():
            if tr in dct.d[key].tr:
                isFound = True
                print()
                dct.d[key].print_all()
        if not isFound:
            print(f'{Fore.RED}Слово с переводом "{tr}" отсутствует в словаре{Style.RESET_ALL}')
    elif cmd in ['У', 'E']:
        print(Fore.YELLOW + '\nВаша общая доля правильных ответов: {:.2%}'.format(dct.count_rating()) + Style.RESET_ALL)
        print('\nВыберите способ')
        print('1 - Угадывать слово по переводу')
        print('2 - Угадывать перевод по слову')
        cmd = input().upper()
        if cmd == '1':
            print('\nВыберите способ')
            print('1 - Со всеми словоформами')
            print('2 - Только начальные формы')
            cmd = input().upper()
            if cmd == '1':
                print('\nВыберите способ')
                print('В - Все слова')
                print('С - все слова (в первую очередь Сложные)')
                print('И - только Избранные слова')
                cmd = input().upper()
                if cmd in ['В', 'D']:
                    has_changes = dct.learn_f()
                elif cmd in ['И', 'B']:
                    has_changes = dct.learn_f_fav()
                elif cmd in ['С', 'C']:
                    has_changes = dct.learn_f_hard()
                else:
                    allert_inp('Неизвестная команда', cmd)
            elif cmd == '2':
                print('\nВыберите способ')
                print('В - Все слова')
                print('С - все слова (в первую очередь Сложные)')
                print('И - только Избранные слова')
                cmd = input().upper()
                if cmd in ['В', 'D']:
                    has_changes = dct.learn()
                elif cmd in ['И', 'B']:
                    has_changes = dct.learn_fav()
                elif cmd in ['С', 'C']:
                    has_changes = dct.learn_hard()
                else:
                    allert_inp('Неизвестная команда', cmd)
            else:
                allert_inp('Неизвестная команда', cmd)
        elif cmd == '2':
            print('\nВыберите способ')
            print('В - Все слова')
            print('С - все слова (в первую очередь Сложные)')
            print('И - только Избранные слова')
            cmd = input().upper()
            if cmd in ['В', 'D']:
                has_changes = dct.learn_t()
            elif cmd in ['И', 'B']:
                has_changes = dct.learn_t_fav()
            elif cmd in ['С', 'C']:
                has_changes = dct.learn_t_hard()
            else:
                allert_inp('Неизвестная команда', cmd)
        else:
            allert_inp('Неизвестная команда', cmd)
    elif cmd in ['Ф', 'A']:
        forms_settings(dct, form_parameters)
        has_changes = True
    elif cmd in ['С', 'C']:
        save_dct(dct, form_parameters, dct_filename)
        save_local_settings(form_parameters, dct_filename)
        print(f'\n{Fore.GREEN}Успешно сохранено{Style.RESET_ALL}')
        has_changes = False
    elif cmd in ['СЛ', 'CK']:
        while True:
            print(f'\nСуществующие словари:')
            s_count = 0
            s_list = []
            for filename in os.listdir(SAVES_DIR):
                base_name, ext = os.path.splitext(filename)
                if ext == '.txt':
                    if filename == dct_filename:
                        print(f'{s_count} - {filename} {Fore.MAGENTA}(ТЕКУЩИЙ){Style.RESET_ALL}')
                    else:
                        print(f'{s_count} - {filename}')
                    s_list += [filename]
                    s_count += 1

            print(f'\nЧто вы хотите сделать?')
            print(f'О - Открыть словарь')
            print(f'С - Создать новый словарь')
            print(f'П - Переименовать словарь')
            print(f'У - Удалить словарь')
            print(f'{Fore.YELLOW}Н - Назад{Style.RESET_ALL}')
            cmd = input().upper()

            if cmd in ['Н', 'Y']:
                break
            elif cmd in ['П', 'G']:
                cmd = input('\nВведите номер словаря: ')
                try:
                    old_name = s_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    allert_inp('Недопустимый номер варианта', cmd)
                    continue

                new_name = input('Введите новое название: ')
                if new_name[-4:] != '.txt':
                    new_name += '.txt'
                if new_name == '.txt':
                    print(f'{Fore.RED}Недопустимое название{Style.RESET_ALL}')
                    continue
                if new_name in s_list:
                    print(f'{Fore.RED}Файл с таким названием уже существует{Style.RESET_ALL}')
                    continue

                os.rename(os.path.join(SAVES_DIR, old_name), os.path.join(SAVES_DIR, new_name))
                os.rename(os.path.join(LOCAL_SETTINGS_DIR, old_name), os.path.join(LOCAL_SETTINGS_DIR, new_name))
                if dct_filename == old_name:
                    dct_filename = new_name
                    with open(SETTINGS_FN, 'w') as setF:
                        setF.write(new_name)
                print(f'\nСловарь "{old_name}" успешно переименован в "{new_name}"')
            elif cmd in ['У', 'E']:
                cmd = input('\nВведите номер словаря: ')
                try:
                    filename = s_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    allert_inp('Недопустимый номер варианта', cmd)
                    continue
                if filename == dct_filename:
                    print(f'{Fore.RED}Вы не можете удалить этот словарь, т.к. он сейчас открыт{Style.RESET_ALL}')
                    continue
                cmd = input(f'Вы уверены? Словарь "{filename}" будет безвозвратно удалён! (+ или -): ')
                if cmd == '+':
                    os.remove(os.path.join(SAVES_DIR, filename))
                    os.remove(os.path.join(LOCAL_SETTINGS_DIR, filename))
                    print(f'\nСловарь "{filename}" успешно удалён')
            elif cmd in ['С', 'C']:
                filename = input('\nВведите название файла со словарём: ')
                if filename[-4:] != '.txt':
                    filename += '.txt'
                if filename == '.txt':
                    print(f'{Fore.RED}Недопустимое название{Style.RESET_ALL}')
                    continue
                if filename in s_list:
                    print(f'{Fore.RED}Файл с таким названием уже существует{Style.RESET_ALL}')
                    continue

                if has_changes:
                    cmd = input('\nХотите сохранить изменения и свой прогресс? (+ или -): ')
                    if cmd == '+':
                        save_dct(dct, form_parameters, dct_filename)
                        save_local_settings(form_parameters, dct_filename)
                dct_filename = filename
                with open(SETTINGS_FN, 'w') as setF:
                    setF.write(filename)
                dct = Dictionary()
                form_parameters = create_dct(dct, filename)
            elif cmd in ['О', 'J']:
                cmd = input('\nВведите номер словаря: ')
                try:
                    filename = s_list[int(cmd)]
                except (ValueError, TypeError, IndexError):
                    allert_inp('Недопустимый номер варианта', cmd)
                    continue
                if has_changes:
                    cmd = input('\nХотите сохранить изменения и свой прогресс? (+ или -): ')
                    if cmd == '+':
                        save_dct(dct, form_parameters, dct_filename)
                        save_local_settings(form_parameters, dct_filename)
                dct_filename = filename
                with open(SETTINGS_FN, 'w') as setF:
                    setF.write(filename)
                dct = Dictionary()
                form_parameters = read_dct(dct, filename)
            else:
                allert_inp('Неизвестная команда', cmd)
    elif cmd in ['З', 'P']:
        if has_changes:
            cmd = input('Хотите сохранить изменения и свой прогресс? (+ или -): ')
            if cmd == '+':
                save_dct(dct, form_parameters, dct_filename)
                save_local_settings(form_parameters, dct_filename)
        break
    else:
        allert_inp('Неизвестная команда', cmd)
