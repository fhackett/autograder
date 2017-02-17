import csv as _csv
import argparse as _argparse
import autograder as _autograder
import inspect as _inspect

class CSVReporter(_autograder.Reporter):
    def __init__(self, name, row_fn, headings=None, **kwargs):
        self.name = name
        self.requirements = {
            name+'_csv_output': {
                'type': _argparse.FileType('w')
            },
        }
        self.headings = headings
        self.row_fn = row_fn
        self.writer_kwargs = kwargs
    def setup(self, **kwargs):
        f = kwargs[self.name+'_csv_output']
        self.file = f
        self.writer = _csv.writer(f, **self.writer_kwargs)
        if self.headings is not None:
            self.writer.writerow(self.headings)
    def on_individual_completion(self, id, success, data, global_data):
        row = self.row_fn(id, success, data, global_data)
        if row is not None:
            if _inspect.isgenerator(row):
                for r in row:
                    self.writer.writerow(r)
            else:
                self.writer.writerow(row)
    def on_completion(self, data):
        self.file.close()
