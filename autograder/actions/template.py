import autograder as _autograder
import pystache as _pystache
import os.path as _path

def _remove_dots(d):
    if isinstance(d, dict):
        return {k.replace('.','_'):_remove_dots(v) for k,v in d.items()}
    else:
        return d

class WriteTemplate(_autograder.Action):
    def __init__(self, template, filename):
        self.template = _pystache.parse(template)
        self.filename = filename
    def perform(self, data, work_dir):
        result = _pystache.render(self.template, _remove_dots(data))
        with open(_path.join(work_dir, self.filename), 'w') as f:
            f.write(result)
        data['write_template_{}'.format(self.filename)] = {
            'success': True,
            'operation': 'render template to {}'.format(self.filename),
        }
        return True
