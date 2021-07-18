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
pandas.set_option('precision', 16)

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
TRACK_CLOUD = "track_cloud"
TRACK_PARALLEL = "track_parallel"

# Track options
OPT_TRACK_SQ = "sq"
OPT_TRACK_INC = "inc"
OPT_TRACK_CHALL_SQ = "chall_sq"
OPT_TRACK_CHALL_INC = "chall_inc"
OPT_TRACK_UC = "uc"
OPT_TRACK_MV = "mv"
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

# Extensions of results .md files
EXT_SQ = "-single-query.md"
EXT_INC = "-incremental.md"
EXT_CHALL_SQ = "-challenge-non-incremental.md"
EXT_CHALL_INC = "-challenge-incremental.md"
EXT_UC = "-unsat-core.md"
EXT_MV = "-model-validation.md"
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
             OPT_TRACK_CLOUD: TRACK_CLOUD,
             OPT_TRACK_PARALLEL: TRACK_PARALLEL }

g_exts = { OPT_TRACK_SQ: EXT_SQ,
           OPT_TRACK_INC: EXT_INC,
           OPT_TRACK_CHALL_SQ: EXT_CHALL_SQ,
           OPT_TRACK_CHALL_INC: EXT_CHALL_INC,
           OPT_TRACK_UC: EXT_UC,
           OPT_TRACK_MV: EXT_MV,
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

# Return true if the solver with given id is competitive.
def is_competitive_solver(solver_id):
    global g_competitive
    return g_competitive[solver_id]

# Return solver name of solver with given solver id.
def get_solver_name(solver_id):
    global g_solver_names
    return g_solver_names.get(solver_id, solver_id)

# Return solver variant name of solver with given solver id.
def get_solver_variant(solver_id):
    global g_solver_variants
    name = g_solver_variants.get(solver_id, solver_id)
    if not g_competitive[solver_id]:
        return '[{}]'.format(name)
    return name

# Do not consider solver variants for determining if a division is
# competitive.
# Uses get_solver_name(solver) to get the base version of solver.
def is_competitive_division(solvers):
    return len(set([get_solver_name(x) for x in solvers])) > 1

# Compute family score modifiers.
# This is based on the presentation in the SMT-COMP 2017 rules document
# and is basically the same in all rules documents.
def get_family_scores(data):
    if data.empty:
        return {}

    raw_fam_scores = {} # The 'raw' score is alpha_b for b in the family.
    score_sum = 0       # The sum in the definition of alpha_b_prime.

    for family, fdata in data.groupby('family'):
        Fb = len(fdata.benchmark.unique())
        alpha_b = (1.0 + math.log(Fb)) / Fb
        raw_fam_scores[family] = alpha_b
        score_sum += Fb * alpha_b

    # Compute normalized weight alpha_prime_b for each benchmark family.
    family_scores = dict((family, alpha_b / score_sum)
                            for family, alpha_b in raw_fam_scores.items())

    return family_scores

# Helper to add mapping of solver id to solver name and solver variant id and
# to g_solver_names and g_solver_variants.
def map_solver_id(row, column):
    global g_competitive, g_solver_names, g_solver_variants
    if column not in row:
        return
    solver_id_str = row[column]
    solver_id = int(solver_id_str) if solver_id_str else None
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


###############################################################################
# Scoring functions
###############################################################################

# Groups the results in 'data' computed by the score function by
# - year
# - division
# - solver
# and ranks the solvers based on the given scoring scheme.
#
# data       : The data to be processed as computed by the score function.
# sequential : Compute sequential results if true, else parallel.
def group_and_rank_solvers(data, sequential):
    global g_args

    # Group results
    if 'num_check_sat' in data.columns:
      data_grouped = data.groupby(['year', 'division', 'solver_id']).agg({
          'correct': sum,
          'error': sum,
          'correct_sat' : sum,
          'correct_unsat' : sum,
          'score_correct': sum,
          'score_error': sum,
          'score_cpu_time': sum,
          'score_wallclock_time': sum,
          'timeout' : sum,
          'memout' : sum,
          'unsolved': sum,
          'competitive': 'first',
          'division_size': 'first',
          'num_check_sat': sum,
          })
    else:
      data_grouped = data.groupby(['year', 'division', 'solver_id']).agg({
          'correct': sum,
          'error': sum,
          'correct_sat' : sum,
          'correct_unsat' : sum,
          'score_correct': sum,
          'score_error': sum,
          'score_cpu_time': sum,
          'score_wallclock_time': sum,
          'timeout' : sum,
          'memout' : sum,
          'unsolved': sum,
          'competitive': 'first',
          'division_size': 'first',
          })



    # Convert solver index to column
    data_grouped.reset_index(level=2, inplace=True)

    # Sort solvers by sort_columns and sort_asc within a division
    sort_columns = ['score_error', 'score_correct']
    sort_asc = [True, False, True, True]

    if sequential:
        sort_columns.extend(['score_cpu_time', 'score_wallclock_time'])
    else:
        sort_columns.extend(['score_wallclock_time', 'score_cpu_time'])

    data_sorted = data_grouped.sort_values(by=sort_columns, ascending=sort_asc)
    data_sorted = data_sorted.sort_index(level=[0,1], sort_remaining=False)

    # Rank solvers in each division starting from rank 1. Note that competitive
    # solvers cannot get awarded a rank and merely get the current rank without
    # increasing it.
    # Note: If there are consecutive non-competitive solvers, their ranking
    #       won't be correct (since the rank won't be incremented).
    ranks = []
    seen = set()
    rank = 1
    for year_division, row in data_sorted.iterrows():
        if year_division not in seen:
            rank = 1
            seen.add(year_division)
        ranks.append(rank)
        if row.competitive:
            rank += 1
    data_sorted['rank'] = ranks

    return data_sorted


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
def score(division,
          data,
          wclock_limit,
          filter_result,
          year,
          use_families,
          skip_unknowns,
          sequential):
    global g_args
    assert not filter_result or filter_result in [RESULT_SAT, RESULT_UNSAT]

    if g_args.log: log("Score for {} in {}".format(year, division))

    num_benchmarks = len(data.benchmark.unique())
    if g_args.log: log("Computing scores for {}".format(division))
    if g_args.log: log("... with {} benchmarks".format(num_benchmarks))

    family_scores = get_family_scores(data) if use_families else {}

    # Create new dataframe with relevant columns and populate new columns
    data_new = data[['division', 'benchmark', 'family', 'solver', 'solver_id',
                     'cpu_time', 'wallclock_time', 'status', 'result',
                     'expected']].copy()
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


###############################################################################
# Processing
###############################################################################

# Process a CSV file with results of one track.
# csv          : the input csv
# year         : the string identifying the year of the results
# filter_result: - None: consider all instances
#                - RESULT_SAT: consider only satisfiable instances
#                - RESULT_UNSAT: consider only unsatisfiable instances
# use_families : use weighted scoring scheme
# skip_unknowns: skip benchmarks with status unknown
def process_csv(csv,
                year,
                time_limit,
                filter_result,
                use_families,
                skip_unknowns,
                sequential):
    global g_args
    global allLogics
    global divisionInfo
    assert not filter_result or filter_result in [RESULT_SAT, RESULT_UNSAT]
    if g_args.log:
        log("Process {} with family: '{}', divisions: '{}', "\
            "year: '{}', time_limit: '{}', "\
            "use_families: '{}', skip_unknowns: '{}', sequential: '{}', "\
            "filter_result: '{}'".format(
            csv,
            g_args.family,
            g_args.divisions,
            year,
            time_limit,
            use_families,
            skip_unknowns,
            sequential,
            filter_result))

    # Load CSV file
    start = time.time() if g_args.show_timestamps else None
    data = pandas.read_csv(csv)
    if g_args.show_timestamps:
        log('time read_csv: {}'.format(time.time() - start))

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

    start = time.time() if g_args.show_timestamps else None
    data = add_division_family_info(data, g_args.family)
    if g_args.show_timestamps:
        log('time add_division_family: {}'.format(time.time() - start))

    # Read a CSV file with the number of check-sat calls for each
    # benchmark.
    # For incremental problems, we need the number of check-sat calls per
    # benchmark in order to correctly compute the largest contribution time
    # ranking.
    if incremental and g_args.incremental:
        check_sat_info = pandas.read_csv(g_args.incremental)
        divisions = check_sat_info.benchmark.str.split('/', n=1).str[0]
        benchmarks = check_sat_info.benchmark.str.split('/', n=1).str[1]
        checks = check_sat_info.num_check_sat
        status = dict(((d, b), n)
                        for d, b, n in zip(divisions, benchmarks, checks))
        data['num_check_sat'] = \
            data[['division', 'benchmark']].apply(
                lambda x: status.get((x.division, x.benchmark), 0), axis=1)

    # -: consider all divisions
    # else list with divisions to consider
    if g_args.divisions != "-":
        divisions = g_args.divisions
        data = data[(data.division.isin(set(divisions)))]

    start = time.time() if g_args.show_timestamps else None
    data = remove_disagreements(data)
    if g_args.show_timestamps:
        log('time disagreements: {}'.format(time.time() - start))

    start = time.time() if g_args.show_timestamps else None
    # Compute the benchmark scores for each division
    dfs = []
    dfsPerLogic = {}
    for division, division_data in data.groupby('division'):
        if g_args.log: log("Compute for {}".format(division))
        res = score(division,
                    division_data,
                    time_limit,
                    filter_result,
                    year,
                    use_families,
                    skip_unknowns,
                    sequential)
        dfs.append(res)
        if g_args.divisions_map:
          dfsPerLogic[division] = res
    if g_args.divisions_map:
      # Read divisions from a JSON formatted file.
      divisionInfo = json.load(open(g_args.divisions_map))
      trackDivisions = divisionInfo[g_tracks[g_args.track]]
      for division in trackDivisions:
        divDfs = []
        nBenchmarks = 0
        logics = trackDivisions[division]
        for logic in logics:
          allLogics.add(logic)
          if logic in dfsPerLogic.keys():
            divDfs.append(dfsPerLogic[logic])
            nBenchmarks += len(dfsPerLogic[logic].benchmark.unique())
        if divDfs:
          dataNew = pandas.concat(divDfs, ignore_index=True)
          dataNew['division'] = division
          dataNew['division_size'] = nBenchmarks
          dfs.append(dataNew)
    if g_args.show_timestamps:
        log('time score: {}'.format(time.time() - start))

    return pandas.concat(dfs, ignore_index=True)

###############################################################################
# Report 2015-2018
###############################################################################

# Auxiliary function to compute results for years 2015-2018.
#
# time_limit : minimum of this limit and the limit used in the competition for
#              a year (given via command line option) is used
# sequential : compute sequential results if true, else parallel
# no_families: overule global 'use_families' setting for table in the report
#              that shows diff between competition settings vs if no family
#              benchmark weights were used in all years (not only in 2015)
# no_unknowns: same as above, overule global 'skip_unknowns' setting for table
#              in the report that shows diff between competition setting
#              (unknowns were excluded from competition in 2015-2016 and
#              included in 2017-2018) vs if they were excluded in all years.
def gen_results_for_report_aux(filter_result,
                               time_limit,
                               sequential,
                               no_families = False,
                               no_unknowns = False):
    global g_args
    dataframes = []
    dataframes.append(
            process_csv(
                g_args.csv['2015'][0],
                '2015',
                min(g_args.csv['2015'][1], time_limit),
                filter_result,
                False,
                True if no_unknowns else g_args.skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2016'][0],
                '2016',
                min(g_args.csv['2016'][1], time_limit),
                filter_result,
                False if no_families else g_args.use_families,
                True if no_unknowns else g_args.skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2017'][0],
                '2017',
                min(g_args.csv['2017'][1], time_limit),
                filter_result,
                False if no_families else g_args.use_families,
                True if no_unknowns else g_args.skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2018'][0],
                '2018',
                min(g_args.csv['2018'][1], time_limit),
                filter_result,
                False if no_families else g_args.use_families,
                True if no_unknowns else g_args.skip_unknowns,
                sequential))

    df = pandas.concat(dataframes, ignore_index=True)
    return group_and_rank_solvers(df, sequential)

# Helper function to be applied to all rows of a dataframe.
# returns: A string with sequential and parallel performance winners joined
#          as '<seq>/<par>'.
def join_winners(x):
    winners = []
    for w in x:
        if w not in winners:
            winners.append(w)
    return '/'.join(winners)

# Helper function to be applied to all rows of a dataframe for printing a
# latex results table for the report.
# returns:  A string with sequential and parallel performance winners joined
#           as '<seq> & <par>'.
def join_winners_latex(x):
    report_latex_color_map = {
            "AProVE": "apr",
            "Alt-Ergo": "alt",
            "Boolector": "bool",
            "COLIBRI": "coli",
            "CVC3": "cvc3",
            "CVC4": "cvc4",
            "Minkeyrink": "mink",
            "ProB": "prob",
            "Q3B": "q3b",
            "Redlog": "redl",
            "SMT-RAT": "rat",
            "SMTInterpol": "smti",
            "SPASS-SATT": "spass",
            "STP": "stp",
            "Vampire": "vamp",
            "Yices": "yices",
            "Z3": "z",
            "veriT": "verit",
    }
    winners = []
    for winner in x:
        # w is a string of the form:
        # <winner> [<non-competitive best if any>]
        if winner:
            w = winner.split()[0]
            assert(w[0] == '[' or w[0] == '-' or w in report_latex_color_map), \
                    "{} not in color map".format(w)
            color = report_latex_color_map[w] \
                    if w[0] != '[' and w[0] != '-' else None
            winner = "{}{}".format(
                        "\\cc{{{}}} ".format(color) if color else '', winner)
        winners.append(winner)
    # In case of a diff table, we can have either seq or par be empty but
    # we still need to distinguish this case since we want to display this
    # as ' | <par>' or '<seq> | '. Hence we sanitize and replace empty seq
    # or par with ' ' for this case and empty out winners list that only
    # contain numpy.nan (which we use in join_winners_diff for 'no diff').
    assert(len(winners) == 2)
    if winners[0] == winners[1]: winners.pop()

    # we split cell into seq/par performance if winners differ
    res = ' & '.join(winners) if len(winners) > 1  \
                              else (\
                  "\\multicolumn{{2}}"\
                  "{{>{{\\columncolor{{white}}[.5em][.5em]}}c}}{{{}}}".format(\
                          winners[0]) if len(winners) else numpy.nan)
    return res

# Helper function to be applied to all rows of a dataframe for generating a
# results diff table for the report.
# returns: A string with sequential and parallel performance winners joined
#          as '<seq>/<par>'.
def join_winners_diff(x):
    if len(x) == 2:
        x = list(x)
        winner_old = x[0]
        winner_new = x[1]
        if winner_old != winner_new:
            return winner_new
    return ''

# Get winners for a track and score for the report.
def get_winners_for_report(df):
    df['solver_name'] = df['solver_id'].map(get_solver_variant)
    df = df[(df['rank'] == 1) & (df['score_correct'] > 0)]
    # In some cases there are more than one non-competitive solvers due to how
    # non-competitive solvers are ranked. We only keep the first
    # non-competitive solver.
    df = df.reset_index()\
            .drop_duplicates(['year', 'division', 'competitive'], keep='first')\
            .sort_values(by='competitive', ascending=False)
    return df.groupby(['year', 'division'])['solver_name'].apply(' '.join)

# Generate and print results table for report:
#
# latex  : Print colored results latex table (non-competitive divisions have to
#          be marked manually from this output).
# default: Print dataframe without any decorations.
def gen_results_table_for_report(winners_seq,
                                 winners_par,
                                 latex=False,
                                 diff=False):
    # merge sequential and parallel
    df = pandas.concat([winners_seq, winners_par])
    # if diff table, drop rows with no diff (= no entries)
    df = df.reset_index()
    # join winners (winner first, best non-competing (if any) second)
    if latex:
        df = df.groupby(['year', 'division'])['solver_name'].apply(
                join_winners_latex)
    else:
        df = df.groupby(['year', 'division'])['solver_name'].apply(
                join_winners)
    df = df.unstack(level=0)
    # drop rows with no entry for a denser table that only shows the diff
    if diff:
        empty_cell = "\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{}"
        df.replace(empty_cell, numpy.nan, inplace=True)
        df.reset_index()
        df.dropna(subset=['2015', '2016', '2017', '2018'],
                  how='all',
                  inplace=True)
    # print the table
    if not latex:
        print(df.fillna(''))
    else:
        # latex tabular header string
        col_year_r = "r@{\\hskip .8em}|@{\\hskip .5em}"\
                     ">{\\columncolor{white}[.5em][.5em]}"
        col_year_l = "l>{\\columncolor{white}[.5em][.8em]}"
        col_head = "r>{\\columncolor{white}[.25em][.8em]}" + \
                "{}{}{}{}{}{}{}l".format(col_year_r, col_year_l,
                                         col_year_r, col_year_l,
                                         col_year_r, col_year_l, col_year_r)
        # we split columns into seq/par performance
        df.rename(columns={'2015':\
                '\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{2015}',
                           '2016':\
                '\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{2016}',
                           '2017':\
                '\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{2017}',
                           '2018':\
                '\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{2018}'},
                 inplace=True)

        # increase column width to avoid that pandas truncates cell content
        with pandas.option_context("max_colwidth", 1000):
            res = df.fillna(
                    '\\multicolumn{2}{>{\\columncolor{white}[.5em][.5em]}c}{}')\
                    .to_latex(
                            column_format=col_head, escape=False)\
                                    .replace('_', '\_')     \
                                    .replace('division','')
            print(res)


# Generate results diff table for report. Only contains entries that differ
# with respect to the original results.
#
# winners_seq, winners_par            : the original results
# winners_other_seq, winners_other_par: the results with respect to different
#                                       constraints (e.g., only sat, only unsat,
#                                       different time limit, ...)
def gen_results_diff_table_for_report(winners_seq,
                                       winners_par,
                                       winners_other_seq,
                                       winners_other_par,
                                       latex=False,
                                       diff=False):
    # sequential diff
    winners_diff_seq = pandas.concat([winners_seq, winners_other_seq])
    winners_diff_seq = winners_diff_seq.reset_index()
    winners_diff_seq = winners_diff_seq.groupby(
            ['year', 'division'])['solver_name'].apply(join_winners_diff)
    # parallel diff
    winners_diff_par = pandas.concat([winners_par, winners_other_par])
    winners_diff_par = winners_diff_par.reset_index()
    winners_diff_par = winners_diff_par.groupby(
            ['year', 'division'])['solver_name'].apply(join_winners_diff)
    # print
    gen_results_table_for_report(
            winners_diff_seq, winners_diff_par, latex, diff)


# Generate all results for the report.
def gen_results_for_report():
    global g_args
    print("----------------------------------------------------------------")
    print("SCORE")
    print("----------------------------------------------------------------")
    start = time.time() if g_args.show_timestamps else None
    score_seq = gen_results_for_report_aux(None, 2400, True)
    score_par = gen_results_for_report_aux(None, 2400, False)
    winners_seq = get_winners_for_report(score_seq)
    winners_par = get_winners_for_report(score_par)
    gen_results_table_for_report(winners_seq, winners_par, True)
    print("----------------------------------------------------------------")
    print("SAT SCORE")
    print("----------------------------------------------------------------")
    score_sat_seq = gen_results_for_report_aux(RESULT_SAT, 2400, True)
    score_sat_par = gen_results_for_report_aux(RESULT_SAT, 2400, False)
    winners_sat_seq = get_winners_for_report(score_sat_seq)
    winners_sat_par = get_winners_for_report(score_sat_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_sat_seq,
                                      winners_sat_par,
                                      True,
                                      True)
    print("----------------------------------------------------------------")
    print("UNSAT SCORE")
    print("----------------------------------------------------------------")
    score_unsat_seq = gen_results_for_report_aux(RESULT_UNSAT, 2400, True)
    score_unsat_par = gen_results_for_report_aux(RESULT_UNSAT, 2400, False)
    winners_unsat_seq = get_winners_for_report(score_unsat_seq)
    winners_unsat_par = get_winners_for_report(score_unsat_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_unsat_seq,
                                      winners_unsat_par,
                                      True,
                                      True)
    print("----------------------------------------------------------------")
    print("24s SCORE")
    print("----------------------------------------------------------------")
    score_24s_seq = gen_results_for_report_aux(None, 24, True)
    score_24s_par = gen_results_for_report_aux(None, 24, False)
    winners_24s_seq = get_winners_for_report(score_24s_seq)
    winners_24s_par = get_winners_for_report(score_24s_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_24s_seq,
                                      winners_24s_par,
                                      True,
                                      True)
    print("----------------------------------------------------------------")
    print("NO FAMILIES SCORE")
    print("----------------------------------------------------------------")
    score_nofam_seq = gen_results_for_report_aux(
            None, 2400, True, no_families=True)
    score_nofam_par = gen_results_for_report_aux(
            None, 2400, False, no_families=True)
    winners_nofam_seq = get_winners_for_report(score_nofam_seq)
    winners_nofam_par = get_winners_for_report(score_nofam_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_nofam_seq,
                                      winners_nofam_par,
                                      True,
                                      True)
    print("----------------------------------------------------------------")
    print("NO UNKNOWN SCORE")
    print("----------------------------------------------------------------")
    score_nounknown_seq = gen_results_for_report_aux(
            None, 2400, True, no_unknowns=True)
    score_nounknown_par = gen_results_for_report_aux(
            None, 2400, False, no_unknowns=True)
    winners_nounknown_seq = get_winners_for_report(score_nounknown_seq)
    winners_nounknown_par = get_winners_for_report(score_nounknown_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_nounknown_seq,
                                      winners_nounknown_par,
                                      True,
                                      True)
    print("----------------------------------------------------------------")
    print("FAMILIES TOP")
    print("----------------------------------------------------------------")
    g_args.family = 'top'
    score_famtop_seq = gen_results_for_report_aux(None, 2400, True)
    score_famtop_par = gen_results_for_report_aux(None, 2400, False)
    winners_famtop_seq = get_winners_for_report(score_famtop_seq)
    winners_famtop_par = get_winners_for_report(score_famtop_par)
    gen_results_diff_table_for_report(winners_seq,
                                      winners_par,
                                      winners_famtop_seq,
                                      winners_famtop_par,
                                      True,
                                      True)


###############################################################################
# Competition-Wide Recognitions
###############################################################################

####
# Biggest Lead Ranking.
####

# Computes the new global ranking based on the distance between the winner of a
# division and the second solver in a division as defined in secion 7.3.1 of
# the SMT-COMP'19 rules.
#
# data      : The dataframe as returned by process_csv.
# sequential: True if results are to be computed for sequential performance.
#
# return    : A dictionary, mapping from year to list of dicts
#             with one dict per division; a dict contains
#             {
#                 'score': <score>,                    # the biggest lead score
#                 'time': <time>,                      # the biggest lead time score
#                 'first_name': <first solver name>,   # name of first ranked solver
#                 'second_name': <second solver name>, # name of second ranked solver
#                 'division': <division>               # name of division
#             }
def biggest_lead_ranking(data, sequential):
    start = time.time() if g_args.show_timestamps else None

    data = group_and_rank_solvers(data, sequential)
    data = data[data['competitive'] == True]
    scores = dict()
    for year, ydata in data.groupby('year'):
        for division, div_data in ydata.groupby('division'):
            # Skip non-competitive divisions
            if not is_competitive_division(div_data.solver_id.unique()):
                continue
            # Skip logics if divisions != logics
            if g_args.divisions_map and division in allLogics:
              continue
            assert len(div_data) >= 2
            first = div_data[div_data['rank'] == 1]
            second = div_data[div_data['rank'] == 2]
            assert len(first) == 1
            assert len(second) == 1
            first = first.iloc[0]
            second = second.iloc[0]

            # If no solver was able to solve a single instance, there is no
            # winner for this division.
            if first.score_correct == 0:
                continue

            if sequential:
                time_first =  first.score_cpu_time
                time_second = second.score_cpu_time
            else:
                time_first =  first.score_wallclock_time
                time_second = second.score_wallclock_time

            # Compute score and time distance between first and second in the
            # division.
            # Note: The time score is only used if solvers have the same score
            # lead.
            score = ((1 + first.score_correct) / (1 + second.score_correct))
            time = (1 + time_second) / (1 + time_first)
            if year not in scores: scores[year] = []
            fields = ['score', 'time', 'first_name', 'second_name', \
                    'division']
            scores[year].append(dict(zip(fields, (score, time,
                get_solver_name(first.solver_id),
                get_solver_name(second.solver_id), division))))

        if year in scores:
            scores[year] = sorted(scores[year], \
                    key = lambda x: (x['score'], x['time']), \
                    reverse=True)

    if g_args.show_timestamps:
        log('time biggest_lead_ranking: {}'.format(time.time() - start))

    return scores


####
# Largest Contribution Ranking.
####

# Compute the correctly solved score for the virtual best solver for a given
# division if the results of 'solver' are excluded. This function corresponds
# to function vbss(D,S) as defined in section 7.3.2 of the SMT-COMP'19 rules.
#
# division_data: The data for a given division
# solver_id    : The solver to exclude
# sequential   : True if results are to be computed for sequential performance.
def vbss(division_data, solver_id, sequential):

    # Remove 'solver_id' and compute the virtual best score and cpu_time.
    data = division_data[division_data.solver_id != solver_id]

    sort_columns = ['benchmark', 'score_correct']
    sort_asc = [True, False, True]

    if sequential:
        sort_columns.append('cpu_time')
    else:
        sort_columns.append('wallclock_time')

    # Get job pair with the highest correctly solved score, which was solved
    # the fastest.
    data_vbs = data.sort_values(
                by=sort_columns, ascending=sort_asc).groupby(
                        'benchmark', as_index=False).first()
    # note that since solvers don't necessarily run on all logics in a division, these numbers may differ
    assert len(data_vbs.benchmark.unique()) == len(division_data.benchmark.unique()) or g_args.divisions_map

    if sequential:
        return (data_vbs.score_correct.sum(), data_vbs.cpu_time.sum())
    return (data_vbs.score_correct.sum(), data_vbs.wallclock_time.sum())


# Largest Contribution Ranking.
#
# Compute the largest contribution to the virtual best solver as defined in
# section 7.3.2 of the SMT-COMP'19 rules.
#
# data:       The dataframe as returned by process_csv.
# time_limit: The time limit, cpu time if sequential, wallclock if not.
# sequential: True if results are to be computed for sequential performance.
#
# return: A dictionary, mapping from year to list of tuples with one tuple per
#         division; a tuple contains
#         {
#             'score': <score>,                  # the largest contribution score
#             'time': <time>,                    # the largest contribution time score
#             'n_solvers': <n_solvers>,          # the number of solvers in the division
#             'division_size': <division_size>,  # the number of benchmarks in the division
#             'first_name': <solver_name>,       # the solver name
#             'division': <division>             # name of division
#         }
def largest_contribution_ranking(data, time_limit, sequential):
    start = time.time() if g_args.show_timestamps else None

    # Set cpu_time/wallclock_time to 'time_limit' if solvers were not able to
    # solve the instance. This ensures that if no solver is able to solve the
    # instance, vbss(D,S) picks 'time_limit' seconds. This corresponds to the
    # min({}) = 2400 seconds in the SMT-COMP'19 rules.
    # Note: For incremental problems we set the cpu_time/wallclock_time to
    # 'time_limit' if not all check-sat calls were answered.
    if 'num_check_sat' in data.columns:
        timeout = data[data.correct < data.num_check_sat]
    else:
        timeout = data[data.correct == 0]
    data.loc[timeout.index,
             ['cpu_time', 'wallclock_time']] = [time_limit, time_limit]

    # Only consider competitive solvers.
    data = data[data.competitive == True]

    weighted_scores = dict()
    for year, ydata in data.groupby('year'):
        num_job_pairs_total = 0
        scores_top = []
        for division, div_data in data.groupby('division'):
            # Skip logics if divisions != logics
            if g_args.divisions_map and division in allLogics:
              continue

            solvers_total = div_data.solver_id.unique()

            # Filter out unsound solvers.
            data_error = div_data[div_data.error > 0]
            solvers_sound = solvers_total
            if len(data_error) > 0:
                solvers_error = set(data_error.solver_id.unique())
                # Filter out job pairs of unsound solvers.
                div_data = div_data[~div_data.solver_id.isin(solvers_error)]
                solvers_sound = div_data.solver_id.unique()

            # Skip divisions with less than 3 competitive solvers.
            if len(solvers_sound) < 3:
                continue

            # Note: For normalization we consider the original number of job pairs,
            #       including unsound solvers.
            division_size = div_data.division_size.iloc[0]
            num_job_pairs_total += division_size * len(solvers_total)

            # Compute the scores for the virtual best solver
            vbs_score_correct, vbs_time = vbss(div_data, '', sequential)

            # If no solver was able to solve a single instance, there is no
            # winner for this division.
            if vbs_score_correct == 0:
                continue

            # Compute the correct_score and cpu_time/wallclock_time impact of
            # removing a solver from the virtual best solver.
            scores_div = []
            for solver in solvers_sound:
                cur_score_correct, cur_time = vbss(div_data, solver, sequential)
                assert cur_score_correct <= vbs_score_correct
                #assert cur_time >= vbs_time

                impact_score = 1 - cur_score_correct / vbs_score_correct
                impact_time = 1 - vbs_time / cur_time

                scores_div.append((impact_score,
                                   impact_time,
                                   len(solvers_total),
                                   division_size,
                                   get_solver_name(solver),
                                   division))

            scores_div_sorted = sorted(scores_div, reverse=True)
            # Pick the solver with the highest impact
            scores_top.append(scores_div_sorted[0])

        # Normalize scores based on division job pairs/total job pairs as defined
        # in section 7.3.2 of the SMT-COMP'19 rules.
        for tup in scores_top:
            impact_score, impact_time, n_solvers, n_benchmarks = tup[:4]
            weight = n_solvers * n_benchmarks / num_job_pairs_total
            w_score, w_time = impact_score * weight, impact_time * weight
            if year not in weighted_scores: weighted_scores[year] = []
            fields = ['score', 'time', 'n_solvers', 'division_size',
                    'first_name', 'division']
            weighted_scores[year].append(dict(zip(fields,\
                (w_score, w_time, n_solvers, n_benchmarks, tup[4],\
                    tup[5]))))
        if year in weighted_scores:
            weighted_scores[year] = sorted(weighted_scores[year], \
                    key = lambda x: (x['score'], x['time']), reverse=True)

    if g_args.show_timestamps:
        log('time largest_contribution_ranking: {}'.format(time.time() - start))

    return weighted_scores


###############################################################################
# Generate competition results and .md files for website
###############################################################################

# Get winner for division and score for results .md files.
# df: The dataframe containing all data for a division and score.
def md_get_div_winner(df):
    if not df[(df.competitive == True) & (df['rank'] == 1)].empty:
        winner = df[(df.competitive == True) & (df['rank'] == 1)].iloc[0]
        # If the first ranked solver has a score of 0, there are no winners for
        # this division.
        if winner.score_correct > 0:
            return get_solver_name(winner.solver_id)
    return '\"-\"'

# Get division score details for results .md files.
#
# df          : The dataframe containing all data for a division and score.
# track       : A string identifying the track, use one of the variables
#                 - TRACK_SQ
#                 - TRACK_INC
#                 - TRACK_CHALL_SQ
#                 - TRACK_CHALL_INC
#                 - TRACK_UC
#                 - TRACK_MV
#                 - TRACK_CLOUD
#                 - TRACK_PARALLEL
# str_score   : A string identifiying the kind of score to be computed.
# n_benchmarks: The number of benchmarks in this division.
def md_get_div_score_details(df, track, str_score, n_benchmarks):
    lines = ["{}:".format(str_score)]
    for index, row in df.iterrows():
        lines.append("- name: {}".format(
            get_solver_name(row.solver_id)))
        lines.append("  competing: {}".format(
            '\"yes\"' if is_competitive_solver(row.solver_id) else '\"no\"'))
        lines.append("  errorScore: {}".format(
            row.score_error))
        lines.append("  correctScore: {}".format(
            row.score_correct))
        if track not in (OPT_TRACK_CLOUD, OPT_TRACK_PARALLEL):
            lines.append("  CPUScore: {}".format(
                round(row.score_cpu_time, 3)))
        lines.append("  WallScore: {}".format(
            round(row.score_wallclock_time, 3)))
        if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ or \
                track == OPT_TRACK_CLOUD or track == OPT_TRACK_PARALLEL:
            lines.append("  solved: {}".format(
                row.correct))
            lines.append("  solved_sat: {}".format(
                row.correct_sat))
            lines.append("  solved_unsat: {}".format(
                row.correct_unsat))
        if track != OPT_TRACK_UC and track != OPT_TRACK_MV:
            lines.append("  unsolved: {}".format(
                row.unsolved))
            if g_args.divisions_map:
              if track == OPT_TRACK_INC:
                lines.append("  abstained: {}".format(
                  row.num_check_sat - (row.correct + row.unsolved)))
              else:
                lines.append("  abstained: {}".format(
                  n_benchmarks - (row.correct + row.unsolved)))
        lines.append("  timeout: {}".format(
            row.timeout))
        lines.append("  memout: {}".format(
            row.memout))
    return '\n'.join(lines)


# Write .md file for a division in a track.
#
# division    : A string identifying the division.
# n_benchmarks: The number of benchmarks in this division.
# data_seq    : The data set for the sequential score.
# data_par    : The data set for the parallel score.
# data_sat    : The data set for the sat score.
# data_unsat  : The data set for the unsat score.
# data_24s    : The data set for the 24s score.
# year        : A string identifying the year of the competition.
# path        : The path of the directory to write the .md file.
# time_limit  : The time_limit limit.
def md_write_file(division,
                  n_benchmarks,
                  data_seq, data_par, data_sat, data_unsat, data_24s,
                  year,
                  path,
                  track,
                  usedLogics,
                  time_limit):
    global g_tracks, g_exts
    # general info about the current division
    str_div = \
            "---\n"\
            "layout: result\n"\
            "resultdate: {}\n\n"\
            "year: {}\n\n"\
            "divisions: divisions_{}\n"\
            "participants: participants_{}\n\n"\
            "disagreements: disagreements_{}\n"\
            "division: {}\n"\
            "track: {}\n"\
            "n_benchmarks: {}\n"\
            "time_limit: {}\n"\
            "mem_limit: {}\n"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    year,
                    year,
                    year,
                    year,
                    division,
                    g_tracks[track],
                    n_benchmarks,
                    time_limit,
                    "60" if track != OPT_TRACK_CLOUD and track != OPT_TRACK_PARALLEL else "N/A"
                    )
    # for each logic in division, see if there was any

    # if division != logic and this is a true division, add logics
    if g_args.divisions_map and not division in allLogics:
      assert usedLogics
      allLogicsStr = ""
      # sort by logic
      usedlogics = sorted(usedLogics.items(), key = lambda x: x[0])
      first = True
      for logic, nBench in usedLogics.items():
        allLogicsStr += "\n" + ("- " if first else "  ")
        first = False
        allLogicsStr += "%s: %s" % (logic, nBench)
      str_div += "logics:%s\n" % allLogicsStr

    # winners
    str_winners = ["winner_par: {}".format(md_get_div_winner(data_par))]
    # division scores
    str_div_scores = \
        [ md_get_div_score_details(data_par, track, 'parallel', n_benchmarks) ]

    if not data_seq.empty:
        str_winners.insert(
                0, "winner_seq: {}".format(md_get_div_winner(data_seq)))
        str_div_scores.insert(
                0, md_get_div_score_details(
                    data_seq, track, 'sequential', n_benchmarks))

    if not data_sat.empty:
        str_winners.append(
                "winner_sat: {}".format(md_get_div_winner(data_sat)))
        str_div_scores.append(
                md_get_div_score_details(
                    data_sat, track, 'sat', n_benchmarks))

    if not data_unsat.empty:
        str_winners.append("winner_unsat: {}".format(
                md_get_div_winner(data_unsat)))
        str_div_scores.append(
                md_get_div_score_details(
                    data_unsat, track, 'unsat', n_benchmarks))

    if not data_24s.empty:
        str_winners.append(
                "winner_24s: {}\n".format(md_get_div_winner(data_24s)))
        str_div_scores.append(
                md_get_div_score_details(
                    data_24s, track, 'twentyfour', n_benchmarks))

    str_winners = "\n".join(str_winners)
    str_div_scores = "\n".join(str_div_scores)

    # write md file
    file_path = os.path.join(path, "{}{}".format(division, g_exts[track]))
    with open(file_path, "w") as outfile:
        outfile.write(
                "\n".join([str_div, str_winners, str_div_scores, '---\n']))


# Generate results .md files for each division in a track.
#
# results_seq  : The data set for the sequential score.
# results_par  : The data set for the parallel score.
# results_sat  : The data set for the sat score.
# results_unsat: The data set for the unsat score.
# results_24s  : The data set for the 24s score.
# path         : The path of the directory to write the .md files.
# time         : The time limit.
def to_md_files(results_seq,
                results_par,
                results_sat,
                results_unsat,
                results_24s,
                path,
                track,
                time):

    if not os.path.exists(path):
        os.mkdir(path)

    # level=[0,1]: group results by year and division
    results = (
               results_seq.groupby(level=[0,1]),
               results_par.groupby(level=[0,1]),
               results_sat.groupby(level=[0,1]),
               results_unsat.groupby(level=[0,1]),
               results_24s.groupby(level=[0,1]),
              )
    # iterate over divisions in track
    # (results are zipped together for iteration)
    empty = pandas.DataFrame()

    for data_seq, data_par, data_sat, data_unsat, data_24s in zip(*results):
        # assert that results are complete and correctly zipped togeher, i.e.,
        # year and division of individual results must match
        assert data_seq[0] == data_par[0] == data_sat[0]
        assert data_sat[0] == data_unsat[0] == data_24s[0]
        year, division = data_seq[0]
        # the actual results data of the current division
        data_seq = data_seq[1]
        data_par = data_par[1]
        data_sat = data_sat[1]
        data_unsat = data_unsat[1]
        data_24s = data_24s[1]
        # total number of benchmarks in the current division
        n_benchmarks = data_seq.iloc[0].division_size
        # track string
        track_str = ""
        ext_str = ".md"
        usedLogics = {}
        if g_args.divisions_map and not division in allLogics:
          tmpDf = results_seq.reset_index()
          divLogics = divisionInfo[g_tracks[track]][division]
          for logic in divLogics:
            logicDf = tmpDf[tmpDf['division'] == logic]
            if len(logicDf) > 0:
             usedLogics[logic] = logicDf['division_size'].iloc[0]
        if track == OPT_TRACK_SQ:
            md_write_file(division,
                          n_benchmarks,
                          data_seq, data_par, data_sat, data_unsat, data_24s,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_INC:
            md_write_file(division,
                          n_benchmarks,
                          empty, data_par, empty, empty, empty,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_UC:
            md_write_file(division,
                          n_benchmarks,
                          data_seq, data_par, empty, empty, empty,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_MV:
            md_write_file(division,
                          n_benchmarks,
                          data_seq, data_par, empty, empty, empty,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_CHALL_SQ:
            md_write_file(division,
                          n_benchmarks,
                          data_seq, data_par, data_sat, data_unsat, data_24s,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_CHALL_INC:
            md_write_file(division,
                          n_benchmarks,
                          empty, data_par, empty, empty, empty,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_CLOUD:
            md_write_file(division,
                          n_benchmarks,
                          empty, data_par, data_sat, data_unsat, data_24s,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)
        elif track == OPT_TRACK_PARALLEL:
            md_write_file(division,
                          n_benchmarks,
                          empty, data_par, data_sat, data_unsat, data_24s,
                          year,
                          path,
                          track,
                          usedLogics,
                          time)

# Get score details for competition-wide biggest lead recognition .md file
# for a division and score.
# bl: The dataframe containing all biggest lead data for a division and score.
def md_comp_get_div_biggest_lead(bl, expdivs = []):
    str_bl = []
    for div_bl in bl:

        str_bl.append("- name: {}\n"\
                      "  second: {}\n"\
                      "  correctScore: {:.8f}\n"\
                      "  timeScore: {:.8f}\n"\
                      "  division: {}\n"\
                      "  experimental: {}".format( \
                      div_bl['first_name'], div_bl['second_name'], \
                      div_bl['score'], div_bl['time'], \
                      div_bl['division'], \
                      ((div_bl['division'] in expdivs) and "true") or "false"))
    return "\n".join(str_bl)

# Get the name of the highest-scoring solver from competition-wide
# recognitions data, ignoring the experimental divisions scores.  If
# there is no winner, return the special name \"-\"
# comp_data: The data for a competition-wide recognition. Maps 'year' to a list
#            of tuples with the actual recognition data.
# year: The year of interest
# exp_division: a list of experimental division names

def md_comp_get_nonexperimental_winner(comp_data, year, exp_divisions):
    if year not in comp_data:
        return '"-"'
    if not comp_data[year]:
        return '"-"'

    non_experimentals = list(\
            filter(lambda x: x['division'] not in exp_divisions,\
                comp_data[year]))

    if len(non_experimentals) > 0:
        return non_experimentals[0]['first_name']
    else:
        return '"-"'

# Generate results .md file for competition-wide biggest lead contribution for
# a track.
#
# results_seq  : The data set for the sequential score.
# results_par  : The data set for the parallel score.
# results_sat  : The data set for the sat score.
# results_unsat: The data set for the unsat score.
# results_24s  : The data set for the 24s score.
# path         : The path of the directory to write the .md files.
# time_limit   : The time limit.
# track        : A string identifying the track, use one of the variables
#                  - TRACK_SQ
#                  - TRACK_INC
#                  - TRACK_CHALL_SQ
#                  - TRACK_CHALL_INC
#                  - TRACK_UC
#                  - TRACK_MV
def to_md_files_comp_biggest_lead(results_seq,
                                  results_par,
                                  results_sat,
                                  results_unsat,
                                  results_24s,
                                  path,
                                  time_limit,
                                  track,
                                  expdivs):
    global g_tracks, g_exts, g_args

    bl_seq = biggest_lead_ranking(results_seq, True)
    bl_par = biggest_lead_ranking(results_par, False)
    bl_sat = biggest_lead_ranking(results_sat, False)
    bl_unsat = biggest_lead_ranking(results_unsat, False)
    bl_24s = biggest_lead_ranking(results_24s, False)

    for year in bl_seq:
        str_bl = []
        str_comp = []

        str_comp.append( "---\n"\
                         "layout: result_comp\n"\
                         "resultdate: {}\n\n"\
                         "year: {}\n\n"\
                         "results: results_{}\n"\
                         "participants: participants_{}\n\n"\
                         "track: {}\n"\
                         "recognition: biggest_lead\n"\
                         .format(datetime.datetime.now().strftime(
                                     "%Y-%m-%d %H:%M:%S"),
                                 year,
                                 year,
                                 year,
                                 g_tracks[track]))

        winner_par_str = \
                md_comp_get_nonexperimental_winner(bl_par, \
                year, expdivs)

        str_comp.append("winner_par: {}".format(winner_par_str))

        str_bl.append("{}{}".format(
            "parallel:\n",
            md_comp_get_div_biggest_lead(bl_par.get(year, ''), expdivs)))

        if track != OPT_TRACK_INC and track != OPT_TRACK_CHALL_INC and \
                track != OPT_TRACK_CLOUD and track != OPT_TRACK_PARALLEL:
            winner_seq_str = \
                    md_comp_get_nonexperimental_winner(bl_seq, \
                    year, expdivs)

            str_comp.insert(1, "winner_seq: {}".format(
                        winner_seq_str))
            str_bl.insert (0, "{}{}".format("sequential:\n",
                md_comp_get_div_biggest_lead(bl_seq.get(year, ''),
                    expdivs)))

        if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ:

            winner_sat = md_comp_get_nonexperimental_winner(bl_sat, \
                    year, expdivs)
            winner_unsat = md_comp_get_nonexperimental_winner(bl_unsat, \
                    year, expdivs)
            winner_24s = md_comp_get_nonexperimental_winner(bl_24s, \
                    year, expdivs)

            str_comp.append("winner_sat: {}\n"\
                            "winner_unsat: {}\n"\
                            "winner_24s: {}"\
                            .format(winner_sat, winner_unsat,
                                winner_24s))

            str_bl.append("{}{}".format(
                "sat:\n",
                md_comp_get_div_biggest_lead(bl_sat.get(year, ''),
                    expdivs)))
            str_bl.append("{}{}".format(
                "unsat:\n",
                md_comp_get_div_biggest_lead(bl_unsat.get(year, ''),
                    expdivs)))
            str_bl.append("{}{}".format(
                "twentyfour:\n",
                md_comp_get_div_biggest_lead(bl_24s.get(year, ''),
                    expdivs)))

        str_comp = "\n".join(str_comp)
        str_bl = "\n".join(str_bl)
        # write md file
        file_path = os.path.join(path, "biggest-lead{}".format(g_exts[track]))
        with open(file_path, "w") as outfile:
            outfile.write("\n".join([str_comp, str_bl, '---\n']))

# Get score details for competition-wide largest contribution recognition
# .md file for a division and score.
# lc: The dataframe containing all largest contribution data for a division
#     and score.
def md_comp_get_div_largest_contribution(lc, expdivs = []):
    str_lc = []
    for div_lc in lc:
        str_lc.append("- name: {}\n"\
                      "  correctScore: {:.8f}\n"\
                      "  timeScore: {:.8f}\n"\
                      "  division: {}\n"\
                      "  experimental: {}".format(\
                      div_lc['first_name'], div_lc['score'],\
                      div_lc['time'], div_lc['division'], \
                      ((div_lc['division'] in expdivs) and "true") or "false"))
    return "\n".join(str_lc)

# Generate results .md file for competition-wide largest contribution for
# a track.
#
# results_seq  : The data set for the sequential score.
# results_par  : The data set for the parallel score.
# results_sat  : The data set for the sat score.
# results_unsat: The data set for the unsat score.
# results_24s  : The data set for the 24s score.
# path         : The path of the directory to write the .md files.
# time_limit   : The time limit.
# track        : A string identifying the track, use one of the variables
#                  - TRACK_SQ
#                  - TRACK_INC
#                  - TRACK_CHALL_SQ
#                  - TRACK_CHALL_INC
#                  - TRACK_UC
#                  - TRACK_MV
def to_md_files_comp_largest_contribution(results_seq,
                                          results_par,
                                          results_sat,
                                          results_unsat,
                                          results_24s,
                                          path,
                                          time_limit,
                                          track,
                                          expdivs):
    global g_tracks, g_exts, g_args

    lc_seq = largest_contribution_ranking(results_seq, time_limit, True)
    lc_par = largest_contribution_ranking(results_par, time_limit, False)
    lc_sat = largest_contribution_ranking(results_sat, time_limit, False)
    lc_unsat = largest_contribution_ranking(results_unsat, time_limit, False)
    lc_24s = largest_contribution_ranking(results_24s, time_limit, False)

    for year in lc_seq:
        str_comp = []
        str_lc = []

        str_comp.append("---\n"\
                        "layout: result_comp\n"\
                        "resultdate: {}\n\n"\
                        "year: {}\n\n"\
                        "results: results_{}\n"\
                        "participants: participants_{}\n\n"\
                        "track: {}\n"\
                        "recognition: largest_contribution\n"\
                        .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                                year,
                                year,
                                year,
                                g_tracks[track]))

        par_winner_str = \
                md_comp_get_nonexperimental_winner(lc_par, year, expdivs)

        str_comp.append("winner_par: {}\n".format(par_winner_str))

        str_lc.append("{}{}".format(
                "parallel:\n",
                md_comp_get_div_largest_contribution(\
                        lc_par.get(year, ''), expdivs)))

        if track != OPT_TRACK_INC and track != OPT_TRACK_CHALL_INC and \
                track != OPT_TRACK_CLOUD and track != OPT_TRACK_PARALLEL:

            seq_winner_str = \
                    md_comp_get_nonexperimental_winner(lc_seq, \
                    year, expdivs)

            str_comp.insert(
                1, "winner_seq: {}\n".format(seq_winner_str))

            str_lc.insert(0, "{}{}".format(
                    "sequential:\n", \
                    md_comp_get_div_largest_contribution(\
                    lc_seq.get(year, ''), expdivs)))

        if track in (OPT_TRACK_SQ, OPT_TRACK_CHALL_SQ, OPT_TRACK_CLOUD,
                OPT_TRACK_PARALLEL):
            winner_sat_str = \
                    md_comp_get_nonexperimental_winner(lc_sat, \
                    year, expdivs)
            winner_unsat_str = \
                    md_comp_get_nonexperimental_winner(lc_unsat, \
                    year, expdivs)
            winner_24s_str = \
                    md_comp_get_nonexperimental_winner(lc_24s, \
                    year, expdivs)

            str_comp.append("winner_sat: {}\n"\
                            "winner_unsat: {}\n"\
                            "winner_24s: {}\n"\
                            .format(winner_sat_str, winner_unsat_str,
                                winner_24s_str))

            str_lc.append("{}{}".format(
                "sat:\n", md_comp_get_div_largest_contribution(lc_sat.get(year, ''))))
            str_lc.append("{}{}".format(
                "unsat:\n", md_comp_get_div_largest_contribution(lc_unsat.get(year, ''))))
            str_lc.append("{}{}".format(
                "twentyfour:\n", md_comp_get_div_largest_contribution(lc_24s.get(year, ''))))

        str_comp = "\n".join(str_comp)
        str_lc = "\n".join(str_lc)
        # write md file
        file_path = os.path.join(
            path, "largest-contribution{}".format(g_exts[track]))
        with open(file_path, "w") as outfile:
            outfile.write("\n".join([str_comp, str_lc, '---\n']))


# Generate results .md file for competition-wide overview for a track.
#
# year         : The year of the competition
# path         : The path of the directory to write the .md files.
# track        : A string identifying the track, use one of the variables
#                  - TRACK_SQ
#                  - TRACK_INC
#                  - TRACK_CHALL_SQ
#                  - TRACK_CHALL_INC
#                  - TRACK_UC
#                  - TRACK_MV
def to_md_files_comp_summary(year, path, track):
    global g_tracks, g_exts, g_args
    scores = []
    if track != OPT_TRACK_INC and track != OPT_TRACK_CHALL_INC and \
            track != OPT_TRACK_CLOUD and track != OPT_TRACK_PARALLEL:
        scores.append("sequential")
    scores.append("parallel")
    if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ or \
            track == OPT_TRACK_CLOUD or track == OPT_TRACK_PARALLEL:
        scores.append("sat")
        scores.append("unsat")
        scores.append("twentyfour")

    str_results = ("---\n"\
                   "layout: results_summary\n"\
                   "track: {track}\n"\
                   "scores: {scores}\n"\
                   "year: {year}\n"\
                   "results: results_{year}\n"\
                   "divisions: divisions_{year}\n"\
                   "participants: participants_{year}\n"\
                   "disagreements: disagreements_{year}\n"\
                   "---\n"
                   .format(year=year,
                           scores=",".join(scores),
                           track=g_tracks[track]))

    # write md file
    file_path = os.path.join(path, "results{}".format(g_exts[track]))
    with open(file_path, "w") as outfile:
        outfile.write(str_results)


# Generate all results .md files for the competition website.
#
# csv       : The input csv with the competition results.
# time_limit: The time limit.
# year      : A string identifying the year of the competition.
# path      : The path of the directory to write the .md file.
def gen_results_md_files(csv, time_limit, year, path, path_comp):
    global g_args
    results_seq = process_csv(csv,
                              year,
                              time_limit,
                              None,
                              g_args.use_families,
                              g_args.skip_unknowns,
                              True)
    results_par = process_csv(csv,
                              year,
                              time_limit,
                              None,
                              g_args.use_families,
                              g_args.skip_unknowns,
                              False)
    results_sat = process_csv(csv,
                              year,
                              time_limit,
                              RESULT_SAT,
                              g_args.use_families,
                              g_args.skip_unknowns,
                              False)
    results_unsat = process_csv(csv,
                                year,
                                time_limit,
                                RESULT_UNSAT,
                                g_args.use_families,
                                g_args.skip_unknowns,
                                False)
    results_24s = process_csv(csv,
                              year,
                              24,
                              None,
                              g_args.use_families,
                              g_args.skip_unknowns,
                              False)
    results_seq_grouped = group_and_rank_solvers(results_seq, True)
    results_par_grouped = group_and_rank_solvers(results_par, False)
    results_sat_grouped = group_and_rank_solvers(results_sat, False)
    results_unsat_grouped = group_and_rank_solvers(results_unsat, False)
    results_24s_grouped = group_and_rank_solvers(results_24s, False)
    to_md_files(results_seq_grouped,
                results_par_grouped,
                results_sat_grouped,
                results_unsat_grouped,
                results_24s_grouped,
                path,
                g_args.track,
                time_limit)
    to_md_files_comp_biggest_lead(results_seq,
                                  results_par,
                                  results_sat,
                                  results_unsat,
                                  results_24s,
                                  path_comp,
                                  time_limit,
                                  g_args.track,
                                  g_args.experimental_divisions)
    to_md_files_comp_largest_contribution(results_seq,
                                          results_par,
                                          results_sat,
                                          results_unsat,
                                          results_24s,
                                          path_comp,
                                          time_limit,
                                          g_args.track,
                                          g_args.experimental_divisions)
    to_md_files_comp_summary(year,
                             path_comp,
                             g_args.track)


###############################################################################
# Main
###############################################################################

# Parse command line arguments.
def parse_args():
    global g_args

    parser = ArgumentParser()

    parser.add_argument("-f", "--family-choice",
                        action="store",
                        dest="family",
                        default="bot",
                        help="Choose notion of benchmark family"\
                              "('top' for top-most directory, "\
                              "'bot' for bottom-most directory)")
    parser.add_argument("-d", "--division-only",
                        metavar="division[,division...]",
                        action="store",
                        dest="divisions",
                        default="-",
                        help="Restrict attention to a single division")
    parser.add_argument("-s", "--sequential",
                        action="store_true",
                        dest="sequential",
                        default=False,
                        help="Compute sequential scores")
    parser.add_argument("-w", "--weighted",
                        action="store_true",
                        dest="use_families",
                        default=False,
                        help="Use weighted scoring scheme")
    parser.add_argument("-u", "--skip-unknowns",
                        action="store_true",
                        dest="skip_unknowns",
                        default=False,
                        help="Skip benchmarks with unknown status")
    parser.add_argument("--show-timestamps",
                        action="store_true",
                        default=False,
                        help="Log time for computation steps")
    parser.add_argument("-l", "--log",
                        action="store_true",
                        default=False,
                        help="Enable logging")
    parser.add_argument('-i', '--incremental',
                        type=str,
                        help='CSV containing incremental status information')
    parser.add_argument("-b", "--bestof",
                        type=str,
                        default="",
                        help="list the best competing solvers, per division, of given year, in a csv with year/division/name")

    parser.add_argument("-D", "--divisions-map",
                        metavar="json",
                        default=None,
                        help="Divisions per track. To be used when divisions != logics")


    required = parser.add_argument_group("required arguments")
    required.add_argument("-c", "--csv",
                        metavar="path[,path...]",
                        required=True,
                        help="list of input csvs with results from StarExec")
    required.add_argument("-y", "--year",
                        metavar="year[,year...]",
                        required=True,
                        help="list of years matching given input csvs")
    required.add_argument("-t", "--time",
                        metavar="time[,time...]",
                        required=True,
                        help="list of time limits matching given input csvs")
    required.add_argument("-S", "--solvers",
                          metavar="csv",
                          required=True,
                          help="csv file that maps solver ID to solver name "\
                               "and solver variant "\
                               "and identifies if a solver is competitive")

    report = parser.add_argument_group(
            "generate results for 2015-2018 competition report")
    report.add_argument("--report",
                        action="store_true",
                        default=False,
                        help="produce results for JSat 2015-2018 submission")

    gen_md = parser.add_argument_group(
            "generate competition results and write results .md files")
    gen_md.add_argument("--gen-md",
                        metavar="dir[,dir]",
                        action="store",
                        default=None,
                        help="generate competition results and .md files for "\
                             "results webpage for given track into "\
                             "given directories (first directory for division"\
                             "results, second for competition-wide results)")
    gen_md.add_argument("-T", "--track",
                        default=None,
                        choices=[OPT_TRACK_SQ, OPT_TRACK_INC, OPT_TRACK_UC,
                                 OPT_TRACK_MV, OPT_TRACK_CHALL_SQ,
                                 OPT_TRACK_CHALL_INC, OPT_TRACK_CLOUD,
                                 OPT_TRACK_PARALLEL],
                        help="A string identifying the competition track")
    gen_md.add_argument("--expdivs",
                        metavar="expdiv[,expdiv...]",
                        default=None,
                        help="List the experimental divisions in "\
                                "the selected track")

    g_args = parser.parse_args()

    if g_args.gen_md:
        if not g_args.track:
            die("Missing track information")
        g_args.gen_md = g_args.gen_md.split(',')
        if len(g_args.gen_md) > 2:
            die("Too many path arguments, expected two")
        if len(g_args.gen_md) == 1:
            g_args.gen_md.append(g_args.gen_md[0])
        if not os.path.exists(g_args.gen_md[0]):
            os.mkdir(g_args.gen_md[0])
        if not os.path.exists(g_args.gen_md[1]):
            os.mkdir(g_args.gen_md[1])

        g_args.experimental_divisions = set(\
            g_args.expdivs.split(',') if \
            g_args.expdivs else [])

    g_args.csv = g_args.csv.split(',') if g_args.csv else []
    g_args.year = g_args.year.split(',') if g_args.year else []
    g_args.time = g_args.time.split(',') if g_args.time else []
    g_args.time = [int(t) for t in g_args.time]

    if len(g_args.year) != len(g_args.csv):
        die ("Number of given years and csv files does not match.")
    if len(g_args.time) != len(g_args.csv):
        die ("Number of given time limits and csv files does not match.")

    if g_args.report:
        assert '2015' in g_args.year
        assert '2016' in g_args.year
        assert '2017' in g_args.year
        assert '2018' in g_args.year

    tmp = zip (g_args.csv, g_args.time)
    g_args.csv = dict(zip(g_args.year, tmp))

    if g_args.divisions != "-":
        g_args.divisions = g_args.divisions.split(',')


# Main function.
def main():
    global g_args

    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_rows', None)

    parse_args()
    read_solvers_csv()

    if g_args.report:
        for year in g_args.csv:
            csv = g_args.csv[year][0]
            if not os.path.exists(csv):
                die("Given csv does not exist: {}".format(csv))
        gen_results_for_report()
    elif g_args.gen_md:
        for year in g_args.csv:
            csv, time_limit = g_args.csv[year]
            gen_results_md_files(
                    csv, time_limit, year, g_args.gen_md[0], g_args.gen_md[1])
    else:
        data = []
        for year in g_args.csv:
            csv, time_limit = g_args.csv[year]
            if not os.path.exists(csv):
                die("Given csv does not exist: {}".format(csv))
            df = process_csv(csv,
                             year,
                             time_limit,
                             None,
                             g_args.use_families,
                             g_args.skip_unknowns,
                             g_args.sequential)
            data.append(df)
            grouped = group_and_rank_solvers(df, g_args.sequential)
            grouped['name'] = grouped.solver_id.map(get_solver_name)
            bl = biggest_lead_ranking(df, g_args.sequential)
            lc = largest_contribution_ranking(df, time_limit, g_args.sequential)
            print(grouped)
            print(bl)
            print(lc)

            if (g_args.bestof != ""):
              # get winner *including non-competitive*
              winners = grouped[\
                          (grouped["rank"] == 1) &\
                          (grouped["score_correct"] > 0) &\
                          (grouped["score_error"] == 0)
                        ]
              winners = winners.reset_index()\
                .drop_duplicates(["year", "division"], keep="first")


              winners[["year", "division", "name","solver_id"]]\
                      .to_csv(path_or_buf = g_args.bestof, \
                              columns = ["division", "name","solver_id"], \
                              index = False)

        result = pandas.concat(data, ignore_index = True)

if __name__ == "__main__":
    main()
