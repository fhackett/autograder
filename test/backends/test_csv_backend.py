from autograder.backends import CSVBackend
import tempfile
import pytest

def test__basic_with_key():
    b = CSVBackend(name='foo', key='y', delimiter=',')

    b.setup(foo_csv_input=[
        'x,y,z',
        '1,2,3',
        '4,5,6',
        '7,8,9',
    ])
    data = {}
    with tempfile.TemporaryDirectory() as d:
        b.prepare_global(data, d)
    assert data == {'foo': {
        '2': {'x': '1', 'y': '2', 'z': '3'},
        '5': {'x': '4', 'y': '5', 'z': '6'},
        '8': {'x': '7', 'y': '8', 'z': '9'},
    }}

def test__basic_no_key():
    b = CSVBackend(name='foo', delimiter=',')

    b.setup(foo_csv_input=[
        'x,y,z',
        '1,2,3',
        '4,5,6',
        '7,8,9',
    ])
    data = {}
    with tempfile.TemporaryDirectory() as d:
        b.prepare_global(data, d)
    assert data == {'foo': [
        {'x': '1', 'y': '2', 'z': '3'},
        {'x': '4', 'y': '5', 'z': '6'},
        {'x': '7', 'y': '8', 'z': '9'},
    ]}
