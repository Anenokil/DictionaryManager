"""
Implements the Dictionary class which stores entries and maintains indexes.

Author: Anenokil
"""

from typing import Iterable, Generator, Mapping, Callable, Literal, Union, TypeVar
from functools import wraps
import re

from .types import (
    Word, Translation, Category, CtgValue, FormPattern, Form, Phrase,
    PhraseTr, Note, Group, Timestamp, EntryID, DctName, SerializedData,
)
from .entry import Entry, deserialize_entry

# Typing aliases used in the module
Entries = dict[EntryID, Entry]
Index = dict[str, set[EntryID]]
Indexes = dict[str, Index]
FeatureRegistry = dict[Category, list[CtgValue]]
GroupRegistry = list[Group]
GroupID = int
GroupIDs = set[GroupID]
Replacements = dict[str, str]
T = TypeVar('T')


class Dictionary:
    """
    A bilingual dictionary.

    Attributes:
    ----------
    - name: Dictionary name.

    Protected Attributes:
    --------------------
    - _name: Dictionary name.
    - _entries: The main dictionary data structure mapping entry IDs to Entry objects.
    - _indexes: Search indexes for fast entry lookup by content. Keys:

      - 'lemmas': Maps lemmas to entry IDs containing them.
      - 'translations': Maps translations to entry IDs containing them.
      - 'forms': Maps inflected forms to entry IDs containing them.
      - 'groups': Maps group names to entry IDs belonging to them.

    - _counters: Word counts statistics with keys:

      - 'lemmas': Total number of entries (lemmas) in the dictionary.
      - 'translations': Total number of translations across all entries in the dictionary.
      - 'forms': Total number of inflected forms across all entries in the dictionary.
      - 'phrases': Total number of phrase examples across all entries.
      - 'notes': Total number of notes across all entries.

    - _features: Collection of all grammatical categories and their values present in the dictionary.
    - _groups: All groups/tags assigned to entries across the entire dictionary.
      Used for organizing and grouping dictionary content.
    - _max_entry_id: Current maximum entry ID. Used to assign the next available ID to new entries
      (current max + 1).
    - _saving_version: The version of the data format used for serialization.
    """

    _schema_version = 1
    default_replacement_modifiers = (
        '', '\\', '/', '|', '`', "'", '"', '^', '<', '>',
        ':', '~', '+', '*', '_', '#', '%', '@', '&', '$',
    )

    def __init__(
            self,
            name: DctName = None,
            replacement_modifiers: Iterable[str] = default_replacement_modifiers
    ):
        """
        Initialize a dictionary.

        Args:
            name: The dictionary name.
        """

        assert all(len(modifier) <= 1 for modifier in replacement_modifiers)

        self._name = name
        self._entries: Entries = dict()
        self._indexes: Indexes = {
            'lemmas': {},
            'translations': {},
            'forms': {},
            'groups': {},
        }
        self._counters = {
            'lemmas': 0,
            'translations': 0,
            'forms': 0,
            'phrases': 0,
            'notes': 0,
        }
        self._features: FeatureRegistry = dict()
        self._groups: GroupRegistry = []
        self._default_group_ids: GroupIDs = set()
        self._replacement_modifiers = set(replacement_modifiers)
        self._input_replacements = {modifier+modifier: modifier for modifier in replacement_modifiers}
        self._max_entry_id = 0
        self._is_modified = True

    @staticmethod
    def _mark_modified(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._is_modified = True
            return result

        return wrapper

    @staticmethod
    def _replace(method: Callable) -> Callable:
        def process_one_arg(self: 'Dictionary', var: T) -> T:
            if isinstance(var, str):
                return self.apply_replacements(var)
            if isinstance(var, Generator):
                return (process_one_arg(self, item) for item in var)
            if isinstance(var, dict):
                return type(var)({process_one_arg(self, k): process_one_arg(self, v) for k, v in var.items()})
            if isinstance(var, Union[tuple, list, set]):
                return type(var)((process_one_arg(self, item) for item in var))
            return var

        @wraps(method)
        def wrapper(self: 'Dictionary', *args, **kwargs):
            processed_args = []
            for arg in args:
                processed_arg = process_one_arg(self, arg)
                processed_args.append(processed_arg)

            processed_kwargs = {}
            for arg_name, arg_value in kwargs.items():
                processed_kwarg_value = process_one_arg(self, arg_value)
                processed_kwargs[arg_name] = processed_kwarg_value

            return method(self, *processed_args, **processed_kwargs)

        return wrapper

    def mark_saved(self):
        self._is_modified = False

    @property
    def is_saved(self) -> bool:
        return not self._is_modified

    def __getitem__(self, item: EntryID) -> Entry:
        return self._entries[item]

    def _update_index(self,
                      index_name: str,
                      search_terms: str | Iterable[str],
                      entry_ids: EntryID | Iterable[EntryID],
                      action: Literal['add', 'remove']):
        """
        Update a search index by adding or removing an entry.

        Args:
            index_name: Name of the index to update ('lemmas', 'translations', 'forms', or 'groups').
            search_terms: One or more search terms to add to or remove from the index.
            entry_ids: One or more entry IDs to associate with the search terms.
            action: Either 'add' or 'remove'.
        """

        assert index_name in self._indexes.keys()
        assert action in ('add', 'remove')

        search_terms = {search_terms} if isinstance(search_terms, str) else set(search_terms)
        entry_ids = {entry_ids} if isinstance(entry_ids, EntryID) else set(entry_ids)

        index = self._indexes[index_name]

        if action == 'add':
            for term in search_terms:
                if term in index:
                    index[term].update(entry_ids)
                else:
                    index[term] = set(entry_ids)
        else:
            for term in search_terms:
                index[term].difference_update(entry_ids)
                if not index[term]:
                    index.pop(term)

    @_mark_modified
    def add_replacement(self, modifier: str, char: str, replacement: str):
        assert modifier in self._replacement_modifiers
        assert char not in self._replacement_modifiers
        assert len(char) == 1
        assert len(replacement) == 1

        self._input_replacements[modifier + char] = replacement

    @_mark_modified
    def delete_replacement(self, modifier: str, char: str):
        assert char != modifier

        del self._input_replacements[modifier + char]

    def apply_replacements(self, text: str):
        pattern = re.compile('|'.join(re.escape(key) for key in self._input_replacements.keys()))

        return pattern.sub(lambda match: self._input_replacements[match.group()], text)

    @property
    def name(self) -> DctName:
        return self._name

    @name.setter
    def name(self, new_name: DctName):
        self.rename(new_name)

    @_mark_modified
    @_replace
    def rename(self, new_name: DctName):
        """
        Rename a dictionary.

        Args:
            new_name: New name of the dictionary.
        """

        self._name = new_name

    @_replace
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
        for entry_id in self._indexes['groups'][group]:
            entry = self._entries[entry_id]
            count_e += 1
            count_t += entry.count_t
            count_f += entry.count_f
        return count_e, count_t, count_f

    @_replace
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
        if group is None:
            for entry in self._entries.values():
                if entry.fav:
                    count_e += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        else:
            for entry_id in self._indexes['groups'][group]:
                entry = self._entries[entry_id]
                if entry.fav:
                    count_e += 1
                    count_t += entry.count_t
                    count_f += entry.count_f
        return count_e, count_t, count_f

    def count(self, counter_name: str) -> int:
        if counter_name == 'groups':
            return len(self._groups)
        if counter_name == 'categories':
            return len(self._features)
        if counter_name == 'ctg_values':
            return sum(len(ctg_vals) for ctg_vals in self._features.values())
        return self._counters[counter_name]

    def score(self) -> tuple[int, int]:
        """
        Get the global count of correct attempts and total attempts across all entries.

        Returns:
            A tuple containing two integers:
            - Total number of correct attempts (wins) across all entries;
            - Total number of all learning attempts across all entries.
        """

        correct = sum(entry.correct_att for entry in self._entries.values())
        total = sum(entry.total_att for entry in self._entries.values())
        return correct, total

    def get_entry_ids(self) -> Generator[EntryID, None, None]:
        """
        Iterate over all entry keys in the dictionary.

        Yields:
            The next entry key in the dictionary.
        """

        yield from self._entries.keys()

    def get_entries(self) -> Generator[Entry, None, None]:
        """
        Iterate over all entries in the dictionary.

        Yields:
            The next entry in the dictionary.
        """

        yield from self._entries.values()

    @_replace
    def search(self, query: Iterable[tuple[str, str]]) -> set[EntryID]:
        """
        Search for entries across multiple indexes using the specified query conditions.

        Performs a logical AND search - returns entries that match ALL specified conditions.

        Args:
            query: Iterable of (index_name, search_term) pairs defining search conditions.
                   - index_name: Name of the index to search in. Valid values:
                     'lemmas', 'translations', 'forms', 'groups'.
                   - search_term: The search term to look for in the index.

        Returns:
            Set of entry IDs that satisfy ALL the specified search conditions.
            Returns empty set if no matches found or index doesn't contain the query.

        Raises:
            AssertionError: If index_name is not a valid index.
        """

        index_names = set(condition[0] for condition in query)
        unexpected_index_names = index_names - set(self._indexes.keys())
        assert not unexpected_index_names, f'No index named "{unexpected_index_names.pop()}"'

        results = []
        for index_name, search_term in query:
            index = self._indexes[index_name]
            if search_term in index:
                results.append(index[search_term])
        return set.intersection(*results) if results else set()

    @property
    def groups(self) -> GroupRegistry:
        return self._groups

    @property
    def default_groups(self) -> GroupRegistry:
        return [self._groups[i] for i in self._default_group_ids]

    @property
    def features(self) -> FeatureRegistry:
        return self._features

    @property
    def replacement_modifiers(self) -> set[str]:
        return self._replacement_modifiers

    @property
    def input_replacements(self) -> Replacements:
        return self._input_replacements

    @_mark_modified
    @_replace
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

        if groups is not None:
            default_groups = {self._groups[i] for i in self._default_group_ids}
            groups = set(groups).union(default_groups)

        self._entries[entry_id] = Entry(
            lemma, tr, forms, phrases, notes, groups, fav,
            total_att, correct_att, win_streak, latest_att_timestamp
        )
        entry = self._entries[entry_id]

        self._update_index('lemmas', entry.lemma, entry_id, 'add')
        self._update_index('translations', entry.tr, entry_id, 'add')
        self._update_index('forms', entry.forms.values(), entry_id, 'add')
        self._update_index('groups', entry.groups, entry_id, 'add')

        self._counters['lemmas'] += 1
        self._counters['translations'] += entry.count_t
        self._counters['forms']        += entry.count_f
        self._counters['phrases']      += entry.count_p
        self._counters['notes']        += entry.count_n

        return entry_id

    @_mark_modified
    def delete_entry(self, entry_id: EntryID):
        """
        Delete a dictionary entry.

        Removes the entry from the dictionary, updates all indexes, and
        adjusts counters accordingly.

        Args:
            entry_id: ID of the entry to delete.
        """

        entry = self._entries[entry_id]

        self._counters['lemmas'] -= 1
        self._counters['translations'] -= entry.count_t
        self._counters['forms']        -= entry.count_f
        self._counters['phrases']      -= entry.count_p
        self._counters['notes']        -= entry.count_n

        self._update_index('lemmas', entry.lemma, entry_id, 'remove')
        self._update_index('translations', entry.tr, entry_id, 'remove')
        self._update_index('forms', entry.forms.values(), entry_id, 'remove')
        self._update_index('groups', entry.groups, entry_id, 'remove')

        del self._entries[entry_id]

    @_mark_modified
    def merge_entries(self, entry_id_1: EntryID, entry_id_2: EntryID):
        """
        Merge two entries with the same word into one.

        Combines all data from the second entry into the first entry.
        The second entry is deleted after merging.

        Args:
            entry_id_1: ID of the main entry (will be kept).
            entry_id_2: ID of the entry to merge into the main entry (will be deleted).
        """

        main_entry = self._entries[entry_id_1]
        additional_entry = self._entries[entry_id_2]

        self._update_index('lemmas', additional_entry.lemma, entry_id_1, 'add')
        self._update_index('translations', additional_entry.tr, entry_id_1, 'add')
        self._update_index('forms', additional_entry.forms.values(), entry_id_1, 'add')
        self._update_index('groups', additional_entry.groups, entry_id_1, 'add')

        self._counters['translations'] -= main_entry.count_t
        self._counters['forms']        -= main_entry.count_f
        self._counters['phrases']      -= main_entry.count_p
        self._counters['notes']        -= main_entry.count_n

        for tr in additional_entry.tr:
            main_entry.add_tr(tr)
        for note in additional_entry.notes:
            main_entry.add_note(note)
        for phr_key in additional_entry.phrases.keys():
            for phr_tr in additional_entry.phrases[phr_key]:
                main_entry.add_phrase(phr_key, phr_tr)
        for form_pattern in additional_entry.forms.keys():
            form = additional_entry.forms[form_pattern]
            main_entry.add_form(form_pattern, form)
        if additional_entry.fav:
            main_entry.fav = True
        for group in additional_entry.groups:
            main_entry.groups.add(group)
        main_entry.total_att += additional_entry.total_att
        main_entry.correct_att += additional_entry.correct_att
        main_entry.win_streak += additional_entry.win_streak

        self._counters['translations'] += main_entry.count_t
        self._counters['forms']        += main_entry.count_f
        self._counters['phrases']      += main_entry.count_p
        self._counters['notes']        += main_entry.count_n

        self.delete_entry(entry_id_2)

    @_mark_modified
    @_replace
    def edit_lemma(self, entry_id: EntryID, new_lemma: Word):
        """
        Update the lemma of an existing dictionary entry.

        Replaces the current lemma with a new one and updates all relevant indexes
        to maintain search consistency.

        Args:
            entry_id: Unique identifier of the entry to modify.
            new_lemma: New lemma word to assign to the entry.

        Raises:
            KeyError: If no entry exists with the given entry_id.
        """

        old_lemma = self._entries[entry_id].lemma
        self._update_index('lemmas', old_lemma, entry_id, 'remove')
        self._entries[entry_id].lemma = new_lemma
        self._update_index('lemmas', new_lemma, entry_id, 'add')

    @_mark_modified
    @_replace
    def add_tr(self, entry_id: EntryID, tr: Translation):
        """
        Add a translation to an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to add.
        """

        entry = self._entries[entry_id]
        self._update_index('translations', tr, entry_id, 'add')
        self._counters['translations'] -= entry.count_t
        entry.add_tr(tr)
        self._counters['translations'] += entry.count_t

    @_mark_modified
    @_replace
    def delete_tr(self, entry_id: EntryID, tr: Translation):
        """
        Delete a translation from an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to delete.
        """

        entry = self._entries[entry_id]
        self._update_index('translations', tr, entry_id, 'remove')
        self._counters['translations'] -= entry.count_t
        entry.delete_tr(tr)
        self._counters['translations'] += entry.count_t

    @_mark_modified
    @_replace
    def add_form(self, entry_id: EntryID, pattern: FormPattern, form: Form):
        """
        Add an inflected form to an entry.

        Args:
            entry_id: ID of the entry.
            pattern: Form pattern for the inflection.
            form: The inflected form to add.
        """

        entry = self._entries[entry_id]
        self._update_index('forms', form, entry_id, 'add')
        self._counters['forms'] -= entry.count_f
        entry.add_form(pattern, form)
        self._counters['forms'] += entry.count_f

    @_mark_modified
    @_replace
    def delete_form(self, entry_id: EntryID, pattern: FormPattern):
        """
        Delete an inflected form from an entry.

        Args:
            entry_id: ID of the entry.
            pattern: Form pattern identifying the form to remove.
        """

        entry = self._entries[entry_id]
        # An entry may contain homographs
        # Therefore, we need to first remove all forms from the index, then add them back to the index
        self._update_index('forms', entry.forms.values(), entry_id, 'remove')
        self._counters['forms'] -= entry.count_f
        entry.delete_form(pattern)
        self._counters['forms'] += entry.count_f
        self._update_index('forms', entry.forms.values(), entry_id, 'add')

    @_mark_modified
    @_replace
    def add_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        """
        Add a phrase with its translation to an entry.

        Args:
            entry_id: ID of the entry.
            phr: The phrase or usage example.
            phr_tr: Translation of the phrase.
        """

        entry = self._entries[entry_id]
        self._counters['phrases'] -= entry.count_p
        entry.add_phrase(phr, phr_tr)
        self._counters['phrases'] += entry.count_p

    @_mark_modified
    @_replace
    def delete_phrase(self, entry_id: EntryID, phr: Phrase, phr_tr: PhraseTr):
        """
        Delete a phrase and its translation from an entry.

        Args:
            entry_id: ID of the entry.
            phr: The phrase to remove.
            phr_tr: The translation of the phrase to remove.
        """

        entry = self._entries[entry_id]
        self._counters['phrases'] -= entry.count_p
        entry.delete_phrase(phr, phr_tr)
        self._counters['phrases'] += entry.count_p

    @_mark_modified
    @_replace
    def add_note(self, entry_id: EntryID, note: Note):
        """
        Add a note to an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to add.
        """

        entry = self._entries[entry_id]
        self._counters['notes'] -= entry.count_n
        entry.add_note(note)
        self._counters['notes'] += entry.count_n

    @_mark_modified
    @_replace
    def delete_note(self, entry_id: EntryID, note: Note):
        """
        Delete a note from an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to remove.
        """

        entry = self._entries[entry_id]
        self._counters['notes'] -= entry.count_n
        entry.delete_note(note)
        self._counters['notes'] += entry.count_n

    @_mark_modified
    @_replace
    def add_entries_to_group(self, group: Group, entry_ids: Iterable[EntryID]):
        """
        Add multiple entries to a group.

        Args:
            group: Group name to add entries to.
            entry_ids: Iterable of entry IDs to add to the group.
        """

        for entry_id in entry_ids:
            self._update_index('groups', group, entry_id, 'add')
            self._entries[entry_id].add_to_group(group)

    @_mark_modified
    @_replace
    def remove_entries_from_group(self, group: Group, entry_ids: Iterable[EntryID]):
        """
        Remove multiple entries from a group.

        Args:
            group: Group name to remove entries from.
            entry_ids: Iterable of entry IDs to remove from the group.
        """

        for entry_id in entry_ids:
            if group in self._entries[entry_id].groups:
                self._update_index('groups', group, entry_id, 'remove')
                self._entries[entry_id].remove_from_group(group)

    @_mark_modified
    def fav_entries(self, entry_ids: Iterable[EntryID]):
        """
        Mark multiple entries as favorites.

        Args:
            entry_ids: Iterable of entry IDs to mark as favorites.
        """

        for entry_id in entry_ids:
            self._entries[entry_id].add_to_fav()

    @_mark_modified
    def unfav_entries(self, entry_ids: Iterable[EntryID]):
        """
        Remove multiple entries from favorites.

        Args:
            entry_ids: Iterable of entry IDs to remove from favorites.
        """

        for entry_id in entry_ids:
            self._entries[entry_id].remove_from_fav()

    @_mark_modified
    @_replace
    def add_ctg(self, ctg_name: Category, ctg_values: list[CtgValue]):
        """
        Add a new grammatical category to the dictionary.

        Adds an empty category position to all existing word forms in all entries.

        Args:
            ctg_name: Name of the new category.
            ctg_values: List of possible values for this category.
        """

        assert ctg_name not in self._features.keys()

        for entry in self._entries.values():
            entry.add_ctg()

        self._features[ctg_name] = ctg_values

    @_mark_modified
    def _delete_ctg(self, ctg_name: Category):
        assert ctg_name in self._features.keys()

        index = tuple(self._features.keys()).index(ctg_name)
        for entry_id, entry in self._entries.items():
            self._update_index('forms', entry.forms.values(), entry_id, 'remove')
            self._counters['forms'] -= entry.count_f
            entry.delete_ctg(index)
            self._counters['forms'] += entry.count_f
            self._update_index('forms', entry.forms.values(), entry_id, 'add')

        self._features.pop(ctg_name)

    @_replace
    def delete_ctg(self, ctg_name: Category):
        """
        Delete a grammatical category from the dictionary.

        Removes the category from all word forms. Forms with non-empty values
        at this category position are deleted entirely.

        Args:
            ctg_name: Name of the category to delete.
        """

        return self._delete_ctg(ctg_name)

    @_mark_modified
    @_replace
    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        """
        Rename a grammatical category.

        Args:
            ctg_name_old: Current name of the category.
            ctg_name_new: New name for the category.
        """

        assert ctg_name_old in self._features.keys()
        assert ctg_name_new not in self._features.keys()

        self._features[ctg_name_new] = self._features[ctg_name_old].copy()
        self._features.pop(ctg_name_old)

    @_mark_modified
    @_replace
    def add_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Add a new value to a grammatical category.

        Args:
            ctg_name: Name of the category.
            ctg_value: New value to add to the category.
        """

        assert ctg_name in self._features.keys()
        assert ctg_value not in self._features[ctg_name]

        self._features[ctg_name] += [ctg_value]

    @_mark_modified
    @_replace
    def delete_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Delete a value from a grammatical category.

        Removes all word forms that use this category value. If the category
        has no values left after deletion, the category itself is removed.

        Args:
            ctg_name: Name of the category.
            ctg_value: Value to remove from the category.
        """

        assert ctg_name in self._features.keys()
        assert ctg_value in self._features[ctg_name]

        index = tuple(self._features.keys()).index(ctg_name)
        for entry_id, entry in self._entries.items():
            self._update_index('forms', entry.forms.values(), entry_id, 'remove')
            self._counters['forms'] -= entry.count_f
            entry.delete_ctg_value(index, ctg_value)
            self._counters['forms'] += entry.count_f
            self._update_index('forms', entry.forms.values(), entry_id, 'add')

        self._features[ctg_name].remove(ctg_value)
        if len(self._features[ctg_name]) == 0:  # If a category has no values left, it is removed
            self._delete_ctg(ctg_name)

    @_mark_modified
    @_replace
    def rename_ctg_value(self, ctg_name: Category, ctg_value_old: CtgValue, ctg_value_new: CtgValue):
        """
        Rename a value in a grammatical category.

        Updates all word forms that use the old value to use the new value.

        Args:
            ctg_name: Name of the category.
            ctg_value_old: Current value to be replaced.
            ctg_value_new: New value to replace the old one.
        """

        assert ctg_name in self._features.keys()
        assert ctg_value_old in self._features[ctg_name]
        assert ctg_value_new not in self._features[ctg_name]

        index = tuple(self._features.keys()).index(ctg_name)
        for entry in self._entries.values():
            entry.rename_ctg_value(index, ctg_value_old, ctg_value_new)

        index = self._features[ctg_name].index(ctg_value_old)
        self._features[ctg_name][index] = ctg_value_new

    @_mark_modified
    @_replace
    def add_group(self, group: Group, is_default: bool = False):
        """
        Add a new group to the dictionary.

        Args:
            group: Name of the group to add.
            is_default: Whether the group is default.
        """

        assert group not in self._groups

        self._indexes['groups'][group] = set()
        self._groups += [group]

        if is_default:
            group_id = len(self._groups) - 1
            self._default_group_ids.add(group_id)

    @_mark_modified
    @_replace
    def delete_group(self, group: Group):
        """
        Delete a group from the dictionary.

        Removes the group from all entries that belong to it.

        Args:
            group: Name of the group to delete.
        """

        assert group in self._groups

        group_id = self._groups.index(group)
        self._default_group_ids = set.union(
            {g_id     for g_id in self._default_group_ids if g_id < group_id},
            {g_id - 1 for g_id in self._default_group_ids if g_id > group_id}
        )

        for entry_id in self._indexes['groups'][group]:
            entry = self._entries[entry_id]
            self._update_index('groups', group, entry_id, 'remove')
            entry.remove_from_group(group)
        del self._indexes['groups'][group]
        self._groups.remove(group)

    @_mark_modified
    @_replace
    def rename_group(self, group_old: Group, group_new: Group):
        """
        Rename a group.

        Updates all entries that belong to the old group to use the new name.

        Args:
            group_old: Current name of the group.
            group_new: New name for the group.
        """

        assert group_old in self._groups
        assert group_new not in self._groups

        group_id = self._groups.index(group_old)
        self._groups[group_id] = group_new

        for entry_id in self._indexes['groups'][group_old]:
            entry = self._entries[entry_id]
            entry.remove_from_group(group_old)
            entry.add_to_group(group_new)

        self._indexes['groups'][group_new] = self._indexes['groups'][group_old]
        del self._indexes['groups'][group_old]

    @_mark_modified
    @_replace
    def mark_group_as_default(self, group: Group):
        group_id = self._groups.index(group)
        self._default_group_ids.add(group_id)

    @_mark_modified
    @_replace
    def unmark_default_group(self, group: Group):
        group_id = self._groups.index(group)
        self._default_group_ids.discard(group_id)

    @_replace
    def is_default_group(self, group: Group) -> bool:
        group_id = self._groups.index(group)
        return group_id in self._default_group_ids

    def serialize(self, frmt: Literal['json', 'pickle']) -> SerializedData:
        """
        Serialize the Dictionary to a dictionary format.

        Args:
            frmt: The format to serialize the entry to (json, pickle).

        Returns:
            Dictionary containing saving version and all Dictionary data.
        """

        data = {
            'version': self._schema_version,
            'data': {
                'name': self._name,
                'entries': self._entries,
                'indexes': self._indexes,
                'counters': self._counters,
                'features': self._features,
                'groups': self._groups,
                'default_group_ids': self._default_group_ids,
                'replacement_modifiers': self._replacement_modifiers,
                'input_replacements': self.input_replacements,
                'max_entry_id': self._max_entry_id,
                'is_modified': self._is_modified,
            }
        }
        if frmt == 'pickle':
            return data

        data['data']['entries'] = {
            entry_id: entry.serialize(frmt)
            for entry_id, entry in self._entries.items()
        }
        data['data']['indexes'] = {
            index_name: {query: tuple(ids) for query, ids in index_data.items()}
            for index_name, index_data in self._indexes.items()
        }
        data['data']['default_group_ids'] = tuple(self._default_group_ids)
        data['data']['replacement_modifiers'] = tuple(self._replacement_modifiers)
        return data

    def deserialize(self, data: SerializedData):
        """
        Deserialize Dictionary data from a dictionary format.

        Args:
            data: Dictionary containing saving version and dictionary data.
        """

        #loaded_version = data.get('version')
        data = data.get('data')

        self._name = data.get('name')
        self._entries = {
            int(entry_id): deserialize_entry(entry_data)
            for entry_id, entry_data in data.get('entries').items()
        }
        self._indexes = {
            index_name: {
                query: {int(i) for i in ids}
                for query, ids in index_data.items()
            } for index_name, index_data in data.get('indexes').items()
        }
        self._counters = {
            name: int(num) for name, num in data.get('counters').items()
        }
        self._features = data.get('features')
        self._groups = data.get('groups')
        self._default_group_ids = {int(i) for i in data.get('default_group_ids')}
        self._replacement_modifiers = set(data.get('replacement_modifiers'))
        self._input_replacements = data.get('input_replacements')
        self._max_entry_id = int(data.get('max_entry_id'))
        self._is_modified = bool(data.get('is_modified'))

    def to_txt(self, filepath: str):
        """
        Print the dictionary to the specified file.

        Outputs a formatted representation of the entire dictionary.

        Args:
            filepath: The path to the text file. The file's contents will be overwritten.
        """

        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self._entries.values():
                file.write(str(entry))
                file.write('\n')
