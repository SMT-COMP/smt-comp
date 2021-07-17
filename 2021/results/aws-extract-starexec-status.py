#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import sys
import os
import re

COL_SMTLIB = "smtlib name"

def die(s):
    print(s)
    sys.exit(1)

def getResults(names, path):
    res = dict()
    for n in names:
        fname = "%s%s" % (path, n)
        with open(fname, "r") as file:
            mo = re.search("\(set-info :status ([^\)]*)", file.read(), re.M)
            status = mo.group(1)
            res[n] = status
    return res

def getSmtlibNames(jobmap_csv):
    l = list()
    with open(jobmap_csv, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            rowDict = dict(zip(iter(header), iter(row)))
            l.append(rowDict[COL_SMTLIB])
    return l

def main():
    parser = ArgumentParser(
            usage = "%s -m <aws-job-map> -p <path-to-smtlib>" %\
            sys.argv[0])
    parser.add_argument("-m", "--aws-job-map",
            help = ("The csv mapping the competition names "\
                    "to smt-lib names"),
            required = True,
            dest = "jobMap")
    parser.add_argument("-p", "--smt-lib",
            help = ("Path to the smtlib root"),
            required = True,
            dest = "smtRoot")

    args = parser.parse_args()

    for f in (args.jobMap, args.smtRoot):
        if not os.path.exists(f):
            die("Path not found: %s." % f)

    names = getSmtlibNames(args.jobMap)

    resDict = getResults(names, args.smtRoot)
    print("benchmark name,status")
    for name in resDict:
        print("%s,%s" % (name, resDict[name]))

if __name__ == '__main__':
    main()
