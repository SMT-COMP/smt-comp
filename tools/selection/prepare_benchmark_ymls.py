#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import sys
import os
import re

def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

SMTLIB_DESCR_TEMPLATE = "http://smtlib.cs.uiowa.edu/logics.shtml#%s"

TRACK_SINGLE_QUERY_RAW = 'track_single_query'
TRACK_INCREMENTAL_RAW = 'track_incremental'
TRACK_SINGLE_QUERY_CHALLENGE_RAW = 'track_single_query_challenge'
TRACK_INCREMENTAL_CHALLENGE_RAW = 'track_incremental_challenge'
TRACK_UNSAT_CORE_RAW = 'track_unsat_core'
TRACK_MODEL_VALIDATION_RAW = 'track_model_validation'

# Tracks
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_CHALLENGE_TRACK_SINGLE_QUERY = 'Challenge Track (single query)'
COL_CHALLENGE_TRACK_INCREMENTAL = 'Challenge Track (incremental)'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'

track_raw_names_to_pretty_names = {
        TRACK_SINGLE_QUERY_RAW: COL_SINGLE_QUERY_TRACK,
        TRACK_INCREMENTAL_RAW: COL_INCREMENTAL_TRACK,
        TRACK_SINGLE_QUERY_CHALLENGE_RAW: COL_CHALLENGE_TRACK_SINGLE_QUERY,
        TRACK_INCREMENTAL_CHALLENGE_RAW: COL_CHALLENGE_TRACK_INCREMENTAL,
        TRACK_UNSAT_CORE_RAW: COL_UNSAT_CORE_TRACK,
        TRACK_MODEL_VALIDATION_RAW: COL_MODEL_VALIDATION_TRACK,
        }

usage_str = """
Produce the md files for the divisions directory on the smt-comp site that
shows the number of selected benchmarks.
"""

# Read divisions from a JSON formatted file.
def read_divisions(fname):
    return json.load(open(fname))

def fillLogic(logic_data, track, bm_files, noncomp_files):
    print("Filling logic_data for track %s using benchmark files `%s'"\
            " and non-competitive division files `%s'" % \
            (track, " ".join(bm_files), " ".join(noncomp_files)))

    for bm_file in bm_files:
        rows = open(bm_file).readlines()
        for row in rows:
            els = row.split('/')

            if len(els) == 1:
                continue # empty line

            logic_data[(els[2])][track][0] += 1

    for noncomp_file in noncomp_files:
        noncomp_rows = open(noncomp_file).readlines()
        for div in noncomp_rows:
            if div[0] == '#':
                comment = div.split()
                if comment[1] in logic_data:
                    # Comments where first word is a logic name comment
                    # on this track's logic
                    logic_data[comment[1]][track][3].append(div[1:].strip())
            else:
                div = div.strip()
                logic_data[div][track][2] = 'non-competitive'

    return logic_data

def tostring(year, logic_name, logic_el):
    track_str_list = []
    comments = []
    for track in logic_el:
        tr_el = logic_el[track]
        track_str_list.append(\
                "- name: track_%s\n  n_insts: %d\n  n_excluded: %d\n" \
                "  status: %s"
                % (track, tr_el[0], tr_el[1], tr_el[2]))
        for i in range(0, len(tr_el[3])):
            comments.append(tr_el[3][i])
    yaml_str = """---
layout: division
year: %d
division: %s
description: %s
tracks:
%s
---
%s
""" % (year, logic_name, SMTLIB_DESCR_TEMPLATE % logic_name, \
        "\n".join(track_str_list), "\n".join(comments))
    return yaml_str

def printYaml(year, logic_name, logic_el, path):

    p = os.path.join(path, "%s.md" % logic_name)
    s = tostring(year, logic_name, logic_el)
    open(p, 'w').write(s)

if __name__ == '__main__':
    tracks = list(map(lambda x: x.replace('track_', ''), track_raw_names_to_pretty_names.keys()))

    parser = ArgumentParser(usage=usage_str)
    parser.add_argument("-d", "--divisions", type=str, required=True,
            help="a json file containing the divisions")
    parser.add_argument("-y", "--year", type=int, required=True,
            help="the competition year")

    for argname in tracks:
        help_str = "A comma separated list of files containing the "\
                "selected %s benchmarks" % \
                track_raw_names_to_pretty_names['track_%s' % argname]
        parser.add_argument("--%s" % argname, metavar="file", type=str,
                dest=argname, help=help_str)

        argname_nc = "%s_noncompetitive" % argname
        hel_str = "A comma separated list of files containing the "\
                "non competitive logics in track %s" % \
                track_raw_names_to_pretty_names['track_%s' % argname]
        parser.add_argument("--%s-noncompetitive" % argname, \
                metavar = "file", type=str, dest=argname_nc, \
                help=help_str)


    parser.add_argument("output_dir", type=str,
            help="directory where the division files should be placed")

    args = parser.parse_args()

    tracks_to_files = {}
    for x in tracks:
        tr_files = eval("args.%s" % x)

        if tr_files == None:
            tr_files = []
        else:
            tr_files = tr_files.split(",")

        tr_nocomp_files = eval("args.%s_noncompetitive" % x)

        if tr_nocomp_files == None:
            tr_nocomp_files = []
        else:
            tr_nocomp_files = tr_nocomp_files.split(",")

        tracks_to_files[x] = (tr_files, tr_nocomp_files)

        for f in tr_files + tr_nocomp_files:
            if not os.path.exists(f):
                die("File not found: {}".format(f))

    if not os.path.exists(args.output_dir):
        die("Path not found: {}".format(args.output_dir))

    logic_data = {}
    all_logics = []
    division_info = read_divisions(args.divisions)
    tracks = list(map(lambda x: x.replace('track_', ''), division_info.keys()))
    for track in division_info:
        all_logics.extend(division_info[track])
    all_logics = set(all_logics)
    for logic in all_logics:
        logic_data[logic] = {}
        for track in tracks:
            logic_data[logic][track] = [0,0,'competitive', []]

    for tr in tracks:
        (bm_files, noncomp_files) = tracks_to_files[tr]
        logic_data = fillLogic(logic_data, tr, bm_files, noncomp_files)

    for logic in all_logics:
        printYaml(args.year, logic, logic_data[logic], args.output_dir)

