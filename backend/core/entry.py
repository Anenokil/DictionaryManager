"""
Implements the Entry class.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Mapping

from .types import (
    Word, Translation, CtgValue, GramForm, WordForm,
    Phrase, PhraseTr, Note, Group, Timestamp, SerializedData,
)
from .errors import DeserializationError
from .utils import (
    gram_form_to_str, validate_required_fields, validate_field_type,
    validate_field_len,
)

# Typing aliases used in the module
Translations = list[Translation]
Forms = dict[GramForm, list[WordForm]]
Phrases = dict[Phrase, list[PhraseTr]]
Notes = list[Note]
Groups = set[Group]


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
    - n_translations: Number of translations for the word.
    - n_gram_forms: Number of grammatical forms.
    - n_phrases: Number of phrases.
    - n_notes: Number of notes.
    - is_fav: True if the entry is favorite.
    - groups: Groups assigned to the entry.
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
        self.tr: Translations = [tr] if isinstance(tr, Translation) else list(tr)
        self.forms: Forms = {
            pattern: list(forms)
            for pattern, forms in forms.items()
        } if forms else dict()
        self.phrases: Phrases = {phrase: list(phrase_tr) for phrase, phrase_tr in phrases.items()} if phrases else dict()
        if not notes:
            self.notes: Notes = []
        elif isinstance(notes, Note):
            self.notes = [notes]
        else:
            self.notes = list(notes)
        self.groups: Groups = set(groups) if groups else set()
        self.is_fav = is_fav
        self.total_att = total_att
        self.correct_att = correct_att
        self.win_streak = win_streak
        self.latest_att_timestamp = latest_att_timestamp

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

    def add_tr(self, tr: Translation):
        """
        Add a new translation to the entry.

        Args:
            tr: The translation to add.
        """

        if tr not in self.tr:
            self.tr.append(tr)

    def delete_tr(self, tr: Translation):
        """
        Delete a translation from the entry.

        Args:
            tr: The translation to delete.
        """

        self.tr.remove(tr)

    def add_form(self, gram_form: GramForm, word_form: WordForm):
        """
        Add a new inflected form to the entry.

        Args:
            gram_form: Grammatical form for the inflection.
            word_form: The actual inflected form to add.
        """

        if gram_form not in self.forms.keys():
            self.forms[gram_form] = [word_form]
        elif word_form not in self.forms[gram_form]:
            self.forms[gram_form].append(word_form)

    def delete_form(self, gram_form: GramForm, word_form: WordForm):
        """
        Remove an inflected form from the entry.

        Args:
            gram_form: Grammatical form identifying the inflection to remove.
            word_form: The actual inflected form to remove.
        """

        self.forms[gram_form].remove(word_form)
        if len(self.forms[gram_form]) == 0:
            self.forms.pop(gram_form)

    def add_phrase(self, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Add a new phrase/usage example with its translation.

        Args:
            phrase: The phrase or usage example containing the word.
            phrase_tr: The translation of the phrase.
        """

        if phrase not in self.phrases.keys():
            self.phrases[phrase] = [phrase_tr]
        elif phrase_tr not in self.phrases[phrase]:
            self.phrases[phrase].append(phrase_tr)

    def delete_phrase(self, phrase: Phrase, phrase_tr: PhraseTr):
        """
        Remove a phrase and its translation from the entry.

        Removes the specified phrase-translation pair from `phrases`.

        Args:
            phrase: The phrase to remove.
            phrase_tr: The translation of the phrase to remove.
        """

        self.phrases[phrase].remove(phrase_tr)
        if len(self.phrases[phrase]) == 0:
            self.phrases.pop(phrase)

    def add_note(self, note: Note):
        """
        Add a new note to the entry.

        Args:
            note: The note text to add.
        """

        if note not in self.notes:
            self.notes.append(note)

    def delete_note(self, note: Note):
        """
        Remove a note from the entry.

        Args:
            note: The note text to remove.
        """

        self.notes.remove(note)

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

        self.is_fav = True

    def remove_from_fav(self):
        """Remove this entry from favorites."""

        self.is_fav = False

    def delete_ctg_value(self, pos: int, ctg_val: CtgValue):
        """
        Delete the specified category value from all word forms.

        Args:
            pos: The position (index) of the category in grammatical form tuple.
            ctg_val: The category value to be removed.
        """

        self.forms = {
            gram_form: word_forms
            for gram_form, word_forms in self.forms.items()
            if gram_form[pos] != ctg_val
        }

    def rename_ctg_value(self, pos: int, old_ctg_val: CtgValue, new_ctg_val: CtgValue):
        """
        Rename the specified category value in all word forms.

        Args:
            pos: The position (index) of the category in grammatical form tuple.
            old_ctg_val: The current category value to be replaced.
            new_ctg_val: The new category value that will replace the old one.
        """

        def update_gram_form(gram_form: GramForm) -> GramForm:
            if gram_form[pos] != old_ctg_val:
                return gram_form
            return tuple(gram_form[:pos] + (new_ctg_val,) + gram_form[pos+1:])

        self.forms = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
        }

    def add_ctg(self):
        """Add a new empty category to all word forms."""

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form + ('',))

        self.forms = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
        }

    def delete_ctg(self, pos: int):
        """
        Delete the category at the specified position from all word forms.

        Removes the entire category (including all its values) at position `pos`
        from all word forms in the entry.

        Args:
            pos: The position (index) of the category to be deleted in grammatical form tuple.
        """

        def update_gram_form(gram_form: GramForm) -> GramForm:
            return tuple(gram_form[:pos] + gram_form[pos+1:])

        self.forms = {
            update_gram_form(gram_form): word_forms
            for gram_form, word_forms in self.forms.items()
            if gram_form[pos] == ''
        }

    def correct(self, session_number: Timestamp):
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

    def incorrect(self, session_number: Timestamp):
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

    @property
    def accuracy(self) -> float:
        return 0 if (self.total_att == 0) else self.correct_att / self.total_att

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

        data = self.to_dict()

        data['forms'] = {
            'keys': list(self.forms.keys()),
            'values': list(self.forms.values()),
        }
        data['groups'] = list(self.groups)

        return data

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
