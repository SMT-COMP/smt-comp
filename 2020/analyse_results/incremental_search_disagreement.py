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
    parser = ArgumentParser(description="Read a list of incremental benchmarks and check their job outputs for disagreements. Report all disagreements as a csv.")

    parser.add_argument("-j", "--jobdir",
            action="store",
            required="true",
            help="The directory containing all Job outputs"
            )

    return parser.parse_args()

def evaluate_benchmark(jobdir, division, family, bench, writer):
    global divisions
    pairids = []
    allresults = []
    maxlen = 0
    for outputfile in glob.glob(str.format(
            "{jobdir}/Job*_output/*Incremental*/{division}/{family}/*/{bench}/*.txt",
            jobdir=jobdir, division=division, family=family, bench=bench)):
        m = re.match(".*/(\d+).txt", outputfile)
        pairids.append(m.group(1))
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
            for (pairid, result) in zip(pairids, column):
                if result == "sat" or result == "unsat":
                    writer.writerow([pairid, str(i), result])

if __name__ == '__main__':
    args = parse_args()

    writer = csv.writer(sys.stdout)
    writer.writerow(["pair id", "query", "result"])
    for line in sys.stdin:
        m = re.match("([^/]*)/(.*)/([^/]*)\n", line)
        evaluate_benchmark(args.jobdir, m.group(1), m.group(2), m.group(3), writer)
