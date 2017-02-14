import autograder as _autograder
import blessings as _blessings
import sys as _sys

class TerminalReporter(_autograder.Reporter):
    requirements = {}

    def __init__(self):
        self.terminal = _blessings.Terminal()
    def on_part_completion(self, name, data):
        t = self.terminal
        if data['success']:
            _sys.stdout.write(t.green('[SUCCESS] '))
        else:
            _sys.stdout.write(t.red('[FAILURE] '))
        _sys.stdout.write(name+': ')
        _sys.stdout.write(t.italic(data['operation']))
        _sys.stdout.write('\n')
        _sys.stdout.write(data['output'])
        _sys.stdout.write('\n')
    def on_individual_completion(self, id, success, data):
        t = self.terminal
        if success:
            c = lambda s: t.green(t.underline(s))
        else:
            c = lambda s: t.red(t.underline(s))
        _sys.stdout.write(c('Finished {}: {}\n'.format(
            id,
            'success' if success else 'failure')))
