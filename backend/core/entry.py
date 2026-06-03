"""
Implements the Entry class.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Iterator, Mapping

from .types import (
    Word, Translation, CtgValue, GramForm, WordForm,
    Phrase, PhraseTr, Note, Group, Timestamp, SerializedData,
)
from .errors import DeserializationError
from .utils import (
    remove_dup, gram_form_to_str, validate_required_fields,
    validate_field_type, validate_field_len,
)


class Translations:
    def __init__(self, translations: Translation | Iterable[Translation]):
        if isinstance(translations, Translation):
            self._data = [translations]
        else:
            self._data = remove_dup(list(translations))
            if not self._data:
                raise ValueError('Entry must have at least one translation')

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Translation]:
        return iter(self._data)

    def add(self, translation: Translation):
        """
        Add a new translation.

        Args:
            translation: The translation to add.
        """

        if translation not in self._data:
            self._data.append(translation)

    def edit(self, translation: Translation, new_translation: Translation):
        """
        Replace an existing translation with a new translation.

        Args:
            translation: The translation to edit.
            new_translation: The new translation.
        """

        if new_translation in self._data:
            if new_translation != translation:
                self._data.remove(translation)
        else:
            index = self._data.index(translation)
            self._data[index] = new_translation

    def delete(self, translation: Translation):
        """
        Delete a translation.

        Args:
            translation: The translation to delete.
        """

        if len(self._data) == 1:
            raise ValueError('Entry must have at least one translation')
        self._data.remove(translation)

    def serialize(self) -> list[Translation]:
        return self._data


class Forms:
    def __init__(self, forms: Mapping[GramForm, Iterable[WordForm]] | None):
        self._data: dict[GramForm, list[WordForm]] = {
            gram_form: remove_dup(list(word_forms))
            for gram_form, word_forms in forms.items()
        } if forms else dict()

        # Drop invalid forms
        self._data = {
            k: v for k, v in self._data.items() if v
        }

    def __bool__(self) -> bool:
        return bool(self._data)

    def __getitem__(self, key: GramForm) -> list[WordForm]:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[GramForm]:
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def add(self, gram_form: GramForm, word_form: WordForm):
        """
        Add a new inflected form.

        Args:
            gram_form: Grammatical form for the inflection.
            word_form: The actual inflected form to add.
        """

        if gram_form not in self._data.keys():
            self._data[gram_form] = [word_form]
        elif word_form not in self._data[gram_form]:
            self._data[gram_form].append(word_form)

    def edit(
            self,
            gram_form: GramForm,
            word_form: WordForm,
            new_gram_form: GramForm,
            new_word_form: WordForm,
    ):
        """
        Replace an existing form with a new form.

        Args:
            gram_form: Grammatical form identifying the inflection to replace.
            word_form: The actual inflected form to replace.
            new_gram_form: The new grammatical form.
            new_word_form: The new inflected form.
        """

        if new_gram_form == gram_form:
            word_forms = self._data[gram_form]
            if new_word_form in word_forms:
                if new_word_form != word_form:
                    word_forms.remove(word_form)
            else:
                index = word_forms.index(word_form)
                word_forms[index] = new_word_form
        else:
            self.delete(gram_form, word_form)
            self.add(new_gram_form, new_word_form)

    def delete(self, gram_form: GramForm, word_form: WordForm):
        """
        Remove an inflected form.

        Args:
            gram_form: Grammatical form identifying the inflection to remove.
            word_form: The actual inflected form to remove.
        """

        self._data[gram_form].remove(word_form)
        if not self._data[gram_form]:
            self._data.pop(gram_form)

    def serialize(self) -> SerializedData:
        return {
            'keys': [list(gram_form) for gram_form in self.keys()],
            'values': list(self.values()),
        }


class Phrases:
    def __init__(self, phrases: Mapping[Phrase, Iterable[PhraseTr]] | None):
        self._data: dict[Phrase, list[PhraseTr]] = {
            phrase: remove_dup(list(phrase_tr))
            for phrase, phrase_tr in phrases.items()
        } if phrases else dict()

        # Drop invalid phrases
        self._data = {
            k: v for k, v in self._data.items() if v
        }

    def __bool__(self) -> bool:
        return bool(self._data)

    def __getitem__(self, key: Phrase) -> list[PhraseTr]:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Phrase]:
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def add(self, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Add a new phrase/usage example with its translation.

        Args:
            phrase: The phrase or usage example containing the word.
            phrase_tr: The translation of the phrase.
        """

        if phrase not in self._data.keys():
            self._data[phrase] = [phrase_tr]
        elif phrase_tr not in self._data[phrase]:
            self._data[phrase].append(phrase_tr)

    def edit(
            self,
            phrase: Phrase,
            phrase_tr: PhraseTr,
            new_phrase: Phrase,
            new_phrase_tr: PhraseTr,
    ):
        """
        Replace an existing phrase with a new phrase.

        Args:
            phrase: The phrase to replace.
            phrase_tr: The translation of the phrase to replace.
            new_phrase: The new phrase.
            new_phrase_tr: The new phrase translation.
        """

        if new_phrase == phrase:
            phrase_trs = self._data[phrase]
            if new_phrase_tr in phrase_trs:
                if new_phrase_tr != phrase_tr:
                    phrase_trs.remove(phrase_tr)
            else:
                index = phrase_trs.index(phrase_tr)
                phrase_trs[index] = new_phrase_tr
        else:
            self.delete(phrase, phrase_tr)
            self.add(new_phrase, new_phrase_tr)

    def delete(self, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Remove a phrase and its translation.

        Args:
            phrase: The phrase to remove.
            phrase_tr: The translation of the phrase to remove.
        """

        self._data[phrase].remove(phrase_tr)
        if not self._data[phrase]:
            self._data.pop(phrase)

    def serialize(self) -> SerializedData:
        return self._data


class Notes:
    def __init__(self, notes: Note | Iterable[Note] | None):
        if not notes:
            self._data: list[Note] = []
        elif isinstance(notes, Note):
            self._data = [notes]
        else:
            self._data = remove_dup(list(notes))

    def __bool__(self) -> bool:
        return bool(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Note]:
        return iter(self._data)

    def add(self, note: Note):
        """
        Add a new note.

        Args:
            note: The note text to add.
        """

        if note not in self._data:
            self._data.append(note)

    def edit(self, note: Note, new_note: Note):
        """
        Replace an existing note with a new note.

        Args:
            note: The note to edit.
            new_note: The new note.
        """

        if new_note in self._data:
            if new_note != note:
                self._data.remove(note)
        else:
            index = self._data.index(note)
            self._data[index] = new_note

    def delete(self, note: Note):
        """
        Remove a note.

        Args:
            note: The note text to remove.
        """

        self._data.remove(note)

    def serialize(self) -> list[Note]:
        return self._data


class Groups:
    def __init__(self, groups: Iterable[Group] | None):
        self._data: set[Group] = set(groups) if groups else set()

    def __bool__(self) -> bool:
        return bool(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Group]:
        return iter(self._data)

    def add(self, group: Group):
        """
        Add a new group.

        Args:
            group: The group name to add.
        """

        self._data.add(group)

    def edit(self, group: Group, new_group: Group):
        """
        Rename an existing group.

        Args:
            group: The group to rename.
            new_group: The new group name.
        """

        self._data.remove(group)
        self._data.add(new_group)

    def delete(self, group: Group):
        """
        Remove a group.

        Args:
            group: The group name to remove.
        """

        self._data.remove(group)

    def serialize(self) -> list[Group]:
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
    - groups: Groups assigned to the entry.
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
            lemma: Word,
            tr: Translation | Iterable[Translation],
            forms: Mapping[GramForm, Iterable[WordForm]] | None = None,
            phrases: Mapping[Phrase, Iterable[PhraseTr]] | None = None,
            notes: Note | Iterable[Note] | None = None,
            groups: Iterable[Group] | None = None,
            is_fav: bool = False,
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
            groups: Groups assigned to the entry.
            is_fav: Whether the entry is favorite.
            total_att: Total number of game attempts.
            correct_att: Number of correct guesses (wins).
            win_streak: Count of consecutive wins.
            latest_att_timestamp: Timestamp of the most recent answer.
        """

        self.lemma = lemma
        self.tr = Translations(tr)
        self.forms = Forms(forms)
        self.phrases = Phrases(phrases)
        self.notes = Notes(notes)
        self.groups = Groups(groups)
        self.is_fav = is_fav
        self.total_att = total_att
        self.correct_att = correct_att
        self.win_streak = win_streak
        self.latest_att_timestamp = latest_att_timestamp

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
            'lemma', 'translations', 'total_att', 'correct_att',
            'win_streak', 'latest_att_timestamp',
        )
        validate_required_fields(data, required_fields)

        # Read required fields
        lemma = data['lemma']
        translations = data['translations']
        total_att = data['total_att']
        correct_att = data['correct_att']
        win_streak = data['win_streak']
        latest_att_timestamp = data['latest_att_timestamp']

        # Read optional fields
        forms = data.get('forms', {'keys': [], 'values': []})
        phrases = data.get('phrases', None)
        notes = data.get('notes', None)
        groups = data.get('groups', None)
        is_fav = data.get('is_fav', False)

        # Validate types
        validate_field_type('lemma', lemma, str)
        validate_field_type('translations', translations, list[str])
        validate_field_type('forms', forms, dict)

        validate_required_fields(forms, ('keys', 'values'))
        validate_field_type('keys', forms['keys'], list[list[str]])
        validate_field_type('values', forms['values'], list[list[str]])

        validate_field_type('phrases', phrases, (dict[str, list[str]], NoneType))
        validate_field_type('notes', notes, (list[str], NoneType))
        validate_field_type('groups', groups, (list[str], NoneType))
        validate_field_type('is_fav', is_fav, bool)
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
            lemma, translations, forms, phrases, notes, groups, is_fav,
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
        tokens.append(f'| {self.lemma} - ')
        tokens.append(', '.join(tr for tr in self.tr))
        tokens.append('\n')
        for gram_form, word_forms in self.forms.items():
            tokens.append(f'|  [{gram_form_to_str(gram_form)}] {', '.join(word_forms)}\n')
        for phrase, phrase_tr in self.phrases.items():
            tokens.append(f'|  {phrase} - ')
            tokens.append(', '.join(tr for tr in phrase_tr))
            tokens.append('\n')
        for note in self.notes:
            tokens.append(f'| > {note}\n')

        return ''.join(tokens)

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
    def n_notes(self) -> int:
        return len(self.notes)

    @property
    def accuracy(self) -> float:
        return 0 if (self.total_att == 0) else self.correct_att / self.total_att

    def add_to_fav(self):
        """Mark this entry as favorite."""

        self.is_fav = True

    def remove_from_fav(self):
        """Remove this entry from favorites."""

        self.is_fav = False

    def delete_ctg_value(self, pos: int, ctg_val: CtgValue):
        """
        Delete the specified category value from all grammatical form tuples.

        Args:
            pos: The position (index) of the category in grammatical form tuple.
            ctg_val: The category value to be removed.
        """

        self.forms = Forms({
            gram_form: word_forms
            for gram_form, word_forms in self.forms.items()
            if gram_form[pos] != ctg_val
        })

    def rename_ctg_value(self, pos: int, old_ctg_val: CtgValue, new_ctg_val: CtgValue):
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

        self.forms = Forms({
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
        })

    def add_ctg(self):
        """Add a new empty category to all grammatical form tuples."""

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form + ('',))

        self.forms = Forms({
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
        })

    def delete_ctg(self, pos: int):
        """
        Delete the category at the specified position from all grammatical form tuples.

        Removes the entire category (including all its values) at position `pos`
        from all word forms in the entry.

        Args:
            pos: The position (index) of the category to be deleted in grammatical form tuple.
        """

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form[:pos] + gram_form[pos+1:])

        self.forms = Forms({
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
            if gram_form[pos] == ''
        })

    def register_correct_answer(self, session_number: Timestamp):
        """
        Update learning statistics when a correct attempt is made.

        Increments both total attempts and correct attempts counters, updates
        the win streak, and sets the latest attempt timestamp.

        Args:
            session_number: A tuple representing the session identifier.
        """

        self.total_att += 1
        self.correct_att += 1
        if self.win_streak <= 0:
            self.win_streak = 1
        else:
            self.win_streak += 1
        self.latest_att_timestamp = session_number

    def register_incorrect_answer(self, session_number: Timestamp):
        """
        Update learning statistics when an incorrect attempt is made.

        Increments the total attempts counter, resets the win streak to 0,
        and sets the latest attempt timestamp.

        Args:
            session_number: A tuple representing the session identifier.
        """

        self.total_att += 1
        if self.win_streak > 0:
            self.win_streak = -1
        else:
            self.win_streak -= 1
        self.latest_att_timestamp = session_number

    def to_dict(self) -> SerializedData:
        """
        Serialize the entry to a dictionary format.

        Returns:
            Dictionary containing entry data.
        """

        return {
            'lemma': self.lemma,
            'translations': self.tr,
            'forms': self.forms,
            'phrases': self.phrases,
            'notes': self.notes,
            'groups': self.groups,
            'is_fav': self.is_fav,
            'total_att': self.total_att,
            'correct_att': self.correct_att,
            'win_streak': self.win_streak,
            'latest_att_timestamp': self.latest_att_timestamp,
        }

    def to_json_dict(self) -> SerializedData:
        """
        Serialize the entry to a JSON format.

        Returns:
            Dictionary containing entry data.
        """

        data = {
            'lemma': self.lemma,
            'translations': self.tr.serialize(),
            'is_fav': self.is_fav,
            'total_att': self.total_att,
            'correct_att': self.correct_att,
            'win_streak': self.win_streak,
            'latest_att_timestamp': list(self.latest_att_timestamp),
        }

        if self.forms:
            data['forms'] = self.forms.serialize()
        if self.phrases:
            data['phrases'] = self.phrases.serialize()
        if self.notes:
            data['notes'] = self.notes.serialize()
        if self.groups:
            data['groups'] = self.groups.serialize()

        return data
