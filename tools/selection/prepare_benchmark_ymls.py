#!/usr/bin/env python3

from argparse import ArgumentParser
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

g_logics_all = {
        TRACK_SINGLE_QUERY_RAW     : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        TRACK_INCREMENTAL_RAW      : [
            'ABVFP','ALIA','ANIA','AUFNIRA','BV','BVFP','LIA','LRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFBVLIA',
            'QF_AUFBVNIA','QF_AUFLIA','QF_BV','QF_BVFP','QF_FP','QF_LIA',
            'QF_LRA','QF_NIA','QF_UF','QF_UFBV','QF_UFBVLIA','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','UFLRA',
            ],
        TRACK_SINGLE_QUERY_CHALLENGE_RAW        : [
            'QF_BV',
            'QF_ABV',
            'QF_AUFBV',
            ],
        TRACK_INCREMENTAL_CHALLENGE_RAW        : [
            'QF_BV',
            'QF_ABV',
            'QF_AUFBV',
            ],
        TRACK_UNSAT_CORE_RAW       : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        TRACK_MODEL_VALIDATION_RAW : ['QF_BV']
        }

all_logics = []
for k in g_logics_all:
    for l in g_logics_all[k]:
        all_logics.append(l)

all_logics = set(all_logics)

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

Produce yamls suitable for showing in the web site from lists of files
submitted to starexec.  The file lists are given as arguments specifying
which track they relate to, and contain lines in the form

/non-incremental/ALIA/piVC/piVC_0f7c6a.smt2

Usage:

  $ %s %s

"""

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
            div = div.strip()
            logic_data[div][track][2] = 'non-competitive'

    return logic_data

def tostring(logic_name, logic_el):
    track_str_list = []
    for track in logic_el:
        tr_el = logic_el[track]
        track_str_list.append(\
                "- name: track_%s\n  n_insts: %d\n  n_excluded: %d\n" \
                "  status: %s"
                % (track, tr_el[0], tr_el[1], tr_el[2]))
    yaml_str = """---
layout: logic
division: %s
description: %s
tracks:
%s
---
""" % (logic_name, SMTLIB_DESCR_TEMPLATE % logic_name, "\n".join(track_str_list))
    return yaml_str

def printYaml(logic_name, logic_el, path):

    p = os.path.join(path, "%s.md" % logic_name)
    s = tostring(logic_name, logic_el)
    open(p, 'w').write(s)

if __name__ == '__main__':
    tracks = list(map(lambda x: x.replace('track_', ''), g_logics_all.keys()))

    s = usage_str % (sys.argv[0], sys.argv[0])
    parser = ArgumentParser(usage = s)

    for argname in tracks:
        help_str = "A list of files containing the "\
                "selected %s benchmarks" % \
                track_raw_names_to_pretty_names['track_%s' % argname]
        parser.add_argument("--%s" % argname, metavar="file", type=str,
                nargs='*', dest=argname, help=help_str)

        argname_nc = "%s_noncompetitive" % argname
        hel_str = "A list of files containing the "\
                "non competitive logics in track %s" % \
                track_raw_names_to_pretty_names['track_%s' % argname]
        parser.add_argument("--%s-noncompetitive" % argname, \
                metavar = "file", type=str, nargs='*', dest=argname_nc, \
                help=help_str)


    parser.add_argument("--yaml-path", metavar="path", type=str,
            dest='yaml_path', required=True, help="path where the yaml"\
            "files should be placed")

    args = parser.parse_args()

    tracks_to_files = {}
    for x in tracks:
        tr_files = eval("args.%s" % x)

        if tr_files == None:
            tr_files = []

        tr_nocomp_files = eval("args.%s_noncompetitive" % x)

        if tr_nocomp_files == None:
            tr_nocomp_files = []

        tracks_to_files[x] = (tr_files, tr_nocomp_files)

        for f in tr_files + tr_nocomp_files:
            if not os.path.exists(f):
                die("File not found: {}".format(f))

    if not os.path.exists(args.yaml_path):
        die("Path not found: {}".format(args.yaml_path))

    logic_data = {}
    for logic in all_logics:
        logic_data[logic] = {}
        for track in tracks:
            logic_data[logic][track] = [0,0,'competitive']

    for tr in tracks:
        (bm_files, noncomp_files) = tracks_to_files[tr]
        logic_data = fillLogic(logic_data, tr, bm_files, noncomp_files)

    for logic in all_logics:
        printYaml(logic, logic_data[logic], args.yaml_path)

