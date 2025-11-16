"""
A module implementing bilingual dictionary.
By Anenokil
"""

from typing import Any, Iterable, Generator, Mapping, TextIO
import os
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
EntryID = int


class Entry:
    """
    A dictionary entry representing a word and its associated data.

    This class encapsulates all linguistic and statistical information
    about a dictionary entry, including translations, inflections,
    usage examples, and learning statistics.

    Attributes:
    ----------
    - id: Entry ID.
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
                 eid: EntryID,
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
            eid: Entry ID.
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

        self.id = eid

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
            frm_key: The form pattern for the inflection.
            new_frm: The actual inflected form to add.
        """

        if frm_key not in self.forms.keys():
            self.forms[frm_key] = new_frm
            self.count_f += 1

    def delete_frm(self, frm_key: FormPattern):
        """
        Remove an inflected form from the entry.

        Args:
            frm_key: The form pattern identifying the inflection to remove.
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
        """Mark this entry as favorite."""

        self.fav = True

    def remove_from_fav(self):
        """Remove this entry from favorites."""

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
        """Add a new empty category to all word forms."""

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
        accuracy rate, updates the win streak, and sets the latest attempt timestamp.

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

        Increments the total attempts counter, recalculates the accuracy rate,
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
        file.write(f'| {self.lemma} - ')
        file.write(', '.join(tr for tr in self.tr))
        file.write('\n')
        for pattern, form in self.forms.items():
            file.write(f'|  [{pattern_to_str(pattern)}] {form}\n')
        for phr, phr_tr in self.phrases.items():
            file.write(f'|  {phr} - ')
            file.write(', '.join(tr for tr in phr_tr))
            file.write('\n')
        for note in self.notes:
            file.write(f'| > {note}\n')


# Typing
Entries = dict[EntryID, Entry]
Index = dict[str, set[EntryID]]
Indexes = dict[str, Index]
AllFeatures = dict[Category, list[CtgValue]]
AllGroups = list[Group]
DctName = str


class Dictionary:
    """
    A bilingual dictionary.

    Attributes:
    ----------
    - name: Dictionary name.
    - entries: The main dictionary data structure mapping entry IDs to Entry objects.
    - indexes: Search indexes for fast entry lookup by content. Keys:

      - 'lemmas': Maps lemmas to entry IDs containing them.
      - 'translations': Maps translations to entry IDs containing them.
      - 'forms': Maps inflected forms to entry IDs containing them.
      - 'groups': Maps group names to entry IDs belonging to them.
    - counters: Word counts statistics with keys:

      - 'lemmas': Total number of entries (lemmas) in the dictionary.
      - 'translations': Total number of translations across all entries in the dictionary.
      - 'forms': Total number of inflected forms across all entries in the dictionary.
      - 'phrases': Total number of phrase examples across all entries.
      - 'notes': Total number of notes across all entries.
    - features: Collection of all grammatical categories and their values present in the dictionary.
    - groups: All groups/tags assigned to entries across the entire dictionary.
      Used for organizing and grouping dictionary content.
    - saving_version: The version of the data format used for serialization.
    """

    def __init__(self, name: DctName | None = None):
        """
        Initialize a dictionary.

        Args:
            name: The dictionary name.
        """

        self.name = name
        self.entries: Entries = dict()
        self.indexes: Indexes = {
            'lemmas': {},
            'translations': {},
            'forms': {},
            'groups': {},
        }
        self.counters = {
            'lemmas': 0,
            'translations': 0,
            'forms': 0,
            'phrases': 0,
            'notes': 0,
        }
        self.features: AllFeatures = dict()
        self.groups: AllGroups = []
        self.saving_version = 1
        self._max_entry_id = 0

    def _update_index(self, index_name: str, keys: Iterable[str], entry_id: EntryID, action: str):
        """
        Update a search index by adding or removing an entry.

        Args:
            index_name: Name of the index to update ('lemmas', 'translations', 'forms', or 'groups').
            keys: Iterable of keys to add or remove from the index.
            entry_id: ID of the entry to associate with the keys.
            action: Either 'add' or 'remove'.
        """

        assert index_name in self.indexes.keys()
        assert action in ('add', 'remove')

        index = self.indexes[index_name]

        if action == 'add':
            for key in keys:
                if key in index:
                    index[key].add(entry_id)
                else:
                    index[key] = {entry_id}
        else:
            for key in keys:
                index[key].remove(entry_id)
                if not index[key]:
                    index.pop(key)

    def rename(self, new_name: str):
        """
        Rename a dictionary.

        Args:
            new_name: New name of the dictionary.
        """

        self.name = new_name

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
        for entry_id in self.indexes['groups'][group]:
            entry = self.entries[entry_id]
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
            for entry_id in self.indexes['groups'][group]:
                entry = self.entries[entry_id]
                if entry.fav:
                    count_e += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        else:
            for entry in self.entries.values():
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

        correct = sum(entry.correct_att for entry in self.entries.values())
        total = sum(entry.total_att for entry in self.entries.values())
        return correct, total

    def get_entries(self) -> Generator[Entry, None, None]:
        """
        Iterate over all entries in the dictionary.

        Yields:
            The next entry in the dictionary.
        """

        yield from self.entries.values()

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
            New entry ID.
        """

        self._max_entry_id += 1
        entry_id = self._max_entry_id

        self.entries[entry_id] = Entry(entry_id, lemma, tr, forms, phrases, notes, groups, fav, total_att,
                                       correct_att, win_streak, latest_att_timestamp)
        entry = self.entries[entry_id]

        self._update_index('lemmas', [lemma], entry_id, 'add')
        self._update_index('translations', tr, entry_id, 'add')
        self._update_index('forms', forms.values(), entry_id, 'add')
        self._update_index('groups', groups, entry_id, 'add')

        self.counters['lemmas'] += 1
        self.counters['translations'] += entry.count_t
        self.counters['forms']        += entry.count_f
        self.counters['phrases']      += entry.count_p
        self.counters['notes']        += entry.count_n

        return entry_id

    def delete_entry(self, entry_id: EntryID):
        """
        Delete a dictionary entry.

        Removes the entry from the dictionary, updates all indexes, and
        adjusts counters accordingly.

        Args:
            entry_id: ID of the entry to delete.
        """

        entry = self.entries[entry_id]

        self.counters['lemmas'] -= 1
        self.counters['translations'] -= entry.count_t
        self.counters['forms']        -= entry.count_f
        self.counters['phrases']      -= entry.count_p
        self.counters['notes']        -= entry.count_n

        self._update_index('lemmas', [entry.lemma], entry_id, 'remove')
        self._update_index('translations', entry.tr, entry_id, 'remove')
        self._update_index('forms', entry.forms.values(), entry_id, 'remove')
        self._update_index('groups', entry.groups, entry_id, 'remove')

        del self.entries[entry_id]

    def merge_entries(self, entry_id_1: EntryID, entry_id_2: EntryID):
        """
        Merge two entries with the same word into one.

        Combines all data from the second entry into the first entry.
        The second entry is deleted after merging.

        Args:
            entry_id_1: ID of the main entry (will be kept).
            entry_id_2: ID of the entry to merge into the main entry (will be deleted).
        """

        main_entry = self.entries[entry_id_1]
        additional_entry = self.entries[entry_id_2]

        self._update_index('lemmas', [additional_entry.lemma], entry_id_1, 'add')
        self._update_index('translations', additional_entry.tr, entry_id_1, 'add')
        self._update_index('forms', additional_entry.forms.values(), entry_id_1, 'add')
        self._update_index('groups', additional_entry.groups, entry_id_1, 'add')

        self.counters['translations'] -= main_entry.count_t
        self.counters['forms']        -= main_entry.count_f
        self.counters['phrases']      -= main_entry.count_p
        self.counters['notes']        -= main_entry.count_n

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

        self.counters['translations'] += main_entry.count_t
        self.counters['forms']        += main_entry.count_f
        self.counters['phrases']      += main_entry.count_p
        self.counters['notes']        += main_entry.count_n

        self.delete_entry(entry_id_2)

    def add_tr(self, entry_id: EntryID, tr: Translation):
        """
        Add a translation to an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to add.
        """

        entry = self.entries[entry_id]
        self._update_index('translations', [tr], entry_id, 'add')
        self.counters['translations'] -= entry.count_t
        entry.add_tr(tr)
        self.counters['translations'] += entry.count_t

    def delete_tr(self, entry_id: EntryID, tr: Translation):
        """
        Delete a translation from an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to delete.
        """

        entry = self.entries[entry_id]
        self._update_index('translations', [tr], entry_id, 'remove')
        self.counters['translations'] -= entry.count_t
        entry.delete_tr(tr)
        self.counters['translations'] += entry.count_t

    def add_frm(self, entry_id: EntryID, pattern: FormPattern, frm: Form):
        """
        Add an inflected form to an entry.

        Args:
            entry_id: ID of the entry.
            pattern: Form pattern for the inflection.
            frm: The inflected form to add.
        """

        entry = self.entries[entry_id]
        self._update_index('forms', [frm], entry_id, 'add')
        self.counters['forms'] -= entry.count_f
        entry.add_frm(pattern, frm)
        self.counters['forms'] += entry.count_f

    def delete_frm(self, entry_id: EntryID, pattern: FormPattern):
        """
        Delete an inflected form from an entry.

        Args:
            entry_id: ID of the entry.
            pattern: Form pattern identifying the form to remove.
        """

        entry = self.entries[entry_id]
        self._update_index('forms', entry.forms.values(), entry_id, 'remove')  # Могут быть омоформы
        self.counters['forms'] -= entry.count_f
        entry.delete_frm(pattern)
        self.counters['forms'] += entry.count_f
        self._update_index('forms', entry.forms.values(), entry_id, 'add')

    def add_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        """
        Add a phrase with its translation to an entry.

        Args:
            entry_id: ID of the entry.
            phr: The phrase or usage example.
            phr_tr: Translation of the phrase.
        """

        entry = self.entries[entry_id]
        self.counters['phrases'] -= entry.count_p
        entry.add_phrase(phr, phr_tr)
        self.counters['phrases'] += entry.count_p

    def delete_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        """
        Delete a phrase and its translation from an entry.

        Args:
            entry_id: ID of the entry.
            phr: The phrase to remove.
            phr_tr: The translation of the phrase to remove.
        """

        entry = self.entries[entry_id]
        self.counters['phrases'] -= entry.count_p
        entry.delete_phrase(phr, phr_tr)
        self.counters['phrases'] += entry.count_p

    def add_note(self, entry_id: EntryID, note: Note):
        """
        Add a note to an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to add.
        """

        entry = self.entries[entry_id]
        self.counters['notes'] -= entry.count_n
        entry.add_note(note)
        self.counters['notes'] += entry.count_n

    def delete_note(self, entry_id: EntryID, note: Note):
        """
        Delete a note from an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to remove.
        """

        entry = self.entries[entry_id]
        self.counters['notes'] -= entry.count_n
        entry.delete_note(note)
        self.counters['notes'] += entry.count_n

    def add_entries_to_group(self, group: Group, entry_ids: Iterable[EntryID]):
        """
        Add multiple entries to a group.

        Args:
            group: Group name to add entries to.
            entry_ids: Iterable of entry IDs to add to the group.
        """

        for entry_id in entry_ids:
            self._update_index('groups', [group], entry_id, 'add')
            self.entries[entry_id].add_to_group(group)

    def remove_entries_from_group(self, group: Group, entry_ids: Iterable[EntryID]):
        """
        Remove multiple entries from a group.

        Args:
            group: Group name to remove entries from.
            entry_ids: Iterable of entry IDs to remove from the group.
        """

        for entry_id in entry_ids:
            if group in self.entries[entry_id].groups:
                self._update_index('groups', [group], entry_id, 'remove')
                self.entries[entry_id].remove_from_group(group)

    def fav_entries(self, entry_ids: Iterable[EntryID]):
        """
        Mark multiple entries as favorites.

        Args:
            entry_ids: Iterable of entry IDs to mark as favorites.
        """

        for entry_id in entry_ids:
            self.entries[entry_id].add_to_fav()

    def unfav_entries(self, entry_ids: Iterable[EntryID]):
        """
        Remove multiple entries from favorites.

        Args:
            entry_ids: Iterable of entry IDs to remove from favorites.
        """

        for entry_id in entry_ids:
            self.entries[entry_id].remove_from_fav()

    def add_ctg(self, ctg_name: Category, ctg_values: list[CtgValue]):
        """
        Add a new grammatical category to the dictionary.

        Adds an empty category position to all existing word forms in all entries.

        Args:
            ctg_name: Name of the new category.
            ctg_values: List of possible values for this category.
        """

        assert ctg_name not in self.features.keys()

        for entry in self.entries.values():
            entry.add_ctg()

        self.features[ctg_name] = ctg_values

    def delete_ctg(self, ctg_name: Category):
        """
        Delete a grammatical category from the dictionary.

        Removes the category from all word forms. Forms with non-empty values
        at this category position are deleted entirely.

        Args:
            ctg_name: Name of the category to delete.
        """

        assert ctg_name in self.features.keys()

        index = tuple(self.features.keys()).index(ctg_name)
        for entry_id, entry in self.entries.items():
            self._update_index('forms', entry.forms.values(), entry_id, 'remove')
            self.counters['forms'] -= entry.count_f
            entry.delete_ctg(index)
            self.counters['forms'] += entry.count_f
            self._update_index('forms', entry.forms.values(), entry_id, 'add')

        self.features.pop(ctg_name)

    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        """
        Rename a grammatical category.

        Args:
            ctg_name_old: Current name of the category.
            ctg_name_new: New name for the category.
        """

        assert ctg_name_old in self.features.keys()
        assert ctg_name_new not in self.features.keys()

        self.features[ctg_name_new] = self.features[ctg_name_old].copy()
        self.features.pop(ctg_name_old)

    def add_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Add a new value to a grammatical category.

        Args:
            ctg_name: Name of the category.
            ctg_value: New value to add to the category.
        """

        assert ctg_name in self.features.keys()
        assert ctg_value not in self.features[ctg_name]

        self.features[ctg_name] += [ctg_value]

    def delete_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Delete a value from a grammatical category.

        Removes all word forms that use this category value. If the category
        has no values left after deletion, the category itself is removed.

        Args:
            ctg_name: Name of the category.
            ctg_value: Value to remove from the category.
        """

        assert ctg_name in self.features.keys()
        assert ctg_value in self.features[ctg_name]

        index = tuple(self.features.keys()).index(ctg_name)
        for entry_id, entry in self.entries.items():
            self._update_index('forms', entry.forms.values(), entry_id, 'remove')
            self.counters['forms'] -= entry.count_f
            entry.delete_ctg_value(index, ctg_value)
            self.counters['forms'] += entry.count_f
            self._update_index('forms', entry.forms.values(), entry_id, 'add')

        self.features[ctg_name].remove(ctg_value)
        if len(self.features[ctg_name]) == 0:  # Если у категории не осталось значений, то она удаляется
            self.delete_ctg(ctg_name)

    def rename_ctg_value(self, ctg_name: Category, ctg_value_old: CtgValue, ctg_value_new: CtgValue):
        """
        Rename a value in a grammatical category.

        Updates all word forms that use the old value to use the new value.

        Args:
            ctg_name: Name of the category.
            ctg_value_old: Current value to be replaced.
            ctg_value_new: New value to replace the old one.
        """

        assert ctg_name in self.features.keys()
        assert ctg_value_old in self.features[ctg_name]
        assert ctg_value_new not in self.features[ctg_name]

        index = tuple(self.features.keys()).index(ctg_name)
        for entry in self.entries.values():
            entry.rename_ctg_value(index, ctg_value_old, ctg_value_new)

        index = self.features[ctg_name].index(ctg_value_old)
        self.features[ctg_name][index] = ctg_value_new

    def add_group(self, group: Group):
        """
        Add a new group to the dictionary.

        Args:
            group: Name of the group to add.
        """

        assert group not in self.groups

        self.groups += [group]

    def delete_group(self, group: Group):
        """
        Delete a group from the dictionary.

        Removes the group from all entries that belong to it.

        Args:
            group: Name of the group to delete.
        """

        assert group in self.groups

        for entry_id in self.indexes['groups'][group]:
            entry = self.entries[entry_id]
            self._update_index('groups', [group], entry_id, 'remove')
            entry.remove_from_group(group)
        self.groups.remove(group)

    def rename_group(self, group_old: Group, group_new: Group):
        """
        Rename a group.

        Updates all entries that belong to the old group to use the new name.

        Args:
            group_old: Current name of the group.
            group_new: New name for the group.
        """

        assert group_old in self.groups
        assert group_new not in self.groups

        self.groups += [group_new]
        for entry_id in self.indexes['groups'][group_old]:
            entry = self.entries[entry_id]
            entry.remove_from_group(group_old)
            entry.add_to_group(group_new)
        self.groups.remove(group_old)

        self.indexes['groups'][group_new] = self.indexes['groups'][group_old]
        del self.indexes['groups'][group_old]

    def serialize(self) -> dict[str, Any]:
        """
        Serialize the Dictionary to a dictionary format.

        Returns:
            Dictionary containing saving version and all dictionary data.
        """

        data = {
            'version': self.saving_version,
            'data': {
                'name': self.name,
                'entries': self.entries,
                'indexes': self.indexes,
                'counters': self.counters,
                'features': self.features,
                'groups': self.groups,
                'max_entry_id': self._max_entry_id,
            }
        }
        return data

    def deserialize(self, data: dict[str, Any]):
        """
        Deserialize Dictionary data from a dictionary format.

        Args:
            data: Dictionary containing saving version and dictionary data.
        """

        loaded_version = data.get('version', 1)
        data = data.get('data', {})

        self.name = data.get('name', '')
        self.entries = data.get('entries', {})
        self.indexes = data.get('indexes', {})
        self.counters = data.get('counters', {})
        self.features = data.get('features', {})
        self.groups = data.get('groups', [])
        self._max_entry_id = data.get('max_entry_id', 0)

    def print_out(self, filepath: str):
        """
        Print the dictionary to the specified file.

        Outputs a formatted representation of the entire dictionary.

        Args:
            filepath: The path to the text file. The file's contents will be overwritten.
        """

        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self.entries.values():
                entry.print_out(file)
                file.write('\n')


# Typing
Dictionaries = list[dict[str, Any]]


class Manager:
    """
    Manager for multiple dictionary instances.

    Handles opening, closing, switching between, and saving multiple dictionary files.
    Maintains a list of opened dictionaries and tracks the currently active one.
    """

    def __init__(self):
        """
        Initialize the dictionary manager.

        Creates an empty manager with no opened dictionaries.
        """

        self.opened_dct: Dictionaries = []
        self.current_dct: int | None = None
        self.allowed_file_ext = ('.pkl',)

    @property
    def dct(self) -> Dictionary | None:
        """
        Get the currently active dictionary.

        Returns:
            The currently active Dictionary instance, or None if no dictionary
            is currently active.
        """

        if self.current_dct is None:
            return None
        return self.opened_dct[self.current_dct]['dct']

    @property
    def filepath(self) -> str | None:
        """
        Get the file path of the currently active dictionary.

        Returns:
            File path of the current dictionary, or None if no dictionary is
            active or if it's a new unsaved dictionary.
        """

        if self.current_dct is None:
            return None
        return self.opened_dct[self.current_dct]['filepath']

    def create_dct(self, name: DctName):
        """
        Create a new empty dictionary and add it to the manager.

        Args:
            name: Name for the new dictionary.
        """

        dct = Dictionary(name)

        self.opened_dct.append({'dct': dct, 'filepath': None})
        self.current_dct = len(self.opened_dct) - 1

    def open_dct(self, filepath: str):
        """
        Open a dictionary from a file and add it to the manager.

        Args:
            filepath: Path to the dictionary file to open.

        Raises:
            AssertionError: If the file extension is not supported.
        """

        ext = os.path.splitext(filepath)[1]
        assert ext in self.allowed_file_ext, f'File extension "{ext}" not supported'

        with open(filepath, 'rb') as f:
            savedata = pickle.load(f)

        dct = Dictionary()
        dct.deserialize(savedata)

        self.opened_dct.append({'dct': dct, 'filepath': filepath})
        self.current_dct = len(self.opened_dct) - 1

    def switch_dct(self, dct_id: int):
        """
        Switch to a different dictionary as the active one.

        Args:
            dct_id: Index of the dictionary to make active.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct)

        self.current_dct = dct_id

    def close_dct(self, dct_id: int):
        """
        Close a dictionary and remove it from the manager.

        Updates the current dictionary index if necessary.

        Args:
            dct_id: Index of the dictionary to close.

        Raises:
            AssertionError: If the dictionary index is out of range.
        """

        assert 0 <= dct_id <= len(self.opened_dct)

        if len(self.opened_dct) == 1:
            self.current_dct = None
        elif dct_id < self.current_dct:
            self.current_dct -= 1

        del self.opened_dct[dct_id]

    def save_dct(self, dct_id: int, filepath: str | None = None):
        """
        Save a dictionary to a file.

        Args:
            dct_id: Index of the dictionary to save.
            filepath: Path where to save the dictionary. If None, uses the
                      dictionary's current filepath.

        Raises:
            AssertionError: If the dictionary index is out of range.
            ValueError: If no filepath is specified and the dictionary has none.
        """

        assert 0 <= dct_id <= len(self.opened_dct)

        if filepath is None:
            filepath = self.opened_dct[dct_id]['filepath']
            if filepath is None:
                raise ValueError('No filepath is specified')

        savedata = self.dct.serialize()

        with open(filepath, 'wb') as f:
            pickle.dump(savedata, f)

        self.opened_dct[dct_id]['filepath'] = filepath

    def rename_dict(self, dct_id: int, new_name: str):
        """
        Rename a dictionary.

        Args:
            dct_id: Index of the dictionary to rename.
            new_name: New name of the dictionary.
        """

        self.opened_dct[dct_id]['dct'].rename(new_name)

    def reorder(self, from_index: int, to_index: int):
        """
        Reorder opened dictionaries.

        Args:
            from_index: Index of the dictionary to move.
            to_index: New index of the dictionary.
        """

        target_dct = self.opened_dct[from_index]
        is_current = from_index == self.current_dct

        if not is_current and self.current_dct > from_index:
            self.current_dct -= 1

        del self.opened_dct[from_index]
        self.opened_dct = self.opened_dct[:to_index] + [target_dct] + self.opened_dct[to_index:]

        if is_current:
            self.current_dct = to_index
        elif self.current_dct > to_index:
            self.current_dct += 1

    def serialize(self) -> dict[str, Any]:
        """
        Serialize the manager state to a dictionary format.

        Returns:
            Dictionary containing manager data.
        """

        data = {
            'opened_dct': self.opened_dct,
            'current_dct': self.current_dct,
        }
        return data

    def deserialize(self, data: dict[str, Any]):
        """
        Deserialize manager state from a dictionary format.

        Args:
            data: Dictionary containing manager data.
        """

        self.opened_dct = data.get('opened_dct', [])
        self.current_dct = data.get('current_dct', None)


def pattern_to_str(pattern: FormPattern) -> str:
    """
    Convert a form pattern to a readable string.

    Joins non-empty category values with commas, skipping empty values.

    Args:
        pattern: Form pattern tuple containing category values.

    Returns:
        Comma-separated string of non-empty category values.
    """

    return ', '.join(token for token in pattern if token)
