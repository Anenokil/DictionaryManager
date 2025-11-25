"""
Implements the Entry class.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable, Mapping, Literal

from .types import (
    Word, Translation, CtgValue, FormPattern, Form,
    Phrase, PhraseTr, Note, Group, Timestamp, SerializedData,
)
from .errors import DeserializationError
from .utils import pattern_to_str, validate_required_fields, validate_field_type

# Typing aliases used in the module
Translations = list[Translation]
Forms = dict[FormPattern, Form]
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
    - accuracy: Ratio of correct guesses to total attempts (correct_att / total_att).
    - win_streak: Count of consecutive wins.
    - latest_att_timestamp: Timestamp of the most recent answer.
    """

    def __init__(
            self,
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
            latest_att_timestamp: Timestamp = (0, 0, 0),
    ):
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
        self.tr: Translations = [tr] if isinstance(tr, Translation) else list(tr)
        self.forms: Forms = forms if forms else dict()
        self.phrases: Phrases = {phr: list(tr) for phr, tr in phrases.items()} if phrases else dict()
        if not notes:
            self.notes: Notes = []
        elif isinstance(notes, Note):
            self.notes = [notes]
        else:
            self.notes = list(notes)
        self.groups: Groups = set(groups) if groups else set()
        self.fav = fav
        self.total_att = total_att
        self.correct_att = correct_att
        self.win_streak = win_streak
        self.latest_att_timestamp = latest_att_timestamp

    @property
    def count_t(self) -> int:
        return len(self.tr)

    @property
    def count_f(self) -> int:
        return len(self.forms)

    @property
    def count_p(self) -> int:
        return len(self.phrases)

    @property
    def count_n(self) -> int:
        return len(self.notes)

    def add_tr(self, new_tr: Translation):
        """
        Add a new translation to the entry.

        Args:
            new_tr: The translation to add.
        """

        if new_tr not in self.tr:
            self.tr.append(new_tr)

    def delete_tr(self, tr: Translation):
        """
        Delete a translation from the entry.

        Args:
            tr: The translation to delete.
        """

        self.tr.remove(tr)

    def add_form(self, form_key: FormPattern, new_form: Form):
        """
        Add a new inflected form to the entry.

        Args:
            form_key: The form pattern for the inflection.
            new_form: The actual inflected form to add.
        """

        if form_key not in self.forms.keys():
            self.forms[form_key] = new_form

    def delete_form(self, form_key: FormPattern):
        """
        Remove an inflected form from the entry.

        Args:
            form_key: The form pattern identifying the inflection to remove.
        """

        self.forms.pop(form_key)

    def add_phrase(self, new_phr: Phrase, new_phr_tr: PhraseTr):
        """
        Add a new phrase/usage example with its translation.

        Args:
            new_phr: The phrase or usage example containing the word.
            new_phr_tr: The translation of the phrase.
        """

        if new_phr not in self.phrases.keys():
            self.phrases[new_phr] = [new_phr_tr]
        elif new_phr_tr not in self.phrases[new_phr]:
            self.phrases[new_phr].append(new_phr_tr)

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

    def add_note(self, new_note: Note):
        """
        Add a new note to the entry.

        Args:
            new_note: The note text to add.
        """

        if new_note not in self.notes:
            self.notes.append(new_note)

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

        self.forms = {
            pattern: form
            for pattern, form in self.forms.items()
            if pattern[pos] != ctg_val
        }

    def rename_ctg_value(self, pos: int, old_ctg_val: CtgValue, new_ctg_val: CtgValue):
        """
        Rename the specified category value in all word forms.

        Args:
            pos: The position (index) of the category in form pattern.
            old_ctg_val: The current category value to be replaced.
            new_ctg_val: The new category value that will replace the old one.
        """

        def update_pattern(pattern: FormPattern) -> FormPattern:
            if pattern[pos] != old_ctg_val:
                return pattern
            return tuple(pattern[:pos] + (new_ctg_val,) + pattern[pos+1:])

        self.forms = {
            update_pattern(pattern): form
            for pattern, form in self.forms.items()
        }

    def add_ctg(self):
        """Add a new empty category to all word forms."""

        def update_pattern(pattern: FormPattern) -> FormPattern:
            return tuple(pattern + ('',))

        self.forms = {
            update_pattern(pattern): form
            for pattern, form in self.forms.items()
        }

    def delete_ctg(self, pos: int):
        """
        Delete the category at the specified position from all word forms.

        Removes the entire category (including all its values) at position `pos`
        from all word forms in the entry.

        Args:
            pos: The position (index) of the category to be deleted in form pattern.
        """

        def update_pattern(pattern: FormPattern) -> FormPattern:
            return tuple(pattern[:pos] + pattern[pos+1:])

        self.forms = {
            update_pattern(pattern): form
            for pattern, form in self.forms.items()
            if pattern[pos] == ''
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
        if self.fav:
            tokens.append('* (fav)\n')
        tokens.append(f'| {self.lemma} - ')
        tokens.append(', '.join(tr for tr in self.tr))
        tokens.append('\n')
        for pattern, form in self.forms.items():
            tokens.append(f'|  [{pattern_to_str(pattern)}] {form}\n')
        for phr, phr_tr in self.phrases.items():
            tokens.append(f'|  {phr} - ')
            tokens.append(', '.join(tr for tr in phr_tr))
            tokens.append('\n')
        for note in self.notes:
            tokens.append(f'| > {note}\n')

        return ''.join(tokens)

    def serialize(self, frmt: Literal['json', 'pickle']) -> SerializedData:
        """
        Serialize the entry to a dictionary format.

        Args:
            frmt: The format to serialize the entry to (json, pickle).

        Returns:
            Dictionary containing entry data.
        """

        assert frmt in ('json', 'pickle')

        data = {
            'lemma': self.lemma,
            'translations': self.tr,
            'forms': self.forms,
            'phrases': self.phrases,
            'notes': self.notes,
            'groups': self.groups,
            'fav': self.fav,
            'total_att': self.total_att,
            'correct_att': self.correct_att,
            'win_streak': self.win_streak,
            'latest_att_timestamp': self.latest_att_timestamp,
        }
        if frmt == 'pickle':
            return data

        data['forms'] = {
            'keys': tuple(self.forms.keys()),
            'values': tuple(self.forms.values()),
        }
        data['groups'] = tuple(self.groups)
        return data

    @classmethod
    def deserialize(cls, data: SerializedData) -> 'Entry':
        """
        Deserialize Entry data from a dictionary format.

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
        forms = data.get('forms', {'keys': (), 'values': ()})
        phrases = data.get('phrases', None)
        notes = data.get('notes', None)
        groups = data.get('groups', None)
        fav = data.get('fav', False)

        # Validate types
        validate_field_type('lemma', lemma, str)
        validate_field_type('translations', translations, (str, Iterable[str]))
        validate_field_type('forms', forms, Mapping)

        required_fields = ('keys', 'values')
        validate_required_fields(forms, required_fields)

        validate_field_type('keys', forms['keys'], Mapping[str, tuple[str, ...]])
        validate_field_type('values', forms['values'], Mapping[str, str])
        validate_field_type('phrases', phrases, (Mapping[str, Iterable[str]], NoneType))
        validate_field_type('notes', notes, (str, Iterable[str], NoneType))
        validate_field_type('groups', groups, (Iterable[str], NoneType))
        validate_field_type('fav', fav, (bool, int))
        validate_field_type('total_att', total_att, (int, str))
        validate_field_type('correct_att', correct_att, (int, str))
        validate_field_type('win_streak', win_streak, (int, str))
        validate_field_type('latest_att_timestamp', latest_att_timestamp,
                            (tuple[int | str, ...], list[int | str]))

        # Validate values
        if isinstance(total_att, str):
            if not total_att.isdigit():
                raise DeserializationError('Field "total_att" must be numeric')
        if isinstance(correct_att, str):
            if not correct_att.isdigit():
                raise DeserializationError('Field "correct_att" must be numeric')
        if isinstance(win_streak, str):
            if not win_streak.isdigit():
                raise DeserializationError('Field "win_streak" must be numeric')
        if isinstance(latest_att_timestamp, list):
            if len(latest_att_timestamp) != 3:
                raise DeserializationError('Field "latest_att_timestamp" must have length 3')

        # Convert types and values
        forms = dict(zip(forms['keys'], forms['values']))
        fav = bool(fav)
        total_att = int(total_att)
        correct_att = int(correct_att)
        win_streak = int(win_streak)
        latest_att_timestamp = tuple(map(int, latest_att_timestamp))

        return cls(
            lemma, translations, forms, phrases, notes, groups, fav,
            total_att, correct_att, win_streak, latest_att_timestamp,
        )
