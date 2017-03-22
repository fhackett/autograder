from autograder.backends import CustomBackend
from unittest import mock
import pytest

def test__custom_backend():
    m = mock.MagicMock(name='foo')
    c = CustomBackend(fn=m)

    c.prepare_global(mock.sentinel.global_data, mock.sentinel.global_dir)
    c.prepare(mock.sentinel.id, mock.sentinel.data, mock.sentinel.work_dir)

    assert m.call_args_list == [
        mock.call(mock.sentinel.data, mock.sentinel.global_data, mock.sentinel.work_dir),
    ]
