#!/usr/bin/env python3

import csv
import sys
import os
import glob
import re
from argparse import ArgumentParser
import datetime

COL_PAIR = 'pair id'
COL_BM = 'benchmark'
COL_SID = 'solver id'
COL_QUERY = 'query'
COL_RES = 'result'
COL_SOLVERS_NAME = 'Solver Name'
COL_SOLVERS_SID = 'Wrapped Solver ID Incremental'

jobs = dict()
divisions = dict()
solver_names = dict()

def parse_args():
    parser = ArgumentParser(description="Read a list of disagreements reported by incremental_search_disagreements.py. Report all disagreements in result files.")

    parser.add_argument("-c", "--csvfile",
            action="store",
            required="true",
            help="The csvfile for the incremental job"
            )

    parser.add_argument("-s", "--solvers",
            action="store",
            required="true",
            help="The solver registration csv"
            )

    parser.add_argument("-o", "--outdir",
            action="store",
            required="true",
            help="Where to place the .mds"
            )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    with open(args.csvfile, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        for row in csvreader:
            drow = dict(zip(iter(header), iter(row)))
            jobs[drow[COL_PAIR]] = (drow[COL_BM], drow[COL_SID])

    with open(args.solvers) as solvers:
        s_reader = csv.reader(solvers)
        s_header = next(s_reader)
        solver_names = dict()
        for row in s_reader:
            drow = dict(zip(iter(s_header), iter(row)))
            solver_names[drow[COL_SOLVERS_SID]] = drow[COL_SOLVERS_NAME]
        
    csvreader = csv.reader(sys.stdin)
    header = next(csvreader)
    for row in csvreader:
        drow = dict(zip(iter(header), iter(row)))
        benchmark, solver = jobs[drow[COL_PAIR]]
        m = re.match("[^/]*/(([^/]*)/.*)", benchmark)
        div = m.group(2)
        bench = m.group(1)
        if not div in divisions:
            divisions[div] = dict()
        file = bench + " query " + drow[COL_QUERY]
        if not file in divisions[div]:
            divisions[div][file] = dict()
        divisions[div][file][solver] = drow[COL_RES]

    for div in divisions:
        ostr_list = []
        ostr_list.append("---")
        ostr_list.append("layout: disagreements")
        ostr_list.append("year: 2020")
        ostr_list.append("gendate: %s" % datetime.datetime.now())
        ostr_list.append("track: track_incremental")
        ostr_list.append("participants: participants_2020")
        ostr_list.append("division: %s" % div)
        ostr_list.append("benchmarks:")
        for bm in divisions[div]:
            ostr_list.append("- name: %s" % bm)
            ostr_list.append("- jobs:")
            for solver in divisions[div][bm]:
                solver_name = solver_names[solver]
                ostr_list.append("  - name: %s" % (solver_name))
                ostr_list.append("    result: %s" % divisions[div][bm][solver])
        ostr_list.append("---")
        open(os.path.join(args.outdir, "%s-incremental.md" % div),
                'w').write("\n".join(ostr_list))
