#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_args = None

TRACK_SINGLE_QUERY = 'track_single_query'
TRACK_INCREMENTAL = 'track_incremental'
TRACK_SINGLE_QUERY_CHALLENGE = 'track_single_query_challenge'
TRACK_INCREMENTAL_CHALLENGE = 'track_incremental_challenge'
TRACK_UNSAT_CORE = 'track_unsat_core'
TRACK_MODEL_VALIDATION = 'track_model_validation'

# job info column names
COL_BENCHMARK = 'benchmark'
COL_BENCHMARK_ID = 'benchmark id'
COL_SOLVER = 'solver'
COL_SOLVER_ID = 'solver id'

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

# Read csv with solver data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
# If 'use_wrapped' is true, use wrapped solver IDs instead.
def read_csv():
    global g_divisions, g_args
    solvers = dict()
    benchmarks = dict()
    with open(g_args.pairs_csv) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            solver_id = drow[COL_SOLVER_ID]
            if not solver_id in solvers:
                solvers[solver_id] = drow[COL_SOLVER]
                benchmarks[solver_id] = dict()
            benchmark_name = drow[COL_BENCHMARK]
            benchmark_path = benchmark_name.split("/")[1:]
            curdir = benchmarks[solver_id]
            for directory in benchmark_path[:-1]:
                if not directory in curdir:
                    curdir[directory] = dict()
                curdir = curdir[directory]
            curdir[benchmark_path[-1]] = drow[COL_BENCHMARK_ID]
    return (solvers,benchmarks)

def open_space(spaceid, name):
    print(f'''<Space id="{spaceid}" name="{name}">
<SpaceAttributes>
<description value="no description" />
<sticky-leaders value="true" />
<inherit-users value="true" />
<locked value="false" />
<add-benchmark-perm value="false" />
<add-job-perm value="false" />
<add-solver-perm value="false" />
<add-space-perm value="false" />
<add-user-perm value="false" />
<rem-benchmark-perm value="false" />
<rem-job-perm value="false" />
<rem-solver-perm value="false" />
<rem-space-perm value="false" />
<rem-user-perm value="false" />
</SpaceAttributes>
''')

def close_space():
    print('</Space>')

def write_directory(spaceid, name, content, solver, solverid):
    if isinstance(content, dict):
        open_space(spaceid, name)
        spaceid += 1
        for (directory, subcontent) in sorted(content.items()):
            spaceid = write_directory(spaceid, directory, subcontent, solver, solverid)
        print(f'<Solver id="{solverid}" name="{solver}" />')
        close_space()
    else:
        print(f'<Benchmark id="{content}" name="{name}" />')
    return spaceid
    
def write_xml(solvers, benchmarks):
    spaceid = 1
    print('<ns0:Spaces xmlns:ns0="https://www.starexec.org/starexec/public/batchSpaceSchema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.starexec.org/starexec/public/batchSpaceSchema.xsd batchSpaceSchema.xsd">')
    for (solverid, solver) in sorted(solvers.items()):
        spaceid = write_directory(spaceid, solver, benchmarks[solverid], solver, solverid)
    print('</ns0:Spaces>')

def main():
    global g_args, g_xml_tree
    parser = ArgumentParser(
            usage="make_space_from_pairs.py <pairs.csv>\n\n"\
                  "Create a space for all pairs in the given csv file in "\
                  "a format suitable for upload as space xml to StarExec.")
    parser.add_argument ("pairs_csv",
            help="the input pairs which should be rerun")
    g_args = parser.parse_args()

    if not os.path.exists(g_args.pairs_csv):
        die("file not found: {}".format(g_args.pairs_csv))

    solvers, benchmarks = read_csv()
    write_xml(solvers, benchmarks)

if __name__ == '__main__':
    main()
