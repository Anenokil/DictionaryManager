"""
Tests for the Trainer class.

Author: Anenokil
"""

import os
import json
import pytest

from backend.core import (
    Dictionary, Trainer, TrainingConfig,
    TrainingFormat as TF, TrainingOrder as TO,
    EntrySelection as ES, FormSelection as FS,
)
from backend.core.utils import difficulty, has_article


@pytest.fixture(params=[101, 201, 202, 203])
def dct_fxt(request):
    dct_id = request.param
    dct_folder_path = os.path.join('tests', 'test_data')
    dct_fns = os.listdir(dct_folder_path)
    dct_fn = {fn for fn in dct_fns if fn.startswith(f'dct_bundle_{dct_id}_')}.pop()
    dct_path = os.path.join(dct_folder_path, dct_fn, 'dct.json')
    with open(dct_path, 'r') as file:
        data = json.load(file)
    return Dictionary.from_json_dict(data)


@pytest.mark.parametrize(
    'frmt', [
        TF.WORD_TO_TRANS, TF.TRANS_TO_WORD,
        TF.PHRASE_TO_TRANS, TF.TRANS_TO_PHRASE,
        TF.ARTICLES_GERMAN,
    ]
)
@pytest.mark.parametrize(
    'order', [TO.RANDOM, TO.EASY_FIRST, TO.DIFFICULT_FIRST, TO.OLDEST_FIRST]
)
@pytest.mark.parametrize(
    'entries', [ES.ALL, ES.FAV, ES.MOSTLY_FAV, ES.UNANSWERED, ES.RANDOM_10, ES.RANDOM_10_FAV]
)
@pytest.mark.parametrize(
    'forms', [FS.LEMMAS, FS.INFLECTED, FS.RANDOM, FS.ALL]
)
@pytest.mark.parametrize(
    'tags', [None, ['noun'], ['verb'], ['verb', 'haben-verb']]
)
def test_initialize(dct_fxt, frmt, order, entries, forms, tags):
    dct = dct_fxt
    train_config = TrainingConfig(True, frmt, order, entries, forms, tags)

    if (
            frmt in (TF.PHRASE_TO_TRANS, TF.TRANS_TO_PHRASE, TF.ARTICLES_GERMAN)
            and
            forms != FS.LEMMAS
    ):
        return

    trainer = Trainer(dct, train_config)
    trainer.initialize()
    pool = trainer.pool

    # 1. Check absence of duplicates
    assert len(pool) == len(set(pool))

    if entries in (ES.ALL, ES.MOSTLY_FAV, ES.RANDOM_10):
        allowed_entries = set(dct)
    elif entries in (ES.FAV, ES.RANDOM_10_FAV):
        allowed_entries = {entry for entry in dct if entry.is_fav}
    elif entries == ES.UNANSWERED:
        allowed_entries = {entry for entry in dct if entry.total_att == 0}

    if tags is not None:
        allowed_entries = {entry for entry in allowed_entries if set(tags).issubset(entry.tags)}

    if frmt in (TF.WORD_TO_TRANS, TF.TRANS_TO_WORD):
        if forms == FS.LEMMAS:
            allowed_tuples = {(entry, None, None) for entry in allowed_entries}
        elif forms == FS.INFLECTED:
            allowed_entries = {
                entry for entry in allowed_entries
                if entry.n_gram_forms != 0
            }
            allowed_tuples = {
                (entry, gram_form, None)
                for entry in allowed_entries
                for gram_form in entry.forms
            }
        elif forms in (FS.ALL, FS.RANDOM):
            allowed_tuples = {
                (entry, gram_form, None)
                for entry in allowed_entries
                for gram_form in set(entry.forms).union({None})
            }
    elif frmt in (TF.PHRASE_TO_TRANS, TF.TRANS_TO_PHRASE):
        allowed_entries = {
            entry for entry in allowed_entries
            if entry.n_phrases != 0
        }
        allowed_tuples = {
            (entry, None, phrase)
            for entry in allowed_entries
            for phrase in entry.phrases
        }
    elif frmt == TF.ARTICLES_GERMAN:
        allowed_entries = {
            entry for entry in allowed_entries
            if all(has_article(lemma.lower(), ('der ', 'die ', 'das ')) for lemma in entry.variants)
        }
        allowed_tuples = {
            (entry, None, None)
            for entry in allowed_entries
        }

    has_random_content = (
        entries in (ES.MOSTLY_FAV, ES.RANDOM_10, ES.RANDOM_10_FAV) or
        frmt in (TF.WORD_TO_TRANS, TF.TRANS_TO_WORD) and forms == FS.RANDOM
    )

    # 2. Check content
    if has_random_content:
        assert set(pool).issubset(allowed_tuples)

        gotten_ids = {t[0] for t in pool}

        if entries == ES.MOSTLY_FAV:
            required_ids = {entry for entry in allowed_entries if entry.is_fav}
            assert required_ids.issubset(gotten_ids)
            assert len(gotten_ids) == min(int(1.25 * len(required_ids)), len(allowed_entries))
        elif entries in (ES.RANDOM_10, ES.RANDOM_10_FAV):
            assert len(gotten_ids) == min(10, len(allowed_entries))

        if forms == FS.RANDOM:
            assert len(gotten_ids) == len(pool)
    else:
        assert set(pool) == allowed_tuples

    # 3. Check order
    gotten_ids = [t[0] for t in pool]
    if order == TO.EASY_FIRST:
        assert gotten_ids == sorted(gotten_ids, key=lambda entry: difficulty(entry))
    elif order == TO.DIFFICULT_FIRST:
        assert gotten_ids == sorted(gotten_ids, key=lambda entry: difficulty(entry), reverse=True)
    elif order == TO.OLDEST_FIRST:
        assert gotten_ids == sorted(gotten_ids, key=lambda entry: entry.latest_att_timestamp)
