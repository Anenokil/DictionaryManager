"""
Tests for the Manager class.

Author: Anenokil
"""

from copy import deepcopy
import os
import json
import pytest

from backend import Manager, DctBundle

data_path = os.path.join('tests', 'test_data')
dct_bundle_path_101 = os.path.join(data_path, 'dct_bundle_101_empty_with_tags.json')
dct_bundle_path_201 = os.path.join(data_path, 'dct_bundle_201_ger_eng_29.json')
dct_bundle_path_202 = os.path.join(data_path, 'dct_bundle_202_ger_eng_128.json')
dct_bundle_path_203 = os.path.join(data_path, 'dct_bundle_203_ger_eng_246.json')


@pytest.fixture
def manager_empty(request):
    return Manager()


@pytest.fixture
def manager_1_dct(request):
    manager = Manager()
    manager.open_dct(dct_bundle_path_201, to_activate=True)
    return manager


@pytest.fixture
def manager_3_dct(request):
    manager = Manager()
    manager.open_dct(dct_bundle_path_101, to_activate=True)
    manager.open_dct(dct_bundle_path_201, to_activate=True)
    manager.open_dct(dct_bundle_path_202, to_activate=True)
    return manager


@pytest.fixture
def manager_3_dct_no_paths(request):
    manager = Manager()
    manager.open_dct(dct_bundle_path_101, to_activate=True)
    manager.open_dct(dct_bundle_path_201, to_activate=True)
    manager.open_dct(dct_bundle_path_202, to_activate=True)
    for i in range(3):
        manager.opened_dct_bundles[i].filepath = None
    return manager


@pytest.fixture
def manager(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('to_activate', [True, False])
def test_add_dct(manager, to_activate):
    size_before = manager.n_opened
    active_id_before = manager.active_dct_id

    db = DctBundle()
    manager.add_dct(db, to_activate)

    assert manager.n_opened == size_before + 1
    if manager.n_opened == 1 or to_activate:
        assert manager.active_dct_id == manager.n_opened - 1
    else:
        assert manager.active_dct_id == active_id_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('name', [None, 'new_name', 'test-dct_deu-eng_29'])
@pytest.mark.parametrize('to_activate', [True, False])
def test_create_dct(manager, name, to_activate):
    size_before = manager.n_opened
    active_id_before = manager.active_dct_id

    manager.create_dct(name, to_activate)

    assert manager.n_opened == size_before + 1
    assert manager.opened_dct_bundles[-1].dct.name == name
    if manager.n_opened == 1 or to_activate:
        assert manager.active_dct_id == manager.n_opened - 1
    else:
        assert manager.active_dct_id == active_id_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('filepath', [dct_bundle_path_101, dct_bundle_path_201])
@pytest.mark.parametrize('to_activate', [True, False])
def test_open_dct(manager, filepath, to_activate):
    size_before = manager.n_opened
    active_id_before = manager.active_dct_id

    manager.open_dct(filepath, to_activate)

    assert manager.n_opened == size_before + 1
    if manager.n_opened == 1 or to_activate:
        assert manager.active_dct_id == manager.n_opened - 1
    else:
        assert manager.active_dct_id == active_id_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('to_activate', [True, False])
def test_open_dct_bad(manager, to_activate):
    state_before = deepcopy(manager.to_dict())

    # Operation should raise on invalid filename
    with pytest.raises(FileNotFoundError):
        manager.open_dct(os.path.join(data_path, 'non-existent file'), to_activate)

    # State must remain unchanged after failed operation
    assert manager.to_dict() == state_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('dct_id', [-1, 0, 1, 2, 3])
def test_switch_dct(manager, dct_id):
    if 0 <= dct_id < manager.n_opened:
        manager.switch_dct(dct_id)

        assert manager.active_dct_id == dct_id
    else:
        state_before = deepcopy(manager.to_dict())

        # Operation should raise on invalid dct_id
        with pytest.raises(KeyError):
            manager.switch_dct(dct_id)

        # State must remain unchanged after failed operation
        assert manager.to_dict() == state_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('dct_id', [-1, 0, 1, 2, 3])
def test_close_dct(manager, dct_id):
    if 0 <= dct_id < manager.n_opened:
        active_id = manager.active_dct_id

        manager.close_dct(dct_id)

        if manager.n_opened == 0:
            assert manager.active_dct_id is None
        else:
            assert manager.active_dct_id == min(active_id, manager.n_opened - 1)
    else:
        state_before = deepcopy(manager.to_dict())

        # Operation should raise on invalid dct_id
        with pytest.raises(KeyError):
            manager.close_dct(dct_id)

        # State must remain unchanged after failed operation
        assert manager.to_dict() == state_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('dct_id', [-1, 0, 1, 2, 3])
@pytest.mark.parametrize('path', ['data.json', 'a/b/c/data.json'])
def test_save_dct(manager, dct_id, tmp_path, path):
    filepath = tmp_path / path

    if 0 <= dct_id < manager.n_opened:
        manager.save_dct(dct_id, filepath)

        assert filepath.exists()

        with open(filepath, 'r') as f:
            data = json.load(f)
        assert data == manager.active.to_dict()
    else:
        state_before = deepcopy(manager.to_dict())

        # Operation should raise on invalid dct_id
        with pytest.raises(KeyError):
            manager.save_dct(dct_id, filepath)

        # State must remain unchanged after failed operation
        assert manager.to_dict() == state_before


@pytest.mark.parametrize('manager', ['manager_3_dct_no_paths'], indirect=True)
@pytest.mark.parametrize('dct_id', [0, 1, 2])
def test_save_dct_bad_path(manager, dct_id):
    state_before = deepcopy(manager.to_dict())

    # State must remain unchanged after failed operation
    assert manager.to_dict() == state_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('dct_id', [-1, 0, 1, 2, 3])
def test_rename_dct(manager, dct_id):
    new_name = 'new name'

    if 0 <= dct_id < manager.n_opened:
        manager.rename_dct(dct_id, new_name)

        assert manager.opened_dct_bundles[dct_id].dct.name == new_name
    else:
        state_before = deepcopy(manager.to_dict())

        # Operation should raise on invalid dct_id
        with pytest.raises(KeyError):
            manager.rename_dct(dct_id, new_name)

        # State must remain unchanged after failed operation
        assert manager.to_dict() == state_before


@pytest.mark.parametrize(
    'manager', ['manager_empty', 'manager_1_dct', 'manager_3_dct', 'manager_3_dct_no_paths'],
    indirect=True
)
@pytest.mark.parametrize('from_index', [-1, 0, 1, 2, 3])
@pytest.mark.parametrize('to_index', [-1, 0, 1, 2, 3])
def test_move_dct(manager, from_index, to_index):
    if (0 <= from_index < manager.n_opened) and (0 <= to_index < manager.n_opened):
        bundles_before = list(manager.opened_dct_bundles)

        manager.move_dct(from_index, to_index)

        bundles_after = list(manager.opened_dct_bundles)

        assert bundles_before[from_index] == bundles_after[to_index]

        del bundles_before[from_index]
        del bundles_after[to_index]
        assert bundles_before == bundles_after
    else:
        state_before = deepcopy(manager.to_dict())

        # Operation should raise on invalid index
        with pytest.raises(KeyError):
            manager.move_dct(from_index, to_index)

        # State must remain unchanged after failed operation
        assert manager.to_dict() == state_before
