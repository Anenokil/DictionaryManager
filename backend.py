"""
A module implementing bilingual dictionary.
By Anenokil
"""

from typing import Iterable, TextIO
import pickle

# Typing
Word = str
Translation = Word
Translations = list[Translation]
Category = str  # e.g., gender, number, tense
Value = str  # e.g., singular/plural, present/past/future
FormPattern = tuple[Value, ...]
Form = Word
Forms = dict[FormPattern, Form]
Text = str
Phrase = Text
PhraseTr = Text
Phrases = dict[Phrase, list[PhraseTr]]
Note = Text
Notes = list[Note]
Group = str
Groups = set[Group]


class Entry(object):
    """
    A dictionary entry representing a word and its associated data.

    This class encapsulates all linguistic and statistical information
    about a dictionary entry, including translations, inflections,
    usage examples, and learning statistics.

    Attributes:
    ----------
    - wrd: The lemma (canonical/dictionary form of the word).
    - tr: Translations.
    - forms: Inflected forms.
    - phrases: Phrases containing the word; usage examples.
    - notes: Notes field.
    - count_t: Translation count.
    - count_f: Inflected form count.
    - count_p: Phrases count.
    - count_n: Notes count.
    - fav: True if the entry is favorite.
    - groups: Groups assigned to the entry.
    - all_att: Total number of game attempts.
    - correct_att: Number of correct guesses (wins).
    - score: Ratio of correct guesses to total attempts (correct_att / all_att).
    - correct_att_in_a_row: Count of consecutive wins.
    - latest_answer_date: Timestamp of the most recent answer.
    """

    # TODO: wrd -> lemma (?)
    # TODO: all_att -> total_att
    # TODO: score -> ratio
    # TODO: correct_att_in_a_row -> win_streak
    # TODO: latest_answer_date -> latest_att_timestamp
    # TODO: groups -> tags

    # TODO: improve __init__ typing

    # TODO: delete / remove - to unify

    def __init__(self,
                 wrd: Word,
                 tr: Translation | Iterable[Translation],
                 forms: Forms | None = None,
                 phrases: dict[Phrase, Iterable[PhraseTr]] | None = None,
                 notes: Note | Iterable[Note] | None = None,
                 groups: Iterable[Group] | None = None,
                 fav: bool = False,
                 all_att: int = 0,
                 correct_att: int = 0,
                 correct_att_in_a_row: int = 0,
                 latest_answer_date: tuple[int, int, int] = (0, 0, 0)):
        """
        Initialize a dictionary entry.

        Args:
            wrd: The lemma (canonical/dictionary form of the word).
            tr: One or more translations.
            forms: Inflected forms of the word (optional).
            phrases: Phrases containing the word; usage examples (optional).
            notes: Notes field (optional).
            groups: Groups assigned to the entry (optional).
            fav: Whether the entry is favorite.
            all_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            correct_att_in_a_row: Count of consecutive wins.
            latest_answer_date: Timestamp of the most recent answer.
        """
        self.wrd = wrd

        self.tr: Translations = [tr] if isinstance(tr, str) else list(tr)
        self.count_t = len(self.tr)

        self.forms: Forms = forms if forms else dict()
        self.count_f = len(self.forms)

        self.phrases: Phrases = {phr: list(tr) for phr, tr in phrases.items()} if phrases else dict()
        self.count_p = len(self.phrases)

        if not notes:
            self.notes: Notes = []
        elif isinstance(notes, str):
            self.notes = [notes]
        else:
            self.notes = list(notes)
        self.count_n = len(self.notes)

        self.groups: Groups = set(groups) if groups else set()

        self.fav = fav

        self.all_att = all_att
        self.correct_att = correct_att
        self.score = 0 if (all_att == 0) else correct_att / all_att
        self.correct_att_in_a_row = correct_att_in_a_row
        self.latest_answer_date = latest_answer_date

    def add_tr(self, new_tr: Translation):
        """
        Add a new translation to the entry.

        Args:
            new_tr: The translation to add.
        """
        if new_tr not in self.tr:
            self.tr += [new_tr]
            self.count_t += 1

    def delete_tr(self, tr: Translation):
        """
        Delete a translation from the entry.

        Args:
            tr: The translation to delete.
        """
        self.tr.remove(tr)
        self.count_t -= 1

    def add_frm(self, frm_key: FormPattern, new_frm: Form):
        """
        Add a new inflected form to the entry.

        Args:
            frm_key: The grammatical category pattern for the inflection.
            new_frm: The actual inflected form to add.
        """
        if frm_key not in self.forms.keys():
            self.forms[frm_key] = new_frm
            self.count_f += 1

    def delete_frm(self, frm_key: FormPattern):
        """
        Remove an inflected form from the entry.

        Args:
            frm_key: The grammatical category pattern identifying the inflection to remove.
        """
        self.forms.pop(frm_key)
        self.count_f -= 1

    def add_phrase(self, new_phr: Phrase, new_phr_tr: PhraseTr):
        """
        Add a new phrase/usage example with its translation.

        Args:
            new_phr: The phrase or usage example containing the word.
            new_phr_tr: The translation of the phrase.
        """
        if new_phr not in self.phrases.keys():
            self.phrases[new_phr] = [new_phr_tr]
            self.count_p += 1
        elif new_phr_tr not in self.phrases[new_phr]:
            self.phrases[new_phr] += [new_phr_tr]
            self.count_p += 1

    def delete_phrase(self, phr: Phrase, phr_tr: PhraseTr):
        """
        Remove a phrase and its translation from the entry.

        Removes the specified phrase-translation pair from `phrases`.

        Args:
            phr: The phrase to remove.
            phr_tr: The translation of the phrase to remove.
        """
        self.phrases[phr].remove(phr_tr)
        if len(self.phrases[phr]) == 0:
            self.phrases.pop(phr)
        self.count_p -= 1

    def add_note(self, new_note: Note):
        """
        Add a new note to the entry.

        Args:
            new_note: The note text to add.
        """
        if new_note not in self.notes:
            self.notes += [new_note]
            self.count_n += 1

    def delete_note(self, note: Note):
        """
        Remove a note from the entry.

        Args:
            note (str): The note text to remove.
        """
        self.notes.remove(note)
        self.count_n -= 1

    def add_to_group(self, group: Group):
        """
        Assign this entry to a group.

        Args:
            group: The group name to add this entry to.
        """
        self.groups.add(group)

    def remove_from_group(self, group: Group):
        """
        Remove this entry from a group.

        Args:
            group: The group name to remove this entry from.
        """
        self.groups.remove(group)

    def add_to_fav(self):
        """
        Mark this entry as favorite.
        """
        self.fav = True

    def remove_from_fav(self):
        """
        Remove this entry from favorites.
        """
        self.fav = False

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

    # Обновить статистику, если совершена верная попытка
    def correct(self, session_number: tuple[int, int, int]):
        self.all_att += 1
        self.correct_att += 1
        self.score = self.correct_att / self.all_att
        if self.correct_att_in_a_row < 0:
            self.correct_att_in_a_row = 1
        else:
            self.correct_att_in_a_row += 1
        self.latest_answer_date = session_number

    # Обновить статистику, если совершена неверная попытка
    def incorrect(self, session_number: tuple[int, int, int]):
        self.all_att += 1
        self.score = self.correct_att / self.all_att
        if self.correct_att_in_a_row > 0:
            self.correct_att_in_a_row = -1
        else:
            self.correct_att_in_a_row -= 1
        self.latest_answer_date = session_number

    # Распечатать статью в файл
    def print_out(self, file: TextIO):
        if self.fav:
            file.write('* (Избр.)\n')
        file.write(f'| {self.wrd} - {self.tr[0]}')
        for i in range(1, self.count_t):
            file.write(f', {self.tr[i]}')
        file.write('\n')
        for frm_template in self.forms.keys():
            file.write(f'|  [{frm_key_to_str_for_print(frm_template)}] {self.forms[frm_template]}\n')
        for phr in self.phrases.keys():
            file.write(f'|  {phr} - {self.phrases[phr][0]}')
            for i in range(1, len(self.phrases[phr])):
                file.write(f', {self.phrases[phr][i]}')
            file.write('\n')
        for note in self.notes:
            file.write(f'| > {note}\n')


DctKey = tuple[Word, int]
DctData = dict[DctKey, Entry]
AllFeatures = dict[Category, list[Value]]
AllGroups = list[Group]


class Dictionary(object):
    """
    A bilingual dictionary.

    Attributes:
    ----------
    - d: The main dictionary data structure mapping lemmas to Entry objects.
    - count_w: Total number of word entries (lemmas) in the dictionary.
    - count_t: Total number of translations across all entries in the dictionary.
    - count_f: Total number of inflected forms across all entries in the dictionary.
    - ctg: Collection of all grammatical categories present in the dictionary.
      Used for categorization and filtering of word forms.
    - groups: All groups/tags assigned to entries across the entire dictionary.
      Used for organizing and grouping dictionary content.
    """

    def __init__(self):
        """
        Initialize a dictionary.
        """
        self.d: DctData = dict()
        self.count_w = 0
        self.count_t = 0
        self.count_f = 0
        self.ctg: AllFeatures = dict()
        self.groups: AllGroups = []
        self.saving_version = 1

    # Подсчитать количество статей в заданной группе
    def count_entries_in_group(self, group: Group) -> tuple[int, int, int]:
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
    def count_fav_entries(self, group: Group | None = None) -> tuple[int, int, int]:
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

    # Подсчитать среднюю долю правильных ответов
    def count_rating(self) -> tuple[int, int]:
        sum_num = sum(entry.correct_att for entry in self.d.values())
        sum_den = sum(entry.all_att for entry in self.d.values())
        return sum_num, sum_den

    # Добавить статью в словарь
    def add_entry(self,
                  wrd: Word,
                  tr: Translation | Iterable[Translation],
                  forms: Forms | None = None,
                  phrases: dict[Phrase, Iterable[PhraseTr]] | None = None,
                  notes: Note | Iterable[Note] | None = None,
                  groups: Iterable[Group] | None = None,
                  fav: bool = False,
                  all_att: int = 0,
                  correct_att: int = 0,
                  correct_att_in_a_row: int = 0,
                  latest_answer_date: tuple[int, int, int] = (0, 0, 0)) -> DctKey:
        i = 0
        while True:
            key = wrd_to_key(wrd, i)
            if key not in self.d.keys():
                self.d[key] = Entry(wrd, tr, forms, phrases, notes, groups, fav, all_att,
                                    correct_att, correct_att_in_a_row, latest_answer_date)
                self.count_w += 1
                self.count_t += self.d[key].count_t
                self.count_f += self.d[key].count_f
                return key
            i += 1

    # Удалить статью
    def delete_entry(self, key: DctKey):
        self.count_w -= 1
        self.count_t -= self.d[key].count_t
        self.count_f -= self.d[key].count_f
        self.d.pop(key)

    # Объединить две статьи с одинаковым словом в одну
    def merge_entries(self, main_entry_key: DctKey, additional_entry_key: DctKey):
        main_entry = self.d[main_entry_key]
        additional_entry = self.d[additional_entry_key]

        self.count_t -= additional_entry.count_t
        self.count_t -= main_entry.count_t
        self.count_f -= additional_entry.count_f
        self.count_f -= main_entry.count_f

        for tr in additional_entry.tr:
            main_entry.add_tr(tr)
        for note in additional_entry.notes:
            main_entry.add_note(note)
        for phr_key in additional_entry.phrases.keys():
            for phr_tr in additional_entry.phrases[phr_key]:
                main_entry.add_phrase(phr_key, phr_tr)
        for frm_key in additional_entry.forms.keys():
            frm = additional_entry.forms[frm_key]
            main_entry.add_frm(frm_key, frm)
        if additional_entry.fav:
            main_entry.fav = True
        for group in additional_entry.groups:
            main_entry.groups.add(group)
        main_entry.all_att += additional_entry.all_att
        main_entry.correct_att += additional_entry.correct_att
        main_entry.score = 0 if (main_entry.all_att == 0) else main_entry.correct_att / main_entry.all_att
        main_entry.correct_att_in_a_row += additional_entry.correct_att_in_a_row

        self.count_w -= 1
        self.count_t += main_entry.count_t
        self.count_f += main_entry.count_f

        self.d.pop(additional_entry_key)

    # Добавить перевод к статье
    def add_tr(self, key: DctKey, tr: Translation):
        self.count_t -= self.d[key].count_t
        self.d[key].add_tr(tr)
        self.count_t += self.d[key].count_t

    # Удалить перевод из статьи
    def delete_tr(self, key: DctKey, tr: Translation):
        self.count_t -= self.d[key].count_t
        self.d[key].delete_tr(tr)
        self.count_t += self.d[key].count_t

    # Добавить словоформу к статье
    def add_frm(self, key: DctKey, frm_key: FormPattern, frm: Form):
        self.count_f -= self.d[key].count_f
        self.d[key].add_frm(frm_key, frm)
        self.count_f += self.d[key].count_f

    # Удалить словоформу из статьи
    def delete_frm(self, key: DctKey, frm_key: FormPattern):
        self.count_f -= self.d[key].count_f
        self.d[key].delete_frm(frm_key)
        self.count_f += self.d[key].count_f

    # Добавить фразу к статье
    def add_phrase(self, key: DctKey, phr: Phrase, phr_tr: PhraseTr):
        self.d[key].add_phrase(phr, phr_tr)

    # Удалить фразу из статьи
    def delete_phrase(self, key: DctKey, phr: Phrase, phr_tr: PhraseTr):
        self.d[key].delete_phrase(phr, phr_tr)

    # Добавить сноску к статье
    def add_note(self, key: DctKey, note: Note):
        self.d[key].add_note(note)

    # Удалить сноску из статьи
    def delete_note(self, key: DctKey, note: Note):
        self.d[key].delete_note(note)

    # Добавить выбранные статьи в группу
    def add_entries_to_group(self, group: Group, dct_keys: Iterable[DctKey]):
        for key in dct_keys:
            self.d[key].add_to_group(group)

    # Убрать выбранные статьи из группы
    def remove_entries_from_group(self, group: Group, dct_keys: Iterable[DctKey]):
        for key in dct_keys:
            if group in self.d[key].groups:
                self.d[key].remove_from_group(group)

    # Добавить выбранные статьи в избранное
    def fav_entries(self, dct_keys: Iterable[DctKey]):
        for key in dct_keys:
            self.d[key].add_to_fav()

    # Убрать выбранные статьи из избранного
    def unfav_entries(self, dct_keys: Iterable[DctKey]):
        for key in dct_keys:
            self.d[key].remove_from_fav()

    # Удалить данное значение категории у всех словоформ
    def delete_forms_with_val(self, pos: int, ctg_val: Value):
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_forms_with_val(pos, ctg_val)
            self.count_f += entry.count_f

    # Переименовать данное значение категории у всех словоформ
    def rename_forms_with_val(self, pos: int, old_ctg_val: Value, new_ctg_val: Value):
        for entry in self.d.values():
            entry.rename_forms_with_val(pos, old_ctg_val, new_ctg_val)

    # Добавить грамматическую категорию
    def add_ctg(self, ctg_name: Category, ctg_values: list[Value]):
        assert ctg_name not in self.ctg.keys()

        for entry in self.d.values():
            entry.add_ctg()

        self.ctg[ctg_name] = ctg_values

    # Удалить грамматическую категорию
    def delete_ctg(self, ctg_name: Category):
        assert ctg_name in self.ctg.keys()

        index = tuple(self.ctg.keys()).index(ctg_name)
        for entry in self.d.values():
            self.count_f -= entry.count_f
            entry.delete_ctg(index)
            self.count_f += entry.count_f

        self.ctg.pop(ctg_name)

    # Переименовать грамматическую категорию
    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        assert ctg_name_old in self.ctg.keys()
        assert ctg_name_new not in self.ctg.keys()

        self.ctg[ctg_name_new] = self.ctg[ctg_name_old].copy()
        self.ctg.pop(ctg_name_old)

    # Добавить значение грамматической категории
    def add_ctg_val(self, ctg_name: Category, ctg_value: Value):
        assert ctg_name in self.ctg.keys()
        assert ctg_value not in self.ctg[ctg_name]

        self.ctg[ctg_name] += [ctg_value]

    # Удалить значение грамматической категории
    def delete_ctg_val(self, ctg_name: Category, ctg_value: Value):
        assert ctg_name in self.ctg.keys()
        assert ctg_value in self.ctg[ctg_name]

        index = tuple(self.ctg.keys()).index(ctg_name)
        self.delete_forms_with_val(index, ctg_value)

        self.ctg[ctg_name].remove(ctg_value)
        if len(self.ctg[ctg_name]) == 0:  # Если у категории не осталось значений, то она удаляется
            self.delete_ctg(ctg_name)

    # Переименовать значение грамматической категории
    def rename_ctg_val(self, ctg_name: Category, ctg_value_old: Value, ctg_value_new: Value):
        assert ctg_name in self.ctg.keys()
        assert ctg_value_old in self.ctg[ctg_name]
        assert ctg_value_new not in self.ctg[ctg_name]

        index = tuple(self.ctg.keys()).index(ctg_name)
        self.rename_forms_with_val(index, ctg_value_old, ctg_value_new)

        index = self.ctg[ctg_name].index(ctg_value_old)
        self.ctg[ctg_name][index] = ctg_value_new

    # Добавить группу
    def add_group(self, group: Group):
        assert group not in self.groups

        self.groups += [group]

    # Удалить группу
    def delete_group(self, group: Group):
        assert group in self.groups

        for entry in self.d.values():
            if group in entry.groups:
                entry.remove_from_group(group)
        self.groups.remove(group)

    # Переименовать группу
    def rename_group(self, group_old: Group, group_new: Group):
        assert group_old in self.groups
        assert group_new not in self.groups

        self.groups += [group_new]
        for entry in self.d.values():
            if group_old in entry.groups:
                entry.remove_from_group(group_old)
                entry.add_to_group(group_new)
        self.groups.remove(group_old)

    # Прочитать словарь из файла
    def read(self, filepath: str):
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)

        loaded_version = save_data.get('version', 1)
        data = save_data.get('data', {})

        self.d = data.get('d', {})
        self.ctg = data.get('ctg', {})
        self.groups = data.get('groups', {})
        self.count_w = data.get('count_w', {})
        self.count_t = data.get('count_t', {})
        self.count_f = data.get('count_f', {})

    # Сохранить словарь в файл
    def save(self, filepath: str):
        save_data = {
            'version': self.saving_version,
            'data': {
                'd': self.d,
                'ctg': self.ctg,
                'groups': self.groups,
                'count_w': self.count_w,
                'count_t': self.count_t,
                'count_f': self.count_f,
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)

    # Распечатать словарь в файл
    def print_out(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.print_out(file)
                file.write('\n')


# Преобразовать шаблон словоформы в читаемый вид (для вывода на экран)
def frm_key_to_str_for_print(input_tuple: FormPattern | list[Value]) -> str:
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
def frm_key_to_str_for_save(input_tuple: FormPattern | list[Value], separator: str = '\n') -> str:
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Перевести слово в ключ для словаря
def wrd_to_key(wrd: Word, num: int) -> DctKey:
    return wrd, num


# Перевести ключ для словаря в слово
def key_to_wrd(key: DctKey) -> str:
    return key[0]
