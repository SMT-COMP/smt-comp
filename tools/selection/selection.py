#!/usr/bin/env python3

import argparse
import csv
import random

#==============================================================================
# Selection parameters
#==============================================================================

# Set time limit for interesting benchmarks. The default here is 1 second.
TIME_LIMIT = 1

# The rules give the following rules for the number of selected benchmarks
# (a) If a logic contains < 300 instances, all instances will be selected
# (b) If a logic contains between 300 and 600, a subset of 300 will be selected
# (c) If a logic contains > 600 then 50% will be selected
# The following three variables represent the parameters in these rules so that
# they can be modified if needed
NUM_LOWER = 300
NUM_UPPER = 600
PERCENT = 0.5

#==============================================================================

def read_benchmarks(file_name):
    # Maps benchmarks to corresponding logic and family.
    # benchmarksk[logic][family] = set(benchmarks...)
    benchmarks = {}
    num_families = 0
    num_benchmarks = 0
    with open(file_name, 'r') as infile:
        for benchmark in infile.readlines():
            benchmark_split = benchmark.strip().split('/')
            logic = benchmark_split[0]
            family = '/'.join(benchmark_split[:-1])
            benchmark = '/'.join(benchmark_split)
            if not logic in benchmarks:
                benchmarks[logic] = {}
            if not family in benchmarks[logic]:
                benchmarks[logic][family] = set()
                num_families += 1
            benchmarks[logic][family].add(benchmark)
            num_benchmarks += 1
    return benchmarks, num_families, num_benchmarks


def read_data(file_name):

    # Map logics to a dict mapping solvers to
    # {(benchmark, family):(status, expected_status, time)}
    data = {}

    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))

            benchmark = drow['benchmark'].strip()
            solver = drow['solver'].strip()
            config = drow['configuration'].strip()
            cpu_time = float(drow['cpu time'].strip())
            status = drow['result'].strip()
            expected = drow['expected'].strip()

            solver_name = '{}_{}'.format(solver, config)

            benchmark_split = benchmark.split('/')

            # Required due to how data was run in 2018 and 2017
            if benchmark_split[0] in ('Other Divisions', 'Datatype Divisions'):
                benchmark_split.pop(0)

            logic = benchmark_split[0]
            benchmark = '/'.join(benchmark_split)
            family = '/'.join(benchmark_split[:-1])

            # Store results for each benchmarks as solver tuples.
            # data[logic][family][benchmark] = [...]
            if logic not in data:
                data[logic] = {}
            if family not in data[logic]:
                data[logic][family] = {}
            if benchmark not in data[logic][family]:
                results = []
                data[logic][family][benchmark] = results
            else:
                results = data[logic][family][benchmark]

            results.append((solver_name, status, cpu_time, expected))

    return data


def sanity_check(data, selected_benchmarks, removed_benchmarks):
    if not data:
        return

    for benchmark in selected_benchmarks:
        benchmark_split = benchmark.split('/')
        logic = benchmark_split[0]
        family = '/'.join(benchmark_split[:-1])

        results_logic = data.get(logic, {})
        results_family = results_logic.get(family, {})
        results_benchmark = results_family.get(benchmark, [])

        if not is_eligible(results_benchmark):
            print(benchmark)
            print('\n'.join([str(x) for x in results_benchmark]))
        assert is_eligible(results_benchmark)

    for benchmark in removed_benchmarks:
        benchmark_split = benchmark.split('/')
        logic = benchmark_split[0]
        family = '/'.join(benchmark_split[:-1])

        results_logic = data.get(logic, {})
        results_family = results_logic.get(family, {})
        results_benchmark = results_family.get(benchmark, [])

        if is_eligible(results_benchmark):
            print(benchmark)
            print('\n'.join([str(x) for x in results_benchmark]))
        assert not is_eligible(results_benchmark)


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
    ap.add_argument('-f', '--filter', dest='filter_csv',
                    help="Filter out benchmarks based on csv containing " \
                         "previous year's results")
    ap.add_argument('-o', '--out', dest='out',
                    help='Output file name to print selected benchmarks')
    ap.add_argument('--print-stats', dest="print_stats",
                    action='store_true',
                    help='print statistics')
    ap.add_argument('--print-eligible', dest='print_eligible',
                    action='store_true',
                    help='print eligible benchmarks')
    return ap.parse_args()


def is_eligible(results):
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
    if args.print_stats:
        for logic, families in all_benchmarks.items():
            num_all_benchmarks[logic] = 0
            for family, benchmarks in families.items():
                num_all_benchmarks[logic] += len(benchmarks)


    # Stores all selected benchmarks
    selected_benchmarks = []
    removed_benchmarks = []

    # Load data of previous year's result used to filter out uninteresting
    # benchmarks.
    data = {}
    if args.filter_csv:
        data = read_data(args.filter_csv)

    # Filter out uninteresting benchmarks from 'all_benchmarks'.
    for logic, families in sorted(data.items()):

        # For printing statistics
        num_removed = 0

        # Logics might have changed compared to last year.
        if logic not in all_benchmarks:
            continue

        for family, benchmarks in families.items():
            # Families might have changed compared to last year.
            if family not in all_benchmarks[logic]:
                continue

            for benchmark, results in benchmarks.items():

                # Benchmarks might have changed compared to last year.
                if benchmark not in all_benchmarks[logic][family]:
                    continue

                assert results
                if not is_eligible(results):
                    all_benchmarks[logic][family].remove(benchmark)
                    removed_benchmarks.append(benchmark)
                    num_removed += 1

        # Print statistics on the reduction achieved by ignoring uninteresting
        # benchmarks.
        if args.print_stats:
            num_total = num_all_benchmarks.get(logic, 0)
            reduction = \
                float(num_removed) / float(num_total) if num_total > 0 else 0.0
            print('{:15s}{:6d}{:20s} {:.2%} removed'.format(
                    '{}:'.format(logic),
                    num_total - num_removed,
                    '\t (out of {})'.format(num_total),
                    reduction
                 ))


    # 'all_benchmarks' now contains all eligible benchmarks (inclucing new
    # benchmarks.
    for logic, families in sorted(all_benchmarks.items()):

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
            assert benchmark in eligible_benchmarks
            eligible_benchmarks.remove(benchmark)
            selected.add(benchmark)

        # Pick the remaining number of benchmarks from all eligible benchmarks.
        while len(selected) < num_select:
            benchmark = random.choice(eligible_benchmarks)
            eligible_benchmarks.remove(benchmark)
            selected.add(benchmark)

        selected_benchmarks.extend(sorted(selected))

    sanity_check(data, selected_benchmarks, removed_benchmarks)

    # Print selected benchmarks
    if args.out:
        with open(args.out, 'w') as outfile:
            outfile.write('\n'.join(selected_benchmarks))


if __name__ == '__main__':
    main()
