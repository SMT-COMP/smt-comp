#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re
import json

g_submissions = None

from extract_data_from_solvers_divisions import g_logics_all as g_logics_all
from extract_data_from_solvers_divisions import (
    TRACK_SINGLE_QUERY_RAW,
    TRACK_INCREMENTAL_RAW,
    TRACK_UNSAT_CORE_RAW,
    TRACK_MODEL_VALIDATION_RAW,
    TRACK_PROOF_EXHIBITION_RAW,
    TRACK_PARALLEL_RAW,
    TRACK_CLOUD_RAW)

TRACK_SINGLE_QUERY_REGEX='track_single_query_regex'
TRACK_INCREMENTAL_REGEX='track_incremental_regex'
TRACK_UNSAT_CORE_REGEX='track_unsat_core_regex'
TRACK_MODEL_VALIDATION_REGEX='track_model_validation_regex'
TRACK_PROOF_EXHIBITION_REGEX='track_proof_exhibition_regex'
TRACK_PARALLEL_REGEX='track_parallel_regex'
TRACK_CLOUD_REGEX='track_cloud_regex'

class ColumnNames:
    def __init__(self, year):
        self.colnames_base(year)
        if year >= 2022:
            self.colnames_2022()

    def colnames_2022(self):
        self.STAREXEC_SOLVERID = 'StarExec ID of your preliminary solver.    If you have different solver ids for several track, please provide them as "12345,12346(uc),12347(inc)".  The tracks are single-query (sq), unsat-core (uc), incremental (inc), model-validation (mv), proof-exhibition (pe).'
        self.SINGLE_QUERY_TRACK = 'For the Single-Query Track, give a regular expression for the supported logics.'
        self.INCREMENTAL_TRACK = 'For the Incremental Track, give a regular expression for the supported logics.'
        self.MODEL_VALIDATION_TRACK = 'For the Model-Validation Track, give a regular expression for the supported logics.'
        self.UNSAT_CORE_TRACK = 'For the Unsat-Core Track, give a regular expression for the supported logics.'
        self.PROOF_EXHIBITION_TRACK = 'For the Proof-Exhibition Track, give a regular expression for the supported logics.'
        self.PARALLEL_TRACK = 'For the Parallel Track, give a regular expression for the supported logics.  (You need to register for the parallel track separately)'
        self.CLOUD_TRACK = 'For the Cloud Track, give a regular expression for the supported logics.  (You need to register for the cloud track separately)'

    def colnames_base(self, year):
        rules = "rules" if year >= 2021 else f"rules{year - 2000}"
        self.USERNAME = 'Username'
        self.SOLVER_NAME = 'Name of Solver'
        self.SOLVER_HOMEPAGE = 'Solver homepage'
        self.SYSDESCR = 'System description  URL'
        self.SYSDESCR_TITLE = 'Title of the system description'
        self.STAREXEC_LINK = 'Link to StarExec solver'
        self.SINGLE_QUERY_TRACK = 'Select all divisions in the Single-Query (previously: Main) Track and the Unsat-Core Track to submit the solver to: '
        self.INCREMENTAL_TRACK = 'Select all divisions in the Incremental Track to submit the solver to:'
        self.MODEL_VALIDATION_TRACK = 'Select all divisions in the Model-Validation Track to submit the solver to:'
        self.VARIANT = 'If this solver is a VARIANT of another submission, e.g. an experimental version, provide the name and the StarExec ID of the main solver, otherwise leave blank.'
        self.WRAPPER = f'If this solver is a WRAPPER TOOL (i.e., it includes and calls one or more other SMT solvers, see Section 4 of the competition rules at https://smt-comp.github.io/{year}/{rules}.pdf), list ALL wrapped solvers and their exact version here, otherwise leave blank.'
        self.DERIVED = f'If this solver is a DERIVED TOOL (i.e., any solver that is based on or extends another SMT solver, see Section 4 of the competition rules at https://smt-comp.github.io/{year}/{rules}.pdf), provide the name of the original tool here. A derived tool should follow the naming convention [name-of-base-solver]-[my-solver-name].'
        self.TEAM = 'Please list all contributors that you wish to be acknowledged here'
        self.SEED = 'Seed'
        self.HOMEPAGE = 'Solver homepage'
        self.SYSDESCR = 'System description URL'
        self.SYSDESCR_NAME = 'Title of the system description'


# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def find_matches(logics, regexstr):
    regex = re.compile(regexstr)
    return [ l for l in logics if re.fullmatch(regex, l) ]

def collect_logics_regex(submission, drow, divisions):
    assert divisions is not None
    submission[TRACK_SINGLE_QUERY_REGEX] = drow[col.SINGLE_QUERY_TRACK]
    submission[TRACK_INCREMENTAL_REGEX] = drow[col.INCREMENTAL_TRACK]
    submission[TRACK_UNSAT_CORE_REGEX] = drow[col.UNSAT_CORE_TRACK]
    submission[TRACK_MODEL_VALIDATION_REGEX] = drow[col.MODEL_VALIDATION_TRACK]
    submission[TRACK_PROOF_EXHIBITION_REGEX] = drow[col.PROOF_EXHIBITION_TRACK]
    submission[TRACK_PARALLEL_REGEX] = drow[col.PARALLEL_TRACK]
    submission[TRACK_CLOUD_REGEX] = drow[col.CLOUD_TRACK]

    submission[TRACK_SINGLE_QUERY_RAW] = find_matches(divisions[TRACK_SINGLE_QUERY_RAW], drow[col.SINGLE_QUERY_TRACK])
    submission[TRACK_MODEL_VALIDATION_RAW] = find_matches(divisions[TRACK_MODEL_VALIDATION_RAW], drow[col.MODEL_VALIDATION_TRACK])
    submission[TRACK_UNSAT_CORE_RAW] = find_matches(divisions[TRACK_UNSAT_CORE_RAW], drow[col.UNSAT_CORE_TRACK])
    submission[TRACK_INCREMENTAL_RAW] = find_matches(divisions[TRACK_INCREMENTAL_RAW], drow[col.INCREMENTAL_TRACK])
    submission[TRACK_PROOF_EXHIBITION_RAW] = find_matches(divisions[TRACK_PROOF_EXHIBITION_RAW], drow[col.PROOF_EXHIBITION_TRACK])
    submission[TRACK_PARALLEL_RAW] = find_matches(divisions[TRACK_PARALLEL_RAW], drow[col.PARALLEL_TRACK])
    submission[TRACK_CLOUD_RAW] = find_matches(divisions[TRACK_CLOUD_RAW], drow[col.CLOUD_TRACK])

def collect_logics_2021(submission, drow):
    """Collect logics for single-query and unsat core track.

    The form had a section with SQ and UC track as matrix.
    The resulting csv thus had logic columns that stated which
    tracks are entered for these two tracks."""
    submission[TRACK_INCREMENTAL_RAW] = drow[col.INCREMENTAL_TRACK].split(';')
    submission[TRACK_MODEL_VALIDATION_RAW] = drow[col.MODEL_VALIDATION_TRACK].split(';')
    submission[TRACK_SINGLE_QUERY_RAW] = []
    submission[TRACK_UNSAT_CORE_RAW] = []
    for key, value in drow.items():
        if not key.startswith(col.SINGLE_QUERY_TRACK):
            continue
        logic = key.replace(col.SINGLE_QUERY_TRACK, '')
        if not value:
            continue
        assert logic[0] == '['
        assert logic[-1] == ']'
        logic = logic[1:-1]
        tracks = value.split(';')
        if 'Single-Query Track' in tracks:
            submission[TRACK_SINGLE_QUERY_RAW].append(logic)
        if 'Unsat Core Track' in tracks:
            submission[TRACK_UNSAT_CORE_RAW].append(logic)


def normalize_whitespace(drow):
    for key in drow.keys():
        drow[key] = re.sub(r'\s+', ' ', drow[key])
        drow[key] = drow[key].strip()


# Read csv with submissions data from Google Form.
def read_csv(col, fname, year, division):
    global g_submissions, g_logics_all
    with open(fname) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        g_submissions = []

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            normalize_whitespace(drow)
            submission = dict()
            submission['username'] = drow[col.USERNAME]
            submission['solver_name'] = drow[col.SOLVER_NAME]
            if year < 2022:
                m = re.search(
                    'solver\.jsp\?id=(\d+)', drow[col.STAREXEC_LINK])
                assert(m)
                submission['solver_id'] = m.group(1)
            else:
                submission['solver_id'] = drow[col.STAREXEC_SOLVERID]
            m = re.search('solver\.jsp\?id=(\d+)', drow[col.VARIANT])
            if not m:
                submission['variant'] = drow[col.VARIANT]
            else:
                submission['variant'] = m.group(1)
            submission['wrapper'] = drow[col.WRAPPER]
            submission['derived'] = drow[col.DERIVED]
            submission['team'] = drow[col.TEAM]
            submission['seed'] = drow[col.SEED]
            submission['homepage'] = drow[col.HOMEPAGE]
            submission['sysdescr_url'] = drow[col.SYSDESCR]
            submission['sysdescr_name'] = drow[col.SYSDESCR_NAME]

            if year < 2022:
                collect_logics_2021(submission, drow)
            else:
                collect_logics_regex(submission, drow, divisions)

            if (not submission[TRACK_INCREMENTAL_RAW] and
                not submission[TRACK_MODEL_VALIDATION_RAW] and
                not submission[TRACK_SINGLE_QUERY_RAW] and
                not submission[TRACK_UNSAT_CORE_RAW] and
                not submission[TRACK_PROOF_EXHIBITION_RAW] and
                not submission[TRACK_PARALLEL_RAW] and
                not submission[TRACK_CLOUD_RAW]):
                die(f'Solver "{drow[col.SOLVER_NAME]}" '\
                    'does not participate in any track')

            g_submissions.append(submission)


# Write csv with uniform submission data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
def write_csv_2021(fname):
    with open(fname, 'w') as outfile:
        outfile.write(",".join([
            "Preliminary Solver ID",
            "Solver ID",
            "Wrapped Solver ID Single Query",
            "Wrapped Solver ID Incremental",
            "Wrapped Solver ID Model Validation",
            "Wrapped Solver ID Unsat Core",
            "Solver Name",
            "Solver homepage",
            "System description URL",
            "System description name",
            "Competing",
            "Single Query Track",
            "Incremental Track",
            "Model Validation Track",
            "Unsat Core Track",
            "Variant Of",
            "Wrapper Tool",
            "Derived Tool",
            "Contact",
            "Team Members",
            "Seed",
            ]) + "\n")
        for submission in g_submissions:
            outfile.write("{},-1,,,,,\"{}\",\"{}\",\"{}\",\"{}\",{},"
                          .format(
                submission['solver_id'],
                submission['solver_name'],
                submission['homepage'],
                submission['sysdescr_url'],
                submission['sysdescr_name'],
                "yes"))
            for track in [TRACK_SINGLE_QUERY_RAW,
                          TRACK_INCREMENTAL_RAW,
                          TRACK_MODEL_VALIDATION_RAW,
                          TRACK_UNSAT_CORE_RAW]:
                if submission[track] == ['ALL']:
                    outfile.write(";".join(g_logics_all[track]))
                else:
                    outfile.write(";".join(submission[track]))
                outfile.write(",")
            outfile.write(
                    "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",{}".format(
                        submission['variant'],
                        submission['wrapper'],
                        submission['derived'],
                        submission['username'],
                        submission['team'],
                        submission['seed']
                        ))
            outfile.write("\n")

# Write csv with uniform submission data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
def write_csv_2022(fname):
    with open(fname, 'w') as outfile:
        outfile.write(",".join([
            "Preliminary Solver ID",
            "Solver ID",
            "Config ID Single Query",
            "Config ID Incremental",
            "Config ID Model Validation",
            "Config ID Unsat Core",
            "Config ID Proof Exhibition",
            "Solver Name",
            "Solver homepage",
            "System description URL",
            "System description name",
            "Competing",
            "Single Query Regex",
            "Incremental Regex",
            "Model Validation Regex",
            "Unsat Core Regex",
            "Proof Exhibition Regex",
            "Single Query Track",
            "Incremental Track",
            "Model Validation Track",
            "Unsat Core Track",
            "Proof Exhibition Track",
            "Variant Of",
            "Wrapper Tool",
            "Derived Tool",
            "Contact",
            "Team Members",
            "Seed",
            ]) + "\n")
        for submission in g_submissions:
            outfile.write("{},-1,,,,,,\"{}\",\"{}\",\"{}\",\"{}\",{},"
                          .format(
                re.sub(r',',';', submission['solver_id']),
                submission['solver_name'],
                submission['homepage'],
                submission['sysdescr_url'],
                submission['sysdescr_name'],
                "yes"))
            for track in [TRACK_SINGLE_QUERY_REGEX,
                          TRACK_INCREMENTAL_REGEX,
                          TRACK_MODEL_VALIDATION_REGEX,
                          TRACK_UNSAT_CORE_REGEX,
                          TRACK_PROOF_EXHIBITION_REGEX]:
                outfile.write(f'"{submission[track]}",')
            for track in [TRACK_SINGLE_QUERY_RAW,
                          TRACK_INCREMENTAL_RAW,
                          TRACK_MODEL_VALIDATION_RAW,
                          TRACK_UNSAT_CORE_RAW,
                          TRACK_PROOF_EXHIBITION_RAW]:
                outfile.write(";".join(submission[track]))
                outfile.write(",")
            outfile.write(
                    "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",{}".format(
                        submission['variant'],
                        submission['wrapper'],
                        submission['derived'],
                        submission['username'],
                        submission['team'],
                        submission['seed']
                        ))
            outfile.write("\n")


if __name__ == '__main__':
    parser = ArgumentParser(
            usage="extract_data_from_submission "\
                  "<year> <submissions: csv> <outfile: csv>\n\n"
                  "Extract and convert csv data from submission form into "
                  "uniformly formatted csv.")
    parser.add_argument("year", type=int,
            help="the year of the competition")
    parser.add_argument("-d", "--division", type=str, dest="division",
                        help="division.json file with tracks and logics",
                        required=False)
    parser.add_argument (
            "in_csv", help="the input submissions csv from Google Forms")
    parser.add_argument (
            "out_csv", help="the output csv")
    args = parser.parse_args()

    if not os.path.exists(args.in_csv):
        die("file not found: {}".format(args.in_csv))

    if args.division:
        with open(args.division) as file:
            divisions = json.load(file)
    else:
        divisions = None

    col = ColumnNames(args.year)
    read_csv(col, args.in_csv, args.year, divisions)
    if args.year >= 2022:
        write_csv_2022(args.out_csv)
    else:
        write_csv(args.out_csv)
