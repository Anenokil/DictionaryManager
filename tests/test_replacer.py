"""
Tests for the Replacer class.

Author: Anenokil
"""

from copy import deepcopy
import os
import json
import pytest

from backend import Replacer

data_path = os.path.join('tests', 'test_data')
dct_replacer_path_100 = os.path.join(data_path, 'replacer_100_german.json')
dct_replacer_path_200 = os.path.join(data_path, 'replacer_200_greek.json')
dct_replacer_path_900 = os.path.join(data_path, 'replacer_900_strange.json')


@pytest.fixture
def replacer_empty(request):
    return Replacer()


@pytest.fixture
def replacer_german(request):
    with open(dct_replacer_path_100, 'r') as f:
        data = json.load(f)
    return Replacer.from_json_dict(data)


@pytest.fixture
def replacer_greek(request):
    with open(dct_replacer_path_200, 'r') as f:
        data = json.load(f)
    return Replacer.from_json_dict(data)


@pytest.fixture
def replacer_strange(request):
    with open(dct_replacer_path_900, 'r') as f:
        data = json.load(f)
    return Replacer.from_json_dict(data)


@pytest.fixture
def replacer(request):
    return request.getfixturevalue(f'replacer_{request.param}')


@pytest.mark.parametrize('modifier', [')', ' ', '::', ':*'])
def test_set_replacement_invalid_modifier(modifier):
    replacer = Replacer()

    input_char = 'a'
    output_char = 'ä'

    state_before = deepcopy(replacer.to_dict())

    with pytest.raises(KeyError):
        replacer.set_replacement(modifier, input_char, output_char)

    assert replacer.to_dict() == state_before


@pytest.mark.parametrize('input_char', ['', ':', '*'])
def test_set_replacement_input_char_is_modifier(input_char):
    replacer = Replacer()

    modifier = ':'
    output_char = 'ä'

    state_before = deepcopy(replacer.to_dict())

    with pytest.raises(ValueError):
        replacer.set_replacement(modifier, input_char, output_char)

    assert replacer.to_dict() == state_before


@pytest.mark.parametrize('input_char', ['::', '**', 'aa'])
def test_set_replacement_invalid_input_char(input_char):
    replacer = Replacer()

    modifier = ':'
    output_char = 'ä'

    state_before = deepcopy(replacer.to_dict())

    with pytest.raises(ValueError):
        replacer.set_replacement(modifier, input_char, output_char)

    assert replacer.to_dict() == state_before


@pytest.mark.parametrize('output_char', ['::', '**', 'ää'])
def test_set_replacement_invalid_output_char(output_char):
    replacer = Replacer()

    modifier = ':'
    input_char = 'a'

    state_before = deepcopy(replacer.to_dict())

    with pytest.raises(ValueError):
        replacer.set_replacement(modifier, input_char, output_char)

    assert replacer.to_dict() == state_before


@pytest.mark.parametrize('replacer, text, replaced', [
    ('empty', 'hello world', 'hello world'),
    ('strange', 'hello world', 'hello world'),
    ('strange', '', ''),
    ('strange', 'potato', 'potAto'),
    ('strange', 'POTATO', 'POTaTO'),
    ('strange', 'p#ot#ato', 'p#otbto'),
    ('strange', 'p:ot:ato', 'p:otäto'),
    ('strange', 'pot::ato', 'pot:Ato'),
    ('strange', 'pot:::ato', 'pot:äto'),
    ('strange', 'pot*ato', 'pot*Ato'),
    ('german', 'M:anner', 'Männer'),
    ('greek', 'logos', 'λογοσ'),
], indirect=['replacer'])
def test_replace(replacer, text, replaced):
    assert replacer.replace(text) == replaced


@pytest.mark.parametrize('replacer, text', [
    ('empty', 'hello world'),
    ('strange', 'hello world'),
    ('strange', ''),
    ('strange', 'potato'),
    ('strange', 'POTATO'),
    ('strange', 'p#otbto'),
    ('strange', 'p:otäto'),
    ('strange', 'pot:Ato'),
    ('strange', 'pot:äto'),
    ('strange', 'pot*Ato'),
    ('german', 'Männer: '),
    ('greek', 'λογοσ'),
    ('greek', ''),
], indirect=['replacer'])
def test_escape(replacer, text):
    assert text == replacer.replace(replacer.escape(text))
