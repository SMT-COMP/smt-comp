#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_submissions = None

g_logics_all = {
        'track_single_query'     : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        'track_incremental'      : [
            'ABVFP','ALIA','ANIA','AUFNIRA','BV','BVFP','LIA','LRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFBVLIA',
            'QF_AUFBVNIA','QF_AUFLIA','QF_BV','QF_BVFP','QF_FP','QF_LIA',
            'QF_LRA','QF_NIA','QF_UF','QF_UFBV','QF_UFBVLIA','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','UFLRA',
            ],
        'track_challenge'        : [
            'QF_BV (non-incremental)',
            'QF_BV (incremental)',
            'QF_ABV (non-incremental)',
            'QF_ABV (incremental)',
            'QF_AUFBV (non-incremental)',
            'QF_AUFBV (incremental)',
            ],
        'track_unsat_core'       : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        'track_model_validation' : ['QF_BV']
        }

COL_SINGLE_QUERY_TRACK = 'Select all divisions in the Single-Query (previously: Main) Track and the Unsat-Core Track to submit the solver to (use checkbox ALL for all divisions): '
COL_INCREMENTAL_TRACK = 'Select all divisions in the Incremental Track to submit the solver to (use checkbox ALL for all divisions):'
COL_MODEL_VALIDATION_TRACK = 'Select all divisions in the Model-Validation Track (experimental) to submit the solver to:'
COL_CHALLENGE_TRACK = 'Select all divisions in the Industry-Challenge Track to submit the solver to (use checkbox ALL for all divisions):'

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

# Read csv with submissions data from Google Form.
def read_csv(fname):
    global g_submissions, g_logics_all
    with open(fname) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        g_submissions = []

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            submission = dict()
            submission['username'] = drow['Username']
            submission['solver_name'] = drow['Name of Solver']
            m = re.search(
                    'solver\.jsp\?id=(\d+)', drow['Link to StarExec solver'])
            assert(m)
            submission['solver_id'] = m.group(1)
            submission['track_incremental'] = drow[COL_INCREMENTAL_TRACK].split(';')
            submission['track_model_validation'] = drow[COL_MODEL_VALIDATION_TRACK].split(';')
            submission['track_challenge'] = drow[COL_CHALLENGE_TRACK].split(';')
            submission['track_single_query'] = []
            submission['track_unsat_core'] = []

            # Collect logics for single-query and unsat core track.
            #
            # The form had a section with SQ and UC track as matrix.
            # The resulting csv thus had logic columns that stated which
            # tracks are entered for these two tracks.
            for key, value in drow.items():
                if not key.startswith(COL_SINGLE_QUERY_TRACK):
                    continue
                if not value:
                    continue
                logic = key.replace(COL_SINGLE_QUERY_TRACK, '')
                assert logic[0] == '['
                assert logic[-1] == ']'
                logic = logic[1:-1]
                tracks = value.split(';')
                if 'Single-Query Track' in tracks:
                    submission['track_single_query'].append(logic)
                if 'Unsat Core Track' in tracks:
                    submission['track_unsat_core'].append(logic)

            if not submission['track_incremental'] and \
               not submission['track_model_validation'] and \
               not submission['track_single_query'] and \
               not submission['track_unsat_core']:
                die('Configuration "{}" '\
                    'does not participate in any track'.format(
                        submission['solver_name']))

            g_submissions.append(submission)


# Write csv with uniform submission data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
def write_csv(fname):
    with open(fname, 'w') as outfile:
        outfile.write("{},{},{},{},{},{},{}\n".format(
            "Solver ID", "Solver Name",
            "Single Query Track",
            "Incremental Track",
            "Challenge Track",
            "Model Validation Track",
            "Unsat Core Track"))
        for submission in g_submissions:
            outfile.write("{},\"{}\",".format(
                submission['solver_id'], submission['solver_name']))
            for track in ['track_single_query',
                          'track_incremental',
                          'track_challenge',
                          'track_model_validation',
                          'track_unsat_core']:
                if submission[track] == ['ALL']:
                    outfile.write(";".join(g_logics_all[track]))
                else:
                    outfile.write(";".join(submission[track]))
                outfile.write(",")
            outfile.write("\n")



if __name__ == '__main__':
    parser = ArgumentParser(
            usage="extract_data_from_submission "\
                  "<submissions: csv> <outfile: csv>\n\n"
                  "Extract and convert csv data from submission form into "
                  "uniformly formatted csv.")
    parser.add_argument (
            "in_csv", help="the input submissions csv from Google Forms")
    parser.add_argument (
            "out_csv", help="the output csv")
    args = parser.parse_args()

    if not os.path.exists(args.in_csv):
        die("file not found: {}".format(args.in_csv))

    read_csv(args.in_csv)
    write_csv(args.out_csv)
