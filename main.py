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
import re  # Несколько разделителей в split
import urllib.request as urllib2  # Для проверки наличия обновлений
import wget  # Для загрузки обновления
import zipfile  # Для распаковки обновления

""" Информация о программе """

PROGRAM_NAME = 'Dictionary'
PROGRAM_VERSION = 'v7.0.0_PRE-96'
PROGRAM_DATE = '20.1.2023  23:31 (UTC+3)'

""" Пути и файлы """

# Ссылка на страницу программы на GitHub
URL_GITHUB = f'https://github.com/Anenokil/{PROGRAM_NAME}'
# Ссылка на файл с названием последней версией
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{PROGRAM_NAME}/master/ver'
# Ссылка для установки последней версии
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{PROGRAM_NAME}/archive/refs/heads/master.zip'

NEW_VERSION_DIR = f'{PROGRAM_NAME}-master'  # Временная папка с обновлением
NEW_VERSION_ZIP = f'{NEW_VERSION_DIR}.zip'  # Архив с обновлением

RESOURCES_DIR = 'resources'  # Папка с ресурсами
SAVES_DIR = 'saves'  # Папка с сохранениями
SAVES_PATH = os.path.join(RESOURCES_DIR, SAVES_DIR)
LOCAL_SETTINGS_DIR = 'local_settings'  # Папка с локальными настройками (настройки словаря)
LOCAL_SETTINGS_PATH = os.path.join(RESOURCES_DIR, LOCAL_SETTINGS_DIR)
GLOBAL_SETTINGS_FN = 'settings.txt'  # Файл с глобальными настройками (настройки программы)
GLOBAL_SETTINGS_PATH = os.path.join(RESOURCES_DIR, GLOBAL_SETTINGS_FN)
CUSTOM_THEMES_DIR = 'themes'  # Папка с пользовательскими темами
CUSTOM_THEMES_PATH = os.path.join(RESOURCES_DIR, CUSTOM_THEMES_DIR)

# Если папки отсутствуют, то они создаются
if RESOURCES_DIR not in os.listdir(os.curdir):
    os.mkdir(RESOURCES_DIR)
if SAVES_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(SAVES_PATH)
if LOCAL_SETTINGS_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(LOCAL_SETTINGS_PATH)
if CUSTOM_THEMES_DIR not in os.listdir(RESOURCES_DIR):
    os.mkdir(CUSTOM_THEMES_PATH)

""" Стандартные темы """

REQUIRED_THEME_VERSION = 1
THEMES = ['light', 'dark']  # Названия тем

# Все: bg
# Все, кроме frame: fg
# Все, кроме текста: border
# Frame: relief
# Кнопки: activebackground
# Entry: selectbackground, highlightcolor

# Стили для каждой темы
ST_BG          = {THEMES[0]: '#EEEEEE', THEMES[1]: '#222222'}  # Цвет фона окна
ST_BG_FIELDS   = {THEMES[0]: '#FFFFFF', THEMES[1]: '#171717'}  # Цвет фона полей ввода

ST_BORDER      = {THEMES[0]: '#222222', THEMES[1]: '#111111'}  # Цвет рамок
ST_RELIEF      = {THEMES[0]: 'groove',  THEMES[1]: 'solid'  }  # Стиль рамок

ST_SELECT      = {THEMES[0]: '#BBBBBB', THEMES[1]: '#444444'}  # Цвет выделения текста
ST_HIGHLIGHT   = {THEMES[0]: '#00DD00', THEMES[1]: '#007700'}  # Цвет подсветки виджета при фокусе

ST_BTN         = {THEMES[0]: '#D0D0D0', THEMES[1]: '#202020'}  # Цвет фона обычных кнопок
ST_BTN_SELECT  = {THEMES[0]: '#BABABA', THEMES[1]: '#272727'}  # Цвет фона обычных кнопок при нажатии
ST_BTNY        = {THEMES[0]: '#88DD88', THEMES[1]: '#446F44'}  # Цвет фона да-кнопок
ST_BTNY_SELECT = {THEMES[0]: '#77CC77', THEMES[1]: '#558055'}  # Цвет фона да-кнопок при нажатии
ST_BTNN        = {THEMES[0]: '#FF6666', THEMES[1]: '#803333'}  # Цвет фона нет-кнопок
ST_BTNN_SELECT = {THEMES[0]: '#EE5555', THEMES[1]: '#904444'}  # Цвет фона нет-кнопок при нажатии

ST_FG_TEXT     = {THEMES[0]: '#222222', THEMES[1]: '#979797'}  # Цвет обычного текста
ST_FG_LOGO     = {THEMES[0]: '#FF7200', THEMES[1]: '#803600'}  # Цвет текста логотипа
ST_FG_FOOTER   = {THEMES[0]: '#666666', THEMES[1]: '#666666'}  # Цвет текста нижнего колонтитула
ST_FG_WARN     = {THEMES[0]: '#DD2222', THEMES[1]: '#DD2222'}  # Цвет текста предупреждения

# Названия стилизуемых элементов
STYLE_ELEMENTS = ('BG', 'BG_FIELDS', 'BORDER', 'RELIEF', 'SELECT', 'HIGHLIGHT',
                  'BTN', 'BTN_SELECT', 'BTNY', 'BTNY_SELECT', 'BTNN', 'BTNN_SELECT',
                  'FG_TEXT', 'FG_LOGO', 'FG_FOOTER', 'FG_WARN')

# Стили для каждого элемента
STYLES = {STYLE_ELEMENTS[0]:  ST_BG,
          STYLE_ELEMENTS[1]:  ST_BG_FIELDS,
          STYLE_ELEMENTS[2]:  ST_BORDER,
          STYLE_ELEMENTS[3]:  ST_RELIEF,
          STYLE_ELEMENTS[4]:  ST_SELECT,
          STYLE_ELEMENTS[5]:  ST_HIGHLIGHT,
          STYLE_ELEMENTS[6]:  ST_BTN,
          STYLE_ELEMENTS[7]:  ST_BTN_SELECT,
          STYLE_ELEMENTS[8]:  ST_BTNY,
          STYLE_ELEMENTS[9]:  ST_BTNY_SELECT,
          STYLE_ELEMENTS[10]: ST_BTNN,
          STYLE_ELEMENTS[11]: ST_BTNN_SELECT,
          STYLE_ELEMENTS[12]: ST_FG_TEXT,
          STYLE_ELEMENTS[13]: ST_FG_LOGO,
          STYLE_ELEMENTS[14]: ST_FG_FOOTER,
          STYLE_ELEMENTS[15]: ST_FG_WARN}

""" Другое """

FORMS_SEPARATOR = '@'  # Разделитель для записи форм в файл

VALUES_ORDER = ('Угадывать слово по переводу', 'Угадывать перевод по слову')
VALUES_WORDS = ('Все слова', 'Чаще сложные', 'Только избранные')

MAX_SAME_WORDS = 100  # Максимальное количество статей с одинаковым словом

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

""" Основные функции """


# Количество строк, необходимых для записи текста, при данной длине строки
def height(text, len_str):
    parts = text.split('\n')
    return sum(math.ceil(len(part) / len_str) for part in parts)


# Ширина моноширинного поля, в которое должно помещаться каждое из данных значений
def width(values, min_width, max_width):
    max_of_vals = max(len(val) for val in values)
    return min(max(max_of_vals, min_width), max_width)


# Вывод текста на виджет
def outp(output_widget, text='', end='\n', mode=tk.END):
    output_widget.insert(mode, f'{text}{end}')


# Вывод сообщения с предупреждением
def warning(window_parent, msg):
    PopupMsgW(window_parent, msg, title='Warning').open()


# Напечатать специальную комбинацию
def special_combination(key):
    val = _0_global_special_combinations[key]
    return f'#{key} -> {val}\n'


# Добавить немецкие буквы
def deu_encode(text):
    text = text.replace('##', '#@')

    for key in _0_global_special_combinations:
        val = _0_global_special_combinations[key]
        text = text.replace(f'#{key}', val)

    text = text.replace('#@', '#')

    return text


# Заменить немецкие буквы английскими (для find_and_highlight)
def deu_to_eng(text):  # deu_to_eng только для немецкого
    text = text.replace('##', '1ä')
    text = text.replace('ss', '2ä')
    text = text.replace('sS', '2ä')
    text = text.replace('SS', '3ä')
    text = text.replace('Ss', '3ä')

    text = text.replace('#a', 'a')
    text = text.replace('#A', 'A')
    text = text.replace('#o', 'o')
    text = text.replace('#O', 'O')
    text = text.replace('#u', 'u')
    text = text.replace('#U', 'U')
    text = text.replace('#s', 's')
    text = text.replace('#S', 'S')

    text = text.replace('1ä', '#')
    text = text.replace('2ä', 's')
    text = text.replace('3ä', 'S')

    return text


# Перевести кортеж в строку (для вывода на экран)
def tpl(input_tuple):
    res = ''
    is_first = True
    for i in range(len(input_tuple)):
        if input_tuple[i] != '':
            if is_first:
                res += f'{input_tuple[i]}'
                is_first = False
            else:
                res += f', {input_tuple[i]}'
    return res


# Перевести кортеж в строку (для сохранения в файл)
def decode_tpl(input_tuple):
    if not input_tuple:
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{FORMS_SEPARATOR}{input_tuple[i]}'
    return res


# Перевести строку в кортеж (для чтения из файла)
def encode_tpl(line):
    return tuple(line.split(FORMS_SEPARATOR))


# Добавить значение параметра форм
def add_frm_param_val(window_parent, values, text='Введите новое значение параметра'):
    while True:
        window_entry = PopupEntryW(window_parent, text)  # Ввод нового значения
        closed, new_val = window_entry.open()
        if closed:
            return None
        if new_val == '':
            warning(window_parent, 'Значение параметра должно содержать хотя бы один символ!')
            continue
        if new_val in values:
            warning(window_parent, f'Значение "{new_val}" уже существует!')
            continue
        if FORMS_SEPARATOR in new_val:
            warning(window_parent, f'Недопустимый символ: {FORMS_SEPARATOR}!')
            continue
        break
    return new_val


# Переименовать значение параметра форм
def rename_frm_param_val(window_parent, values, pos, dct):
    window_choose = PopupChooseW(window_parent, values, default_value=values[0],
                                 combo_width=width(values, 5, 100))  # Выбор значения, которое нужно переименовать
    closed, old_val = window_choose.open()
    if closed or old_val == '':
        return
    while True:
        window_entry = PopupEntryW(window_parent,
                                   'Введите новое название для значения параметра')  # Ввод нового значения
        closed, new_val = window_entry.open()
        if closed:
            return
        if new_val == '':
            warning(window_parent, 'Значение параметра должно содержать хотя бы один символ!')
            continue
        if new_val in values:
            warning(window_parent, f'Значение "{new_val}" уже существует!')
            continue
        if FORMS_SEPARATOR in new_val:
            warning(window_parent, f'Недопустимый символ: {FORMS_SEPARATOR}!')
        break
    dct.rename_forms_with_val(pos, old_val, new_val)  # Переименовать значение во всех словоформах, его содержащих
    index = values.index(old_val)
    values[index] = new_val


# Удалить значение параметра форм
def delete_frm_param_val(window_parent, values, dct):
    window_choose = PopupChooseW(window_parent, values, default_value=values[0],
                                 combo_width=width(values, 5, 100))  # Выбор значения, которое нужно удалить
    closed, val = window_choose.open()
    if closed or val == '':
        return
    window_dia = PopupDialogueW(window_parent, 'Все словоформы, содержащие это значение параметра, будут удалены!\n'
                                               'Хотите продолжить?',
                                set_focus_on_btn='none')
    answer = window_dia.open()
    if answer:
        index = values.index(val)
        values.pop(index)
        dct.delete_forms_with_val(index, val)  # Удалить все словоформы, содержащие это значение параметра


# Добавить параметр словоформ
def add_frm_param(window_parent, parameters, dct):
    window_entry = EnterFormParameterNameW(window_parent, parameters.keys())
    name_is_correct, new_par = window_entry.open()
    if not name_is_correct:
        return

    new_val = add_frm_param_val(window_parent, (), 'Необходимо добавить хотя бы одно значение для параметра')
    if not new_val:
        return

    dct.add_forms_param()
    parameters[new_par] = []
    parameters[new_par] += [new_val]


# Переименовать параметр словоформ
def rename_frm_param(window_parent, parameters, dct):
    par_names = [par_name for par_name in parameters.keys()]
    window_choose = PopupChooseW(window_parent, par_names, default_value=par_names[0], btn_text='Переименовать',
                                 combo_width=width(par_names, 5, 100))
    closed, old_name = window_choose.open()
    if closed or old_name == '':
        return
    while True:
        window_entry = PopupEntryW(window_parent, 'Введите новое название параметра')
        closed, new_name = window_entry.open()
        if closed:
            return
        if new_name == '':
            warning(window_parent, 'Название параметра должно содержать хотя бы один символ!')
            continue
        if new_name in parameters:
            warning(window_parent, f'Параметр "{new_name}" уже существует!')
            continue
        break
    # dct.rename_forms_param(index)
    parameters[new_name] = parameters[old_name]
    parameters.pop(old_name)


# Удалить параметр словоформ
def delete_frm_param(window_parent, parameters, dct):
    par_names = [par_name for par_name in parameters.keys()]
    window_choose = PopupChooseW(window_parent, par_names, default_value=par_names[0], btn_text='Удалить',
                                 combo_width=width(par_names, 5, 100))
    closed, selected_par_name = window_choose.open()
    if closed or selected_par_name == '':
        return
    window_dia = PopupDialogueW(window_parent, 'Все словоформы, содержащие этот параметр, будут удалены!\n'
                                               'Хотите продолжить?',
                                set_focus_on_btn='none')
    answer = window_dia.open()
    if answer:
        pos = par_names.index(selected_par_name)
        parameters.pop(selected_par_name)
        dct.delete_forms_param(pos)


# Найти в строке подстроку и выделить её
def find_and_highlight(target_wrd, search_wrd):
    length = len(search_wrd)
    if target_wrd != search_wrd:  # Полное совпадение не учитывается
        pos = deu_to_eng(target_wrd).lower().find(deu_to_eng(search_wrd).lower())
        if pos != -1:
            encoded_wrd = deu_encode(target_wrd)
            end_pos = pos + length
            if search_wrd == '':
                res = f'{encoded_wrd}'
            else:
                res = f'{encoded_wrd[:pos]}[{encoded_wrd[pos:end_pos]}]{encoded_wrd[end_pos:]}'
            return res
    return ''


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
        if self.count_t == 0:
            return ''
        _res = f'> {deu_encode(self.tr[0])}'
        for _i in range(1, self.count_t):
            _res += f'\n> {deu_encode(self.tr[_i])}'
        return _res

    # Записать сноски в строку
    def notes_to_str(self):
        if self.count_n == 0:
            return ''
        _res = f'> {deu_encode(self.notes[0])}'
        for _i in range(1, self.count_n):
            _res += f'\n> {deu_encode(self.notes[_i])}'
        return _res

    # Записать формы в строку
    def frm_to_str(self):
        if self.count_f == 0:
            return ''
        _keys = list(self.forms.keys())
        _res = f'[{tpl(_keys[0])}] {deu_encode(self.forms[_keys[0]])}'
        for _i in range(1, self.count_f):
            _res += f'\n[{tpl(_keys[_i])}] {deu_encode(self.forms[_keys[_i]])}'
        return _res

    # Напечатать перевод
    def tr_print(self, output_widget, end='\n'):
        if self.count_t != 0:
            outp(output_widget, deu_encode(self.tr[0]), end='')
            for _i in range(1, self.count_t):
                outp(output_widget, f', {deu_encode(self.tr[_i])}', end='')
        outp(output_widget, '', end=end)

    # Напечатать сноски
    def notes_print(self, output_widget, _tab=0):
        for _i in range(self.count_n):
            outp(output_widget, ' ' * _tab + f'> {deu_encode(self.notes[_i])}')

    # Напечатать словоформы
    def frm_print(self, output_widget, _tab=0):
        for _key in self.forms.keys():
            outp(output_widget, ' ' * _tab + f'[{tpl(_key)}] {deu_encode(self.forms[_key])}')

    # Напечатать статистику
    def stat_print(self, output_widget, end='\n'):
        if self.last_att == -1:
            outp(output_widget, '[-:  0%]', end=end)
        else:
            score = '{:.0%}'.format(self.score)
            tab = ' ' * (4 - len(score))
            outp(output_widget, f'[{self.last_att}:{tab}{score}]', end=end)

    # Служебный метод для print_briefly и print_briefly_with_forms
    def _print_briefly(self, output_widget):
        if self.fav:
            outp(output_widget, '(*)', end=' ')
        else:
            outp(output_widget, '   ', end=' ')
        self.stat_print(output_widget, end=' ')
        outp(output_widget, f'{deu_encode(self.wrd)}: ', end='')
        self.tr_print(output_widget)

    # Напечатать статью - кратко
    def print_briefly(self, output_widget):
        self._print_briefly(output_widget)
        self.notes_print(output_widget, _tab=13)

    # Напечатать статью - кратко с формами
    def print_briefly_with_forms(self, output_widget):
        self._print_briefly(output_widget)
        self.frm_print(output_widget, _tab=13)
        self.notes_print(output_widget, _tab=13)

    # Напечатать статью - слово со статистикой
    def print_wrd_with_stat(self, output_widget):
        outp(output_widget, deu_encode(self.wrd), end=' ')
        self.stat_print(output_widget)

    # Напечатать статью - перевод со статистикой
    def print_tr_with_stat(self, output_widget):
        self.tr_print(output_widget, end=' ')
        self.stat_print(output_widget)

    # Напечатать статью - перевод с формой и со статистикой
    def print_tr_and_frm_with_stat(self, output_widget, frm_key):
        self.tr_print(output_widget, end=' ')
        outp(output_widget, f'({tpl(frm_key)})', end=' ')
        self.stat_print(output_widget)

    # Напечатать статью - со всей информацией
    def print_all(self, output_widget):
        outp(output_widget, f'       Слово: {deu_encode(self.wrd)}')
        outp(output_widget, '     Перевод: ', end='')
        self.tr_print(output_widget)
        outp(output_widget, ' Формы слова: ', end='')
        if self.count_f == 0:
            outp(output_widget, '-')
        else:
            keys = [key for key in self.forms.keys()]
            outp(output_widget, f'[{tpl(keys[0])}] {deu_encode(self.forms[keys[0]])}')
            for i in range(1, self.count_f):
                outp(output_widget, f'              [{tpl(keys[i])}] {deu_encode(self.forms[keys[i]])}')
        outp(output_widget, '      Сноски: ', end='')
        if self.count_n == 0:
            outp(output_widget, '-')
        else:
            outp(output_widget, f'> {deu_encode(self.notes[0])}')
            for i in range(1, self.count_n):
                outp(output_widget, f'              > {deu_encode(self.notes[i])}')
        outp(output_widget, f'   Избранное: {self.fav}')
        if self.last_att == -1:
            outp(output_widget, '  Статистика: 1) Последних неверных ответов: -')
            outp(output_widget, '              2) Доля верных ответов: 0')
        else:
            outp(output_widget, f'  Статистика: 1) Последних неверных ответов: {self.last_att}')
            outp(output_widget, f'              2) Доля верных ответов: '
                 f'{self.correct_att}/{self.all_att} = ' + '{:.0%}'.format(self.score))

    # Добавить перевод
    def add_tr(self, new_tr, window_parent=None):
        if new_tr not in self.tr:
            self.tr += [new_tr]
            self.count_t += 1
        elif window_parent:
            warning(window_parent, 'У этого слова уже есть такой перевод!')

    # Добавить сноску
    def add_note(self, new_note):
        self.notes += [new_note]
        self.count_n += 1

    # Добавить словоформу
    def add_frm(self, frm_key, new_frm, window_parent=None):
        if new_frm == '':
            warning(window_parent, 'Форма должна содержать хотя бы один символ!')
        elif frm_key not in self.forms.keys():
            self.forms[frm_key] = new_frm
            self.count_f += 1
        elif window_parent:
            warning(window_parent, f'Слово уже имеет форму с такими параметрами {tpl(frm_key)}: {self.forms[frm_key]}!')

    # Удалить словоформу
    def delete_frm_with_choose(self, window_parent):
        keys = [key for key in self.forms.keys()]
        variants = [f'[{tpl(key)}] {deu_encode(self.forms[key])}' for key in keys]

        window_choose = PopupChooseW(window_parent, variants, 'Выберите форму, которую хотите удалить',
                                     default_value=variants[0], combo_width=width(variants, 5, 100))
        closed, answer = window_choose.open()
        if closed or answer == '':
            return
        index = variants.index(answer)
        key = keys[index]
        self.forms.pop(key)
        self.count_f -= 1

    # Изменить словоформу
    def edit_frm_with_choose(self, window_parent):
        keys = [key for key in self.forms.keys()]
        variants = [f'[{tpl(key)}] {deu_encode(self.forms[key])}' for key in keys]

        window_choose = PopupChooseW(window_parent, variants, 'Выберите форму, которую хотите изменить',
                                     default_value=variants[0], combo_width=width(variants, 5, 100))
        closed, answer = window_choose.open()
        if closed or answer == '':
            return
        index = variants.index(answer)
        key = keys[index]

        window_entry = PopupEntryW(window_parent, 'Введите форму слова')
        closed, new_frm = window_entry.open()
        if closed:
            return
        if new_frm == '':
            warning(window_parent, 'Форма должна содержать хотя бы один символ!')
            return
        self.forms[key] = new_frm

    # Объединить статистику при объединении двух статей
    def merge_stat(self, all_att, correct_att, last_att):
        self.all_att += all_att
        self.correct_att += correct_att
        self.score = self.correct_att / self.all_att if (self.all_att != 0) else 0
        self.last_att += last_att

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
    def delete_forms_with_val(self, pos, frm_val):
        to_delete = []
        for key in self.forms.keys():
            if key[pos] == frm_val:
                to_delete += [key]
                self.count_f -= 1
        for key in to_delete:
            self.forms.pop(key)

    # Переименовать данное значение параметра у всех форм слова
    def rename_forms_with_val(self, pos, frm_val, new_frm_val):
        to_rename = []
        for key in self.forms.keys():
            if key[pos] == frm_val:
                to_rename += [key]
        for key in to_rename:
            lst = list(key)
            lst[pos] = new_frm_val
            lst = tuple(lst)
            self.forms[lst] = self.forms[key]
            self.forms.pop(key)

    # Добавить новый параметр ко всем формам слова
    def add_forms_param(self):
        keys = list(self.forms.keys())
        for key in keys:
            new_key = list(key)
            new_key += ['']
            new_key = tuple(new_key)
            self.forms[new_key] = self.forms[key]
            self.forms.pop(key)

    # Удалить данный параметр у всех форм слова
    def delete_forms_param(self, pos):
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

    # Переименовать данный параметр у всех форм слова
    """ def rename_forms_param(self, _pos): """

    # Сохранить статью в файл
    def save(self, file):
        file.write(f'w{self.wrd}\n')
        file.write(f'{self.all_att}#{self.correct_att}#{self.last_att}\n')
        file.write(f'{self.tr[0]}\n')
        for i in range(1, self.count_t):
            file.write(f't{self.tr[i]}\n')
        for note in self.notes:
            file.write(f'd{note}\n')
        for frm_template in self.forms.keys():
            file.write(f'f{decode_tpl(frm_template)}\n{self.forms[frm_template]}\n')
        if self.fav:
            file.write('*\n')


# Перевести слово из статьи в ключ для словаря
def wrd_to_key(wrd, num):
    return str(num // 10) + str(num % 10) + wrd


# Перевести ключ для словаря в слово из статьи
def key_to_wrd(key):
    return key[2:]


# Выбрать окончание слова в зависимости от количественного числительного
def set_postfix(n, wrd_forms):
    if 5 <= (n % 100) <= 20:
        return wrd_forms[2]  # Пример: 5 яблок
    elif n % 10 == 1:
        return wrd_forms[0]  # Пример: 1 яблоко
    elif 1 < n % 10 < 5:
        return wrd_forms[1]  # Пример: 2 яблока
    else:
        return wrd_forms[2]  # Пример: 0 яблок


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

    # Вывести информацию о количестве статей в словаре
    def dct_info(self):
        w = set_postfix(self.count_w, ('слово', 'слова', 'слов'))
        f = set_postfix(self.count_w + self.count_f, ('словоформа', 'словоформы', 'словоформ'))
        t = set_postfix(self.count_t, ('перевод', 'перевода', 'переводов'))
        return f'< {self.count_w} {w} | {self.count_w + self.count_f} {f} | {self.count_t} {t} >'

    # Напечатать словарь
    def print(self, output_widget):
        for entry in self.d.values():
            entry.print_briefly(output_widget)

    # Напечатать словарь (со всеми формами)
    def print_with_forms(self, output_widget):
        for entry in self.d.values():
            entry.print_briefly_with_forms(output_widget)

    # Вывести информацию о количестве избранных статей в словаре
    def dct_info_fav(self, count_w, count_t, count_f):
        w = set_postfix(count_w, ('слово', 'слова', 'слов'))
        f = set_postfix(count_w + count_f, ('словоформа', 'словоформы', 'словоформ'))
        t = set_postfix(count_t, ('перевод', 'перевода', 'переводов'))
        return f'< {count_w}/{self.count_w} {w} | ' \
               f'{count_w + count_f}/{self.count_w + self.count_f} {f} | ' \
               f'{count_t}/{self.count_t} {t} >'

    # Напечатать словарь (только избранные слова)
    def print_fav(self, output_widget):
        count_w = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if entry.fav:
                entry.print_briefly(output_widget)
                count_w += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_w, count_t, count_f

    # Напечатать словарь (только избранные слова, со всеми формами)
    def print_fav_with_forms(self, output_widget):
        count_w = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if entry.fav:
                entry.print_briefly_with_forms(output_widget)
                count_w += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_w, count_t, count_f

    # Напечатать статьи, в которых слова содержат данную строку
    def print_words_with_str(self, output_widget, search_wrd):
        is_found = False
        for key in self.d.keys():
            wrd = key_to_wrd(key)
            res = find_and_highlight(wrd, search_wrd)
            if res != '':
                if is_found:
                    outp(output_widget)  # Вывод новой строки после найденной статьи (кроме первой)
                else:
                    is_found = True
                outp(output_widget, res, end='')
        if not is_found:
            outp(output_widget, 'Частичных совпадений не найдено', end='')

    # Напечатать статьи, в которых переводы содержат данную строку
    def print_translations_with_str(self, output_widget, search_tr):
        is_found = False
        for entry in self.d.values():
            is_first_in_line = True
            for tr in entry.tr:
                res = find_and_highlight(tr, search_tr)
                if res != '':
                    if is_first_in_line:
                        is_first_in_line = False
                        if is_found:
                            outp(output_widget)  # Вывод новой строки после найденной статьи (кроме первой)
                        outp(output_widget, deu_encode(entry.wrd), end=': ')  # Вывод слова
                    else:
                        # Вывод запятой после найденного перевода (кроме первого в статье перевода)
                        outp(output_widget, ', ', end='')
                    is_found = True
                    outp(output_widget, res, end='')  # Вывод перевода
        if not is_found:
            outp(output_widget, 'Частичных совпадений не найдено', end='')

    # Выбрать одну статью из нескольких с одинаковыми словами
    def choose_one_of_similar_entries(self, _window, _wrd):
        if wrd_to_key(_wrd, 1) not in self.d.keys():  # Если статья только одна, то возвращает её ключ
            return wrd_to_key(_wrd, 0)
        _window_note = ChooseNoteW(_window, _wrd)
        _closed, _answer = _window_note.open()
        if _closed:
            return None
        return _answer

    # Добавить перевод к статье
    def add_tr(self, _key, _tr, _window=None):
        self.count_t -= self.d[_key].count_t
        self.d[_key].add_tr(_tr, _window)
        self.count_t += self.d[_key].count_t

    # Добавить сноску к статье
    def add_note(self, key, note):
        self.d[key].add_note(note)

    # Добавить словоформу к статье
    def add_frm(self, _key, _frm_key, _frm, _window=None):
        self.count_f -= self.d[_key].count_f
        self.d[_key].add_frm(_frm_key, _frm, _window)
        self.count_f += self.d[_key].count_f

    # Изменить слово в статье
    def edit_wrd(self, _window, _key, _new_wrd):
        if wrd_to_key(_new_wrd, 0) in self.d.keys():  # Если в словаре уже есть статья с таким словом
            window = PopupDialogueW(_window, 'Статья с таким словом уже есть в словаре\n'
                                             'Что вы хотите сделать?',
                                    'Добавить к существующей статье', 'Создать новую статью',
                                    set_focus_on_btn='none', st_left='std', st_right='std',
                                    val_left='l', val_right='r', val_on_close='c')
            _answer = window.open()
            if _answer == 'l':  # Добавить к существующей статье
                _new_key = self.choose_one_of_similar_entries(_window, _new_wrd)
                if not _new_key:
                    return None

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
            elif _answer == 'r':  # Создать новую статью
                for _i in range(MAX_SAME_WORDS):
                    _new_key = wrd_to_key(_new_wrd, _i)
                    if _new_key not in self.d.keys():
                        self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                                 self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                                 self.d[_key].last_att)
                        self.d.pop(_key)
                        return _new_key
                    _i += 1
                warning(_window, 'Слишком много статей с одинаковым словом!')
            else:
                return None
        else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
            _new_key = wrd_to_key(_new_wrd, 0)
            self.d[_new_key] = Entry(_new_wrd, self.d[_key].tr, self.d[_key].notes, self.d[_key].forms,
                                     self.d[_key].fav, self.d[_key].all_att, self.d[_key].correct_att,
                                     self.d[_key].last_att)
            self.d.pop(_key)
            return _new_key

    # Изменить словоформу в статье
    def edit_frm_with_choose(self, _window, _key):
        self.d[_key].edit_frm_with_choose(_window)

    # Удалить перевод в статье
    def delete_tr_with_choose(self, _window, _key):
        self.count_t -= self.d[_key].count_t
        _window_choose = PopupChooseW(_window, self.d[_key].tr, 'Выберите, какой перевод хотите удалить',
                                      default_value=self.d[_key].tr[0], combo_width=width(self.d[_key].tr, 5, 100))
        _closed, _tr = _window_choose.open()
        if _closed or _tr == '':
            return
        self.d[_key].tr.remove(_tr)
        self.d[_key].count_t -= 1
        self.count_t += self.d[_key].count_t

    # Удалить описание в статье
    def delete_note_with_choose(self, _window, _key):
        _window_choose = PopupChooseW(_window, self.d[_key].notes, 'Выберите, какую сноску хотите удалить',
                                      default_value=self.d[_key].notes[0], combo_width=width(self.d[_key].notes, 5, 100))
        _closed, _note = _window_choose.open()
        if _closed or _note == '':
            return
        self.d[_key].notes.remove(_note)
        self.d[_key].count_n -= 1

    # Удалить словоформу в статье
    def delete_frm_with_choose(self, _window, _key):
        self.count_f -= self.d[_key].count_f
        self.d[_key].delete_frm_with_choose(_window)
        self.count_f += self.d[_key].count_f

    # Добавить статью в словарь (для пользователя)
    def add_entry(self, _window, _wrd, _tr):
        if wrd_to_key(_wrd, 0) in self.d.keys():  # Если в словаре уже есть статья с таким словом
            while True:
                window = PopupDialogueW(_window, 'Статья с таким словом уже есть в словаре\n'
                                                 'Что вы хотите сделать?',
                                        'Добавить к существующей статье', 'Создать новую статью',
                                        set_focus_on_btn='none', st_left='std', st_right='std',
                                        val_left='l', val_right='r', val_on_close='c')
                _answer = window.open()
                if _answer == 'l':  # Добавить к существующей статье
                    _key = self.choose_one_of_similar_entries(_window, _wrd)
                    if not _key:
                        return None
                    self.add_tr(_key, _tr, _window)
                    return _key
                elif _answer == 'r':  # Создать новую статью
                    for _i in range(MAX_SAME_WORDS):
                        _key = wrd_to_key(_wrd, _i)
                        if _key not in self.d.keys():
                            self.d[_key] = Entry(_wrd, [_tr])
                            self.count_w += 1
                            self.count_t += 1
                            return _key
                        _i += 1
                    warning(_window, 'Слишком много статей с одинаковым словом!')
                else:
                    return None
        else:  # Если в словаре ещё нет статьи с таким словом, то она создаётся
            _key = wrd_to_key(_wrd, 0)
            self.d[_key] = Entry(_wrd, [_tr])
            self.count_w += 1
            self.count_t += 1
            return _key

    # Добавить статью в словарь (при чтении файла)
    def load_entry(self, wrd, tr, all_att, correct_att, last_att):
        for i in range(MAX_SAME_WORDS):
            key = wrd_to_key(wrd, i)
            if key not in self.d.keys():
                self.d[key] = Entry(wrd, [tr], _all_att=all_att, _correct_att=correct_att, _last_att=last_att)
                self.count_w += 1
                self.count_t += 1
                return key
            i += 1

    # Удалить статью
    def delete_entry(self, key):
        self.count_w -= 1
        self.count_t -= self.d[key].count_t
        self.count_f -= self.d[key].count_f
        self.d.pop(key)

    # Удалить данное значение параметра у всех форм
    def delete_forms_with_val(self, pos, frm_val):
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_forms_with_val(pos, frm_val)
            self.count_f += entry.count_f

    # Переименовать данное значение параметра у всех форм
    def rename_forms_with_val(self, pos, frm_val, new_frm_val):
        for entry in self.d.values():
            entry.rename_forms_with_val(pos, frm_val, new_frm_val)

    # Добавить данный параметр ко всем словоформам
    def add_forms_param(self):
        for entry in self.d.values():
            entry.add_forms_param()

    # Удалить данный параметр у всех словоформ
    def delete_forms_param(self, pos):
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_forms_param(pos)
            self.count_f += entry.count_f

    # Переименовать данный параметр у всех словоформ
    """def rename_forms_param(self, pos):
        for entry in self.d.values():
            entry.rename_frm_param(pos)"""

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
    def random_hard(self, min_good_score_perc):
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

    # Сохранить словарь в файл
    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.save(file)

    # Прочитать словарь из файла
    def read(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                while True:
                    line = file.readline().strip()
                    if not line:
                        break
                    elif line[0] == 'w':
                        wrd = line[1:]
                        all_att, correct_att, last_att = (int(el) for el in file.readline().strip().split('#'))
                        tr = file.readline().strip()
                        key = self.load_entry(wrd, tr, all_att, correct_att, last_att)
                    elif line[0] == 't':
                        self.add_tr(key, line[1:])
                    elif line[0] == 'd':
                        self.add_note(key, line[1:])
                    elif line[0] == 'f':
                        frm_key = encode_tpl(line[1:])
                        self.add_frm(key, frm_key, file.readline().strip())
                    elif line[0] == '*':
                        self.d[key].fav = True
            return 0
        except FileNotFoundError:
            return 1
        except (ValueError, TypeError):
            return 2
        except Exception:
            return 3


_0_global_dct_savename = 'words'  # Просто чтобы работала функция


# Получить название файла со словарём
def dct_filename(savename=_0_global_dct_savename):
    return f'{savename}.txt'


# Загрузка пользовательских тем
def upload_themes(themes):
    if os.listdir(CUSTOM_THEMES_PATH):
        print('\nЗагрузка тем...')
    for file_name in os.listdir(CUSTOM_THEMES_PATH):
        base_name, ext = os.path.splitext(file_name)
        theme = base_name
        file_path = os.path.join(CUSTOM_THEMES_PATH, file_name)
        try:
            is_correct = True
            with open(file_path, 'r', encoding='utf-8') as theme_file:
                line = theme_file.readline().strip()
                theme_version = int(re.split(' |//', line)[0])  # После // идут комментарии
                if theme_version != REQUIRED_THEME_VERSION:  # Проверка версии темы
                    print(f'Не удалось загрузить тему "{theme}", т. к. она устарела!')
                    continue
                themes += [theme]  # Добавляем название новой темы
                for style_elem in STYLE_ELEMENTS:  # Проходимся по стилизуемым элементам
                    line = theme_file.readline().strip()
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
        except:
            print(f'Не удалось загрузить тему "{theme}" из-за ошибки!')
        else:
            print(f'Тема "{theme}" успешно загружена')


# Проверка наличия обновлений программы
def check_updates(window_parent, show_updates):
    print('\nПроверка наличия обновлений...')
    window_last_version = None
    try:
        data = urllib2.urlopen(URL_LAST_VERSION)
        last_version = str(data.read().decode('utf-8')).strip()
        if PROGRAM_VERSION == last_version:
            print('Установлена последняя доступная версия')
        else:
            print(f'Доступна новая версия: {last_version}')
            if show_updates:
                window_last_version = CheckUpdatesW(window_parent, last_version)
    except:
        print('Ошибка, возможно отсутствует соединение')
    return window_last_version


# Загрузить глобальные настройки (настройки программы)
def upload_global_settings():
    try:  # Открываем файл с названием словаря
        open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
            global_settings_file.write('words\n'
                                '1\n'
                                f'{THEMES[0]}')
    with open(GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        dct_savename = global_settings_file.readline().strip()
        try:
            show_updates = int(global_settings_file.readline().strip())
        except (ValueError, TypeError):
            show_updates = 1
        theme = global_settings_file.readline().strip()
        if theme not in THEMES:
            theme = THEMES[0]
    return dct_savename, show_updates, theme


# Загрузить локальные настройки (настройки словаря)
def upload_local_settings(filename):
    local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    form_parameters = {}
    try:
        open(local_settings_path, 'r', encoding='utf-8')
    except FileNotFoundError:  # Если файл отсутствует, то создаётся файл по умолчанию
        with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
            local_settings_file.write('67\n'
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
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        try:
            min_good_score_perc = int(local_settings_file.readline().strip())
        except (ValueError, TypeError):
            min_good_score_perc = 67
        while True:
            key = local_settings_file.readline().strip()
            if not key:
                break
            value = local_settings_file.readline().strip().split(FORMS_SEPARATOR)
            form_parameters[key] = value
    return min_good_score_perc, form_parameters


# Загрузить словарь (с обработкой исключений)
def upload_dct(window_parent, dct, savename):
    global _0_global_dct_savename

    filename = dct_filename(savename)
    filepath = os.path.join(SAVES_PATH, filename)
    res_code = dct.read(filepath)
    if res_code == 0:  # Если чтение прошло успешно, то выводится соответствующее сообщение
        print(f'\nСловарь "{savename}" успешно открыт')
    elif res_code == 1:  # Если файл отсутствует, то создаётся пустой словарь
        print(f'\nСловарь "{savename}" не найден!')
        open(filepath, 'w', encoding='utf-8')
        dct.read(filepath)
        print('Создан и загружен пустой словарь')
    else:  # Если файл повреждён, то предлагается открыть другой файл
        print(f'\nФайл со словарём "{savename}" повреждён или некорректен!')
        while True:
            window_dia = PopupDialogueW(window_parent, f'Файл со словарём "{savename}" повреждён или некорректен!\n'
                                                       f'Хотите открыть другой словарь?',
                                        'Да', 'Завершить работу', set_focus_on_btn='none', title='Warning')
            answer = window_dia.open()
            if answer:
                window_entry = PopupEntryW(window_parent, 'Введите название словаря\n'
                                                          '(если он ещё не существует, то будет создан пустой словарь)')
                closed, _0_global_dct_savename = window_entry.open()
                if closed:
                    continue
                if _0_global_dct_savename == '':
                    warning(window_parent, 'Название словаря должно содержать хотя бы один символ!')
                    continue
                save_dct_name()
                dct = Dictionary()
                upload_dct(window_parent, dct, _0_global_dct_savename)
            else:
                exit()


# Создать и загрузить пустой словарь
def create_dct(dct, savename):
    filename = dct_filename(savename)
    filepath = os.path.join(SAVES_PATH, filename)
    open(filepath, 'w', encoding='utf-8')
    dct.read(filepath)
    print(f'\nСловарь "{savename}" успешно создан и открыт')
    return upload_local_settings(filename)


# Сохранить глобальные настройки (настройки программы)
def save_global_settings():
    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write(f'{_0_global_dct_savename}\n'
                                   f'{_0_global_show_updates}\n'
                                   f'{th}')


# Сохранить название открытого словаря
def save_dct_name():
    _, tmp_show_updates, tmp_th = upload_global_settings()

    with open(GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write(f'{_0_global_dct_savename}\n'
                                   f'{tmp_show_updates}\n'
                                   f'{tmp_th}')


# Сохранить локальные настройки (настройки словаря)
def save_local_settings(min_good_score_perc, form_parameters, filename):
    local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write(f'{min_good_score_perc}\n')
        for key in form_parameters.keys():
            local_settings_file.write(f'{key}\n')
            local_settings_file.write(form_parameters[key][0])
            for i in range(1, len(form_parameters[key])):
                local_settings_file.write(f'{FORMS_SEPARATOR}{form_parameters[key][i]}')
            local_settings_file.write('\n')


# Сохранить словоформы
def save_forms(form_parameters, filename):
    local_settings_path = os.path.join(LOCAL_SETTINGS_PATH, filename)
    try:
        with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
            tmp_min_good_score_perc = int(local_settings_file.readline().strip())
    # Если файл отсутствует или повреждён, то создаётся файл по умолчанию
    except (FileNotFoundError, ValueError, TypeError):
        tmp_min_good_score_perc = 67

    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write(f'{tmp_min_good_score_perc}\n')
        for key in form_parameters.keys():
            local_settings_file.write(f'{key}\n')
            local_settings_file.write(form_parameters[key][0])
            for i in range(1, len(form_parameters[key])):
                local_settings_file.write(f'{FORMS_SEPARATOR}{form_parameters[key][i]}')
            local_settings_file.write('\n')


# Предложить сохранение настроек, если есть прогресс
def save_settings_if_has_changes(window_parent):
    window_dia = PopupDialogueW(window_parent, 'Хотите сохранить изменения настроек?', 'Да', 'Нет')
    answer = window_dia.open()
    if answer:
        save_global_settings()
        save_local_settings(_0_global_min_good_score_perc, _0_global_form_parameters, dct_filename())
        PopupMsgW(window_parent, 'Настройки успешно сохранены').open()
        print('\nНастройки успешно сохранены')


# Сохранить словарь
def save_dct(dct, filename):
    filepath = os.path.join(SAVES_PATH, filename)
    dct.save(filepath)


# Предложить сохранение словаря, если есть прогресс
def save_dct_if_has_progress(window_parent, dct, filename, has_progress):
    if has_progress:
        window_dia = PopupDialogueW(window_parent, 'Хотите сохранить свой прогресс?', 'Да', 'Нет')
        answer = window_dia.open()
        if answer:
            save_dct(dct, filename)
            PopupMsgW(window_parent, 'Прогресс успешно сохранён').open()
            print('\nПрогресс успешно сохранён')


""" Графический интерфейс """


# Ввод только целых чисел от 0 до max_val
def validate_int_max(value, max_val):
    return value == '' or value.isnumeric() and int(value) <= max_val


# Ввод только целых чисел от 0 до 100
def validate_percent(value):
    return validate_int_max(value, 100)


# Валидация ключа специальной комбинации
def validate_special_combination_key(value):
    return len(value) <= 1 and value not in ('#', '@')


# Валидация значения специальной комбинации
def validate_special_combination_val(value):
    return len(value) <= 1 and value not in ('#', '@')


# При выборе второго метода учёбы нельзя добавить словоформы
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
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False

        self.lbl_msg = tk.Label(self, text=msg, bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.btn_ok = tk.Button(self, text=btn_text, command=self.ok, overrelief='groove',
                                bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(row=0, column=0, padx=6, pady=4)
        self.btn_ok.grid( row=1, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    def open(self):
        self.focus_set()
        self.btn_ok.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed


# Всплывающее окно с сообщением и двумя кнопками
class PopupDialogueW(tk.Toplevel):
    def __init__(self, parent, msg='Вы уверены?', btn_left='Да', btn_right='Отмена',
                 st_left='yes', st_right='no',
                 val_left: object = True,  # Значение, возвращаемое при нажатии на левую кнопку
                 val_right: object = False,  # Значение, возвращаемое при нажатии на правую кнопку
                 val_on_close: object = False,  # Значение, возвращаемое при закрытии окна крестиком
                 set_focus_on_btn='left',  # Какая кнопка срабатывает при нажатии кнопки enter
                 title=PROGRAM_NAME):
        ALLOWED_ST_VALUES = ['std', 'yes', 'no']  # Проверка корректности параметров
        assert st_left  in ALLOWED_ST_VALUES, f'Bad value: st_left\nAllowed values: {ALLOWED_ST_VALUES}'
        assert st_right in ALLOWED_ST_VALUES, f'Bad value: st_right\nAllowed values: {ALLOWED_ST_VALUES}'
        ALLOWED_FOCUS_VALUES = ['left', 'right', 'none']  # Проверка корректности параметров
        assert set_focus_on_btn in ALLOWED_FOCUS_VALUES, f'Bad value: set_focus_on_btn\nAllowed values: {ALLOWED_FOCUS_VALUES}'

        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.set_focus_on_btn = set_focus_on_btn
        self.answer = val_on_close  # Значение, возвращаемое методом self.open
        self.val_left = val_left
        self.val_right = val_right

        if st_left == 'std':
            self.left_bg = ST_BTN[th]
            self.left_activebackground = ST_BTN_SELECT[th]
        elif st_left == 'yes':
            self.left_bg = ST_BTNY[th]
            self.left_activebackground = ST_BTNY_SELECT[th]
        elif st_left == 'no':
            self.left_bg = ST_BTNN[th]
            self.left_activebackground = ST_BTNN_SELECT[th]

        if st_right == 'std':
            self.right_bg = ST_BTN[th]
            self.right_activebackground = ST_BTN_SELECT[th]
        elif st_right == 'yes':
            self.right_bg = ST_BTNY[th]
            self.right_activebackground = ST_BTNY_SELECT[th]
        elif st_right == 'no':
            self.right_bg = ST_BTNN[th]
            self.right_activebackground = ST_BTNN_SELECT[th]

        self.lbl_msg = tk.Label(self, text=msg, bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.btn_left = tk.Button(self, text=btn_left, command=self.left, overrelief='groove',
                                  bg=self.left_bg, fg=ST_FG_TEXT[th],
                                  activebackground=self.left_activebackground, highlightbackground=ST_BORDER[th])
        self.btn_right = tk.Button(self, text=btn_right, command=self.right, overrelief='groove',
                                   bg=self.right_bg, fg=ST_FG_TEXT[th],
                                   activebackground=self.right_activebackground, highlightbackground=ST_BORDER[th])

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

    def open(self):
        self.focus_set()
        if self.set_focus_on_btn == 'left':
            self.btn_left.focus_set()
            self.bind('<Return>', lambda event=None: self.btn_left.invoke())
        elif self.set_focus_on_btn == 'right':
            self.btn_right.focus_set()
            self.bind('<Return>', lambda event=None: self.btn_right.invoke())

        self.grab_set()
        self.wait_window()
        return self.answer


# Всплывающее окно с полем Combobox
class PopupChooseW(tk.Toplevel):
    def __init__(self, parent, values, msg='Выберите один из вариантов', btn_text='Подтвердить',
                 combo_width=20, default_value=None, title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False

        self.var_answer = tk.StringVar(value=default_value)

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_msg = tk.Label(self, text=msg, bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo_vals = ttk.Combobox(self, textvariable=self.var_answer, values=values, width=combo_width,
                                       font='TkFixedFont', state='readonly', style='.TCombobox')
        self.btn_ok = tk.Button(self, text=btn_text, command=self.ok, overrelief='groove',
                                bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(   row=0, padx=6, pady=(4, 1))
        self.combo_vals.grid(row=1, padx=6, pady=1)
        self.btn_ok.grid(    row=2, padx=6, pady=4)

        self.option_add('*TCombobox*Listbox*Font', 'TkFixedFont')  # Моноширинный шрифт в списке combobox

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    def open(self):
        self.focus_set()
        self.btn_ok.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed, self.var_answer.get()


# Всплывающее окно с полем ввода и кнопкой
class PopupEntryW(tk.Toplevel):
    def __init__(self, parent, msg='Введите строку', btn_text='Подтвердить', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False

        self.var_text = tk.StringVar()

        self.lbl_msg = tk.Label(self, text=f'{msg}:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_inp = tk.Entry(self, textvariable=self.var_text, width=30, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                  highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th],
                                  highlightcolor=ST_HIGHLIGHT[th])
        self.btn_ok = tk.Button(self, text=btn_text, command=self.ok, overrelief='groove',
                                bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(  row=0, padx=6, pady=(6, 3))
        self.entry_inp.grid(row=1, padx=6, pady=(0, 6))
        self.btn_ok.grid(   row=2, padx=6, pady=(0, 6))

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    def open(self):
        self.focus_set()
        self.entry_inp.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed, self.var_text.get()


# Окно ввода специальной комбинации
class EntrySpecialCombinationW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False

        self.var_key = tk.StringVar()
        self.var_val = tk.StringVar()

        self.vcmd_key = (self.register(validate_special_combination_key), '%P')
        self.vcmd_val = (self.register(validate_special_combination_val), '%P')

        self.lbl_msg = tk.Label(self, text='Задайте комбинацию', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.frame_main = tk.Frame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_1 = tk.Label(self.frame_main, text='#', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_key = tk.Entry(self.frame_main, textvariable=self.var_key, width=2, justify='right',
                                  validate='key', vcmd=self.vcmd_key, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                  highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th],
                                  highlightcolor=ST_HIGHLIGHT[th])
        self.lbl_2 = tk.Label(self.frame_main, text='->', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_val = tk.Entry(self.frame_main, textvariable=self.var_val, width=2,
                                  validate='key', vcmd=self.vcmd_val, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                  highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th],
                                  highlightcolor=ST_HIGHLIGHT[th])
        # }
        self.btn_ok = tk.Button(self, text='Подтвердить', command=self.ok, overrelief='groove',
                                bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])

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

    def open(self):
        self.focus_set()
        self.entry_key.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed, self.var_key.get(), self.var_val.get()


# Окно уведомления о выходе новой версии
class CheckUpdatesW(tk.Toplevel):
    def __init__(self, parent, last_version):
        super().__init__(parent)
        self.title('New version available')
        self.configure(bg=ST_BG[th])

        self.var_url = tk.StringVar(value=URL_GITHUB)  # Ссылка, для загрузки новой версии

        self.lbl_msg = tk.Label(self, text=f'Доступна новая версия программы\n'
                                           f'{last_version}',
                                bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_url = tk.Entry(self, textvariable=self.var_url, state='readonly', width=40, justify='center',
                                  relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                  highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                                  selectbackground=ST_SELECT[th], readonlybackground=ST_BG_FIELDS[th])
        self.btn_update = tk.Button(self, text='Обновить', command=self.download_and_install, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_close = tk.Button(self, text='Закрыть', command=self.destroy, overrelief='groove',
                                   bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(   row=1, columnspan=2, padx=6, pady=(4, 0))
        self.entry_url.grid( row=2, columnspan=2, padx=6, pady=(0, 4))
        self.btn_update.grid(row=3, column=0,     padx=6, pady=4)
        self.btn_close.grid( row=3, column=1,     padx=6, pady=4)

    # Скачать и установить обновление
    def download_and_install(self):
        try:  # Загрузка
            print('download zip')
            wget.download(URL_DOWNLOAD_ZIP, out=os.path.dirname(__file__))  # Скачиваем архив с обновлением
        except:
            warning(self, 'Не удалось загрузить обновление!')
            self.destroy()
        try:  # Установка
            # Распаковываем архив во временную папку
            print('\nextracting')
            with zipfile.ZipFile(NEW_VERSION_ZIP, 'r') as zip_file:
                zip_file.extractall(os.path.dirname(__file__))
            # Удаляем архив
            print('delete zip')
            os.remove(NEW_VERSION_ZIP)
            # Удаляем файлы текущей версии
            print('delete old files')
            os.remove('ver')
            os.remove('README.txt')
            os.remove('README.md')
            os.remove('main.py')
            # Из временной папки достаём файлы новой версии
            print('set new files')
            os.replace(os.path.join(NEW_VERSION_DIR, 'ver'), 'ver')
            os.replace(os.path.join(NEW_VERSION_DIR, 'README.txt'), 'README.txt')
            os.replace(os.path.join(NEW_VERSION_DIR, 'README.md'), 'README.md')
            os.replace(os.path.join(NEW_VERSION_DIR, 'main.py'), 'main.py')
            # Удаляем временную папку
            print('delete tmp dir')
            os.rmdir(NEW_VERSION_DIR)
        except:
            warning(self, 'Не удалось установить обновление!')
            self.destroy()
        else:
            PopupMsgW(self, 'Обновление успешно установлено\n'
                            'Программа закроется').open()
            exit(777)

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно выбора одной статьи из нескольких с одинаковыми словами
class ChooseNoteW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME}')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False
        self.vals_count = -1  # Количество вариантов для выбора (вычисляется в self.print_variants)
        self.wrd = wrd
        self.answer = None

        self.var_input = tk.StringVar()

        # Ввод номеров ограниченных количеством вариантов
        self.vcmd_max = (self.register(lambda value: validate_int_max(value, self.vals_count)), '%P')

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_input = tk.Label(self.frame_main, text='Выберите одну из статей:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_input = tk.Entry(self.frame_main, textvariable=self.var_input, width=5,
                                    validate='key', vcmd=self.vcmd_max, relief='solid',
                                    bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.btn_choose = tk.Button(self.frame_main, text='Выбор', command=self.choose, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    highlightbackground=ST_BORDER[th], activebackground=ST_BTN_SELECT[th])
        # }
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_words = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set,
                                  bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                  selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])

        self.frame_main.grid(row=0, columnspan=2, padx=6, pady=6)
        # {
        self.lbl_input.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.btn_choose.grid( row=0, column=2, padx=6,      pady=6)
        # }
        self.text_words.grid(row=1, column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid( row=1, column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')

        self.scrollbar.config(command=self.text_words.yview)

        self.print_variants()

    # Вывод вариантов статей
    def print_variants(self):
        self.text_words['state'] = 'normal'
        self.vals_count = MAX_SAME_WORDS - 1
        for _i in range(MAX_SAME_WORDS):
            _key = wrd_to_key(self.wrd, _i)
            if _key not in _0_global_dct.d.keys():
                self.vals_count = _i - 1
                break
            outp(self.text_words, f'\n({_i})')
            _0_global_dct.d[_key].print_all(self.text_words)
        self.text_words['state'] = 'disabled'

    # Выбор одной статьи из нескольких
    def choose(self):
        _input = self.var_input.get()
        if _input != "":
            _index = int(_input)
            self.answer = wrd_to_key(self.wrd, _index)
        self.closed = False
        self.destroy()

    def open(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_choose.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed, self.answer


# Окно для ввода названия словаря
class EnterDctNameW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.name_is_correct = False

        self.var_name = tk.StringVar()

        self.lbl_msg = tk.Label(self, text='Введите название словаря', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_name = tk.Entry(self, textvariable=self.var_name, width=30, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                   highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th],
                                   highlightcolor=ST_HIGHLIGHT[th])
        self.btn_ok = tk.Button(self, text='Подтвердить', command=self.check_and_return, overrelief='groove',
                                bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(   row=0, padx=6, pady=(4, 1))
        self.entry_name.grid(row=1, padx=6, pady=1)
        self.btn_ok.grid(    row=2, padx=6, pady=4)

    # Проверить название и вернуть, если оно корректно
    def check_and_return(self):
        savename = self.var_name.get()
        if savename == '':
            warning(self, 'Название должно содержать хотя бы один символ!')
            return
        if dct_filename(savename) in os.listdir(SAVES_PATH):  # Если уже есть сохранение с таким названием
            warning(self, 'Файл с таким названием уже существует!')
            return
        self.name_is_correct = True
        self.destroy()

    def open(self):
        self.focus_set()
        self.entry_name.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.name_is_correct, self.var_name.get()


# Окно для ввода названия параметра словоформ
class EnterFormParameterNameW(tk.Toplevel):
    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.name_is_correct = False
        self.parameters = parameters

        self.var_name = tk.StringVar()

        self.lbl_msg = tk.Label(self, text='Введите название нового параметра', width=30,
                                bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_name = tk.Entry(self, textvariable=self.var_name, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                   highlightbackground=ST_BORDER[th], selectbackground=ST_SELECT[th],
                                   highlightcolor=ST_HIGHLIGHT[th])
        self.btn_ok = tk.Button(self, text='Подтвердить', command=self.check_and_return, overrelief='groove',
                                bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_msg.grid(   row=0, padx=6, pady=(4, 1))
        self.entry_name.grid(row=1, padx=6, pady=1)
        self.btn_ok.grid(    row=2, padx=6, pady=4)

    # Проверить название и вернуть, если оно корректно
    def check_and_return(self):
        par_name = self.var_name.get()
        if par_name == '':
            warning(self, 'Название параметра должно содержать хотя бы один символ!')
            return
        if par_name in self.parameters:  # Если уже есть параметр с таким названием
            warning(self, f'Параметр "{par_name}" уже существует!')
            return
        self.name_is_correct = True
        self.destroy()

    def open(self):
        self.focus_set()
        self.entry_name.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())

        self.grab_set()
        self.wait_window()
        return self.name_is_correct, self.var_name.get()


# Окно выбора значения параметра словоформы
class ChooseFormParValW(tk.Toplevel):
    def __init__(self, parent, par_name, par_vals, combo_width=20):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False
        self.res = ''
        self.vals = par_vals
        self.var_par = tk.StringVar(value=self.vals[0])

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_choose = tk.Label(self, text=f'Задайте значение параметра "{par_name}"',
                                   bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo = ttk.Combobox(self, textvariable=self.var_par, values=self.vals, width=combo_width,
                                  font='TkFixedFont', state='readonly', style='.TCombobox')
        self.btn_choose = tk.Button(self, text='Задать', command=self.choose, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_none = tk.Button(self, text='Не указывать/неприменимо', command=self.set_none, overrelief='groove',
                                  bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                  activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_new = tk.Button(self, text='Добавить вариант', command=self.new_val, overrelief='groove',
                                 bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_choose.grid(row=0, column=0,     padx=(6, 1), pady=(6, 3))
        self.combo.grid(     row=0, column=1,     padx=(0, 3), pady=(6, 3))
        self.btn_choose.grid(row=0, column=2,     padx=(0, 6), pady=(6, 3))
        self.btn_none.grid(  row=1, columnspan=3, padx=6,      pady=3)
        self.btn_new.grid(   row=2, columnspan=3, padx=6,      pady=(3, 6))

        self.option_add('*TCombobox*Listbox*Font', 'TkFixedFont')  # Моноширинный шрифт в списке combobox

    # Выбрать параметр и задать ему значение
    def choose(self):
        val = self.var_par.get()
        if val == '':
            return
        self.res = val
        self.closed = False
        self.destroy()

    # Сбросить значение параметра
    def set_none(self):
        self.res = ''
        self.closed = False
        self.destroy()

    # Добавить новое значение параметра
    def new_val(self):
        new_value = add_frm_param_val(self, self.vals)
        if not new_value:
            return
        self.vals += [new_value]
        self.combo['values'] = self.vals

    def open(self):
        self.focus_set()
        self.btn_choose.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_choose.invoke())

        self.grab_set()
        self.wait_window()
        return self.closed, self.res


# Окно создания шаблона словоформы
class CreateFormTemplateW(tk.Toplevel):
    def __init__(self, parent, key, combo_width=20):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.closed = True  # Если окно закрыто крестиком, метод self.open возвращает True, иначе - False
        self.parameters = list(_0_global_form_parameters.keys())  # Список параметров словоформ
        self.template = []  # Шаблон словоформы
        for _ in range(len(self.parameters)):
            self.template += ['']
        self.void_template = self.template.copy()  # Пустой шаблон (для сравнения на пустоту)
        self.key = key

        self.var_template = tk.StringVar(value='Текущий шаблон формы: ""')
        self.var_par = tk.StringVar(value=self.parameters[0])

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_template = tk.Label(self, textvariable=self.var_template, bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.lbl_choose = tk.Label(self, text='Выберите параметр', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo = ttk.Combobox(self, textvariable=self.var_par, values=self.parameters, width=combo_width,
                                  font='TkFixedFont', state='readonly', style='.TCombobox')
        self.btn_choose = tk.Button(self, text='Задать значение', command=self.choose, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_done = tk.Button(self, text='Закончить с шаблоном и ввести форму слова', command=self.done,
                                  state='disabled', overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                  activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_template.grid(row=0, columnspan=3, padx=6,      pady=(6, 1))
        self.lbl_choose.grid(  row=1, column=0,     padx=(6, 1), pady=(6, 1))
        self.combo.grid(       row=1, column=1,     padx=(0, 3), pady=1)
        self.btn_choose.grid(  row=1, column=2,     padx=(0, 6), pady=1)
        self.btn_done.grid(    row=2, columnspan=3, padx=(0, 6), pady=6)

        self.option_add('*TCombobox*Listbox*Font', 'TkFixedFont')  # Моноширинный шрифт в списке combobox

    # Выбрать параметр и задать ему значение
    def choose(self):
        par = self.var_par.get()
        if par == '':
            return
        index = self.parameters.index(par)

        window = ChooseFormParValW(self, par, _0_global_form_parameters[par], combo_width=width(_0_global_form_parameters[par], 5, 100))
        closed, val = window.open()
        if closed:
            return
        self.template[index] = val

        self.var_template.set(f'Текущий шаблон формы: "{tpl(self.template)}"')

        if self.template == self.void_template:  # Пока шаблон пустой, нельзя нажать кнопку
            self.btn_done['state'] = 'disabled'
        else:
            self.btn_done['state'] = 'normal'

        # В combobox значением по умолчанию становится первый ещё не заданный параметр
        for i in range(len(self.template)):
            if self.template[i] == '':
                self.var_par.set(self.parameters[i])
                break

    # Закончить с шаблоном
    def done(self):
        if tuple(self.template) in _0_global_dct.d[self.key].forms.keys():
            warning(self, f'У слова "{key_to_wrd(self.key)}" уже есть форма с таким шаблоном!')
            return
        self.closed = False
        self.destroy()

    def open(self):
        self.focus_set()
        self.btn_choose.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_choose.invoke())

        self.grab_set()
        self.wait_window()

        if self.closed:
            return None
        if self.template == self.void_template:
            return None
        if tuple(self.template) in _0_global_dct.d[self.key].forms.keys():
            return None
        return tuple(self.template)


# Окно вывода похожих статей для редактирования
class ParticularMatchesW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Similar')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_wrd = tk.StringVar(value=wrd)

        self.lbl_header = tk.Label(self, text=f'Слово "{wrd}" отсутствует в словаре\n'
                                              f'Возможно вы искали:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.lbl_wrd = tk.Label(self, text=f'Слова, содержащие "{wrd}"', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_wrd = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_wrd = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_wrd.set,
                                bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.lbl_tr = tk.Label(self, text=f'Переводы, содержащие "{wrd}"', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_tr = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_tr = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_tr.set,
                               bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                               selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])

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
        _0_global_dct.print_words_with_str(self.text_wrd, search_wrd)
        self.text_wrd['state'] = 'disabled'

        # Поиск по переводу
        search_tr = self.var_wrd.get()
        self.text_tr['state'] = 'normal'
        self.text_tr.delete(1.0, tk.END)
        _0_global_dct.print_translations_with_str(self.text_tr, search_tr)
        self.text_tr['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()


# Окно настроек словоформ
class FormsSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.var_par = tk.StringVar()

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_form_par  = tk.Label(self, text='Существующие параметры форм:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_form_par = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                     bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.frame_buttons = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.btn_add = tk.Button(self.frame_buttons, text='Добавить параметр форм', command=self.add,
                                 overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_rename = tk.Button(self.frame_buttons, text='Переименовать параметр форм', command=self.rename,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_delete = tk.Button(self.frame_buttons, text='Удалить параметр форм', command=self.delete,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_values = tk.Button(self.frame_buttons, text='Изменить значения параметра форм', command=self.values,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # }

        self.lbl_form_par.grid( row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.text_form_par.grid(row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(    row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_rename.grid(row=1, padx=6, pady=3)
        self.btn_delete.grid(row=2, padx=6, pady=3)
        self.btn_values.grid(row=3, padx=6, pady=(3, 6))
        # }

        self.scrollbar.config(command=self.text_form_par.yview)

        self.refresh()

    # Добавить параметр
    def add(self):
        add_frm_param(self, _0_global_form_parameters, _0_global_dct)
        self.refresh()

    # Удалить параметр
    def delete(self):
        delete_frm_param(self, _0_global_form_parameters, _0_global_dct)
        self.refresh()

    # Переименовать параметр
    def rename(self):
        rename_frm_param(self, _0_global_form_parameters, _0_global_dct)
        self.refresh()

    # Перейти к настройкам значения параметра
    def values(self):
        keys = [_key for _key in _0_global_form_parameters.keys()]
        window = PopupChooseW(self, keys, 'Какой параметр форм вы хотите изменить?',
                              default_value=keys[0], combo_width=width(keys, 5, 100))
        closed, key = window.open()
        if closed or key == '':
            return
        FormsParameterSettingsW(self, key).open()

    # Напечатать существующие параметры форм
    def print_form_par_list(self):
        self.text_form_par['state'] = 'normal'
        self.text_form_par.delete(1.0, tk.END)
        for key in _0_global_form_parameters.keys():
            self.text_form_par.insert(tk.END, f'{key}\n')
        self.text_form_par['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_form_par_list()
        if _0_global_form_parameters:
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

        save_forms(_0_global_form_parameters, dct_filename())


# Окно настроек параметра словоформ
class FormsParameterSettingsW(tk.Toplevel):
    def __init__(self, parent, parameter):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.parameter = parameter  # Название изменяемого параметра
        self.par_vals = _0_global_form_parameters[self.parameter]  # Значения изменяемого параметра

        self.var_par = tk.StringVar()

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_par_val = tk.Label(self, text=f'Существующие значения параметра\n"{parameter}":',
                                    bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_par_val = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                    bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.frame_buttons = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.btn_add = tk.Button(self.frame_buttons, text='Добавить значение параметра', command=self.add,
                                 overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_rename = tk.Button(self.frame_buttons, text='Переименовать значение параметра', command=self.rename,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_delete = tk.Button(self.frame_buttons, text='Удалить значение параметра', command=self.delete,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # }

        self.lbl_par_val.grid(  row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.text_par_val.grid( row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(    row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_rename.grid(row=1, padx=6, pady=3)
        self.btn_delete.grid(row=2, padx=6, pady=3)
        # }

        self.scrollbar.config(command=self.text_par_val.yview)

        self.refresh()

    # Добавить значение параметра
    def add(self):
        new_val = add_frm_param_val(self, self.par_vals)
        if not new_val:
            return
        self.par_vals += [new_val]
        self.refresh()

    # Удалить значение параметра
    def delete(self):
        delete_frm_param_val(self, self.par_vals, _0_global_dct)
        self.refresh()

    # Переименовать значение параметра
    def rename(self):
        index = tuple(_0_global_form_parameters).index(self.parameter)
        rename_frm_param_val(self, self.par_vals, index, _0_global_dct)
        self.refresh()

    # Напечатать существующие параметры форм
    def print_par_val_list(self):
        self.text_par_val['state'] = 'normal'
        self.text_par_val.delete(1.0, tk.END)
        for key in self.par_vals:
            self.text_par_val.insert(tk.END, f'{key}\n')
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


# Окно настроек специальных комбинаций
class SpecialCombinationsSettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(PROGRAM_NAME)
        self.configure(bg=ST_BG[th])

        self.var_par = tk.StringVar()

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])

        self.lbl_form_par  = tk.Label(self, text='Существующие комбинации:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_form_par = tk.Text(self, width=24, height=10, state='disabled', yscrollcommand=self.scrollbar.set,
                                     bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.frame_buttons = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.btn_add = tk.Button(self.frame_buttons, text='Добавить комбинацию', command=self.add,
                                 overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_delete = tk.Button(self.frame_buttons, text='Удалить комбинацию', command=self.delete,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # }

        self.lbl_form_par.grid( row=0,            column=0, padx=(6, 0), pady=(6, 0))
        self.text_form_par.grid(row=1,            column=0, padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(    row=1,            column=1, padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_buttons.grid(row=0, rowspan=2, column=2, padx=6,      pady=6)
        # {
        self.btn_add.grid(   row=0, padx=6, pady=(6, 3))
        self.btn_delete.grid(row=1, padx=6, pady=(3, 6))
        # }

        self.scrollbar.config(command=self.text_form_par.yview)

        self.refresh()

    # Добавить комбинацию
    def add(self):
        window = EntrySpecialCombinationW(self)
        closed, key, val = window.open()
        if closed or key == '' or val == '':
            return
        if key in _0_global_special_combinations.keys():
            warning(self, f'Комбинация #{key} уже существует!')
            return
        _0_global_special_combinations[key] = val
        self.refresh()

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

    # Напечатать существующие комбинации
    def print_combinations(self):
        self.text_form_par['state'] = 'normal'
        self.text_form_par.delete(1.0, tk.END)
        for key in _0_global_special_combinations.keys():
            self.text_form_par.insert(tk.END, special_combination(key))
        self.text_form_par['state'] = 'disabled'

    # Обновить отображаемую информацию
    def refresh(self):
        self.print_combinations()
        if _0_global_special_combinations:
            self.btn_delete['state'] = 'normal'
        else:
            self.btn_delete['state'] = 'disabled'

    def open(self):
        self.grab_set()
        self.wait_window()

        #save_forms(_0_global_form_parameters, dct_filename())


# Окно выбора режима перед изучением слов
class ChooseLearnModeW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Learn')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.res = None

        self.var_order = tk.StringVar(value=VALUES_ORDER[0])  # Метод учёбы
        self.var_forms = tk.BooleanVar(value=True)  # Со всеми ли словоформами
        self.var_words = tk.StringVar(value=VALUES_WORDS[0])  # Способ подбора слов

        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])
        # Стиль для checkbutton
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[th])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[th])])

        self.lbl_header = tk.Label(self, text='Выберите способ учёбы', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.frame_main = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_order = tk.Label(self.frame_main, text='Метод:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo_order = ttk.Combobox(self.frame_main, textvariable=self.var_order, values=VALUES_ORDER,
                                        validate='focusin', width=30, state='readonly', style='.TCombobox')
        self.lbl_forms = tk.Label(self.frame_main, text='Все словоформы:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, style='.TCheckbutton')
        self.lbl_words = tk.Label(self.frame_main, text='Подбор слов:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo_words = ttk.Combobox(self.frame_main, textvariable=self.var_words, values=VALUES_WORDS,
                                        width=30, state='readonly', style='.TCombobox')
        # }
        self.btn_start = tk.Button(self, text='Учить', command=self.start, overrelief='groove',
                                   bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   highlightbackground=ST_BORDER[th], activebackground=ST_BTN_SELECT[th])

        self.lbl_header.grid(row=0, column=0, padx=6, pady=(6, 3))
        self.frame_main.grid(row=1, column=0, padx=6, pady=(0, 3))
        # {
        self.lbl_order.grid(  row=1, column=0, padx=(3, 1), pady=(3, 3), sticky='E')
        self.combo_order.grid(row=1, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        self.lbl_forms.grid(  row=2, column=0, padx=(3, 1), pady=(0, 3), sticky='E')
        self.check_forms.grid(row=2, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        self.lbl_words.grid(  row=3, column=0, padx=(3, 1), pady=(0, 3), sticky='E')
        self.combo_words.grid(row=3, column=1, padx=(0, 3), pady=(0, 3), sticky='W')
        # }
        self.btn_start.grid(row=2, column=0, padx=6, pady=(0, 6))

        # При выборе второго метода учёбы нельзя добавить словоформы
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
        self.focus_set()
        self.btn_start.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_start.invoke())

        self.grab_set()
        self.wait_window()
        return self.res


# Окно печати словаря
class PrintW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Print')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_fav   = tk.BooleanVar(value=False)
        self.var_forms = tk.BooleanVar(value=True)
        self.var_info  = tk.StringVar()

        # Стиль для checkbutton
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[th])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[th])])

        self.lbl_dct_name = tk.Label(self, text=f'Открыт словарь "{_0_global_dct_savename}"', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.frame_main = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_fav     = tk.Label(self.frame_main, text='Только избранные:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.lbl_forms   = tk.Label(self.frame_main, text='Все формы:',        bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.check_fav   = ttk.Checkbutton(self.frame_main, variable=self.var_fav,   style='.TCheckbutton')
        self.check_forms = ttk.Checkbutton(self.frame_main, variable=self.var_forms, style='.TCheckbutton')
        self.btn_print   = tk.Button(self.frame_main, text='Печать', command=self.print, overrelief='groove',
                                     bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                     highlightbackground=ST_BORDER[th], activebackground=ST_BTN_SELECT[th])
        # }
        self.scrollbar_x = tk.Scrollbar(self, bg=ST_BG[th])
        self.scrollbar_y = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_dct    = tk.Text(self, width=70, height=30, state='disabled', wrap='none',
                                   xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set,
                                   bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.lbl_info  = tk.Label(self, textvariable=self.var_info, bg=ST_BG[th], fg=ST_FG_TEXT[th])

        self.lbl_dct_name.grid(row=0, columnspan=2, padx=6, pady=(6, 4))
        self.frame_main.grid(  row=1, columnspan=2, padx=6, pady=(0, 4))
        # {
        self.lbl_fav.grid(    row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.check_fav.grid(  row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.lbl_forms.grid(  row=0, column=2, padx=(6, 1), pady=6, sticky='E')
        self.check_forms.grid(row=0, column=3, padx=(0, 6), pady=6, sticky='W')
        self.btn_print.grid(  row=0, column=4, padx=6,      pady=6)
        # }
        self.text_dct.grid(   row=2, column=0,     padx=(6, 0), pady=0,      sticky='NSEW')
        self.scrollbar_x.grid(row=3, column=0,     padx=(6, 0), pady=0,      sticky='NWE')
        self.scrollbar_y.grid(row=2, column=1,     padx=(0, 6), pady=0,      sticky='NSW')
        self.lbl_info.grid(   row=4, columnspan=2, padx=6,      pady=(0, 6))

        self.scrollbar_x.config(command=self.text_dct.xview, orient='horizontal')
        self.scrollbar_y.config(command=self.text_dct.yview, orient='vertical')

        self.print()

    # Напечатать словарь
    def print(self):
        self.text_dct['state'] = 'normal'
        self.text_dct.delete(1.0, tk.END)
        if self.var_fav.get():
            if self.var_forms.get():
                w, t, f = _0_global_dct.print_fav_with_forms(self.text_dct)
            else:
                w, t, f = _0_global_dct.print_fav(self.text_dct)
            self.var_info.set(_0_global_dct.dct_info_fav(w, t, f))
        else:
            if self.var_forms.get():
                _0_global_dct.print_with_forms(self.text_dct)
            else:
                _0_global_dct.print(self.text_dct)
            self.var_info.set(_0_global_dct.dct_info())
        self.text_dct.yview_moveto(1.0)
        self.text_dct['state'] = 'disabled'

    def open(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_print.invoke())

        self.grab_set()
        self.wait_window()


# Окно поиска статей
class SearchW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Search')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_wrd = tk.StringVar(value=wrd)

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_input = tk.Label(self.frame_main, text='Введите запрос:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_input = tk.Entry(self.frame_main, textvariable=self.var_wrd, width=60, relief='solid',
                                    bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.btn_search = tk.Button(self.frame_main, text='Поиск', command=self.search, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    activebackground=ST_BTN_SELECT[th])
        # }
        self.lbl_wrd = tk.Label(self, text='Поиск по слову', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_wrd = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_wrd = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_wrd.set,
                                bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.lbl_tr = tk.Label(self, text='Поиск по переводу', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_tr = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_tr = tk.Text(self, width=50, height=30, state='disabled', yscrollcommand=self.scrollbar_tr.set,
                               bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                               selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])

        self.frame_main.grid(row=0, columnspan=4, padx=6, pady=(6, 4))
        # {
        self.lbl_input.grid(  row=0, column=0, padx=(6, 1), pady=6, sticky='E')
        self.entry_input.grid(row=0, column=1, padx=(0, 6), pady=6, sticky='W')
        self.btn_search.grid( row=0, column=2, padx=6,      pady=6)
        # }
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

        outp(self.text_wrd, 'Полное совпадение:')
        if wrd_to_key(search_wrd, 0) not in _0_global_dct.d.keys():
            outp(self.text_wrd, f'Слово "{deu_encode(search_wrd)}" отсутствует в словаре', end='')
        else:
            for i in range(MAX_SAME_WORDS):
                key = wrd_to_key(search_wrd, i)
                if key not in _0_global_dct.d.keys():
                    break
                outp(self.text_wrd)
                _0_global_dct.d[key].print_all(self.text_wrd)

        outp(self.text_wrd, '\n\nЧастичное совпадение:')
        _0_global_dct.print_words_with_str(self.text_wrd, search_wrd)

        self.text_wrd['state'] = 'disabled'

        # Поиск по переводу
        search_tr = self.var_wrd.get()

        self.text_tr['state'] = 'normal'
        self.text_tr.delete(1.0, tk.END)

        outp(self.text_tr, 'Полное совпадение:')
        is_found = False
        for entry in _0_global_dct.d.values():
            if search_tr in entry.tr:
                is_found = True
                outp(self.text_tr)
                entry.print_all(self.text_tr)
        if not is_found:
            outp(self.text_tr, f'Слово с переводом "{deu_encode(search_tr)}" отсутствует в словаре', end='')

        outp(self.text_tr, '\n\nЧастичное совпадение:')
        _0_global_dct.print_translations_with_str(self.text_tr, search_tr)

        self.text_tr['state'] = 'disabled'

    def open(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_search.invoke())

        self.grab_set()
        self.wait_window()


# Окно изменения статьи
class EditW(tk.Toplevel):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Edit an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.key = key
        self.line_width = 35
        self.max_height = 5

        self.var_wrd = tk.StringVar(value=_0_global_dct.d[key].wrd)
        self.var_fav = tk.BooleanVar(value=_0_global_dct.d[key].fav)

        # Стиль для checkbutton
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[th])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[th])])

        self.frame_main = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_wrd = tk.Label(self.frame_main, text='Слово:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_wrd = tk.Scrollbar(self.frame_main, bg=ST_BG[th])
        self.txt_wrd = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_wrd.set,
                               relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                               highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                               selectbackground=ST_SELECT[th])
        self.scrollbar_wrd.config(command=self.txt_wrd.yview)
        self.btn_wrd_edt = tk.Button(self.frame_main, text='изм.', command=self.wrd_edt, overrelief='groove',
                                     bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     activebackground=ST_BTN_SELECT[th])
        #
        self.lbl_tr = tk.Label(self.frame_main, text='Перевод:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_tr = tk.Scrollbar(self.frame_main, bg=ST_BG[th])
        self.txt_tr = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_tr.set,
                              relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                              highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                              selectbackground=ST_SELECT[th])
        self.scrollbar_tr.config(command=self.txt_tr.yview)
        self.frame_btns_tr = tk.Frame(self.frame_main, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                      relief=ST_RELIEF[th])
        # { {
        self.btn_tr_add = tk.Button(self.frame_btns_tr, text='+', command=self.tr_add, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    activebackground=ST_BTN_SELECT[th])
        self.btn_tr_del = tk.Button(self.frame_btns_tr, text='-', command=self.tr_del, overrelief='groove',
                                    bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    activebackground=ST_BTN_SELECT[th])
        # } }
        self.lbl_notes = tk.Label(self.frame_main, text='Сноски:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_notes = tk.Scrollbar(self.frame_main, bg=ST_BG[th])
        self.txt_notes = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_notes.set,
                                 relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                 highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                                 selectbackground=ST_SELECT[th])
        self.scrollbar_notes.config(command=self.txt_notes.yview)
        self.frame_btns_notes = tk.Frame(self.frame_main, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                         relief=ST_RELIEF[th])
        # { {
        self.btn_notes_add = tk.Button(self.frame_btns_notes, text='+', command=self.notes_add, overrelief='groove',
                                       bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                       activebackground=ST_BTN_SELECT[th])
        self.btn_notes_del = tk.Button(self.frame_btns_notes, text='-', command=self.notes_del, overrelief='groove',
                                       bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                       activebackground=ST_BTN_SELECT[th])
        # } }
        self.lbl_frm = tk.Label(self.frame_main, text='Формы слова:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar_frm = tk.Scrollbar(self.frame_main, bg=ST_BG[th])
        self.txt_frm = tk.Text(self.frame_main, width=self.line_width, yscrollcommand=self.scrollbar_frm.set,
                               relief='solid', bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                               highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                               selectbackground=ST_SELECT[th])
        self.scrollbar_frm.config(command=self.txt_frm.yview)
        self.frame_btns_frm = tk.Frame(self.frame_main, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                       relief=ST_RELIEF[th])
        # { {
        self.btn_frm_add = tk.Button(self.frame_btns_frm, text='+', command=self.frm_add, overrelief='groove',
                                     bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     activebackground=ST_BTN_SELECT[th])
        self.btn_frm_del = tk.Button(self.frame_btns_frm, text='-', command=self.frm_del, overrelief='groove',
                                     bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     activebackground=ST_BTN_SELECT[th])
        self.btn_frm_edt = tk.Button(self.frame_btns_frm, text='изм.', command=self.frm_edt, overrelief='groove',
                                     bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                     activebackground=ST_BTN_SELECT[th])
        # } }
        self.lbl_fav = tk.Label(self.frame_main, text='Избранное:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.check_fav = ttk.Checkbutton(self.frame_main, variable=self.var_fav, command=self.set_fav,
                                         style='.TCheckbutton')
        # }
        self.btn_back = tk.Button(self, text='Закончить', command=self.back, overrelief='groove', bg=ST_BTN[th],
                                  fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                  activebackground=ST_BTN_SELECT[th])
        self.btn_delete = tk.Button(self, text='Удалить статью', command=self.delete, overrelief='groove',
                                    bg=ST_BTNN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    activebackground=ST_BTNN_SELECT[th])
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

        self.refresh()

    # Обновить поля
    def refresh(self):
        height_w = max(min(height(_0_global_dct.d[self.key].wrd,            self.line_width), self.max_height), 1)
        height_t =     min(height(_0_global_dct.d[self.key].tr_to_str(),    self.line_width), self.max_height)
        height_n =     min(height(_0_global_dct.d[self.key].notes_to_str(), self.line_width), self.max_height)
        height_f =     min(height(_0_global_dct.d[self.key].frm_to_str(),   self.line_width), self.max_height)

        self.txt_wrd  ['height'] = height_w
        self.txt_tr   ['height'] = height_t
        self.txt_notes['height'] = height_n
        self.txt_frm  ['height'] = height_f

        self.txt_wrd['state'] = 'normal'
        self.txt_wrd.delete(1.0, tk.END)
        self.txt_wrd.insert(tk.END, deu_encode(_0_global_dct.d[self.key].wrd))
        self.txt_wrd['state'] = 'disabled'

        self.txt_tr['state'] = 'normal'
        self.txt_tr.delete(1.0, tk.END)
        self.txt_tr.insert(tk.END, _0_global_dct.d[self.key].tr_to_str())
        self.txt_tr['state'] = 'disabled'

        self.txt_notes['state'] = 'normal'
        self.txt_notes.delete(1.0, tk.END)
        self.txt_notes.insert(tk.END, _0_global_dct.d[self.key].notes_to_str())
        self.txt_notes['state'] = 'disabled'

        self.txt_frm['state'] = 'normal'
        self.txt_frm.delete(1.0, tk.END)
        self.txt_frm.insert(tk.END, _0_global_dct.d[self.key].frm_to_str())
        self.txt_frm['state'] = 'disabled'

        self.btn_tr_del.grid(     row=0, column=1, padx=(1, 0), pady=0)
        self.btn_notes_del.grid(  row=0, column=1, padx=(1, 0), pady=0)
        self.btn_frm_del.grid(    row=0, column=1, padx=(1, 1), pady=0)
        self.btn_frm_edt.grid(    row=0, column=2, padx=(1, 0), pady=0)
        self.scrollbar_wrd.grid(  row=0, column=2, padx=(0, 1), pady=(6, 3), sticky='NSW')
        self.scrollbar_tr.grid(   row=1, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_notes.grid(row=2, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')
        self.scrollbar_frm.grid(  row=3, column=2, padx=(0, 1), pady=(0, 3), sticky='NSW')

        if _0_global_dct.d[self.key].count_t < 2:
            self.btn_tr_del.grid_remove()
        if _0_global_dct.d[self.key].count_n < 1:
            self.btn_notes_del.grid_remove()
        if _0_global_dct.d[self.key].count_f < 1:
            self.btn_frm_del.grid_remove()
            self.btn_frm_edt.grid_remove()

        if height_w < self.max_height:
            self.scrollbar_wrd.grid_remove()
        if height_t < self.max_height:
            self.scrollbar_tr.grid_remove()
        if height_n < self.max_height:
            self.scrollbar_notes.grid_remove()
        if height_f < self.max_height:
            self.scrollbar_frm.grid_remove()

    # Изменить слово
    def wrd_edt(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новое слово')
        closed, new_wrd = window.open()
        if closed:
            return
        if new_wrd == '':
            warning(self, 'Слово должно содержать хотя бы один символ!')
            return
        if new_wrd == key_to_wrd(self.key):
            warning(self, 'Это то же самое слово!')
            return

        self.key = _0_global_dct.edit_wrd(self, self.key, new_wrd)
        if not self.key:
            return

        _0_global_has_progress = True
        self.refresh()

    # Добавить перевод
    def tr_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите новый перевод')
        closed, tr = window.open()
        if closed:
            return
        if tr == '':
            warning(self, 'Перевод должен содержать хотя бы один символ!')
            return
        if tr in _0_global_dct.d[self.key].tr:
            warning(self, f'У слова "{_0_global_dct.d[self.key].wrd}" уже есть такой перевод!')
            return

        _0_global_dct.add_tr(self.key, tr, self)

        _0_global_has_progress = True
        self.refresh()

    # Удалить перевод
    def tr_del(self):
        global _0_global_has_progress

        _0_global_dct.delete_tr_with_choose(self, self.key)

        _0_global_has_progress = True
        self.refresh()

    # Добавить сноску
    def notes_add(self):
        global _0_global_has_progress

        window = PopupEntryW(self, 'Введите сноску')
        closed, note = window.open()
        if closed:
            return
        if note == '':
            warning(self, 'Сноска должна содержать хотя бы один символ!')
            return
        if note in _0_global_dct.d[self.key].notes:
            warning(self, f'У слова "{_0_global_dct.d[self.key].wrd}" уже есть такая сноска!')
            return

        _0_global_dct.add_note(self.key, note)

        _0_global_has_progress = True
        self.refresh()

    # Удалить сноску
    def notes_del(self):
        global _0_global_has_progress

        _0_global_dct.delete_note_with_choose(self, self.key)

        _0_global_has_progress = True
        self.refresh()

    # Добавить словоформу
    def frm_add(self):
        global _0_global_has_progress

        if not _0_global_form_parameters:
            warning(self, 'Отсутствуют параметры форм!\n'
                          'Чтобы их добавить, перейдите в\n'
                          'Настройки/Настройки словаря/Настройки словоформ')
            return

        window_template = CreateFormTemplateW(self, self.key, combo_width=width(_0_global_form_parameters, 5, 100))  # Создание шаблона словоформы
        frm_key = window_template.open()
        if not frm_key:
            return
        window_form = PopupEntryW(self, 'Введите форму слова')  # Ввод словоформы
        closed, frm = window_form.open()
        if closed:
            return

        _0_global_dct.add_frm(self.key, frm_key, frm, self)

        _0_global_has_progress = True
        self.refresh()

    # Удалить словоформу
    def frm_del(self):
        global _0_global_has_progress

        _0_global_dct.delete_frm_with_choose(self, self.key)

        _0_global_has_progress = True
        self.refresh()

    # Изменить словоформу
    def frm_edt(self):
        global _0_global_has_progress

        _0_global_dct.edit_frm_with_choose(self, self.key)

        _0_global_has_progress = True
        self.refresh()

    # Добавить в избранное/убрать из избранного
    def set_fav(self):
        _0_global_dct.d[self.key].fav = self.var_fav.get()

    # Закрыть настройки
    def back(self):
        self.destroy()

    # Удалить статью
    def delete(self):
        global _0_global_has_progress

        window = PopupDialogueW(self, 'Вы уверены, что хотите удалить эту статью?', set_focus_on_btn='none')
        answer = window.open()
        if answer:
            _0_global_dct.delete_entry(self.key)
            _0_global_has_progress = True
            self.destroy()

    def open(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_back.invoke())

        self.grab_set()
        self.wait_window()


# Окно добавления статьи
class AddW(tk.Toplevel):
    def __init__(self, parent, wrd):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Add an entry')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.key = None

        self.var_wrd = tk.StringVar(value=wrd)
        self.var_tr  = tk.StringVar()
        self.var_fav = tk.BooleanVar(value=False)

        # Стиль для checkbutton
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[th])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[th])])

        self.lbl_wrd   = tk.Label( self, text='Введите слово:',   bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_wrd = tk.Entry( self, textvariable=self.var_wrd, width=60, relief='solid', bg=ST_BG_FIELDS[th],
                                   fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.lbl_tr    = tk.Label( self, text='Введите перевод:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_tr  = tk.Entry( self, textvariable=self.var_tr,  width=60, relief='solid', bg=ST_BG_FIELDS[th],
                                   fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.lbl_fav   = tk.Label( self, text='Избранное:',       bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.check_fav = ttk.Checkbutton(self, variable=self.var_fav, style='.TCheckbutton')
        self.btn_add   = tk.Button(self, text='Добавить', command=self.add, overrelief='groove', bg=ST_BTN[th],
                                   fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   activebackground=ST_BTN_SELECT[th])

        self.lbl_wrd.grid(  row=0, column=0,     padx=(6, 1), pady=(6, 3), sticky='E')
        self.entry_wrd.grid(row=0, column=1,     padx=(0, 6), pady=(6, 3), sticky='W')
        self.lbl_tr.grid(   row=1, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.entry_tr.grid( row=1, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.lbl_fav.grid(  row=2, column=0,     padx=(6, 1), pady=(0, 3), sticky='E')
        self.check_fav.grid(row=2, column=1,     padx=(0, 6), pady=(0, 3), sticky='W')
        self.btn_add.grid(  row=3, columnspan=2, padx=6,      pady=(0, 6))

    # Добавление статьи
    def add(self):
        global _0_global_has_progress

        if self.var_wrd.get() == '':
            warning(self, 'Слово должно содержать хотя бы один символ!')
            return
        if self.var_tr.get() == '':
            warning(self, 'Перевод должен содержать хотя бы один символ!')
            return

        self.key = _0_global_dct.add_entry(self, self.var_wrd.get(), self.var_tr.get())
        if not self.key:
            return
        _0_global_dct.d[self.key].fav = self.var_fav.get()

        _0_global_has_progress = True
        self.destroy()

    def open(self):
        self.focus_set()
        self.entry_wrd.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_add.invoke())

        self.grab_set()
        self.wait_window()
        return self.key


# Окно изучения слов
class LearnW(tk.Toplevel):
    def __init__(self, parent, conf):
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
        self.conf = conf  # Режим изучения слов

        self.var_input = tk.StringVar()

        self.lbl_global_rating = tk.Label(self,
                                          text=f'Ваш общий рейтинг по словарю: {round(_0_global_dct.count_rating() * 100)}%',
                                          bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar = tk.Scrollbar(self, bg=ST_BG[th])
        self.text_dct = tk.Text(self, width=70, height=30, state='disabled', yscrollcommand=self.scrollbar.set,
                                bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                selectbackground=ST_SELECT[th], relief=ST_RELIEF[th])
        self.scrollbar.config(command=self.text_dct.yview)
        self.frame_main = tk.Frame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # { {
        self.btn_input = tk.Button(self.frame_main, text='Ввод', command=self.input, overrelief='groove',
                                   bg=ST_BTN[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   activebackground=ST_BTN_SELECT[th])
        self.entry_input = tk.Entry(self.frame_main, textvariable=self.var_input, width=50, relief='solid',
                                    bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                    highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.btn_notes = tk.Button(self.frame_main, text='Посмотреть сноски', command=self.show_notes,
                                   overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   highlightbackground=ST_BORDER[th], activebackground=ST_BTN_SELECT[th])
        # } }
        self.btn_stop = tk.Button(self, text='Закончить', command=self.stop, overrelief='groove',
                                  bg=ST_BTNN[th], fg=ST_FG_TEXT[th],
                                  highlightbackground=ST_BORDER[th], activebackground=ST_BTNN_SELECT[th])

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

    # Начать учить слова
    def start(self):
        global _0_global_has_progress

        order = self.conf[0]
        forms = self.conf[1]
        words = self.conf[2]

        if order == VALUES_ORDER[0]:
            if forms:
                if words == VALUES_WORDS[0]:
                    _0_global_has_progress = self.choose_f(_0_global_dct) or _0_global_has_progress
                elif words == VALUES_WORDS[1]:
                    _0_global_has_progress = self.choose_f_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_f_fav(_0_global_dct) or _0_global_has_progress
            else:
                if words == VALUES_WORDS[0]:
                    _0_global_has_progress = self.choose(_0_global_dct) or _0_global_has_progress
                elif words == VALUES_WORDS[1]:
                    _0_global_has_progress = self.choose_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_fav(_0_global_dct) or _0_global_has_progress
        else:
            if words == VALUES_WORDS[0]:
                _0_global_has_progress = self.choose_t(_0_global_dct) or _0_global_has_progress
            elif words == VALUES_WORDS[1]:
                _0_global_has_progress = self.choose_t_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
            else:
                _0_global_has_progress = self.choose_t_fav(_0_global_dct) or _0_global_has_progress

    # Ввод ответа и переход к следующему слову
    def input(self):
        global _0_global_has_progress

        order = self.conf[0]
        forms = self.conf[1]
        words = self.conf[2]

        answer = deu_encode(self.entry_input.get())  # Вывод пользовательского ответа
        if answer != '':
            self.outp(answer)

        if order == VALUES_ORDER[1]:
            self.check_tr()
        elif forms and self.rnd_f != -1:
            self.check_form()
        else:
            self.check_wrd()

        if order == VALUES_ORDER[0]:
            if forms:
                if words == VALUES_WORDS[0]:
                    _0_global_has_progress = self.choose_f(_0_global_dct) or _0_global_has_progress
                elif words == VALUES_WORDS[1]:
                    _0_global_has_progress = self.choose_f_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_f_fav(_0_global_dct) or _0_global_has_progress
            else:
                if words == VALUES_WORDS[0]:
                    _0_global_has_progress = self.choose(_0_global_dct) or _0_global_has_progress
                elif words == VALUES_WORDS[1]:
                    _0_global_has_progress = self.choose_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
                else:
                    _0_global_has_progress = self.choose_fav(_0_global_dct) or _0_global_has_progress
        else:
            if words == VALUES_WORDS[0]:
                _0_global_has_progress = self.choose_t(_0_global_dct) or _0_global_has_progress
            elif words == VALUES_WORDS[1]:
                _0_global_has_progress = self.choose_t_hard(_0_global_dct, _0_global_min_good_score_perc) or _0_global_has_progress
            else:
                _0_global_has_progress = self.choose_t_fav(_0_global_dct) or _0_global_has_progress

        self.btn_notes['state'] = 'normal'
        self.entry_input.delete(0, tk.END)
        self.lbl_global_rating['text'] = f'Ваш общий рейтинг по словарю: {round(_0_global_dct.count_rating() * 100)}%'

    # Просмотр сносок
    def show_notes(self):
        self.text_dct['state'] = 'normal'
        entry = _0_global_dct.d[self.current_key]
        entry.notes_print(self.text_dct)
        self.text_dct.yview_moveto(1.0)
        self.text_dct['state'] = 'disabled'
        self.btn_notes['state'] = 'disabled'

    # Завершение учёбы
    def stop(self):
        self.frame_main.grid_remove()
        self.btn_stop.grid_remove()

        if len(self.used_words) == _0_global_dct.count_w:
            PopupMsgW(self, f'Ваш результат: {self.count_correct}/{self.count_all}')
        self.outp(f'\nВаш результат: {self.count_correct}/{self.count_all}')

    # Проверка введённого слова
    def check_wrd(self):
        entry = _0_global_dct.d[self.current_key]
        if self.entry_input.get() == entry.wrd:
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
            self.used_words.add(self.current_key)
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{deu_encode(entry.wrd)}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Неверно.\n'
                                              'Хотите добавить слово в избранное?',
                                        'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Проверка введённой словоформы
    def check_form(self):
        entry = _0_global_dct.d[self.current_key]
        if self.entry_input.get() == entry.forms[self.current_form]:
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
            self.used_words.add((self.current_key, self.current_form))
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{deu_encode(entry.forms[self.current_form])}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Неверно.\n'
                                              'Хотите добавить слово в избранное?',
                                        'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Проверка введённого перевода
    def check_tr(self):
        entry = _0_global_dct.d[self.current_key]
        if self.entry_input.get() in entry.tr:
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
            self.used_words.add(self.current_key)
        else:
            entry.incorrect()
            self.outp(f'Неверно. Правильный ответ: "{deu_encode(entry.tr)}"\n')
            if not entry.fav:
                window = PopupDialogueW(self, 'Неверно.\n'
                                              'Хотите добавить слово в избранное?',
                                        'Да', 'Нет')
                answer = window.open()
                if answer:
                    entry.fav = True
            self.count_all += 1

    # Выбор слова - все
    def choose(self, _dct):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(_dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

        return True

    # Выбор слова - избранные
    def choose_fav(self, _dct):
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
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

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
        _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

        return True

    # Выбор словоформы - все
    def choose_f(self, _dct):
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
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
                    self.text_dct['state'] = 'disabled'
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form)
                    self.text_dct['state'] = 'disabled'
                    break

        return True

    # Выбор словоформы - избранные
    def choose_f_fav(self, _dct):
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
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
                    self.text_dct['state'] = 'disabled'
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form)
                    self.text_dct['state'] = 'disabled'
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
                    _dct.d[self.current_key].print_tr_with_stat(self.text_dct)
                    self.text_dct['state'] = 'disabled'
                    break
            else:
                self.current_form = list(_dct.d[self.current_key].forms.keys())[self.rnd_f]
                if (self.current_key, self.current_form) not in self.used_words:
                    self.text_dct['state'] = 'normal'
                    _dct.d[self.current_key].print_tr_and_frm_with_stat(self.text_dct, self.current_form)
                    self.text_dct['state'] = 'disabled'
                    break

        return True

    # Выбор перевода - все
    def choose_t(self, _dct):
        if len(self.used_words) == _dct.count_w:
            self.stop()
            return
        while True:
            self.current_key = random.choice(list(_dct.d.keys()))
            if self.current_key not in self.used_words:
                break

        self.text_dct['state'] = 'normal'
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

        return True

    # Выбор перевода - избранные
    def choose_t_fav(self, _dct):
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
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

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
        _dct.d[self.current_key].print_wrd_with_stat(self.text_dct)
        self.text_dct['state'] = 'disabled'

        return True

    def open(self):
        self.focus_set()
        self.entry_input.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_input.invoke())

        self.grab_set()
        self.wait_window()


# Окно настроек
class SettingsW(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f'{PROGRAM_NAME} - Settings')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_mgsp = tk.StringVar(value=str(_0_global_min_good_score_perc))
        self.var_show_updates = tk.BooleanVar(value=bool(_0_global_show_updates))
        self.var_theme = tk.StringVar(value=th)

        # Только целые числа от 0 до 100
        self.vcmd = (self.register(validate_percent), '%P')

        # Стиль для checkbutton
        self.st_check = ttk.Style()
        self.st_check.configure(style='.TCheckbutton', background=ST_BG[th])
        self.st_check.map('.TCheckbutton', background=[('active', ST_SELECT[th])])
        # Стиль для combobox
        self.st_combo = ttk.Style()
        self.st_combo.configure(style='.TCombobox', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                                highlightbackground=ST_BORDER[th])
        self.st_combo.map('.TCombobox', background=[('readonly', ST_BG[th])],
                          foreground=[('readonly', ST_FG_TEXT[th])], highlightbackground=[('readonly', ST_BORDER[th])])
        # Стиль для notebook
        self.st_note = ttk.Style()
        self.st_note.configure(style='.TNotebook', background=ST_BG[th], foreground=ST_FG_TEXT[th],
                               highlightbackground=ST_BORDER[th])

        self.tabs = ttk.Notebook(self, style='.TNotebook')
        self.tab_local = tk.Frame(self.tabs, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                  relief=ST_RELIEF[th])
        self.lbl_dct_name = tk.Label(self, text=f'Открыт словарь "{_0_global_dct_savename}"',
                                     bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.tabs.add(self.tab_local, text='Настройки словаря')
        # {
        self.frame_mgsp = tk.LabelFrame(self.tab_local, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                        relief=ST_RELIEF[th])
        # { {
        self.lbl_mgsp = tk.Label(self.frame_mgsp, text='Минимальный приемлемый процент угадываний слова:',
                                 bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.entry_mgsp = tk.Entry(self.frame_mgsp, textvariable=self.var_mgsp, width=5, relief='solid',
                                   validate='key', vcmd=self.vcmd, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                   highlightbackground=ST_BORDER[th], highlightcolor=ST_HIGHLIGHT[th],
                                   selectbackground=ST_SELECT[th])
        self.lbl_mgsp_2 = tk.Label(self.frame_mgsp, text='Статьи, у которых процент угадывания ниже этого значения,'
                                                         'будут считаться более сложными',
                                   bg=ST_BG[th], fg=ST_FG_TEXT[th])
        # } }
        self.btn_forms = tk.Button(self.tab_local, text='Настройки словоформ', command=self.forms,
                                   overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.lbl_forms_warn = tk.Label(self.tab_local, text='Настройки словоформ сохраняются сразу!',
                                       bg=ST_BG[th], fg=ST_FG_WARN[th])
        #
        self.btn_special_combinations = tk.Button(self.tab_local, text='Специальные комбинации', state='disabled',
                                                  command=self.special_combinations, overrelief='groove',
                                                  bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                                  activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.lbl_special_combinations_warn = tk.Label(self.tab_local, text='Специальные комбинации сохраняются сразу!',
                                                      bg=ST_BG[th], fg=ST_FG_WARN[th])
        # }
        self.tab_global = tk.Frame(self.tabs, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                   relief=ST_RELIEF[th])
        self.tabs.add(self.tab_global, text='Настройки программы')
        # {
        self.frame_show_updates = tk.LabelFrame(self.tab_global, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                                relief=ST_RELIEF[th])
        # { {
        self.lbl_show_updates = tk.Label(self.frame_show_updates, text='Сообщать о выходе новых версий:',
                                         bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.check_show_updates = ttk.Checkbutton(self.frame_show_updates, variable=self.var_show_updates,
                                                  style='.TCheckbutton')
        # } }
        self.frame_dcts = tk.LabelFrame(self.tab_global, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                        relief=ST_RELIEF[th])
        # { {
        self.lbl_dcts = tk.Label(self.frame_dcts, text='Существующие словари:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.scrollbar = tk.Scrollbar(self.frame_dcts, bg=ST_BG[th])
        self.text_dcts = tk.Text(self.frame_dcts, width=20, height=10, state='disabled', relief=ST_RELIEF[th],
                                 yscrollcommand=self.scrollbar.set, bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                 selectbackground=ST_SELECT[th], highlightbackground=ST_BORDER[th])
        self.frame_dct_buttons = tk.LabelFrame(self.frame_dcts, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                               relief=ST_RELIEF[th])
        # { { {
        self.btn_dct_open = tk.Button(self.frame_dct_buttons, text='Открыть словарь', command=self.dct_open,
                                      overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                      activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_dct_create = tk.Button(self.frame_dct_buttons, text='Создать словарь', command=self.dct_create,
                                        overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                        activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_dct_rename = tk.Button(self.frame_dct_buttons, text='Переименовать словарь', command=self.dct_rename,
                                        overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                        activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_dct_delete = tk.Button(self.frame_dct_buttons, text='Удалить словарь', command=self.dct_delete,
                                        overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                        activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # } } }
        self.lbl_dcts_warn = tk.Label(self.frame_dcts, text='Настройки словарей сохраняются сразу!',
                                      bg=ST_BG[th], fg=ST_FG_WARN[th])
        # } }
        self.frame_themes = tk.LabelFrame(self.tab_global, bg=ST_BG[th], highlightbackground=ST_BORDER[th],
                                          relief=ST_RELIEF[th])
        # { {
        self.lbl_themes = tk.Label(self.frame_themes, text='Тема:', bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.combo_themes = ttk.Combobox(self.frame_themes, textvariable=self.var_theme, values=THEMES,
                                         state='readonly', style='.TCombobox')
        # } }
        # }
        self.btn_save = tk.Button(self, text='Сохранить изменения', command=self.save, overrelief='groove',
                                  bg=ST_BTNY[th], fg=ST_FG_TEXT[th], activebackground=ST_BTNY_SELECT[th],
                                  highlightbackground=ST_BORDER[th])

        self.lbl_dct_name.grid(row=0, padx=6, pady=(6, 0))
        self.tabs.grid(        row=1, padx=6, pady=(0, 6))
        #
        self.frame_mgsp.grid(row=0, padx=6, pady=6, sticky='E')
        # {
        self.lbl_mgsp.grid(  row=0, column=0,     padx=(6, 1), pady=6,      sticky='E')
        self.entry_mgsp.grid(row=0, column=1,     padx=(0, 1), pady=6,      sticky='W')
        self.lbl_mgsp_2.grid(row=1, columnspan=2, padx=6,      pady=(0, 6))
        # }
        self.btn_forms.grid(     row=1, padx=6, pady=(0, 3))
        self.lbl_forms_warn.grid(row=2, padx=6, pady=(0, 6))
        #
        self.btn_special_combinations.grid(     row=3, padx=6, pady=(0, 3))
        self.lbl_special_combinations_warn.grid(row=4, padx=6, pady=(0, 6))
        #
        self.frame_show_updates.grid(row=0, padx=6, pady=6)
        # {
        self.lbl_show_updates.grid(  row=0, column=0, padx=(6, 0), pady=6)
        self.check_show_updates.grid(row=0, column=1, padx=(0, 6), pady=6)
        # }
        self.frame_dcts.grid(row=1, padx=6, pady=6)
        # {
        self.lbl_dcts.grid(         row=0,            column=0, columnspan=2, padx=6,      pady=(6, 0))
        self.text_dcts.grid(        row=1, rowspan=2, column=0,               padx=(6, 0), pady=(0, 6), sticky='NSEW')
        self.scrollbar.grid(        row=1, rowspan=2, column=1,               padx=(0, 6), pady=(0, 6), sticky='NSW')
        self.frame_dct_buttons.grid(row=1,            column=2,               padx=6,      pady=6)
        # { {
        self.btn_dct_open.grid(  row=0, column=0, padx=6, pady=6)
        self.btn_dct_create.grid(row=0, column=1, padx=6, pady=6)
        self.btn_dct_rename.grid(row=1, column=0, padx=6, pady=6)
        self.btn_dct_delete.grid(row=1, column=1, padx=6, pady=6)
        # } }
        self.lbl_dcts_warn.grid(row=2, column=2, padx=6, pady=6, sticky='N')
        # }
        self.frame_themes.grid(row=2, padx=6, pady=6)
        # {
        self.lbl_themes.grid(  row=0, column=0, padx=(6, 1), pady=6)
        self.combo_themes.grid(row=0, column=1, padx=(0, 6), pady=6)
        # }
        self.btn_save.grid(row=3, padx=6, pady=6)

        self.scrollbar.config(command=self.text_dcts.yview)

        self.print_dct_list()

    # Изменить значение MGSP
    def set_mgsp(self):
        global _0_global_min_good_score_perc

        val = self.var_mgsp.get()
        if val == '':
            _0_global_min_good_score_perc = 0
        else:
            _0_global_min_good_score_perc = int(val)

    # Настройки словоформ
    def forms(self):
        FormsSettingsW(self).open()

    # Настройки специальных комбинаций
    def special_combinations(self):
        SpecialCombinationsSettingsW(self).open()

    # Разрешить/запретить сообщать о новых версиях
    def set_show_updates(self):
        global _0_global_show_updates

        _0_global_show_updates = int(self.var_show_updates.get())  # 0 или 1

    # Открыть словарь
    def dct_open(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc, _0_global_form_parameters

        saves_count = 0
        saves_list = []
        for file_name in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(file_name)
            if ext == '.txt':
                if base_name != _0_global_dct_savename:
                    saves_list += [base_name]
                    saves_count += 1
        if saves_count == 0:  # Если нет сохранённых словарей
            warning(self, 'Нет других сохранённых словарей!')
            return

        window = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите открыть',
                              default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, savename = window.open()
        if closed or savename == '':
            return

        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(), _0_global_has_progress)

        _0_global_dct = Dictionary()
        upload_dct(self, _0_global_dct, savename)
        _0_global_min_good_score_perc, _0_global_form_parameters = upload_local_settings(dct_filename(savename))
        _0_global_dct_savename = savename
        save_dct_name()

        self.lbl_dct_name['text'] = f'Открыт словарь "{savename}"'

        self.refresh()

    # Создать словарь
    def dct_create(self):
        global _0_global_dct, _0_global_dct_savename, _0_global_min_good_score_perc, _0_global_form_parameters

        window = EnterDctNameW(self)
        filename_is_correct, savename = window.open()
        if not filename_is_correct:
            return

        if self.has_local_changes():
            save_settings_if_has_changes(self)
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(), _0_global_has_progress)

        _0_global_dct_savename = savename
        save_dct_name()
        _0_global_dct = Dictionary()
        _0_global_min_good_score_perc, _0_global_form_parameters = create_dct(_0_global_dct, savename)

        self.lbl_dct_name['text'] = f'Открыт словарь "{savename}"'

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
        if closed or old_savename == '':
            return

        window_rename = EnterDctNameW(self)
        new_name_is_correct, new_savename = window_rename.open()
        if not new_name_is_correct:
            return

        old_filename = dct_filename(old_savename)
        new_filename = dct_filename(new_savename)
        os.rename(os.path.join(SAVES_PATH, old_filename), os.path.join(SAVES_PATH, new_filename))
        os.rename(os.path.join(LOCAL_SETTINGS_PATH, old_filename), os.path.join(LOCAL_SETTINGS_PATH, new_filename))
        if _0_global_dct_savename == old_savename:
            _0_global_dct_savename = new_savename
            save_dct_name()
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
                if base_name != _0_global_dct_savename:
                    saves_list += [base_name]
                    saves_count += 1
        if saves_count == 0:  # Если нет сохранённых словарей
            warning(self, 'Нет других сохранённых словарей!')
            return

        window_choose = PopupChooseW(self, saves_list, 'Выберите словарь, который хотите удалить',
                                     default_value=saves_list[0], combo_width=width(saves_list, 5, 100))
        closed, savename = window_choose.open()
        if closed or savename == '':
            return
        if savename == _0_global_dct_savename:
            warning(self, 'Нельзя удалить словарь, который сейчас открыт!')
            return

        window_confirm = PopupDialogueW(self, f'Словарь "{savename}" будет безвозвратно удалён!\n'
                                              f'Хотите продолжить?',
                                        set_focus_on_btn='none')
        answer = window_confirm.open()
        if not answer:
            return

        filename = dct_filename(savename)
        os.remove(os.path.join(SAVES_PATH, filename))
        os.remove(os.path.join(LOCAL_SETTINGS_PATH, filename))
        PopupMsgW(self, f'Словарь "{savename}" успешно удалён').open()

        self.print_dct_list()

    # Установить выбранную тему
    def set_theme(self):
        global th

        th = self.var_theme.get()
        self.destroy()

    # Были ли изменения
    def has_local_changes(self):
        return int(self.var_mgsp.get()) != _0_global_min_good_score_perc

    # Вывод существующих словарей
    def print_dct_list(self):
        self.text_dcts['state'] = 'normal'
        self.text_dcts.delete(1.0, tk.END)
        for filename in os.listdir(SAVES_PATH):
            base_name, ext = os.path.splitext(filename)
            if ext == '.txt':
                if base_name == _0_global_dct_savename:
                    self.text_dcts.insert(tk.END, f'"{base_name}" (ОТКРЫТ)\n')
                else:
                    self.text_dcts.insert(tk.END, f'"{base_name}"\n')
        self.text_dcts['state'] = 'disabled'

    # Обновить значения настроек
    def refresh(self):
        self.var_mgsp.set(str(_0_global_min_good_score_perc))
        self.print_dct_list()

    # Сохранить настройки
    def save(self):
        self.set_mgsp()
        self.set_show_updates()
        self.set_theme()
        save_local_settings(_0_global_min_good_score_perc, _0_global_form_parameters, dct_filename())
        save_global_settings()

    def open(self):
        self.focus_set()
        self.entry_mgsp.focus_set()

        self.grab_set()
        self.wait_window()


# Главное окно
class MainW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.configure(bg=ST_BG[th])

        self.var_word = tk.StringVar(value='')

        self.frame_head = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_header1 = tk.Label(self.frame_head, text='Anenokil development presents', font='StdFont 15',
                                    bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.lbl_header2 = tk.Label(self.frame_head, text=PROGRAM_NAME, font='Times 21',
                                    bg=ST_BG[th], fg=ST_FG_LOGO[th])
        # }
        self.btn_print = tk.Button(self, text='Напечатать словарь', font='StdFont 12', command=self.print,
                                   overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_learn = tk.Button(self, text='Учить слова', font='StdFont 12', command=self.learn,
                                   overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                   activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.frame_word = tk.LabelFrame(self, bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.entry_word = tk.Entry(self.frame_word, textvariable=self.var_word, width=30, relief='solid',
                                   bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                   highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.btn_search = tk.Button(self.frame_word, text='Найти статью', font='StdFont 12', command=self.search,
                                    overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_edit = tk.Button(self.frame_word, text='Изменить статью', font='StdFont 12', command=self.edit,
                                  overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                  activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_add = tk.Button(self.frame_word, text='Добавить статью', font='StdFont 12', command=self.add,
                                 overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # }
        self.btn_settings = tk.Button(self, text='Настройки', font='StdFont 12', command=self.settings,
                                      overrelief='groove', bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                      activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_save = tk.Button(self, text='Сохранить прогресс', font='StdFont 12', command=self.save,
                                  overrelief='groove', bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                  activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_close = tk.Button(self, text='Закрыть программу', font='StdFont 12', command=self.close,
                                   overrelief='groove', bg=ST_BTNN[th], fg=ST_FG_TEXT[th],
                                   activebackground=ST_BTNN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_footer = tk.Label(self, text=f'{PROGRAM_VERSION} - {PROGRAM_DATE}', font='StdFont 8',
                                   bg=ST_BG[th], fg=ST_FG_FOOTER[th])

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

        self.focus_set()
        self.entry_word.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_search.invoke())

    # Печать словаря
    def print(self):
        PrintW(self).open()

    # Поиск статьи
    def search(self):
        wrd = self.var_word.get()
        SearchW(self, wrd).open()

    # Изменение статьи
    def edit(self):
        wrd = self.var_word.get()
        if wrd_to_key(wrd, 0) not in _0_global_dct.d.keys():  # Если такого слова нет, то выводятся частично совпадающие слова
            ParticularMatchesW(self, wrd).open()
            return
        key = _0_global_dct.choose_one_of_similar_entries(self, wrd)
        if not key:
            return None
        EditW(self, key).open()

    # Добавление статьи
    def add(self):
        wrd = self.var_word.get()
        key = AddW(self, wrd).open()
        if not key:
            return
        EditW(self, key).open()

    # Учить слова
    def learn(self):
        res = ChooseLearnModeW(self).open()
        if not res:
            return
        LearnW(self, res).open()

    # Открыть настройки
    def settings(self):
        SettingsW(self).open()

        # Обновление тем
        self.configure(bg=ST_BG[th])
        self.frame_head.configure(bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.lbl_header1.configure(bg=ST_BG[th], fg=ST_FG_TEXT[th])
        self.lbl_header2.configure(bg=ST_BG[th], fg=ST_FG_LOGO[th])
        # }
        self.btn_print.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_learn.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.frame_word.configure(bg=ST_BG[th], highlightbackground=ST_BORDER[th], relief=ST_RELIEF[th])
        # {
        self.entry_word.configure(bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th], highlightbackground=ST_BORDER[th],
                                  highlightcolor=ST_HIGHLIGHT[th], selectbackground=ST_SELECT[th])
        self.btn_search.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                  activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_edit.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_add.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                               activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        # }
        self.btn_settings.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                    activebackground=ST_BTN_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_save.configure(bg=ST_BTNY[th], fg=ST_FG_TEXT[th],
                                activebackground=ST_BTNY_SELECT[th], highlightbackground=ST_BORDER[th])
        self.btn_close.configure(bg=ST_BTNN[th], fg=ST_FG_TEXT[th],
                                 activebackground=ST_BTNN_SELECT[th], highlightbackground=ST_BORDER[th])

        self.lbl_footer.configure(bg=ST_BG[th], fg=ST_FG_FOOTER[th])

        try:
            _0_global_window_last_version.configure(bg=ST_BG[th])
            _0_global_window_last_version.lbl_msg.configure(bg=ST_BG[th], fg=ST_FG_TEXT[th])
            _0_global_window_last_version.entry_url.configure(bg=ST_BG_FIELDS[th], fg=ST_FG_TEXT[th],
                                                              highlightbackground=ST_BORDER[th],
                                                              highlightcolor=ST_HIGHLIGHT[th],
                                                              selectbackground=ST_SELECT[th],
                                                              readonlybackground=ST_BG_FIELDS[th])
            _0_global_window_last_version.btn_update.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                                               activebackground=ST_BTN_SELECT[th],
                                                               highlightbackground=ST_BORDER[th])
            _0_global_window_last_version.btn_close.configure(bg=ST_BTN[th], fg=ST_FG_TEXT[th],
                                                              activebackground=ST_BTN_SELECT[th],
                                                              highlightbackground=ST_BORDER[th])
        except:  # Если окно обновления не открыто
            pass

    # Сохранить прогресс
    def save(self):
        global _0_global_has_progress

        save_dct(_0_global_dct, dct_filename())
        PopupMsgW(self, 'Прогресс успешно сохранён').open()
        print('\nПрогресс успешно сохранён')

        _0_global_has_progress = False

    # Закрытие программы
    def close(self):
        save_dct_if_has_progress(self, _0_global_dct, dct_filename(), _0_global_has_progress)
        self.quit()


# Вывод информации о программе
print( '======================================================================================\n')
print( '                            Anenokil development  presents')
print(f'                               {PROGRAM_NAME} {PROGRAM_VERSION}')
print(f'                               {PROGRAM_DATE}\n')
print( '======================================================================================')

_0_global_special_combinations = {'a': 'ä',
                                  'A': 'Ä',
                                  'o': 'ö',
                                  'O': 'Ö',
                                  'u': 'ü',
                                  'U': 'Ü',
                                  's': 'ß',
                                  'S': 'ẞ'}

_0_global_dct = Dictionary()
_0_global_has_progress = False

upload_themes(THEMES)  # Загружаем темы
_0_global_dct_savename, _0_global_show_updates, th = upload_global_settings()  # Загружаем глобальные настройки
root = MainW()  # Создаём графический интерфейс
upload_dct(root, _0_global_dct, _0_global_dct_savename)  # Загружаем словарь
_0_global_min_good_score_perc, _0_global_form_parameters = upload_local_settings(dct_filename())  # Загружаем локальные настройки
_0_global_window_last_version = check_updates(root, _0_global_show_updates)  # Проверяем наличие обновлений
root.mainloop()

# попробовать tk.ScrolledText
# добавить изменение статьи по переводу
# принимать несколько ответов при угадывании слова
# если ответ немного отличается от правильного, то ...
# открывать программу после обновления
# при наведении на Text (PrintW) выводить подсказку
# при смене табов, менять размеры
# проблема с сохранением изменений в настройках словоформ
# перенести все стили '.TWidget' в MainW

# доделать специальные комбинации
# при закрытии окна возвращать фокус предыдущему окну
