"""
Implements the Dictionary class which stores Entries.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Iterator, Mapping, Callable, Literal
from itertools import chain
from functools import wraps
import uuid

from .types import (
    Word, Translation, Category, CtgValue, GramForm, WordForm, Phrase,
    PhraseTr, Note, Tag, Timestamp, DctName, SerializedData,
)
from .errors import BackendError
from .entry import Entry
from .utils import validate_required_fields, validate_field_type

# Typing aliases used in the module
Entries = list[Entry]
Index = dict[str, set[Entry]]
Indexes = dict[str, Index]
FeatureRegistry = dict[Category, list[CtgValue]]
TagRegistry = list[Tag]
TagID = int
TagIDs = set[TagID]


class InvalidVariantError(BackendError, KeyError): ...
class InvalidTranslationError(BackendError, KeyError): ...
class InvalidGramFormError(BackendError, KeyError): ...
class InvalidWordFormError(BackendError, KeyError): ...
class InvalidPhraseError(BackendError, KeyError): ...
class InvalidPhraseTrError(BackendError, KeyError): ...
class InvalidNoteError(BackendError, KeyError): ...
class InvalidTagError(BackendError, KeyError): ...
class InvalidCategoryError(BackendError, KeyError): ...
class CategoryExistsError(BackendError, ValueError): ...
class InvalidCtgValueError(BackendError, KeyError): ...
class CtgValueExistsError(BackendError, ValueError): ...


class Dictionary:
    """
    Bilingual dictionary.

    Attributes:
        name: Dictionary name.
        is_modified: True when the Dictionary has unsaved changes.
        features: All grammar categories and their values.
        tags: All tags defined in the Dictionary.
        default_tags: Tags marked as default. Default tags are automatically added to all newly
                      created Entries.
        total_score: Total correct and total attempts across all Entries, as a pair of ints.
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
        Initialize a Dictionary.

        Args:
            name: Dictionary name.
        """

        self._name = name

        self._id: str = ...
        self._set_id()

        # The main Dictionary data structure containing Entry objects
        self._entries: Entries = []

        # Search indexes for fast Entry lookup by content
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

        # Collection of all grammatical categories and their values present in the Dictionary
        self._features: FeatureRegistry = {}

        # All tags which can be assigned to Dictionary Entries.
        # Used for organizing and grouping Dictionary content.
        self._tags: TagRegistry = []

        # Tags that are marked as default
        self._default_tag_ids: TagIDs = set()

        self._is_modified = True

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Dictionary':
        """
        Deserialize Dictionary data from a JSON format.

        Args:
            data: Dict containing saving version and Dictionary data.

        Returns:
            Dictionary object.

        Raises:
            MissingFieldError: If any of the required fields are missing from the data.
            FieldTypeError: If any of fields has an unexpected type.
        """

        dct = cls()
        dct.load_from_json_dict(data)
        return dct

    def __getitem__(self, index: int) -> Entry:
        """
        Return the Entry with the given index.

        Args:
            index: Index of the Entry to retrieve.

        Returns:
            Entry object.

        Raises:
            IndexError: If the index is out of range.
        """

        return self._entries[index]

    def __iter__(self) -> Iterator[Entry]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def name(self) -> DctName:
        return self._name

    @name.setter
    def name(self, new_name: DctName):
        self.rename(new_name)

    @property
    def id(self) -> str:
        return self._id

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
    def default_tags(self) -> set[Tag]:
        return {self._tags[i] for i in self._default_tag_ids}

    @property
    def total_score(self) -> tuple[int, int]:
        """
        Get the global count of correct attempts and total attempts across all Entries.

        Returns:
            Pair (correct, all).
            - correct: Total number of correct attempts (wins) across all Entries.
            - all: Total number of all learning attempts across all Entries.
        """

        correct = sum(entry.correct_att for entry in self._entries)
        total   = sum(entry.total_att   for entry in self._entries)
        return correct, total

    def count(self, target: str) -> int:
        """
        Count the total number of objects of the given type across the Dictionary.

        Args:
            target: Object to count. Options: 'lemmas', 'translations', 'gram_forms', 'word_forms',
                    'phrases', 'phrase_trs', 'notes', 'tags', 'categories', 'ctg_values'.

        Returns:
            Total count of target objects across the entire Dictionary.

        Raises:
            KeyError: If an invalid target is specified.
        """

        if target == 'tags':
            return len(self._tags)
        if target == 'categories':
            return len(self._features)
        if target == 'ctg_values':
            return sum(len(ctg_vals) for ctg_vals in self._features.values())
        return self._counters[target]

    def count_forms_by_ctg(self, ctg: Category, ctg_value: CtgValue | None = None) -> tuple[int, int]:
        ctg_idx = list(self._features.keys()).index(ctg)

        if ctg_value is None:
            is_match = lambda gf: gf[ctg_idx] != ''
        else:
            is_match = lambda gf: gf[ctg_idx] == ctg_value

        n_gram_forms = 0
        n_word_forms = 0
        for entry in self._entries:
            for gram_form, word_forms in entry.forms.items():
                if is_match(gram_form):
                    n_gram_forms += 1
                    n_word_forms += len(word_forms)

        return n_gram_forms, n_word_forms

    def search(
            self,
            variants: list[str] | None = None,
            translations: list[str] | None = None,
            forms: list[str] | None = None,
            tags: list[str] | None = None,
    ) -> set[Entry]:
        """
        Search for Entries across multiple indexes using the specified query conditions.

        Performs a logical AND search - returns Entries that match ALL specified conditions.

        Args:
            lemma: Lemma to look for.
            translations: Translations to look for.
            forms: Word forms to look for.
            tags: Tags to look for.

        Returns:
            Set of Entry objects that satisfy ALL the specified search conditions.
            Returns empty set if no matches found.
        """

        query = {}
        if variants is not None:
            query['lemmas'] = variants
        if translations is not None:
            query['translations'] = translations
        if forms is not None:
            query['forms'] = forms
        if tags is not None:
            query['tags'] = tags

        results = set()
        for index_name, search_terms in query.items():
            index = self._indexes[index_name]
            for search_term in search_terms:
                found = index.get(search_term, set())
                if results:
                    results.intersection_update(found)
                else:
                    results = set(found)
        return results

    def mark_saved(self):
        self._is_modified = False

    def mark_modified(self):
        self._is_modified = True

    def rename(self, new_name: DctName):
        """
        Rename a Dictionary.

        Args:
            new_name: New name of the Dictionary.
        """

        if self._name == new_name:
            return

        self._name = new_name
        self._is_modified = True

    @_mark_modified
    def add_entry(
            self,
            lemma: Word | Iterable[Word],
            tr: Translation | Iterable[Translation],
            forms: Mapping[GramForm, Iterable[WordForm]] | None = None,
            phrases: Mapping[Phrase, Iterable[PhraseTr]] | None = None,
            notes: Note | Iterable[Note] | None = None,
            tags: Iterable[Tag] | None = None,
            is_fav: bool = False,
            img_fn: str | None = None,
            total_att: int = 0,
            correct_att: int = 0,
            win_streak: int = 0,
            latest_att_timestamp: Timestamp = (0, 0, 0),
            to_add_default_tags: bool = True,
    ) -> Entry:
        """
        Add a new Entry.

        Args:
            lemma: Lemma (canonical/dictionary form of the word).
            tr: One or more translations.
            forms: Inflected forms of the word (except the lemma).
            phrases: Phrases containing the word; usage examples.
            notes: Notes field.
            tags: Tags assigned to the Entry.
            is_fav: Whether the Entry is favorite.
            total_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            win_streak: Count of consecutive wins.
            latest_att_timestamp: Timestamp of the most recent answer.

        Returns:
            New Entry object.

        Raises:
            InvalidGramFormError: If invalid grammatical forms are specified.
            InvalidTagError: If invalid tags are specified.
        """

        if forms is not None:
            for gram_form in forms.keys():
                if len(gram_form) != len(self._features):
                    raise InvalidGramFormError(gram_form)
                for ctg_val, ctg in zip(gram_form, self._features):
                    if ctg_val not in self._features[ctg]:
                        raise InvalidGramFormError(ctg_val)

        tags = set() if tags is None else set(tags)
        invalid_tags = tags.difference(set(self._tags))
        if invalid_tags:
            raise InvalidTagError(*invalid_tags)
        if to_add_default_tags:
            tags.update(self.default_tags)

        new_entry = Entry(
            lemma, tr, forms, phrases, notes, tags, is_fav, img_fn,
            total_att, correct_att, win_streak, latest_att_timestamp,
        )
        self._entries.append(new_entry)

        self._update_index('lemmas', new_entry.variants, new_entry, 'add')
        self._update_index('translations', new_entry.tr, new_entry, 'add')
        self._update_index('forms', chain(*new_entry.forms.values()), new_entry, 'add')
        self._update_index('tags', new_entry.tags, new_entry, 'add')

        self._counters['lemmas']       += new_entry.n_variants
        self._counters['translations'] += new_entry.n_translations
        self._counters['gram_forms']   += new_entry.n_gram_forms
        self._counters['word_forms']   += new_entry.n_word_forms
        self._counters['phrases']      += new_entry.n_phrases
        self._counters['phrase_trs']   += new_entry.n_phrase_translations
        self._counters['notes']        += new_entry.n_notes

        return new_entry

    @_mark_modified
    def rewrite_entry(
            self,
            entry: Entry,
            lemma: Word | Iterable[Word],
            tr: Translation | Iterable[Translation],
            forms: Mapping[GramForm, Iterable[WordForm]],
            phrases: Mapping[Phrase, Iterable[PhraseTr]],
            notes: Note | Iterable[Note],
            tags: Iterable[Tag],
            is_fav: bool,
            img_fn: str | None,
    ):
        """
        Edit all fields of an Entry.

        Args:
            entry: Entry to edit.
            lemma: Lemma (canonical/dictionary form of the word); one or more spelling variants.
            tr: One or more translations.
            forms: Inflected forms of the word (except the lemma).
            phrases: Phrases containing the word; usage examples.
            notes: Notes field.
            tags: Tags assigned to the Entry.
            is_fav: Whether the Entry is favorite.

        Returns:
            New Entry object.

        Raises:
            InvalidGramFormError: If invalid grammatical forms are specified.
            InvalidTagError: If invalid tags are specified.
        """

        if forms is not ...:
            for gram_form in forms.keys():
                if len(gram_form) != len(self._features):
                    raise InvalidGramFormError(gram_form)
                for ctg_val, ctg in zip(gram_form, self._features):
                    if ctg_val != '' and ctg_val not in self._features[ctg]:
                        raise InvalidGramFormError(ctg_val)

        if tags is not ...:
            tags = set(tags)
            invalid_tags = tags.difference(set(self._tags))
            if invalid_tags:
                raise InvalidTagError(*invalid_tags)

        self._update_index('lemmas', entry.variants, entry, 'remove')
        self._update_index('translations', entry.tr, entry, 'remove')
        self._update_index('forms', chain(*entry.forms.values()), entry, 'remove')
        self._update_index('tags', entry.tags, entry, 'remove')

        self._counters['lemmas']       -= entry.n_variants
        self._counters['translations'] -= entry.n_translations
        self._counters['gram_forms']   -= entry.n_gram_forms
        self._counters['word_forms']   -= entry.n_word_forms
        self._counters['phrases']      -= entry.n_phrases
        self._counters['phrase_trs']   -= entry.n_phrase_translations
        self._counters['notes']        -= entry.n_notes

        entry._edit(lemma, tr, forms, phrases, notes, tags, is_fav, img_fn)

        self._update_index('lemmas', entry.variants, entry, 'add')
        self._update_index('translations', entry.tr, entry, 'add')
        self._update_index('forms', chain(*entry.forms.values()), entry, 'add')
        self._update_index('tags', entry.tags, entry, 'add')

        self._counters['lemmas']       += entry.n_variants
        self._counters['translations'] += entry.n_translations
        self._counters['gram_forms']   += entry.n_gram_forms
        self._counters['word_forms']   += entry.n_word_forms
        self._counters['phrases']      += entry.n_phrases
        self._counters['phrase_trs']   += entry.n_phrase_translations
        self._counters['notes']        += entry.n_notes

    @_mark_modified
    def delete_entry(self, entry: Entry):
        """
        Delete an Entry.

        Removes the Entry from the Dictionary, updates all indexes, and adjusts counters
        accordingly.

        Args:
            entry: Entry to delete.
        """

        self._counters['lemmas']       -= entry.n_variants
        self._counters['translations'] -= entry.n_translations
        self._counters['gram_forms']   -= entry.n_gram_forms
        self._counters['word_forms']   -= entry.n_word_forms
        self._counters['phrases']      -= entry.n_phrases
        self._counters['phrase_trs']   -= entry.n_phrase_translations
        self._counters['notes']        -= entry.n_notes

        self._update_index('lemmas', entry.variants, entry, 'remove')
        self._update_index('translations', entry.tr, entry, 'remove')
        self._update_index('forms', chain(*entry.forms.values()), entry, 'remove')
        self._update_index('tags', entry.tags, entry, 'remove')

        self._entries.remove(entry)

    @_mark_modified
    def merge_entries(self, target_entry: Entry, source_entry: Entry):
        """
        Merge two Entries with the same word into one.

        Combines all data from the source Entry into the target Entry.
        The source Entry is deleted after merging.

        Args:
            target_entry: Entry to merge into (will be kept).
            source_entry: Entry to merge into the target Entry (will be deleted).
        """

        self._update_index('lemmas', source_entry.variants, target_entry, 'add')
        self._update_index('translations', source_entry.tr, target_entry, 'add')
        self._update_index('forms', chain(*source_entry.forms.values()), target_entry, 'add')
        self._update_index('tags', source_entry.tags, target_entry, 'add')

        self._counters['translations'] -= target_entry.n_translations
        self._counters['gram_forms']   -= target_entry.n_gram_forms
        self._counters['word_forms']   -= target_entry.n_word_forms
        self._counters['phrases']      -= target_entry.n_phrases
        self._counters['phrase_trs']   -= target_entry.n_phrase_translations
        self._counters['notes']        -= target_entry.n_notes

        target_entry._merge(source_entry)
        self.delete_entry(source_entry)

        self._counters['translations'] += target_entry.n_translations
        self._counters['gram_forms']   += target_entry.n_gram_forms
        self._counters['word_forms']   += target_entry.n_word_forms
        self._counters['phrases']      += target_entry.n_phrases
        self._counters['phrase_trs']   += target_entry.n_phrase_translations
        self._counters['notes']        += target_entry.n_notes

    def add_variant(self, entry: Entry, variant: Word):
        """
        Add a spelling variant of the lemma to an Entry.

        Args:
            entry: Entry to add spelling variant to.
            variant: Spelling variant to add.
        """

        is_modified, counter_delta = entry.variants._add(variant)

        self._counters['lemmas'] += counter_delta
        self._update_index('lemmas', variant, entry, 'add')

        self._is_modified |= is_modified

    def edit_variant(self, entry: Entry, variant: Word, new_variant: Word):
        """
        Replace an existing spelling variant of the lemma with a new one.

        Args:
            entry: Entry to modify.
            variant: Spelling variant to replace.
            new_variant: New spelling variant.

        Raises:
            InvalidVariantError: If the Entry does not have the specified spelling variant.
        """

        if variant not in entry.variants:
            raise InvalidVariantError(variant)

        is_modified, counter_delta = entry.variants._edit(variant, new_variant)

        self._counters['lemmas'] += counter_delta
        self._update_index('lemmas', variant, entry, 'remove')
        self._update_index('lemmas', new_variant, entry, 'add')

        self._is_modified |= is_modified

    @_mark_modified
    def delete_variant(self, entry: Entry, variant: Word):
        """
        Delete a spelling variant of the lemma from an Entry.

        Args:
            entry: Entry to delete spelling variant from.
            variant: Spelling variant to delete.

        Raises:
            InvalidVariantError: If the Entry does not have the specified spelling variant.
        """

        if variant not in entry.variants:
            raise InvalidVariantError(variant)

        self._counters['lemmas'] -= 1
        self._update_index('lemmas', variant, entry, 'remove')

        entry.variants._delete(variant)

    def add_tr(self, entry: Entry, tr: Translation):
        """
        Add a translation to an Entry.

        Args:
            entry: Entry to add translation to.
            tr: Translation to add.
        """

        is_modified, counter_delta = entry.tr._add(tr)

        self._counters['translations'] += counter_delta
        self._update_index('translations', tr, entry, 'add')

        self._is_modified |= is_modified

    def edit_tr(self, entry: Entry, tr: Translation, new_tr: Translation):
        """
        Replace an existing translation with a new translation.

        Args:
            entry: Entry to modify.
            tr: Translation to replace.
            new_tr: New translation.

        Raises:
            InvalidTranslationError: If the Entry does not have the specified translation.
        """

        if tr not in entry.tr:
            raise InvalidTranslationError(tr)

        is_modified, counter_delta = entry.tr._edit(tr, new_tr)

        self._counters['translations'] += counter_delta
        self._update_index('translations', tr, entry, 'remove')
        self._update_index('translations', new_tr, entry, 'add')

        self._is_modified |= is_modified

    @_mark_modified
    def delete_tr(self, entry: Entry, tr: Translation):
        """
        Delete a translation from an Entry.

        Args:
            entry: Entry to delete translation from.
            tr: Translation to delete.

        Raises:
            InvalidTranslationError: If the Entry does not have the specified translation.
        """

        if tr not in entry.tr:
            raise InvalidTranslationError(tr)

        entry.tr._delete(tr)

        self._counters['translations'] -= 1
        self._update_index('translations', tr, entry, 'remove')

    def add_form(self, entry: Entry, gram_form: GramForm, word_form: WordForm):
        """
        Add an inflected form to an Entry.

        Args:
            entry: Entry to add form to.
            gram_form: Grammatical form for the inflection.
            word_form: Inflected form to add.
        """

        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms._add(gram_form, word_form)

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', word_form, entry, 'add')

        self._is_modified |= is_modified

    def edit_form(
            self,
            entry: Entry,
            gram_form: GramForm,
            word_form: WordForm,
            new_gram_form: GramForm,
            new_word_form: WordForm,
    ):
        """
        Edit grammatical or/and inflected form of an Entry.

        Args:
            entry: Entry to modify.
            gram_form: Grammatical form to edit.
            word_form: Inflected form to edit.
            new_gram_form: Replacement grammatical form.
            new_word_form: Replacement inflected form.

        Raises:
            InvalidGramFormError: If the specified gram_form is not found.
            InvalidWordFormError: If the specified word_form is not found.
        """

        if gram_form not in entry.forms:
            raise InvalidGramFormError(gram_form)
        if word_form not in entry.forms[gram_form]:
            raise InvalidWordFormError(word_form)

        # An Entry may contain homographs.
        # Therefore, we need to first remove all forms from the index, then add them back to the
        # index.
        to_rm_from_index = set(chain(*entry.forms.values()))
        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms._edit(
            gram_form, word_form, new_gram_form, new_word_form
        )
        to_rm_from_index.difference_update(*entry.forms.values())

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', to_rm_from_index, entry, 'add')

        self._is_modified |= is_modified

    def delete_form(self, entry: Entry, gram_form: GramForm, word_form: WordForm):
        """
        Delete an inflected form from an Entry.

        Args:
            entry: Entry to delete form from.
            gram_form: Grammatical form identifying the form to remove.
            word_form: Inflected form to remove.

        Raises:
            InvalidGramFormError: If the specified gram_form is not found.
            InvalidWordFormError: If the specified word_form is not found.
        """

        if gram_form not in entry.forms:
            raise InvalidGramFormError(gram_form)
        if word_form not in entry.forms[gram_form]:
            raise InvalidWordFormError(word_form)

        # An Entry may contain homographs.
        # Therefore, we need to first remove all forms from the index, then add them back to the
        # index.
        to_rm_from_index = set(chain(*entry.forms.values()))
        is_modified, cnt_delta_gram, cnt_delta_word = entry.forms._delete(gram_form, word_form)
        to_rm_from_index.difference_update(*entry.forms.values())

        self._counters['gram_forms'] += cnt_delta_gram
        self._counters['word_forms'] += cnt_delta_word
        self._update_index('forms', to_rm_from_index, entry, 'add')

        self._is_modified |= is_modified

    def add_phrase(self, entry: Entry, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Add a phrase with its translation to an Entry.

        Args:
            entry: Entry to add phrase to.
            phrase: Phrase to add.
            phrase_tr: Phrase translation to add.
        """

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases._add(phrase, phrase_tr)

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def edit_phrase(
            self,
            entry: Entry,
            phrase: Phrase,
            phrase_tr: PhraseTr,
            new_phrase: Phrase,
            new_phrase_tr: PhraseTr,
    ):
        """
        Edit a phrase or/and its translation.

        Args:
            entry: Entry to modify.
            phrase: Phrase to edit.
            phrase_tr: Phrase translation to edit.
            new_phrase: Replacement phrase.
            new_phrase_tr: Replacement phrase translation.

        Raises:
            InvalidPhraseError: If the specified phrase is not found.
            InvalidPhraseTrError: If the specified phrase_tr is not found.
        """

        if phrase not in entry.phrases:
            raise InvalidPhraseError(phrase)
        if phrase_tr not in entry.phrases[phrase]:
            raise InvalidPhraseTrError(phrase_tr)

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases._edit(
            phrase, phrase_tr, new_phrase, new_phrase_tr
        )

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def delete_phrase(self, entry: Entry, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Delete a phrase and its translation from an Entry.

        Args:
            entry: Entry to delete phrase from.
            phrase: Phrase to remove.
            phrase_tr: Phrase translation to remove.

        Raises:
            InvalidPhraseError: If the specified phrase is not found.
            InvalidPhraseTrError: If the specified phrase_tr is not found.
        """

        if phrase not in entry.phrases:
            raise InvalidPhraseError(phrase)
        if phrase_tr not in entry.phrases[phrase]:
            raise InvalidPhraseTrError(phrase_tr)

        is_modified, cnt_delta_ph, cnt_delta_tr = entry.phrases._delete(phrase, phrase_tr)

        self._counters['phrases']    += cnt_delta_ph
        self._counters['phrase_trs'] += cnt_delta_tr

        self._is_modified |= is_modified

    def add_note(self, entry: Entry, note: Note):
        """
        Add a note to an Entry.

        Args:
            entry: Entry to add note to.
            note: Note text to add.
        """

        is_modified, counter_delta = entry.notes._add(note)

        self._counters['notes'] += counter_delta

        self._is_modified |= is_modified

    def edit_note(self, entry: Entry, note: Note, new_note: Note):
        """
        Edit a note

        Args:
            entry: Entry to modify.
            note: Note to edit.
            new_note: Replacement note.

        Raises:
            InvalidNoteError: If the specified note is not found.
        """

        if note not in entry.notes:
            raise InvalidNoteError(note)

        is_modified, counter_delta = entry.notes._edit(note, new_note)

        self._counters['notes'] += counter_delta

        self._is_modified |= is_modified

    @_mark_modified
    def delete_note(self, entry: Entry, note: Note):
        """
        Delete a note from an Entry.

        Args:
            entry: Entry to delete note from.
            note: Note text to remove.

        Raises:
            InvalidNoteError: If the specified note is not found.
        """

        if note not in entry.notes:
            raise InvalidNoteError(note)

        entry.notes._delete(note)

        self._counters['notes'] -= 1

    def add_tag_to_entries(self, tag: Tag, entries: Iterable[Entry]):
        """
        Assign a tag to multiple Entries.

        Args:
            tag: Tag to assign to the Entries.
            entries: Iterable of Entry objects to assign the tag to.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        entries_to_update = set(entries).difference(self._indexes['tags'][tag])

        if not entries_to_update:
            return

        for entry in entries_to_update:
            entry.tags._add(tag)

        self._update_index('tags', tag, entries_to_update, 'add')

        self._is_modified = True

    def remove_tag_from_entries(self, tag: Tag, entries: Iterable[Entry]):
        """
        Remove a tag from multiple Entries.

        Args:
            tag: Tag to remove from the Entries.
            entries: Iterable of Entry objects to remove the tag from.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        entries_to_update = set(entries).intersection(self._indexes['tags'][tag])

        if not entries_to_update:
            return

        for entry in entries_to_update:
            entry.tags._delete(tag)

        self._update_index('tags', tag, entries_to_update, 'remove')

        self._is_modified = True

    def add_to_fav(self, entries: Iterable[Entry]):
        """
        Mark multiple Entries as favorites.

        Args:
            entries: Iterable of Entry objects to mark as favorites.
        """

        for entry in entries:
            if not entry.is_fav:
                entry.is_fav = True
                self._is_modified = True

    def remove_from_fav(self, entries: Iterable[Entry]):
        """
        Remove multiple Entries from favorites.

        Args:
            entries: Iterable of Entry objects to remove from favorites.
        """

        for entry in entries:
            if entry.is_fav:
                entry.is_fav = False
                self._is_modified = True

    @_mark_modified
    def register_correct_answer(self, entry: Entry, timestamp: Timestamp):
        entry._register_correct_answer(timestamp)

    @_mark_modified
    def register_incorrect_answer(self, entry: Entry, timestamp: Timestamp):
        entry._register_incorrect_answer(timestamp)

    def reset_stats(self, entry: Entry):
        if entry.total_att == 0:
            return

        entry._reset_stats()
        self._is_modified = True

    @_mark_modified
    def add_ctg(self, ctg_name: Category, ctg_values: list[CtgValue]):
        """
        Add a new grammatical category to the Dictionary.

        Adds an empty category position to all existing word forms in all Entries.

        Args:
            ctg_name: Name of the new category.
            ctg_values: List of possible values for this category.

        Raises:
            CategoryExistsError: If the specified category is already in the Dictionary.
        """

        if ctg_name in self._features.keys():
            raise CategoryExistsError(ctg_name)

        for entry in self._entries:
            entry.forms._add_ctg()

        self._features[ctg_name] = ctg_values

    @_mark_modified
    def rename_ctg(self, ctg_name_old: Category, ctg_name_new: Category):
        """
        Rename a grammatical category.

        Args:
            ctg_name_old: Current name of the category.
            ctg_name_new: New name for the category.

        Raises:
            InvalidCategoryError: If the specified category does not exist.
            CategoryExistsError: If the specified new name already exists.
        """

        if ctg_name_old not in self._features.keys():
            raise InvalidCategoryError(ctg_name_old)
        if ctg_name_new in self._features.keys():
            raise CategoryExistsError(ctg_name_new)

        self._features[ctg_name_new] = self._features.pop(ctg_name_old)

    def rename_ctgs(self, renames: Mapping[Category, Category]):
        temp_names = {}

        for old in renames:
            temp_name = f'__tmp_{uuid.uuid4().hex}__'
            temp_names[old] = temp_name
            self.rename_ctg(old, temp_name)

        for old, new in renames.items():
            self.rename_ctg(temp_names[old], new)

    @_mark_modified
    def delete_ctg(self, ctg_name: Category):
        """
        Delete a grammatical category from the Dictionary.

        Removes the category from all word forms. Forms with non-empty values at this category
        position are deleted entirely.

        Args:
            ctg_name: Name of the category to delete.

        Raises:
            InvalidCategoryError: If the specified category does not exist.
        """

        if ctg_name not in self._features.keys():
            raise InvalidCategoryError(ctg_name)

        index = tuple(self._features.keys()).index(ctg_name)

        self._features.pop(ctg_name)

        for entry in self._entries:
            self._update_index('forms', chain(*entry.forms.values()), entry, 'remove')
            self._counters['gram_forms'] -= entry.n_gram_forms
            self._counters['word_forms'] -= entry.n_word_forms
            entry.forms._delete_ctg(index)
            self._counters['gram_forms'] += entry.n_gram_forms
            self._counters['word_forms'] += entry.n_word_forms
            self._update_index('forms', chain(*entry.forms.values()), entry, 'add')

    def add_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Add a new value to a grammatical category.

        Args:
            ctg_name: Name of the category.
            ctg_value: New value to add to the category.

        Raises:
            InvalidCategoryError: If the specified category does not exist.
        """

        if ctg_name not in self._features:
            raise InvalidCategoryError(ctg_name)

        if ctg_value in self._features[ctg_name]:
            return

        self._features[ctg_name].append(ctg_value)

        self._is_modified = True

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

        Raises:
            InvalidCategoryError: If the specified category does not exist.
            InvalidCtgValueError: If the specified category value does not exist.
            CtgValueExistsError: If the new value already exists.
        """

        if ctg_name not in self._features:
            raise InvalidCategoryError(ctg_name)
        if ctg_value_old not in self._features[ctg_name]:
            raise InvalidCtgValueError(ctg_value_old)
        if ctg_value_new in self._features[ctg_name]:
            raise CtgValueExistsError(ctg_value_new)

        index_ctg = tuple(self._features.keys()).index(ctg_name)
        index_val = self._features[ctg_name].index(ctg_value_old)

        self._features[ctg_name][index_val] = ctg_value_new

        for entry in self._entries:
            entry.forms._rename_ctg_value(index_ctg, ctg_value_old, ctg_value_new)

    def rename_ctg_values(self, renames: Mapping[tuple[Category, CtgValue], CtgValue]):
        temp_names = {}

        for ctg, old in renames:
            temp_name = f'__tmp_{uuid.uuid4().hex}__'
            temp_names[ctg, old] = temp_name
            self.rename_ctg_value(ctg, old, temp_name)

        for (ctg, old), new in renames.items():
            self.rename_ctg_value(ctg, temp_names[ctg, old], new)

    @_mark_modified
    def delete_ctg_value(self, ctg_name: Category, ctg_value: CtgValue):
        """
        Delete a value from a grammatical category.

        Removes all word forms that use this category value.
        If the category has no values left after deletion, the category itself is removed.

        Args:
            ctg_name: Name of the category.
            ctg_value: Value to remove from the category.

        Raises:
            InvalidCategoryError: If the specified category does not exist.
            InvalidCtgValueError: If the specified category value does not exist.
        """

        if ctg_name not in self._features:
            raise InvalidCategoryError(ctg_name)
        if ctg_value not in self._features[ctg_name]:
            raise InvalidCtgValueError(ctg_value)

        if self._features[ctg_name] == [ctg_value]:
            self.delete_ctg(ctg_name)
        else:
            index = tuple(self._features.keys()).index(ctg_name)

            self._features[ctg_name].remove(ctg_value)

            for entry in self._entries:
                self._update_index('forms', chain(*entry.forms.values()), entry, 'remove')
                self._counters['gram_forms'] -= entry.n_gram_forms
                self._counters['word_forms'] -= entry.n_word_forms
                entry.forms._delete_ctg_value(index, ctg_value)
                self._counters['gram_forms'] += entry.n_gram_forms
                self._counters['word_forms'] += entry.n_word_forms
                self._update_index('forms', chain(*entry.forms.values()), entry, 'add')

    def add_tag(self, tag: Tag, is_default: bool = False):
        """
        Add a new tag to the Dictionary.

        If the tag already exists in the Dictionary, no changes are made.

        Args:
            tag: Tag to add.
            is_default: Whether the tag is default.
        """

        if tag in self._tags:
            tag_id = self._tags.index(tag)
            if is_default == (tag_id in self._default_tag_ids):
                return

            if is_default:
                self._default_tag_ids.add(tag_id)
            else:
                self._default_tag_ids.discard(tag_id)
        else:
            self._indexes['tags'][tag] = set()
            self._tags.append(tag)

            if is_default:
                tag_id = len(self._tags) - 1
                self._default_tag_ids.add(tag_id)

        self._is_modified = True

    def rename_tag(self, tag_old: Tag, tag_new: Tag):
        """
        Rename a tag.

        Updates all Entries with the old tag to use the new name.

        Args:
            tag_old: Tag to rename.
            tag_new: New tag name.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag_old not in self._tags:
            raise InvalidTagError(tag_old)

        if tag_old == tag_new:
            return

        for entry in self._indexes['tags'][tag_old]:
            entry.tags._edit(tag_old, tag_new)

        tag_id = self._tags.index(tag_old)

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

    def rename_tags(self, renames: Mapping[Tag, Tag]):
        temp_names = {}

        for old in renames:
            temp_name = f'__tmp_{uuid.uuid4().hex}__'
            temp_names[old] = temp_name
            self.rename_tag(old, temp_name)

        for old, new in renames.items():
            self.rename_tag(temp_names[old], new)

    @_mark_modified
    def delete_tag(self, tag: Tag):
        """
        Delete a tag from the Dictionary.

        Removes the tag from all Entries it was assigned to.

        Args:
            tag: Tag to delete.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        tag_id = self._tags.index(tag)
        self._default_tag_ids = set.union(
            {def_tag_id     for def_tag_id in self._default_tag_ids if def_tag_id < tag_id},
            {def_tag_id - 1 for def_tag_id in self._default_tag_ids if def_tag_id > tag_id}
        )

        entries = self._indexes['tags'][tag]

        for entry in entries:
            entry.tags._delete(tag)

        self._update_index('tags', tag, entries, 'remove')

        self._tags.remove(tag)

    def mark_tag_as_default(self, tag: Tag):
        """
        Mark the given tag as default.

        Default tags are automatically added to all newly created Entries.

        Args:
            tag: Tag to mark as default.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        tag_id = self._tags.index(tag)

        if tag_id in self._default_tag_ids:
            return

        self._default_tag_ids.add(tag_id)
        self._is_modified = True

    def unmark_tag_as_default(self, tag: Tag):
        """
        Unmark the given tag as default.

        The tag will no longer be automatically added to newly created Entries.

        Args:
            tag: Tag to unmark as default.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        tag_id = self._tags.index(tag)

        if tag_id not in self._default_tag_ids:
            return

        self._default_tag_ids.discard(tag_id)
        self._is_modified = True

    def is_default_tag(self, tag: Tag) -> bool:
        """
        Check if the given tag is default.

        Args:
            tag: Tag to check.

        Returns:
            True if the specified tag is default.

        Raises:
            InvalidTagError: If the specified tag does not exist.
        """

        if tag not in self._tags:
            raise InvalidTagError(tag)

        tag_id = self._tags.index(tag)
        return tag_id in self._default_tag_ids

    def to_txt(self, filepath: str):
        """
        Print the Dictionary to the specified file.

        Outputs a formatted representation of the entire Dictionary.

        Args:
            filepath: Path to the text file. The file's contents will be overwritten.
        """

        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in self._entries:
                file.write(str(entry))
                file.write('\n')

    def to_dict(self) -> SerializedData:
        """
        Serialize the Dictionary to a JSON format.

        Returns:
            Dict containing saving version and all Dictionary data.
        """

        entries = [entry.to_dict() for entry in self._entries]
        indexes = {
            index_name: {
                query: [self._entries.index(entry) for entry in entries]
                for query, entries in index_data.items()
            } for index_name, index_data in self._indexes.items()
        }
        default_tag_ids = list(self._default_tag_ids)

        return {
            'version': self._schema_version,
            'data': {
                'name': self._name,
                'id': self._id,
                'entries': entries,
                'indexes': indexes,
                'counters': self._counters,
                'features': self._features,
                'tags': self._tags,
                'default_tag_ids': default_tag_ids,
                'is_modified': self._is_modified,
            }
        }

    def load_from_json_dict(self, data: SerializedData):
        """
        Deserialize Dictionary data from a JSON format.

        Args:
            data: Dict containing saving version and Dictionary data.

        Raises:
            MissingFieldError: If any of the required fields are missing from the data.
            FieldTypeError: If any of fields has an unexpected type.
        """

        # Validate required fields
        required_fields = ('version', 'data')
        validate_required_fields(data, required_fields)

        required_fields = ('id', 'indexes', 'counters', 'is_modified')
        validate_required_fields(data['data'], required_fields)

        # Read required fields
        data = data['data']
        dct_id = data['id']
        indexes = data['indexes']
        counters = data['counters']
        is_modified = data['is_modified']

        # Read optional fields
        name = data.get('name', None)
        entries = data.get('entries', [])
        features = data.get('features', {})
        tags = data.get('tags', [])
        default_tag_ids = data.get('default_tag_ids', [])

        # Validate types
        validate_field_type('name', name, (str, NoneType))
        validate_field_type('id', dct_id, str)
        validate_field_type('entries', entries, list[SerializedData])
        validate_field_type('indexes', indexes, dict[str, dict[str, list[int]]])
        validate_field_type('counters', counters, dict[str, int])
        validate_field_type('features', features, dict[str, list[str]])
        validate_field_type('tags', tags, list[str])
        validate_field_type('default_tag_ids', default_tag_ids, list[int])
        validate_field_type('is_modified', is_modified, bool)

        # Convert types and values
        entries = [Entry.from_json_dict(entry_data) for entry_data in entries]

        indexes = {
            index_name: {
                query: {entries[index] for index in indexes}
                for query, indexes in index_data.items()
            } for index_name, index_data in indexes.items()
        }

        default_tag_ids = set(default_tag_ids)

        # Set attributes
        self._name = name
        self._id = dct_id
        self._entries = entries
        self._indexes = indexes
        self._counters = counters
        self._features = features
        self._tags = tags
        self._default_tag_ids = default_tag_ids
        self._is_modified = is_modified

    def _set_id(self):
        self._id = str(uuid.uuid4())

    def _update_index(
            self,
            index_name: str,
            search_terms: str | Iterable[str],
            entries: Entry | Iterable[Entry],
            action: Literal['add', 'remove'],
    ):
        """
        Update a search index by adding or removing an Entry.

        Args:
            index_name: Name of the index to update ('lemmas', 'translations', 'forms', or 'tags').
            search_terms: One or more search terms to add to or remove from the index.
            entries: One or more Entry objects to associate with the search terms.
            action: Either 'add' or 'remove'.

        Raises:
            KeyError: If an invalid index is specified.
        """

        search_terms = {search_terms} if isinstance(search_terms, str) else set(search_terms)
        entries = {entries} if isinstance(entries, Entry) else set(entries)

        index = self._indexes[index_name]

        if action == 'add':
            for term in search_terms:
                index.setdefault(term, set()).update(entries)
        elif action == 'remove':
            for term in search_terms:
                index[term].difference_update(entries)
                if index_name != 'tags' and not index[term]:
                    del index[term]
