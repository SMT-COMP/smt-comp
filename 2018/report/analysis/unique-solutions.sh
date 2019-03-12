#!/bin/bash

set -e
set -u

# number of unique solutions (for groups of solvers)

# $1: solver-groups.txt
# $2: CSV file

declare -A SOLVERGROUPS # maps solver IDs to solver (group) names
declare -A BENCHMARKS   # maps benchmark IDs to solver (group) names
declare -A UNIQUES      # maps benchmark IDs to 1 iff the benchmark was uniquely solved
declare -A SOLUTIONS    # maps solver (group) names to their number of unique solutions

# build reverse index from solver IDs to solver (group) names
while read SOLVER SOLVER_IDS
do
    for ID in $SOLVER_IDS
    do
        SOLVERGROUPS[$ID]="$SOLVER"
    done
done < "$1"

# determine which benchmarks were uniquely solved
while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID CONFIG CONFIG_ID STATUS CPU_TIME WALL_TIME MEMORY RESULT EXPECTED
do
    SOLVERGROUP="${SOLVERGROUPS[$SOLVER_ID]}"
    SOLUTIONS[$SOLVERGROUP]=0
    if [ "$RESULT" != "sat" ] && [ "$RESULT" != "unsat" ]; then
        continue
    fi
    if [ ${BENCHMARKS[$BENCHMARK_ID]+isset} ]; then
        if [ "$SOLVERGROUP" != "${BENCHMARKS[$BENCHMARK_ID]}" ]; then
            unset "UNIQUES[$BENCHMARK_ID]"
        fi
    else
        BENCHMARKS[$BENCHMARK_ID]="$SOLVERGROUP"
        UNIQUES[$BENCHMARK_ID]=1
    fi
done < "$2"

# count each uniquely solved benchmark for the corresponding solver group
for BENCHMARK_ID in ${!UNIQUES[@]}
do
    SOLVERGROUP="${BENCHMARKS[$BENCHMARK_ID]}"
    SOLUTIONS[$SOLVERGROUP]=$(( ${SOLUTIONS[$SOLVERGROUP]} + 1 ))
done

# output results
for SOLVERGROUP in ${!SOLUTIONS[@]}
do
    echo "$SOLVERGROUP,${SOLUTIONS[$SOLVERGROUP]}"
done|sort
