#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import subprocess
import os

COL_SOLVER_ID = 'Solver ID'
COL_SOLVER_NAME = 'Solver Name'
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="wrap_solvers <solvers: csv> <space: id> <inc_space: id>\n\n"

                  "Download, wrap and upload solvers for non-incremental and "
                  "incremental tracks.")
    parser.add_argument ("csv",
            help="the input csv with solvers and divisions as generated from"\
                 "tools/prep/extract_data_from_submission.py")
    parser.add_argument ("space_id",
            help="the StarExec space id for non-incremental wrapped solvers")
    parser.add_argument ("space_id_inc",
            help="the StarExec space id for incremental wrapped solvers")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        die("file not found: {}".format(args.csv))

    with open(args.csv, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            solver_id = drow[COL_SOLVER_ID]
            solver_name = drow[COL_SOLVER_NAME]
            single_query_track = drow[COL_SINGLE_QUERY_TRACK]
            incremental_track = drow[COL_INCREMENTAL_TRACK]

            print(solver_name)

            if single_query_track:
                print('wrapping for single query track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-sq', 'wrapper_sq', solver_id, args.space_id, "solvers"])
                p.communicate()
            if incremental_track:
                print('wrapping for incremental track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-inc', 'wrapper_inc', solver_id, args.space_id_inc, "solvers-inc"])
                p.communicate()

