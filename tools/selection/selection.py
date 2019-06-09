#!/usr/bin/env python2

import argparse
import csv
import os
import random
import sys

g_args = None

def read_data(data, file_name, verdict):

    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            drow = dict(zip(iter(header), iter(row)))

            benchmark = drow['benchmark']
            solver = drow['solver']
            config = drow['configuration']
            cpu_time = float(drow['cpu time'])
            status = drow['result'].strip()
            expected = drow['expected'].strip()

            if verdict != "any" and expected != verdict:
               continue

            solver_name = '{}_{}'.format(solver, config)

            benchmark_split = benchmark.split('/')
            logic = benchmark_split[0]

            # Required due to how data was run in 2018 and 2017
            if logic in ('Other Divisions', 'Datatype Divisions'):
                logic = benchmark_split[1]
                benchmark = '/'.join(benchmark_split[1:])

            if logic in data:
                solvers = data[logic]
            else:
                solvers = {}
                data[logic] = solvers

            if solver_name in solvers:
                results = solvers[solver_name]
            else:
                results = {}
                solvers[solver_name] = results

            family = '/'.join(benchmark_split[:-1])
            results[(benchmark, family)] = (status, expected, cpu_time)



def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--seed', dest='seed', type=int, help='RNG seed',
                    required=True)
    ap.add_argument('-o', '--old-csv', dest='old_csv',
                    help='CSV containing previous year\'s results',
                    required=True)
    ap.add_argument('-n', '--new-csv', dest='new_csv',
                    help='CSV containing new problems',
                    required=True)
    ap.add_argument('-f', '--filter', dest='filter',
                    action='store_true',
                    default=False,
                    help='Filter out benchmarks based on \'old_csv\' results')
    ap.add_argument('-x', '--out', dest='out',
                    help='Output file name to print selected benchmarks')
    ap.add_argument('-v', '--verdict', dest="verdict", default="any",
                    help="Restrict problems to those with this verdict")
    return ap.parse_args()


def main():
    global g_args

    g_args = parse_args()

    # Map logics to a dict mapping solvers
    # to {(benchmark, family):(status, expected_status, time)}
    data = {}

    # Set up RNG
    random.seed(g_args.seed)

    # Load data on previous years results and new divisions
    # The new csv file should contain the same columns as we get
    # from StarExec with a solver called NEW but as if we had timed out e.g.
    # x,<logic/family/path>,x,NEW,x,x,x,timeout (wallclock),5000,5000,0,starexec-unknown,unsat
    # the problem is described in the <logic/family/path> bit
    # one could put the correct status as the expected value but this script does not
    # currently use it
    read_data(data, g_args.old_csv, g_args.verdict)
    read_data(data, g_args.new_csv, g_args.verdict)

    # Set time limit for interesting benchmarks. The default here is 1 second.
    time_limit = 1

    # This is used to predict the amount of time the resulting problem
    # selection will take using this number nodes.
    #nodes = 150
    #starexec_time_limit = 1200

    # The rules give the following rules for the number of selected benchmarks
    # (a) If a logic contains < 300 instances, all instances will be selected
    # (b) If a logic contains between 300 and 600, a subset of 300 will be selected
    # (c) If a logic contains > 600 then 50% will be selected
    # The following three variables represent the parameters in these rules so that
    # they can be modified if needed
    lower = 300
    upper = 600
    percent = 0.5

    #================================================================


    # count up the time taken to run all logics
    # this assumes the same number of participants for divisions
    # as in previous years
    #all_time = 0

    for (logic,solvers) in sorted(data.items()):

        # place eligible problems here
        eligible = set()
        new_families = {}

        # map from problem to set of solvers solving it
        solved_by = {}
        #run_in = {}

        # used for statistics
        count = 0
        total = 0

        for (solver,results) in sorted(solvers.items()):
            if solver == "NEW_x":
                for ((prob,fam),(stat,expected,time)) in results.items():
                    count = count+1
                    eligible.add(prob)
                    if fam not in new_families:
                        new_families[fam] = set()
                    new_families[fam].add(prob)
            else:
                total = total + len(results)
                for ((prob,fam),(stat,expected,time)) in results.items():
                    #if prob not in run_in:
                    #  run_in[prob] = 0
                    #run_in[prob] = run_in[prob] + min(time,starexec_time_limit)
                    # It's solved if it has a unsat/sat result, is solved within the time limit
                    # and the solution is sound. We don't check for disagreements on unknowns here
                    if (stat=="unsat" or stat=="sat") \
                            and (time<=time_limit) \
                            and (expected=="starexec-unknown" \
                            or stat==expected):
                        if prob not in solved_by:
                            solved_by[prob] = set()
                        solved_by[prob].add(solver)

        competing_solvers = set(solvers.keys())
        if 'NEW_x' in competing_solvers:
            competing_solvers.remove('NEW_x')
        for (prob,ss) in solved_by.items():
            if g_args.filter:
            # add problem if not all solvers solve it
                if len(ss) < len(competing_solvers):
                    count = count+1
                    eligible.add(prob)
            else:
                count = count+1
                eligible.add(prob)

            # Set to True to print statistics on the reduction acheived by ignoring uninteresting
        if False:
            per = "{0:.2f}".format(100.0 * float(total-count) / float(total))
            print("{}:{}{} {}% removed".format(
                logic.ljust(15),
                str(count).ljust(6),
                ("\t (out of "+str(total)+")").ljust(20),
                per))

        #if count != len(eligible):
        #  print("Something went wrong")
        #  print("count is "+str(count)+" but eligible is "+str(len(eligible)))
        #  sys.exit(0)

        #Perform selection
        # Note that this only really makes sense for particular parameters
        # percent*upper should equal lower

        # This first check would allow us to place a minimum size but for now
        # just ignores 'empty' divisions
        count = len(eligible)
        if count > 0:
            if count <= lower:
                select = count
            elif count > lower and count <= upper:
                select = lower
            else:
                select = int(percent*count)

            #for prob in eligible:
            #  print("Eligible: " + str(prob))

            print("For {} selected {}".format(logic.ljust(15), str(select)))
            selected = set()

            for (fam,problems) in new_families.items():
                select = select-1
                prob = random.choice(tuple(problems))
                eligible.remove(prob)
                selected.add(prob)
                #print("Select "+prob+" from new family "+fam)

            while len(selected) < select:
                prob = random.choice(tuple(eligible))
                eligible.remove(prob)
                selected.add(prob)

            # print selected problems
            if g_args.out != "":
                with open(g_args.out,"w") as f:
                    for prob in selected:
                        f.write(prob+"\n")


if __name__ == '__main__':
    main()
