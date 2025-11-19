"""
Implements the Trainer class that provides a queue generator for
interactive study sessions.

Author: Anenokil
"""

from typing import Iterable
from enum import Enum
from dataclasses import dataclass
import random

from .types import FormPattern, Phrase, Group, EntryID
from .dictionary import Dictionary
from .utils import difficulty, has_article

# Typing aliases used in the module
Pool = list[tuple[EntryID, FormPattern | None, Phrase | None]]


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


@dataclass
class TrainingConfig:
    method: TrainingMethod
    order: TrainingOrder
    entries: EntrySelection
    forms: FormSelection
    groups: list[Group] | None = None


def create_training_config(
        method: TrainingMethod | str,
        order: TrainingOrder | str,
        entries: EntrySelection | str,
        forms: FormSelection | str,
        groups: Iterable[Group] | None
) -> TrainingConfig:
    """
    Create a TrainingConfig instance from mixed inputs.

    This helper accepts either enum members or their string values for the
    configuration fields and returns a fully typed TrainingConfig object.

    Args:
        method: Training method.
        order: Training ordering.
        entries: Which entries to include.
        forms: Which forms to include.
        groups: Optional iterable of groups to restrict the training pool.

    Returns:
        A TrainingConfig instance populated with the provided values.
    """

    return TrainingConfig(
        method=TrainingMethod(method),
        order=TrainingOrder(order),
        entries=EntrySelection(entries),
        forms=FormSelection(forms),
        groups=None if groups is None else list(groups),
    )


class Trainer:
    """Trainer for word practice exercises."""

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

        def filter_by_group() -> Iterable[EntryID]:
            if self._config.groups is None:
                yield from self.dct.get_entry_ids()
            else:
                yield from self.dct.search(
                    [('groups', group) for group in self._config.groups]
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
                fav_ids = {entry_id for entry_id in all_ids if self.dct[entry_id].fav}
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
                    if self.dct[entry_id].fav:
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
                fav_ids = {entry_id for entry_id in ids if self.dct[entry_id].fav}
                if len(fav_ids) <= 10:
                    yield from fav_ids
                else:
                    yield from random.sample(list(fav_ids), 10)

        def select_forms(ids: Iterable[EntryID]) -> Iterable[tuple[EntryID, FormPattern | None]]:
            if self._config.forms == FormSelection.LEMMAS:
                for entry_id in ids:
                    yield entry_id, None
            elif self._config.forms == FormSelection.RANDOM:
                for entry_id in ids:
                    form_patterns = [None] + list(self.dct[entry_id].forms.keys())
                    yield entry_id, random.choice(form_patterns)
            elif self._config.forms == FormSelection.INFLECTED:
                for entry_id in ids:
                    for form_pattern in self.dct[entry_id].forms.keys():
                        yield entry_id, form_pattern
            elif self._config.forms == FormSelection.ALL:
                for entry_id in ids:
                    yield entry_id, None
                    for form_pattern in self.dct[entry_id].forms.keys():
                        yield entry_id, form_pattern

        def selected_phrases(items: Iterable[tuple[EntryID, FormPattern | None]]) -> Iterable[tuple[EntryID, FormPattern | None, Phrase | None]]:
            if self._config.method in (TrainingMethod.PHRASE_TO_TRANS, TrainingMethod.TRANS_TO_PHRASE):
                for key, frm in items:
                    for phr in self.dct[key].phrases.keys():
                        yield key, frm, phr
            else:
                for key, frm in items:
                    yield key, frm, None

        pool = filter_by_group()
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

    def get_task(self) -> tuple[EntryID, FormPattern | None, Phrase | None, set[EntryID]]:
        """
        Pop and return the next training task.

        The returned tuple contains the entry id, an optional form
        pattern, an optional phrase, and a set of homonym entry ids
        (other entries that share the same lemma/translation/form/phrase).

        Returns:
            A 4-tuple: (entry id, form pattern, phrase, homonyms).
        """

        entry_id, form_pattern, phrase = self._pool.pop(0)

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

        self._current_task = entry_id, form_pattern, phrase, homonyms
        return self._current_task

    def get_correct_answers(self) -> list[str]:
        """
        Return the list of accepted correct answers for the current task.

        The returned list contains string answers that should be treated
        as correct for the active task.

        Returns:
            A list of strings representing correct answers.
        """

        entry_id, form_pattern, phrase, _ = self._current_task
        entry = self.dct[entry_id]

        if self._config.method == TrainingMethod.TRANS_TO_WORD:
            if form_pattern is None:
                correct_answers = [entry.lemma]
            else:
                correct_answers = [entry.forms[form_pattern]]
        elif self._config.method == TrainingMethod.WORD_TO_TRANS:
            correct_answers = entry.tr
        elif self._config.method == TrainingMethod.TRANS_TO_PHRASE:
            correct_answers = [phrase]
        elif self._config.method == TrainingMethod.PHRASE_TO_TRANS:
            correct_answers = entry.phrases[phrase]
        else:
            correct_answers = [entry.lemma[:3]]

        return correct_answers

    def is_answer_correct(self, user_answer: str, is_case_sensitive: bool = False) -> bool:
        """
        Check a user's answer against the current task's correct answers.

        The function evaluates whether the provided `user_answer` matches
        any of the accepted correct answers for the current task. If the
        answer is incorrect the task is re-inserted into the pool; its
        position depends on the training order (`DIFFICULT_FIRST` keeps
        difficult items earlier).

        Args:
            user_answer: The answer string provided by the user.
            is_case_sensitive: Whether to compare answers using case
                sensitivity.

        Returns:
            True if the answer is correct, False otherwise.
        """

        entry_id, form_pattern, phrase, _ = self._current_task

        correct_answers = self.get_correct_answers()
        if not is_case_sensitive:
            user_answer = user_answer.lower()
            correct_answers = [word.lower() for word in correct_answers]

        is_correct = user_answer in correct_answers

        if not is_correct:
            if self._config.order == TrainingOrder.DIFFICULT_FIRST:
                self._pool.append((entry_id, form_pattern, phrase))
                self._pool.sort(key=lambda item: difficulty(self.dct[item[0]]), reverse=True)
            else:
                rnd_index = random.randint(0, len(self._pool))
                self._pool.insert(rnd_index, (entry_id, form_pattern, phrase))

        return is_correct
