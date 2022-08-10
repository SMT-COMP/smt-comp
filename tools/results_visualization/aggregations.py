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
g_logic_to_division = {}

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

def read_logic_to_division():
   global g_logic_to_division, divisionInfo
   # Read divisions from a JSON formatted file.
   divisionInfo = json.load(open(g_args.divisions_map))
   trackDivisions = divisionInfo[g_tracks[g_args.track]]
   for division in trackDivisions:
     logics = trackDivisions[division]
     for logic in logics:
         assert logic not in g_logic_to_division,"logic in multiple division"
         g_logic_to_division[logic] = division

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
    global g_logic_to_division
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
    data['logic'] = split.str[1]
    data['division'] = split.str[1].map(g_logic_to_division)
    data['family'] = split.str[2]
    return data

# Return true if the solver with given id is competitive.
def is_competitive_solver(solver_config_id):
    global g_competitive
    return g_competitive[solver_config_id]

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

# Drop any rows that contain benchmarks with status unknown where two otherwise
# sound solvers disagree on the result.
def remove_disagreements(data):
    global g_args

    # First find and filter out unsound solvers, i.e., solvers that disagree
    # with the expected status.
    unsound_solvers = set(data[(data.expected != RESULT_UNKNOWN)
                               & (data.result != RESULT_UNKNOWN)
                               & (data.result != data.expected)]['solver'])

    # Consider only unknown benchmarks that were solved by sound solvers.
    solved_unknown = data[(data.expected == RESULT_UNKNOWN)
                          & (~data.solver.isin(unsound_solvers))
                          & ((data.result == RESULT_SAT)
                              | (data.result == RESULT_UNSAT))]

    # Remove duplicate (benchmark, result) pairs to produces unique
    # result values for each benchmark.
    solved_unknown = solved_unknown.drop_duplicates(
                            subset=['benchmark', 'result'])

    # Group by division + benchmarks and count the number of results. It's
    # necessary to group by division as well as family+name can give duplicates
    grouped_results = solved_unknown.groupby(['division', 'benchmark'], as_index=False).agg(
                            {'result': 'count'})

    # If the number of results is more than one, we have disagreeing solvers,
    # i.e., the result column contains 'sat' and 'unsat' for the corresponding
    # benchmark.
    disagreements = grouped_results[grouped_results['result'] > 1]

    exclude = list(zip(disagreements['division'], disagreements['benchmark']))

    if g_args.log:
        log('Found {} disagreements:'.format(len(exclude)))
        i = 1
        for d, b in exclude:
            log('[{}] {}/{}'.format(i, d, b))
            bad_solvers = data[(data.benchmark == b) & (~data.solver.isin(unsound_solvers))
                          & ((data.result == RESULT_SAT)
                              | (data.result == RESULT_UNSAT))]
            print(bad_solvers[["solver", "result", "cpu_time"]].to_string(header=None, index=False))
            i += 1

    # Exclude benchmarks on which solvers disagree.
    data = data[~(data.benchmark.isin(set(disagreements.benchmark)))]
    return data


###############################################################################
# Main
###############################################################################


# Parse command line arguments.
def parse_args():
    global g_args

    parser = ArgumentParser()

    parser.add_argument("-T", "--track",
                        default=OPT_TRACK_SQ,
                        choices=[OPT_TRACK_SQ, OPT_TRACK_INC, OPT_TRACK_UC,
                                 OPT_TRACK_MV, OPT_TRACK_PE, OPT_TRACK_CHALL_SQ,
                                 OPT_TRACK_CHALL_INC, OPT_TRACK_CLOUD,
                                 OPT_TRACK_PARALLEL],
                        help="A string identifying the competition track")
    parser.add_argument("-l", "--log",
                        action="store_true",
                        default=False,
                        help="Enable logging")

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

    required.add_argument("-D", "--divisions-map",
                        metavar="json",
                          required=True,
                        default=None,
                        help="Divisions per track.")
    required.add_argument("-t", "--time",
                        metavar="time[,time...]",
                        required=True,
                        help="list of time limits matching given input csvs")
    g_args = parser.parse_args()

# Main scoring function that allows it to capture different scoring schemes.
# division       : the division to compute the scores for
# data           : the results data of this division
# wclock_limit   : the wallclock time limit
# year           : the string identifying the year of the results
# filter_result  : - None: consider all instances
#                  - RESULT_SAT: consider only satisfiable instances
#                  - RESULT_UNSAT: consider only unsatisfiable instances
# use_families   : use weighted scoring scheme (as used from 2016-2018)
# skip_unknowns  : skip benchmarks with status unknown (as done prior to 2017)
def score(
          data,
          wclock_limit,
          filter_result,
          year,
          use_families,
          skip_unknowns,
          sequential):
    global g_args
    assert not filter_result or filter_result in [RESULT_SAT, RESULT_UNSAT]

    if g_args.log: log("Score for {} in {}".format(year, "ALL"))

    num_benchmarks = len(data.benchmark.unique())
    if g_args.log: log("Computing scores for {}".format("ALL"))
    if g_args.log: log("... with {} benchmarks".format(num_benchmarks))

    family_scores = get_family_scores(data) if use_families else {}

    # Create new dataframe with relevant columns and populate new columns
    data_new = data[['division', 'logic', 'benchmark', 'family', 'solver', 'solver_id',
                     'cpu_time', 'wallclock_time', 'status', 'result',
                     'expected']].copy()
    if int(year) >= 2022:
        data_new['solver_id'] = data['configuration_id']
    data_new['year'] = year
    data_new['correct'] = 0       # Number of correctly solved benchmarks
    data_new['error'] = 0         # Number of wrong results
    data_new['correct_sat'] = 0   # Number of correctly solved sat benchmarks
    data_new['correct_unsat'] = 0 # Number of correctly solved unsat benchmarks
    data_new['division_size'] = num_benchmarks
    data_new['competitive'] = data_new.solver_id.map(is_competitive_solver)
    data_new['timeout'] = 0
    data_new['memout'] = 0
    data_new['unsolved'] = 0
    data_new['configuration_id'] = data['configuration_id']

    # Set the column that is used to determine if a benchmark was solved
    # within the time limit.
    time_column = 'cpu_time' if sequential else 'wallclock_time'

    # Set penalty of 'wclock_limit' seconds for jobs with memouts.
    data_new.loc[data_new.status == 'memout',
                 ['cpu_time', 'wallclock_time']] = [wclock_limit, wclock_limit]

    # Reset cpu_time/wallclock_time/status/result if wclock_limit is exceeded.
    # This can happen e.g., for the 24s scoring.
    data_new.loc[data_new[time_column] > wclock_limit,
                 ['cpu_time', 'wallclock_time', 'status', 'result']] = \
                    [wclock_limit, wclock_limit, 'timeout', RESULT_UNKNOWN]

    # Determine memouts/timeouts based on status.
    data_new.loc[data_new.status.str.startswith('timeout'), 'timeout'] = 1
    data_new.loc[data_new.status == 'memout', 'memout'] = 1

    # Column 'wrong-answers' only exists in incremental tracks.
    incremental = 'wrong-answers' in data.columns
    assert not incremental or 'correct-answers' in data.columns
    unsat_core = 'reduction' in data.columns
    assert not unsat_core or 'result-is-erroneous' in data.columns

    # Column 'model_validator_status' only exists in the model validation track.
    model_validation = 'model_validator_status' in data.columns
    if model_validation:
        data_new['model_validator_status'] = data['model_validator_status']
        data_new['model_validator_error'] = data['model_validator_error']
        data_new['model_validator_exception'] = data['model_validator_exception']
    # Column 'reason' only exists in proof exhibition track.
    proof_exhibition = 'reason' in data.columns
    if proof_exhibition:
        data_new['reason'] = data['reason']

    # Note: For incremental tracks we have to consider all benchmarks (also
    #       the ones that run into resource limits).
    if incremental:
        data_new['correct'] = data['correct-answers']
        data_new['error'] = data['wrong-answers']
        data_new['num_check_sat'] = data['num_check_sat']
        data_new['unsolved'] = data_new.num_check_sat - data_new.correct
    # Set correct/error column for solved benchmarks.
    else:
        if filter_result:
            if filter_result == RESULT_UNSAT:
                negated_filter_result = RESULT_SAT
            else:
                assert filter_result == RESULT_SAT
                negated_filter_result = RESULT_UNSAT
            # Filter benchmarks based on given verdict.  A benchmark is
            # marked as sat/unsat if its expected result is sat/unsat, or
            # its expected result is unknown and at least one solver
            # returned sat/unsat.
            data_with_result = \
                data_new[(data_new.expected == filter_result)
                         | ((data_new.result == filter_result)
                            & (data_new.expected == RESULT_UNKNOWN))]
            benchmarks = set(data_with_result.benchmark.unique())
            data_new.loc[(~data_new.benchmark.isin(benchmarks))
                         & (data_new.result != filter_result),
                         ['cpu_time', 'wallclock_time', 'result']] = \
                            [0.0, 0.0, RESULT_UNKNOWN]
            # After 2021, we count unsound results to the sat/unsat
            # score depending on the solver's result, not the benchmark
            # status. Before, it was the other way round.
            if int(year) >= 2021:
                data_new.loc[data_new.result == negated_filter_result,
                             ['cpu_time', 'wallclock_time', 'result']] = \
                                [0.0, 0.0, RESULT_UNKNOWN]
            else:
                data_new.loc[data_new.expected == negated_filter_result,
                             ['cpu_time', 'wallclock_time', 'result']] = \
                                [0.0, 0.0, RESULT_UNKNOWN]

        # Select benchmarks with results sat/unsat.
        solved = data_new[(data_new.result == RESULT_SAT)
                          | (data_new.result == RESULT_UNSAT)]
        # Select benchmarks that are within the time limit.
        solved = solved[(solved[time_column] <= wclock_limit)]

        if skip_unknowns:
            solved = solved[(solved.result == solved.expected)]
        else:
            solved = solved[(solved.expected == RESULT_UNKNOWN)
                            | (solved.result == solved.expected)]

        if unsat_core:
            data_new.loc[solved.index, 'correct'] = data['reduction']
            data_new.loc[solved.index, 'error'] = data['result-is-erroneous']
        # Note: The model validator reports INVALID if a solver crashes on an
        #       instance. Hence, only when a solver reports statisfiable, we
        #       check the status of the model validator.
        elif model_validation:
            solved = solved[solved.result == RESULT_SAT]
            solved_valid = solved[solved.model_validator_status == 'VALID']

            if int(year) <= 2019:
                solved_invalid = solved[solved.model_validator_status == 'INVALID']
            else:
                # Note: The model validator does not report a result, even if
                #       the solver produces an invalid model or the solver
                #       reports unsat.  We check for particular error messages
                #       that indicate crashes, timeouts, or sat without
                #       any model ("sat expected" or "( expected").
                #       Due to some unknown problem the jobs on fixed and
                #       best of 2019 solvers produced no entries ("-") in
                #       that column.
                incomplete_model = data_new['model_validator_exception']\
                        .str.contains("^(?:.*: \( expected|.*: sat expected|-)$")
                solved_invalid = data_new[(data_new.model_validator_status == 'INVALID')
                                          & ((data_new.model_validator_error != 'unhandled_exception')
                                             | (incomplete_model == False))]
            data_new.loc[solved_valid.index, 'correct'] = 1
            data_new.loc[solved_invalid.index, 'error'] = 1
        elif proof_exhibition:
            data_new.loc[data_new.reason == 'valid', 'correct'] = 1
            data_new.loc[data_new.reason == 'invalid', 'error'] = 1
            data_new.loc[data_new.result == 'sat', 'error'] = 1
        else:
            data_new.loc[solved.index, 'correct'] = 1

            # Get all job pairs on which solvers were wrong
            data_new.loc[(data_new.result != RESULT_UNKNOWN)
                         & (data_new.result != data_new.expected)
                         & (data_new.expected != RESULT_UNKNOWN), 'error'] = 1

            # Count number of sat/unsat
            solved_sat = solved[solved.result == RESULT_SAT]
            solved_unsat = solved[solved.result == RESULT_UNSAT]
            data_new.loc[solved_sat.index, 'correct_sat'] = 1
            data_new.loc[solved_unsat.index, 'correct_unsat'] = 1

        # Determine unsolved benchmarks.
        data_new.loc[data_new.correct == 0, 'unsolved'] = 1
        if filter_result:
            data_new.loc[~data_new.benchmark.isin(benchmarks), 'unsolved'] = 0

    # Set alpha_prime_b for each benchmark, set to 1 if family is not in the
    # 'family_scores' dictionary (use_families == False).
    data_new['alpha_prime_b'] = \
        data_new.family.map(lambda x: family_scores.get(x, 1))

    if use_families:
        data_new['score_modifier'] = \
            data_new.alpha_prime_b * data_new.division_size
    else:
        data_new['score_modifier'] = 1

    # Compute scores
    data_new['score_correct'] = data_new.correct * data_new.score_modifier
    data_new['score_error'] = data_new.error * data_new.score_modifier
    data_new['score_cpu_time'] = data_new.cpu_time * data_new.alpha_prime_b
    data_new['score_wallclock_time'] = \
        data_new.wallclock_time * data_new.alpha_prime_b

    # Delete temporary columns
    return data_new.drop(columns=['alpha_prime_b', 'score_modifier'])

# Main function.
def main():
    global g_args, g_solver_names

    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_rows', None)

    parse_args()
    read_solvers_csv()
    read_logic_to_division()

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

    data = remove_disagreements(data)

    data = score(data,
            int(g_args.time),
            None,
            2022,
            False,
            False,
            False)


    data["nb"] = 1

    data.drop(columns=["benchmark","solver","configuration_id","status","competitive","score_error","score_cpu_time","score_wallclock_time","year","correct","error","correct_sat","correct_unsat","division_size","timeout","memout","unsolved","score_correct"],inplace=True)
    # ["pair_id","solver_id","cpu_time","wallclock_time","memory_usage","result","expected","division","family"]

    data['time']=data["cpu_time"].apply(lambda x: "<=24s" if x <= 24. else ">=24s")

    data=data.groupby(by=["solver_id","division","logic","result","time"],as_index=False).sum()
    data['solver']  = data.solver_id.map(get_solver_name)
    data.drop(columns=["solver_id"],inplace=True)

    with open(g_args.out, "w") as outfile:
        data.to_csv(path_or_buf=outfile, sep=',',index=False)

    #TODO: remove disagreementor not


if __name__ == "__main__":
    main()
