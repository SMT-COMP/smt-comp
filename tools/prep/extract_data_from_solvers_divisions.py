#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import OrderedDict
import csv
import json

import sys
import os
import re

g_sum_seed = 0
g_submissions = None
g_logics_all = None
g_logics_to_tracks = None

TRACK_SINGLE_QUERY_RAW = 'track_single_query'
TRACK_INCREMENTAL_RAW = 'track_incremental'
TRACK_UNSAT_CORE_RAW = 'track_unsat_core'
TRACK_MODEL_VALIDATION_RAW = 'track_model_validation'
TRACK_CLOUD_RAW = 'track_cloud'
TRACK_PARALLEL_RAW = 'track_parallel'
TRACK_PROOF_EXHIBITION_RAW = 'track_proof_exhibition'

COL_PRELIMINARY_SOLVER_ID = 'Preliminary Solver ID'
COL_SOLVER_ID = 'Solver ID'
COL_SOLVER_NAME = 'Solver Name'

COL_CONTACT = 'Contact'
COL_CONTRIBUTORS = 'Team Members'
COL_CERTIFICATS = 'Certificates'
COL_COMPETING = 'Competing'

# Tracks
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'
COL_PROOF_EXHIBITION_TRACK = 'Proof Exhibition Track'
COL_CLOUD_TRACK = 'Cloud Track'
COL_PARALLEL_TRACK = 'Parallel Track'

COL_CONFIG_ID_SQ = 'Config ID Single Query'

track_raw_names_to_pretty_names = {
        TRACK_SINGLE_QUERY_RAW: COL_SINGLE_QUERY_TRACK,
        TRACK_INCREMENTAL_RAW: COL_INCREMENTAL_TRACK,
        TRACK_UNSAT_CORE_RAW: COL_UNSAT_CORE_TRACK,
        TRACK_MODEL_VALIDATION_RAW: COL_MODEL_VALIDATION_TRACK,
        TRACK_PROOF_EXHIBITION_RAW: COL_PROOF_EXHIBITION_TRACK,
        TRACK_CLOUD_RAW: COL_CLOUD_TRACK,
        TRACK_PARALLEL_RAW: COL_PARALLEL_TRACK
        }

COL_VARIANT_OF = 'Variant Of'
COL_WRAPPER_TOOL = 'Wrapper Tool'
COL_DERIVED_TOOL = 'Derived Tool'

COL_SEED = 'Seed'
COL_SOLVER_HOMEPAGE = 'Solver homepage'
COL_SYS_DESCR_URL = 'System description URL'
COL_SYS_DESCR_NAME = 'System description name'

g_properties = [
            ['solver_name', 'name', COL_SOLVER_NAME],
            ['solver_id', 'preliminaryID', COL_PRELIMINARY_SOLVER_ID],
            ['final_id', 'finalID', COL_SOLVER_ID],
            ['contributors', 'team', COL_CONTRIBUTORS],
            ['variant_of', 'variantOf', COL_VARIANT_OF],
            ['wrapper_tool', 'wrapperTool', COL_WRAPPER_TOOL],
            ['derived_tool', 'derivedTool', COL_DERIVED_TOOL],
            ['competing', 'competing', COL_COMPETING],
            ['seed', 'seed', COL_SEED],
            ['solver_homepage', 'solverHomePage', COL_SOLVER_HOMEPAGE],
            ['system_description_url', 'sysDescrUrl', COL_SYS_DESCR_URL],
            ['system_description_name', 'sysDescrName', COL_SYS_DESCR_NAME]
        ]


# update g_properties to include year-specific fields
def add_properties(year):
    global g_properties, COL_CONFIG_ID_SQ
    if int(year) >= 2022:
        g_properties.insert(3, ['config_id_sq', 'configID_sq', COL_CONFIG_ID_SQ])


# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

# Read divisions from a JSON formatted file.
def read_divisions(fname):
    logics_all=json.load(open(fname))
    logics_to_tracks={}
    for track in logics_all:
        for logic in logics_all[track]:
            if not logic in logics_to_tracks:
                logics_to_tracks[logic] = []
            logics_to_tracks[logic].append(track)
    return (logics_all, logics_to_tracks)

# Read csv with submissions data from solvers_divisions_final.
def read_csv(fname):
    global g_submissions, g_logics_all, g_logics_to_track
    with open(fname) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        g_submissions = dict()

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            submission = dict()
            for (subm_key, md_key, div_key) in g_properties:
                submission[subm_key] = drow[div_key]

            for key in track_raw_names_to_pretty_names.keys():
                pretty_name = track_raw_names_to_pretty_names[key]
                submission[key] = drow[pretty_name].split(';') if pretty_name in drow else []

            if not submission[TRACK_SINGLE_QUERY_RAW] and \
               not submission[TRACK_INCREMENTAL_RAW] and \
               not submission[TRACK_UNSAT_CORE_RAW] and \
               not submission[TRACK_MODEL_VALIDATION_RAW] and\
               not submission[TRACK_PROOF_EXHIBITION_RAW] and\
               not submission[TRACK_CLOUD_RAW] and\
               not submission[TRACK_PARALLEL_RAW]:
                die('Configuration "{}" '\
                    'does not participate in any track'.format(
                        submission['solver_name']))

            g_submissions[submission['solver_name']] = submission

# Converts the structures in g_submission to mds
def write_mds(year, path):
    global g_sum_seed
    for sname in g_submissions:
        s = g_submissions[sname]
        if s['seed']: g_sum_seed += int(s['seed'])

        md_descr = {}

        # Read & convert the properties from g_submissions to the md format
        for (prop_name, repr_name, col_name) in g_properties:
            md_descr[repr_name] = \
                    (prop_name in s) and (s[prop_name] or '') or ''
            if repr_name == "competing":
                md_descr[repr_name] = '\"{}\"'.format(md_descr[repr_name])

        s_logics = {}

        for track in g_logics_all.keys():
            for logic in s[track]:
                if (len(logic) == 0):
                    continue
                if logic not in s_logics:
                    s_logics[logic] = []
                s_logics[logic].append(track)

        def quote(s):
            if (s != "" and s[0] == '"'):
                return s
            else:
                return '"%s"' % s

        attr_fields_str = "\n".join(map(lambda x: '{}: {}'.format(
            x, quote(md_descr[x])), md_descr.keys()))

        logic_fields = []
        for l in s_logics:
            sub_logic_fields = "- name: {}\n  tracks:\n{}".format(
                    l, "\n".join(
                        map(lambda x: "  - {}".format(x), s_logics[l])))
            logic_fields.append(sub_logic_fields)
        logic_fields_str = "\n".join(logic_fields)

        ofile_name = \
                "{}.md".format(s['solver_name']).replace(" ", "_").replace("/", "_")
        outfile = open(os.path.join(path, ofile_name), "w")
        md_str = "---\n"\
                 "layout: participant\n"\
                 "year: {}\n"\
                 "{}\ndivisions:\n{}\n---".format(
                         year, attr_fields_str, logic_fields_str)
        outfile.write(md_str)

def print_div_competitiveness(o_path, canonical):
    global g_submissions
    global g_logics_all

    competitiveness = {}

    for track in g_logics_all:
        if track not in competitiveness.keys():
            competitiveness[track] = {}

        for division in g_logics_all[track]:
            competitiveness[track][division] = set()

    for s in g_submissions:
        if s in canonical:
            s_canon = canonical[s]
        else:
            s_canon = s
        for track in track_raw_names_to_pretty_names.keys():
            for division in g_submissions[s][track]:
                if division == "":
                    continue
                if not division in competitiveness[track]:
                    print("WARNING: Solver %s entered in non-existing division %s in %s"
                          % (s_canon, division, track))
                    continue
                if s_canon not in competitiveness[track][division]:
                    competitiveness[track][division].add(s_canon)

    for track in competitiveness:
        ofile = os.path.join(o_path, track.replace("track_", ""))
        ofd = open(ofile, 'w')

        for division in competitiveness[track]:
            part_set = competitiveness[track][division]

            part_set_filtered = filter(lambda x: g_submissions[x]['competing'] == 'yes', part_set)
            if len(set(part_set_filtered)) <= 1:
                ofd.write("%s\n" % division)
                ofd.write("# %s %s participated %s.\n" %\
                        (division,
                            track_raw_names_to_pretty_names[track], \
                            "by no solver" if len(set(part_set)) == 0 \
                            else "only by " + (", ".join(sorted(set(part_set))))))
        ofd.close()

def read_canon(f):
    canon_to_versions = json.load(open(f))
    canonical = dict()
    for k in canon_to_versions.keys():
        versions = canon_to_versions[k]
        for v in versions:
            if v in canonical:
                die("Solver `%s' indicated as having both `%s' and `%s' "\
                        "as the canonical version."\
                        % (v, canonical[v], k))
            canonical[v] = k

        if k in canonical.keys():
            die("Canonical solver %s is marked as a version of %s" %\
                    canonical[k])
        canonical[k] = k

    return canonical

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Extract csv data from solvers_divisions_final.csv "\
                          "into per-solver .md files for the website. "\
                          "Output competition seed base seed (to which "\
                          "randomness (NYSE index) must still be added. "\
                          "Optionally, identify non-competitive divisions "\
                          "based on the given mapping from solver variants "\
                          "their canonical version.")
    parser.add_argument ("-d", "--divisions", required=True,
            help="a json file with the tracks and divisions (required)")
    parser.add_argument ("solver_divisions",
            help="the main csv from solver registrations")
    parser.add_argument("md_path",
            help="output path for generated .md files for the participants")
    parser.add_argument("year",
            help="the year of the competition")
    parser.add_argument("-c", "--canon",
            default=None,
            help="a json file identifying the variants of a solver as "\
                 "determined by the judges. (requires -n)")
    parser.add_argument("-n", "--non-competing",
            default=None,
            help="the path for the generated output files if --canon is "\
                 "given; these output files suggest which divisions "\
                 "are not competitive and the reasons, one for each track. "\
                 "(requires -c)")

    args = parser.parse_args()

    if not args.canon and args.non_competing:
        die("Missing solver variants json file")
    if not os.path.exists(args.solver_divisions):
        die("File not found: {}".format(args.solver_divisions))
    if not os.path.exists(args.md_path):
        die("Path not found: {}".format(args.md_path))

    add_properties(args.year)
    g_logics_all,g_logics_to_tracks = read_divisions(args.divisions)
    read_csv(args.solver_divisions)

    if args.canon:
        if not os.path.exists(args.canon):
            die("File not found: {}".format(args.canon))
        if not args.non_competing:
            die("Missing output files path")
        if not os.path.exists(args.non_competing):
            os.mkdir(args.non_competing)
        canonical = read_canon(args.canon)
        print_div_competitiveness(args.non_competing, canonical)

    write_mds(args.year, args.md_path)

    print("Seeds (sum mod 2^30): {}".format(g_sum_seed % (2**30)))
