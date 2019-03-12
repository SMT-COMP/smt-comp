#!/bin/bash

set -e
set -u

declare -A SAT
declare -A UNSAT

while IFS="," read JOBID BENCHMARK BENCHMARKID SOLVER SOLVERID CONFIG CONFIGID STATUS X Y Z RESULT EXPECTED; do
    if [ "$RESULT" = "sat" ]; then
        SAT[$BENCHMARKID]=1
    elif [ "$RESULT" = "unsat" ]; then
        UNSAT[$BENCHMARKID]=1
    fi
done < "$1"

while IFS="," read JOBID BENCHMARK BENCHMARKID SOLVER SOLVERID CONFIG CONFIGID STATUS X Y Z RESULT EXPECTED; do
    if [ "$RESULT" = "starexec-unknown" ]; then
        continue
    fi
    if [ ${SAT[$BENCHMARKID]+isset} ]; then
        if [ ${UNSAT[$BENCHMARKID]+isset} ]; then
            echo "$JOBID,$BENCHMARK,$BENCHMARKID,$SOLVER,$SOLVERID,$CONFIG,$CONFIGID,$STATUS,$X,$Y,$Z,$RESULT,$EXPECTED"
        fi
    fi
done < "$1"
