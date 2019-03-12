#!/bin/bash

set -e
set -u

# $1: CSV file containing unsound solvers (DIVISION,SOLVER,SOLVER_ID)
# $2: CSV file containing job pair data

declare -A UNSOUND

while IFS=, read DIVISION SOLVER SOLVER_ID
do
    UNSOUND[$DIVISION,$SOLVER_ID]=1
done < "$1"

while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID REST
do
    DIVISION=${BENCHMARK%%/*}
    if [[ ! ${UNSOUND[$DIVISION,$SOLVER_ID]+isset} ]]; then
        echo $PAIR_ID,$BENCHMARK,$BENCHMARK_ID,$SOLVER,$SOLVER_ID,$REST
    fi
done < "$2"
