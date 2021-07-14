#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import sys

def parseArgs():
    parser = ArgumentParser(
            description = "Given two csvs, the original and the adjunct, "\
                          "go over original's headers and pick the "\
                          "corresponding entries from the adjunct. "\
                          "Ensures that the output will have the same "\
                          "number of columns as the original.  If an original "\
                          "column does not appear in the adjunct, the "\
                          "entry will be empty. ")
    parser.add_argument("-o", "--original", required=True,
            help="the original csv")
    parser.add_argument("-a", "--adjunct", required=True,
            help="the adjunct csv")
    return parser.parse_args()

if __name__ == '__main__':
    global g_args
    g_args = parseArgs()

    with open(g_args.original) as orig, open(g_args.adjunct) as adjunct:
        reader = csv.reader(orig)
        writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')
        o_header_list = next(reader)
        writer.writerow(o_header_list)
        a_reader = csv.reader(adjunct)
        a_header = next(a_reader)
        for row in a_reader:
            drow = dict(zip(iter(a_header), iter(row)))
            new_row = [ drow[col] if col in drow else "-"
                        for col in o_header_list ]
            writer.writerow(new_row)

