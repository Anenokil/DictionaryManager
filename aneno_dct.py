import typing


# Словарная статья
class Entry(object):
    # self.wrd - слово (начальная форма)
    # self.tr - переводы
    # self.notes - сноски
    # self.forms - словоформы (кроме начальной)
    # self.count_t - количество переводов
    # self.count_n - количество сносок
    # self.count_f - количество словоформ (кроме начальной)
    # self.fav - избранное или нет
    # self.groups - группы, к которым относится эта статья
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
                 fav=False, groups: set[str] | None = None,
                 all_att=0, correct_att=0, correct_att_in_a_row=0, latest_answer_session=(0, 0, 0)):
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
        self.groups = groups if groups else set()
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

    # Добавить в группу
    def add_to_group(self, group: str):
        self.groups.add(group)

    # Убрать из группы
    def remove_from_group(self, group: str):
        self.groups.remove(group)

    # Изменить статус группы
    def change_group_status(self, group: str):
        if group in self.groups:
            self.remove_from_group(group)
        else:
            self.add_to_group(group)

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
            if key[pos] == '':
                to_edit += [key]
            else:
                to_delete += [key]
                self.count_f -= 1
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
    def save(self, file: typing.TextIO):
        file.write(f'w{self.wrd}\n')
        file.write(f'{self.all_att}:{self.correct_att}:{self.correct_att_in_a_row}\n')
        file.write(f'{self.latest_answer_session[0]}:{self.latest_answer_session[1]}:{self.latest_answer_session[2]}\n')
        file.write(f'{self.tr[0]}\n')
        for i in range(1, self.count_t):
            file.write(f't{self.tr[i]}\n')
        for note in self.notes:
            file.write(f'n{note}\n')
        for frm_template in self.forms.keys():
            file.write(f'f{frm_key_to_str_for_save(frm_template)}\n'
                       f'{self.forms[frm_template]}\n')
        if self.fav:
            file.write('*\n')
        for group in self.groups:
            file.write(f'g{group}\n')

    # Распечатать статью в файл
    def print_out(self, file: typing.TextIO):
        if self.fav:
            file.write('* (Избр.)\n')
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
    # self.ctg - все грамматические категории
    # self.groups - все группы
    def __init__(self):
        self.d: dict[tuple[str, int], Entry] = {}
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0
        self.ctg: dict[str, list[str]] = {}
        self.groups: list[str] = []

    # Подсчитать количество статей в заданной группе
    def count_entries_in_group(self, group: str):
        count_w = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if group in entry.groups:
                count_w += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_w, count_t, count_f

    # Подсчитать количество избранных статей
    def count_fav_entries(self, group: str | None = None):
        count_w = 0
        count_t = 0
        count_f = 0
        if group:
            for entry in self.d.values():
                if entry.fav and group in entry.groups:
                    count_w += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        else:
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
        for group in self.d[additional_entry_key].groups:
            self.d[main_entry_key].groups.add(group)
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
                  fav: bool = False, groups: set[str] | None = None,
                  all_att: int = 0, correct_att: int = 0, correct_att_in_a_row: int = 0,
                  latest_answer_session: tuple[int, int, int] = (0, 0, 0)):
        i = 0
        while True:
            key = wrd_to_key(wrd, i)
            if key not in self.d.keys():
                self.d[key] = Entry(wrd, tr, notes, forms, fav, groups, all_att, correct_att, correct_att_in_a_row,
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

    # Добавить выбранные статьи в избранное
    def fav_entries(self, dct_keys: tuple[tuple[str, int], ...]):
        for key in dct_keys:
            self.d[key].add_to_fav()

    # Убрать выбранные статьи из избранного
    def unfav_entries(self, dct_keys: tuple[tuple[str, int], ...]):
        for key in dct_keys:
            self.d[key].remove_from_fav()

    # Добавить выбранные статьи в группу
    def add_entries_to_group(self, group: str, dct_keys: tuple[tuple[str, int], ...] | list[tuple[str, int]]):
        for key in dct_keys:
            self.d[key].add_to_group(group)

    # Убрать выбранные статьи из группы
    def remove_entries_from_group(self, group: str, dct_keys: tuple[tuple[str, int], ...] | list[tuple[str, int]]):
        for key in dct_keys:
            if group in self.d[key].groups:
                self.d[key].remove_from_group(group)

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

    # Подсчитать среднюю долю правильных ответов
    def count_rating(self):
        sum_num = sum(entry.correct_att for entry in self.d.values())
        sum_den = sum(entry.all_att for entry in self.d.values())
        if sum_den == 0:
            return 0
        return sum_num / sum_den

    # Добавить грамматическую категорию
    def add_ctg(self, ctg_name: str, ctg_values: list[str]):
        assert ctg_name not in self.ctg.keys()

        for entry in self.d.values():
            entry.add_ctg()

        self.ctg[ctg_name] = ctg_values

    # Удалить грамматическую категорию
    def delete_ctg(self, ctg_name: str):
        assert ctg_name in self.ctg.keys()

        index = tuple(self.ctg.keys()).index(ctg_name)
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_ctg(index)
            self.count_f += entry.count_f

        self.ctg.pop(ctg_name)

    # Переименовать грамматическую категорию
    def rename_ctg(self, ctg_name_old: str, ctg_name_new: str):
        assert ctg_name_old in self.ctg.keys()
        assert ctg_name_new not in self.ctg.keys()

        self.ctg[ctg_name_new] = self.ctg[ctg_name_old].copy()
        self.ctg.pop(ctg_name_old)

    # Добавить значение грамматической категории
    def add_ctg_val(self, ctg_name: str, ctg_value: str):
        assert ctg_name in self.ctg.keys()
        assert ctg_value not in self.ctg[ctg_name]

        self.ctg[ctg_name] += [ctg_value]

    # Удалить значение грамматической категории
    def delete_ctg_val(self, ctg_name: str, ctg_value: str):
        assert ctg_name in self.ctg.keys()
        assert ctg_value in self.ctg[ctg_name]

        index = self.ctg[ctg_name].index(ctg_value)
        self.delete_forms_with_val(index, ctg_value)

        self.ctg[ctg_name].remove(ctg_value)
        if len(self.ctg[ctg_name]) == 0:  # Если у категории не осталось значений, то она удаляется
            self.delete_ctg(ctg_name)

    # Переименовать значение грамматической категории
    def rename_ctg_val(self, ctg_name: str, ctg_value_old: str, ctg_value_new: str):
        assert ctg_name in self.ctg.keys()
        assert ctg_value_old in self.ctg[ctg_name]
        assert ctg_value_new not in self.ctg[ctg_name]

        index = tuple(self.ctg.keys()).index(ctg_name)
        self.rename_forms_with_val(index, ctg_value_old, ctg_value_new)

        index = self.ctg[ctg_name].index(ctg_value_old)
        self.ctg[ctg_name][index] = ctg_value_new

    # Добавить группу
    def add_group(self, group: str):
        assert group not in self.groups

        self.groups += [group]

    # Удалить группу
    def delete_group(self, group: str):
        assert group in self.groups

        for entry in self.d.values():
            if group in entry.groups:
                entry.remove_from_group(group)
        self.groups.remove(group)

    # Переименовать группу
    def rename_group(self, group_old: str, group_new: str):
        assert group_old in self.groups
        assert group_new not in self.groups

        self.groups += [group_new]
        for entry in self.d.values():
            if group_old in entry.groups:
                entry.remove_from_group(group_old)
                entry.add_to_group(group_new)
        self.groups.remove(group_old)

    # Прочитать словарь из файла
    def read(self, filepath: str, count_ctg: int):
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
                    frm_key = [line[1:]]
                    for i in range(1, count_ctg):
                        frm_key += [file.readline().strip()]
                    self.add_frm(key, tuple(frm_key), file.readline().strip())
                elif line[0] == '*':
                    self.d[key].add_to_fav()
                elif line[0] == 'g':
                    group = line[1:]
                    self.d[key].add_to_group(group)
                    if group not in self.groups:
                        self.add_group(group)

    # Сохранить словарь в файл
    def save(self, filepath: str, saves_version: int | str):
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f'v{saves_version}\n')
            for entry in self.d.values():
                entry.save(file)

    # Распечатать словарь в файл
    def print_out(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.print_out(file)
                file.write('\n')


# Преобразовать шаблон словоформы в читаемый вид (для вывода на экран)
def frm_key_to_str_for_print(input_tuple: tuple[str, ...] | list[str]):
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
def frm_key_to_str_for_save(input_tuple: tuple[str, ...] | list[str], separator: str = '\n'):
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Перевести слово в ключ для словаря
def wrd_to_key(wrd: str, num: int):
    return wrd, num


# Перевести ключ для словаря в слово
def key_to_wrd(key: tuple[str, int]):
    return key[0]
