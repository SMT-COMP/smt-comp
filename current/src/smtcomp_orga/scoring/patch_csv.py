#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import sys

def parseArgs():
    parser = ArgumentParser(
            description = "Patch a given original csv using a patch file. "\
                          "The patch file is also a CSV file.  The first "\
                          "column of this file must be a unique id.  The "\
                          "other columns provide the corrected value.\n"\
                          "This function will go over the original CSV row "\
                          "by row and if the id column matches it replaces "\
                          "all other columns by the new value.")
    parser.add_argument("-o", "--original", required=True,
            help="the original csv")
    parser.add_argument("-p", "--patch", required=True,
            help="the patch csv")
    return parser.parse_args()

if __name__ == '__main__':
    global g_args
    g_args = parseArgs()
    patches = dict()

    with open(g_args.patch) as patch:
        reader = csv.reader(patch)
        header = next(reader)
        patch_column = header[0]
        for row in reader:
            key = row[0]
            drow = dict(zip(iter(header[1:]), iter(row[1:])))
            patches[key] = drow

    with open(g_args.original) as orig:
        reader = csv.reader(orig)
        writer = csv.writer(sys.stdout)
        header = next(reader)
        writer.writerow(header)
        for row in reader:
            new_row = row
            drow = dict(zip(iter(header), iter(row)))
            key = drow[patch_column]
            if key in patches:
                patch = patches[key]
                for (k,v) in patch.items():
                    drow[k] = v
                new_row = [drow[col] for col in header]
            writer.writerow(new_row)
