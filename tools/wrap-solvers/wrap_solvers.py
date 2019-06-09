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
            usage="wrap_solvers [options] <solvers: csv>\n\n"

                  "Download, wrap and upload solvers for non-incremental and "
                  "incremental tracks.")
    parser.add_argument ("csv",
            help="the input csv with solvers and divisions as generated from"\
                 "tools/prep/extract_data_from_submission.py")
    parser.add_argument ("-d", dest="download_only", action="store_true",
                         default=False,
                         help="download solvers only")
    parser.add_argument ("-w", dest="wrap_only", action="store_true",
                         default=False,
                         help="wrap solvers only")
    parser.add_argument ("-W", dest="wrap", action="store_true",
                         default=False,
                         help="wrap solvers")
    parser.add_argument ("-u", dest="upload_only", action="store_true",
                         default=False,
                         help="upload solvers only")
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

            add_args = []
            if args.download_only:
                add_args.append("-d")
            if args.wrap_only:
                add_args.append("-w")
            if args.upload_only:
                add_args.append("-u")
            if args.wrap:
                add_args.append("-W")

            script_args = [os.path.dirname(os.path.abspath(__file__)) + '/wrap_solver.sh']
            if args.space_id and single_query_track:
                print('wrapping for single query track')
                script_args.extend(add_args)
                script_args.extend(['wrapped-sq', 'wrapper_sq', solver_id, args.space_id, "solvers"])
                p = subprocess.Popen(script_args)
                p.communicate()
            if args.space_id_mv and model_validation_track:
                print('wrapping for model validation track')
                script_args.extend(add_args)
                script_args.extend(['wrapped-mv', 'wrapper_sq', solver_id, args.space_id_mv, "solvers-mv"])
                p = subprocess.Popen(script_args)
                p.communicate()
            if args.space_id_uc and unsat_core_track:
                print('wrapping for unsat core track')
                script_args.extend(add_args)
                script_args.extend(['wrapped-uc', 'wrapper_sq', solver_id, args.space_id_uc, "solvers-uc"])
                p = subprocess.Popen(script_args)
                p.communicate()
            if args.space_id_inc and incremental_track:
                print('wrapping for incremental track')
                script_args.extend(add_args)
                script_args.extend(['./wrap_solver.sh', 'wrapped-inc', 'wrapper_inc', solver_id, args.space_id_inc, "solvers-inc"])
                p = subprocess.Popen(script_args)
                p.communicate()

