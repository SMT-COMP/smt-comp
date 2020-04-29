#!/usr/bin/env python3

from argparse import ArgumentParser
from extract_data_from_solvers_divisions import g_logics_all as g_logics_all
import sys
import os

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def get_division_str(divisions_indexed_by_tracks):
    divisions = {}
    for track in divisions_indexed_by_tracks:
        for l in divisions_indexed_by_tracks[track]:
            if l not in divisions:
                divisions[l] = []
            divisions[l].append(track)

    division_fields = []
    for l in sorted(divisions):
        sub_division_fields = "- name: {}\n  tracks:\n{}".format(
                l, "\n".join(
                    map(lambda x: "  - {}".format(x), divisions[l])))
        division_fields.append(sub_division_fields)
    division_fields_str = "\n".join(division_fields)
    return division_fields_str

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Generate participants.md file for website.")
    parser.add_argument ("-y", "--year",
            required=True,
            help="the year of the competition")
    parser.add_argument ("-n", "--nyse",
            required=True,
            help="nyse opening date and value as 'yyyy-mm-dd;xxxxx.xx'")
    parser.add_argument("md_path",
            help="output path for generated participants.md file")
    args = parser.parse_args()

    if not os.path.exists(args.md_path):
        die("Path not found: {}".format(args.md_path))

    args.nyse = args.nyse.split(';')
    if not len(args.nyse) == 2:
        die("Invalid NYSE data")

    ofile_name = "participants.md"
    outfile = open(os.path.join(args.md_path, ofile_name), "w")
    md_str = "---\n"\
             "layout: participants_2020\n\n"\
             "year: {}\n"\
             "participants: participants_{}\n\n"\
             "nyse:\n"\
             "  date: {}\n"\
             "  value: {}\n\n"\
             "divisions:\n{}\n---".format(
                 args.year,
                 args.year,
                 args.nyse[0],
                 args.nyse[1],
                 get_division_str(g_logics_all))
    outfile.write(md_str)

