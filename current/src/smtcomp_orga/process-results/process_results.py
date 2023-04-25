#!/usr/bin/env python3
#
# This scripts processes results from the StarExec CSV files:
#  1. removes excluded benchmarks,
#  2. set expected result for benchmark with manually chosen status,
#  3. optionally adds column for incremental track.
#

from argparse import ArgumentParser
import csv
import os
import sys

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)


def read_exclude_file(path):
    filter = set()
    with open(path, "r") as file:
        for benchmark in file.readlines():
            benchmark = benchmark.rstrip()
            if benchmark.startswith("./"):
                benchmark = benchmark[2:]
            filter.add(benchmark)
    return filter


def read_map_file(path):
    benchmap = dict()
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for line in reader:
            benchmark = line[0]
            benchmap[benchmark] = line[1]
    return benchmap


def read_inc_decision_file(path):
    benchmap = dict()
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for line in reader:
            # lines are of the form benchmark,wrong answers,solver,solver id
            benchmark = line[0]
            benchmap[benchmark] = dict()
            benchmap[benchmark][line[3]] = line[1]
    return benchmap


def process_csv(csvpath, excluded, decided, inc_decided):
    with open(csvpath, "r") as file:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        header = next(reader)
        writer.writerow(header)
        for pair in reader:
            drow = dict(zip(iter(header), iter(pair)))
            benchmark = drow["benchmark"]
            benchmark = benchmark[benchmark.index("/") + 1:]
            if benchmark in decided:
                drow["expected"] = decided[benchmark]
                pair = [ drow[col] for col in header]
            if benchmark in inc_decided:
                if drow["solver id"] in inc_decided[benchmark]:
                    # if there was a wrong answer, the correct-answers
                    # is set to 0 according to rules.
                    drow["wrong-answers"] = 1
                    drow["correct-answers"] = 0
                    pair = [ drow[col] for col in header]
            if benchmark not in excluded:
                writer.writerow(pair)


def main():
    global g_args
    parser = ArgumentParser(
            usage="process_result_csv "\
                  "<input: csv>\n\n" \
                  "Filter the csv files and remove problematic pairs " \
                  "based on blacklist")
    parser.add_argument("-x", "--exclude",
                        help="file containing the benchmarks that are " \
                        "to be excluded")
    parser.add_argument("-d", "--decision",
                        help="csv file containing status for manually " \
                        "decided benchmarks")
    parser.add_argument("-i", "--incremental_decision",
                        help="csv file containing manually determined " \
                        "wrong results in incremental track")
    parser.add_argument ("input_csv",
            help="the csv file containing results from starexec")
    g_args = parser.parse_args()

    if not os.path.exists(g_args.input_csv):
        die("file not found: {}".format(g_args.input_csv))

    excluded = set()
    if (g_args.exclude):
        if not os.path.exists(g_args.exclude):
            die("file not found: {}".format(g_args.exclude))

        excluded=read_exclude_file(g_args.exclude)

    decided = dict()
    if (g_args.decision):
        if not os.path.exists(g_args.decision):
            die("file not found: {}".format(g_args.decision))

        decided = read_map_file(g_args.decision)

    inc_decided = dict()
    if (g_args.incremental_decision):
        if not os.path.exists(g_args.incremental_decision):
            die("file not found: {}".format(g_args.incremental_decision))

        inc_decided = read_inc_decision_file(g_args.incremental_decision)

    process_csv(g_args.input_csv, excluded, decided, inc_decided)

if __name__ == '__main__':
    main()
