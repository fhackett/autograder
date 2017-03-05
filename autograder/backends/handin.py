import autograder as _autograder
import os as _os
import os.path as _path
import datetime as _datetime
import shutil as _shutil

class HandinBackend(_autograder.Backend):
    name = 'handin'
    requirements = {
        'handin-directory': {
            "help": "This is the directory where the course's handin files go. Look in csbox and go to the right year/term.",
        },
    }

    def __init__(self, submission_name):
        self.submission_name = submission_name

    def setup(self, handin_directory, **kwargs):
        self.handin_directory = handin_directory

    def prepare(self, id, data, work_dir):
        prefix = _path.join(self.handin_directory, self.submission_name, id)
        # is_late
        is_late = _path.exists(
            _path.join(prefix, 'DateSTAMP.LATE'))
        # submission_timestamp
        if is_late:
            timestamp_filename = 'DateSTAMP.LATE'
        elif _path.exists(_path.join(prefix, 'DateSTAMP')):
            timestamp_filename = 'DateSTAMP'
        submission_timestamp = _datetime.datetime.fromtimestamp(
            _os.stat(
                _path.join(prefix, timestamp_filename)).st_ctime)
        # partner id
        partner_filename = _path.join(self.handin_directory, self.submission_name+'.partner', id)
        if _path.isfile(partner_filename):
            with open(partner_filename) as f:
                partner_ids = set(p.strip() for p in f)
        else:
            partner_ids = set()

        # copy over files
        for f in _os.listdir(prefix):
            fname = _path.join(prefix, f)
            if _path.isdir(fname):
                _shutil.copytree(src=fname, dst=_path.join(work_dir, f))
            else:
                _shutil.copy2(src=fname, dst=_path.join(work_dir, f))


        data.setdefault('meta',{}).update({
            'submitter_id': id,
            'is_late': is_late,
            'submission_timestamp': submission_timestamp,
            'partner_id': next(iter(partner_ids), None),
            'source_dir': _path.join(self.handin_directory, self.submission_name, id),
        })

    def get_ids(self):
        p = _path.join(self.handin_directory, self.submission_name)
        dirs = _os.listdir(p)
        return {
            d for d in dirs
            if _path.isdir(_path.join(p, d))}
