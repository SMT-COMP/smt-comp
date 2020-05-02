#!/usr/bin/env python3

import argparse
import csv
import random
import re

#==============================================================================
# Selection parameters
#==============================================================================

# Set time limit for interesting benchmarks. The default here is 1 second.
TIME_LIMIT = 1
# Set the minimum for number of asserts in unsat core track
NUM_ASSERTS = 2

# The rules give the following rules for the number of selected benchmarks
# (a) If a logic contains < 300 instances, all instances will be selected
# (b) If a logic contains between 300 and 600, a subset of 300 will be selected
# (c) If a logic contains > 600 then 40% will be selected
# The following three variables represent the parameters in these rules so that
# they can be modified if needed
NUM_LOWER = 300
NUM_UPPER = 600
PERCENT = 0.4

#==============================================================================

COL_BENCHMARK = 'benchmark'
COL_SOLVER = 'solver'
COL_CONFIG = 'configuration'
COL_CPU = 'cpu time'
COL_STATUS = 'status'
COL_RESULT = 'result'
COL_EXPECTED = 'expected'
COL_ASSERTS = 'number of asserts'

#==============================================================================
LOGICS = set([
        'ABVFP', 'ALIA', 'AUFBVDTLIA', 'AUFDTLIA', 'AUFLIA', 'AUFLIRA',
        'AUFNIA', 'AUFNIRA', 'BV', 'BVFP', 'FP', 'LIA', 'LRA', 'NIA',
        'NRA', 'QF_ABV', 'QF_ABVFP', 'QF_ALIA', 'QF_ANIA', 'QF_AUFBV',
        'QF_AUFLIA', 'QF_AUFNIA', 'QF_AX', 'QF_BV', 'QF_BVFP',
        'QF_BVFPLRA', 'QF_DT', 'QF_FP', 'QF_FPLRA', 'QF_IDL', 'QF_LIA',
        'QF_LIRA', 'QF_LRA', 'QF_NIA', 'QF_NIRA', 'QF_NRA', 'QF_RDL',
        'QF_S', 'QF_SLIA', 'QF_UF', 'QF_UFBV', 'QF_UFIDL', 'QF_UFLIA',
        'QF_UFLRA', 'QF_UFNIA', 'QF_UFNRA', 'UF', 'UFBV', 'UFDT',
        'UFDTLIA', 'UFDTNIA', 'UFIDL', 'UFLIA', 'UFLRA', 'UFNIA', 'ABV',
        'ABVFPLRA', 'AUFDTLIRA', 'AUFDTNIRA', 'AUFFPDTLIRA', 'BVFPLRA',
        'FPLRA', 'QF_ABVFPLRA', 'QF_UFFP', 'UFDTLIRA', 'UFDTNIRA',
        'UFFPDTLIRA', 'UFFPDTNIRA'
        ])
#==============================================================================

# Get the benchmark name from a raw string.  The benchmarks may be
# prepended with a path.  The actual name is assumed to start with the
# first occurrence of a known logic name.
def get_benchmark_name(raw_str):
    raw_split = raw_str.strip().split('/')
    while (len(raw_split) > 0 and raw_split[0] not in LOGICS):
        raw_split.pop(0)
    return "/".join(raw_split)

def split_benchmark_to_logic_family(benchmark):
    benchmark_split = benchmark.split("/")
    logic = benchmark_split[0]
    family = '/'.join(benchmark_split[:-1])
    benchmark = '/'.join(benchmark_split)
    return (logic, family, benchmark)

def read_benchmarks(file_name):
    # Maps benchmarks to corresponding logic and family.
    # benchmarks[logic][family] = set(benchmarks...)
    benchmarks = {}
    num_families = 0
    num_benchmarks = 0
    with open(file_name, 'r') as infile:
        for benchmark in infile.readlines():
            benchmark_name = get_benchmark_name(benchmark.strip())
            (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark_name)
            if logic == "":
                print(benchmark)
                assert(False)
            if not logic in benchmarks:
                benchmarks[logic] = {}
            if not family in benchmarks[logic]:
                benchmarks[logic][family] = set()
                num_families += 1
            benchmarks[logic][family].add(benchmark)
            num_benchmarks += 1
    return benchmarks, num_families, num_benchmarks

def read_data_unsat(file_name):
    # Map logics to a dict mapping solvers to
    # {(benchmark, family): num_asserts}
    data = {}
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))

            # Read data
            benchmark = drow[COL_BENCHMARK].strip()
            benchmark = get_benchmark_name(benchmark)
            (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)
            # Results for each benchmark is stored as list of tuples.
            # data[logic][family][benchmark] = [...]
            if logic not in data:
                data[logic] = {}
            if family not in data[logic]:
                data[logic][family] = {}

            assert(benchmark not in data[logic][family])

            data[logic][family][benchmark] = int(drow[COL_ASSERTS])

    return data

def read_data_results(file_name):
    # Map logics to a dict mapping solvers to
    # {(benchmark, family):(status, expected_status, time)}
    data = {}

    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))

            # Read data
            benchmark = drow[COL_BENCHMARK].strip()
            benchmark = get_benchmark_name(benchmark)
            (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)

            # Results for each benchmark is stored as list of tuples.
            # data[logic][family][benchmark] = [...]
            # the list [...] contains the tuples for all solvers.
            if logic not in data:
                data[logic] = {}
            if family not in data[logic]:
                data[logic][family] = {}
            if benchmark not in data[logic][family]:
                data[logic][family][benchmark] = []

            results = data[logic][family][benchmark]

            solver = drow[COL_SOLVER].strip()
            config = drow[COL_CONFIG].strip()
            cpu_time = float(drow[COL_CPU].strip())
            status = drow[COL_RESULT].strip()
            expected = drow[COL_EXPECTED].strip() \
                    if COL_EXPECTED in drow else 'starexec-unknown'
            solver_name = '{}_{}'.format(solver, config)
            results.append((solver_name, status, cpu_time, expected))

    return data

def is_eligible_unsat(benchmark, solving_data, num_asrts):
    # A benchmark is eligible for the unsat core track if the following
    # conditions hold: it
    #  - has more assertions than the minimum limit
    #  - is known to be unsat or is unknown,
    #  - all solvers have shown it unsat
    #  - at least two solvers have solved it
    num_solved_unsats = 0
    for solver_name, status, cpu_time, expected in solving_data:
        if status == 'unsat' \
                and expected in ('starexec-unknown', 'unsat'):
            num_solved_unsats += 1
    # All solvers correctly showed 'benchmark' to be unsat
    # Note: We require that at least two solvers were in the division.
    if num_solved_unsats >= 2 and num_solved_unsats == len(solving_data):
        return num_asrts >= NUM_ASSERTS

    return False

def is_eligible_standard(results):
    # Determine number of solvers that were able to correctly solve
    # the benchmark within 'TIME_LIMIT' seconds.
    num_solved = 0
    for solver_name, status, cpu_time, expected in results:
        if status in ('unsat', 'sat') \
           and expected in ('starexec-unknown', status) \
           and cpu_time <= TIME_LIMIT:
            num_solved += 1
    # All solvers correctly solved 'benchmark' within 'TIME_LIMIT'
    # seconds, hence remove benchmark from 'all_benchmarks'.
    #
    # Note: We require that at least two solvers were in the division.
    if num_solved >= 2 and num_solved == len(results):
        return False
    return True



def sanity_check_standard(data_list, selected_benchmarks, removed_benchmarks):
    if data_list == []:
        return

    for benchmark in selected_benchmarks:
        (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)

        for data, path in data_list:
            results_logic = data.get(logic, {})
            results_family = results_logic.get(family, {})
            results_benchmark = results_family.get(benchmark, [])

            if not is_eligible_standard(results_benchmark):
                print(benchmark)
                print('\n'.join([str(x) for x in results_benchmark]))
                assert(False)

    for benchmark in removed_benchmarks:
        (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)

        ineligibility_justified = False
        for data in data_list:
            results_logic = data.get(logic, {})
            results_family = results_logic.get(family, {})
            results_benchmark = results_family.get(benchmark, [])

            if not is_eligible_standard(results_benchmark):
                ineligibility_justified = True

        if not ineligibility_justified:
            print(benchmark)
            print('\n'.join([str(x) for x in results_benchmark]))
            assert(False)

def sanity_check_unsat(results_list, unsat_data, selected_benchmarks, removed_benchmarks):
    if results_list == [] or not unsat_data:
        return

    for benchmark in selected_benchmarks:
        (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)

        candidate_non_eligible = {}

        for (results, path) in results_list:
            results_logic = results.get(logic, {})
            results_family = results_logic.get(family, {})
            results_benchmark = results_family.get(benchmark, [])

            n_asrts_logic = unsat_data.get(logic, {})
            n_asrts_family = n_asrts_logic.get(family, {})
            n_asrts_benchmark = n_asrts_family.get(benchmark, 0)

            if not is_eligible_unsat(benchmark, results_benchmark, n_asrts_benchmark):
                if  benchmark not in candidate_non_eligible:
                    candidate_non_eligible[benchmark] = 0
                candidate_non_eligible[benchmark] += 1

        for k in candidate_non_eligible:
            if candidate_non_eligible[k] == len(results_list):
                print(k)
                (logic, family, benchmark) = \
                    split_benchmark_to_logic_family(k)
                for (res, path) in results_list:
                    print('\n'.join([str(x) for x in \
                        res[logic][family][benchmark]]))
                assert Fales

    for benchmark in sorted(removed_benchmarks):
        (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)

        ineligibility_justified_by = 0
        for (results, path) in results_list:
            results_logic = results.get(logic, {})
            results_family = results_logic.get(family, {})
            results_benchmark = results_family.get(benchmark, [])

            n_asrts_logic = unsat_data.get(logic, {})
            n_asrts_family = n_asrts_logic.get(family, {})
            n_asrts_benchmark = n_asrts_family.get(benchmark, 0)

            if not is_eligible_unsat(benchmark, results_benchmark, n_asrts_benchmark):
                ineligibility_justified_by += 1

        if ineligibility_justified_by != len(results_list):
            print("Ingeligibility justified by %d but there are %d "\
                    "filters" % (ineligibility_justified_by,\
                        len(results_list)))
            print(benchmark)
            assert(False)

# Given the solving data and all benchmarks, place the
# benchmarks that qualify based on solving data to a list
#
# input:
#  solving_data     - the filtering data
#  all_benchmark    - all benchmarks to be considered (not changed here)
# return:
#  added_benchmarks - the qualifying benchmarks from all_benchmarks are
#                     added here
def compute_qualifying_for_unsat_based_on_result(solving_data, all_benchmarks):

    added_benchmarks = []

    for logic, families in sorted(all_benchmarks.items()):
        if (logic not in solving_data):
            continue

        for family, benchmarks in families.items():
            if (family not in solving_data[logic]):
                continue
            for benchmark in benchmarks:
                if (benchmark not in solving_data[logic][family]):
                    continue

                results = solving_data[logic][family][benchmark]
                assert results

                num_solved_unsats = 0

                for solver_name, status, cpu_time, expected in results:
                    if status == 'unsat' \
                            and expected in ('starexec-unknown', 'unsat'):
                        num_solved_unsats += 1

                # All solvers correctly showed 'benchmark' to be unsat
                # Note: We require that at least two solvers were in the division.
                if num_solved_unsats >= 2 and num_solved_unsats == len(results):
                    added_benchmarks.append(benchmark)

    return added_benchmarks

# Filter out uninteresting benchmarks from 'all_benchmarks'.
# input:
#  data               - the solving data
#  all_benchmarks     - all currently interesting benchmarks
#  removed_benchmarks - benchmarks that have been removed
# output:
#  num_removed_per_logic - map from a logic to number of removed
#                          benchmarks in that logic.
# all_benchmarks and removed_benchmarks are changed by the function

def filter_uninteresting_standard(data, all_benchmarks,
        removed_benchmarks):
    num_removed_per_logic = {}
    for logic, families in sorted(data.items()):

        # Logics might have changed compared to last year.
        if logic not in all_benchmarks:
            continue

        num_removed_per_logic[logic] = 0

        for family, benchmarks in families.items():
            # Families might have changed compared to last year.
            if family not in all_benchmarks[logic]:
                continue

            for benchmark, results in benchmarks.items():
                # Benchmarks might have changed compared to last year.
                if benchmark not in all_benchmarks[logic][family]:
                    continue

                assert results
                if not is_eligible_standard(results):
                    all_benchmarks[logic][family].remove(benchmark)
                    removed_benchmarks.append(benchmark)
                    num_removed_per_logic[logic] += 1

    return num_removed_per_logic

def filter_asserts(asrts_data, all_benchmarks, num_all_benchmarks,
        stats):
    num_removed_per_logic = {}
    removed_benchmarks = []

    for logic, families in sorted(asrts_data.items()):
        num_removed_per_logic[logic] = 0

        if (logic not in all_benchmarks):
            print(logic)
            assert(False)

        for family, benchmarks in families.items():
            assert(family in all_benchmarks[logic])

            for benchmark, num_asrts in benchmarks.items():
                if num_asrts < NUM_ASSERTS:
                    all_benchmarks[logic][family].remove(benchmark)
                    removed_benchmarks.append(benchmark)
                    num_removed_per_logic[logic] += 1

    if stats:
        print_stats(num_removed_per_logic, num_all_benchmarks)

    return (removed_benchmarks, all_benchmarks, num_removed_per_logic)

# main_filter_standard: Remove benchmarks on the standard tracks based
# on multiple years' results.
# Input:
#  filter_csvs        - list of filter data to be used for filtering
#  all_benchmarks     - all available bechmarks
#  num_all_benchmarks - A map from logic to number of benchmarks it has
#  stats              - A boolean flag to print statistics
# Output:
#  removed_benchmarks - a list containing the benchmarks removed by the filtering
#  all_benchmarks     - a map containing benchmarks not removed by the filtering

def main_filter_standard(filter_csvs, all_benchmarks,
        num_all_benchmarks, stats):

    removed_benchmarks = []

    for (filter_csv, name) in filter_csvs:
        print("Filtering based on {}".format(name))
        num_removed_per_logic = filter_uninteresting_standard(filter_csv, all_benchmarks, \
                    removed_benchmarks)

    if stats:
        print_stats(num_removed_per_logic, num_all_benchmarks)

    return (removed_benchmarks, all_benchmarks)

# main_filter_unsat: Remove benchmarks on the unsat tracks based
# on multiple years' results and nuber of assertions
# Input:
#  filter_csvs        - list of filter data to be used for filtering
#  all_benchmarks     - all available bechmarks
#  num_all_benchmarks - A map from logic to number of benchmarks it has
#  asrts_data         - Data mapping benchmark to its number of
#                       assertions
#  stats              - A boolean flag to print statistics
# Output:
#  removed_benchmarks - a list containing the benchmarks removed by the filtering
#  all_benchmarks     - a map containing benchmarks not removed by the filtering


def main_filter_unsat(filter_csvs, all_benchmarks, num_all_benchmarks,
        asrts_data, stats):

    print("Filtering based on assert counts")
    (removed_benchmarks, all_benchmarks, num_removed_per_logic) = \
        filter_asserts(asrts_data, all_benchmarks, num_all_benchmarks,
                stats)

    added_benchmarks_hash = {}

    for (filter_csv, name) in filter_csvs:
        print("Filtering based on {}".format(name))
        added_benchmarks = compute_qualifying_for_unsat_based_on_result(filter_csv,
                all_benchmarks)

        for benchmark in added_benchmarks:
            (logic, family, benchmark) = split_benchmark_to_logic_family(benchmark)
            if (logic not in added_benchmarks_hash):
                added_benchmarks_hash[logic] = {}
            if (family not in added_benchmarks_hash[logic]):
                added_benchmarks_hash[logic][family] = set()

            added_benchmarks_hash[logic][family].add(benchmark)
            assert(benchmark in
                    added_benchmarks_hash[logic][family])

    for logic in all_benchmarks:
        if logic not in added_benchmarks_hash:
            # no benchmark added from this logic
            for family in all_benchmarks[logic]:
                for benchmark in all_benchmarks[logic][family]:
                    removed_benchmarks.append(benchmark)
                    num_removed_per_logic[logic] += 1
                all_benchmarks[logic][family] = []
            continue

        for family in all_benchmarks[logic]:
            if family not in added_benchmarks_hash[logic]:
                # no benchmark added from this family
                for benchmark in all_benchmarks[logic][family]:
                    removed_benchmarks.append(benchmark)
                    num_removed_per_logic[logic] += 1
                all_benchmarks[logic][family] = []
                continue

            to_remove = []
            for benchmark in all_benchmarks[logic][family]:
                if benchmark not in added_benchmarks_hash[logic][family]:
                    # this benchmark was not added from the family
                    to_remove.append(benchmark)
            for benchmark in to_remove:
                all_benchmarks[logic][family].remove(benchmark)
                num_removed_per_logic[logic] += 1
                removed_benchmarks.append(benchmark)

    if stats:
        print_stats(num_removed_per_logic, num_all_benchmarks)

    return (removed_benchmarks, all_benchmarks)


def print_stats(num_removed_per_logic, num_all_benchmarks):

    # Print statistics on the reduction achieved by ignoring uninteresting
    # benchmarks.
    for logic in num_removed_per_logic:
        num_total = num_all_benchmarks.get(logic, 0)
        num_removed = num_removed_per_logic[logic]
        reduction = \
            float(num_removed) / float(num_total) if num_total > 0 else 0.0
        print('{:15s}{:6d}{:20s} {:.2%} removed'.format(
                '{}:'.format(logic),
                num_total - num_removed,
                '\t (out of {})'.format(num_total),
                reduction
             ))


def main():

    args = parse_args()

    # Set up RNG
    random.seed(args.seed)

    # Load list of all considered benchmarks for this year's competition.
    all_benchmarks, num_logics, num_all_benchmarks = \
            read_benchmarks(args.benchmarks_file)
    print('All Benchmarks: {} logics, {} families, {} benchmarks'.format(
          len(all_benchmarks), num_logics, num_all_benchmarks))

    # Load list of benchmarks that are new for this year's competition
    new_benchmarks, num_new_logics, num_new_benchmarks = \
            read_benchmarks(args.new_benchmarks_file)
    print('New Benchmarks: {} logics, {} families, {} benchmarks'.format(
          len(new_benchmarks), num_new_logics, num_new_benchmarks))

    # Determine total number of benchmarks for each logic.
    num_all_benchmarks = {}
    for logic, families in all_benchmarks.items():
        num_all_benchmarks[logic] = 0
        for family, benchmarks in families.items():
            num_all_benchmarks[logic] += len(benchmarks)


    # Stores all selected benchmarks
    selected_benchmarks = []
    removed_benchmarks = []

    # empty means all logics are kept
    filter_logics = []
    if args.filter_logic:
        filter_logics = args.filter_logic.split(";")
        print("Filter logics: {0}".format(filter_logics))

    # Load data csvs to base filtering of 'uninteresting benchmarks' on.
    # Default: results csv from previous year
    # Unsat Core: csv with benchmark,number of assertions

    data_list = []
    for path in args.filter_csv:
        data_list.append((read_data_results(path), path))

    if (not args.unsat):
        (removed_bencharks, all_benchmarks) = \
            main_filter_standard(data_list, all_benchmarks,
                    num_all_benchmarks, args.print_stats)
    else:
        data = {}
        unsat_data = read_data_unsat(args.unsat)

        (removed_benchmarks, all_benchmarks) = \
                main_filter_unsat(data_list, all_benchmarks,
                        num_all_benchmarks, unsat_data,
                        args.print_stats)

    # 'all_benchmarks' now contains all eligible benchmarks (inclucing new
    # benchmarks.
    for logic, families in sorted(all_benchmarks.items()):
        if filter_logics and not logic in filter_logics:
            # print("Ignoring logic {0}".format(logic))
            continue
        # Collect all eligible benchmarks.
        eligible_benchmarks = set()
        for family, benchmarks in families.items():
            eligible_benchmarks.update(benchmarks)
        num_eligible = len(eligible_benchmarks)

        # This check would allow us in the future to place a minimum number of
        # benchmarks for a division, but for now just ignores 'empty'
        # divisions.
        if num_eligible == 0:
            print('No eligible benchmarks for {}. Skipping.'.format(logic))
            continue

        # Determine number of benchmarks to select.
        if num_eligible <= NUM_LOWER:
            num_select = num_eligible
        elif NUM_LOWER < num_eligible <= NUM_UPPER:
            num_select = NUM_LOWER
        else:
            num_select = int(PERCENT * num_eligible)

        print("For {:15s} selected {}".format(logic, num_select))

        if args.print_eligible:
            for benchmark in eligible_benchmarks:
                print('  Eligible: {}'.format(benchmark))

        # Stores the selected benchmarks for this logic.
        selected = set()

        # Sort eligible benchmarks. Make sure that the order of eligible
        # benchmarks is always the same for each execution of the script.
        # Sets in Python don't necessarily have the same order in each
        # execution of the script.
        eligible_benchmarks = sorted(eligible_benchmarks)

        # Pick at least one benchmark from each new family.
        new_families = new_benchmarks.get(logic, {})
        for family, benchmarks in new_families.items():
            benchmark = random.choice(sorted(benchmarks))
            assert args.unsat or benchmark in eligible_benchmarks
            if benchmark in eligible_benchmarks:
                eligible_benchmarks.remove(benchmark)
                selected.add(benchmark)

        # Pick the remaining number of benchmarks from all eligible benchmarks.
        while len(selected) < num_select:
            benchmark = random.choice(eligible_benchmarks)
            eligible_benchmarks.remove(benchmark)
            selected.add(benchmark)

        selected_benchmarks.extend(sorted(selected))

    if (args.unsat):
        sanity_check_unsat(data_list, unsat_data, selected_benchmarks, removed_benchmarks)
    else:
        sanity_check_standard(data_list, selected_benchmarks, removed_benchmarks)

    # Print selected benchmarks
    if args.out:
        with open(args.out, 'w') as outfile:
            benchmarks = ['{}{}'.format(args.prefix, b) \
                          for b in selected_benchmarks]
            outfile.write('\n'.join(benchmarks))

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--seed', dest='seed', type=int, help='RNG seed',
                    required=True)
    ap.add_argument('-b', '--benchmarks', dest='benchmarks_file',
                    help='List of benchmarks to be selected',
                    required=True)
    ap.add_argument('-n', '--new-benchmarks', dest='new_benchmarks_file',
                    help='List of new benchmarks to be selected',
                    required=True)
    ap.add_argument('-l', '--logics', dest='filter_logic',
                    help="Filter out benchmarks not in any of the given " \
                    "logics (semicolon separated) (default: all logics)")
    ap.add_argument('-f', '--filter', dest='filter_csv', action='append',
                    help="Filter out benchmarks based on csv")
    ap.add_argument('-o', '--out', dest='out',
                    help='Output file name to print selected benchmarks')
    ap.add_argument('--unsat', dest='unsat',
                    help="Filter for unsat core track")
    ap.add_argument('--print-stats', dest="print_stats",
                    action='store_true',
                    help='Print statistics')
    ap.add_argument('--print-eligible', dest='print_eligible',
                    action='store_true',
                    help='Print eligible benchmarks')
    ap.add_argument('--prefix', dest='prefix', default='',
                    help='The prefix to prepend to selected benchmark lines')
    return ap.parse_args()



if __name__ == '__main__':
    main()
