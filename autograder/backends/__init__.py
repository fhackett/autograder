from .handin import HandinBackend
from .csv import CSVBackend

from autograder import Backend

class CustomBackend(Backend):
    requirements = {}
    
    def __init__(self, fn):
        self.fn = fn
    def prepare_global(self, data, global_dir):
        self.global_data = data
    def prepare(self, id, data, work_dir):
        self.fn(data, self.global_data, work_dir)
