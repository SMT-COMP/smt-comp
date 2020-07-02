#!/usr/bin/env python3

import csv
import sys
import os
import glob
import re
from argparse import ArgumentParser
import datetime

divisions = dict()

def parse_args():
    parser = ArgumentParser(description="Read a list of incremental benchmarks and check their job outputs for disagreements. Report all disagreements in result files.")

    parser.add_argument("-j", "--jobdir",
            action="store",
            required="true",
            help="The directory containing all Job outputs"
            )

    parser.add_argument("-o", "--outdir",
            action="store",
            required="true",
            help="Where to place the .mds"
            )

    return parser.parse_args()

def evaluate_benchmark(jobdir, division, family, bench):
    global divisions
    solvers = []
    allresults = []
    maxlen = 0
    for outputfile in glob.glob(str.format(
            "{jobdir}/Job*_output/*Incremental*/{division}/{family}/*/{bench}/*.txt",
            jobdir=jobdir, division=division, family=family, bench=bench)):
        m = re.match(".*/([^/]*)___[^/]*/.*", outputfile)
        solvers.append(m.group(1))
        results = []
        with open(outputfile, "r") as output:
            for line in output:
                m = re.match("^\d+\.\d+/\d+\.\d+\t(sat|unsat)$", line)
                if m:
                    results.append(m.group(1))
                else:
                    results.append("unknown")
        allresults.append(results)
        maxlen = max(maxlen, len(results))
    if not allresults:
        return
    for i in range(1,maxlen):
        column = [result[i-1] if i <= len(result) else "unknown" for result in allresults]
        if ("sat" in column) and ("unsat" in column):
            divergingresults = dict()
            for (solver, result) in zip(solvers, column):
                if result == "sat" or result == "unsat":
                    divergingresults[solver] = result
            if not division in divisions:
                divisions[division] = dict()
            fullpath = family + "/" + bench + " query " + str(i)
            divisions[division][fullpath] = divergingresults

if __name__ == '__main__':
    args = parse_args()

    for line in sys.stdin:
        m = re.match("([^/]*)/(.*)/([^/]*)\n", line)
        evaluate_benchmark(args.jobdir, m.group(1), m.group(2), m.group(3))

    for div in divisions:
        ostr_list = []
        ostr_list.append("---")
        ostr_list.append("layout: disagreements")
        ostr_list.append("year: 2020")
        ostr_list.append("gendate: %s" % datetime.datetime.now())
        ostr_list.append("track: track_single_query")
        ostr_list.append("participants: participants_2020")
        ostr_list.append("division: %s" % div)
        ostr_list.append("benchmarks:")
        for bm in divisions[div]:
            ostr_list.append("- name: %s" % bm)
            ostr_list.append("- jobs:")
            for solver in divisions[div][bm]:
                ostr_list.append("  - name: %s" % (solver))
                ostr_list.append("    result: %s" % divisions[div][bm][solver])
        ostr_list.append("---")
        open(os.path.join(args.outdir, "%s-incremental.md" % div),
                'w').write("\n".join(ostr_list))
