#! /bin/bash -eu

TESTING=0

if [ $TESTING == 1 ]; then
    mkdir -p testing

    # use last year's seed
    SEED=332349782

    OUT_SQ="testing/benchmark_selection_single_query"
    OUT_INC="testing/benchmark_selection_incremental"
    OUT_MV="testing/benchmark_selection_model_validation"
    OUT_UC="testing/benchmark_selection_unsat_core"

    RATIO=0.01
    NUM_LOWER=5
else
    mkdir -p final

    SEED=$(cat ../../COMPETITION_SEED)

    OUT_SQ="final/benchmark_selection_single_query"
    OUT_INC="final/benchmark_selection_incremental"
    OUT_MV="final/benchmark_selection_model_validation"
    OUT_UC="final/benchmark_selection_unsat_core"

    RATIO=0.5
    NUM_LOWER=300
fi

echo "Seed: $SEED"

SCRIPTDIR=`dirname $(readlink -f "$0")`
SELECT="$SCRIPTDIR/../../../tools/selection/selection.py"

BENCHMARKS_SQ="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_SQ_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_SQ_CSV_2018="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"
FILTER_SQ_CSV_2019="$SCRIPTDIR/../../../2019/results/Single_Query_Track.csv"
FILTER_SQ_CSV_2020="$SCRIPTDIR/../../../2020/results/Single_Query_Track.csv"

BENCHMARKS_INC="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_all.txt"
NEW_INC_CSV="$SCRIPTDIR/../SMT-LIB_incremental_benchmarks_new.txt"

BENCHMARKS_UC="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_UC_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_assertions.csv"

BENCHMARKS_MV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
NEW_MV_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_new.txt"
FILTER_MV_CSV="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all_assertions.csv"

# Note that python2 and python3 disagree on random choice function.
# Always use python3 to get reproducible results.
PYTHON=python3

printf "MV TRACK\n\n"
$PYTHON $SELECT --benchmarks "$BENCHMARKS_MV" --new-benchmarks "$NEW_MV_CSV" -s $SEED --print-stats --out "$OUT_MV" --prefix "/non-incremental/" --logic "QF_BV;QF_LIA;QF_LRA;QF_LIRA;QF_RDL;QF_IDL;QF_UF;QF_UFBV;QF_UFIDL;QF_UFLRA;QF_UFLIA" --sat "$FILTER_MV_CSV" --ratio $RATIO --min-per-logic $NUM_LOWER

printf "+++++++++++\n\nSQ TRACK\n\n"
$PYTHON $SELECT --filter "$FILTER_SQ_CSV_2020" --filter "$FILTER_SQ_CSV_2019" --filter "$FILTER_SQ_CSV_2018" --benchmarks "$BENCHMARKS_SQ" --new-benchmarks "$NEW_SQ_CSV" -s $SEED --print-stats --out "$OUT_SQ" --prefix "/non-incremental/" --ratio $RATIO --min-per-logic $NUM_LOWER

printf "+++++++++++\n\nINC TRACK\n\n"
$PYTHON $SELECT --benchmarks "$BENCHMARKS_INC" --new-benchmarks "$NEW_INC_CSV" -s $SEED --print-stats --out "$OUT_INC" --prefix "/incremental/" --ratio $RATIO --min-per-logic $NUM_LOWER

printf "+++++++++++\n\nUC TRACK\n\n"
$PYTHON $SELECT --benchmarks "$BENCHMARKS_UC" --new-benchmarks "$NEW_UC_CSV" -s $SEED --print-stats --out "$OUT_UC" --prefix "/non-incremental/" --unsat "$FILTER_UC_CSV" --ratio $RATIO --min-per-logic $NUM_LOWER
