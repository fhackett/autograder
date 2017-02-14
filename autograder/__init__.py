import tempfile as _tempfile
import abc as _abc
import concurrent.futures as _futures
import collections as _collections
import argparse as _argparse
import json as _json
import sys as _sys


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
    def on_part_completion(self, name, data):
        pass
    def on_individual_completion(self, id, success, data):
        pass
    def on_completion(self, data):
        pass

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

    def get_ids(self):
        ids = set()
        for backend in self.backends:
            ids |= backend.get_ids()
        return ids

    def run_individual(self, id):
        data = _collections.OrderedDict()
        with _tempfile.TemporaryDirectory() as work_dir:
            for backend in self.backends:
                backend.prepare(id, data, work_dir)
            seq = ActionSequence(self.actions, self.reporters)
            success = seq.perform(data, work_dir)
            data['success'] = success
            for reporter in self.reporters:
                reporter.on_individual_completion(id, success, data)
        return data

    def run(self):
        with _tempfile.TemporaryDirectory() as global_dir:
            data = {}
            for backend in self.backends:
                backend.prepare_global(data, global_dir)
            with _futures.ThreadPoolExecutor() as executor:
                data = {}
                procs = {executor.submit(self.run_individual, id): id for id in self.get_ids()}
                for proc in _futures.as_completed(procs):
                    id = procs[proc]
                    try:
                        res = proc.result()
                    except Exception as exc:
                        raise exc
                    else:
                        data[id] = res
            for reporter in self.reporters:
                reporter.on_completion(data)
        return data

    def run_from_results(self, results):
        for id, data in results.items():
            for name, d in data.items():
                if isinstance(d, dict) and 'success' in d:
                    for reporter in self.reporters:
                        reporter.on_part_completion(name, d)
            for reporter in self.reporters:
                reporter.on_individual_completion(id, data['success'], data)
        for reporter in self.reporters:
            reporter.on_completion(results)

def setup_args(parser, backends):
    reqs = {}
    for backend in backends:
        reqs.update(backend.requirements)
    for name, h in reqs.items():
        parser.add_argument(name, help=h)

def main():
    first_parser = _argparse.ArgumentParser()
    first_parser.add_argument('gradefile', type=_argparse.FileType('r'), help='python file defining backends, reporters and actions to take')
    first_parser.add_argument('--run-from', nargs='?', type=_argparse.FileType('r'), default=None, help='report the contents of this result file')
    first_parser.add_argument('--output', nargs='?', type=_argparse.FileType('w'), help='filename to output json', default=_sys.stdout)
    args, rest = first_parser.parse_known_args()
    compiled_definitions = compile(args.gradefile.read(), 'input', 'exec')
    definitions = {}
    exec(compiled_definitions, definitions)
    output_file = args.output
    input_file = args.run_from
    parser = _argparse.ArgumentParser()
    if input_file is None:
        setup_args(parser, definitions['backends'])
        setup_args(parser, definitions['reporters'])
    args = parser.parse_args(rest)

    session = Session(
        definitions['backends'] if input_file is None else [],
        definitions['reporters'],
        definitions['actions'],
        backend_setup=args.__dict__)

    if input_file is not None:
        results = _json.load(input_file)
        session.run_from_results(results)
    else:
        results = session.run()
        _json.dump(results, output_file, indent=2, default=repr)

if __name__ == '__main__':
    main()
