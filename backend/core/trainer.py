"""
Implements the Trainer class that provides a queue generator for
interactive study sessions.

Author: Anenokil
"""

from types import NoneType
from typing import Iterable
from enum import Enum
import random

from .types import GramForm, Phrase, Tag, EntryID, SerializedData
from .errors import UnknownVersionError
from .dictionary import Dictionary
from .utils import (
    difficulty, has_article, validate_required_fields, validate_field_type,
)

# Typing aliases used in the module
Pool = list[tuple[EntryID, GramForm | None, Phrase | None]]


class TrainingMethod(Enum):
    WORD_TO_TRANS = 'word_to_translation'
    TRANS_TO_WORD = 'translation_to_word'
    PHRASE_TO_TRANS = 'phrase_to_translation'
    TRANS_TO_PHRASE = 'translation_to_phrase'
    ARTICLES_GERMAN = 'articles_german_(der-die-das)'


class TrainingOrder(Enum):
    RANDOM = 'random'
    #EASY_FIRST = 'easy_first'
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
            method: TrainingMethod = TrainingMethod.TRANS_TO_WORD,
            order: TrainingOrder = TrainingOrder.DIFFICULT_FIRST,
            entries: EntrySelection = EntrySelection.MOSTLY_FAV,
            forms: FormSelection = FormSelection.RANDOM,
            tag: Tag | None = None
            #tags: list[Tag] | None = None,  # TODO
    ):
        self.is_case_sensitive = is_case_sensitive
        self.method = method
        self.order = order
        self.entries = entries
        self.forms = forms
        self.tag = tag

    def set_defaults(self):
        self.is_case_sensitive = True
        self.method = TrainingMethod.TRANS_TO_WORD
        self.order = TrainingOrder.DIFFICULT_FIRST
        self.entries = EntrySelection.MOSTLY_FAV
        self.forms = FormSelection.RANDOM
        self.tag = None

    def to_dict(self) -> SerializedData:
        return {
            'version': self._schema_version,
            'is_case_sensitive': self.is_case_sensitive,
            'method': self.method.value,
            'order': self.order.value,
            'entries': self.entries.value,
            'forms': self.forms.value,
            'tag': self.tag,
        }

    def load_from_dict(self, data: SerializedData):
        data = self._check_and_migrate(data)

        self.is_case_sensitive = data['is_case_sensitive']
        self.method = TrainingMethod(data['method'])
        self.order = TrainingOrder(data['order'])
        self.entries = EntrySelection(data['entries'])
        self.forms = FormSelection(data['forms'])
        self.tag = data['tag']

    @classmethod
    def from_dict(cls, data: SerializedData):
        config = cls()
        config.load_from_dict(data)
        return config

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
        str_fields = ('method', 'order', 'entries', 'forms')
        required_fields = str_fields + ('is_case_sensitive', 'tag',)
        validate_required_fields(data, required_fields)

        for field_name in str_fields:
            validate_field_type(field_name, data[field_name], str)
        validate_field_type('is_case_sensitive', data['is_case_sensitive'], bool)
        validate_field_type('tag', data['tag'], (str, NoneType))


class Trainer:
    """
    Trainer for word-practice exercises.

    This class builds and manages a queue (the training pool) of tasks
    derived from a `Dictionary` according to a `TrainingConfig`. Each task
    is a tuple (entry_id, gram_form | None, phrase | None) and may be
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

        Use this to change training parameters (method, order, filters,
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

        def filter_by_tag() -> Iterable[EntryID]:
            if self._config.tags is None:
                yield from self.dct.get_entry_ids()
            else:
                yield from self.dct.search(
                    [('tags', tag) for tag in self._config.tags]
                )

        def filter_by_method(ids: Iterable[EntryID]) -> Iterable[EntryID]:
            if self._config.method == TrainingMethod.ARTICLES_GERMAN:
                for entry_id in ids:
                    lemma = self.dct[entry_id].lemma
                    if len(lemma) > 4 and lemma[0:4].lower() in ('der ', 'die ', 'das '):
                        yield entry_id
            else:
                yield from ids

        def filter_by_forms(ids: Iterable[EntryID]) -> Iterable[EntryID]:
            if self._config.forms == FormSelection.INFLECTED:
                for entry_id in ids:
                    if self.dct[entry_id].count_f != 0:
                        yield entry_id
            else:
                yield from ids

        def filter_by_entries(ids: Iterable[EntryID]) -> Iterable[EntryID]:
            if self._config.entries == EntrySelection.ALL:  # Учить все слова
                yield from ids
            elif self._config.entries == EntrySelection.MOSTLY_FAV:  # Учить преимущественно избранные слова
                all_ids = set(ids)
                fav_ids = {entry_id for entry_id in all_ids if self.dct[entry_id].is_fav}
                unfav_ids = all_ids - fav_ids

                n_fav = len(fav_ids)
                n_unfav = len(unfav_ids)

                unfav_ids = sorted(unfav_ids, key=lambda i: self.dct[i].latest_att_timestamp)
                if n_fav > 4 * n_unfav:
                    unfav_ids = unfav_ids[:min(n_unfav, n_fav // 2)]
                    unfav_ids = random.sample(unfav_ids, n_fav // 4)

                # Помимо всех избранных слов (пусть их количество N) добавим N // 4 остальных слов
                # Выберем их из самых давно не отвечаемых слов

                yield from fav_ids
                yield from unfav_ids
            elif self._config.entries == EntrySelection.FAV:  # Учить только избранные слова
                for entry_id in ids:
                    if self.dct[entry_id].is_fav:
                        yield entry_id
            elif self._config.entries == EntrySelection.UNANSWERED:  # Учить только неотвеченные слова
                for entry_id in ids:
                    if self.dct[entry_id].correct_att == 0:
                        yield entry_id
            elif self._config.entries == EntrySelection.RANDOM_10:  # Учить 10 случайных слов
                ids = list(ids)
                if len(ids) <= 10:
                    yield from ids
                else:
                    yield from random.sample(ids, 10)
            elif self._config.entries == EntrySelection.RANDOM_10_FAV:  # Учить 10 случайных избранных слов
                fav_ids = {entry_id for entry_id in ids if self.dct[entry_id].is_fav}
                if len(fav_ids) <= 10:
                    yield from fav_ids
                else:
                    yield from random.sample(list(fav_ids), 10)

        def select_forms(ids: Iterable[EntryID]) -> Iterable[tuple[EntryID, GramForm | None]]:
            if self._config.forms == FormSelection.LEMMAS:
                for entry_id in ids:
                    yield entry_id, None
            elif self._config.forms == FormSelection.RANDOM:
                for entry_id in ids:
                    gram_forms = [None] + list(self.dct[entry_id].forms.keys())
                    yield entry_id, random.choice(gram_forms)
            elif self._config.forms == FormSelection.INFLECTED:
                for entry_id in ids:
                    for gram_form in self.dct[entry_id].forms.keys():
                        yield entry_id, gram_form
            elif self._config.forms == FormSelection.ALL:
                for entry_id in ids:
                    yield entry_id, None
                    for gram_form in self.dct[entry_id].forms.keys():
                        yield entry_id, gram_form

        def selected_phrases(
                items: Iterable[tuple[EntryID, GramForm | None]]
        ) -> Iterable[tuple[EntryID, GramForm | None, Phrase | None]]:
            if self._config.method in (TrainingMethod.PHRASE_TO_TRANS, TrainingMethod.TRANS_TO_PHRASE):
                for key, form in items:
                    for phrase in self.dct[key].phrases.keys():
                        yield key, form, phrase
            else:
                for key, form in items:
                    yield key, form, None

        pool = filter_by_tag()
        pool = filter_by_method(pool)
        pool = filter_by_forms(pool)
        pool = filter_by_entries(pool)
        pool = select_forms(pool)
        pool = selected_phrases(pool)

        if self._config.order == TrainingOrder.RANDOM:
            self._pool = list(pool)
            random.shuffle(self._pool)
        elif self._config.order == TrainingOrder.DIFFICULT_FIRST:
            self._pool = sorted(pool, key=lambda item: difficulty(self.dct[item[0]]), reverse=True)
        elif self._config.order == TrainingOrder.OLDEST_FIRST:
            self._pool = sorted(pool, key=lambda item: self.dct[item[0]].latest_att_timestamp)

        self._current_task = None

    def is_finished(self) -> bool:
        """
        Return True when there are no remaining tasks in the pool.

        Returns:
            True if the training pool is empty, False otherwise.
        """

        return len(self._pool) == 0

    def get_task(self) -> tuple[EntryID, GramForm | None, Phrase | None, set[EntryID]]:
        """
        Pop and return the next training task.

        The returned tuple contains the entry id, an optional grammatical
        form, an optional phrase, and a set of homonym entry ids (other
        entries that share the same lemma/translation/form/phrase).

        Returns:
            A 4-tuple: (entry id, grammatical form, phrase, homonyms).
        """

        entry_id, gram_form, phrase = self._pool.pop(0)

        if self._config.method == TrainingMethod.WORD_TO_TRANS:
            lemma = self.dct[entry_id].lemma
            homonyms = self.dct.search([('lemmas', lemma)])
        elif self._config.method == TrainingMethod.TRANS_TO_WORD:
            translations = self.dct[entry_id].tr
            homonyms = self.dct.search([('translations', tr) for tr in translations])
        elif self._config.method == TrainingMethod.ARTICLES_GERMAN:
            lemma = self.dct[entry_id].lemma
            homonyms = set(
                eid for eid in self.dct.get_entry_ids()
                if lemma == self.dct[eid].lemma and
                has_article(self.dct[eid].lemma, ('der ', 'die ', 'das '))
            )
        else:
            homonyms = set()
        homonyms -= {entry_id}

        self._current_task = entry_id, gram_form, phrase, homonyms
        return self._current_task

    def get_correct_answers(self) -> list[str]:
        """
        Return the list of accepted correct answers for the current task.

        The returned list contains string answers that should be treated
        as correct for the active task.

        Returns:
            A list of strings representing correct answers.
        """

        entry_id, gram_form, phrase, _ = self._current_task
        entry = self.dct[entry_id]

        if self._config.method == TrainingMethod.TRANS_TO_WORD:
            if gram_form is None:
                correct_answers = [entry.lemma]
            else:
                correct_answers = [entry.forms[gram_form]]
        elif self._config.method == TrainingMethod.WORD_TO_TRANS:
            correct_answers = entry.tr
        elif self._config.method == TrainingMethod.TRANS_TO_PHRASE:
            correct_answers = [phrase]
        elif self._config.method == TrainingMethod.PHRASE_TO_TRANS:
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

        entry_id, gram_form, phrase, _ = self._current_task

        correct_answers = self.get_correct_answers()
        if not self._config.is_case_sensitive:
            user_answer = user_answer.lower()
            correct_answers = [word.lower() for word in correct_answers]

        is_correct = user_answer in correct_answers

        if not is_correct:
            if self._config.order == TrainingOrder.DIFFICULT_FIRST:
                self._pool.append((entry_id, gram_form, phrase))
                self._pool.sort(key=lambda item: difficulty(self.dct[item[0]]), reverse=True)
            else:
                rnd_index = random.randint(0, len(self._pool))
                self._pool.insert(rnd_index, (entry_id, gram_form, phrase))

        return is_correct
