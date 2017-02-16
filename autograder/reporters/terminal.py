import autograder as _autograder
try:
    import blessings as _blessings
except ImportError:
    # fake it well enough for our use cases
    class _blessings:
        class Terminal:
            def green(self, s):
                return s
            def red(self, s):
                return s
            def italic(self, s):
                return s
            def underlins(self, s):
                return s
import sys as _sys

class TerminalReporter(_autograder.Reporter):
    requirements = {}

    def __init__(self):
        if _blessings is None:
            self.terminal
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
    def on_individual_completion(self, id, success, data, global_data):
        t = self.terminal
        if success:
            c = lambda s: t.green(t.underline(s))
        else:
            c = lambda s: t.red(t.underline(s))
        _sys.stdout.write(c('Finished {}: {}\n'.format(
            id,
            'success' if success else 'failure')))
