#! /bin/bash

OUT_SPACE_SQ=$1

SCRIPTDIR=`dirname $(readlink -f "$0")`
PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
IN_SPACE_SQ="../non-incremental-space.xml"
BENCHMARKS_SQ="../SMT-LIB_non_incremental_benchmarks_all_no_challenge.txt"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"
SELECT_SQ="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2019_no_strings"
Z3_SQ=24192

python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -w -e $Z3_SQ
