#!/bin/bash

set -e
set -u

# print a list of all solvers that have given an incorrect answer
# (together with the respective division)

while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID STATUS RESULT RESULT_ERR REDUCTION
do
    if [[ ("$RESULT" == "sat") ]]; then
        DIVISION=${BENCHMARK%%/*}
        echo $DIVISION,$SOLVER,$SOLVER_ID
    fi
done < "$1"|LC_ALL=C sort -u
