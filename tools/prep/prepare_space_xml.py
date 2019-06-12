#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_args = None
g_xml_tree = None
g_divisions = {}
selected = set()

TRACK_SINGLE_QUERY = 'track_single_query'
TRACK_INCREMENTAL = 'track_incremental'
TRACK_SINGLE_QUERY_CHALLENGE = 'track_single_query_challenge'
TRACK_INCREMENTAL_CHALLENGE = 'track_incremental_challenge'
TRACK_UNSAT_CORE = 'track_unsat_core'
TRACK_MODEL_VALIDATION = 'track_model_validation'

# Solver ID columns
COL_SOLVER_ID_PRELIM = 'Preliminary Solver ID'
COL_SOLVER_ID = 'Solver ID'
COL_SOLVER_ID_WRAPPED_SQ = 'Wrapped Solver ID Single Query'
COL_SOLVER_ID_WRAPPED_INC = 'Wrapped Solver ID Incremental'
COL_SOLVER_ID_WRAPPED_MV = 'Wrapped Solver ID Model Validation'
COL_SOLVER_ID_WRAPPED_UC = 'Wrapped Solver ID Unsat Core'
# Track Columns
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_CHALLENGE_TRACK_SINGLE_QUERY = 'Challenge Track (single query)'
COL_CHALLENGE_TRACK_INCREMENTAL = 'Challenge Track (incremental)'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

# Read csv with solver data of the form:
#   solver_id  | solver_name | single_query_track | ... other tracks
#   ....       | ....        | entered divisions  | ...
# Order of tracks: single query, incremental, challenge, model val, unsat core
# Columns are separated by ',' and divisions are separated by ';'.
# If 'use_wrapped' is true, use wrapped solver IDs instead.
def read_csv(fname, track, use_wrapped):
    global g_divisions
    col_solver_id = COL_SOLVER_ID
    if use_wrapped:
        if track == TRACK_SINGLE_QUERY:
            col_solver_id = COL_SOLVER_ID_WRAPPED_SQ
        elif track == TRACK_INCREMENTAL:
            col_solver_id = COL_SOLVER_ID_WRAPPED_INC
        elif track == TRACK_SINGLE_QUERY_CHALLENGE:
            col_solver_id = COL_SOLVER_ID_WRAPPED_SQ
        elif track == TRACK_INCREMENTAL_CHALLENGE:
            col_solver_id = COL_SOLVER_ID_WRAPPED_INC
        elif track == TRACK_MODEL_VALIDATION:
            col_solver_id = COL_SOLVER_ID_WRAPPED_MV
        elif track == TRACK_UNSAT_CORE:
            col_solver_id = COL_SOLVER_ID_WRAPPED_UC
    with open(fname) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            solver_id = drow[col_solver_id]
            if not solver_id: continue
            divisions = None
            if track == TRACK_SINGLE_QUERY:
                divisions = drow[COL_SINGLE_QUERY_TRACK].split(';')
            elif track == TRACK_INCREMENTAL:
                divisions = drow[COL_INCREMENTAL_TRACK].split(';')
            elif track == TRACK_SINGLE_QUERY_CHALLENGE:
                divisions = drow[COL_CHALLENGE_TRACK_SINGLE_QUERY].split(';')
            elif track == TRACK_INCREMENTAL_CHALLENGE:
                divisions = drow[COL_CHALLENGE_TRACK_INCREMENTAL].split(';')
            elif track == TRACK_MODEL_VALIDATION:
                divisions = drow[COL_MODEL_VALIDATION_TRACK].split(';')
            elif track == TRACK_UNSAT_CORE:
                divisions = drow[COL_UNSAT_CORE_TRACK].split(';')
            assert (divisions)

            for division in divisions:
                if division == "":
                    continue
                if division not in g_divisions:
                    g_divisions[division] = []
                g_divisions[division].append(
                        [drow[col_solver_id], drow['Solver Name']])

def read_selected(fname):
    global selected
    with open(fname) as file:
       for line in file:
         line = line.strip()
         if line:
           selected.add(line)


def is_model_validation_benchmark(benchmark):
    isSat = False
    isQF_BV = False
    for child in benchmark:
        if child.attrib['name'] == 'status' and child.attrib['value'] == "sat":
            isSat = True
        if child.attrib['name'] == 'set-logic' and child.attrib['value'] == "QF_BV":
            isQF_BV = True
    return isSat and isQF_BV

def filter_model_validation_benchmarks(space, select_benchmarks):
    spaces = space.findall('Space')
    for s in spaces: filter_model_validation_benchmarks(s, select_benchmarks)
    benchmarks = space.findall('Benchmark')
    for b in benchmarks:
        if (not is_model_validation_benchmark(b)):
            space.remove(b)

def space_is_empty(space):
    spaces = space.findall('Space')
    benchmarks = space.findall('Benchmark')
    return not spaces and not benchmarks

def space_has_no_solvers(space):
    solvers = space.findall('Solver')
    return not solvers

def remove_empty_spaces(space):
    spaces = space.findall('Space')
    for s in spaces:
        remove_empty_spaces(s)
        if space_is_empty(s):
            space.remove(s)

def remove_spaces_without_solvers(space):
    spaces = space.findall('Space')
    for s in spaces:
        remove_spaces_without_solvers(s)
        if space_has_no_solvers(s):
            space.remove(s)

def is_unsat_core_benchmark(benchmark):
    isUnsat = False
    hasNumAsrtsTag = False
    hasMoreThanOneAsrt = False

    for child in benchmark:
        if child.attrib['name'] == 'status' and child.attrib['value'] == "unsat":
            isUnsat = True
        if child.attrib['name'] == 'num_asrts':
            hasNumAsrtsTag = True
            if int(child.attrib['value']) > 1:
                hasMoreThanOneAsrt = True
    return isUnsat and (not hasNumAsrtsTag or hasMoreThanOneAsrt)

def filter_unsat_core_benchmarks(space, select_benchmarks):
    spaces = space.findall('Space')
    for s in spaces: filter_unsat_core_benchmarks(s, select_benchmarks)
    benchmarks = space.findall('Benchmark')
    for b in benchmarks:
        if (not is_unsat_core_benchmark(b)):
            space.remove(b)

# Traverse space and remove all but one benchmark for each (sub)space with
# benchmarks (for test runs on StarExec).
def filter_benchmarks_in_space(space, n, select_benchmarks,path):
    path = path+"/"+space.attrib['name']
    spaces = space.findall('Space')
    for s in spaces: filter_benchmarks_in_space(s, n, select_benchmarks,path)
    benchmarks = space.findall('Benchmark')
    if select_benchmarks:
      for b in benchmarks:
        bname = path +"/"+b.attrib['name']
        if bname not in selected:
          space.remove(b)
        else:
          selected.remove(bname)
    if n>0:
      for b in benchmarks[n:]: space.remove(b)

# Traverse space and add solvers to divisions and their subspaces.
def add_solvers_in_space(space, solvers):
    spaces = space.findall('Space')
    for s in spaces: add_solvers_in_space(s, solvers)
    for solver in solvers:
        ET.SubElement(
                space,
                'Solver',
                attrib = {'id': solver[0], 'name': solver[1]})

# Return if a division is competitive based on the list of given solvers.
# Currently, this only considers non-competing solvers as given via '-e'.
def is_competitive(solvers):
    global g_args
    count = len(solvers)
    for nc in g_args.non_competing:
        for s in solvers:
            if nc == s[0]:
                count -= 1
                break
    return count > 1


# Parse xml and add solvers to divisions.
# If 'filter_benchmarks' is true, remove all but one benchmark for each
# (sub)space with benchmarks (for test runs on StarExec).
def add_solvers(track, filter_benchmarks, select_benchmarks):
    global g_xml_tree
    root = g_xml_tree.getroot()
    incremental_space = root.find('.//Space[@name="incremental"]')
    non_incremental_space = root.find('.//Space[@name="non-incremental"]')
    for space in [incremental_space, non_incremental_space]:
        if space:
            n = 1 # number of benchmarks to keep in each family
            if track == TRACK_MODEL_VALIDATION:
                filter_model_validation_benchmarks(space, select_benchmarks)
                n = 3
            elif track == TRACK_UNSAT_CORE:
                filter_unsat_core_benchmarks(space, select_benchmarks)
            # filter benchmarks
            if filter_benchmarks:
                filter_benchmarks_in_space(space, n, select_benchmarks,"")
            elif select_benchmarks:
                filter_benchmarks_in_space(space, 0, select_benchmarks,"")
            # remove spaces without benchmarks
            remove_empty_spaces(space)
            # add solvers
            subspaces = space.findall('Space')
            for subspace in subspaces:
                division = subspace.attrib['name']
                if division in g_divisions:
                    solvers = g_divisions[division]
                    # Only add solvers if the division is competitive.
                    # Consequently, solvers do not get added to non-competitive
                    # divisions, which are then removed below.
                    if is_competitive(solvers):
                      add_solvers_in_space(subspace, solvers)
            # remove spaces without solvers
            remove_spaces_without_solvers(space)
            # remove top-level non-incremental/incremental space tag
            subspaces = space.findall('Space')
            root.extend(subspaces)
            root.remove(space)


def main():
    global g_args, g_xml_tree
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
                 "'single_query', 'incremental', 'single_query_challenge',"\
                 "'incremental_challenge', 'model_validation', 'unsat_core'",
            required = True)
    parser.add_argument ("-f",
            action="store_true", dest="filter", default=False,
            help="filter space to only keep one (the first) benchmark " \
                  "in each space with benchmarks (for test runs)")
    parser.add_argument("-s","--select",
            action="store",dest="select",default="none",
            help="A list of benchmarks to select", required=False)
    parser.add_argument("-w",
            action="store_true", dest="wrapped", default=False,
            help="use wrapped solver IDs")
    parser.add_argument("-e", metavar="solver_id[,solver_id...]",
                        dest="non_competing",
                        help="list of non-competing solvers (StarExec IDs)")
    g_args = parser.parse_args()

    if not os.path.exists(g_args.space_xml):
        die("file not found: {}".format(g_args.space_xml))
    if not os.path.exists(g_args.csv):
        die("file not found: {}".format(g_args.csv))

    if g_args.track not in ['single_query', 'incremental', 'single_query_challenge',
                          'incremental_challenge', 'model_validation', 'unsat_core']:
        die("invalid track name")
    g_args.track = "track_{}".format(g_args.track)

    if g_args.select != "none":
      read_selected(g_args.select)
      print("selected "+str(len(selected)))

    g_args.non_competing = g_args.non_competing.split(',') \
            if g_args.non_competing else []

    g_xml_tree = ET.parse(g_args.space_xml)
    read_csv(g_args.csv, g_args.track, g_args.wrapped)
    add_solvers(g_args.track, g_args.filter,g_args.select!="none")
    g_xml_tree.write(g_args.out_xml)

    if g_args.select != "none":
      print("there are "+str(len(selected))+" benchmarks unselected")
      for s in selected:
        print(s)

if __name__ == '__main__':
    main()
