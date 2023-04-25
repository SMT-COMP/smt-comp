#!/usr/bin/env python3.8

import sys, csv, re

def run():
    with open(sys.argv[1],"r") as sqStatuses, \
    open("SMT-LIB_non_incremental_benchmarks_all_assertions.csv","r") as original, \
    open("SMT-LIB_non_incremental_benchmarks_all_assertions_sqSolved.csv","w") as result:

        wrt = csv.writer(result)
        original = list(csv.reader(original, delimiter = ','))
        sqStatuses = list(csv.reader(sqStatuses, delimiter = ','))[1:]

        i = 0
        wrt.writerow(original[0] + ["sqSatRes", "sqUnsatRes"])
        original = original[1:]
        for row in original:
            if not row[2] == "unknown":
                wrt.writerow(row + ["0", "0"])
                continue
            solved = list(filter(lambda x : x[0] == row[0], sqStatuses))
            if not solved:
                wrt.writerow(row + ["0", "0"])
                continue
            assert(len(solved) == 1)
            solved = solved[0][1].split(";")
            wrt.writerow(row + [solved.count("sat"), solved.count("unsat")])

if __name__ == '__main__':
    run ()
