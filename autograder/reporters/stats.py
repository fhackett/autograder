import abc as _abc
import autograder as _autograder

class StatsReporter(_autograder.Reporter):
    requirements = {}

    class Operation(metaclass=_abc.ABCMeta):
        def __init__(self, name):
            self.name = name
        @_abc.abstractmethod
        def read(self, data, global_data):
            pass
        @_abc.abstractmethod
        def accumulate(self, accumulator):
            pass

    def __init__(self, operations):
        self.operations = operations
        self.accumulators = {op.name: [] for op in operations}
        self.item_count = 0
    def on_individual_completion(self, id, success, data, global_data):
        if success:
            self.item_count += 1
            for op in self.operations:
                self.accumulators[op.name].append(op.read(data, global_data))
    def on_completion(self, data):
        print('Statistics (of {} successful items):'.format(self.item_count))
        for op in self.operations:
            print('{name}: {value}'.format(
                name=op.name,
                value=op.accumulate(self.accumulators[op.name])))
