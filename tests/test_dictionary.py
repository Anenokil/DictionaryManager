"""
Tests for the Dictionary class.

Author: Anenokil
"""

from typing import Iterable, TypeVar
from copy import deepcopy
import os
import json
import pytest

from backend.core import Dictionary, InvalidTagError

T = TypeVar('T')


def to_type(iterable: Iterable[T], target_type: str) -> Iterable[T]:
    if target_type == 'list':
        return list(iterable)
    if target_type == 'tuple':
        return tuple(iterable)
    if target_type == 'set':
        return set(iterable)
    if target_type == 'generator':
        return (val for val in iterable)
    raise NotImplementedError(f'Unknown target type: {target_type}')


@pytest.fixture
def dct_small(request):
    dct_path = os.path.join('tests', 'test_data', 'dct_bundle_201_ger_eng_29/dct.json')
    with open(dct_path, 'r') as file:
        data = json.load(file)
    return Dictionary.from_json_dict(data)


@pytest.mark.parametrize('tag', ['noun', 'difficult', 'new', 'plural other', 'invalid'])
@pytest.mark.parametrize(
    'entry_indexes', [
        [],
        [0],
        [0, 16, 3],
        [9, 11, 12],
        [27],
        [28],
        [3, 7, 10, 11, 15, 16, 25, 27, 28],
        [27, 7, 3, 10, 15, 28, 16, 25, 11],
        'all',
    ]
)
@pytest.mark.parametrize('iter_type', ['list', 'tuple', 'set', 'generator'])
def test_add_tag_to_entries(dct_small, tag, entry_indexes, iter_type):
    dct = dct_small

    if entry_indexes == 'all':
        entries = list(dct)
    else:
        entries = [dct[index] for index in entry_indexes]
    entries_ = to_type(entries, iter_type)

    if tag in dct.tags:
        tag_entries = dct.search(tags=[tag])

        dct.add_tag_to_entries(tag, entries_)

        assert dct.search(tags=[tag]) == tag_entries.union(entries)
    else:
        state_before = deepcopy(dct.to_dict())

        # Operation should raise on invalid arguments
        with pytest.raises(InvalidTagError):
            dct.add_tag_to_entries(tag, entries_)

        state_after = dct.to_dict()

        # State must remain unchanged after failed operation
        assert state_after == state_before


@pytest.mark.parametrize('tag', ['noun', 'difficult', 'new', 'plural other', 'invalid'])
@pytest.mark.parametrize(
    'entry_indexes', [
        [],
        [0],
        [0, 16, 3],
        [9, 11, 12],
        [27],
        [28],
        [3, 7, 10, 11, 15, 16, 25, 27, 28],
        [27, 7, 3, 10, 15, 28, 16, 25, 11],
        'all',
    ]
)
@pytest.mark.parametrize('iter_type', ['list', 'tuple', 'set', 'generator'])
def test_remove_tag_from_entries(dct_small, tag, entry_indexes, iter_type):
    dct = dct_small

    if entry_indexes == 'all':
        entries = list(dct)
    else:
        entries = [dct[index] for index in entry_indexes]
    entries_ = to_type(entries, iter_type)

    if tag in dct.tags:
        tag_entries = dct.search(tags=[tag])

        dct.remove_tag_from_entries(tag, entries_)

        assert dct.search(tags=[tag]) == tag_entries.difference(entries)
    else:
        state_before = deepcopy(dct.to_dict())

        # Operation should raise on invalid arguments
        with pytest.raises(InvalidTagError):
            dct.remove_tag_from_entries(tag, entries_)

        state_after = dct.to_dict()

        # State must remain unchanged after failed operation
        assert state_after == state_before


@pytest.mark.parametrize('tag', ['', 'new tag', 'verb', 'new'])
@pytest.mark.parametrize('is_default', [True, False])
def test_add_tag(dct_small, tag, is_default):
    dct = dct_small

    tag_entries = dct.search(tags=[tag])

    dct.add_tag(tag, is_default)

    assert tag in dct.tags
    assert dct.search(tags=[tag]) == tag_entries
    if is_default:
        assert dct.is_default_tag(tag)
        assert tag in dct.default_tags
    else:
        assert not dct.is_default_tag(tag)
        assert tag not in dct.default_tags


@pytest.mark.parametrize('target_tag', ['adjective', 'new'])
@pytest.mark.parametrize('new_tag', ['', 'adj', 'verb', 'adjective', 'new'])
def test_rename_tag(dct_small, target_tag, new_tag):
    dct = dct_small

    target_tag_entries = dct.search(tags=[target_tag])
    new_tag_entries = dct.search(tags=[new_tag])

    dct.rename_tag(target_tag, new_tag)

    assert new_tag in dct.tags
    assert dct.search(tags=[new_tag]) == target_tag_entries.union(new_tag_entries)
    for entry in new_tag_entries:
        assert new_tag in entry.tags

    if new_tag != target_tag:
        assert target_tag not in dct.tags
        assert target_tag not in dct.default_tags
        assert dct.search(tags=[target_tag]) == set()
        for entry in new_tag_entries:
            assert target_tag not in entry.tags


@pytest.mark.parametrize('target_tag', ['', 'invalid'])
@pytest.mark.parametrize('new_tag', ['', 'adj', 'verb', 'new', 'invalid'])
def test_rename_tag_bad(dct_small, target_tag, new_tag):
    dct = dct_small

    state_before = deepcopy(dct.to_dict())

    # Operation should raise on invalid rename
    with pytest.raises(InvalidTagError):
        dct.rename_tag(target_tag, new_tag)

    state_after = dct.to_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_delete_tag(dct_small, tag):
    dct = dct_small

    tag_entries = dct.search(tags=[tag])

    dct.delete_tag(tag)

    assert tag not in dct.tags
    assert tag not in dct.default_tags
    assert dct.search(tags=[tag]) == set()
    for entry in tag_entries:
        assert tag not in entry.tags


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_delete_tag_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.delete_tag(tag)

    state_after = dct.to_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_mark_tag_as_default(dct_small, tag):
    dct = dct_small

    default_tags = deepcopy(dct.default_tags)

    dct.mark_tag_as_default(tag)

    assert dct.is_default_tag(tag)
    assert dct.default_tags == default_tags.union({tag})


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_mark_tag_as_default_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.mark_tag_as_default(tag)

    state_after = dct.to_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_unmark_tag_as_default(dct_small, tag):
    dct = dct_small

    default_tags = deepcopy(dct.default_tags)

    dct.mark_tag_as_default(tag, False)

    assert not dct.is_default_tag(tag)
    assert dct.default_tags == default_tags.difference({tag})


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_unmark_tag_as_default_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.mark_tag_as_default(tag, False)

    state_after = dct.to_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before
