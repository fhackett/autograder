import autograder as _autograder
import shutil as _shutil
import os as _os
import os.path as _path
import json as _json
import traceback as _traceback
import subprocess as _subprocess

from .meta import CopyToSourceDir
from .template import WriteTemplate

def find_command(*args, path=None):
    for arg in args:
        result = _shutil.which(arg, path=path)
        if result is not None:
            return result
    raise NameError(args)

class Subprocess(_autograder.Action):
    def __init__(self, name, command, timeout=None):
        self.name = name
        self.command = command
        self.timeout = timeout
    def perform(self, data, work_dir):
        result = {
            'operation': ' '.join(self.command),
            'output': '',
            'return_code': None,
            'success': False,
        }
        data[self.name] = result
        try:
            command = [find_command(self.command[0], path=work_dir)] + self.command[1:]
            output = _subprocess.check_output(
                command,
                stderr=_subprocess.STDOUT,
                universal_newlines=True,
                cwd=work_dir,
                timeout=self.timeout)
            result['return_code'] = 0
            result['output'] = output
            result['success'] = True
            return True
        except _subprocess.CalledProcessError as e:
            result['return_code'] = e.returncode
            result['output'] = e.output
        except FileNotFoundError:
            result['output'] = 'File not found: {}'.format(command[0])
        except _subprocess.TimeoutExpired:
            result['output'] = 'Timed out after: {}'.format(self.timeout)
        except Exception:
            result['output'] = _traceback.format_exc()
        return False

class Make(_autograder.Action):
    def __init__(self, target):
        self._proc = Subprocess(
            name='make_'+target,
            command=[find_command('make'), target])
    def perform(self, data, work_dir):
        return self._proc.perform(data, work_dir)

class CompileCXX(_autograder.Action):
    def __init__(self, filename):
        basename, _ = _path.splitext(filename)
        self._proc = Subprocess(
            name='compilecxx_'+basename,
            command=[find_command('g++', 'clang++')] + '-c -Wall -g --std=c++11'.split(' ') + [filename, '-o', basename+'.o'])
    def perform(self, data, work_dir):
        return self._proc.perform(data, work_dir)

class LinkCXX(_autograder.Action):
    def __init__(self, program, objects, libraries=[]):
        self._proc = Subprocess(
            name='linkcxx_'+program,
            command=[find_command('g++', 'clang++')] + '-Wall -g --std=c++11'.split(' ') + objects + ['-o', program])
    def perform(self, data, work_dir):
        return self._proc.perform(data, work_dir)

class Valgrind(_autograder.Action):
    def __init__(self, command, options=[]):
        self.options = options
        self.command = command
    def perform(self, data, work_dir):
        try:
            proc = Subprocess(
                name='valgrind_{}'.format(self.command[0]),
                command=[find_command('valgrind')] + self.options + [find_command(self.command[0], path=work_dir)] + self.command[1:])
            return proc.perform(data, work_dir)
        except NameError:
            data['valgrind_{}'.format(self.command[0])] = {
                'operation': 'valgrind {}'.format(self.command),
                'success': False,
                'output': _traceback.format_exc(),
            }
            return False

class ReadFile(_autograder.Action):
    def __init__(self, filename):
        self.filename = filename
    def perform(self, data, work_dir):
        path = _path.join(work_dir, self.filename)
        results = {
            'success': False,
            'operation': 'read {}'.format(path),
        }
        try:
            with open(_path.join(work_dir, self.filename)) as f:
                contents = f.read()
                data[self.filename] = contents
                results['success'] = True
                results['output'] = contents
                data['read_'+self.filename] = results
                return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['read_'+self.filename] = results
            return False

class WriteFile(_autograder.Action):
    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
    def perform(self, data, work_dir):
        path = _path.join(work_dir, self.filename)
        results = {
            'success': False,
            'operation': 'write {}'.format(path),
        }
        try:
            with open(_path.join(work_dir, self.filename), 'w') as f:
                f.write(self.contents)
                results['success'] = True
                results['output'] = self.contents
                data['write_'+self.filename] = results
                return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['read_'+self.filename] = results
            return False

class CopyFile(_autograder.Action):
    def __init__(self, filename):
        self.filename = filename
    def perform(self, data, work_dir):
        results = {
            'success': False,
            'operation': 'copy {}'.format(self.filename),
            'output': '',
        }
        try:
            _shutil.copy2(
                src=_path.join(_os.getcwd(), self.filename),
                dst=_path.join(work_dir, self.filename))
            results['success'] = True
            data['copy_'+self.filename] = results
            return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['copy_'+self.filename] = results
            return False

class ReadJSON(_autograder.Action):
    def __init__(self, filename):
        self.filename = filename
    def perform(self, data, work_dir):
        path = _path.join(work_dir, self.filename)
        results = {
            'success': False,
            'operation': 'read {}'.format(path),
        }
        try:
            with open(_path.join(work_dir, self.filename)) as f:
                js = _json.load(f)
                data[self.filename] = js
                results['success'] = True
                results['output'] = str(js)
                data['read_'+self.filename] = results
                return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['read_'+self.filename] = results
            return False

class WriteJSON(_autograder.Action):
    def __init__(self, filename):
        self.filename = filename
    def perform(self, data, work_dir):
        path = _path.join(work_dir, self.filename)
        results = {
            'success': False,
            'operation': 'write {}'.format(path),
        }
        try:
            with open(_path.join(work_dir, self.filename), 'w') as f:
                _json.dump(data[self.filename], f)
                results['success'] = True
                results['output'] = str(data[self.filename])
                data['write_'+self.filename] = results
                return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['write_'+self.filename] = results
            return False

class CalculateGrade(_autograder.Action):
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn
    def perform(self, data, work_dir):
        results = {
            'success': False,
            'operation': 'calculate grade {}'.format(self.name),
        }
        try:
            o = self.fn(data)
            data.setdefault('grades', {})[self.name] = o
            results['success'] = True
            results['output'] = str(o)
            data['calculate_grade_{}'.format(self.name)] = results
            return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data['calculate_grade_{}'.format(self.name)] = results
            return False

class Call(_autograder.Action):
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn
    def perform(self, data, work_dir):
        results = {
            'success': False,
            'operation': 'call {}'.format(self.name),
        }
        try:
            self.fn(data)
            results['success'] = True
            results['output'] = ''
            data[self.name] = results
            return True
        except Exception:
            results['output'] = _traceback.format_exc()
            data[self.name] = results
            return False

class Try(_autograder.Action):
    def __init__(self, actions):
        self.actions = actions
    def perform(self, data, work_dir):
        for action in self.actions:
            action.perform(data, work_dir)
        return True
