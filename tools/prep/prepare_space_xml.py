#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_xml_tree = None
g_divisions = {}

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)


# Read csv with solver data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
def read_csv(fname, track):
    global g_divisions
    with open(args.csv) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            divisions = None
            if track == 'track_single_query':
                divisions = drow['Single Query Track'].split(';')
            elif track == 'track_incremental':
                divisions = drow['Incremental Track'].split(';')
            elif track == 'track_challenge':
                divisions = drow['Challenge Track'].split(';')
            elif track == 'track_model_validation':
                divisions = drow['Model Validation Track'].split(';')
            elif track == 'track_unsat_core':
                divisions = drow['Unsat Core Track'].split(';')
            assert (divisions)

            for division in divisions:
                if division == "":
                    continue
                if division not in g_divisions:
                    g_divisions[division] = []
                g_divisions[division].append(
                        [drow['Solver ID'], drow['Solver Name']])


def is_model_validation_benchmark(benchmark):
    isSat = False
    isQF_BV = False
    for child in benchmark:
        if child.attrib['name'] == 'status' and child.attrib['value'] == "sat":
            isSat = True
        if child.attrib['name'] == 'set-logic' and child.attrib['value'] == "QF_BV":
            isQF_BV = True
    return isSat and isQF_BV

def filter_model_validation_benchmarks(space):
    spaces = space.findall('Space')
    for s in spaces: filter_model_validation_benchmarks(s)
    benchmarks = space.findall('Benchmark')
    for b in benchmarks:
        if (not is_model_validation_benchmark(b)):
            space.remove(b)

# Traverse space and remove all but one benchmark for each (sub)space with
# benchmarks (for test runs on StarExec).
def filter_benchmarks_in_space(space):
    spaces = space.findall('Space')
    for s in spaces: filter_benchmarks_in_space(s)
    benchmarks = space.findall('Benchmark')
    for b in benchmarks[1:]: space.remove(b)

# Traverse space and add solvers to divisions and their subspaces.
def add_solvers_in_space(space, solvers):
    spaces = space.findall('Space')
    for s in spaces: add_solvers_in_space(s, solvers)
    for solver in solvers:
        ET.SubElement(
                space,
                'Solver',
                attrib = {'id': solver[0], 'name': solver[1]})

# Parse xml and add solvers to divisions.
# If 'filter_benchmarks' is true, remove all but one benchmark for each
# (sub)space with benchmarks (for test runs on StarExec).
def add_solvers(track, filter_benchmarks):
    global g_xml_tree
    root = g_xml_tree.getroot()
    incremental_space = root.find('.//Space[@name="incremental"]')
    non_incremental_space = root.find('.//Space[@name="non-incremental"]')
    for space in [incremental_space, non_incremental_space]:
        if space:
            if track == 'track_model_validation':
                filter_model_validation_benchmarks(space)
            # filter benchmarks
            if filter_benchmarks:
                filter_benchmarks_in_space(space)
            # add solvers
            subspaces = space.findall('Space')
            for subspace in subspaces:
                division = subspace.attrib['name']
                if division in g_divisions:
                    solvers = g_divisions[division]
                    # Only add solvers if the division is competitive
                    # TODO make this check aware of non-competitive solvers and solver variants
                    if len(solvers) > 1:
                      add_solvers_in_space(subspace, solvers)
            # remove top-level non-incremental/incremental space tag
            root.extend(subspaces)
            root.remove(space)


if __name__ == '__main__':
    parser = ArgumentParser(
            usage="prepare_space_xml "\
                  "-t <track> "\
                  "<space: xml> <solvers: csv> <outfile: xml>\n\n"
                  "Add solvers from csv to space with divisions "\
                  "(and benchmarks)\nto upload as space xml to StarExec.")
    parser.add_argument ("space_xml",
            help="the input space xml from the SMT-LIB space on StarExec "\
                    "(with divisions and benchmarks), top-level space: "\
                    "non-incremental or incremental")
    parser.add_argument ("csv",
            help="the input csv with solvers and divisions as generated from"\
                 "tools/prep/extract_data_from_submission.py")
    parser.add_argument ("out_xml",
            help="the output space xml (with solvers added to divisions)")
    parser.add_argument('-t',
            type=str, dest="track",
            help="SMT-COMP track name (one out of:"\
                 "'single_query', 'incremental', 'challenge',"\
                 "'model_validation', 'unsat_core'",
            required = True)
    parser.add_argument ("-f",
            action="store_true", dest="filter", default=False,
            help="filter space to only keep one (the first) benchmark " \
                  "in each space with benchmarks (for test runs)")
    args = parser.parse_args()

    if not os.path.exists(args.space_xml):
        die("file not found: {}".format(args.space_xml))
    if not os.path.exists(args.csv):
        die("file not found: {}".format(args.csv))

    if args.track not in ['single_query', 'incremental', 'challenge',
                          'model_validation', 'unsat_core']:
        die("invalid track name")
    args.track = "track_{}".format(args.track)

    g_xml_tree = ET.parse(args.space_xml)
    read_csv(args.csv, args.track)
    add_solvers(args.track, args.filter)
    g_xml_tree.write(args.out_xml)
