#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import OrderedDict
import json

import sys
import os
import re

import extract_data_from_solvers_divisions as ed

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Extract competitive logics for "\
                    "a track using solvers_divisions_final.csv and the"\
                    "cloud/parallel track definition of competitiveness")
    parser.add_argument ("-d", "--divisions", required=True,
            help="a json file with the tracks and divisions (required)")
    parser.add_argument ("solver_divisions",
            help="the main csv from solver registrations")
    parser.add_argument("-t", "--track", required=True,
            help="solver track, either `cloud' or `parallel'")

    args = parser.parse_args()

    if not os.path.exists(args.solver_divisions):
        ed.die("File not found: {}".format(args.solver_divisions))

    if not args.track in ('cloud', 'parallel'):
        ed.die("Unknown track: %s" % args.track)

    ed.g_logics_all,ed.g_logics_to_tracks = ed.read_divisions(args.divisions)
    ed.read_csv(args.solver_divisions)

    tracknames = {'cloud': ed.TRACK_CLOUD_RAW,\
            'parallel': ed.TRACK_PARALLEL_RAW}

    track = tracknames[args.track]

    trackLogicsSolverNums = dict()
    for solver in ed.g_submissions.keys():
        solverEntry = ed.g_submissions[solver]
        trackLogicsForSolver = solverEntry[track]
        for logic in trackLogicsForSolver:
            if logic == "":
                continue
            if logic in trackLogicsSolverNums:
                trackLogicsSolverNums[logic] += 1
            else:
                trackLogicsSolverNums[logic] = 1
    competitiveLogics = dict()
    for logic in trackLogicsSolverNums:
        n_solvers = trackLogicsSolverNums[logic]
        if n_solvers > 1:
            competitiveLogics[logic] = n_solvers

    print("%s" % ";".join([k for k in competitiveLogics]))

