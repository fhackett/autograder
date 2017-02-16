import pytest
import tempfile
import os.path
import csv

from autograder.reporters.csv import CSVReporter

def fn(id, success, data, global_data):
    return (id, success, data, global_data)

def test__basic():
    with tempfile.TemporaryDirectory() as d:
        r = CSVReporter(name='foo', row_fn=fn, headings=('a', 'b', 'c'), delimiter=',')
        path = os.path.join(d, 'output.csv')
        with open(path, 'w') as f:
            r.setup(foo_csv_output=f)
            r.on_individual_completion(1, 2, 3, 4)
            r.on_individual_completion(5, 6, 7, 8)
        with open(path) as f:
            assert f.read() == """\
a,b,c
1,2,3,4
5,6,7,8
"""
