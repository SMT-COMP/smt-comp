#!/usr/bin/env python3
#
# This script has been written to compute the scores of SMT-COMP
# It is purposefully trying to be flexible to changes in the scoring
# mechanisms. It can be used to apply scoring schemes from different
# years of the competition to different sets of data.
#
# This script requires the pandas data analysis framework
#
# @author Giles Reger, Aina Niemetz, Mathias Preiner
# @date 2019

# Data processing library pandas
import numpy
import pandas

# We need higher precisions for some of the reduction scores of the unsat-core
# track.
pandas.set_option('display.precision', 16)

# Options parsing
from argparse import ArgumentParser

import json
import os
import sys
import csv
import math
import time
import datetime

# StarExec result strings
RESULT_UNKNOWN = 'starexec-unknown'
RESULT_SAT = 'sat'
RESULT_UNSAT = 'unsat'

# Tracks
TRACK_SQ = "track_single_query"
TRACK_INC = "track_incremental"
TRACK_CHALL_SQ = "track_single_query_challenge"
TRACK_CHALL_INC = "track_incremental_challenge"
TRACK_UC = "track_unsat_core"
TRACK_MV = "track_model_validation"
TRACK_PE = "track_proof_exhibition"
TRACK_CLOUD = "track_cloud"
TRACK_PARALLEL = "track_parallel"

# Track options
OPT_TRACK_SQ = "sq"
OPT_TRACK_INC = "inc"
OPT_TRACK_CHALL_SQ = "chall_sq"
OPT_TRACK_CHALL_INC = "chall_inc"
OPT_TRACK_UC = "uc"
OPT_TRACK_MV = "mv"
OPT_TRACK_PE = "pe"
OPT_TRACK_CLOUD = "ct"
OPT_TRACK_PARALLEL = "pt"

# Columns of solvers csv
COL_SOLVER_ID = "Solver ID"
COL_SOLVER_NAME = "Solver Name"
COL_VARIANT_OF_ID = "Variant Of"
COL_COMPETING = "Competing"
COL_SOLVER_ID_SQ_2019 = "Wrapped Solver ID Single Query"
COL_SOLVER_ID_INC_2019 = "Wrapped Solver ID Incremental"
COL_SOLVER_ID_UC_2019 = "Wrapped Solver ID Unsat Core"
COL_SOLVER_ID_MV_2019 = "Wrapped Solver ID Model Validation"

COL_CONFIG_ID_SQ = "Config ID Single Query"
COL_CONFIG_ID_MV = "Config ID Model Validation"
COL_CONFIG_ID_UC = "Config ID Unsat Core"
COL_CONFIG_ID_INC = "Config ID Incremental"
COL_CONFIG_ID_PE = "Config ID Proof Exhibition"

# Extensions of results .md files
EXT_SQ = "-single-query.md"
EXT_INC = "-incremental.md"
EXT_CHALL_SQ = "-challenge-non-incremental.md"
EXT_CHALL_INC = "-challenge-incremental.md"
EXT_UC = "-unsat-core.md"
EXT_MV = "-model-validation.md"
EXT_PE = "-proof-exhibition.md"
EXT_CLOUD = "-cloud.md"
EXT_PARALLEL = "-parallel.md"

g_args = None

g_competitive = {}
g_solver_names = {}
g_solver_variants = {}

g_tracks = { OPT_TRACK_SQ: TRACK_SQ,
             OPT_TRACK_INC: TRACK_INC,
             OPT_TRACK_CHALL_SQ: TRACK_CHALL_SQ,
             OPT_TRACK_CHALL_INC: TRACK_CHALL_INC,
             OPT_TRACK_UC: TRACK_UC,
             OPT_TRACK_MV: TRACK_MV,
             OPT_TRACK_PE: TRACK_PE,
             OPT_TRACK_CLOUD: TRACK_CLOUD,
             OPT_TRACK_PARALLEL: TRACK_PARALLEL }

g_exts = { OPT_TRACK_SQ: EXT_SQ,
           OPT_TRACK_INC: EXT_INC,
           OPT_TRACK_CHALL_SQ: EXT_CHALL_SQ,
           OPT_TRACK_CHALL_INC: EXT_CHALL_INC,
           OPT_TRACK_UC: EXT_UC,
           OPT_TRACK_MV: EXT_MV,
           OPT_TRACK_PE: EXT_PE,
           OPT_TRACK_CLOUD: EXT_CLOUD,
           OPT_TRACK_PARALLEL: EXT_PARALLEL }

allLogics = set()
divisionInfo = {}


###############################################################################
# Helper functions
###############################################################################

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

# Log message.
def log(string):
    print("[score] {}".format(string))


# Split a benchmark string into benchmark, division and family.
def split_benchmark_division_family(x, family_func):
    assert len(x) == 2, "weird x: {0}".format(x)
    division, benchmark = x[0], x[1]
    # Check if division is a logic string.
    # Note: This assumes that space names are not in upper case.
    if not division.isupper():
        division, benchmark = benchmark.split('/', 1)
    family = family_func(benchmark)
    return benchmark, division, family

# Determine the top-most directory as benchmark family.
# Note: 'benchmark' is not prefixed with the division name.
def get_family_top(benchmark):
    return benchmark.split('/', 1)[0]

# Determine the bottom-most directory as benchmark family.
# Note: 'benchmark' is not prefixed with the division name.
def get_family_bot(benchmark):
    return benchmark.rsplit('/', 1)[0]

# Add columns for division and family.
# Also does some tidying of benchmark column for specific years of the
# competition. Edit this function if you want to edit how families are added.
def add_division_family_info(data, family_definition):
    # Select family extraction functions.
    # This depends on the family_definition option:
    #   - 'top' interprets the top-most directory, and
    #   - 'bot' interprets the bottom-most directory
    # as benchmark family.
    # The rules have always specified 'top' but the scoring scripts for many
    # years actually implemented 'bot'. The scripts allow you to choose.
    fam_func = None
    if family_definition == 'top':
        fam_func = get_family_top
    elif family_definition == 'bot':
        fam_func = get_family_bot
    else:
        die('Family option not supported: {}'.format(family_definition))

    split = data['benchmark'].str.split('/', n=1)
    split = split.map(lambda x: split_benchmark_division_family(x, fam_func))
    data['benchmark'] = split.str[0]
    data['division'] = split.str[1]
    data['family'] = split.str[2]
    return data

# Return solver name of solver with given solver id.
def get_solver_name(solver_id):
    global g_solver_names
    return g_solver_names.get(solver_id, solver_id)

# Helper to add mapping of solver id to solver name and solver variant id and
# to g_solver_names and g_solver_variants.
def map_solver_id(row, column):
    global g_competitive, g_solver_names, g_solver_variants
    if column not in row:
        return
    solver_id_str = row[column]
    solver_id = int(solver_id_str) if isinstance(solver_id_str, int) or solver_id_str.isnumeric() else None
    if solver_id:
        g_competitive[solver_id] = row[COL_COMPETING] == 'yes'
        g_solver_names[solver_id] = row[COL_SOLVER_NAME]
        g_solver_variants[solver_id] = row[COL_VARIANT_OF_ID] \
                if row[COL_VARIANT_OF_ID] else row[COL_SOLVER_NAME]

# Read csv mapping solver id to solver name and solver variant.
def read_solvers_csv():
    global g_args, g_solver_names, g_solver_variants, g_competitive
    data = pandas.read_csv(g_args.solvers, keep_default_na=False)
    for index, row in data.iterrows():
        assert not pandas.isnull(row[COL_SOLVER_ID])
        map_solver_id(row, COL_SOLVER_ID)
        map_solver_id(row, COL_SOLVER_ID_SQ_2019)
        map_solver_id(row, COL_SOLVER_ID_INC_2019)
        map_solver_id(row, COL_SOLVER_ID_UC_2019)
        map_solver_id(row, COL_SOLVER_ID_MV_2019)
        map_solver_id(row, COL_CONFIG_ID_SQ)
        map_solver_id(row, COL_CONFIG_ID_INC)
        map_solver_id(row, COL_CONFIG_ID_UC)
        map_solver_id(row, COL_CONFIG_ID_MV)
        map_solver_id(row, COL_CONFIG_ID_PE)


###############################################################################
# Main
###############################################################################


# Parse command line arguments.
def parse_args():
    global g_args

    parser = ArgumentParser()

    required = parser.add_argument_group("required arguments")
    required.add_argument("-c", "--csv",
                        metavar="path",
                        required=True,
                        help="input csv with results from StarExec")
    required.add_argument("-S", "--solvers",
                          metavar="csv",
                          required=True,
                          help="csv file that maps solver ID to solver name "\
                               "and solver variant "\
                               "and identifies if a solver is competitive")
    required.add_argument("-o", "--out",
                          metavar="csv",
                          required=True,
                          help="csv output aggregated by logic")

    g_args = parser.parse_args()

# Main function.
def main():
    global g_args, g_solver_names

    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_rows', None)

    parse_args()
    read_solvers_csv()

    data = pandas.read_csv(g_args.csv, keep_default_na=False)

    # Remove spaces from columns for ease (other functions rely on this)
    cols = data.columns
    cols = cols.map(lambda x: x.replace(' ', '_'))
    data.columns = cols

    incremental = 'wrong-answers' in data.columns

    # For incremental tracks, the CSV does not contain the 'expected' column.
    if incremental:
        assert 'expected' not in data.columns
        data['expected'] = None

    # Make sure that the expected column contains RESULT_SAT, RESULT_UNSAT or
    # RESULT_UNKNOWN. For some exported StarExec data, the expected column is
    # '-', which can happen when extracting the status of a benchmark fails
    # while uploading the benchmark to StarExec.
    data.loc[~data.expected.isin({RESULT_SAT, RESULT_UNSAT}),
             'expected'] = RESULT_UNKNOWN

    data = add_division_family_info(data, "bot")

    data["nb"] = 1

    data.drop(columns=["pair_id","benchmark","benchmark_id","solver","configuration","configuration_id","status","memory_usage"],inplace=True)
    # ["pair_id","solver_id","cpu_time","wallclock_time","memory_usage","result","expected","division","family"]

    data=data.groupby(by=["solver_id","division","family","result"],as_index=False).sum()
    data['solver'] = data.solver_id.map(get_solver_name)
    data.drop(columns=["solver_id"],inplace=True)

    with open(g_args.out, "w") as outfile:
        data.to_csv(path_or_buf=outfile, sep=',',index=False)

    #TODO: remove disagreementor not


if __name__ == "__main__":
    main()
