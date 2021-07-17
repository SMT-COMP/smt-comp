#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import sys
import os

# Columns in the scramble map
COL_SMTLIB_NAME = "smtlib name"
COL_COMPETITION_NAME = "competition name"

# Columns in the status map
COL_BENCHMARK_NAME = "benchmark name"
COL_STATUS = "status"

# Columns in the name->id map
COL_NAME_ID = "solver id"
COL_NAME_SOLVER = "solver name"

# Columns for the final starexec-style result csv
COL_PAIR_ID = "pair id"
COL_BENCHMARK = "benchmark"
COL_BENCHMARK_ID = "benchmark id"
COL_SOLVER = "solver"
COL_SOLVER_ID = "solver id"
COL_CONFIGURATION = "configuration"
COL_CONFIGURATION_ID = "configuration id"
COL_STATUS = "status"
COL_CPU_TIME = "cpu time"
COL_WALLCLOCK_TIME = "wallclock time"
COL_MEMORY_USAGE = "memory usage"
COL_RESULT = "result"
COL_EXPECTED = "expected"

starexec_cols = [
        COL_PAIR_ID, COL_BENCHMARK, COL_BENCHMARK_ID, COL_SOLVER,
        COL_SOLVER_ID, COL_CONFIGURATION, COL_CONFIGURATION_ID,
        COL_STATUS, COL_CPU_TIME, COL_WALLCLOCK_TIME, COL_MEMORY_USAGE,
        COL_RESULT, COL_EXPECTED
    ]

def fixBenchmarkPrefix(benchmark, new_prefix):
    expectedPrefix = "/non-incremental"
    assert benchmark.startswith(expectedPrefix)
    return "%s%s" % (new_prefix, benchmark[len(expectedPrefix):])

def getStarexecResult(time, result):
    if time == "CRASHED":
        return "starexec-unknown"
    if time == "PARSE_ERROR":
        return "starexec-unknown"
    if time == "TIMEOUT":
        return "starexec-unknown"
    if float(time) > 1200:
        return "starexec-unknown"

    if result == "":
        # Empty result should be caught by the cases above
        assert False
    if result == "SATISFIABLE":
        return "sat"
    if result == "UNSATISFIABLE":
        return "unsat"

def getStarexecTime(time):
    if time in ["CRASHED", "PARSE_ERROR"]:
        return str(0.0)
    if time == "TIMEOUT":
        return str(1201.00)
    else:
        return time

def getStarexecStatus(status):
    if status == "unknown":
        return "starexec-unknown"
    else:
        return status

def die(s):
    print(s)
    sys.exit(1)

def printResultsAsStarexec(results_csv, jobMap, statuses, prefix,
        nameMap, competition_prefix):
    rows = list()
    with open(results_csv, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            rowDict = dict(zip(iter(header), iter(row)))

            benchmark_competition = rowDict[COL_BENCHMARK]
            assert benchmark_competition[:len(prefix)] == prefix
            benchmark_competition_stripped = \
                    benchmark_competition[len(prefix):]
            if benchmark_competition_stripped not in jobMap:
                print("Foreign benchmark: %s" %\
                        benchmark_competition_stripped)
                assert False
            d = {
                COL_BENCHMARK:
                fixBenchmarkPrefix(jobMap[benchmark_competition_stripped], competition_prefix),
                COL_SOLVER: rowDict[COL_SOLVER],
                COL_WALLCLOCK_TIME: getStarexecTime(rowDict[COL_WALLCLOCK_TIME]),
                COL_RESULT: getStarexecResult(rowDict[COL_WALLCLOCK_TIME], rowDict[COL_RESULT]),
                COL_STATUS: "complete",
                COL_PAIR_ID: str(-1),
                COL_BENCHMARK_ID: str(-1),
                COL_SOLVER_ID: nameMap[rowDict[COL_SOLVER]],
                COL_CONFIGURATION: "default",
                COL_CONFIGURATION_ID: str(-1),
                COL_CPU_TIME: str(-1),
                COL_MEMORY_USAGE: str(-1),
                COL_EXPECTED: getStarexecStatus(statuses[jobMap[benchmark_competition_stripped]])
            }
            rows.append(",".join(map(lambda x: d[x], starexec_cols)))

    print(",".join(starexec_cols))
    print("\n".join(rows))

def readMap(jobMap):
    outMap = dict()

    with open(jobMap, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            rowDict = dict(zip(iter(header), iter(row)))
            compName = rowDict[COL_COMPETITION_NAME]
            smtlibName = rowDict[COL_SMTLIB_NAME]
            assert compName not in outMap
            outMap[compName] = smtlibName
    return outMap

def readStatuses(statuses):
    outMap = dict()

    with open(statuses, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            rowDict = dict(zip(iter(header), iter(row)))
            smtlibName = rowDict[COL_BENCHMARK_NAME]
            smtlibStatus = rowDict[COL_STATUS]
            outMap[smtlibName] = smtlibStatus

    return outMap

def readNames(names):
    outMap = dict()

    with open(names, "r") as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            rowDict = dict(zip(iter(header), iter(row)))
            solverName = rowDict[COL_NAME_SOLVER]
            solverId = rowDict[COL_NAME_ID]
            outMap[solverName] = solverId

    return outMap

def main():
    parser = ArgumentParser(
            usage = "%s -r <aws-result-csv> -m <aws-job-map> "\
                    "-s <instance-statuses> -p <prefix> -n <name-id-map>" % sys.argv[0])
    parser.add_argument("-r", "--aws-result-csv",
            help = "The csv containing the results from aws",
            required = True,
            dest = "awsResults")

    parser.add_argument("-m", "--aws-job-map",
            help = "The csv mapping the competition names "\
                    "to smt-lib names",
            required = True,
            dest = "jobMap")
    parser.add_argument("-s", "--job-statuses",
            help = "The smtlib statuses of the jobs as a csv",
            required = True,
            dest = "statuses")
    parser.add_argument("-p", "--prefix",
            help = "Prefix to be removed from the competition names",
            required = True,
            dest = "prefix")

    parser.add_argument("-n", "--name-to-id",
            help = "A csv file mapping the name used in the run to the"\
            "id appearing in registration",
            required = True,
            dest = "names")

    parser.add_argument("-q", "--competition-prefix",
            help = "Prefix to insert into the smtlib names to indicate"\
            "the track",
            required = True,
            dest = "competitionPrefix")

    args = parser.parse_args()

    for f in (args.awsResults, args.jobMap, args.statuses):
        if not os.path.exists(f):
            die("file not found: %s." % f)

    jobMap = readMap(args.jobMap)
    statuses = readStatuses(args.statuses)
    nameMap = readNames(args.names)

    printResultsAsStarexec(args.awsResults, jobMap, statuses,
            args.prefix, nameMap, args.competitionPrefix)

if __name__ == '__main__':
    main()
