"""
A module implementing bilingual dictionary.
By Anenokil
"""

from typing import Iterable, Generator, Mapping, TextIO
import pickle

# Typing
Word = str
Translation = Word
Translations = list[Translation]
Category = str  # e.g., gender, number, tense
CtgValue = str  # e.g., singular/plural, present/past/future
FormPattern = tuple[CtgValue, ...]
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
Timestamp = tuple[int, int, int]


class Entry(object):
    """
    A dictionary entry representing a word and its associated data.

    This class encapsulates all linguistic and statistical information
    about a dictionary entry, including translations, inflections,
    usage examples, and learning statistics.

    Attributes:
    ----------
    - lemma: The lemma (canonical/dictionary form of the word).
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
    - total_att: Total number of game attempts.
    - correct_att: Number of correct guesses (wins).
    - accuracy_rate: Ratio of correct guesses to total attempts (correct_att / total_att).
    - win_streak: Count of consecutive wins.
    - latest_att_timestamp: Timestamp of the most recent answer.
    """

    # TODO: delete / remove - to unify

    def __init__(self,
                 lemma: Word,
                 tr: Translation | Iterable[Translation],
                 forms: Mapping[FormPattern, Form] | None = None,
                 phrases: Mapping[Phrase, Iterable[PhraseTr]] | None = None,
                 notes: Note | Iterable[Note] | None = None,
                 groups: Iterable[Group] | None = None,
                 fav: bool = False,
                 total_att: int = 0,
                 correct_att: int = 0,
                 win_streak: int = 0,
                 latest_att_timestamp: Timestamp = (0, 0, 0)):
        """
        Initialize a dictionary entry.

        Args:
            lemma: The lemma (canonical/dictionary form of the word).
            tr: One or more translations.
            forms: Inflected forms of the word.
            phrases: Phrases containing the word; usage examples.
            notes: Notes field.
            groups: Groups assigned to the entry.
            fav: Whether the entry is favorite.
            total_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            win_streak: Count of consecutive wins.
            latest_att_timestamp: Timestamp of the most recent answer.
        """
        self.lemma = lemma

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

        self.total_att = total_att
        self.correct_att = correct_att
        self.accuracy_rate = 0 if (total_att == 0) else correct_att / total_att
        self.win_streak = win_streak
        self.latest_att_timestamp = latest_att_timestamp

    def add_tr(self, new_tr: Translation):
        """
        Add a new translation to the entry.

        Args:
            new_tr: The translation to add.
        """
        if new_tr not in self.tr:
            self.tr.append(new_tr)
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
            note: The note text to remove.
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

    def delete_ctg_value(self, pos: int, ctg_val: CtgValue):
        """
        Delete the specified category value from all word forms.

        Args:
            pos: The position (index) of the category in form pattern.
            ctg_val: The category value to be removed.
        """
        to_delete = [key for key in self.forms.keys() if key[pos] == ctg_val]
        self.count_f -= len(to_delete)
        for key in to_delete:
            self.forms.pop(key)

    def rename_ctg_value(self, pos: int, old_ctg_val: CtgValue, new_ctg_val: CtgValue):
        """
        Rename the specified category value in all word forms.

        Args:
            pos: The position (index) of the category in form pattern.
            old_ctg_val: The current category value to be replaced.
            new_ctg_val: The new category value that will replace the old one.
        """
        to_rename = [key for key in self.forms.keys() if key[pos] == old_ctg_val]
        for key in to_rename:
            lst = list(key)
            lst[pos] = new_ctg_val
            lst = tuple(lst)
            self.forms[lst] = self.forms[key]
            self.forms.pop(key)

    def add_ctg(self):
        """
        Add a new empty category to all word forms.
        """
        keys = list(self.forms.keys())
        for key in keys:
            new_key = list(key) + ['']
            new_key = tuple(new_key)
            self.forms[new_key] = self.forms[key]
            self.forms.pop(key)

    def delete_ctg(self, pos: int):
        """
        Delete the category at the specified position from all word forms.

        Removes the entire category (including all its values) at position `pos`
        from all word forms in the entry.

        Args:
            pos: The position (index) of the category to be deleted in form pattern.
        """
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

    def correct(self, session_number: Timestamp):
        """
        Update learning statistics when a correct attempt is made.

        Increments both total attempts and correct attempts counters, recalculates the
        correct accuracy_rate, updates the win streak, and sets the latest attempt timestamp.

        Args:
            session_number: A tuple representing the session identifier.
        """
        self.total_att += 1
        self.correct_att += 1
        self.accuracy_rate = self.correct_att / self.total_att
        if self.win_streak <= 0:
            self.win_streak = 1
        else:
            self.win_streak += 1
        self.latest_att_timestamp = session_number

    def incorrect(self, session_number: Timestamp):
        """
        Update learning statistics when an incorrect attempt is made.

        Increments the total attempts counter, recalculates the correct accuracy_rate,
        resets the win streak to 0, and sets the latest attempt timestamp.

        Args:
            session_number: A tuple representing the session identifier.
        """
        self.total_att += 1
        self.accuracy_rate = self.correct_att / self.total_att
        if self.win_streak > 0:
            self.win_streak = -1
        else:
            self.win_streak -= 1
        self.latest_att_timestamp = session_number

    def print_out(self, file: TextIO):
        """
        Print the dictionary entry to the specified file.

        Outputs a formatted representation of the entire dictionary entry including
        lemma, translations, inflected forms, phrases, notes, and learning statistics
        to the given file handle.

        Args:
            file: A text file object opened for writing where the entry will be printed.
        """
        if self.fav:
            file.write('* (Избр.)\n')
        file.write(f'| {self.lemma} - {self.tr[0]}')
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


# Typing
EntryID = int
DctData = dict[EntryID, Entry]
AllFeatures = dict[Category, list[CtgValue]]
AllGroups = list[Group]


class Dictionary(object):
    """
    A bilingual dictionary.

    Attributes:
    ----------
    - d: The main dictionary data structure mapping lemmas to Entry objects.
    - count_e: Total number of word entries (lemmas) in the dictionary.
    - count_t: Total number of translations across all entries in the dictionary.
    - count_f: Total number of inflected forms across all entries in the dictionary.
    - ctg: Collection of all grammatical categories present in the dictionary.
      Used for categorization and filtering of word forms.
    - groups: All groups/tags assigned to entries across the entire dictionary.
      Used for organizing and grouping dictionary content.
    - saving_version: The version of the data format used for serialization.
    """

    def __init__(self):
        """
        Initialize a dictionary.
        """
        self.d: DctData = dict()
        self.counters = {
            'lemmas': 0,
            'translations': 0,
            'forms': 0,
            'phrases': 0,
            'notes': 0,
        }
        self.ctg: AllFeatures = dict()
        self.groups: AllGroups = []
        self.saving_version = 1
        self._max_entry_id = 0

    def count_entries_in_group(self, group: Group) -> tuple[int, int, int]:
        """
        Count the number of entries, translations, and inflected forms in the specified group.

        Args:
            group: The group for which to count statistics.

        Returns:
            A tuple containing three integers:
            - Number of dictionary entries (lemmas) in the group;
            - Total number of translations across all entries in the group;
            - Total number of inflected forms across all entries in the group.
        """
        count_e = 0
        count_t = 0
        count_f = 0
        for entry in self.d.values():
            if group in entry.groups:
                count_e += 1
                count_t += entry.count_t
                count_f += entry.count_f
        return count_e, count_t, count_f

    def count_fav_entries(self, group: Group | None = None) -> tuple[int, int, int]:
        """
        Count the number of favorite entries, their translations, and inflected forms.

        Args:
            group: If specified, counts only favorite entries within the given group.
                   If None, counts all favorite entries in the dictionary.

        Returns:
            A tuple containing three integers:
            - Number of favorite dictionary entries (lemmas);
            - Total number of translations across favorite entries;
            - Total number of inflected forms across favorite entries.
        """
        count_e = 0
        count_t = 0
        count_f = 0
        if group:
            for entry in self.d.values():
                if entry.fav and group in entry.groups:
                    count_e += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        else:
            for entry in self.d.values():
                if entry.fav:
                    count_e += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        return count_e, count_t, count_f

    def score(self) -> tuple[int, int]:
        """
        Get the global count of correct attempts and total attempts across all entries.

        Returns:
            A tuple containing two integers:
            - Total number of correct attempts (wins) across all entries;
            - Total number of all learning attempts across all entries.
        """
        correct = sum(entry.correct_att for entry in self.d.values())
        total = sum(entry.total_att for entry in self.d.values())
        return correct, total

    def get_entries(self) -> Generator[Entry, None, None]:
        """
        Iterate over all entries in the dictionary.

        Yields:
            The next entry in the dictionary.

        Returns:
            Generator yielding Entry objects.
        """
        yield from self.d.values()

    def add_entry(self,
                  lemma: Word,
                  tr: Translation | Iterable[Translation],
                  forms: Mapping[FormPattern, Form] | None = None,
                  phrases: Mapping[Phrase, Iterable[PhraseTr]] | None = None,
                  notes: Note | Iterable[Note] | None = None,
                  groups: Iterable[Group] | None = None,
                  fav: bool = False,
                  total_att: int = 0,
                  correct_att: int = 0,
                  win_streak: int = 0,
                  latest_att_timestamp: Timestamp = (0, 0, 0)) -> EntryID:
        """
        Add a new dictionary entry.

        Args:
            lemma: The lemma (canonical/dictionary form of the word).
            tr: One or more translations.
            forms: Inflected forms of the word.
            phrases: Phrases containing the word; usage examples.
            notes: Notes field.
            groups: Groups assigned to the entry.
            fav: Whether the entry is favorite.
            total_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            win_streak: Count of consecutive wins.
            latest_att_timestamp: Timestamp of the most recent answer.

        Returns:
            The dictionary key under which the entry was stored.
        """
        self._max_entry_id += 1
        entry_id = self._max_entry_id

        self.d[entry_id] = Entry(lemma, tr, forms, phrases, notes, groups, fav, total_att,
                                 correct_att, win_streak, latest_att_timestamp)

        self.counters['lemmas'] += 1
        self.counters['translations'] += self.d[entry_id].count_t
        self.counters['forms']        += self.d[entry_id].count_f
        self.counters['phrases']      += self.d[entry_id].count_p
        self.counters['notes']        += self.d[entry_id].count_n

        return entry_id

    # Удалить статью
    def delete_entry(self, entry_id: EntryID):
        self.counters['lemmas'] -= 1
        self.counters['translations'] -= self.d[entry_id].count_t
        self.counters['forms']        -= self.d[entry_id].count_f
        self.counters['phrases']      -= self.d[entry_id].count_p
        self.counters['notes']        -= self.d[entry_id].count_n

        del self.d[entry_id]

    # Объединить две статьи с одинаковым словом в одну
    def merge_entries(self, entry_id_1: EntryID, entry_id_2: EntryID):
        main_entry = self.d[entry_id_1]
        additional_entry = self.d[entry_id_2]

        for entry_id in (entry_id_1, entry_id_2):
            self.counters['translations'] -= self.d[entry_id].count_t
            self.counters['forms']        -= self.d[entry_id].count_f
            self.counters['phrases']      -= self.d[entry_id].count_p
            self.counters['notes']        -= self.d[entry_id].count_n

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
        main_entry.total_att += additional_entry.total_att
        main_entry.correct_att += additional_entry.correct_att
        main_entry.accuracy_rate = 0 if (main_entry.total_att == 0) else main_entry.correct_att / main_entry.total_att
        main_entry.win_streak += additional_entry.win_streak

        for entry_id in (entry_id_1, entry_id_2):
            self.counters['translations'] += self.d[entry_id].count_t
            self.counters['forms']        += self.d[entry_id].count_f
            self.counters['phrases']      += self.d[entry_id].count_p
            self.counters['notes']        += self.d[entry_id].count_n
        self.counters['lemmas'] -= 1

        del self.d[entry_id_2]

    # Добавить перевод к статье
    def add_tr(self, entry_id: EntryID, tr: Translation):
        self.counters['translations'] -= self.d[entry_id].count_t
        self.d[entry_id].add_tr(tr)
        self.counters['translations'] += self.d[entry_id].count_t

    # Удалить перевод из статьи
    def delete_tr(self, entry_id: EntryID, tr: Translation):
        self.counters['translations'] -= self.d[entry_id].count_t
        self.d[entry_id].delete_tr(tr)
        self.counters['translations'] += self.d[entry_id].count_t

    # Добавить словоформу к статье
    def add_frm(self, entry_id: EntryID, frm_key: FormPattern, frm: Form):
        self.counters['forms'] -= self.d[entry_id].count_f
        self.d[entry_id].add_frm(frm_key, frm)
        self.counters['forms'] += self.d[entry_id].count_f

    # Удалить словоформу из статьи
    def delete_frm(self, entry_id: EntryID, frm_key: FormPattern):
        self.counters['forms'] -= self.d[entry_id].count_f
        self.d[entry_id].delete_frm(frm_key)
        self.counters['forms'] += self.d[entry_id].count_f

    # Добавить фразу к статье
    def add_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        self.counters['phrases'] -= self.d[entry_id].count_p
        self.d[entry_id].add_phrase(phr, phr_tr)
        self.counters['phrases'] += self.d[entry_id].count_p

    # Удалить фразу из статьи
    def delete_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        self.counters['phrases'] -= self.d[entry_id].count_p
        self.d[entry_id].delete_phrase(phr, phr_tr)
        self.counters['phrases'] += self.d[entry_id].count_p

    # Добавить сноску к статье
    def add_note(self, entry_id: EntryID, note: Note):
        self.counters['notes'] -= self.d[entry_id].count_n
        self.d[entry_id].add_note(note)
        self.counters['notes'] += self.d[entry_id].count_n

    # Удалить сноску из статьи
    def delete_note(self, entry_id: EntryID, note: Note):
        self.counters['notes'] -= self.d[entry_id].count_n
        self.d[entry_id].delete_note(note)
        self.counters['notes'] += self.d[entry_id].count_n

    # Добавить выбранные статьи в группу
    def add_entries_to_group(self, group: Group, entry_ids: Iterable[EntryID]):
        for entry_id in entry_ids:
            self.d[entry_id].add_to_group(group)

    # Убрать выбранные статьи из группы
    def remove_entries_from_group(self, group: Group, entry_ids: Iterable[EntryID]):
        for entry_id in entry_ids:
            if group in self.d[entry_id].groups:
                self.d[entry_id].remove_from_group(group)

    # Добавить выбранные статьи в избранное
    def fav_entries(self, entry_ids: Iterable[EntryID]):
        for entry_id in entry_ids:
            self.d[entry_id].add_to_fav()

    # Убрать выбранные статьи из избранного
    def unfav_entries(self, entry_ids: Iterable[EntryID]):
        for entry_id in entry_ids:
            self.d[entry_id].remove_from_fav()

    # Добавить грамматическую категорию
    def add_ctg(self, ctg_name: Category, ctg_values: list[CtgValue]):
        assert ctg_name not in self.ctg.keys()

        for entry in self.d.values():
            entry.add_ctg()

        self.ctg[ctg_name] = ctg_values

    # Удалить грамматическую категорию
    def delete_ctg(self, ctg_name: Category):
        assert ctg_name in self.ctg.keys()

        index = tuple(self.ctg.keys()).index(ctg_name)
        for entry in self.d.values():
            self.counters['forms'] -= entry.count_f
            entry.delete_ctg(index)
            self.counters['forms'] += entry.count_f

        self.ctg.pop(ctg_name)

    # Переименовать грамматическую категорию
    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        assert ctg_name_old in self.ctg.keys()
        assert ctg_name_new not in self.ctg.keys()

        self.ctg[ctg_name_new] = self.ctg[ctg_name_old].copy()
        self.ctg.pop(ctg_name_old)

    # Добавить значение грамматической категории
    def add_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        assert ctg_name in self.ctg.keys()
        assert ctg_value not in self.ctg[ctg_name]

        self.ctg[ctg_name] += [ctg_value]

    # Удалить значение грамматической категории
    def delete_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        assert ctg_name in self.ctg.keys()
        assert ctg_value in self.ctg[ctg_name]

        index = tuple(self.ctg.keys()).index(ctg_name)
        for entry in self.d.values():
            self.counters['forms'] -= entry.count_f
            entry.delete_ctg_value(index, ctg_value)
            self.counters['forms'] += entry.count_f

        self.ctg[ctg_name].remove(ctg_value)
        if len(self.ctg[ctg_name]) == 0:  # Если у категории не осталось значений, то она удаляется
            self.delete_ctg(ctg_name)

    # Переименовать значение грамматической категории
    def rename_ctg_value(self, ctg_name: Category, ctg_value_old: CtgValue, ctg_value_new: CtgValue):
        assert ctg_name in self.ctg.keys()
        assert ctg_value_old in self.ctg[ctg_name]
        assert ctg_value_new not in self.ctg[ctg_name]

        index = tuple(self.ctg.keys()).index(ctg_name)
        for entry in self.d.values():
            entry.rename_ctg_value(index, ctg_value_old, ctg_value_new)

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

    def read(self, filepath: str):
        """
        Read the dictionary from the specified file.

        Args:
            filepath: The path to the file from which the dictionary will be loaded.
        """
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)

        loaded_version = save_data.get('version', 1)
        data = save_data.get('data', {})

        self.d = data.get('d', {})
        self.ctg = data.get('ctg', {})
        self.groups = data.get('groups', {})
        self.counters = data.get('counters', {})
        self._max_entry_id = data.get('max_entry_id', {})

    def save(self, filepath: str):
        """
        Save the dictionary to the specified file.

        Args:
            filepath: The path to the file where the dictionary will be saved. The file will be
                      created if it doesn't exist, or overwritten if it exists.
        """
        save_data = {
            'version': self.saving_version,
            'data': {
                'd': self.d,
                'ctg': self.ctg,
                'groups': self.groups,
                'counters': self.counters,
                'max_entry_id': self._max_entry_id,
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)

    def print_out(self, filepath: str):
        """
        Print the dictionary to the specified file.

        Outputs a formatted representation of the entire dictionary.

        Args:
            filepath: The path to the text file. The files contents will be overwritten.
        """
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.d.values():
                entry.print_out(file)
                file.write('\n')


# Преобразовать шаблон словоформы в читаемый вид (для вывода на экран)
def frm_key_to_str_for_print(input_tuple: FormPattern | list[CtgValue]) -> str:
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
def frm_key_to_str_for_save(input_tuple: FormPattern | list[CtgValue], separator: str = '\n') -> str:
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# TODO : remove
# Перевести слово в ключ для словаря
#def wrd_to_key(lemma: Word, num: int) -> DctKey:
#    return lemma, num


# TODO : remove
# Перевести ключ для словаря в слово
#def key_to_wrd(key: DctKey) -> str:
#    return key[0]
