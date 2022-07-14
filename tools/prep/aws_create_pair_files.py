#!/usr/bin/env python3

from argparse import ArgumentParser
import csv, re
from sys import stdout
import extract_data_from_solvers_divisions as ed


def process(logics,fname):
    with open(fname) as file:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(stdout, delimiter=',')
        header = next(reader)
        writer.writerow(["solver","input file"])
        for row in reader:
            competition_name = row[1]
            logic = re.search('^/[^/]*/([^/]*)/.*$', competition_name, re.IGNORECASE)
            if logic:
                logic = logic.group(1)
            else:
                exit("error in", competition_name)
            if logic in logics:
                for solver in logics[logic]:
                    writer.writerow([solver,competition_name])
            else:
                exit("error logic",logic,"without solvers")
            stdout.flush()

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Create pair (solver,bechmark) files for aws")
    parser.add_argument ("map_file",
            help="the map_file with the list of selected benchmark with scrambled names")
    parser.add_argument ("solver_divisions",
            help="the main csv from solver registrations")
    parser.add_argument("-t", "--track", required=True,
            help="solver track, either `cloud' or `parallel'")

    args = parser.parse_args()
    ed.read_csv(args.solver_divisions)

    tracknames = {'cloud': ed.TRACK_CLOUD_RAW,\
                  'parallel': ed.TRACK_PARALLEL_RAW}
    track = tracknames[args.track]

    logics=dict()
    for solver in ed.g_submissions.keys():
        solverEntry = ed.g_submissions[solver]
        for logic in solverEntry[track]:
            if logic == "":
                continue
            if logic in logics:
                logics[logic] += [solverEntry["solver_name"]]
            else:
                logics[logic] = [solverEntry["solver_name"]]


    process(logics,args.map_file)
