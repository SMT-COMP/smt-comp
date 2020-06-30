#!/usr/bin/env python3

import csv
import sys
import os
from argparse import ArgumentParser
import datetime

def parse_args():

    parser = ArgumentParser()

    parser.add_argument("-i", "--input",
            action="store",
            required="true",
            help="The input csv containing disagreements"
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

COL_BM = 'benchmark'
COL_SID = 'solver id'
COL_RES = 'result'
COL_SOLVERS_NAME = 'Solver Name'
COL_SOLVERS_SID = 'Wrapped Solver ID Single Query'

if __name__ == '__main__':
    args = parse_args()

    divisions = dict()

    with open(args.input) as disagreements, \
            open(args.solvers) as solvers:


        s_reader = csv.reader(solvers)
        s_header = next(s_reader)
        solver_names = dict()
        for row in s_reader:
            drow = dict(zip(iter(s_header), iter(row)))
            solver_names[drow[COL_SOLVERS_SID]] = drow[COL_SOLVERS_NAME]

        reader = csv.reader(disagreements)
        header = next(reader)

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            benchmark = drow[COL_BM]
            solver_id = drow[COL_SID]
            result = drow[COL_RES]

            div = benchmark.split('/')[0]
            if div not in divisions:
                divisions[div] = dict()
            if benchmark not in divisions[div]:
                divisions[div][benchmark] = dict()
            divisions[div][benchmark][solver_id] = result

    for div in divisions:
        ostr_list = []
        ostr_list.append("---")
        ostr_list.append("layout: disagreements")
        ostr_list.append("year: 2020")
        ostr_list.append("gendate: %s" % datetime.datetime.now())
        ostr_list.append("track: track_single_query")
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
        open(os.path.join(args.outdir, "%s.md" % div),
                'w').write("\n".join(ostr_list))
