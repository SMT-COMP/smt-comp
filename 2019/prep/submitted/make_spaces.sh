#! /bin/bash

OUT_SPACE_SQ=$1
OUT_SPACE_CHALL_NON_INC=$2
OUT_SPACE_CHALL_INC=$3
OUT_SPACE_INC=$4
OUT_SPACE_MV=$5
OUT_SPACE_SQ_ONLY=$6
OUT_SPACE_CHALL_NON_INC_ONLY=$7

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

IN_SPACE_MV="../non-incremental-space.xml"
SELECT_MV="$SCRIPTDIR/../selection/model_validation/benchmark_selection_model_validation_2019"

IN_SPACE_CHALL_NON_INC="../non-incremental-space.xml"
SELECT_CHALL_NON_INC="$SCRIPTDIR/../selection/challenge-non-incremental/benchmark_selection_challenge_non-incremental_2019"

IN_SPACE_CHALL_INC="../incremental-space.xml"
SELECT_CHALL_INC="$SCRIPTDIR/../selection/challenge-incremental/benchmark_selection_challenge_incremental_2019"

IN_SPACE_SQ="../non-incremental-space.xml"
SELECT_SQ="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2019_no_strings"

IN_SPACE_INC="../incremental-space.xml"
SELECT_INC="$SCRIPTDIR/../selection/incremental/benchmark_selection_incremental_2019"

NON_COMPETITIVE_SQ="24192,24193,24160"  # Z3,Boolector-ReasonLS,CVC4-SymBreak
NON_COMPETITIVE_CHALL_NON_INC="24192"   # Z3
NON_COMPETITIVE_CHALL_INC="24017"       # Z3
NON_COMPETITIVE_INC="24017,23970"       # Z3,Boolector-ReasonLS

ONLY_SOLVERS_SQ="24281,24282"           # STP-mergesat-fixed,STP-portfolio-fixed

# Single Query Track
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -w -e $NON_COMPETITIVE_SQ

# Challenge Track non-incremental
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w -e $NON_COMPETITIVE_CHALL_NON_INC

# Challenge Track incremental
python $PREPARE "$IN_SPACE_CHALL_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC" -t incremental_challenge --select "$SELECT_CHALL_INC" -w -e $NON_COMPETITIVE_CHALL_INC

# Incremental Track
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" -t incremental --select "$SELECT_INC" -w -e $NON_COMPETITIVE_INC

# Single Query Track
python $PREPARE "$IN_SPACE_MV" "$SOLVERS_CSV" "$OUT_SPACE_MV" -t model_validation --select "$SELECT_MV" -w

# Single Query Track - fixed STP versions
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ_ONLY" -t single_query --select "$SELECT_SQ" -w -e $NON_COMPETITIVE_SQ --only-solvers $ONLY_SOLVERS_SQ

# Challenge Track non-incremental - fixed STP versions
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_ONLY" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w -e $NON_COMPETITIVE_CHALL_NON_INC --only-solvers $ONLY_SOLVERS_SQ
