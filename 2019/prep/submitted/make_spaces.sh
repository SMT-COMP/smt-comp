#! /bin/bash

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

NON_COMPETITIVE_SOLVERS_SQ="24192,24193,24160"  # Z3,Boolector-ReasonLS,CVC4-SymBreak
NON_COMPETITIVE_SOLVERS_CHALL_NON_INC="24192"   # Z3
NON_COMPETITIVE_SOLVERS_CHALL_INC="24017"       # Z3
NON_COMPETITIVE_SOLVERS_INC="24017,23970"       # Z3,Boolector-ReasonLS

FIXED_SOLVERS_SQ="24281,24282"          # STP-mergesat-fixed,STP-portfolio-fixed

OUT_SPACE_SQ=
OUT_SPACE_CHALL_NON_INC=
OUT_SPACE_CHALL_INC=
OUT_SPACE_INC=
OUT_SPACE_MV=
OUT_SPACE_SQ_FIXED=
OUT_SPACE_CHALL_NON_INC_FIXED=

while [ $# -gt 0 ]
do
  case $1 in
    -h|--help)
      echo -n "usage: $(basename $0) [<option>]"
      echo
      echo "Generate StarExec competition spaces."
      echo
      echo "  options:"
      echo "    -h, --help          print this message and exit"
      echo "    --sq <file>         Single Query track output xml"
      echo "    --inc <file>        Incremental track output xml"
      echo "    --csq <file>        Challenge track non-incremental output xml"
      echo "    --cinc <file>       Challenge track incremental output xml"
      echo "    --uc <file>         Unsat Core track output xml"
      echo "    --mv <file>         Model Validation track output xml"
      echo "    --sq-fixed <file>   Single Query track output xml for fixed"
      echo "                        (non-competing) solvers"
      echo "    --csq-fixed <file>  Challenge track non-incremental output xml"
      echo "                        for fixed (non-competing) solvers"
      echo
      exit
      ;;
    --sq)
      shift
      OUT_SPACE_SQ=$1
      ;;
    --inc)
      shift
      OUT_SPACE_INC=$1
      ;;
    --csq)
      shift
      OUT_SPACE_CHALL_NON_INC=$1
      ;;
    --cinc)
      shift
      OUT_SPACE_CHALL_INC=$1
      ;;
    --uc)
      ;;
    --mv)
      shift
      OUT_SPACE_MV=$1
      ;;
    --sq-fixed)
      shift
      OUT_SPACE_SQ_FIXED=$1
      ;;
    --csq-fixed)
      shift
      OUT_SPACE_CHALL_NON_INC_FIXED=$1
      ;;
    -*)
        echo "ERROR: invalid option '$1'"
        exit 1
      ;;
    *)
      break
  esac
  shift
done

# Single Query Track
[[ -n $OUT_SPACE_SQ ]] && \
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --exclude-solvers $FIXED_SOLVERS_SQ

# Challenge Track non-incremental
[[ -n $OUT_SPACE_CHALL_NON_INC ]] && \
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --exclude-solvers $FIXED_SOLVERS_SQ

# Challenge Track incremental
[[ -n $OUT_SPACE_CHALL_INC ]] && \
python $PREPARE "$IN_SPACE_CHALL_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC" -t incremental_challenge --select "$SELECT_CHALL_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC

# Incremental Track
[[ -n $OUT_SPACE_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC

# Model Validation Track
[[ -n $OUT_SPACE_MV ]] && \
python $PREPARE "$IN_SPACE_MV" "$SOLVERS_CSV" "$OUT_SPACE_MV" -t model_validation --select "$SELECT_MV" -w

# Single Query Track - fixed STP versions
[[ -n $OUT_SPACE_SQ_FIXED ]] && \
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ_FIXED" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $FIXED_SOLVERS_SQ

# Challenge Track non-incremental - fixed STP versions
[[ -n $OUT_SPACE_CHALL_NON_INC_FIXED ]] && \
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_FIXED" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --solvers $FIXED_SOLVERS_SQ
