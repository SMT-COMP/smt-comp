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
g_selected = set()

TRACK_SINGLE_QUERY = 'track_single_query'
TRACK_INCREMENTAL = 'track_incremental'
TRACK_SINGLE_QUERY_CHALLENGE = 'track_single_query_challenge'
TRACK_INCREMENTAL_CHALLENGE = 'track_incremental_challenge'
TRACK_UNSAT_CORE = 'track_unsat_core'
TRACK_MODEL_VALIDATION = 'track_model_validation'
TRACK_PROOF_EXHIBITION = 'track_proof_exhibition'

# Solver ID columns
COL_SOLVER_ID_PRELIM = 'Preliminary Solver ID'
COL_SOLVER_ID = 'Solver ID'
COL_CONFIG_ID_SQ = 'Config ID Single Query'
COL_CONFIG_ID_INC = 'Config ID Incremental'
COL_CONFIG_ID_MV = 'Config ID Model Validation'
COL_CONFIG_ID_UC = 'Config ID Unsat Core'
COL_CONFIG_ID_PE = 'Config ID Proof Exhibition'
# Track Columns
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_CHALLENGE_TRACK_SINGLE_QUERY = 'Challenge Track (single query)'
COL_CHALLENGE_TRACK_INCREMENTAL = 'Challenge Track (incremental)'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'
COL_PROOF_EXHIBITION_TRACK = 'Proof Exhibition Track'
# Other Columns
COL_IS_COMPETING = 'Competing'

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
def read_csv():
    global g_divisions, g_args
    track = g_args.track
    if track == TRACK_SINGLE_QUERY:
        col_solver_id = COL_CONFIG_ID_SQ
    elif track == TRACK_INCREMENTAL:
        col_solver_id = COL_CONFIG_ID_INC
    elif track == TRACK_SINGLE_QUERY_CHALLENGE:
        col_solver_id = COL_CONFIG_ID_SQ
    elif track == TRACK_INCREMENTAL_CHALLENGE:
        col_solver_id = COL_CONFIG_ID_INC
    elif track == TRACK_MODEL_VALIDATION:
        col_solver_id = COL_CONFIG_ID_MV
    elif track == TRACK_UNSAT_CORE:
        col_solver_id = COL_CONFIG_ID_UC
    elif track == TRACK_PROOF_EXHIBITION:
        col_solver_id = COL_CONFIG_ID_PE
    with open(g_args.csv) as file:
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
            elif track == TRACK_PROOF_EXHIBITION:
                divisions = drow[COL_PROOF_EXHIBITION_TRACK].split(';')
            assert (divisions)
            if drow[COL_IS_COMPETING] == "no":
                g_args.non_competing.append(solver_id)

            for division in divisions:
                if division == "":
                    continue
                if division not in g_divisions:
                    g_divisions[division] = []
                g_divisions[division].append(
                        [drow[col_solver_id], drow['Solver Name']])

def read_selected(fname):
    global g_selected
    with open(fname) as file:
       for line in file:
         line = line.strip()
         if line:
           g_selected.add(line)

# Traverse space and remove all but one benchmark for each (sub)space with
# benchmarks (for test runs on StarExec).
def filter_benchmarks_in_space(space, select_benchmarks, path):
    path = "{}/{}".format(path, space.attrib['name'])
    spaces = space.findall('Space')
    for s in spaces:
        filter_benchmarks_in_space(s, select_benchmarks, path)
    benchmarks = space.findall('Benchmark')
    if select_benchmarks:
        for b in benchmarks:
            bname = "{}/{}".format(path, b.attrib['name'])
            if bname not in g_selected:
                space.remove(b)
            else:
                g_selected.remove(bname)

# Traverse space and add solvers to divisions and their subspaces.
def add_solvers_in_space(space, solvers):
    global g_args
    spaces = space.findall('Space')
    for s in spaces: add_solvers_in_space(s, solvers)
    included_solvers = g_args.solvers
    excluded_solvers = g_args.excluded_solvers
    for solver in solvers:
        solver_id = solver[0]
        if included_solvers and solver_id not in included_solvers: continue
        if excluded_solvers and solver_id in excluded_solvers: continue
        ET.SubElement(
                space,
                'Solver',
                attrib = {'id': solver[0], 'name': solver[1]})

# Return if a division is competitive based on the list of given solvers.
# Currently, this only considers non-competing solvers as given via '--nc'.
def is_competitive(solvers):
    global g_args
    if g_args.run_noncompetitive:
        return True
    count = len(solvers)
    for nc in g_args.non_competing:
        for s in solvers:
            if nc == s[0]:
                count -= 1
                break
    return count > 1

def add_job_pairs(job, path, space, solvers):
    jobpath = path + "/" + space.attrib['name']
    for benchmark in space.findall('Benchmark'):
        benchname = benchmark.attrib['name']
        benchid = benchmark.attrib['id']

        for solver in solvers:
            ET.SubElement(job, 'JobPair',
                          attrib={'bench-id': benchid,
                                  'bench-name': benchname,
                                  'config-id': solver[0],
                                  'solver-name': solver[1],
                                  'job-space-path': jobpath})
    for subspace in space.findall('Space'):
        add_job_pairs(job, jobpath, subspace, solvers)

def build_job():
    global g_xml_tree, g_args
    root = ET.fromstring('''\
<?xml version="1.0" encoding="UTF-8"?>
<tns:Jobs xmlns:tns="https://www.starexec.org/starexec/public/batchJobSchema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.starexec.org/starexec/public/batchJobSchema.xsd batchJobSchema.xsd">
</tns:Jobs>''')
    job = ET.SubElement(root, 'Job', attrib = { 'name': g_args.jobname })
    jobattributes = ET.SubElement(job, 'JobAttributes')
    ET.SubElement(jobattributes, 'description',
                  attrib = { 'value': "no description" })
    ET.SubElement(jobattributes, 'queue-id',
                  attrib = { 'value': str(g_args.queue_id) })
    ET.SubElement(jobattributes, 'bench-framework',
                  attrib = { 'value': "runsolver" })
    ET.SubElement(jobattributes, 'start-paused',
                  attrib = { 'value': "true" })
    ET.SubElement(jobattributes, 'cpu-timeout',
                  attrib = { 'value': str(4 * g_args.timeout) })
    ET.SubElement(jobattributes, 'wallclock-timeout',
                  attrib = { 'value': str(g_args.timeout) })
    ET.SubElement(jobattributes, 'seed',
                  attrib = { 'value': str(g_args.seed) })
    ET.SubElement(jobattributes, 'mem-limit',
                  attrib = { 'value': g_args.memlimit })
    ET.SubElement(jobattributes, 'postproc-id',
                  attrib = { 'value': str(g_args.postprocessor) })
    ET.SubElement(jobattributes, 'preproc-id',
                  attrib = { 'value': str(g_args.preprocessor) })

    spaceroot = g_xml_tree.getroot()
    incremental_space = spaceroot.find('.//Space[@name="incremental"]')
    non_incremental_space = spaceroot.find('.//Space[@name="non-incremental"]')
    select_benchmarks = g_args.select != 'none'
    for space in [incremental_space, non_incremental_space]:
        if space is not None:
            n = 1 # number of benchmarks to keep in each family
            # filter benchmarks
            if select_benchmarks:
                filter_benchmarks_in_space(space, select_benchmarks,"")
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
                        included_solvers = g_args.solvers
                        excluded_solvers = g_args.excluded_solvers
                        if included_solvers:
                            solvers = [ id for id in solvers if id in included_solvers ]
                        if excluded_solvers:
                            solvers = [ id for id in solvers if id not in excluded_solvers ]
                        add_job_pairs(job, g_args.track, subspace, solvers)
                    else:
                        print("Removing division {} without enough competitive solvers".format(division))
    return root

def main():
    global g_args, g_xml_tree
    parser = ArgumentParser(
            usage="prepare_space_xml "\
                  "-t <track> "\
                  "--name <job name> "\
                  "--queue <starexec queue id> "\
                  "--pre <pre-processor id> --post <post-processor id> "\
                  "--wall <wallclock-timeout> --seed <seed> "\
                  "--memlimit <memory limit> "\
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
                 "'incremental_challenge', 'model_validation', 'unsat_core',"\
                 "'proof_exhibition'",
            required = True)  
    parser.add_argument('--name',
                        type=str, dest="jobname",
                        help="Name of the job",
                        required = True)
    parser.add_argument('--queue',
                        type=int, dest="queue_id",
                        help="Starexec queue id, e.g., 1 for all.q",
                        required = True)
    parser.add_argument('--pre',
                        type=int, dest="preprocessor",
                        help="Pre-processor ID",
                        required = True)
    parser.add_argument('--post',
                        type=int, dest="postprocessor",
                        help="Post-processor ID",
                        required = True)
    parser.add_argument('--wall',
                        type=int, dest="timeout",
                        help="Wall-clock timeout",
                        required = True)
    parser.add_argument('--memlimit',
                        type=str, dest="memlimit",
                        help="Memory Limit in GB",
                        required = True)
    parser.add_argument('--seed',
                        type=int, dest="seed",
                        help="Competition seed for scrambling",
                        required = True)
    parser.add_argument("-s","--select",
            action="store",dest="select",default="none",
            help="A list of benchmarks to select", required=False)
    parser.add_argument("-p",
            action="store_true", dest="preliminary", default=False,
            help="use preliminary solver IDs")
    parser.add_argument("--nc", metavar="solver_id[,solver_id...]",
                        dest="non_competing",
                        help="list of non-competing solvers (StarExec IDs)")
    parser.add_argument("--solvers", metavar="solver_id[,solver_id...]",
                        dest="solvers",
                        help="generate space including only the listed "\
                             "solvers (StarExec IDs, config IDs)")
    parser.add_argument("--exclude-solvers", metavar="solver_id[,solver_id...]",
                        dest="excluded_solvers",
                        help="generate space excluding the listed "\
                             "solvers (StarExec IDs, config IDs)")
    parser.add_argument("--include-non-competitive",
                        default=False,
                        dest="run_noncompetitive",
                        action="store_true",
                        help="include non-competitive divisions")
    g_args = parser.parse_args()

    if not os.path.exists(g_args.space_xml):
        die("file not found: {}".format(g_args.space_xml))
    if not os.path.exists(g_args.csv):
        die("file not found: {}".format(g_args.csv))

    if g_args.track not in ['single_query', 'incremental', 'single_query_challenge',
                            'incremental_challenge', 'model_validation', 'unsat_core',
                            'proof_exhibition']:
        die("invalid track name")
    g_args.track = "track_{}".format(g_args.track)

    if g_args.select != "none":
        read_selected(g_args.select)
        print("selected {}".format(len(g_selected)))

    g_args.non_competing = g_args.non_competing.split(',') \
            if g_args.non_competing else []

    g_args.solvers = g_args.solvers.split(',') \
            if g_args.solvers else []

    g_args.excluded_solvers = g_args.excluded_solvers.split(',') \
            if g_args.excluded_solvers else []

    g_xml_tree = ET.parse(g_args.space_xml)
    read_csv()
    job_xml_tree = build_job()
    with open(g_args.out_xml, "wb") as f:
        f.write(ET.tostring(job_xml_tree))

    if g_args.select != "none" and len(g_selected) > 0:
        for s in g_selected:
            print(s)
        print(f"We did not find {len(g_selected)} benchmarks!")

if __name__ == '__main__':
    main()
