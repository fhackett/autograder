import autograder.reporters.stats as stats
import pytest
from unittest import mock

def test__report_stats():
    op1 = mock.create_autospec(stats.StatsReporter.Operation, name='op1')
    op1.name = 'op1'
    op2 = mock.create_autospec(stats.StatsReporter.Operation, name='op2')
    op2.name = 'op2'
    r = stats.StatsReporter([op1, op2])

    r.on_individual_completion(mock.sentinel.id1, True, mock.sentinel.data1, mock.sentinel.global_data)
    r.on_individual_completion(mock.sentinel.id2, False, mock.sentinel.data2, mock.sentinel.global_data)
    r.on_individual_completion(mock.sentinel.id3, True, mock.sentinel.data3, mock.sentinel.global_data)

    r.on_completion(mock.sentinel.data)

    assert op1.read.call_args_list == [
        mock.call(mock.sentinel.data1, mock.sentinel.global_data),
        mock.call(mock.sentinel.data3, mock.sentinel.global_data),
    ]
    assert op2.read.call_args_list == [
        mock.call(mock.sentinel.data1, mock.sentinel.global_data),
        mock.call(mock.sentinel.data3, mock.sentinel.global_data),
    ]
    assert op1.accumulate.call_args_list == [
        mock.call([op1.read.return_value, op1.read.return_value]),
    ]
    assert op2.accumulate.call_args_list == [
        mock.call([op2.read.return_value, op2.read.return_value]),
    ]
