#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import subprocess
import os
import re

COL_SOLVER_ID = 'Solver ID'
COL_PRELIM_SOLVER_ID = 'Preliminary Solver ID'
COL_SOLVER_NAME = 'Solver Name'
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'
COL_PROOF_EXHIBITION_TRACK = 'Proof Exhibition Track'

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)


def find_solver_id(solverid, track):
    solverid = f";{solverid};"
    regextrack = re.compile(f';(\d+)\({track}\);')
    m = re.search(regextrack, solverid)
    if m is not None:
        return m.group(1)
    regex = r';(\d+);'
    m = re.search(regex, solverid)
    if m is not None:
        return m.group(1)
    die(f"cannot find solver id for {track}: {solverid}")

def run_wrapper(args, wrap_script, solver_id):
    mydir = os.path.dirname(os.path.abspath(__file__)) + '/'
    script_args = [ mydir + 'wrap_solver.sh']
    if args.download_only:
        script_args.append("-d")
    if args.unzip_only:
        script_args.append("-x")
    if args.wrap_only:
        script_args.append("-w")
    if args.upload_only:
        script_args.append("-u")
    if args.wrap:
        script_args.append("-W")
    if args.zip_only:
        script_args.append("-z")
    script_args.extend(['wrapped', mydir + wrap_script, solver_id, "solvers"])
    print(script_args)
    p = subprocess.Popen(script_args)
    p.communicate()

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="wrap_solvers [options] <solvers: csv>\n\n"

                  "Download, wrap and upload solvers for incremental and "
                  "proof tracks.")
    parser.add_argument ("csv",
            help="the input csv with solvers and divisions as generated from"\
                 "tools/prep/extract_data_from_submission.py")
    parser.add_argument ("-d", dest="download_only", action="store_true",
                         default=False,
                         help="download solvers only")
    parser.add_argument ("-x", dest="unzip_only", action="store_true",
                         default=False,
                         help="unzip solvers only")
    parser.add_argument ("-w", dest="wrap_only", action="store_true",
                         default=False,
                         help="wrap solvers only")
    parser.add_argument ("-W", dest="wrap", action="store_true",
                         default=False,
                         help="wrap solvers")
    parser.add_argument ("-u", dest="upload_only", action="store_true",
                         default=False,
                         help="upload solvers only")
    parser.add_argument ("-z", dest="zip_only", action="store_true",
                         default=False,
                         help="only zip solvers from existing wrapped "
                              "directories when wrapping")
    parser.add_argument ("--prelim", dest="preliminary", action="store_true",
            help="wrap the preliminary solvers")
    args = parser.parse_args()
    if args.preliminary:
        COL_SOLVER_ID = COL_PRELIM_SOLVER_ID

    if not os.path.exists(args.csv):
        die("file not found: {}".format(args.csv))

    if not os.path.exists("wrapper_inc/smtlib2_trace_executor"):
        die("Please, copy the smtlib2_trace_executor binary to wrapper_inc")

    with open(args.csv, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            solver_id = drow[COL_SOLVER_ID]
            solver_name = drow[COL_SOLVER_NAME]
            incremental_track = drow[COL_INCREMENTAL_TRACK]
            proof_exhibition_track = drow[COL_PROOF_EXHIBITION_TRACK]

            solver_id_inc = (find_solver_id(solver_id, 'inc')
                             if incremental_track else None)
            solver_id_pe = (find_solver_id(solver_id, 'pe')
                            if proof_exhibition_track else None)

            if solver_id_inc is None and solver_id_pe is None:
                continue
            
            if solver_id_inc == solver_id_pe:
                print(f'wrapping {solver_name} for incremental and proof exhibition track')
                run_wrapper(args, 'wrap_incremental_proof.sh', solver_id_inc)

            else:
                if solver_id_inc is not None:
                    print(f'wrapping {solver_name} for incremental track')
                    run_wrapper(args, 'wrap_incremental.sh', solver_id_inc)

                if solver_id_pe is not None:
                    print(f'wrapping {solver_name} for proof exhibition track')
                    run_wrapper(args, 'wrap_proof.sh', solver_id_pe)
