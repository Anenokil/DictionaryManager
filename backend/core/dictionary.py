"""
Implements the Dictionary class which stores entries and maintains indexes.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Collection, Generator, Mapping, Callable, Literal
from itertools import chain
from functools import wraps

from .types import (
    Word, Translation, Category, CtgValue, GramForm, WordForm, Phrase,
    PhraseTr, Note, Tag, Timestamp, EntryID, DctName, SerializedData,
)
from .errors import DeserializationError
from .entry import Entry
from .utils import validate_required_fields, validate_field_type

# Typing aliases used in the module
Entries = dict[EntryID, Entry]
Index = dict[str, set[EntryID]]
Indexes = dict[str, Index]
FeatureRegistry = dict[Category, list[CtgValue]]
TagRegistry = list[Tag]
TagID = int
TagIDs = set[TagID]


class Dictionary:
    """
    A bilingual dictionary.

    Attributes:
    ----------
    - name: Dictionary name (read-write).
    - is_modified: True when the dictionary has unsaved changes.
    - features: All grammar categories and their values.
    - tags: All tags defined in the dictionary.
    - default_tags: Tags marked as default.
    - total_score: Pair; the global count of correct attempts
      and total attempts across all entries.
    """

    _schema_version = 1

    @staticmethod
    def _mark_modified(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._is_modified = True
            return result

        return wrapper

    def __init__(self, name: DctName = None):
        """
        Initialize a dictionary.

        Args:
            name: The dictionary name.
        """

        self._name = name

        # The main dictionary data structure mapping entry IDs to Entry objects
        self._entries: Entries = dict()

        # Search indexes for fast entry lookup by content
        self._indexes: Indexes = {
            'lemmas': {},
            'translations': {},
            'forms': {},
            'tags': {},
        }

        # Word counts statistics
        self._counters = {
            'lemmas': 0,
            'translations': 0,
            'gram_forms': 0,
            'word_forms': 0,
            'phrases': 0,
            'phrase_trs': 0,
            'notes': 0,
        }

        # Collection of all grammatical categories and their values present in the dictionary
        self._features: FeatureRegistry = dict()

        # All tags assigned to entries across the entire dictionary.
        # Used for organizing and grouping dictionary content.
        self._tags: TagRegistry = []

        # Tags that are marked as default
        self._default_tag_ids: TagIDs = set()

        # Current maximum entry ID.
        # Used to assign the next available ID to new entries (current max + 1).
        self._max_entry_id = 0

        self._is_modified = True

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Dictionary':
        """
        Deserialize Dictionary data from a JSON format.

        Args:
            data: Dictionary containing saving version and dictionary data.

        Returns:
            A Dictionary object.
        """

        dct = cls()
        dct.load_from_json_dict(data)
        return dct

    def __getitem__(self, key: EntryID) -> Entry:
        return self._entries[key]

    @property
    def name(self) -> DctName:
        return self._name

    @name.setter
    def name(self, new_name: DctName):
        self.rename(new_name)

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @property
    def features(self) -> FeatureRegistry:
        return self._features

    @property
    def tags(self) -> TagRegistry:
        return self._tags

    @property
    def default_tags(self) -> TagRegistry:
        return [self._tags[i] for i in self._default_tag_ids]

    @property
    def total_score(self) -> tuple[int, int]:
        """
        Get the global count of correct attempts and total attempts across all entries.

        Returns:
            A tuple containing two integers:
            - Total number of correct attempts (wins) across all entries;
            - Total number of all learning attempts across all entries.
        """

        correct = sum(entry.correct_att for entry in self._entries.values())
        total   = sum(entry.total_att   for entry in self._entries.values())
        return correct, total

    def mark_saved(self):
        self._is_modified = False

    def mark_modified(self):
        self._is_modified = True

    def rename(self, new_name: DctName):
        """
        Rename a dictionary.

        Args:
            new_name: New name of the dictionary.
        """

        if self._name == new_name:
            return

        self._name = new_name
        self._is_modified = True

    def count_by_tag(self, tag: Tag) -> tuple[int, int, int, int]:
        """
        Count the number of entries, translations, and inflected forms with the specified tag.

        Args:
            tag: The tag for which to count statistics.

        Returns:
            A tuple containing three integers:
            - Number of dictionary entries (lemmas) with the tag;
            - Total number of translations across all entries with the tag;
            - Total number of grammatical forms across all entries with the tag;
            - Total number of word forms across all entries with the tag.
        """

        n_entries = 0
        n_translations = 0
        n_gram_forms = 0
        n_word_forms = 0
        for entry_id in self._indexes['tags'][tag]:
            entry = self._entries[entry_id]
            n_entries += 1
            n_translations += entry.n_translations
            n_gram_forms += entry.n_gram_forms
            n_word_forms += entry.n_word_forms
        return n_entries, n_translations, n_gram_forms, n_word_forms

    def count_by_fav(self, tag: Tag | None = None) -> tuple[int, int, int, int]:
        """
        Count the number of favorite entries, their translations, and inflected forms.

        Args:
            tag: If specified, counts only favorite entries within the tag.
                 If None, counts all favorite entries in the dictionary.

        Returns:
            A tuple containing three integers:
            - Number of favorite dictionary entries (lemmas);
            - Total number of translations across favorite entries;
            - Total number of grammatical forms across favorite entries;
            - Total number of word forms across favorite entries.
        """

        n_entries = 0
        n_translations = 0
        n_gram_forms = 0
        n_word_forms = 0
        if tag is None:
            for entry in self._entries.values():
                if entry.is_fav:
                    n_entries += 1
                    n_translations += entry.n_translations
                    n_gram_forms += entry.n_gram_forms
                    n_word_forms += entry.n_word_forms
        else:
            for entry_id in self._indexes['tags'][tag]:
                entry = self._entries[entry_id]
                if entry.is_fav:
                    n_entries += 1
                    n_translations += entry.n_translations
                    n_gram_forms += entry.n_gram_forms
                    n_word_forms += entry.n_word_forms
        return n_entries, n_translations, n_gram_forms, n_word_forms

    def count(self, target: str) -> int:
        if target == 'tags':
            return len(self._tags)
        if target == 'categories':
            return len(self._features)
        if target == 'ctg_values':
            return sum(len(ctg_vals) for ctg_vals in self._features.values())
        return self._counters[target]

    def iter_entry_ids(self) -> Generator[EntryID, None, None]:
        """
        Iterate over all entry keys in the dictionary.

        Yields:
            The next entry key in the dictionary.
        """

        yield from self._entries.keys()

    def iter_entries(self) -> Generator[Entry, None, None]:
        """
        Iterate over all entries in the dictionary.

        Yields:
            The next entry in the dictionary.
        """

        yield from self._entries.values()

    def search(self, query: Collection[tuple[str, str]]) -> set[EntryID]:
        """
        Search for entries across multiple indexes using the specified query conditions.

        Performs a logical AND search - returns entries that match ALL specified conditions.

        Args:
            query: Collection of (index_name, search_term) pairs defining search conditions.
                   - index_name: Name of the index to search in. Valid values:
                     'lemmas', 'translations', 'forms', 'tags'.
                   - search_term: The search term to look for in the index.

        Returns:
            Set of entry IDs that satisfy ALL the specified search conditions.
            Returns empty set if no matches found or index doesn't contain the query.

        Raises:
            AssertionError: If index_name is not a valid index.
        """

        index_names = {condition[0] for condition in query}
        unexpected_index_names = index_names - set(self._indexes.keys())
        if unexpected_index_names:
            raise KeyError(f'No index named "{unexpected_index_names.pop()}"')

        results = []
        for index_name, search_term in query:
            index = self._indexes[index_name]
            if search_term in index:
                results.append(index[search_term])
        return set.intersection(*results) if results else set()

    @_mark_modified
    def add_entry(
            self,
            lemma: Word,
            tr: Translation | Iterable[Translation],
            forms: Mapping[GramForm, Iterable[WordForm]] | None = None,
            phrases: Mapping[Phrase, Iterable[PhraseTr]] | None = None,
            notes: Note | Iterable[Note] | None = None,
            tags: Iterable[Tag] | None = None,
            is_fav: bool = False,
            total_att: int = 0,
            correct_att: int = 0,
            win_streak: int = 0,
            latest_att_timestamp: Timestamp = (0, 0, 0),
    ) -> EntryID:
        """
        Add a new dictionary entry.

        Args:
            lemma: The lemma (canonical/dictionary form of the word).
            tr: One or more translations.
            forms: Inflected forms of the word (except the lemma).
            phrases: Phrases containing the word; usage examples.
            notes: Notes field.
            tags: Tags assigned to the entry.
            is_fav: Whether the entry is favorite.
            total_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            win_streak: Count of consecutive wins.
            latest_att_timestamp: Timestamp of the most recent answer.

        Returns:
            New entry ID.
        """

        if tags is not None:
            default_tags = {self._tags[i] for i in self._default_tag_ids}
            tags = set(tags).union(default_tags)

        self._max_entry_id += 1
        entry_id = self._max_entry_id

        self._entries[entry_id] = Entry(
            lemma, tr, forms, phrases, notes, tags, is_fav,
            total_att, correct_att, win_streak, latest_att_timestamp
        )
        entry = self._entries[entry_id]

        self._update_index('lemmas', entry.lemma, entry_id, 'add')
        self._update_index('translations', entry.tr, entry_id, 'add')
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'add')
        self._update_index('tags', entry.tags, entry_id, 'add')

        self._counters['lemmas']       += 1
        self._counters['translations'] += entry.n_translations
        self._counters['gram_forms']   += entry.n_gram_forms
        self._counters['word_forms']   += entry.n_word_forms
        self._counters['phrases']      += entry.n_phrases
        self._counters['phrase_trs']   += entry.n_phrase_translations
        self._counters['notes']        += entry.n_notes

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

        self._counters['lemmas']       -= 1
        self._counters['translations'] -= entry.n_translations
        self._counters['gram_forms']   -= entry.n_gram_forms
        self._counters['word_forms']   -= entry.n_word_forms
        self._counters['phrases']      -= entry.n_phrases
        self._counters['phrase_trs']   -= entry.n_phrase_translations
        self._counters['notes']        -= entry.n_notes

        self._update_index('lemmas', entry.lemma, entry_id, 'remove')
        self._update_index('translations', entry.tr, entry_id, 'remove')
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'remove')
        self._update_index('tags', entry.tags, entry_id, 'remove')

        del self._entries[entry_id]

    @_mark_modified
    def merge_entries(self, target_entry_id: EntryID, source_entry_id: EntryID):
        """
        Merge two entries with the same word into one.

        Combines all data from the source entry into the target entry.
        The source entry is deleted after merging.

        Args:
            target_entry_id: ID of the entry to merge into (will be kept).
            source_entry_id: ID of the entry to merge into the target entry (will be deleted).
        """

        target_entry = self._entries[target_entry_id]
        source_entry = self._entries[source_entry_id]

        self._update_index('lemmas', source_entry.lemma, target_entry_id, 'add')
        self._update_index('translations', source_entry.tr, target_entry_id, 'add')
        self._update_index('forms', chain(*source_entry.forms.values()), target_entry_id, 'add')
        self._update_index('tags', source_entry.tags, target_entry_id, 'add')

        self._counters['translations'] -= target_entry.n_translations
        self._counters['gram_forms']   -= target_entry.n_gram_forms
        self._counters['word_forms']   -= target_entry.n_word_forms
        self._counters['phrases']      -= target_entry.n_phrases
        self._counters['phrase_trs']   -= target_entry.n_phrase_translations
        self._counters['notes']        -= target_entry.n_notes

        target_entry.merge(source_entry)
        self.delete_entry(source_entry_id)

        self._counters['translations'] += target_entry.n_translations
        self._counters['gram_forms']   += target_entry.n_gram_forms
        self._counters['word_forms']   += target_entry.n_word_forms
        self._counters['phrases']      += target_entry.n_phrases
        self._counters['phrase_trs']   += target_entry.n_phrase_translations
        self._counters['notes']        += target_entry.n_notes

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

        if old_lemma == new_lemma:
            return

        self._entries[entry_id].lemma = new_lemma

        self._update_index('lemmas', old_lemma, entry_id, 'remove')
        self._update_index('lemmas', new_lemma, entry_id, 'add')

        self._is_modified = True

    def add_tr(self, entry_id: EntryID, tr: Translation):
        """
        Add a translation to an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to add.
        """

        entry = self._entries[entry_id]

        is_modified, counter_delta = entry.tr.add(tr)

        self._counters['translations'] += counter_delta
        self._update_index('translations', tr, entry_id, 'add')

        self._is_modified |= is_modified

    @_mark_modified
    def delete_tr(self, entry_id: EntryID, tr: Translation):
        """
        Delete a translation from an entry.

        Args:
            entry_id: ID of the entry.
            tr: Translation to delete.
        """

        entry = self._entries[entry_id]

        entry.tr.delete(tr)

        self._counters['translations'] -= 1
        self._update_index('translations', tr, entry_id, 'remove')

    def edit_tr(self, entry_id: EntryID, tr: Translation, new_tr: Translation):
        entry = self._entries[entry_id]

        is_modified, counter_delta = entry.tr.edit(tr, new_tr)

        self._counters['translations'] += counter_delta
        self._update_index('translations', tr, entry_id, 'remove')
        self._update_index('translations', new_tr, entry_id, 'add')

        self._is_modified |= is_modified

    def add_form(self, entry_id: EntryID, gram_form: GramForm, word_form: WordForm):
        """
        Add an inflected form to an entry.

        Args:
            entry_id: ID of the entry.
            gram_form: Grammatical form for the inflection.
            word_form: The inflected form to add.
        """

        entry = self._entries[entry_id]

        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms.add(gram_form, word_form)

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', word_form, entry_id, 'add')

        self._is_modified |= is_modified

    def delete_form(self, entry_id: EntryID, gram_form: GramForm, word_form: WordForm):
        """
        Delete an inflected form from an entry.

        Args:
            entry_id: ID of the entry.
            gram_form: Grammatical form identifying the form to remove.
            word_form: The actual inflected form to remove.
        """

        entry = self._entries[entry_id]

        # An entry may contain homographs
        # Therefore, we need to first remove all forms from the index, then add them back to the index
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'remove')

        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms.delete(gram_form, word_form)

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'add')

        self._is_modified |= is_modified

    def edit_form(
            self,
            entry_id: EntryID,
            gram_form: GramForm,
            word_form: WordForm,
            new_gram_form: GramForm,
            new_word_form: WordForm,
    ):
        entry = self._entries[entry_id]

        # An entry may contain homographs
        # Therefore, we need to first remove all forms from the index, then add them back to the index
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'remove')

        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms.edit(
            gram_form, word_form, new_gram_form, new_word_form
        )

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', chain(*entry.forms.values()), entry_id, 'add')

        self._is_modified |= is_modified

    def add_phrase(self, entry_id: EntryID, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Add a phrase with its translation to an entry.

        Args:
            entry_id: ID of the entry.
            phrase: The phrase or usage example.
            phrase_tr: Translation of the phrase.
        """

        entry = self._entries[entry_id]

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases.add(phrase, phrase_tr)

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def delete_phrase(self, entry_id: EntryID, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Delete a phrase and its translation from an entry.

        Args:
            entry_id: ID of the entry.
            phrase: The phrase to remove.
            phrase_tr: The translation of the phrase to remove.
        """

        entry = self._entries[entry_id]

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases.delete(phrase, phrase_tr)

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def edit_phrase(
            self,
            entry_id: EntryID,
            phrase: Phrase,
            phrase_tr: PhraseTr,
            new_phrase: Phrase,
            new_phrase_tr: PhraseTr,
    ):
        entry = self._entries[entry_id]

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases.edit(
            phrase, phrase_tr, new_phrase, new_phrase_tr
        )

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def add_note(self, entry_id: EntryID, note: Note):
        """
        Add a note to an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to add.
        """

        entry = self._entries[entry_id]

        is_modified, counter_delta = entry.notes.add(note)

        self._counters['notes'] += counter_delta

        self._is_modified |= is_modified

    @_mark_modified
    def delete_note(self, entry_id: EntryID, note: Note):
        """
        Delete a note from an entry.

        Args:
            entry_id: ID of the entry.
            note: Note text to remove.
        """

        entry = self._entries[entry_id]

        entry.notes.delete(note)

        self._counters['notes'] -= 1

    def edit_note(self, entry_id: EntryID, note: Note, new_note: Note):
        entry = self._entries[entry_id]

        is_modified, counter_delta = entry.notes.edit(note, new_note)

        self._counters['notes'] += counter_delta

        self._is_modified |= is_modified

    def add_tag_to_entries(self, tag: Tag, entry_ids: Iterable[EntryID]):
        """
        Assign a tag to multiple entries.

        Args:
            tag: The tag to assign to the entries.
            entry_ids: Iterable of entry IDs to assign the tag to.
        """

        if tag in self._tags:
            entry_ids_to_update = set(entry_ids).difference(self._indexes['tags'][tag])
        else:
            entry_ids_to_update = entry_ids

        if not entry_ids_to_update:
            return

        for entry_id in entry_ids_to_update:
            self._entries[entry_id].tags.add(tag)

        self._update_index('tags', tag, entry_ids_to_update, 'add')

        self._is_modified = True

    def remove_tag_from_entries(self, tag: Tag, entry_ids: Iterable[EntryID]):
        """
        Remove a tag from multiple entries.

        Args:
            tag: The tag to remove from the entries.
            entry_ids: Iterable of entry IDs to remove the tag from.
        """

        entry_ids_to_update = set(entry_ids).intersection(self._indexes['tags'][tag])

        if not entry_ids_to_update:
            return

        for entry_id in entry_ids_to_update:
            self._entries[entry_id].tags.delete(tag)

        self._update_index('tags', tag, entry_ids_to_update, 'remove')

        self._is_modified = True

    def add_to_fav(self, entry_ids: Iterable[EntryID]):
        """
        Mark multiple entries as favorites.

        Args:
            entry_ids: Iterable of entry IDs to mark as favorites.
        """

        for entry_id in entry_ids:
            if not self._entries[entry_id].is_fav:
                self._entries[entry_id].is_fav = True
                self._is_modified = True

    def remove_from_fav(self, entry_ids: Iterable[EntryID]):
        """
        Remove multiple entries from favorites.

        Args:
            entry_ids: Iterable of entry IDs to remove from favorites.
        """

        for entry_id in entry_ids:
            if self._entries[entry_id].is_fav:
                self._entries[entry_id].is_fav = False
                self._is_modified = True

    @_mark_modified
    def add_ctg(self, ctg_name: Category, ctg_values: list[CtgValue]):
        """
        Add a new grammatical category to the dictionary.

        Adds an empty category position to all existing word forms in all entries.

        Args:
            ctg_name: Name of the new category.
            ctg_values: List of possible values for this category.
        """

        if ctg_name in self._features.keys():
            raise ValueError(f'Category {ctg_name} already exists')

        for entry in self._entries.values():
            entry.forms.add_ctg()

        self._features[ctg_name] = ctg_values

    @_mark_modified
    def delete_ctg(self, ctg_name: Category):
        """
        Delete a grammatical category from the dictionary.

        Removes the category from all word forms. Forms with non-empty values
        at this category position are deleted entirely.

        Args:
            ctg_name: Name of the category to delete.
        """

        index = tuple(self._features.keys()).index(ctg_name)

        for entry_id, entry in self._entries.items():
            self._update_index('forms', chain(*entry.forms.values()), entry_id, 'remove')
            self._counters['gram_forms'] -= entry.n_gram_forms
            self._counters['word_forms'] -= entry.n_word_forms
            entry.forms.delete_ctg(index)
            self._counters['gram_forms'] += entry.n_gram_forms
            self._counters['word_forms'] += entry.n_word_forms
            self._update_index('forms', chain(*entry.forms.values()), entry_id, 'add')

        self._features.pop(ctg_name)

    @_mark_modified
    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        """
        Rename a grammatical category.

        Args:
            ctg_name_old: Current name of the category.
            ctg_name_new: New name for the category.
        """

        if ctg_name_new in self._features.keys():
            raise ValueError(f'Category {ctg_name_new} already exists')

        self._features[ctg_name_new] = self._features.pop(ctg_name_old)

    def add_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Add a new value to a grammatical category.

        Args:
            ctg_name: Name of the category.
            ctg_value: New value to add to the category.
        """

        if ctg_value in self._features[ctg_name]:
            return

        self._features[ctg_name].append(ctg_value)

        self._is_modified = True

    @_mark_modified
    def delete_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Delete a value from a grammatical category.

        Removes all word forms that use this category value. If the category
        has no values left after deletion, the category itself is removed.

        Args:
            ctg_name: Name of the category.
            ctg_value: Value to remove from the category.
        """

        index = tuple(self._features.keys()).index(ctg_name)

        for entry_id, entry in self._entries.items():
            self._update_index('forms', chain(*entry.forms.values()), entry_id, 'remove')
            self._counters['gram_forms'] -= entry.n_gram_forms
            self._counters['word_forms'] -= entry.n_word_forms
            entry.forms.delete_ctg_value(index, ctg_value)
            self._counters['gram_forms'] += entry.n_gram_forms
            self._counters['word_forms'] += entry.n_word_forms
            self._update_index('forms', chain(*entry.forms.values()), entry_id, 'add')

        self._features[ctg_name].remove(ctg_value)
        if len(self._features[ctg_name]) == 0:  # If a category has no values left, it is removed
            self.delete_ctg(ctg_name)

    @_mark_modified
    def rename_ctg_value(
            self,
            ctg_name: Category,
            ctg_value_old: CtgValue,
            ctg_value_new: CtgValue,
    ):
        """
        Rename a value in a grammatical category.

        Updates all word forms that use the old value to use the new value.

        Args:
            ctg_name: Name of the category.
            ctg_value_old: Current value to be replaced.
            ctg_value_new: New value to replace the old one.
        """

        if ctg_value_new in self._features[ctg_name]:
            raise ValueError(f'Category value {ctg_value_new} already exists')

        index_ctg = tuple(self._features.keys()).index(ctg_name)
        for entry in self._entries.values():
            entry.forms.rename_ctg_value(index_ctg, ctg_value_old, ctg_value_new)

        index_val = self._features[ctg_name].index(ctg_value_old)
        self._features[ctg_name][index_val] = ctg_value_new

    def add_tag(self, tag: Tag, is_default: bool = False):
        """
        Add a new tag to the dictionary.

        Args:
            tag: The tag to add.
            is_default: Whether the tag is default.
        """

        if tag in self._tags:
            return

        self._indexes['tags'][tag] = set()
        self._tags.append(tag)

        if is_default:
            tag_id = len(self._tags) - 1
            self._default_tag_ids.add(tag_id)

        self._is_modified = True

    @_mark_modified
    def delete_tag(self, tag: Tag):
        """
        Delete a tag from the dictionary.

        Removes the tag from all entries that.

        Args:
            tag: The tag to delete.
        """

        tag_id = self._tags.index(tag)
        self._default_tag_ids = set.union(
            {def_tag_id     for def_tag_id in self._default_tag_ids if def_tag_id < tag_id},
            {def_tag_id - 1 for def_tag_id in self._default_tag_ids if def_tag_id > tag_id}
        )

        entry_ids = self._indexes['tags'][tag]

        for entry_id in entry_ids:
            entry = self._entries[entry_id]
            entry.tags.delete(tag)

        self._update_index('tags', tag, entry_ids, 'remove')

        del self._indexes['tags'][tag]
        self._tags.remove(tag)

    def rename_tag(self, tag_old: Tag, tag_new: Tag):
        """
        Rename a tag.

        Updates all entries with the old tag to use the new name.

        Args:
            tag_old: The tag ro rename.
            tag_new: New tag name.
        """

        tag_id = self._tags.index(tag_old)

        if tag_old == tag_new:
            return

        for entry_id in self._indexes['tags'][tag_old]:
            entry = self._entries[entry_id]
            entry.tags.edit(tag_old, tag_new)

        if tag_new in self._tags:
            self._tags.remove(tag_old)
            self._default_tag_ids = set.union(
                {def_tag_id     for def_tag_id in self._default_tag_ids if def_tag_id < tag_id},
                {def_tag_id - 1 for def_tag_id in self._default_tag_ids if def_tag_id > tag_id}
            )

            self._indexes['tags'][tag_new].update(self._indexes['tags'][tag_old])
            del self._indexes['tags'][tag_old]
        else:
            self._tags[tag_id] = tag_new

            self._indexes['tags'][tag_new] = self._indexes['tags'][tag_old]
            del self._indexes['tags'][tag_old]

        self._is_modified = True

    def mark_tag_as_default(self, tag: Tag):
        tag_id = self._tags.index(tag)

        if tag_id in self._default_tag_ids:
            return

        self._default_tag_ids.add(tag_id)
        self._is_modified = True

    def unmark_default_tag(self, tag: Tag):
        tag_id = self._tags.index(tag)

        if tag_id not in self._default_tag_ids:
            return

        self._default_tag_ids.discard(tag_id)
        self._is_modified = True

    def is_default_tag(self, tag: Tag) -> bool:
        tag_id = self._tags.index(tag)
        return tag_id in self._default_tag_ids

    def to_json_dict(self) -> SerializedData:
        """
        Serialize the Dictionary to a JSON format.

        Returns:
            Dictionary containing saving version and all Dictionary data.
        """

        entries = {
            str(entry_id): entry.to_json_dict()
            for entry_id, entry in self._entries.items()
        }
        indexes = {
            index_name: {query: list(ids) for query, ids in index_data.items()}
            for index_name, index_data in self._indexes.items()
        }
        default_tag_ids = list(self._default_tag_ids)

        return {
            'version': self._schema_version,
            'data': {
                'name': self._name,
                'entries': entries,
                'indexes': indexes,
                'counters': self._counters,
                'features': self._features,
                'tags': self._tags,
                'default_tag_ids': default_tag_ids,
                'max_entry_id': self._max_entry_id,
                'is_modified': self._is_modified,
            }
        }

    def load_from_json_dict(self, data: SerializedData):
        """
        Deserialize Dictionary data from a JSON format.

        Args:
            data: Dictionary containing saving version and dictionary data.
        """

        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('indexes', 'counters', 'max_entry_id', 'is_modified')
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        indexes = data['indexes']
        counters = data['counters']
        max_entry_id = data['max_entry_id']
        is_modified = data['is_modified']

        # Read optional fields
        name = data.get('name', None)
        entries = data.get('entries', {})
        features = data.get('features', {})
        tags = data.get('tags', [])
        default_tag_ids = data.get('default_tag_ids', [])

        # Validate types
        validate_field_type('name', name, (str, NoneType))
        validate_field_type('entries', entries, dict[str, SerializedData])
        validate_field_type('indexes', indexes, dict[str, dict[str, list[int]]])
        validate_field_type('counters', counters, dict[str, int])
        validate_field_type('features', features, dict[str, list[str]])
        validate_field_type('tags', tags, list[str])
        validate_field_type('default_tag_ids', default_tag_ids, list[int])
        validate_field_type('max_entry_id', max_entry_id, int)
        validate_field_type('is_modified', is_modified, bool)

        # Convert types and values
        try:
            entries = {
                int(entry_id): Entry.from_json_dict(entry_data)
                for entry_id, entry_data in entries.items()
            }
        except ValueError as e:
            if 'invalid literal for int()' in str(e):
                raise DeserializationError('Entry IDs must be numeric.')
            raise

        indexes = {
            index_name: {
                query: set(ids)
                for query, ids in index_data.items()
            } for index_name, index_data in indexes.items()
        }

        default_tag_ids = set(default_tag_ids)

        # Set attributes
        self._name = name
        self._entries = entries
        self._indexes = indexes
        self._counters = counters
        self._features = features
        self._tags = tags
        self._default_tag_ids = default_tag_ids
        self._max_entry_id = max_entry_id
        self._is_modified = is_modified

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

    def _update_index(
            self,
            index_name: str,
            search_terms: str | Iterable[str],
            entry_ids: EntryID | Iterable[EntryID],
            action: Literal['add', 'remove'],
    ):
        """
        Update a search index by adding or removing an entry.

        Args:
            index_name: Name of the index to update ('lemmas', 'translations', 'forms', or 'tags').
            search_terms: One or more search terms to add to or remove from the index.
            entry_ids: One or more entry IDs to associate with the search terms.
            action: Either 'add' or 'remove'.
        """

        search_terms = {search_terms} if isinstance(search_terms, str) else set(search_terms)
        entry_ids = {entry_ids} if isinstance(entry_ids, EntryID) else set(entry_ids)

        index = self._indexes[index_name]

        if action == 'add':
            for term in search_terms:
                if term in index:
                    index[term].update(entry_ids)
                else:
                    index[term] = entry_ids
        else:
            for term in search_terms:
                index[term].difference_update(entry_ids)
                if not index[term]:
                    index.pop(term)
