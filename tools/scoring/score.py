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

# Track options
OPT_TRACK_SQ = "sq"
OPT_TRACK_INC = "inc"
OPT_TRACK_CHALL_SQ = "chall_sq"
OPT_TRACK_CHALL_INC = "chall_inc"
OPT_TRACK_UC = "uc"
OPT_TRACK_MV = "mv"

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

g_args = None

g_competitive = {}
g_solver_names = {}

g_tracks = { OPT_TRACK_SQ: TRACK_SQ,
             OPT_TRACK_INC: TRACK_INC,
             OPT_TRACK_CHALL_SQ: TRACK_CHALL_SQ,
             OPT_TRACK_CHALL_INC: TRACK_CHALL_INC,
             OPT_TRACK_UC: TRACK_UC,
             OPT_TRACK_MV: TRACK_MV }

g_exts = { OPT_TRACK_SQ: EXT_SQ,
           OPT_TRACK_INC: EXT_INC,
           OPT_TRACK_CHALL_SQ: EXT_CHALL_SQ,
           OPT_TRACK_CHALL_INC: EXT_CHALL_INC,
           OPT_TRACK_UC: EXT_UC,
           OPT_TRACK_MV: EXT_MV }

###############################################################################
# Helper functions

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def log(string):
    print("[score] {}".format(string))

def split_benchmark_division_family(x, family_func):
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

# adds columns for division and family to data
# also does some tidying of benchmark column for specific years of the competition
# edit this function if you want to edit how families are added
def add_division_family_info(data, family_definition):

    # Select family extraction functions.
    # This depends on the family_definition option:
    #   - 'top' interprets the top-most directory, and
    #   - 'bot' interprets the bottom-most directory as benchmark family.
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

    # Group by benchmarks and count the number of results.
    grouped_results = solved_unknown.groupby('benchmark', as_index=False).agg(
                            {'result': 'count'})

    # If the number of results is more than one, we have disagreeing solvers, 
    # i.e., the result column contains 'sat' and 'unsat' for the corresponding
    # benchmark.
    disagreements = grouped_results[grouped_results['result'] > 1]

    exclude = set(disagreements.benchmark)

    if g_args.log:
        log('Found {} disagreements:'.format(len(exclude)))
        i = 1
        for b in exclude:
            log('[{}] {}'.format(i, b))
            i += 1

    # Exclude benchmarks on which solvers disagree.
    data = data[~(data.benchmark.isin(exclude))]
    return data

# Return true if the solver with given id is competitive.
def is_competitive_solver(solver_id):
    global g_competitive
    return g_competitive[solver_id]

# Return solver name of solver with given solver id.
def get_solver_name(solver_id):
    global g_solver_names
    return g_solver_names.get(solver_id, solver_id)

# compute family scores
# this is based on the presentation in the SMT-COMP 2017 rules document
# but this is basically the same in all rules documents
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

# Selects the winners (e.g. rank 0) from the results for a division and year
# Returns these as a list (there may be more than one)
# TODO: needs to be refactored with new dataframe layout
#def select(results, division, year):
#    return results[(results.year == year)
#                   & (results.division == division)].groupby(
#                        ['year', 'division']).first()['solver'].tolist()

# The same as select but turns the winners into a pretty string
# TODO: needs to be refactored with new dataframe layout
#def select_str(results, division, year):
#  winners = select_winners(results[(results.year == year)
#                                   & (results.division == division)])
#  winners_strs = sorted(map(lambda s: get_solver_name(s) if is_competitive_solver(year,s) else "["+get_solver_name(s)+"]", winners))
#  return " ".join(winners_strs)


# TODO: needs to be refactored with new solvers input file layout
# Checks the winners recorded in new_results against an existing winners.csv file
# This was used to validate this script against previous results computed by
# other scripts
#def check_winners(new_results, year, sequential):
#    global g_args
#    assert year in ('2015', '2016', '2017', '2018')
#
#    # First load the previous files from a winners file, which should be a CSV
#    winners_old = pandas.read_csv("winners.csv")
#
#    # Select sequential winners only
#    if sequential:
#        for year in g_args.year:
#            winners_old[year] = winners_old[year].str.split('/').str[0]
#    # Select parallel winners only
#    else:
#        for year in g_args.year:
#            winners_old[year] = winners_old[year].str.split('/').str[-1]
#
#    old = winners_old[['Division', year]].set_index(['Division'])
#    old.columns = ['solver_old']
#
#    # Get all division winners from year 'year'.
#    new = new_results.xs(year)
#    new = new[new['rank'] == 1][['solver']]
#    new['solver'] = new['solver'].map(get_solver_name)
#    new = new.groupby(level=0).agg({'solver': lambda x: ' '.join(
#                sorted(x, key=lambda x: (is_competitive_solver(x, year), x)))})
#
#    merged = new.merge(old, left_index=True, right_index=True, how='outer')
#    diff = merged[(merged.solver.notna() | merged.solver_old.notna())
#                  & (merged.solver != merged.solver_old)]
#
#    if len(diff) > 0:
#        print('Found difference in old and new results {}:'.format(year))
#        print(diff[['solver_old', 'solver']])

# Turns a set of results into a LaTeX table that lists winners/best solvers
# per division as listed in the report for 2015-2018.
# TODO: needs to be refactored with new dataframe layout
#def to_latex_for_report(results):
#     print("\begin{tabular}{"\
#           "r@{\hskip 1em}>{\columncolor{white}[.25em][.5em]}"\
#           "c@{\hskip 1em}>{\columncolor{white}[.5em][.5em]}"\
#           "c@{\hskip 1em}>{\columncolor{white}[.5em][.5em]}"\
#           "c@{\hskip 1em}>{\columncolor{white}[.5em][0.5em]}c}")
#     print("\\toprule")
#     print("Division & 2015 & 2016 & 2017 & 2018 \\\\")
#     print("\\hline\\hline")
#
#     divisions = results.division.unique()
#     for division in divisions:
#       print("\\wc {} & {} & {} & {} & {} \\\\".format(
#           division,
#           select_str(results, division, "2015"),
#           select_str(results, division, "2016"),
#           select_str(results, division, "2017"),
#           select_str(results, division, "2018")))
#     print("\\bottomrule")
#     print("\\end{tabular}")

def map_solver_id(row, column):
    global g_competitive, g_solver_names
    if column not in row:
        return
    solver_id = int(row[column]) if not pandas.isnull(row[column]) else None
    if solver_id:
        g_competitive[solver_id] = row[COL_COMPETING] == 'yes'
        g_solver_names[solver_id] = row[COL_SOLVER_NAME]

def read_solvers_csv():
    global g_args, g_solver_names, g_competitive
    data = pandas.read_csv(g_args.solvers)
    for index, row in data.iterrows():
        assert not pandas.isnull(row[COL_SOLVER_ID])
        map_solver_id(row, COL_SOLVER_ID)
        map_solver_id(row, COL_SOLVER_ID_SQ_2019)
        map_solver_id(row, COL_SOLVER_ID_INC_2019)
        map_solver_id(row, COL_SOLVER_ID_UC_2019)
        map_solver_id(row, COL_SOLVER_ID_MV_2019)


###############################################################################
# Scoring functions

def group_and_rank_solver(data, sequential):
    global g_args

    # Group results
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

    # Note: For incremental tracks we have to consider all benchmarks (also
    #       the ones that run into resource limits).
    if incremental:
        data_new['correct'] = data['correct-answers']
        data_new['error'] = data['wrong-answers']
        data_new['num_check_sat'] = data['num_check_sat']
        data_new['unsolved'] = data_new.num_check_sat - data_new.correct
    # Set correct/error column for solved benchmarks.
    else:
        # Filter job pairs based on given verdict. For the sat/unsat scoring
        # only satisfiable/unsatisfiable instances are considered, i.e., if
        # either the expected status is sat/unsat or a solver solves the
        # instance.
        if filter_result:
            expected = set([filter_result, RESULT_UNKNOWN])
            data_with_result = \
                data_new[(data_new.expected == filter_result)
                         | ((data_new.result == filter_result)
                            & (data_new.expected.isin(expected)))]
            benchmarks = set(data_with_result.benchmark.unique())
            #data_new = data_new[data_new.benchmark.isin(benchmarks)]
            data_new.loc[~data_new.benchmark.isin(benchmarks),
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
            solved_invalid = solved[solved.model_validator_status == 'INVALID']
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
            g_args.use_families,
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
    if g_args.show_timestamps:
        log('time score: {}'.format(time.time() - start))

    return pandas.concat(dfs, ignore_index=True)

###############################################################################
# Report 2015-2018

# Use the names in the file name_lookups.csv to rename the names of solvers
# This is used to print nice output. If you want to change how a solver
# appears in output you should update name_lookups.csv
def report_rename_solvers(data):
    data.solver = data.solver.map(get_solver_name)
    return data

# TODO: needs to be refactored with new solvers input file layout
#def report_read_competitive():
#    global g_non_competitive
#    with open('noncompetitive.csv', mode='r') as f:
#        reader = csv.reader(f)
#        for rows in reader:
#            year = rows[0]
#            solver = rows[1]
#
#            if year not in g_non_competitive:
#                g_non_competitive[year] = set()
#            g_non_competitive[year].add(solver)

# TODO: needs to be refactored with new solvers input file layout
#def report_read_solver_names():
#    global g_solver_names
#    with open('name_lookup.csv', mode='r') as f:
#      reader = csv.reader(f)
#      g_solver_names = dict((r[0], r[1]) for r in reader)

# Finds the difference between two sets of results, allows us to compare two
# scoring mechanisms.l This was useful when preparing the SMT-COMP journal
# paper and for discussing how scoring rules could be changed.
def report_project(normal,other):
    normal = report_rename_solvers(normal)
    other = report_rename_solvers(other)
    different = pandas.concat(
            [normal,other],
            keys=['normal','other']).drop_duplicates(
                    keep=False,
                    subset=['solver','rank'])
    if different.empty:
        return different
    other_different = different.loc['other']
    return other_different


# This function runs with specific values for certain years but keeps some
# options open to allow us to try diferent things
def gen_results_for_report_aux(
        filter_result, time_limit, bytotal, skip_unknowns, sequential):
    global g_args
    dataframes = []
    dataframes.append(
            process_csv(
                g_args.csv['2015'][0],
                '2015',
                min(g_args.csv['2015'][1], time_limit),
                filter_result,
                False,
                skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2016'][0],
                '2016',
                min(g_args.csv['2016'][1], time_limit),
                filter_result,
                not bytotal,
                skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2017'][0],
                '2017',
                min(g_args.csv['2017'][1], time_limit),
                filter_result,
                not bytotal,
                skip_unknowns,
                sequential))
    dataframes.append(
            process_csv(
                g_args.csv['2018'][0],
                '2018',
                min(g_args.csv['2018'][1], time_limit),
                filter_result,
                not bytotal,
                skip_unknowns,
                sequential))

    df = pandas.concat(dataframes, ignore_index=True)
    return group_and_rank_solver(df, sequential)


def gen_results_for_report():
    global g_args

    report_read_competitive()
    report_read_solver_names()

    print("PARALLEL")
    start = time.time() if g_args.show_timestamps else None
    normal = gen_results_for_report_aux(
                None, 2400, False, False, g_args.sequential)
    check_all_winners(normal, False)
    grouped_normal = group_and_rank_solver(normal, g_args.sequential)
    #to_latex_for_report(normal)
    #vbs_winners(normal)
    #biggest_lead_ranking(normal,"a_normal")
    if g_args.show_timestamps:
        log('time parallel: {}'.format(time.time() - start))

    print("UNSAT")
    start = time.time() if g_args.show_timestamps else None
    unsat = gen_results_for_report_aux(
            RESULT_UNSAT, 2400, False, False, g_args.sequential)
    #biggest_lead_ranking(unsat,"b_unsat")
    grouped_unsat = group_and_rank_solver(unsat, g_args.sequential)
    unsat_new = report_project(select_winners(grouped_normal),
                               select_winners(grouped_unsat))
    #to_latex_for_report(unsat_new)
    #vbs_select_winners(unsat)
    if g_args.show_timestamps:
        log('time unsat: {}'.format(time.time() - start))

    print("SAT")
    start = time.time() if g_args.show_timestamps else None
    sat = gen_results_for_report_aux(
            RESULT_SAT, 2400, False, False, g_args.sequential)
    grouped_sat = group_and_rank_solver(sat, g_args.sequential)
    #biggest_lead_ranking(sat,"c_sat")
    sat_new = report_project(select_winners(grouped_normal),
                             select_winners(grouped_sat))
    #to_latex_for_report(sat_new)
    #vbs_select_winners(sat)
    if g_args.show_timestamps:
        log('time sat: {}'.format(time.time() - start))

    print("24s")
    start = time.time() if g_args.show_timestamps else None
    twenty_four = gen_results_for_report_aux(
                    None, 24, False, False, g_args.sequential)
    grouped_twenty_four = group_and_rank_solver(twenty_four, g_args.sequential)
    #biggest_lead_ranking(twenty_four,"d_24")
    twenty_four_new = report_project(select_winners(grouped_normal),
                                     select_winners(grouped_twenty_four))
    #to_latex_for_report(twenty_four_new)
    #vbs_select_winners(twenty_four)
    if g_args.show_timestamps:
        log('time 24s: {}'.format(time.time() - start))

    #print("Total Solved")
    #by_total_scored  = gen_results_for_report_aux(
    #        None, 2400, True, False, g_args.sequential)
    #biggest_lead_ranking(by_total_scored,"e_total")
    #by_total_scored_new = report_project(select_winners(normal),select_winners(by_total_scored))
    #to_latex_for_report(by_total_scored_new)

    #print("Without unknowns")
    #without_unknowns  = gen_results_for_report_aux(
    #         None, 2400, False, True, g_args.sequential)
    #without_unknowns_new = report_project(select_winners(normal),select_winners(without_unknowns))
    #to_latex_for_report(without_unknowns_new)

# Checks winners for a fixed number of years
def check_all_winners(results, sequential):
    global g_args

    print("Check differences")
    for year in g_args.year:
        print(year)
        check_winners(results, year, sequential)

# Select winners from given years and divisions.
def select_winners(data):
  top = data.copy()
  #res =  top[(data.Rank==0) & (data.competitive==True)]
  res =  top[(data['rank'] == 1)]
  return res

# Do not consider solver variants for determining if a division is
# competitive.
# Uses get_solver_name(solver) to get the base version of solver.
def is_competitive_division(solvers):
    return len(set([get_solver_name(x) for x in solvers])) > 1

# Biggest Lead Ranking.
#
# Computes the new global ranking based on the distance between the winner of a
# division and the second solver in a division as defined in secion 7.3.1 of
# the SMT-COMP'19 rules.
#
# Note: The function prints a list of sorted tuples starting with the first
#       place (winner).
#
def biggest_lead_ranking(data, sequential):
    start = time.time() if g_args.show_timestamps else None

    data = group_and_rank_solver(data, sequential)
    data = data[data['competitive'] == True]
    scores = dict()
    for year, ydata in data.groupby('year'):
        scores[year] = []
        for division, div_data in ydata.groupby('division'):
            # Skip non-competitive divisions
            if not is_competitive_division(div_data.solver_id.unique()):
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
            scores[year].append((score,
                           time,
                           get_solver_name(first.solver_id),
                           get_solver_name(second.solver_id),
                           division))
        scores[year] = sorted(scores[year], reverse=True)

#        scores_sorted = sorted(scores[year], reverse=True)
#        print('{} Biggest Lead Ranking'.format(year) +
#              '(Score, 1st Solver, 2nd Solver, Division)')
#        for s in scores_sorted:
#            print(s)

    if g_args.show_timestamps:
        log('time biggest_lead_ranking: {}'.format(time.time() - start))

    return scores


# Largest Contribution Ranking.
#
# Compute the correctly solved score for the virtual best solver for a given
# division if the results of 'solver' are excluded. This function corresponds
# to function vbss(D,S) as defined in section 7.3.2 of the SMT-COMP'19 rules.
#
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
    assert len(data_vbs.benchmark.unique()) == len(division_data.benchmark.unique())

    if sequential:
        return (data_vbs.score_correct.sum(), data_vbs.cpu_time.sum())
    return (data_vbs.score_correct.sum(), data_vbs.wallclock_time.sum())


# Largest Contribution Ranking.
#
# Compute the largest contribution to the virtual best solver as defined in
# section 7.3.2 of the SMT-COMP'19 rules.
#
# Note: The function prints the list of division winners sorted by the computed
#       largest contribution score.
#
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
        weighted_scores[year] = []
        for tup in scores_top:
            impact_score, impact_time, n_solvers, n_benchmarks = tup[:4]
            weight = n_solvers * n_benchmarks / num_job_pairs_total
            w_score, w_time = impact_score * weight, impact_time * weight
            weighted_scores[year].append(
                (w_score, w_time, n_solvers, n_benchmarks, tup[4], tup[5]))
        weighted_scores[year] = sorted(weighted_scores[year], reverse=True)
        #print('Largest Contribution Ranking')
        #for s in sorted(weighted_scores[year], reverse=True):
        #    print(s)

    if g_args.show_timestamps:
        log('time largest_contribution_ranking: {}'.format(time.time() - start))

    return weighted_scores


###############################################################################
# Generate competition results and .md files for website

def md_get_winner(df):
    winner = df[(df.competitive == True) & (df['rank'] == 1)].iloc[0]
    # If the first ranked solver has a score of 0, there are no winners for
    # this division.
    if winner.score_correct == 0:
        return ''
    return get_solver_name(winner.solver_id)

def md_table_details(df, track, scoring, n_benchmarks):
    lines = ["{}:".format(scoring)]
    for index, row in df.iterrows():
        lines.append("- name: {}".format(
            get_solver_name(row.solver_id)))
        lines.append("  competing: {}".format(
            '\"yes\"' if is_competitive_solver(row.solver_id) else '\"no\"'))
        lines.append("  errorScore: {}".format(
            row.score_error))
        lines.append("  correctScore: {}".format(
            row.score_correct))
        lines.append("  CPUScore: {}".format(
            round(row.score_cpu_time, 3)))
        lines.append("  WallScore: {}".format(
            round(row.score_wallclock_time, 3)))
        if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ:
            lines.append("  solved: {}".format(
                row.correct))
            lines.append("  solved_sat: {}".format(
                row.correct_sat))
            lines.append("  solved_unsat: {}".format(
                row.correct_unsat))
        if track != OPT_TRACK_UC:
            lines.append("  unsolved: {}".format(
                row.unsolved))
        lines.append("  timeout: {}".format(
            row.timeout))
        lines.append("  memout: {}".format(
            row.memout))
    return '\n'.join(lines)

def write_md_file_sq(division,
                     n_benchmarks,
                     data_seq, data_par, data_sat, data_unsat, data_24s,
                     year,
                     path,
                     track,
                     time):
    global g_tracks, g_exts
    # general info about the current division
    str_div = \
            "---\n"\
            "layout: result\n"\
            "resultdate: {}\n"\
            "division: {}\n"\
            "track: {}\n"\
            "n_benchmarks: {}\n"\
            "time_limit: {}\n"\
            "\n"\
            "winner_seq: {}\n"\
            "winner_par: {}\n"\
            "winner_sat: {}\n"\
            "winner_unsat: {}\n"\
            "winner_24s: {}\n"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    division,
                    g_tracks[track],
                    n_benchmarks,
                    time,
                    md_get_winner(data_seq),
                    md_get_winner(data_par),
                    md_get_winner(data_sat),
                    md_get_winner(data_unsat),
                    md_get_winner(data_24s))
    # division scores
    str_seq   = md_table_details(data_seq, track, 'sequential', n_benchmarks)
    str_par   = md_table_details(data_par, track, 'parallel', n_benchmarks)
    str_sat   = md_table_details(data_sat, track, 'sat', n_benchmarks)
    str_unsat = md_table_details(data_unsat, track, 'unsat', n_benchmarks)
    str_24s   = md_table_details(data_24s, track, 'twentyfour', n_benchmarks)
    # write md file
    year_path = os.path.join(path, year)
    if not os.path.exists(year_path): os.mkdir(year_path)
    track_path = os.path.join(year_path, track)
    if not os.path.exists(track_path): os.mkdir(track_path)
    outfile = open(
            os.path.join(track_path, "{}{}".format(
                division, g_exts[track])), "w")
    outfile.write("\n".join([
        str_div, str_seq, str_par, str_sat, str_unsat, str_24s, '---\n']))

def write_md_file_inc(division,
                      n_benchmarks,
                      data_par,
                      year,
                      path,
                      track,
                      time):
    global g_tracks, g_exts
    # general info about the current division
    str_div = \
            "---\n"\
            "layout: result_inc\n"\
            "resultdate: {}\n"\
            "division: {}\n"\
            "track: {}\n"\
            "n_benchmarks: {}\n"\
            "time_limit: {}\n"\
            "\n"\
            "winner_par: {}\n"\
            .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    division,
                    g_tracks[track],
                    n_benchmarks,
                    time,
                    md_get_winner(data_par))
    # division scores
    str_par = md_table_details(data_par, track, 'parallel', n_benchmarks)
    # write md file
    year_path = os.path.join(path, year)
    if not os.path.exists(year_path): os.mkdir(year_path)
    track_path = os.path.join(year_path, track)
    if not os.path.exists(track_path): os.mkdir(track_path)
    outfile = open(
            os.path.join(track_path, "{}{}".format(
                division, g_exts[track])), "w")
    outfile.write("\n".join([str_div, str_par, '---\n']))


def write_md_file_others(division,
                         n_benchmarks,
                         data_seq, data_par,
                         year,
                         path,
                         track,
                         time,
                         is_experimental=False):
    global g_tracks, g_exts
    # general info about the current division
    str_div = \
            "---\n"\
            "layout: result_{}\n"\
            "resultdate: {}\n"\
            "division: {}\n"\
            "track: {}\n"\
            "n_benchmarks: {}\n"\
            "time_limit: {}\n"\
            "\n"\
            "winner_seq: {}\n"\
            "winner_par: {}\n"\
            .format('exp' if is_experimental else 'others',
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    division,
                    g_tracks[track],
                    n_benchmarks,
                    time,
                    md_get_winner(data_seq),
                    md_get_winner(data_par))
    # division scores
    str_seq   = md_table_details(data_seq, track, 'sequential', n_benchmarks)
    str_par   = md_table_details(data_par, track, 'parallel', n_benchmarks)
    # write md file
    year_path = os.path.join(path, year)
    if not os.path.exists(year_path): os.mkdir(year_path)
    track_path = os.path.join(year_path, track)
    if not os.path.exists(track_path): os.mkdir(track_path)
    outfile = open(
            os.path.join(track_path, "{}{}".format(
                division, g_exts[track])), "w")
    outfile.write("\n".join([str_div, str_seq, str_par, '---\n']))


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
        if track == OPT_TRACK_SQ:
            write_md_file_sq(division,
                             n_benchmarks,
                             data_seq, data_par, data_sat, data_unsat, data_24s,
                             year,
                             path,
                             track,
                             time)
        elif track == OPT_TRACK_INC:
            write_md_file_inc(division,
                              n_benchmarks,
                              data_par,
                              year,
                              path,
                              track,
                              time)
        elif track == OPT_TRACK_UC:
            write_md_file_others(division,
                             n_benchmarks,
                             data_seq, data_par,
                             year,
                             path,
                             track,
                             time)
        elif track == OPT_TRACK_MV:
            write_md_file_others(division,
                                 n_benchmarks,
                                 data_seq, data_par,
                                 year,
                                 path,
                                 track,
                                 time,
                                 OPT_TRACK_MV in g_args.exp_tracks)
        elif track == OPT_TRACK_CHALL_SQ:
            write_md_file_sq(division,
                             n_benchmarks,
                             data_seq, data_par, data_sat, data_unsat, data_24s,
                             year,
                             path,
                             track,
                             time)
        elif track == OPT_TRACK_CHALL_INC:
            write_md_file_inc(division,
                              n_benchmarks,
                              data_par,
                              year,
                              path,
                              track,
                              time)

def md_file_comp_bl(bl):
    str_bl = []
    for div_bl in bl:
        str_bl.append("- name: {}\n"\
                      "  second: {}\n"\
                      "  correctScore: {:.8f}\n"\
                      "  timeScore: {:.8f}\n"\
                      "  division: {}".format(
                      div_bl[2], div_bl[3], div_bl[0], div_bl[1], div_bl[4]))
    return "\n".join(str_bl)

def to_md_files_comp_biggest_lead(results_seq,
                                  results_par,
                                  results_sat,
                                  results_unsat,
                                  results_24s,
                                  path,
                                  time_limit,
                                  track):
    global g_tracks, g_exts, g_args

    bl_seq = biggest_lead_ranking(results_seq, True)
    bl_par = biggest_lead_ranking(results_par, False)
    bl_sat = biggest_lead_ranking(results_sat, False)
    bl_unsat = biggest_lead_ranking(results_unsat, False)
    bl_24s = biggest_lead_ranking(results_24s, False)

    for year in bl_seq:
        assert year in bl_par
        assert year in bl_sat
        assert year in bl_unsat
        assert year in bl_24s
        if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: biggest_lead\n"\
                    "\n"\
                    "winner_seq: {}\n"\
                    "winner_par: {}\n"\
                    "winner_sat: {}\n"\
                    "winner_unsat: {}\n"\
                    "winner_24s: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            bl_seq[year][0][2],
                            bl_par[year][0][2],
                            bl_sat[year][0][2],
                            bl_unsat[year][0][2],
                            bl_24s[year][0][2])
        elif track == OPT_TRACK_INC or track == OPT_TRACK_CHALL_INC:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: biggest_lead\n"\
                    "\n"\
                    "winner_par: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            bl_par[year][0][2])
        else:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: biggest_lead\n"\
                    "\n"\
                    "winner_seq: {}\n"\
                    "winner_par: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            bl_seq[year][0][2],
                            bl_par[year][0][2])

        str_bl = []
        str_bl.append("{}{}".format(
            "sequential:\n", md_file_comp_bl(bl_seq[year])))
        str_bl.append("{}{}".format(
            "parallel:\n", md_file_comp_bl(bl_par[year])))
        str_bl.append("{}{}".format(
            "sat:\n", md_file_comp_bl(bl_sat[year])))
        str_bl.append("{}{}".format(
            "unsat:\n", md_file_comp_bl(bl_unsat[year])))
        str_bl.append("{}{}".format(
            "twentyfour:\n", md_file_comp_bl(bl_24s[year])))
        str_bl = "\n".join(str_bl)
        # write md file
        year_path = os.path.join(path, year)
        if not os.path.exists(year_path): os.mkdir(year_path)
        track_path = os.path.join(year_path, track)
        if not os.path.exists(track_path): os.mkdir(track_path)
        outfile = open(os.path.join(
            track_path, "biggest-lead{}".format(g_exts[track])), "w")
        outfile.write("\n".join([str_comp, str_bl, '---\n']))


def md_file_comp_lc(lc):
    str_lc = []
    for div_lc in lc:
        str_lc.append("- name: {}\n"\
                      "  correctScore: {:.8f}\n"\
                      "  timeScore: {:.8f}\n"\
                      "  division: {}".format(
                      div_lc[4], div_lc[0], div_lc[1], div_lc[5]))
    return "\n".join(str_lc)

def to_md_files_comp_largest_contribution(results_seq,
                                          results_par,
                                          results_sat,
                                          results_unsat,
                                          results_24s,
                                          path,
                                          time_limit,
                                          track):
    global g_tracks, g_exts, g_args

    lc_seq = largest_contribution_ranking(results_seq, time_limit, True)
    lc_par = largest_contribution_ranking(results_par, time_limit, False)
    lc_sat = largest_contribution_ranking(results_sat, time_limit, False)
    lc_unsat = largest_contribution_ranking(results_unsat, time_limit, False)
    lc_24s = largest_contribution_ranking(results_24s, time_limit, False)

    for year in lc_seq:
        assert year in lc_par
        assert year in lc_sat
        assert year in lc_unsat
        assert year in lc_24s
        if track == OPT_TRACK_SQ or track == OPT_TRACK_CHALL_SQ:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: largest_contribution\n"\
                    "\n"\
                    "winner_seq: {}\n"\
                    "winner_par: {}\n"\
                    "winner_sat: {}\n"\
                    "winner_unsat: {}\n"\
                    "winner_24s: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            lc_seq[year][0][4],
                            lc_par[year][0][4],
                            lc_sat[year][0][4],
                            lc_unsat[year][0][4],
                            lc_24s[year][0][4])
        elif track == OPT_TRACK_INC or track == OPT_TRACK_CHALL_INC:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: largest_contribution\n"\
                    "\n"\
                    "winner_par: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            lc_par[year][0][4])
        else:
            str_comp = \
                    "---\n"\
                    "layout: result_comp\n"\
                    "resultdate: {}\n"\
                    "track: {}\n"\
                    "recognition: largest_contribution\n"\
                    "\n"\
                    "winner_seq: {}\n"\
                    "winner_par: {}\n"\
                    "\n"\
                    .format(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"),
                            g_tracks[track],
                            lc_seq[year][0][4],
                            lc_par[year][0][4])

        str_lc = []
        str_lc.append("{}{}".format(
            "sequential:\n", md_file_comp_lc(lc_seq[year])))
        str_lc.append("{}{}".format(
            "parallel:\n", md_file_comp_lc(lc_par[year])))
        str_lc.append("{}{}".format(
            "sat:\n", md_file_comp_lc(lc_sat[year])))
        str_lc.append("{}{}".format(
            "unsat:\n", md_file_comp_lc(lc_unsat[year])))
        str_lc.append("{}{}".format(
            "twentyfour:\n", md_file_comp_lc(lc_24s[year])))
        str_lc = "\n".join(str_lc)
        # write md file
        year_path = os.path.join(path, year)
        if not os.path.exists(year_path): os.mkdir(year_path)
        track_path = os.path.join(year_path, track)
        if not os.path.exists(track_path): os.mkdir(track_path)
        outfile = open(os.path.join(
            track_path, "largest-contribution{}".format(g_exts[track])), "w")
        outfile.write("\n".join([str_comp, str_lc, '---\n']))


def gen_results_md_files(csv, time_limit, year, path):
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
    results_seq_grouped = group_and_rank_solver(results_seq, True)
    results_par_grouped = group_and_rank_solver(results_par, False)
    results_sat_grouped = group_and_rank_solver(results_sat, False)
    results_unsat_grouped = group_and_rank_solver(results_unsat, False)
    results_24s_grouped = group_and_rank_solver(results_24s, False)
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
                                  path,
                                  time_limit,
                                  g_args.track)
    to_md_files_comp_largest_contribution(results_seq,
                                          results_par,
                                          results_sat,
                                          results_unsat,
                                          results_24s,
                                          path,
                                          time_limit,
                                          g_args.track)



###############################################################################
# Main

def parse_args():
    global g_args

    parser = ArgumentParser()

    parser.add_argument("-f", "--family-choice",
                        action="store",
                        dest="family",
                        default="bot",
                        help="Choose notion of benchmark family"\
                              "('top' for top-most directory, "\
                              "'bot' for bottom-most directory")
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
                        metavar="directory",
                        action="store",
                        default=None,
                        help="generate competition results and .md files for "\
                             "results webpage for given track into "\
                             "given directory")
    gen_md.add_argument("-T", "--track",
                        default=None,
                        choices=[OPT_TRACK_SQ, OPT_TRACK_INC, OPT_TRACK_UC,
                                 OPT_TRACK_MV, OPT_TRACK_CHALL_SQ,
                                 OPT_TRACK_CHALL_INC],
                        help="A string identifying the competition track")
    gen_md.add_argument("--exp-tracks",
                        metavar="track[,track...]",
                        action="store",
                        help="list with experimental tracks "\
                             "(see -T for track names)")

    g_args = parser.parse_args()

    if g_args.gen_md and not g_args.track:
        die ("Missing track information")

    g_args.csv = g_args.csv.split(',') if g_args.csv else []
    g_args.year = g_args.year.split(',') if g_args.year else []
    g_args.time = g_args.time.split(',') if g_args.time else []
    g_args.time = [int(t) for t in g_args.time]

    g_args.exp_tracks = g_args.exp_tracks.split(',') \
            if g_args.exp_tracks else []

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


def main():
    global g_args
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
            gen_results_md_files(csv, time_limit, year, g_args.gen_md)
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
            print(group_and_rank_solver(df, g_args.sequential))
            biggest_lead_ranking(df, g_args.sequential)
            largest_contribution_ranking(df, time_limit, g_args.sequential)
#            # Sanity check for previous years
#            if year in ('2015', '2016', '2017', '2018'):
#                check_winners(
#                        group_and_rank_solver(df, g_args.sequential),
#                        year, g_args.sequential)

        result = pandas.concat(data, ignore_index = True)


if __name__ == "__main__":
    main()

