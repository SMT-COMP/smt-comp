#!/bin/bash

set -e
set -u

# print a list of all solvers that have given an incorrect answer
# (together with the respective division)

while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID CONFIG CONFIG_ID STATUS CPU_TIME WALL_TIME MEMORY RESULT WRONG CORRECT
do
    if [[ ("$WRONG" != "0") ]]; then
        DIVISION=${BENCHMARK%%/*}
        echo $DIVISION,$SOLVER,$SOLVER_ID
    fi
done < "$1"|LC_ALL=C sort -u
