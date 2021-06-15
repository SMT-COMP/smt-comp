#!/bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

INCLUDE_NONCOMPETITIVE=""

### Input space xml files
IN_SPACE_NON_INC="../non-incremental-space.xml"
IN_SPACE_INC="../incremental-space.xml"

### Benchmark selection
SELECT_SQ="$SCRIPTDIR/../selection/$SELECTION/benchmark_selection_single_query"
SELECT_INC="$SCRIPTDIR/../selection/$SELECTION/benchmark_selection_incremental"
SELECT_MV="$SCRIPTDIR/../selection/$SELECTION/benchmark_selection_model_validation"
SELECT_UC="$SCRIPTDIR/../selection/$SELECTION/benchmark_selection_unsat_core"

### Output space xml files
# Single Query
OUT_SPACE_SQ=
OUT_SPACE_SQ_FIXED=
OUT_SPACE_SQ_FIXED_NC=
OUT_SPACE_SQ_2018=
OUT_SPACE_SQ_STRINGS=
# Challenge Track - non-incremental
OUT_SPACE_CHALL_NON_INC=
OUT_SPACE_CHALL_NON_INC_FIXED=
OUT_SPACE_CHALL_NON_INC_2018=
# Challenge Track - incremental
OUT_SPACE_CHALL_INC=
OUT_SPACE_CHALL_INC_UNKNOWN=
OUT_SPACE_CHALL_INC_FIXED=
OUT_SPACE_CHALL_INC_2018=
# Incremental Track
OUT_SPACE_INC=
OUT_SPACE_INC_UNKNOWN=
OUT_SPACE_INC_FIXED=
OUT_SPACE_INC_2018=
# Unsat Core Track
OUT_SPACE_UC=
OUT_SPACE_UC_2018=
# Model Validation Track
OUT_SPACE_MV=

# output usage if called without parameters
if [ $# -eq 0 ]; then
    set -- -h
fi

while [ $# -gt 0 ]
do
  case $1 in
    -h|--help)
      echo -n "usage: $(basename $0) [<option>]"
      echo
      echo "Generate StarExec competition spaces."
      echo
      echo "  options:"
      echo "    -h, --help           Print this message and exit"
      echo "    --include-nc         Run also non-competitive divisions"
      echo "    --sq          <file> Single Query track (no strings) output xml"
      echo "    --inc         <file> Incremental track output xml"
      echo "    --uc          <file> Unsat Core track output xml"
      echo "    --mv          <file> Model Validation track output xml"
      echo "    --solvdiv     <file> An optional alternative solvers divisions file"
      echo
      exit
      ;;
    --sq)
      shift
      OUT_SPACE_SQ=$1
      ;;
    --sq-2018)
      shift
      OUT_SPACE_SQ_2018=$1
      ;;
    --inc)
      shift
      OUT_SPACE_INC=$1
      ;;
    --inc-2018)
      shift
      OUT_SPACE_INC_2018=$1
      ;;
    --uc)
      shift
      OUT_SPACE_UC=$1
      ;;
    --uc-2018)
      shift
      OUT_SPACE_UC_2018=$1
      ;;
    --mv)
      shift
      OUT_SPACE_MV=$1
      ;;
    --solvdiv)
      shift
      SOLVERS_CSV=$1
      ;;
    --include-nc)
      INCLUDE_NONCOMPETITIVE="--include-non-competitive"
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
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ" \
    -t single_query --select "$SELECT_SQ" -w \
    $INCLUDE_NONCOMPETITIVE

# Incremental Track
[[ -n $OUT_SPACE_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" \
    -t incremental --select "$SELECT_INC" -w \
    $(echo $INCLUDE_NONCOMPETITIVE)


# Model Validation Track
[[ -n $OUT_SPACE_MV ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_MV" \
    -t model_validation --select "$SELECT_MV" -w \
    $(echo $INCLUDE_NONCOMPETITIVE)


# Unsat Core Track
[[ -n $OUT_SPACE_UC ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_UC" \
    -t unsat_core --select "$SELECT_UC" -w \
    $(echo $INCLUDE_NONCOMPETITIVE)

