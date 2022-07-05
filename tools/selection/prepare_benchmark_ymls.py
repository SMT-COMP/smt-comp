#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import sys
import os
import re
import csv

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
TRACK_PROOF_EXHIBITION_RAW = 'track_proof_exhibition'
TRACK_CLOUD_RAW = 'track_cloud'
TRACK_PARALLEL_RAW = 'track_parallel'

# Tracks
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_CHALLENGE_TRACK_SINGLE_QUERY = 'Challenge Track (single query)'
COL_CHALLENGE_TRACK_INCREMENTAL = 'Challenge Track (incremental)'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'
COL_PROOF_EXHIBITION_TRACK = 'Proof Exhibition Track'
COL_CLOUD_TRACK = 'Cloud Track'
COL_PARALLEL_TRACK = 'Parallel Track'

track_raw_names_to_pretty_names = {
        TRACK_SINGLE_QUERY_RAW: COL_SINGLE_QUERY_TRACK,
        TRACK_INCREMENTAL_RAW: COL_INCREMENTAL_TRACK,
        TRACK_SINGLE_QUERY_CHALLENGE_RAW: COL_CHALLENGE_TRACK_SINGLE_QUERY,
        TRACK_INCREMENTAL_CHALLENGE_RAW: COL_CHALLENGE_TRACK_INCREMENTAL,
        TRACK_UNSAT_CORE_RAW: COL_UNSAT_CORE_TRACK,
        TRACK_MODEL_VALIDATION_RAW: COL_MODEL_VALIDATION_TRACK,
        TRACK_PROOF_EXHIBITION_RAW: COL_PROOF_EXHIBITION_TRACK,
        TRACK_CLOUD_RAW: COL_CLOUD_TRACK,
        TRACK_PARALLEL_RAW: COL_PARALLEL_TRACK,
        }

logic2division = {}

usage_str = """
Produce the md files for the divisions directory on the smt-comp site that
shows the number of selected benchmarks.
"""

# Read divisions from a JSON formatted file.
def read_divisions(fname):
    return json.load(open(fname))

def fillDivision(division_data, track, bm_files, noncomp_files):
    print("Filling division_data for track %s using benchmark files `%s'"\
            " and non-competitive division files `%s'" % \
            (track, " ".join(bm_files), " ".join(noncomp_files)))

    for bm_file in bm_files:
        rows = open(bm_file).readlines()
        for row in rows:
            els = row.split('/')
            if len(els) == 1:
                continue # empty line
            division_data[logic2division[els[2]]][track][3][els[2]][0] += 1
    for noncomp_file in noncomp_files:
        noncomp_rows = open(noncomp_file).readlines()
        for logic in noncomp_rows:
            if logic[0] == '#':
                comment = logic.split()
                if comment[1] in division_data:
                    # Comments where first word is a logic name comment
                    # on this track's logic
                    division_data[logic2division[comment[1]]][track][3][comment[1]][2].append(logic[1:].strip())
            else:
                logic = logic.strip()
                division_data[logic2division[logic]][track][0] = 'non-competitive'

    for division in division_data:
      for track in division_data[division]:
        insts = 0
        excluded = 0
        for logic in division_data[division][track][3]:
          insts += division_data[division][track][3][logic][0]
          excluded += division_data[division][track][3][logic][1]
        division_data[division][track][1] = insts
        division_data[division][track][2] = excluded
    return division_data

def tostring(year, division_name, division_el):
    track_str_list = []
    comments = []
    allLogics = []
    if year < 2021:
      for track in division_el:
        tr_el = division_el[track]
        track_str_list.append(\
                "- name: track_%s\n  n_insts: %d\n  n_excluded: %d\n" \
                "  status: %s"
                % (track, tr_el[1], tr_el[2], tr_el[0]))
        for i in range(0, len(tr_el[3][division_name][2])):
          comments.append(tr_el[3][division_name][2][i])
      yaml_str = """---
layout: division
year: %d
division: %s
description: %s
tracks:
%s
---
%s
""" % (year, division_name, SMTLIB_DESCR_TEMPLATE % division_name, \
         "\n".join(track_str_list), "\n".join(comments))
      return yaml_str
    else:
      for track in division_el:
          tr_el = division_el[track]
          trackStr = \
                  "- name: track_%s\n  status: %s\n" \
                  % (track, tr_el[0])
          trackStr += "  n_insts: " + str(tr_el[1]);
          trackStr += "\n  logic_insts:";
          first = True
          for logic in sorted(tr_el[3]):
            trackStr += "\n  " + ("-" if first else " ")
            first = False
            trackStr += " %s: %s" % (logic, tr_el[3][logic][0])
            allLogics += [logic]
            for i in range(0, len(tr_el[3][logic][2])):
              comments.append(tr_el[3][logic][2][i])
          trackStr += "\n  n_excluded: " + str(tr_el[2]);
          first = True
          trackStr += "\n  logic_excluded:";
          for logic in tr_el[3]:
            trackStr += "\n  " + ("-" if first else " ")
            first = False
            trackStr += " %s: %s" % (logic, tr_el[3][logic][1])
          track_str_list.append(trackStr)
      allLogics = set(allLogics)
      allLogicsStr = ""
      first = True
      for logic in sorted(allLogics):
        allLogicsStr += "\n" + ("-" if first else " ")
        first = False
        allLogicsStr += " %s: %s" % (logic, SMTLIB_DESCR_TEMPLATE % logic)
      yaml_str = """---
layout: division
year: %d
division: %s
logics: %s
tracks:
%s
---
%s
""" % (year, division_name, allLogicsStr, \
       "\n".join(track_str_list), "\n".join(comments))
      return yaml_str

def printYaml(year, division_name, division_el, path):

    p = os.path.join(path, "%s.md" % division_name)
    s = tostring(year, division_name, division_el)
    open(p, 'w').write(s)

if __name__ == '__main__':
    tracks = list(map(lambda x: x.replace('track_', ''), track_raw_names_to_pretty_names.keys()))

    parser = ArgumentParser(usage=usage_str)
    parser.add_argument("-d", "--divisions", type=str, required=True,
            help="a json file containing the divisions")
    parser.add_argument("-y", "--year", type=int, required=True,
            help="the competition year")
    parser.add_argument("-e", "--experimental", type=str, required=True,
            help="a csv files containing experimental divisions")

    for argname in tracks:
        help_str = "A comma separated list of files containing the "\
                "selected %s benchmarks" % \
                track_raw_names_to_pretty_names['track_%s' % argname]
        parser.add_argument("--%s" % argname, metavar="file", type=str,
                dest=argname, help=help_str)

        argname_nc = "%s_noncompetitive" % argname
        help_str = "A comma separated list of files containing the "\
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

    # Dictionary from divisions to tracks to:
    # - status (whether "competitive")
    # - total number of instances
    # - total number of excluded instances
    # - dictionary from logics to
    #   - number of instances
    #   - number of excluded instances
    #   - list of comments on why benchmarks excluded
    division_data = {}
    all_divisions = []
    division_info = read_divisions(args.divisions)
    tracks = list(map(lambda x: x.replace('track_', ''), division_info.keys()))
    for track in division_info:
        trackName = track.replace('track_', '')
        if args.year >= 2021:
            division_logics = division_info[track]
        else:
            # before 2021 every logic was its own division
            division_logics = { logic : [logic]
                                for logic in division_info[track] }

        for division,logics in division_logics.items():
            all_divisions += [division]
            if not division in division_data.keys():
                division_data[division] = {}
            # status, total insts, total excluded, insts/excluded per logic
            division_data[division][trackName] = ["competitive", 0, 0, {}]
            for logic in logics:
                division_data[division][trackName][3][logic] = [0,0,[]]
                logic2division[logic] = division
    all_divisions = set(all_divisions)

    for tr in tracks:
        (bm_files, noncomp_files) = tracks_to_files[tr]
        division_data = fillDivision(division_data, tr, bm_files, noncomp_files)

    if args.experimental:
        with open(args.experimental) as expfile:
            reader = csv.reader(expfile)
            header = next(reader)

            for row in reader:
                drow = dict(zip(iter(header), iter(row)))
                logic = drow['logic']
                track = drow['track']
                division_data[logic2division[logic]][track][0] = 'experimental'

    for division in all_divisions:
        printYaml(args.year, division, division_data[division], args.output_dir)
