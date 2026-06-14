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
        return (eid for eid in iterable)
    raise NotImplementedError(f'Unknown target type: {target_type}')


@pytest.fixture
def dct_small(request):
    dct_path = os.path.join('tests', 'test_data', 'dct_201_ger_eng_29.json')
    with open(dct_path, 'r') as file:
        data = json.load(file)
    return Dictionary.from_json_dict(data)


@pytest.mark.parametrize('tag', ['noun', 'difficult', 'new', 'plural other', 'invalid'])
@pytest.mark.parametrize(
    'entry_ids', [
        [],
        [3],
        [3, 3, 3],
        [3, 80, 6],
        [36, 44, 45],
        [745],
        [3156],
        [6, 32, 43, 44, 70, 80, 408, 745, 3156],
        [745, 32, 6, 43, 70, 3156, 80, 408, 44],
        [44, 745, 32, 6, 43, 43, 70, 3156, 80, 408, 44, 6, 32],
        'all',
        [9999],
        [9997, 9999, 9998],
        [3, 9999],
        [745, 32, 6, 43, 70, 3156, 9999, 80, 408, 44],
        [44, 745, 32, 6, 43, 43, 70, 9999, 3156, 80, 408, 44, 6, 32],
    ]
)
@pytest.mark.parametrize('tags_type', ['list', 'tuple', 'set', 'generator'])
def test_add_tag_to_entries(dct_small, tag, entry_ids, tags_type):
    dct = dct_small

    if entry_ids == 'all':
        entry_ids = list(dct.iter_entry_ids())
    entry_ids_ = to_type(entry_ids, tags_type)

    if (tag in dct.tags) and set(entry_ids).issubset(set(dct.iter_entry_ids())):
        tag_ids = dct.search(tags=[tag])

        dct.add_tag_to_entries(tag, entry_ids_)

        assert dct.search(tags=[tag]) == tag_ids.union(entry_ids)
    else:
        state_before = deepcopy(dct.to_json_dict())

        # Operation should raise on invalid arguments
        with pytest.raises(KeyError):
            dct.add_tag_to_entries(tag, entry_ids_)

        state_after = dct.to_json_dict()

        # State must remain unchanged after failed operation
        assert state_after == state_before


@pytest.mark.parametrize('tag', ['noun', 'difficult', 'new', 'plural other', 'invalid'])
@pytest.mark.parametrize(
    'entry_ids', [
        [],
        [3],
        [3, 3, 3],
        [3, 80, 6],
        [36, 44, 45],
        [745],
        [3156],
        [6, 32, 43, 44, 70, 80, 408, 745, 3156],
        [745, 32, 6, 43, 70, 3156, 80, 408, 44],
        [44, 745, 32, 6, 43, 43, 70, 3156, 80, 408, 44, 6, 32],
        'all',
        [9999],
        [9997, 9999, 9998],
        [3, 9999],
        [745, 32, 6, 43, 70, 3156, 9999, 80, 408, 44],
        [44, 745, 32, 6, 43, 43, 70, 9999, 3156, 80, 408, 44, 6, 32],
    ]
)
@pytest.mark.parametrize('tags_type', ['list', 'tuple', 'set', 'generator'])
def test_remove_tag_from_entries(dct_small, tag, entry_ids, tags_type):
    dct = dct_small

    if entry_ids == 'all':
        entry_ids = list(dct.iter_entry_ids())
    entry_ids_ = to_type(entry_ids, tags_type)

    if (tag in dct.tags) and set(entry_ids).issubset(set(dct.iter_entry_ids())):
        tag_ids = dct.search(tags=[tag])

        dct.remove_tag_from_entries(tag, entry_ids_)

        assert dct.search(tags=[tag]) == tag_ids.difference(entry_ids)
    else:
        state_before = deepcopy(dct.to_json_dict())

        # Operation should raise on invalid arguments
        with pytest.raises(KeyError):
            dct.remove_tag_from_entries(tag, entry_ids_)

        state_after = dct.to_json_dict()

        # State must remain unchanged after failed operation
        assert state_after == state_before


@pytest.mark.parametrize('tag', ['', 'new tag', 'verb', 'new'])
@pytest.mark.parametrize('is_default', [True, False])
def test_add_tag(dct_small, tag, is_default):
    dct = dct_small

    tag_ids = dct.search(tags=[tag])

    dct.add_tag(tag, is_default)

    assert tag in dct.tags
    assert dct.search(tags=[tag]) == tag_ids
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

    target_tag_ids = dct.search(tags=[target_tag])
    new_tag_ids = dct.search(tags=[new_tag])

    dct.rename_tag(target_tag, new_tag)

    assert new_tag in dct.tags
    assert dct.search(tags=[new_tag]) == target_tag_ids.union(new_tag_ids)
    for eid in new_tag_ids:
        assert new_tag in dct[eid].tags

    if new_tag != target_tag:
        assert target_tag not in dct.tags
        assert target_tag not in dct.default_tags
        assert dct.search(tags=[target_tag]) == set()
        for eid in new_tag_ids:
            assert target_tag not in dct[eid].tags


@pytest.mark.parametrize('target_tag', ['', 'invalid'])
@pytest.mark.parametrize('new_tag', ['', 'adj', 'verb', 'new', 'invalid'])
def test_rename_tag_bad(dct_small, target_tag, new_tag):
    dct = dct_small

    state_before = deepcopy(dct.to_json_dict())

    # Operation should raise on invalid rename
    with pytest.raises(InvalidTagError):
        dct.rename_tag(target_tag, new_tag)

    state_after = dct.to_json_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_delete_tag(dct_small, tag):
    dct = dct_small

    tag_ids = dct.search(tags=[tag])

    dct.delete_tag(tag)

    assert tag not in dct.tags
    assert tag not in dct.default_tags
    assert dct.search(tags=[tag]) == set()
    for eid in tag_ids:
        assert tag not in dct[eid].tags


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_delete_tag_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_json_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.delete_tag(tag)

    state_after = dct.to_json_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_mark_tag_as_default(dct_small, tag):
    dct = dct_small

    default_tags = deepcopy(dct.default_tags)

    dct.mark_tag_as_default(tag)

    assert dct.is_default_tag(tag)
    assert set(dct.default_tags) == set(default_tags).union({tag})


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_mark_tag_as_default_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_json_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.mark_tag_as_default(tag)

    state_after = dct.to_json_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before


@pytest.mark.parametrize('tag', ['adjective', 'verb', 'haben-verb', 'plural -en', 'new'])
def test_unmark_tag_as_default(dct_small, tag):
    dct = dct_small

    default_tags = deepcopy(dct.default_tags)

    dct.unmark_tag_as_default(tag)

    assert not dct.is_default_tag(tag)
    assert set(dct.default_tags) == set(default_tags).difference({tag})


@pytest.mark.parametrize('tag', ['', 'invalid'])
def test_unmark_tag_as_default_bad(dct_small, tag):
    dct = dct_small

    state_before = deepcopy(dct.to_json_dict())

    # Operation should raise on invalid tag
    with pytest.raises(InvalidTagError):
        dct.unmark_tag_as_default(tag)

    state_after = dct.to_json_dict()

    # State must remain unchanged after failed operation
    assert state_after == state_before
