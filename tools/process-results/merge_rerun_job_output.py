#! /usr/bin/python

import pandas
from argparse import ArgumentParser

import os
import sys
import csv

def parse_args():
    parser = ArgumentParser(
            description="Merge csvs with results from StarExec for one "\
                        "track. If (parts of) a job were rerun, duplicate "\
                        "older job pairs are filtered out.")
    parser.add_argument ("-c", "--csv",
                         metavar="path[,path...]",
                         help="list of (overlapping) input csvs with results "\
                              "from StarExec")
    parser.add_argument ("-o", "--output",
                         help="path to output file")
    args = parser.parse_args()
    if not args.csv:
        die ("Missing input csv(s).")
    args.csv = args.csv.split(',') if args.csv else []
    return args


def main():
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_rows', None)
    args = parse_args()
    data = []
    for csv in args.csv:
        if not os.path.exists(csv):
            print("error: given file does not exist: {}".format(csv))
            sys.exit(1)
        data.append(pandas.read_csv(csv, dtype=str))
    result = pandas.concat(data, ignore_index=True)
    result.sort_values('pair id', ascending=True, inplace=True)
    result.drop_duplicates(
                    keep='last',
                    subset=['benchmark id','solver id'],
                    inplace=True)
    result.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
