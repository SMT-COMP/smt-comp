#! /bin/bash

OUT_SQ=$1
OUT_INC=$2
OUT_MV=$3
OUT_UC=$4

SCRIPTDIR=`dirname $(readlink -f "$0")`
SELECT="$SCRIPTDIR/../../../tools/selection/selection.py"

BENCHMARKS_SQ="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_SQ_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_SQ_CSV_2018="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"
FILTER_SQ_CSV_2019="$SCRIPTDIR/../../../2019/results/Single_Query_Track.csv"

BENCHMARKS_INC="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_all_filtered.txt"
NEW_INC_CSV="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_new_filtered.txt"
FILTER_INC_CSV_2018="$SCRIPTDIR/../../../2018/csv/Application_Track.csv"
FILTER_INC_CSV_2019="$SCRIPTDIR/../../../2019/results/Incremental_Track.csv"

BENCHMARKS_UC="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_assertions.csv"

BENCHMARKS_MV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_MV_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_MV_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_assertions.csv"

SEED=0

printf "MV TRACK\n\n"
python $SELECT --benchmarks "$BENCHMARKS_MV" --new-benchmarks "$NEW_MV_CSV" -s $SEED --print-stats --out "$OUT_MV" --prefix "/non-incremental/" --logic "QF_BV;QF_LIA;QF_LRA;QF_LIRA;QF_RDL;QF_IDL" --sat "$FILTER_MV_CSV"

printf "+++++++++++\n\nSQ TRACK\n\n"
python $SELECT --filter "$FILTER_SQ_CSV_2019" --filter "$FILTER_SQ_CSV_2018" --benchmarks "$BENCHMARKS_SQ" --new-benchmarks "$NEW_SQ_CSV" -s $SEED --print-stats --out "$OUT_SQ" --prefix "/non-incremental/"

printf "+++++++++++\n\nINC TRACK\n\n"
python $SELECT --benchmarks "$BENCHMARKS_INC" --new-benchmarks "$NEW_INC_CSV" -s $SEED --print-stats --out "$OUT_INC" --prefix "/incremental/"

printf "+++++++++++\n\nUC TRACK\n\n"
python $SELECT --benchmarks "$BENCHMARKS_UC" --new-benchmarks "$NEW_UC_CSV" -s $SEED --print-stats --out "$OUT_UC" --prefix "/non-incremental/" --unsat "$FILTER_UC_CSV"
