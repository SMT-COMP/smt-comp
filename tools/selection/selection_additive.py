#!/usr/bin/env python3

import sys
import argparse

import selection

# Set time limit for interesting benchmarks (in seconds)
TIME_LIMIT=600

def is_provably_hard(results, solve_type):
    assert solve_type in ('hard-only', 'unsolved-only')
    assert len(results) != 0
    # Determine number of solvers that were able to correctly solve
    # the benchmark within 'TIME_LIMIT' seconds.
    num_solved_within_limit = 0
    num_solved_after_limit = 0
    for solver_name, status, cpu_time, expected in results:
        if status in ('unsat', 'sat') \
                and expected in ('starexec-unknown', status):
            if cpu_time <= TIME_LIMIT:
                num_solved_within_limit += 1
            else:
                num_solved_after_limit += 1
    # At least one solver correctly solved 'benchmark' within 'TIME_LIMIT'
    # seconds, inclusion to 'added_benchmarks' not justified here.
    #
    # Note: We require that at least one solver was in the division.
    # We want the instance to have been attempted
    if num_solved_within_limit >= 1:
        # Ineligible because solved within time limit by at least one solver
        return False

    assert num_solved_within_limit == 0

    if num_solved_after_limit >= 1:
        if solve_type == 'unsolved-only':
            return False
        else:
            return True

    assert num_solved_after_limit == 0
    if solve_type == 'unsolved-only':
        return True
    else:
        return False

# Modifies added_benchmarks
def get_provably_hard(data, added_benchmarks, selection_mode):
    num_added_per_logic = {}
    for logic, families in sorted(data.items()):
        num_added_per_logic[logic] = 0
        if logic not in added_benchmarks:
            added_benchmarks[logic] = {}
        for family, benchmarks in families.items():
            if family not in added_benchmarks[logic]:
                added_benchmarks[logic][family] = set()
            for benchmark, results in benchmarks.items():
                assert results
                if benchmark not in added_benchmarks[logic][family] and\
                        is_provably_hard(results, selection_mode):
                    added_benchmarks[logic][family].add(benchmark)
                    num_added_per_logic[logic] += 1

    return num_added_per_logic

def print_stats_added(num_added_per_logic, num_all_benchmarks):

    # Print statistics on the reduction achieved by ignoring uninteresting
    # benchmarks.
    for logic in num_added_per_logic:
        num_total = num_all_benchmarks.get(logic, 0)
        num_added = num_added_per_logic[logic]
        reduction = \
            1 - float(num_added) / float(num_total) if num_total > 0 else 1.0
        print('{:15s}{:6d}{:20s} {:.2%} removed'.format(
                '{}:'.format(logic),
                num_added,
                '\t (out of {})'.format(num_total),
                reduction
             ))




# main_add_standard: Add benchmarks on the cloud track based
# on multiple years' results.
# Input:
#  justification_csvs - list of justificatioon data to be used for
#                       inclusion
#  all_benchmarks     - all available bechmarks
#  num_all_benchmarks - A map from logic to number of benchmarks it has
#  stats              - A boolean flag to print statistics
# Output:
#  added_benchmarks   - a map containing the added benchmarks

def main_add_standard(justification_csvs, all_benchmarks, num_all_benchmarks,
        selection_mode, stats):

    added_benchmarks = {}
    for (justification_csv, name) in justification_csvs:
        print("Adding based on {}".format(name))
        num_added_per_logic = get_provably_hard(justification_csv,
                added_benchmarks, selection_mode)
    logics_to_delete = []
    for logic in added_benchmarks:
        if logic not in all_benchmarks:
            # logic is not available this year
            logics_to_delete.append(logic)
            continue
        families_to_delete = []
        for family in added_benchmarks[logic]:
            if family not in all_benchmarks[logic]:
                # family not available this year
                families_to_delete.append(family)
                continue
            benchmarks_to_delete = []
            for benchmark in added_benchmarks[logic][family]:
                if benchmark not in all_benchmarks[logic][family]:
                    # benchmark not available this year
                    benchmarks_to_delete.append(benchmark)
            for k in benchmarks_to_delete:
                added_benchmarks[logic][family].remove(k)
        for k in families_to_delete:
            del added_benchmarks[logic][k]
    for k in logics_to_delete:
        del added_benchmarks[k]

    if stats:
        print("Number of benchmarks per logic after adding:")
        print_stats_added(num_added_per_logic, num_all_benchmarks)

    return added_benchmarks



def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--benchmarks', dest='benchmarks_file',
                    help='List of benchmarks to be selected',
                    required=True)
    ap.add_argument('-l', '--logics', dest='filter_logic',
                    help="Filter out benchmarks not in any of the given " \
                    "logics (semicolon separated) (default: all logics)")
    ap.add_argument('-f', '--justification', dest='justification_csv', action='append',
                    help="Include based on csv", required=True)
    ap.add_argument('-o', '--out', dest='out',
                    help='Output file name to print selected benchmarks')
    ap.add_argument('--print-stats', dest="print_stats",
                    action='store_true',
                    help='Print statistics')
    ap.add_argument('--prefix', dest='prefix', default='',
                    help='The prefix to prepend to selected benchmark lines')
    ap.add_argument('--selection-mode', dest='selection_mode',
                    default='hard-only', help='Which type of benhmarks are included'\
                    'Either hard-only or unsolved-only')
    return ap.parse_args()

def main():
    args = parse_args()

    if (args.justification_csv == None):
        print("No justification csvs given. Selection is empty")

    selection_mode = args.selection_mode

    print("Using selection mode %s" % selection_mode)
    assert selection_mode in ('hard-only', 'unsolved-only')

    all_benchmarks, num_logics, num_all_benchmarks = \
            selection.read_benchmarks(args.benchmarks_file)

    print('All Benchmarks: {} logics, {} families, {} benchmarks'.format(
          len(all_benchmarks), num_logics, num_all_benchmarks))

    # Determine total number of benchmarks for each logic.
    num_all_benchmarks = {}
    for logic, families in all_benchmarks.items():
        num_all_benchmarks[logic] = 0
        for family, benchmarks in families.items():
            num_all_benchmarks[logic] += len(benchmarks)

    # Stores all selected benchmarks
    selected_benchmarks = []

    # empty means all logics are kept
    filter_logics = []
    if args.filter_logic:
        filter_logics = args.filter_logic.split(";")
        print("Filter logics: {0}".format(filter_logics))

    # Load data csvs to base inclusion of 'interesting benchmarks' on.
    # Default: results csv from previous years

    data_list = []
    for path in args.justification_csv:
        data_list.append((selection.read_data_results(path), path))

    added_benchmarks = \
            main_add_standard(data_list, all_benchmarks,
                    num_all_benchmarks, selection_mode,
                    args.print_stats)

    # 'added_benchmarks' now contains all eligible benchmarks
    total_selected = 0
    for logic, families in sorted(added_benchmarks.items()):
        if filter_logics and not logic in filter_logics:
            # print("Ignoring logic {0}".format(logic))
            continue
        # Collect all eligible benchmarks.
        eligible_benchmarks = set()
        for family, benchmarks in families.items():
            eligible_benchmarks.update(benchmarks)
        num_eligible = len(eligible_benchmarks)

        # Some logics migh contain no eligible benchmarks
        if num_eligible == 0:
            print('No eligible benchmarks for {}. Skipping.'.format(logic))
            continue

        num_select = num_eligible

        print("For {:15s} selected {}".format(logic, num_select))
        total_selected += num_select

        # Sort eligible benchmarks. Make sure that the order of eligible
        # benchmarks is always the same for each execution of the script.
        # Sets in Python don't necessarily have the same order in each
        # execution of the script.
        eligible_benchmarks = sorted(eligible_benchmarks)

        selected_benchmarks.extend(eligible_benchmarks)

    print("Total selected: {}".format(total_selected))

    # Print selected benchmarks
    if args.out:
        with open(args.out, 'w') as outfile:
            benchmarks = ['{}{}'.format(args.prefix, b) \
                          for b in selected_benchmarks]
            outfile.write('\n'.join(benchmarks))

if __name__ == '__main__':
    main()
