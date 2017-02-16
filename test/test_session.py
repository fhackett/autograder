import autograder

from unittest import mock
import pytest

@pytest.fixture
def reporter():
    return mock.create_autospec(autograder.Reporter)

@pytest.fixture
def backend():
    b = mock.create_autospec(autograder.Backend)
    b.get_ids.return_value = {mock.sentinel.id1, mock.sentinel.id2}
    return b

@pytest.fixture
def action1():
    a = mock.create_autospec(autograder.Action, name='action1')
    def side_effect(data, work_dir):
        data['action1'] = {'success': True}
        return True
    a.perform.side_effect = side_effect
    return a

@pytest.fixture
def action2():
    a = mock.create_autospec(autograder.Action, name='action2')
    def side_effect(data, work_dir):
        data['action2'] = {'success': False}
        return False
    a.perform.side_effect = side_effect
    return a

def test__session___init__(backend, reporter):
    session = autograder.Session([backend], [reporter], [], {'a': mock.sentinel.a, 'b': mock.sentinel.b})
    assert backend.setup.call_args_list == [
        mock.call(a=mock.sentinel.a, b=mock.sentinel.b),
    ]
    assert reporter.setup.call_args_list == [
        mock.call(a=mock.sentinel.a, b=mock.sentinel.b),
    ]

def test__session_get_ids(backend):
    session = autograder.Session([backend], [], [])
    assert session.get_ids() == {mock.sentinel.id1, mock.sentinel.id2}

@mock.patch('tempfile.TemporaryDirectory', autospec=True)
@mock.patch('collections.OrderedDict', autospec=True)
def test__session_run_invididual(OrderedDict, TemporaryDirectory, reporter, backend, action1, action2):
    data = OrderedDict.return_value
    work_dir = TemporaryDirectory().__enter__.return_value
    data.items.return_value = [(mock.sentinel.name, mock.sentinel.data)]
    session = autograder.Session([backend], [reporter], [action1, action2])
    global_data = {}

    assert session.run_individual(mock.sentinel.id, global_data) == data

    assert backend.prepare.call_args_list == [
        mock.call(mock.sentinel.id, data, work_dir)
    ]
    assert reporter.on_part_completion.call_args_list == [mock.call(mock.sentinel.name, mock.sentinel.data)]*2
    assert reporter.on_individual_completion.call_args_list == [
        mock.call(mock.sentinel.id, False, data, global_data),
    ]
    assert action1.perform.call_args_list == [mock.call(data, work_dir)]
    assert action2.perform.call_args_list == [mock.call(data, work_dir)]

@mock.patch('tempfile.TemporaryDirectory', autospec=True)
@mock.patch('autograder.Session.run_individual', autospec=True)
def test__session_run(run_individual, TemporaryDirectory, backend, reporter):
    work_dir = TemporaryDirectory().__enter__.return_value
    session = autograder.Session([backend], [reporter], [])

    assert session.run() == {
        mock.sentinel.id1: run_individual.return_value,
        mock.sentinel.id2: run_individual.return_value,
    }

    assert backend.prepare_global.call_args_list == [
        mock.call(mock.ANY, work_dir),
    ]
    assert reporter.on_completion.called
