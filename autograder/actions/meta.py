import autograder as _autograder
import shutil as _shutil
import os.path as _path

class CopyToSourceDir(_autograder.Action):
    def __init__(self, filename):
        self.filename = filename
    def perform(self, data, work_dir):
        _shutil.copy2(
            src=_path.join(work_dir, self.filename),
            dst=_path.join(data['meta']['source_dir'], self.filename))
        return True
