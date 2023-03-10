import typing


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
    # self.correct_att_in_a_row - количество последних удачных попыток подряд
    # self.latest_answer_session - сессия, на которой было в последний раз отвечено это слово
    def __init__(self,
                 wrd: str,
                 tr: str | list[str],
                 notes: str | list[str] | None = None,
                 forms: dict[tuple[str, ...], str] | None = None,
                 fav=False, all_att=0, correct_att=0, correct_att_in_a_row=0, latest_answer_session=(0, 0, 0)):
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
        self.score = 0 if (all_att == 0) else correct_att / all_att
        self.correct_att_in_a_row = correct_att_in_a_row
        self.latest_answer_session = latest_answer_session

    # Добавить в избранное
    def add_to_fav(self):
        self.fav = True

    # Убрать из избранного
    def remove_from_fav(self):
        self.fav = False

    # Изменить статус избранного
    def change_fav(self):
        self.fav = not self.fav

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
    def merge_stat(self, all_att: int, correct_att: int, correct_att_in_a_row: int):
        self.all_att += all_att
        self.correct_att += correct_att
        self.score = 0 if (self.all_att == 0) else self.correct_att / self.all_att
        self.correct_att_in_a_row += correct_att_in_a_row

    # Обновить статистику, если совершена верная попытка
    def correct(self, session_number: tuple[int, int, int]):
        self.all_att += 1
        self.correct_att += 1
        self.score = self.correct_att / self.all_att
        if self.correct_att_in_a_row < 0:
            self.correct_att_in_a_row = 1
        else:
            self.correct_att_in_a_row += 1
        self.latest_answer_session = session_number

    # Обновить статистику, если совершена неверная попытка
    def incorrect(self):
        self.all_att += 1
        self.score = self.correct_att / self.all_att
        if self.correct_att_in_a_row > 0:
            self.correct_att_in_a_row = -1
        else:
            self.correct_att_in_a_row -= 1

    # Сохранить статью в файл
    def save(self, file: typing.TextIO, frm_template_separator: str):
        file.write(f'w{self.wrd}\n')
        file.write(f'{self.all_att}:{self.correct_att}:{self.correct_att_in_a_row}\n')
        file.write(f'{self.latest_answer_session[0]}:{self.latest_answer_session[1]}:{self.latest_answer_session[2]}\n')
        file.write(f'{self.tr[0]}\n')
        for i in range(1, self.count_t):
            file.write(f't{self.tr[i]}\n')
        for note in self.notes:
            file.write(f'n{note}\n')
        for frm_template in self.forms.keys():
            file.write(f'f{frm_key_to_str_for_save(frm_template, frm_template_separator)}\n'
                       f'{self.forms[frm_template]}\n')
        if self.fav:
            file.write('*\n')

    # Распечатать статью в файл
    def print_out(self, file: typing.TextIO):
        if self.fav:
            file.write('| (Избр.)\n')
        file.write(f'| {self.wrd} - {self.tr[0]}')
        for i in range(1, self.count_t):
            file.write(f', {self.tr[i]}')
        file.write('\n')
        for frm_template in self.forms.keys():
            file.write(f'|  [{frm_key_to_str_for_print(frm_template)}] {self.forms[frm_template]}\n')
        for note in self.notes:
            file.write(f'| > {note}\n')


# Словарь
class Dictionary(object):
    # self.d - сам словарь
    # self.count_w - количество статей (слов) в словаре
    # self.count_t - количество переводов в словаре
    # self.count_f - количество неначальных словоформ в словаре
    def __init__(self):
        self.d: dict[tuple[str, int], Entry] = {}
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0

    # Подсчитать количество избранных статей
    def count_fav_info(self):
        count_w = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if entry.fav:
                count_w += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_w, count_t, count_f

    # Объединить две статьи с одинаковым словом в одну
    def merge_entries(self, main_entry_key: tuple[str, int], additional_entry_key: tuple[str, int]):
        self.count_t -= self.d[additional_entry_key].count_t
        self.count_t -= self.d[main_entry_key].count_t
        self.count_f -= self.d[additional_entry_key].count_f
        self.count_f -= self.d[main_entry_key].count_f

        for tr in self.d[additional_entry_key].tr:
            self.d[main_entry_key].add_tr(tr)
        for note in self.d[additional_entry_key].notes:
            self.d[main_entry_key].add_note(note)
        for frm_key in self.d[additional_entry_key].forms.keys():
            frm = self.d[additional_entry_key].forms[frm_key]
            self.d[main_entry_key].add_frm(frm_key, frm)
        if self.d[additional_entry_key].fav:
            self.d[main_entry_key].fav = True
        self.d[main_entry_key].merge_stat(self.d[additional_entry_key].all_att,
                                          self.d[additional_entry_key].correct_att,
                                          self.d[additional_entry_key].correct_att_in_a_row)

        self.count_w -= 1
        self.count_t += self.d[main_entry_key].count_t
        self.count_f += self.d[main_entry_key].count_f

        self.d.pop(additional_entry_key)

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

    # Добавить статью в словарь
    def add_entry(self, wrd: str, tr: str | list[str],
                  notes: str | list[str] = None, forms: dict[tuple[str, ...], str] = None,
                  fav: bool = False, all_att: int = 0, correct_att: int = 0, correct_att_in_a_row: int = 0,
                  latest_answer_session: tuple[int, int, int] = (0, 0, 0)):
        i = 0
        while True:
            key = wrd_to_key(wrd, i)
            if key not in self.d.keys():
                self.d[key] = Entry(wrd, tr, notes, forms, fav, all_att, correct_att, correct_att_in_a_row,
                                    latest_answer_session)
                self.count_w += 1
                self.count_t += self.d[key].count_t
                self.count_f += self.d[key].count_f
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
        sum_num = sum(entry.correct_att for entry in self.d.values())
        sum_den = sum(entry.all_att for entry in self.d.values())
        if sum_den == 0:
            return 0
        return sum_num / sum_den

    # Прочитать словарь из файла
    def read(self, filepath: str, frm_template_separator: str):
        with open(filepath, 'r', encoding='utf-8') as file:
            file.readline()  # Первая строка - версия сохранения словаря
            while True:
                line = file.readline().strip()
                if not line:
                    break
                elif line[0] == 'w':
                    wrd = line[1:]
                    all_att, correct_att, correct_att_in_a_row = (int(el) for el in file.readline().strip().split(':'))
                    latest_answer_session = tuple((int(el) for el in file.readline().strip().split(':')))
                    tr = file.readline().strip()
                    key = self.add_entry(wrd, tr, all_att=all_att, correct_att=correct_att,
                                         correct_att_in_a_row=correct_att_in_a_row,
                                         latest_answer_session=latest_answer_session)
                elif line[0] == 't':
                    self.add_tr(key, line[1:])
                elif line[0] == 'n':
                    self.add_note(key, line[1:])
                elif line[0] == 'f':
                    frm_key = read_frm_key(line[1:], frm_template_separator)
                    self.add_frm(key, frm_key, file.readline().strip())
                elif line[0] == '*':
                    self.d[key].add_to_fav()

    # Сохранить словарь в файл
    def save(self, filepath: str, frm_template_separator: str, saves_version: int | str):
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'v{saves_version}\n')
            for entry in self.d.values():
                entry.save(file, frm_template_separator)

    # Распечатать словарь в файл
    def print_out(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.print_out(file)
                file.write('\n')


# Преобразовать шаблон словоформы в читаемый вид (для вывода на экран)
def frm_key_to_str_for_print(input_tuple: tuple | list):
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
def frm_key_to_str_for_save(input_tuple: tuple | list, separator: str):
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Преобразовать строку в кортеж (для чтения значений категории из файла локальных настроек)
def read_frm_key(line: str, separator: str):
    return tuple(line.split(separator))


# Перевести слово в ключ для словаря
def wrd_to_key(wrd: str, num: int):
    return wrd, num


# Перевести ключ для словаря в слово
def key_to_wrd(key: tuple[str, int]):
    return key[0]
