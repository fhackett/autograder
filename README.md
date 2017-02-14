autograder
==========

This package is written to help automate grading for CPSC221 at UBC.

To use it, write a file like this `grade.py`:
```python
from autograder.backends.handin import HandinBackend
from autograder.reporters.terminal import TerminalReporter
from autograder.actions import CalculateGrade

def fn(data):
    return 3

backends = [HandinBackend('bar')]
reporters = [TerminalReporter()]
actions = [
    CalculateGrade(fn)
]
```

You can then run `autograder grade`, passing other options as the backends and reporters ask for them.

More documentation and testing coming eventually.
