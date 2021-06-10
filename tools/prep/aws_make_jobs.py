#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import csv

import extract_data_from_solvers_divisions as ed

SCRAMBLE_COL='competition name'

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Construct aws jobs from"\
                    "solvers_divisions_final.csv and the benchmark"\
                    "selection scramble file")
    parser.add_argument ("-s", "--selection", required=True,
            help="a csv file with the benchmarks and their "\
                    "scrambled names")
    parser.add_argument ("solver_divisions",
            help="the main csv from solver registrations")
    parser.add_argument("-t", "--track", required=True,
            help="solver track, either `cloud' or `parallel'")

    args = parser.parse_args()

    for path in (args.solver_divisions, args.selection):
        if not os.path.exists(path):
            ed.die("File not found: {}".format(path))

    if not args.track in ('cloud', 'parallel'):
        ed.die("Unknown track: %s" % args.track)

    trackMap = {'cloud': ed.TRACK_CLOUD_RAW,\
            'parallel': ed.TRACK_PARALLEL_RAW}
    track = trackMap[args.track]

    ed.read_csv(args.solver_divisions)

    logicToSolvers = dict()

    for solver in ed.g_submissions.keys():
        solverEntry = ed.g_submissions[solver]
        trackLogicsForSolver = solverEntry[track]
        for logic in trackLogicsForSolver:
            if logic == "":
                continue
            if logic not in logicToSolvers:
                logicToSolvers[logic] = []
            logicToSolvers[logic].append(solver)

    logicToInstances = dict()

    with open(args.selection) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        jobs = dict()

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))
            scrambledName = drow[SCRAMBLE_COL]
            logic = scrambledName.split("/")[2]
            if logic not in logicToInstances:
                logicToInstances[logic] = []

            logicToInstances[logic].append(scrambledName)

    for logic in logicToInstances:
        for solver in logicToSolvers[logic]:
            for instance in logicToInstances[logic]:
                print("%s %s" % (solver, instance))

