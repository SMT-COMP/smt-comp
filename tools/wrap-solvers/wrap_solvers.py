#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import subprocess
import os

COL_SOLVER_ID = 'Solver ID'
COL_SOLVER_NAME = 'Solver Name'
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="wrap_solvers <solvers: csv> <space: id> <inc_space: id>\n\n"

                  "Download, wrap and upload solvers for non-incremental and "
                  "incremental tracks.")
    parser.add_argument ("csv",
            help="the input csv with solvers and divisions as generated from"\
                 "tools/prep/extract_data_from_submission.py")
    parser.add_argument ("--sq", dest="space_id",
            help="the StarExec space id for non-incremental wrapped solvers")
    parser.add_argument ("--inc", dest="space_id_inc",
            help="the StarExec space id for incremental wrapped solvers")
    parser.add_argument ("--mv", dest="space_id_mv",
            help="the StarExec space id for model validation track wrapped solvers")
    parser.add_argument ("--uc", dest="space_id_uc",
            help="the StarExec space id for unsat core track wrapped solvers")
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
            unsat_core_track = drow[COL_UNSAT_CORE_TRACK]
            model_validation_track = drow[COL_MODEL_VALIDATION_TRACK]

            print(solver_name)

            if args.space_id and single_query_track:
                print('wrapping for single query track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-sq', 'wrapper_sq', solver_id, args.space_id, "solvers"])
                p.communicate()
            if args.space_id_mv and model_validation_track:
                print('wrapping for model validation track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-mv', 'wrapper_sq', solver_id, args.space_id_mv, "solvers-mv"])
                p.communicate()
            if args.space_id_uc and unsat_core_track:
                print('wrapping for unsat core track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-uc', 'wrapper_sq', solver_id, args.space_id_uc, "solvers-uc"])
                p.communicate()
            if args.space_id_inc and incremental_track:
                print('wrapping for incremental track')
                p = subprocess.Popen(['./wrap_solver.sh', 'wrapped-inc', 'wrapper_inc', solver_id, args.space_id_inc, "solvers-inc"])
                p.communicate()

