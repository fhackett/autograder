from  autograder.backends.handin import HandinBackend

import pytest
import os
import os.path
import datetime
import tempfile


@pytest.fixture
def backend(datadir):
    b = HandinBackend(submission_name='bar')
    b.setup(handin_directory=datadir['handin_dir'])
    return b

@pytest.fixture
def my_tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield d

def test__get_ids(backend):
    assert set(backend.get_ids()) == {'1','2','3'}

@pytest.mark.parametrize('id,expected_meta', [
    ('1', {
        'is_late': False,
        'submission_timestamp': None,
        'partner_id': None,
    }),
    ('2', {
        'is_late': True,
        'submission_timestamp': None,
        'partner_id': '4',
    }),
    ('3', {
        'is_late': False,
        'submission_timestamp': None,
        'partner_id': '5',
    })])
def test__prepare(id, expected_meta, backend, my_tmpdir):
    data = {}
    backend.prepare(id, data, my_tmpdir)
    source_dir = os.path.join(backend.handin_directory,backend.submission_name,id)
    assert data['files'] == {'source_dir': source_dir}
    if expected_meta['is_late']:
        stamp_name = 'DateSTAMP.LATE'
    else:
        stamp_name = 'DateSTAMP'

    expected_meta['submission_timestamp'] = datetime.datetime.fromtimestamp(
        os.stat(os.path.join(source_dir,stamp_name)).st_ctime)
    assert data['meta'] == expected_meta

    assert set(os.listdir(str(my_tmpdir))) == {stamp_name, id}
