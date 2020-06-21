#!/usr/bin/env python3
#
# This scripts filters results from the StarExec CSV files, based on a
# list of blacklisted benchmarks.
#
# Benchmarks can be blacklisted because they are malformed, sorted into the
# wrong division, or because there were problems running some Job pairs on
# StarExec.
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
    filter = {}
    with open(path, "r") as file:
        for benchmark in file.readlines():
            benchmark = benchmark.rstrip()
            if benchmark.startswith("./"):
                benchmark = benchmark[2:]
            filter[benchmark] = 1
    return filter


def filter_csv(csvpath, filter):
    with open(csvpath, "r") as file:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        header = next(reader)
        writer.writerow(header)
        for pair in reader:
            drow = dict(zip(iter(header), iter(pair)))
            benchmark = drow["benchmark"]
            benchmark = benchmark[benchmark.index("/") + 1:]
            if benchmark not in filter:
                writer.writerow(pair)


def main():
    global g_args
    parser = ArgumentParser(
            usage="filter_result_csv "\
                  "<input: csv>\n\n" \
                  "Filter the csv files and remove problematic pairs " \
                  "based on blacklist")
    parser.add_argument ("input_csv",
            help="the csv file containing results from starexec")
    parser.add_argument("-x", "--exclude",
                        help="file containing the benchmarks that are " \
                        "to be excluded",
                        required = True)
    g_args = parser.parse_args()

    if not os.path.exists(g_args.input_csv):
        die("file not found: {}".format(g_args.input_csv))
    if not os.path.exists(g_args.exclude):
        die("file not found: {}".format(g_args.exclude))

    filter=read_exclude_file(g_args.exclude)
    filter_csv(g_args.input_csv, filter)

if __name__ == '__main__':
    main()
