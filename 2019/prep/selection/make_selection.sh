#! /bin/bash

OUT_SQ=$1

SCRIPTDIR=`dirname $(readlink -f "$0")`
SELECT="$SCRIPTDIR/../../../tools/selection/selection.py"
BENCHMARKS_SQ="../SMT-LIB_non_incremental_benchmarks_all_no_challenge.txt"
NEW_SQ_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new_no_challenge.txt"
OLD_SQ_CSV="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"
SEED=912681576

python $SELECT --filter "$OLD_SQ_CSV" --benchmarks "$BENCHMARKS_SQ" --new-benchmarks "$NEW_SQ_CSV" -s $SEED --print-stats --out "$OUT_SQ"
