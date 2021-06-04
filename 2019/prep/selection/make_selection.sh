#! /bin/bash

OUT_SQ=$1
OUT_INC=$2
OUT_MV=$3
OUT_UC=$4

RATIO=0.5
NUM_LOWER=300

SCRIPTDIR=`dirname $(readlink -f "$0")`
SELECT="$SCRIPTDIR/../../../tools/selection/selection.py"

BENCHMARKS_SQ="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_no_challenge.txt"
NEW_SQ_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new_no_challenge.txt"
FILTER_SQ_CSV="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"

BENCHMARKS_INC="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_all_no_challenge.txt"
NEW_INC_CSV="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_new_no_challenge.txt"
FILTER_INC_CSV="$SCRIPTDIR/../../../2018/csv/Application_Track.csv"

BENCHMARKS_UC="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_unsat.txt"
NEW_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new_unsat.txt"
FILTER_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_status_asserts.csv"

BENCHMARKS_MV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_sat.txt"
NEW_MV_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new_sat.txt"

SEED=912681576

python $SELECT --filter "$FILTER_SQ_CSV" --benchmarks "$BENCHMARKS_SQ" --new-benchmarks "$NEW_SQ_CSV" -s $SEED --print-stats --out "$OUT_SQ" --prefix "/non-incremental/" --ratio $RATIO --min-per-logic $NUM_LOWER
python $SELECT --filter "$FILTER_INC_CSV" --benchmarks "$BENCHMARKS_INC" --new-benchmarks "$NEW_INC_CSV" -s $SEED --print-stats --out "$OUT_INC" --prefix "/incremental/" --ratio $RATIO --min-per-logic $NUM_LOWER
python $SELECT --benchmarks "$BENCHMARKS_MV" --new-benchmarks "$NEW_MV_CSV" -s $SEED --print-stats --out "$OUT_MV" --prefix "/non-incremental/" --ratio $RATIO --min-per-logic $NUM_LOWER
python $SELECT --benchmarks "$BENCHMARKS_UC" --new-benchmarks "$NEW_UC_CSV" -s $SEED --print-stats --out "$OUT_UC" --prefix "/non-incremental/" --unsat "$FILTER_UC_CSV" --ratio $RATIO --min-per-logic $NUM_LOWER
