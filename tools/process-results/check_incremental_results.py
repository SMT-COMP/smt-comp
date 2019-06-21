#!/usr/bin/env python3

# Check incremental results for discrepancies.
# A discrepancy exists if solvers disagree on a check-sat result. This check
# is necessary for check-sat calls with unknown status (known status calls
# are checked by the incremental post-processor).

from argparse import ArgumentParser
from itertools import zip_longest
from collections import Counter
import csv
import os
import sys

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def main():
    parser = ArgumentParser()
    parser.add_argument ("outputs",
                        help="the directory with StarExec output files")
    args = parser.parse_args()

    if not os.path.exists(args.outputs):
        die("directory not found: {}".format(args.outputs))

    if not os.path.isdir(args.outputs):
        die("directory does not exist: {}".format(args.outputs))

    output_files = dict()
    for (path, dirs, files) in os.walk(args.outputs):
        if files:
            path_split = path.split('/')
            p = "/".join(path_split[:-2])
            solver = path_split[-2]
            benchmark = path_split[-1]
            if p not in output_files:
                output_files[p] = dict()
            for f in files:
                if benchmark not in output_files[p]:
                    output_files[p][benchmark] = []
                output = []
                with open("{}/{}".format(path, f)) as output_file:
                    for line in output_file.readlines():
                        output.append(" ".join(line.split()[1:]))
                output_files[p][benchmark].append([solver, output])

    for p in output_files:
        for benchmark in output_files[p]:
            outputs = []
            for solver,output in output_files[p][benchmark]:
                outputs.append(output)
            zipped = zip_longest(*outputs)
            counts = []
            idx = 0
            for z in zipped:
                counter = Counter(z)
                counts = (counter['sat'], counter['unsat'])
                if counts[0] != 0 and counts[1] != 0:
                    sat = []
                    unsat = []
                    for solver,output in output_files[p][benchmark]:
                        if idx < len(output):
                            if output[idx] == 'sat':
                                sat.append(solver)
                            elif output[idx] == 'unsat':
                                unsat.append(solver)
                    print(">> Path: {}".format(p))
                    print(">> Benchmark: {}".format(benchmark))
                    print("   !!! Discrepancy:")
                    print("       sat:   {}".format("\n              ".join(sat)))
                    print("       unsat: {}".format("\n              ".join(unsat)))
                idx += 1

if __name__ == '__main__':
    main()
