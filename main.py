import random
import os

RESOURCES_DIR = 'resources'
SAVES_DIR = os.path.join(RESOURCES_DIR, 'saves')
SETTINGS_FN = os.path.join(RESOURCES_DIR, 'settings.txt')
LOCAL_SETTINGS_DIR = os.path.join(RESOURCES_DIR, 'local_settings')
FORMS_SEPARATOR = '@'


def code(_str):  # Добавить немецкие буквы
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


def code_tpl(_tuple, _separator=FORMS_SEPARATOR):  # Перевести кортеж в строку
    _res = ''
    if len(_tuple) != 0:
        _res += _tuple[0]
    for _i in range(1, len(_tuple)):
        _res += f'{_separator}{_tuple[_i]}'
    return _res


def decode_tpl(_str, _separator=FORMS_SEPARATOR):  # Перевести строку в кортеж
    return tuple(_str.split(_separator))


def tpl(_tuple):
    return code_tpl(_tuple, ', ')


def add_frm_val(_frm_list):  # Добавить значение параметра формы слова
    _new_f = input('\nВведите новое значение параметра: ')
    if _new_f in _frm_list:
        print(f'Значение "{_new_f}" уже существует')
    elif _new_f == '':
        print('Недопустимое значение')
    elif FORMS_SEPARATOR in _new_f:
        print(f'Недопустимый символ: "{FORMS_SEPARATOR}"')
    else:
        _frm_list += [_new_f]


def remove_frm_val(_frm_list):  # Удалить значение параметра формы слова
    if len(_frm_list) == 1:
        print('\nВы не можете удалить единственное значение параметра')
        return
    print('\nВыберите один из предложенных вариантов')
    for _i in range(len(_frm_list)):
        print(f'{_i} - {_frm_list[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _frm_list.pop(int(_index))
    except (ValueError, IndexError):
        print(f'Недопустимый номер варианта: "{_index}"')


def add_frm_param(_frm_parameters):  # Добавить параметр форм
    _new_p = input('\nВведите новый параметр: ')
    if _new_p in _frm_parameters.keys():
        print(f'Параметр "{_new_p}" уже существует')
    elif _new_p == '':
        print('Недопустимый параметр')
    else:
        _frm_parameters[_new_p] = []
        print('Необходимо добавить хотя бы одно значение для параметра')
        while _frm_parameters[_new_p] == []:
            add_frm_val(_frm_parameters[_new_p])


def remove_frm_param(_frm_parameters):  # Удалить параметр форм
    print('\nВыберите один из предложенных вариантов')
    _keys = [_key for _key in _frm_parameters.keys()]
    for _i in range(len(_keys)):
        print(f'{_i} - {_keys[_i]}')
    _index = input('Введите номер варианта: ')
    try:
        _frm_parameters.pop(_keys[int(_index)])
    except (ValueError, IndexError):
        print(f'Недопустимый номер варианта: "{_index}"')


def choose_frm_param(_frm_name, _frm_list):  # Выбрать значение одного из параметров формы слова
    while True:
        print(f'\nВыберите {_frm_name}')
        for _i in range(len(_frm_list)):
            print(f'{_i} - {_frm_list[_i]}')
        print('Н - Не указывать/Неприменимо')
        print('Д - Добавить новый вариант')
        _cmd = input().upper()
        if _cmd in ['Н', 'Y']:
            return ''
        elif _cmd in ['Д', 'L']:
            add_frm_val(_frm_list)
        else:
            try:
                return _frm_list[int(_cmd)]
            except (ValueError, IndexError):
                print(f'Недопустимый вариант: "{_cmd}"')


def choose_frm_type():  # Выбрать параметр формы слова
    print('Выберите тип формы слова')
    _res = []
    for _key in form_parameters:
        _tmp = choose_frm_param(_key, form_parameters[_key])
        if _tmp != '':
            _res += [_tmp]
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
        if _dsc == None:
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
        if self.last_tries == -1:
            print('[-:  0%]', end=_end)
        else:
            _perc = '{:.0%}'.format(self.percent)
            _tab = ' ' * (4 - len(_perc))
            print(f'[{self.last_tries}:{_tab}{_perc}]', end=_end)

    """ Напечатать запись - кратко """
    def print_briefly(self):
        if self.fav:
            print('(*)', end=' ')
        else:
            print('   ', end=' ')

        self.stat_print(_end=' ')

        print(code(self.wrd) + ': ', end='')
        self.tr_print()
        self.dsc_print(_tab=13)

    """ Напечатать запись - кратко с формами """
    def print_briefly_with_forms(self):
        if self.fav:
            print('(*)', end=' ')
        else:
            print('   ', end=' ')

        self.stat_print(_end=' ')

        print(code(self.wrd) + ': ', end='')
        self.tr_print()
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
        print(f'({_frm_type})', end=' ')
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
            print(f'У этого слова уже есть такой перевод')

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
            print(f'Слово уже имеет форму {tpl(_frm_type)}: {self.forms[_frm_type]}')

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
            print('Вы не можете удалить единственный перевод слова')
            return
        print('Выберите один из предложенных вариантов')
        for _i in range(self.count_t):
            print(f'{_i} - {code(self.tr[_i])}')
        _index = input('Введите номер варианта: ')
        try:
            _index = int(_index)
            self.tr.pop(_index)
        except (ValueError, IndexError):
            print(f'Недопустимый номер варианта: "{_index}"')
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
            print(f'Недопустимый номер варианта: "{_index}"')
        else:
            self.count_d -= 1

    """ Удалить форму слова """
    def remove_frm(self):
        _keys = [_key for _key in self.forms.keys()]
        print('Выберите один из предложенных вариантов')
        for _i in range(self.count_f):
            print(f'{_i} - [{tpl(_keys[_i])}] {code(self.forms[_keys[_i]])}')
        _index = input('Введите номер варианта: ')
        try:
            _index = int(_index)
            self.forms.pop(_keys[_index])
        except (ValueError, IndexError):
            print(f'Недопустимый номер варианта: "{_index}"')
        else:
            self.count_f -= 1

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


def guess_wrd(_note, _count_correct, _count_all):  # Угадать слово по переводу
    print()
    _note.print_tr_with_stat()
    _wrd_ans = input('Введите слово (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input('Введите слово (# - чтобы закончить): ')
    if _wrd_ans == '#':
        print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
        return 1

    if _wrd_ans == _note.wrd:
        _note.correct_try()
        print('\033[32mВерно\033[38m')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'\033[31mНеверно. Правильный ответ: "{_note.wrd}"\033[38m')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


def guess_wrd_f(_note, _wrd_f, _count_correct, _count_all):  # Угадать словоформу по переводу
    print()
    _note.print_tr_and_frm_with_stat(_wrd_f)
    _wrd_ans = input('Введите слово в данной форме (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input('Введите слово в данной форме (# - чтобы закончить): ')
    if _wrd_ans == '#':
        print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
        return 1

    if _wrd_ans == _note.forms[_wrd_f]:
        _note.correct_try()
        print('\033[32mВерно\033[38m')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'\033[31mНеверно. Правильный ответ: "{_note.wrd}"\033[38m')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


def guess_tr(_note, _count_correct, _count_all):  # Угадать перевод по слову
    print()
    _note.print_wrd_with_stat()
    _wrd_ans = input('Введите перевод (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
    if _wrd_ans == '@':
        _note.dsc_print()
        _wrd_ans = input('Введите перевод (# - чтобы закончить): ')
    if _wrd_ans == '#':
        print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
        return 1

    if _wrd_ans in _note.tr:
        _note.correct_try()
        print('\033[32mВерно\033[38m')
        if _note.fav:
            _fav = input('Оставить слово в избранном? (+ или -): ')
            if _fav == '-':
                _note.fav = False
        return 2
    else:
        _note.incorrect_try()
        print(f'\033[31mНеверно. Правильный ответ: {_note.tr}\033[38m')
        if not _note.fav:
            _fav = input('Добавить слово в избранное? (+ или -): ')
            if _fav == '+':
                _note.fav = True
        return 3


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
        print(f'< {self.count_w} сл. | {self.count_w + self.count_f} словоформ. | {self.count_t} перев. >')

    """ Напечатать словарь (со всеми формами) """
    def print_with_forms(self):
        for _note in self.d.values():
            _note.print_briefly_with_forms()
        print(f'< {self.count_w} сл. | {self.count_w + self.count_f} словоформ. | {self.count_t} перев. >')

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
        print(f'< {_count_w}/{self.count_w} сл. | {_count_w + _count_f}/{self.count_w + self.count_f} словоформ. | {_count_t}/{self.count_t} перев. >')

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
        print(f'< {_count_w}/{self.count_w} сл. | {_count_w + _count_f}/{self.count_w + self.count_f} словоформ. | {_count_t}/{self.count_t} перев. >')

    """ Подсчитать среднюю долю правильных ответов """
    def count_rating(self):
        _sum_num = 0
        _sum_den = 0
        for _note in self.d.values():
            _sum_num += _note.correct_tries
            _sum_den += _note.all_tries
        return _sum_num / _sum_den

    """ Добавить запись в словарь (при чтении сохранения) """
    def add_note(self, _wrd, _tr, _all_tries, _correct_tries, _last_tries):
        self.d[_wrd] = Note(_wrd, [_tr], _all_tries=_all_tries, _correct_tries=_correct_tries, _last_tries=_last_tries)
        self.count_w += 1
        self.count_t += 1

    """ Добавить запись в словарь """
    def add_val(self, _wrd, _tr, _show_msg=True):
        if _wrd in self.d.keys():
            self.add_tr(_wrd, _tr, _show_msg)
        else:
            self.d[_wrd] = Note(_wrd, [_tr])
            self.count_w += 1
            self.count_t += 1

    """ Изменить слово """
    def edit_wrd(self, _wrd, _new_wrd):
        if _new_wrd in self.d.keys():
            self.count_t -= self.d[_wrd].count_t
            self.count_t -= self.d[_new_wrd].count_t
            for _tr in self.d[_wrd].tr:
                self.d[_new_wrd].add_tr(_tr, False)
            for _dsc in self.d[_wrd].dsc:
                self.add_dsc(_new_wrd, _dsc)
            self.count_t += self.d[_new_wrd].count_t
            self.count_w -= 1
            if self.d[_wrd].fav:
                self.d[_new_wrd].fav = True
            self.d[_new_wrd].merge_stat(self.d[_wrd].all_tries, self.d[_wrd].correct_tries, self.d[_wrd].last_tries)
        else:
            self.d[_new_wrd] = Note(_new_wrd, self.d[_wrd].tr, self.d[_wrd].dsc, self.d[_wrd].fav, self.d[_wrd].all_tries, self.d[_wrd].correct_tries, self.d[_wrd].last_tries)
        self.d.pop(_wrd)

    """ Добавить перевод к записи в словаре """
    def add_tr(self, _wrd, _tr, _show_msg=True):
        self.count_t -= self.d[_wrd].count_t
        self.d[_wrd].add_tr(_tr, _show_msg)
        self.count_t += self.d[_wrd].count_t

    """ Добавить сноску к записи в словаре """
    def add_dsc(self, _wrd, _dsc):
        self.d[_wrd].add_dsc(_dsc)

    """ Добавить форму слова к записи в словаре """
    def add_frm(self, _wrd, _frm_type, _frm, _show_msg=True):
        self.count_f -= self.d[_wrd].count_f
        self.d[_wrd].add_frm(_frm_type, _frm, _show_msg)
        self.count_f += self.d[_wrd].count_f

    """ Удалить перевод из словаря """
    def remove_tr(self, _wrd):
        self.count_t -= self.d[_wrd].count_t
        self.d[_wrd].remove_tr()
        self.count_t += self.d[_wrd].count_t

    """ Удалить описание из словаря """
    def remove_dsc(self, _wrd):
        self.d[_wrd].remove_dsc()

    """ Удалить форму слова из словаря """
    def remove_frm(self, _wrd):
        self.count_f -= self.d[_wrd].count_f
        self.d[_wrd].remove_frm()
        self.count_f += self.d[_wrd].count_f

    """ Удалить запись из словаря """
    def remove_note(self, _wrd):
        self.count_w -= 1
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
                        self.add_note(_wrd, _tr, _all_tries, _correct_tries, _last_tries)
                    elif _line[0] == 't':
                        self.add_tr(_wrd, _line[1:], False)
                    elif _line[0] == 'd':
                        self.add_dsc(_wrd, _line[1:])
                    elif _line[0] == 'f':
                        _frm_type = decode_tpl(_line[1:])
                        self.add_frm(_wrd, _frm_type, _file.readline().strip())
                    elif _line[0] == '*':
                        self.d[_wrd].fav = True
            return 0
        except FileNotFoundError:
            return 1
        except (ValueError, TypeError):
            return 2

    """ Изменить запись в словаре """
    def edit_note(self, _wrd):
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
            print('Н  - вернуться Назад')
            _cmd = input().upper()
            if _cmd in ['СЛ', 'CK']:
                _new_wrd = input('\nВведите новое слово: ')
                self.edit_wrd(_wrd, _new_wrd)
                _wrd = _new_wrd
                _has_changes = True
            elif _cmd in ['П', 'G']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить перевод')
                print('У - Удалить перевод')
                print('Н - Назад')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    _tr = input('\nВведите перевод: ')
                    self.add_tr(_wrd, _tr)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    self.remove_tr(_wrd)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    print(f'Неизвестная команда: "{_cmd}"')
            elif _cmd in ['Ф', 'A']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить форму')
                print('У - Удалить форму')
                print('Н - Назад')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    print()
                    _frm_type = choose_frm_type()
                    if _frm_type in self.d[_wrd].forms.keys():
                        print(f'\nУ слова "{_wrd}" уже есть такая форма')
                    else:
                        _frm = input('\nВведите форму слова: ')
                        self.add_frm(_wrd, _frm_type, _frm)
                        _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    if self.d[_wrd].count_f == 0:
                        print('У этого слова нет других форм')
                        continue
                    self.remove_frm(_wrd)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    print(f'Неизвестная команда: "{_cmd}"')
            elif _cmd in ['СН', 'CY']:
                print('\nЧто вы хотите сделать?')
                print('Д - Добавить сноску')
                print('У - Удалить сноску')
                print('Н - Назад')
                _cmd = input().upper()
                if _cmd in ['Д', 'L']:
                    _dsc = input('\nВведите сноску: ')
                    self.add_dsc(_wrd, _dsc)
                    _has_changes = True
                elif _cmd in ['У', 'E']:
                    print()
                    if self.d[_wrd].count_d == 0:
                        print('В этой статье нет сносок')
                        continue
                    self.remove_dsc(_wrd)
                    _has_changes = True
                elif _cmd in ['Н', 'Y']:
                    continue
                else:
                    print(f'Неизвестная команда: "{_cmd}"')
            elif _cmd in ['И', 'B']:
                self.d[_wrd].fav = not self.d[_wrd].fav
                _has_changes = True
            elif _cmd in ['У', 'E']:
                _cmd = input('\nВы уверены, что хотите удалить эту запись? (+ или -): ')
                if _cmd == '+':
                    self.remove_note(_wrd)
                    _has_changes = True
                    break
            elif _cmd in ['Н', 'Y']:
                break
            else:
                print(f'Неизвестная команда: "{_cmd}"')
        return _has_changes

    """ Выбор случайного слова с учётом сложности """
    def random_smart(self):
        _sum = 0
        for _note in self.d.values():
            _sum += (100 - round(100 * _note.percent)) * 4 + 1
        _r = random.randint(1, _sum)

        for _wrd in self.d.keys():
            _r -= (100 - round(100 * self.d[_wrd].percent)) * 4 + 1
            if _r <= 0:
                return _wrd

    """ Учить слова - все """
    def learn(self):
        _count_all = 0
        _count_correct = 0
        _used_words = set()
        while True:
            if len(_used_words) == self.count_w:
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = random.choice(list(self.d.keys()))
                if _wrd not in _used_words:
                    break

            _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
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
                    print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                    return None
                _wrd = random.choice(list(self.d.keys()))
                if not self.d[_wrd].fav:
                    _used_words.add(_wrd)
                    continue
                if _wrd not in _used_words:
                    break

            _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
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
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = self.random_smart()
                if _wrd not in _used_words:
                    break

            _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
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
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = random.choice(list(self.d.keys()))
                _rnd_f = random.randint(-1, self.d[_wrd].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _wrd
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_wrd].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_wrd], _wrd_f, _count_correct, _count_all)
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
                    print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                    return None
                _wrd = random.choice(list(self.d.keys()))
                if not self.d[_wrd].fav:
                    _used_words.add(_wrd)
                    for _frm in self.d[_wrd].forms.keys():
                        _used_words.add(_frm)
                    continue
                _rnd_f = random.randint(-1, self.d[_wrd].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _wrd
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_wrd].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_wrd], _wrd_f, _count_correct, _count_all)
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
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = self.random_smart()
                _rnd_f = random.randint(-1, self.d[_wrd].count_f - 1)
                if _rnd_f == -1:
                    _wrd_f = _wrd
                    if _wrd_f not in _used_words:
                        _res = guess_wrd(self.d[_wrd], _count_correct, _count_all)
                        break
                else:
                    _wrd_f = random.choice(list(self.d[_wrd].forms.keys()))
                    if _wrd_f not in _used_words:
                        _res = guess_wrd_f(self.d[_wrd], _wrd_f, _count_correct, _count_all)
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
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = random.choice(list(self.d.keys()))
                if _wrd not in _used_words:
                    break

            _res = guess_tr(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
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
                    print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                    return None
                _wrd = random.choice(list(self.d.keys()))
                if not self.d[_wrd].fav:
                    _used_words.add(_wrd)
                    continue
                if _wrd not in _used_words:
                    break

            _res = guess_tr(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
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
                print(f'\033[33mВаш результат: {_count_correct}/{_count_all}\033[38m')
                break
            while True:
                _wrd = self.random_smart()
                if _wrd not in _used_words:
                    break

            _res = guess_tr(self.d[_wrd], _count_correct, _count_all)
            if _res == 1:
                break
            elif _res == 2:
                _count_all += 1
                _count_correct += 1
                _used_words.add(_wrd)
            elif _res == 3:
                _count_all += 1

        return True


def read_local_settings(_filename):  # Прочитать файл с настройками словаря
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
            _values = _locSetF.readline().strip().split(FORMS_SEPARATOR)
            _form_parameters[_key] = _values
    return _form_parameters


def save_local_settings(_form_parameters, _filename):  # Сохранить настройки словаря
    _local_settings_fn = os.path.join(LOCAL_SETTINGS_DIR, _filename)
    with open(_local_settings_fn, 'w') as _locSetF:
        for _key in _form_parameters.keys():
            _locSetF.write(f'{_key}\n')
            if len(_form_parameters[_key]) != 0:
                _locSetF.write(_form_parameters[_key][0])
            for _i in range(1, len(_form_parameters[_key])):
                _locSetF.write(f'{FORMS_SEPARATOR}{_form_parameters[_key][_i]}')
            _locSetF.write('\n')


def read_dct(_dct, _filename):  # Прочитать словарь и его настройки из файлов
    _filepath = os.path.join(SAVES_DIR, _filename)
    _res_code = _dct.read(_filepath)
    if _res_code == 0:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'Файл со словарём "{_filename}" открыт')
        return read_local_settings(_filename)
    elif _res_code == 1:  # Если файл отсутствует, то создаётся пустой словарь
        print(f'Файл "{_filename}" не найден')
        open(_filepath, 'w')
        _dct.read(_filepath)
        print('Создан файл с пустым словарём')
        return read_local_settings(_filename)
    elif _res_code == 2:  # Если файл повреждён, то предлагается открыть другой файл
        print(f'Файл "{_filename}" повреждён или некорректен')
        while True:
            print('\nХотите открыть другой словарь?')
            print('О - Открыть другой словарь')
            print('З - Завершить работу')
            _cmd = input().upper()
            if _cmd in ['О', 'J']:
                _filename = input('\nВведите название файла со словарём (если он ещё не существует, то будет создан пустой словарь): ')
                with open(SETTINGS_FN, 'w') as _setF:
                    _setF.write(filename)
                _dct = Dictionary()
                read_dct(_dct, _filename)
                break
            elif _cmd in ['З', 'P']:
                exit()
            else:
                print(f'Неизвестная команда: "{_cmd}"')


def save_dct(_dct, _form_parameters, _filename):  # Сохранить словарь и его настройки
    _filepath = os.path.join(SAVES_DIR, _filename)
    _dct.save(_filepath)
    save_local_settings(_form_parameters, _filename)


print('======================================================================================\n')  # Вывод информации о программе
print('                            Anenokil development  presents')
print('                              Dictionary  v6.0.0_PRE-3.1')
print('                                   22.12.2022  8:14\n')
print('======================================================================================\n')

try:  # Открываем файл с названием словаря
    open(SETTINGS_FN, 'r')
except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
    with open(SETTINGS_FN, 'w') as setF:
        setF.write('words.txt')
with open(SETTINGS_FN, 'r') as setF:
    filename = setF.readline().strip()

dct = Dictionary()
form_parameters = read_dct(dct, filename)  # Загружаем словарь и его настройки

print('\nИспользуйте эти комбинации для немецких букв: #a = ä, #o = ö, #u = ü, #s = ß')

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
    print('Ф  - настройки словоФорм')
    print('С  - Сохранить изменения')
    print('О  - Открыть другой словарь')
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
        tr = input('Введите перевод слова: ')
        dct.add_val(wrd, tr)

        cmd = input('Хотите добавить сноску? (+ или -): ')
        if cmd == '+':
            dsc = input('Введите сноску: ')
            dct.add_dsc(wrd, dsc)

        fav = input('Хотите добавить статью в избранное? (+ или -): ')
        if fav == '+':
            dct.d[wrd].fav = True

        has_changes = True
        dct.edit_note(wrd)
    elif cmd in ['И', 'B']:
        wrd = input('\nВведите слово, статью с которым хотите изменить: ')
        if wrd in dct.d.keys():
            has_changes = dct.edit_note(wrd)
        else:
            print(f'Слово "{wrd}" отсутствует в словаре')
    elif cmd in ['НС', 'YC']:
        wrd = input('\nВведите слово, которое хотите найти: ')
        if wrd in dct.d.keys():
            dct.d[wrd].print_all()
        else:
            print(f'Слово "{wrd}" отсутствует в словаре')
    elif cmd in ['НП', 'YG']:
        tr = input('\nВведите перевод слова, которое хотите найти: ')
        isFound = False
        for wrd in dct.d.keys():
            if tr in dct.d[wrd].tr:
                isFound = True
                print()
                dct.d[wrd].print_all()
        if not isFound:
            print(f'Слово с переводом "{tr}" отсутствует в словаре')
    elif cmd in ['У', 'E']:
        print('\nВаша общая доля правильных ответов: {:.2%}'.format(dct.count_rating()))
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
                    print(f'Неизвестная команда: "{cmd}"')
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
                    print(f'Неизвестная команда: "{cmd}"')
            else:
                print(f'Неизвестная команда: "{cmd}"')
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
                print(f'Неизвестная команда: "{cmd}"')
        else:
            print(f'Неизвестная команда: "{cmd}"')
    elif cmd in ['Ф', 'A']:
        while True:
            print('\nСуществующие параметры форм:')
            keys = [key for key in form_parameters.keys()]
            for i in range(len(keys)):
                print(f'{keys[i]}')
            print('\nЧто вы хотите сделать?')
            print('Д - Добавить параметр форм')
            print('У - Удалить параметр форм')
            print('И - Изменить параметр форм')
            print('Н - Назад')
            cmd = input().upper()
            if cmd in ['Д', 'L']:
                add_frm_param(form_parameters)
            elif cmd in ['У', 'E']:
                remove_frm_param(form_parameters)
            elif cmd in ['И', 'B']:
                while True:
                    print('\nКакой параметр форм вы хотите изменить?')
                    print('Выберите одно из предложенного')
                    keys = [key for key in form_parameters.keys()]
                    for i in range(len(keys)):
                        print(f'{i} - {keys[i]}')
                    print('Н - Назад')
                    index = input('Введите номер варианта: ')
                    if index.upper() in ['Н', 'Y']:
                        break
                    try:
                        index = int(index)
                        frm_list = form_parameters[keys[index]]
                    except (ValueError, IndexError):
                        print(f'Неверный номер варианта: "{index}"')
                        continue
                    while True:
                        print('\nСуществующие значения параметра:')
                        for i in range(len(frm_list)):
                            print(f'{frm_list[i]}')
                        print('\nЧто вы хотите сделать?')
                        print('Д - Добавить значение параметра')
                        print('У - Удалить значение параметра')
                        print('Н - Назад')
                        cmd = input().upper()
                        if cmd in ['Д', 'L']:
                            add_frm_val(frm_list)
                        elif cmd in ['У', 'E']:
                            remove_frm_val(frm_list)
                        elif cmd in ['Н', 'Y']:
                            break
                        else:
                            print(f'Неизвестная команда: "{cmd}"')
            elif cmd in ['Н', 'Y']:
                break
            else:
                print(f'Неизвестная команда: "{cmd}"')
    elif cmd in ['С', 'C']:
        save_dct(dct, form_parameters, filename)
        save_local_settings(form_parameters, filename)
        print('\nУспешно сохранено')
        has_changes = False
    elif cmd in ['О', 'J']:
        if has_changes:
            cmd = input('Хотите сохранить изменения и свой прогресс? (+ или -): ')
            if cmd == '+':
                save_dct(dct, form_parameters, filename)
                save_local_settings(form_parameters, filename)
        filename = input('\nВведите название файла со словарём (если он ещё не существует, то будет создан пустой словарь): ')
        with open(SETTINGS_FN, 'w') as setF:
            setF.write(filename)
        dct = Dictionary()
        form_parameters = read_dct(dct, filename)
    elif cmd in ['З', 'P']:
        if has_changes:
            cmd = input('Хотите сохранить изменения и свой прогресс? (+ или -): ')
            if cmd == '+':
                save_dct(dct, form_parameters, filename)
                save_local_settings(form_parameters, filename)
        break
    else:
        print(f'Неизвестная команда: "{cmd}"')

# разобраться с цветами
# доработать систему типов форм слова
# сделать чтобы можно было делать несколько статей с одинаковыми словами
