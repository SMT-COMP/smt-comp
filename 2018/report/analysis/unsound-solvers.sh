#!/bin/bash

set -e
set -u

# print a list of all solvers that have given an incorrect answer
# (together with the respective division)

while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID CONFIG CONFIG_ID STATUS CPU_TIME WALL_TIME MEMORY RESULT EXPECTED
do
    if [[ ("$RESULT" == "sat" && "$EXPECTED" == "unsat") || ("$RESULT" == "unsat" && "$EXPECTED" == "sat") ]]; then
        DIVISION=${BENCHMARK%%/*}
        echo $DIVISION,$SOLVER,$SOLVER_ID
    fi
done < "$1"|LC_ALL=C sort -u
