import autograder as _autograder
import argparse as _argparse
import csv as _csv

class CSVBackend(_autograder.Backend):
    def __init__(self, name, key=None, **kwargs):
        self.name = name
        self.key = key
        self.requirements = {
            '{}_csv_input'.format(name): {
                'type': _argparse.FileType('r')
            }
        }
        self.reader_kwargs = kwargs

    def setup(self, **kwargs):
        f = kwargs['{}_csv_input'.format(self.name)]
        self.reader = _csv.reader(f, **self.reader_kwargs)
        headers = next(self.reader)
        if self.key is not None:
            rows = {}
            k_index = headers.index(self.key)
        else:
            rows = []
            k_index = None
        for row in self.reader:
            r = {}
            for name, item in zip(headers, row):
                r[name] = item
            if k_index is not None:
                rows[row[k_index]] = r
            else:
                rows.append(r)
        self.rows = rows

    def prepare_global(self, data, global_dir):
        data[self.name] = self.rows
