import tempfile as _tempfile
import abc as _abc
import concurrent.futures as _futures
import collections as _collections
import argparse as _argparse
import multiprocessing as _multiprocessing
import json as _json
import sys as _sys
import traceback as _traceback


class Backend(metaclass=_abc.ABCMeta):
    def get_ids(self):
        return set()
    def prepare(self, id, data, work_dir):
        pass
    def prepare_global(self, data, global_dir):
        pass
    def setup(self, **data):
        pass

class Action(metaclass=_abc.ABCMeta):
    @_abc.abstractmethod
    def perform(self, data, work_dir):
        pass

class Reporter(metaclass=_abc.ABCMeta):
    def setup(self, **data):
        pass
    def on_part_completion(self, name, data):
        pass
    def on_individual_completion(self, id, success, data, global_data):
        pass
    def on_completion(self, data):
        pass

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
            def underline(self, s):
                return s
import sys as _sys

class _TerminalReporter(Reporter):
    requirements = {}

    def __init__(self):
        if _blessings is None:
            self.terminal
        self.terminal = _blessings.Terminal()
        self.failed_ids = []
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
        traceback = data.get(
            'traceback',
            '\n'.join('    {operation} failed. {output}'.format(**d) for d in data.values() if isinstance(d, dict) and 'success' in d and not d['success']))
        if success:
            c = lambda s: t.green(t.underline(s))
        else:
            self.failed_ids.append((id, traceback))
            c = lambda s: t.red(t.underline(s))
        _sys.stdout.write(c('Finished {}: {}\n'.format(
            id,
            'success' if success else 'failure')))
        if not success:
            _sys.stdout.write(traceback+'\n')
    def on_completion(self, data):
        _sys.stdout.write(self.terminal.red('Failed IDs:\n'))
        for id, trace in self.failed_ids:
            _sys.stdout.write('- '+id+'\n'+trace+'\n')


class ActionSequence(Action):
    def __init__(self, actions, reporters=[]):
        self.actions = actions
        self.reporters = reporters
    def perform(self, data, workdir):
        for action in self.actions:
            success = action.perform(data, workdir)
            for reporter in self.reporters:
                reporter.on_part_completion(*list(data.items())[-1])
            if not success:
                return False
        return True

class Session:
    def __init__(self, backends, reporters, actions, backend_setup={}):
        self.backends = backends
        self.actions = actions
        self.reporters = reporters
        for backend in self.backends:
            backend.setup(**backend_setup)
        for reporter in self.reporters:
            reporter.setup(**backend_setup)
        self.reporting_failed = set()

    def get_ids(self):
        ids = set()
        for backend in self.backends:
            ids |= backend.get_ids()
        return ids

    def _run_reporters_individual_completion(self, id, success, data, global_data):
        try:
            for reporter in self.reporters:
                reporter.on_individual_completion(id, data['success'], data, global_data)
        except Exception as ex:
            self.reporting_failed.add((id, _traceback.format_exc()))

    def run_individual(self, id, global_data):
        data = _collections.OrderedDict()
        with _tempfile.TemporaryDirectory() as work_dir:
            try:
                for backend in self.backends:
                    backend.prepare(id, data, work_dir)
                seq = ActionSequence(self.actions, self.reporters)
                success = seq.perform(data, work_dir)
                data['success'] = success
            except Exception as ex:
                data['success'] = False
                data['traceback'] = _traceback.format_exc()
            self._run_reporters_individual_completion(id, data['success'], data, global_data)
        return data

    def run(self):
        with _tempfile.TemporaryDirectory() as global_dir:
            data = {}
            for backend in self.backends:
                backend.prepare_global(data, global_dir)
            with _futures.ThreadPoolExecutor(max_workers=_multiprocessing.cpu_count()*4) as executor:
                submissions = {}
                procs = {executor.submit(self.run_individual, id, data): id for id in self.get_ids()}
                for proc in _futures.as_completed(procs):
                    id = procs[proc]
                    try:
                        res = proc.result()
                    except Exception as exc:
                        raise exc
                    else:
                        submissions[id] = res
                data['submissions'] = submissions
            for reporter in self.reporters:
                reporter.on_completion(data)
        return data

    def run_from_results(self, results):
        for id, data in results['submissions'].items():
            for name, d in data.items():
                if isinstance(d, dict) and 'success' in d:
                    for reporter in self.reporters:
                        reporter.on_part_completion(name, d)
            self._run_reporters_individual_completion(id, data['success'], data, results)
        for reporter in self.reporters:
            reporter.on_completion(results)

def setup_args(parser, backends):
    reqs = {}
    for backend in backends:
        reqs.update(backend.requirements)
    for name, h in reqs.items():
        parser.add_argument('--'+name, **h)

def main():
    first_parser = _argparse.ArgumentParser()
    first_parser.add_argument('gradefile', type=_argparse.FileType('r'), help='python file defining backends, reporters and actions to take')
    first_parser.add_argument('--run-from', nargs='?', type=_argparse.FileType('r'), default=None, help='report the contents of this result file')
    first_parser.add_argument('--output', nargs='?', type=_argparse.FileType('w'), help='filename to output json', default=_sys.stdout)
    first_parser.add_argument('--only-terminal', action='store_true', help='disables all reporters, displaying output on the terminal only')
    args, rest = first_parser.parse_known_args()
    compiled_definitions = compile(args.gradefile.read(), 'input', 'exec')
    definitions = {}
    exec(compiled_definitions, definitions)
    output_file = args.output
    input_file = args.run_from
    only_terminal = args.only_terminal
    parser = _argparse.ArgumentParser()
    if input_file is None:
        setup_args(parser, definitions['backends'])
    if not only_terminal:
        setup_args(parser, definitions['reporters'])
    args = parser.parse_args(rest)

    session = Session(
        definitions['backends'] if input_file is None else [],
        definitions['reporters'] if not only_terminal else [_TerminalReporter()],
        definitions['actions'],
        backend_setup=args.__dict__)

    if input_file is not None:
        results = _json.load(input_file)
        session.run_from_results(results)
    else:
        results = session.run()
        _json.dump(results, output_file, indent=2, default=repr)

    # if reporting failed, note the swallowed exception:
    if len(session.reporting_failed) != 0:
        print('Reporting failed:')
        for rfail, ex in sorted(session.reporting_failed):
            print('- {}: {}'.format(rfail, ex))

if __name__ == '__main__':
    main()
