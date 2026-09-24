"""
Implements the Trainer class that provides a queue generator for
interactive study sessions.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable
from enum import Enum
import random

from .types import GramForm, Phrase, Tag, SerializedData
from .errors import UnknownVersionError
from .entry import Entry
from .dictionary import Dictionary
from .utils import (
    difficulty, has_article, validate_required_fields, validate_field_type,
)

# Typing aliases used in the module
Pool = list[tuple[Entry, GramForm | None, Phrase | None]]


class TrainingFormat(Enum):
    WORD_TO_TRANS = 'word_to_translation'
    TRANS_TO_WORD = 'translation_to_word'
    PHRASE_TO_TRANS = 'phrase_to_translation'
    TRANS_TO_PHRASE = 'translation_to_phrase'
    ARTICLES_GERMAN = 'articles_german_(der-die-das)'


class TrainingOrder(Enum):
    RANDOM = 'random'
    EASY_FIRST = 'easy_first'
    DIFFICULT_FIRST = 'difficult_first'
    OLDEST_FIRST = 'oldest_first'


class EntrySelection(Enum):
    ALL = 'all'
    FAV = 'fav'
    MOSTLY_FAV = 'mostly_fav'
    UNANSWERED = 'unanswered'
    RANDOM_10 = 'random_sample_10'
    RANDOM_10_FAV = 'fav_random_sample_10'
    #RANDOM = 'random_sample'
    #RANDOM_FAV = 'fav_random_sample'


class FormSelection(Enum):
    LEMMAS = 'lemmas_only'
    INFLECTED = 'inflected_only'
    RANDOM = 'random_form'
    ALL = 'all'


class TrainingConfig:
    """ TODO """

    _schema_version = 1

    def __init__(
            self,
            is_case_sensitive: bool = False,
            format: TrainingFormat = TrainingFormat.TRANS_TO_WORD,
            order: TrainingOrder = TrainingOrder.DIFFICULT_FIRST,
            entries: EntrySelection = EntrySelection.MOSTLY_FAV,
            forms: FormSelection = FormSelection.RANDOM,
            tags: list[Tag] | None = None,
    ):
        self.is_case_sensitive = is_case_sensitive
        self.format = format
        self.order = order
        self.entries = entries
        self.forms = forms
        self.tags = tags

    @classmethod
    def from_dict(cls, data: SerializedData):
        config = cls()
        config.load_from_dict(data)
        return config

    def set_defaults(self):
        self.is_case_sensitive = True
        self.format = TrainingFormat.TRANS_TO_WORD
        self.order = TrainingOrder.DIFFICULT_FIRST
        self.entries = EntrySelection.MOSTLY_FAV
        self.forms = FormSelection.RANDOM
        self.tags = None

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'is_case_sensitive': self.is_case_sensitive,
            'format': self.format.value,
            'order': self.order.value,
            'entries': self.entries.value,
            'forms': self.forms.value,
            'tags': self.tags,
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.is_case_sensitive = data['is_case_sensitive']
        self.format = TrainingFormat(data['format'])
        self.order = TrainingOrder(data['order'])
        self.entries = EntrySelection(data['entries'])
        self.forms = FormSelection(data['forms'])
        self.tags = data['tags']

    @staticmethod
    def _check_and_migrate(data: SerializedData) -> SerializedData:
        validate_required_fields(data, ('version',))
        validate_field_type('version', data['version'], int)

        version: int = data['version']
        if version == 1:
            TrainingConfig._validate_data(data)
            return data
        raise UnknownVersionError(TrainingConfig.__name__, version)

    @staticmethod
    def _validate_data(data: SerializedData):
        str_fields = ('format', 'order', 'entries', 'forms')
        required_fields = str_fields + ('is_case_sensitive', 'tags')
        validate_required_fields(data, required_fields)

        for field_name in str_fields:
            validate_field_type(field_name, data[field_name], str)
        validate_field_type('is_case_sensitive', data['is_case_sensitive'], bool)
        validate_field_type('tags', data['tags'], (list[str], NoneType))


class Trainer:
    """
    Trainer for word-practice exercises.

    This class builds and manages a queue (the training pool) of tasks
    derived from a `Dictionary` according to a `TrainingConfig`. Each task
    is a tuple (entry, gram_form | None, phrase | None) and may be
    served to the caller via `get_task`. The trainer also evaluates user
    answers and reinserts failed tasks back into the pool according to the
    configured ordering.

    Attributes:
    ----------
    - dct: Reference to the dictionary containing entries used to build tasks.
    - pool: Read-only view of the current internal task pool.
    - config: Active training configuration that controls selection and ordering.

    Protected Attributes:
    --------------------
    - _pool: Internal list of tasks awaiting presentation to the user.
    - _config: Internal copy of the active configuration.
    - _current_task: The currently active task (set by `get_task`) or `None` when no task is active.
    """

    def __init__(self, dct: Dictionary, config: TrainingConfig):
        """
        Initialize a Trainer instance.

        The trainer holds a reference to the provided dictionary and a
        training configuration. The internal pool of tasks is initially
        empty; call :meth:`initialize` to populate it according to the
        configuration.

        Args:
            dct: The Dictionary instance containing entries.
            config: TrainingConfig to control training.
        """

        self.dct = dct
        self._pool: Pool = []
        self._config = config
        self._current_task = None

    @property
    def pool(self) -> Pool:
        """
        Return the current training pool.

        Returns:
            The current task pool.
        """

        return self._pool

    @property
    def config(self) -> TrainingConfig:
        """
        Return the active training configuration.

        Returns:
            The TrainingConfig currently used by the trainer.
        """

        return self._config

    def reconfigure(self, config: TrainingConfig):
        """
        Replace the trainer's configuration.

        Use this to change training parameters (format, order, filters,
        etc.). After reconfiguring, `initialize` should be called to rebuild
        the internal pool according to the new settings.

        Args:
            config: New TrainingConfig to apply.
        """

        self._config = config

    def initialize(self):
        """
        Build the internal training pool according to the configuration.

        This method applies a sequence of filters to generate a
        list of tasks. The resulting pool ordering is controlled by
        the configuration's `order` option.

        After calling this method the trainer is ready to serve tasks
        via `get_task`.
        """

        def filter_by_tags() -> Iterable[Entry]:
            if not self._config.tags:
                yield from self.dct
            else:
                yield from self.dct.search(tags=self._config.tags)

        def filter_by_format(entries: Iterable[Entry]) -> Iterable[Entry]:
            if self._config.format == TrainingFormat.ARTICLES_GERMAN:
                for entry in entries:
                    lemma = entry.lemma
                    if has_article(lemma.lower(), ('der ', 'die ', 'das ')):
                        yield entry
            elif self._config.format in (
                    TrainingFormat.PHRASE_TO_TRANS, TrainingFormat.TRANS_TO_PHRASE
            ):
                for entry in entries:
                    if entry.n_phrases != 0:
                        yield entry
            else:
                yield from entries

        def filter_by_forms(entries: Iterable[Entry]) -> Iterable[Entry]:
            if self._config.forms == FormSelection.INFLECTED:
                for entry in entries:
                    if entry.n_gram_forms != 0:
                        yield entry
            else:
                yield from entries

        def filter_by_entries(entries: Iterable[Entry]) -> Iterable[Entry]:
            if self._config.entries == EntrySelection.ALL:  # Учить все слова
                yield from entries
            elif self._config.entries == EntrySelection.MOSTLY_FAV:  # Учить преимущественно избранные слова
                all_entries = set(entries)
                fav_entries = {entry for entry in all_entries if entry.is_fav}
                unfav_entries = all_entries - fav_entries

                n_fav = len(fav_entries)
                n_unfav = len(unfav_entries)

                if n_unfav > n_fav:
                    unfav_entries = sorted(unfav_entries, key=lambda e: e.latest_att_timestamp)
                    unfav_entries = unfav_entries[:n_fav]
                if n_unfav > n_fav // 4:
                    unfav_entries = random.sample(list(unfav_entries), n_fav // 4)

                # Помимо всех избранных слов (пусть их количество N) добавим N // 4 остальных слов
                # Выберем их из самых давно не отвечаемых слов

                yield from fav_entries
                yield from unfav_entries
            elif self._config.entries == EntrySelection.FAV:  # Учить только избранные слова
                for entry in entries:
                    if entry.is_fav:
                        yield entry
            elif self._config.entries == EntrySelection.UNANSWERED:  # Учить только неотвеченные слова
                for entry in entries:
                    if entry.correct_att == 0:
                        yield entry
            elif self._config.entries == EntrySelection.RANDOM_10:  # Учить 10 случайных слов
                entries = list(entries)
                if len(entries) <= 10:
                    yield from entries
                else:
                    yield from random.sample(entries, 10)
            elif self._config.entries == EntrySelection.RANDOM_10_FAV:  # Учить 10 случайных избранных слов
                fav_entries = {entry for entry in entries if entry.is_fav}
                if len(fav_entries) <= 10:
                    yield from fav_entries
                else:
                    yield from random.sample(list(fav_entries), 10)

        def select_forms(entries: Iterable[Entry]) -> Iterable[tuple[Entry, GramForm | None]]:
            if self._config.forms == FormSelection.LEMMAS:
                for entry in entries:
                    yield entry, None
            elif self._config.forms == FormSelection.RANDOM:
                for entry in entries:
                    gram_forms = [None] + list(entry.forms.keys())
                    yield entry, random.choice(gram_forms)
            elif self._config.forms == FormSelection.INFLECTED:
                for entry in entries:
                    for gram_form in entry.forms.keys():
                        yield entry, gram_form
            elif self._config.forms == FormSelection.ALL:
                for entry in entries:
                    yield entry, None
                    for gram_form in entry.forms.keys():
                        yield entry, gram_form

        def select_phrases(
                items: Iterable[tuple[Entry, GramForm | None]]
        ) -> Iterable[tuple[Entry, GramForm | None, Phrase | None]]:
            if self._config.format in (
                    TrainingFormat.PHRASE_TO_TRANS,
                    TrainingFormat.TRANS_TO_PHRASE,
            ):
                for entry, form in items:
                    for phrase in entry.phrases.keys():
                        yield entry, form, phrase
            else:
                for entry, form in items:
                    yield entry, form, None

        pool = filter_by_tags()
        pool = filter_by_format(pool)
        pool = filter_by_forms(pool)
        pool = filter_by_entries(pool)
        pool = select_forms(pool)
        pool = select_phrases(pool)

        if self._config.order == TrainingOrder.RANDOM:
            self._pool = list(pool)
            random.shuffle(self._pool)
        elif self._config.order == TrainingOrder.EASY_FIRST:
            self._pool = sorted(pool, key=lambda item: difficulty(item[0]))
        elif self._config.order == TrainingOrder.DIFFICULT_FIRST:
            self._pool = sorted(pool, key=lambda item: difficulty(item[0]), reverse=True)
        elif self._config.order == TrainingOrder.OLDEST_FIRST:
            self._pool = sorted(pool, key=lambda item: item[0].latest_att_timestamp)

        self._current_task = None

    def is_finished(self) -> bool:
        """
        Return True when there are no remaining tasks in the pool.

        Returns:
            True if the training pool is empty, False otherwise.
        """

        return len(self._pool) == 0

    def get_task(self) -> tuple[Entry, GramForm | None, Phrase | None, set[Entry]]:
        """
        Pop and return the next training task.

        The returned tuple contains the entry, an optional grammatical
        form, an optional phrase, and a set of homonyms (other
        entries that share the same lemma/translation/form/phrase).

        Returns:
            A 4-tuple: (entry, grammatical form, phrase, homonyms).
        """

        entry, gram_form, phrase = self._pool.pop(0)

        if self._config.format == TrainingFormat.WORD_TO_TRANS:
            related = self.dct.search(lemma=entry.lemma)
        elif self._config.format == TrainingFormat.TRANS_TO_WORD:
            related = set().union(*(
                self.dct.search(translations=[tr]) for tr in entry.tr
            ))
        elif self._config.format == TrainingFormat.ARTICLES_GERMAN:
            related = {
                e for e in self.dct.search(lemma=entry.lemma)
                if has_article(e.lemma.lower(), ('der ', 'die ', 'das '))
            }
        else:
            related = set()
        related -= {entry}

        self._current_task = entry, gram_form, phrase, related
        return self._current_task

    def get_correct_answers(self) -> list[str]:
        """
        Return the list of accepted correct answers for the current task.

        The returned list contains string answers that should be treated
        as correct for the active task.

        Returns:
            A list of strings representing correct answers.
        """

        entry, gram_form, phrase, _ = self._current_task

        if self._config.format == TrainingFormat.TRANS_TO_WORD:
            if gram_form is None:
                correct_answers = entry.variants
            else:
                correct_answers = entry.forms[gram_form]
        elif self._config.format == TrainingFormat.WORD_TO_TRANS:
            correct_answers = entry.tr
        elif self._config.format == TrainingFormat.TRANS_TO_PHRASE:
            correct_answers = [phrase]
        elif self._config.format == TrainingFormat.PHRASE_TO_TRANS:
            correct_answers = entry.phrases[phrase]
        else:
            correct_answers = [entry.lemma[:3]]

        return correct_answers

    def is_answer_correct(self, user_answer: str) -> bool:
        """
        Check a user's answer against the current task's correct answers.

        The function evaluates whether the provided `user_answer` matches
        any of the accepted correct answers for the current task. If the
        answer is incorrect the task is re-inserted into the pool; its
        position depends on the training order (`DIFFICULT_FIRST` keeps
        difficult items earlier).

        Args:
            user_answer: The answer string provided by the user.

        Returns:
            True if the answer is correct, False otherwise.
        """

        entry, gram_form, phrase, _ = self._current_task

        correct_answers = self.get_correct_answers()
        if not self._config.is_case_sensitive:
            user_answer = user_answer.lower()
            correct_answers = [word.lower() for word in correct_answers]

        is_correct = user_answer in correct_answers

        if not is_correct:
            if self._config.order == TrainingOrder.RANDOM:
                rnd_index = random.randint(0, len(self._pool))
                self._pool.insert(rnd_index, (entry, gram_form, phrase))
            else:
                self._pool.append((entry, gram_form, phrase))
                if self._config.order == TrainingOrder.EASY_FIRST:
                    self._pool.sort(key=lambda item: difficulty(item[0]))
                elif self._config.order == TrainingOrder.DIFFICULT_FIRST:
                    self._pool.sort(key=lambda item: difficulty(item[0]), reverse=True)
                else:
                    self._pool.sort(key=lambda item: item[0].latest_att_timestamp)

        return is_correct
