#!/usr/bin/env python

import cProfile
import pstats
import StringIO
from multiprocessing import Value, Lock
from spring.wgen import AsyncKVWorker, N1QLWorker, WorkloadGen


workload_settings = type(
                         'WorkloadSettings',
                         (object, ),
                         {
                         'creates': 0,
                         'reads': 0,
                         'updates': 100,
                         'deletes': 0,
                         'cases': 0,

                         'ops': 8000,
                         'throughput': float('inf'),

                         'size': 2048,
                         'items': 10000,
                         'expiration': 0,
                         'working_set': 100,
                         'working_set_access': 100,

                         'workers': 0,
                         'query_workers': 0,
                         'dcp_workers': 0,

                         'n1ql': None,
                         'n1ql_workers': 8,
                         'n1ql_throughput': 800,
                         'n1ql_queries': ['SELECT * FROM `{bucket}` USE KEYS(\"{key}\")']
                         }
                         )()

target_settings = type(
                       'TargetSettings',
                       (object, ),
                       {
                       'node': '172.23.121.113:8091',
                       'bucket': 'bucket-1',
                       'password': 'password',
                       'prefix': None,
                       }
                       )


def run():
    curr_items = Value('i', workload_settings.items)
    deleted_items = Value('i', 0)
    lock = Lock()

    workload = WorkloadGen(workload_settings, target_settings)
    workload.start_n1ql_workers(curr_items, deleted_items)
    workload.run()

def profile():
    pr = cProfile.Profile()
    s = StringIO.StringIO()

    pr.enable()
    run()
    pr.disable()

    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.reverse_order()
    ps.print_stats()
    ps.dump_stats('profile.prof')


if __name__ == '__main__':
    profile()