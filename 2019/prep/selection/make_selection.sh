#! /bin/bash

OUT_SQ=$1
OUT_INC=$2

SCRIPTDIR=`dirname $(readlink -f "$0")`
SELECT="$SCRIPTDIR/../../../tools/selection/selection.py"

BENCHMARKS_SQ="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_no_challenge.txt"
NEW_SQ_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new_no_challenge.txt"
OLD_SQ_CSV="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"

BENCHMARKS_INC="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_all_no_challenge.txt"
NEW_INC_CSV="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_new_no_challenge.txt"
OLD_INC_CSV="$SCRIPTDIR/../../../2018/csv/Application_Track.csv"

SEED=912681576

python $SELECT --filter "$OLD_SQ_CSV" --benchmarks "$BENCHMARKS_SQ" --new-benchmarks "$NEW_SQ_CSV" -s $SEED --print-stats --out "$OUT_SQ" --prefix "/non-incremental/"
python $SELECT --filter "$OLD_INC_CSV" --benchmarks "$BENCHMARKS_INC" --new-benchmarks "$NEW_INC_CSV" -s $SEED --print-stats --out "$OUT_INC" --prefix "/incremental/"
