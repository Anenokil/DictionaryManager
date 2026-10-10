"""
Implements the Entry class.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Iterator, Mapping, Any

from .types import (
    Word, Translation, CtgValue, GramForm, WordForm,
    Phrase, PhraseTr, Note, Tag, Timestamp, SerializedData,
)
from .errors import DeserializationError
from .utils import (
    remove_dup, gram_form_to_str, validate_required_fields,
    validate_field_type, validate_field_len,
)


class UniqueList:
    def __init__(self, values: Word | Iterable[Word] | None):
        if values is None:
            self._data: list[Word] = []
        elif isinstance(values, Word):
            self._data = [values]
        else:
            self._data = remove_dup(list(values))

    def __bool__(self) -> bool:
        return bool(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Word]:
        return iter(self._data)

    def __getitem__(self, key: Any) -> Word:
        return self._data[key]

    def __str__(self) -> str:
        return str(self._data)

    def _add(self, value: Word) -> tuple[bool, int]:
        """
        Add a new value.

        Args:
            value: The word to add.

        Returns:
            Pair (is_modified, delta).
            - is_modified: True if the object was modified.
            - delta: Change in the number of values.
        """

        if value in self._data:
            return False, 0
        else:
            self._data.append(value)
            return True, 1

    def _edit(self, value: Word, new_value: Word) -> tuple[bool, int]:
        """
        Replace an existing value with a new one.

        Args:
            value: The word to edit.
            new_value: The new word.

        Returns:
            Pair (is_modified, delta).
            - is_modified: True if the object was modified.
            - delta: Change in the number of values.

        Raises:
            ValueError: If the specified value is not found.
        """

        if new_value in self._data:
            if new_value == value:
                return False, 0
            else:
                self._data.remove(value)
                return True, -1
        else:
            index = self._data.index(value)
            self._data[index] = new_value
            return True, 0

    def _delete(self, value: Word):
        """
        Remove a value.

        Args:
            value: The word to remove.

        Raises:
            ValueError: If the specified value is not found.
        """

        self._data.remove(value)

    def _serialize(self) -> list[Word]:
        return self._data


Notes = UniqueList


class Variants(UniqueList):
    def __init__(self, variants: Word | Iterable[Word]):
        super().__init__(variants)

        if not self._data:
            raise ValueError('Entry must have at least one spelling variant of the lemma')

    def _delete(self, variant: Word):
        """
        Delete a spelling variant.

        Args:
            variant: Spelling variant to delete.

        Raises:
            ValueError: If the specified spelling variant is not found,
                        or if it is the only spelling variant.
        """

        if len(self._data) == 1:
            raise ValueError('Entry must have at least one spelling variant of the lemma')
        self._data.remove(variant)


class Translations(UniqueList):
    def __init__(self, translations: Translation | Iterable[Translation]):
        super().__init__(translations)

        if not self._data:
            raise ValueError('Entry must have at least one translation')

    def _delete(self, translation: Translation):
        """
        Delete a translation.

        Args:
            translation: The translation to delete.

        Raises:
            ValueError: If the specified translation is not found, or if it is the only translation.
        """

        if len(self._data) == 1:
            raise ValueError('Entry must have at least one translation')
        self._data.remove(translation)


class ListDict:
    def __init__(self, values: Mapping[Any, Iterable[Word]] | None):
        self._data: dict[Any, list[Word]] = {
            k: remove_dup(list(v))
            for k, v in values.items()
        } if values else dict()

        # Drop empty lists
        self._data = {
            k: v for k, v in self._data.items() if v
        }

    def __bool__(self) -> bool:
        return bool(self._data)

    def __getitem__(self, key: Any) -> list[Word]:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Word]:
        return iter(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def _add(self, key: Any, value: Word) -> tuple[bool, int, int]:
        """
        Add a new key-value pair.

        Args:
            key: The key to add.
            value: The value to add.

        Returns:
            Tuple (is_modified, delta_k, delta_v).
            - is_modified: True if the object was modified.
            - delta_k: Change in the number of keys.
            - delta_v: Change in the number of values.
        """

        if key in self._data.keys():
            if value in self._data[key]:
                return False, 0, 0
            else:
                self._data[key].append(value)
                return True, 0, 1
        else:
            self._data[key] = [value]
            return True, 1, 1

    def _edit(
            self,
            key: Any,
            value: Word,
            new_key: Any,
            new_value: Word,
    ) -> tuple[bool, int, int]:
        """
        Replace an existing key-value pair with a new one.

        Args:
            key: The key to edit.
            value: The value to edit.
            new_key: The new key.
            new_value: The new value.

        Returns:
            Tuple (is_modified, delta_k, delta_v).
            - is_modified: True if the object was modified.
            - delta_k: Change in the number of keys.
            - delta_v: Change in the number of values.

        Raises:
            KeyError: If the specified key is not found.
            ValueError: If the specified value is not found.
        """

        if new_key == key:
            values = self._data[key]
            if new_value in values:
                if new_value == value:
                    return False, 0, 0
                else:
                    values.remove(value)
                    return True, 0, -1
            else:
                index = values.index(value)
                values[index] = new_value
                return True, 0, 0
        else:
            m1, p1, t1 = self._delete(key, value)
            m2, p2, t2 = self._add(new_key, new_value)
            return m1 or m2, p1 + p2, t1 + t2

    def _delete(self, key: Any, value: Word) -> tuple[bool, int, int]:
        """
        Remove a key-value pair.

        Args:
            key: The key to remove.
            value: The value to remove.

        Returns:
            Tuple (is_modified, delta_k, delta_v).
            - is_modified: True if the object was modified.
            - delta_k: Change in the number of keys.
            - delta_v: Change in the number of values.

        Raises:
            KeyError: If the specified key is not found.
            ValueError: If the specified value is not found.
        """

        self._data[key].remove(value)
        if self._data[key]:
            return True, 0, -1
        else:
            self._data.pop(key)
            return True, -1, -1

    def _serialize(self) -> SerializedData:
        return self._data


class Phrases(ListDict):
    def __init__(self, phrases: Mapping[Phrase, Iterable[PhraseTr]] | None):
        super().__init__(phrases)

    def _serialize(self) -> SerializedData:
        return self._data


class Forms(ListDict):
    def __init__(self, forms: Mapping[GramForm, Iterable[WordForm]] | None):
        super().__init__(forms)

    def _add_ctg(self):
        """Add a new empty category to all grammatical form tuples."""

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form + ('',))

        self._data = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self._data.items()
        }

    def _delete_ctg(self, pos: int):
        """
        Delete the category at the specified position from all grammatical form tuples.

        Removes the entire category (including all its values) at position `pos`
        from all word forms.

        Args:
            pos: The position (index) of the category to be deleted in grammatical form tuple.
        """

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form[:pos] + gram_form[pos+1:])

        self._data = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self._data.items()
            if gram_form[pos] == ''
        }

    def _rename_ctg_value(self, pos: int, old_ctg_val: CtgValue, new_ctg_val: CtgValue):
        """
        Rename the specified category value in all grammatical form tuples.

        Args:
            pos: The position (index) of the category in grammatical form tuple.
            old_ctg_val: The current category value to be replaced.
            new_ctg_val: The new category value that will replace the old one.
        """

        def update_gram_form(gram_form: GramForm) -> GramForm:
            if gram_form[pos] != old_ctg_val:
                return gram_form
            return tuple(gram_form[:pos] + (new_ctg_val,) + gram_form[pos+1:])

        self._data = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self._data.items()
        }

    def _delete_ctg_value(self, pos: int, ctg_val: CtgValue):
        """
        Delete the specified category value from all grammatical form tuples.

        Args:
            pos: The position (index) of the category in grammatical form tuple.
            ctg_val: The category value to be removed.
        """

        self._data = {
            gram_form: word_forms
            for gram_form, word_forms in self._data.items()
            if gram_form[pos] != ctg_val
        }

    def _serialize(self) -> SerializedData:
        return {
            'keys': [list(gram_form) for gram_form in self.keys()],
            'values': list(self.values()),
        }


class Tags:
    def __init__(self, tags: Iterable[Tag] | None):
        self._data: set[Tag] = set(tags) if tags else set()

    def __bool__(self) -> bool:
        return bool(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Tag]:
        return iter(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def _add(self, tag: Tag) -> tuple[bool, int]:
        """
        Add a new tag.

        Args:
            tag: The tag to add.

        Returns:
            Pair (is_modified, delta).
            - is_modified: True if the object was modified.
            - delta: Change in the number of tags.
        """

        if tag in self._data:
            return False, 0
        else:
            self._data.add(tag)
            return True, 1

    def _edit(self, tag: Tag, new_tag: Tag) -> tuple[bool, int]:
        """
        Rename an existing tag.

        Args:
            tag: The tag to rename.
            new_tag: The new tag name.

        Returns:
            Pair (is_modified, delta).
            - is_modified: True if the object was modified.
            - delta: Change in the number of tags.
        """

        if new_tag in self._data:
            if tag == new_tag:
                return False, 0
            else:
                self._data.remove(tag)
                return True, -1
        else:
            self._data.remove(tag)
            self._data.add(new_tag)
            return True, 0

    def _delete(self, tag: Tag):
        """
        Remove a tag.

        Args:
            tag: The tag to remove.
        """

        self._data.remove(tag)

    def _serialize(self) -> list[Tag]:
        return list(self._data)


class Entry:
    """
    A dictionary entry representing a word and its associated data.

    This class encapsulates all linguistic and statistical information
    about a dictionary entry, including translations, inflections,
    usage examples, and learning statistics.

    Attributes:
    ----------
    - lemma: The lemma (canonical/dictionary form of the word).
    - tr: Translations.
    - forms: Inflected forms (except the lemma).
    - phrases: Phrases containing the word; usage examples.
    - notes: Notes field.
    - tags: Tags assigned to the entry.
    - n_translations: Number of translations for the word.
    - n_gram_forms: Number of grammatical forms.
    - n_word_forms: Number of word forms.
    - n_phrases: Number of phrases.
    - n_notes: Number of notes.
    - is_fav: True if the entry is favorite.
    - total_att: Total number of game attempts.
    - correct_att: Number of correct guesses (wins).
    - accuracy: Ratio of correct guesses to total attempts (correct_att / total_att).
    - win_streak: Count of consecutive wins.
    - latest_att_timestamp: Timestamp of the most recent answer.
    """

    def __init__(
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
    ):
        """
        Initialize a dictionary entry.

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
        """

        self.variants = Variants(lemma)
        self.tr = Translations(tr)
        self.forms = Forms(forms)
        self.phrases = Phrases(phrases)
        self.notes = Notes(notes)
        self.tags = Tags(tags)
        self.is_fav = is_fav
        self.img_fn = img_fn
        self._total_att = total_att
        self._correct_att = correct_att
        self._win_streak = win_streak
        self._latest_att_timestamp = latest_att_timestamp

    @classmethod
    def from_json_dict(cls, data: SerializedData) -> 'Entry':
        """
        Deserialize Entry data from a JSON format.

        Args:
            data: Dictionary containing entry data.

        Returns:
            An Entry object.
        """

        # Validate required fields
        required_fields = (
            'variants', 'translations', 'total_att', 'correct_att',
            'win_streak', 'latest_att_timestamp',
        )
        validate_required_fields(data, required_fields)

        # Read required fields
        variants = data['variants']
        translations = data['translations']
        total_att = data['total_att']
        correct_att = data['correct_att']
        win_streak = data['win_streak']
        latest_att_timestamp = data['latest_att_timestamp']

        # Read optional fields
        forms = data.get('forms', {'keys': [], 'values': []})
        phrases = data.get('phrases', None)
        notes = data.get('notes', None)
        tags = data.get('tags', None)
        is_fav = data.get('is_fav', False)
        img_fn = data.get('img_fn', None)

        # Validate types
        validate_field_type('variants', variants, list[str])
        validate_field_type('translations', translations, list[str])
        validate_field_type('forms', forms, dict)

        validate_required_fields(forms, ('keys', 'values'))
        validate_field_type('keys', forms['keys'], list[list[str]])
        validate_field_type('values', forms['values'], list[list[str]])

        validate_field_type('phrases', phrases, (dict[str, list[str]], NoneType))
        validate_field_type('notes', notes, (list[str], NoneType))
        validate_field_type('tags', tags, (list[str], NoneType))
        validate_field_type('is_fav', is_fav, bool)
        validate_field_type('img_fn', img_fn, (str, NoneType))
        validate_field_type('total_att', total_att, int)
        validate_field_type('correct_att', correct_att, int)
        validate_field_type('win_streak', win_streak, int)
        validate_field_type('latest_att_timestamp', latest_att_timestamp, list[int])

        # Validate values
        validate_field_len('latest_att_timestamp', latest_att_timestamp, 3)
        if len(forms['keys']) != len(forms['values']):
            raise DeserializationError('Field "keys" and "values" must have same length')

        # Convert types and values
        forms = {
            tuple(key): val
            for key, val in zip(forms['keys'], forms['values'])
        }
        latest_att_timestamp = tuple(latest_att_timestamp)

        return cls(
            variants, translations, forms, phrases, notes, tags, is_fav, img_fn,
            total_att, correct_att, win_streak, latest_att_timestamp,
        )

    def __str__(self) -> str:
        """
        Get string representation of the entry.

        Returns:
            A formatted representation of the entire dictionary entry including
            lemma, translations, inflected forms, phrases, notes, and learning statistics.
        """

        tokens = []
        if self.is_fav:
            tokens.append('* (fav)\n')
        tokens.append(f'| {self.lemma}')
        if self.n_variants > 1:
            tokens.append(f' (alternative: {", ".join(self.variants[1:])})')
        tokens.append(' - ')
        tokens.append(', '.join(self.tr))
        tokens.append('\n')
        for gram_form, word_forms in self.forms.items():
            tokens.append(f'|  [{gram_form_to_str(gram_form)}] {", ".join(word_forms)}\n')
        for phrase, phrase_tr in self.phrases.items():
            tokens.append(f'|  {phrase} - ')
            tokens.append(', '.join(tr for tr in phrase_tr))
            tokens.append('\n')
        for note in self.notes:
            tokens.append(f'| > {note}\n')

        return ''.join(tokens)

    @property
    def lemma(self) -> Word:
        return self.variants[0]

    @property
    def n_variants(self) -> int:
        return len(self.variants)

    @property
    def n_translations(self) -> int:
        return len(self.tr)

    @property
    def n_gram_forms(self) -> int:
        return len(self.forms)

    @property
    def n_word_forms(self) -> int:
        return sum(len(forms) for forms in self.forms.values())

    @property
    def n_phrases(self) -> int:
        return len(self.phrases)

    @property
    def n_phrase_translations(self) -> int:
        return sum(len(phrase_tr) for phrase_tr in self.phrases.values())

    @property
    def n_notes(self) -> int:
        return len(self.notes)

    @property
    def n_tags(self) -> int:
        return len(self.tags)

    @property
    def total_att(self) -> int:
        return self._total_att

    @property
    def correct_att(self) -> int:
        return self._correct_att

    @property
    def accuracy(self) -> float:
        return 0 if (self._total_att == 0) else self._correct_att / self._total_att

    @property
    def win_streak(self) -> int:
        return self._win_streak

    @property
    def latest_att_timestamp(self) -> Timestamp:
        return self._latest_att_timestamp

    def _edit(
            self,
            lemma: Word | Iterable[Word] = ...,
            tr: Translation | Iterable[Translation] = ...,
            forms: Mapping[GramForm, Iterable[WordForm]] = ...,
            phrases: Mapping[Phrase, Iterable[PhraseTr]] = ...,
            notes: Note | Iterable[Note] = ...,
            tags: Iterable[Tag] = ...,
            is_fav: bool = ...,
            img_fn: str | None = ...,
            total_att: int = ...,
            correct_att: int = ...,
            win_streak: int = ...,
            latest_att_timestamp: Timestamp = ...,
    ):
        if lemma is not ...:
            self.variants = Variants(lemma)
        if tr is not ...:
            self.tr = Translations(tr)
        if forms is not ...:
            self.forms = Forms(forms)
        if phrases is not ...:
            self.phrases = Phrases(phrases)
        if notes is not ...:
            self.notes = Notes(notes)
        if tags is not ...:
            self.tags = Tags(tags)
        if is_fav is not ...:
            self.is_fav = is_fav
        if img_fn is not ...:
            self.img_fn = img_fn
        if total_att is not ...:
            self._total_att = total_att
        if correct_att is not ...:
            self._correct_att = correct_att
        if win_streak is not ...:
            self._win_streak = win_streak
        if latest_att_timestamp is not ...:
            self._latest_att_timestamp = latest_att_timestamp

    def has_same_content(self, other: 'Entry', include_stats: bool = False) -> bool:
        if include_stats:
            if not (
                    self._total_att == other._total_att and
                    self._correct_att == other._correct_att and
                    self._win_streak == other._win_streak and
                    self._latest_att_timestamp == other._latest_att_timestamp
            ):
                return False

        return (
            self.is_fav == other.is_fav and
            self.img_fn == other.img_fn and
            set(self.tags) == set(other.tags) and
            list(self.variants) == list(other.variants) and
            list(self.tr) == list(other.tr) and
            list(self.notes) == list(other.notes) and
            dict(self.forms) == dict(other.forms) and
            dict(self.phrases) == dict(other.phrases)
        )

    def register_correct_answer(self, timestamp: Timestamp):
        """
        Update learning statistics when a correct attempt is made.

        Increments both total attempts and correct attempts counters, updates
        the win streak, and sets the latest attempt timestamp.

        Args:
            timestamp: A tuple representing the session identifier.
        """

        self._total_att += 1
        self._correct_att += 1
        if self._win_streak <= 0:
            self._win_streak = 1
        else:
            self._win_streak += 1
        self._latest_att_timestamp = timestamp

    def register_incorrect_answer(self, timestamp: Timestamp):
        """
        Update learning statistics when an incorrect attempt is made.

        Increments the total attempts counter, resets the win streak to 0,
        and sets the latest attempt timestamp.

        Args:
            timestamp: A tuple representing the session identifier.
        """

        self._total_att += 1
        if self._win_streak > 0:
            self._win_streak = -1
        else:
            self._win_streak -= 1
        self._latest_att_timestamp = timestamp

    def reset_stats(self):
        """Reset learning statistics."""

        self._total_att = 0
        self._correct_att = 0
        self._win_streak = 0

    def merge(self, other: 'Entry'):
        for variant in other.variants:
            self.variants._add(variant)
        for tr in other.tr:
            self.tr._add(tr)
        for gram_form, word_forms in other.forms.items():
            for word_form in word_forms:
                self.forms._add(gram_form, word_form)
        for phrase in other.phrases.keys():
            for phrase_tr in other.phrases[phrase]:
                self.phrases._add(phrase, phrase_tr)
        for note in other.notes:
            self.notes._add(note)
        for tag in other.tags:
            self.tags._add(tag)
        if other.is_fav:
            self.is_fav = True
        if self.img_fn is None:
            self.img_fn = other.img_fn
        self._total_att += other._total_att
        self._correct_att += other._correct_att
        self._win_streak += other._win_streak
        self._latest_att_timestamp = max(self._latest_att_timestamp, other._latest_att_timestamp)

    def to_dict(self) -> SerializedData:
        """
        Serialize the entry to a JSON format.

        Returns:
            Dictionary containing entry data.
        """

        data: SerializedData = {
            'variants': self.variants._serialize(),
            'translations': self.tr._serialize(),
            'is_fav': self.is_fav,
            'total_att': self._total_att,
            'correct_att': self._correct_att,
            'win_streak': self._win_streak,
            'latest_att_timestamp': list(self._latest_att_timestamp),
        }

        if self.forms:
            data['forms'] = self.forms._serialize()
        if self.phrases:
            data['phrases'] = self.phrases._serialize()
        if self.notes:
            data['notes'] = self.notes._serialize()
        if self.tags:
            data['tags'] = self.tags._serialize()
        if self.img_fn:
            data['img_fn'] = self.img_fn

        return data
