#!/usr/bin/env python3

import argparse
import csv
import random
import re
import sys

COL_BENCHMARK = "benchmark"
COL_STATUS = "status"
COL_ASSERTS = "number of asserts"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--asserts', dest='asrt_count',
                    help='CSV mapping benchmarks to number of assertions',
                    required=True)
    ap.add_argument('-s', '--statuses', dest='statuses',
                    help='CSV mapping benchmarks to statuses',
                    required=True)
    return ap.parse_args()

def main():
    args = parse_args()

    data = {}

    with open(args.asrt_count, 'r') as asrts_file:
        reader = csv.reader(asrts_file)
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            benchmark = drow[COL_BENCHMARK]
            n_asrts = drow[COL_ASSERTS]

            assert(benchmark not in data)
            data[benchmark] = [int(n_asrts), None]

    with open(args.statuses, 'r') as statuses_file:
        reader = csv.reader(statuses_file)
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            benchmark = drow[COL_BENCHMARK]
            status = drow[COL_STATUS]

            assert(benchmark in data)
            data[benchmark][1] = status

    print("%s,%s,%s" % (COL_BENCHMARK,COL_ASSERTS,COL_STATUS))
    for k in data:
        assert(data[k][1] != None)
        print("%s,%s,%s" % (k, data[k][0], data[k][1]))

if __name__ == '__main__':
    main()
