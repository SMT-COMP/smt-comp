#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_submissions = None

g_logics_all = {
        'track_single_query'     : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        'track_incremental'      : [
            'ABVFP','ALIA','ANIA','AUFNIRA','BV','BVFP','LIA','LRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFBVLIA',
            'QF_AUFBVNIA','QF_AUFLIA','QF_BV','QF_BVFP','QF_FP','QF_LIA',
            'QF_LRA','QF_NIA','QF_UF','QF_UFBV','QF_UFBVLIA','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','UFLRA',
            ],
        'track_challenge'        : [
            'QF_BV (non-incremental)',
            'QF_BV (incremental)',
            'QF_ABV (non-incremental)',
            'QF_ABV (incremental)',
            'QF_AUFBV (non-incremental)',
            'QF_AUFBV (incremental)',
            ],
        'track_unsat_core'       : [
            'ABVFP','ALIA','AUFBVDTLIA','AUFDTLIA','AUFLIA','AUFLIRA','AUFNIA',
            'AUFNIRA','BV','BVFP','FP','LIA','LRA','NIA','NRA','QF_ABV',
            'QF_ABVFP','QF_ALIA','QF_ANIA','QF_AUFBV','QF_AUFLIA','QF_AUFNIA',
            'QF_AX','QF_BV','QF_BVFP','QF_BVFPLRA','QF_DT','QF_FP','QF_FPLRA',
            'QF_IDL','QF_LIA','QF_LIRA','QF_LRA','QF_NIA','QF_NIRA','QF_NRA',
            'QF_RDL','QF_S','QF_SLIA','QF_UF','QF_UFBV','QF_UFIDL','QF_UFLIA',
            'QF_UFLRA','QF_UFNIA','QF_UFNRA','UF','UFBV','UFDT','UFDTLIA',
            'UFDTNIA','UFIDL','UFLIA','UFLRA','UFNIA',
            ],
        'track_model_validation' : ['QF_BV']
        }

g_logics_to_tracks = {}
for track in g_logics_all:
    for logic in g_logics_all[track]:
        if not logic in g_logics_to_tracks:
            g_logics_to_tracks[logic] = []
        g_logics_to_tracks[logic].append(track)

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
COL_CHALLENGE_TRACK = 'Challenge Track'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'

COL_VARIANT_OF = 'Variant Of'
COL_WRAPPER_TOOL = 'Wrapper Tool'
COL_DERIVED_TOOL = 'Derived Tool'

COL_SEED = 'Seed'
COL_SOLVER_HOMEPAGE = 'Solver homepage'
COL_SYS_DESCR_URL = 'System description URL'
COL_SYS_DESCR_NAME = 'System description name'

g_properties = [
            ['username', 'contactEmail', COL_CONTACT],
            ['solver_name', 'name', COL_SOLVER_NAME],
            ['solver_id', 'preliminaryID', COL_PRELIMINARY_SOLVER_ID],
            ['final_id', 'finalID', COL_SOLVER_ID],
            ['contributors', 'contactName', COL_CONTRIBUTORS],
            ['variant_of', 'variantOf', COL_VARIANT_OF],
            ['wrapper_tool', 'wrapperTool', COL_WRAPPER_TOOL],
            ['derived_tool', 'derivedTool', COL_DERIVED_TOOL],
            ['competing', 'competing', COL_COMPETING],
            ['seed', 'seed', COL_SEED],
            ['solver_homepage', 'solverHomePage', COL_SOLVER_HOMEPAGE],
            ['system_description_url', 'sysDescrUrl', COL_SYS_DESCR_URL],
            ['system_description_name', 'sysDescrName', COL_SYS_DESCR_NAME]
        ]

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

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

            submission['track_incremental'] = drow[COL_INCREMENTAL_TRACK].split(';')
            submission['track_model_validation'] = drow[COL_MODEL_VALIDATION_TRACK].split(';')
            submission['track_challenge'] = drow[COL_CHALLENGE_TRACK].split(';')
            submission['track_single_query'] = drow[COL_SINGLE_QUERY_TRACK].split(';')
            submission['track_unsat_core'] = drow[COL_UNSAT_CORE_TRACK].split(';')

            if not submission['track_incremental'] and \
               not submission['track_model_validation'] and \
               not submission['track_single_query'] and \
               not submission['track_unsat_core']:
                die('Configuration "{}" '\
                    'does not participate in any track'.format(
                        submission['solver_name']))

            g_submissions[submission['solver_name']] = submission

# Converts the structures in g_submission to mds
def write_mds(path):
    for sname in g_submissions:
        s = g_submissions[sname]

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

        attr_fields_str = "\n".join(map(lambda x: "{}: {}".format(
            x, md_descr[x]), md_descr.keys()))

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
        md_str = "---\nlayout: participant\n{}\nlogics:\n{}\n---".format(
                attr_fields_str, logic_fields_str)
        outfile.write(md_str)



if __name__ == '__main__':
    parser = ArgumentParser(
            usage="extract_data_from_submission "
                  "<solvers-divisions: csv> "
                  "<mdfile_path: path>\n\n"
                  "Extract csv data from solvers_divisions_final.csv"
                  "into per solver md files for the website")
    parser.add_argument (
            "in_csv", help="input csv")
    parser.add_argument(
            "out_md_path", help="output path for generated md files")
    args = parser.parse_args()

    if not os.path.exists(args.in_csv):
        die("file not found: {}".format(args.in_csv))
    if not os.path.exists(args.out_md_path):
        os.makedirs(args.out_md_path)

    read_csv(args.in_csv)
    write_mds(args.out_md_path)
