#! /bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

### Input space xml files
IN_SPACE_SQ="../non-incremental-space.xml"
SELECT_SQ="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2019_no_strings"

IN_SPACE_INC="../incremental-space.xml"
SELECT_INC="$SCRIPTDIR/../selection/incremental/benchmark_selection_incremental_2019"

IN_SPACE_CHALL_NON_INC="../non-incremental-space.xml"
SELECT_CHALL_NON_INC="$SCRIPTDIR/../selection/challenge-non-incremental/benchmark_selection_challenge_non-incremental_2019"

IN_SPACE_CHALL_INC="../incremental-space.xml"
SELECT_CHALL_INC="$SCRIPTDIR/../selection/challenge-incremental/benchmark_selection_challenge_incremental_2019"

IN_SPACE_UC="../non-incremental-space.xml"
SELECT_UC="$SCRIPTDIR/../selection/unsat_core/benchmark_selection_unsat_core_2019"

IN_SPACE_MV="../non-incremental-space.xml"
SELECT_MV="$SCRIPTDIR/../selection/model_validation/benchmark_selection_model_validation_2019"

### Fixed solver versions (non-competitive)
FIXED_SOLVERS_SQ="24281,24282"  # STP-mergesat-fixed,STP-portfolio-fixed

### Best solvers 2018
# Main track
SOLVERS_2018_SQ="19771,19772,19775,19777,19783,19784,19788,19791,19792"
# Application track
SOLVERS_2018_INC="19991,19992,19993,19994,19995,19996"
# Unsat core track
SOLVERS_2018_UC="19793,19795,19796,19797,19827"

### Non-competitive solvers
# Z3,Boolector-ReasonLS,CVC4-SymBreak
NON_COMPETITIVE_SOLVERS_SQ="24192,24193,24160,$SOLVERS_2018_SQ"
# Z3
NON_COMPETITIVE_SOLVERS_CHALL_NON_INC="24192,$SOLVERS_2018_SQ"
# Z3
NON_COMPETITIVE_SOLVERS_CHALL_INC="24017,$SOLVERS_2018_INC"
# Z3,Boolector-ReasonLS
NON_COMPETITIVE_SOLVERS_INC="24017,23970,$SOLVERS_2018_INC"
# Z3
NON_COMPETITIVE_SOLVERS_UC="24202,$SOLVERS_2018_UC"

### Output space xml files
OUT_SPACE_SQ=
OUT_SPACE_CHALL_NON_INC=
OUT_SPACE_CHALL_INC=
OUT_SPACE_INC=
OUT_SPACE_UC=
OUT_SPACE_MV=
OUT_SPACE_SQ_FIXED=
OUT_SPACE_CHALL_NON_INC_FIXED=
OUT_SPACE_SQ_2018=
OUT_SPACE_CHALL_NON_INC_2018=
OUT_SPACE_CHALL_INC_2018=
OUT_SPACE_INC_2018=
OUT_SPACE_UC_2018=

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
      echo "    --sq-2018 <file>    Single Query track for best solvers 2018 output xml"
      echo "    --inc <file>        Incremental track output xml"
      echo "    --csq <file>        Challenge track non-incremental output xml"
      echo "    --cinc <file>       Challenge track incremental output xml"
      echo "    --uc <file>         Unsat Core track output xml"
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
      shift
      OUT_SPACE_UC=$1
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
    --sq-2018)
      shift
      OUT_SPACE_SQ_2018=$1
      ;;
    --inc-2018)
      shift
      OUT_SPACE_INC_2018=$1
      ;;
    --csq-2018)
      shift
      OUT_SPACE_CHALL_NON_INC_2018=$1
      ;;
    --cinc-2018)
      shift
      OUT_SPACE_CHALL_INC_2018=$1
      ;;
    --uc-2018)
      shift
      OUT_SPACE_UC_2018=$1
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
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --exclude-solvers "$FIXED_SOLVERS_SQ,$SOLVERS_2018_SQ"

# Challenge Track non-incremental
[[ -n $OUT_SPACE_CHALL_NON_INC ]] && \
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --exclude-solvers "$FIXED_SOLVERS_SQ,$SOLVERS_2018_SQ"

# Challenge Track incremental
[[ -n $OUT_SPACE_CHALL_INC ]] && \
python $PREPARE "$IN_SPACE_CHALL_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC" -t incremental_challenge --select "$SELECT_CHALL_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --exclude-solvers "$SOLVERS_2018_INC"

# Incremental Track
[[ -n $OUT_SPACE_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC --exclude-solvers "$SOLVERS_2018_INC"

# Unsat Core Track
[[ -n $OUT_SPACE_UC ]] && \
python $PREPARE "$IN_SPACE_UC" "$SOLVERS_CSV" "$OUT_SPACE_UC" -t unsat_core --select "$SELECT_UC" -w --nc $NON_COMPETITIVE_SOLVERS_UC --exclude-solvers "$SOLVERS_2018_UC"

# Model Validation Track
[[ -n $OUT_SPACE_MV ]] && \
python $PREPARE "$IN_SPACE_MV" "$SOLVERS_CSV" "$OUT_SPACE_MV" -t model_validation --select "$SELECT_MV" -w

# Single Query Track - fixed STP versions
[[ -n $OUT_SPACE_SQ_FIXED ]] && \
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ_FIXED" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $FIXED_SOLVERS_SQ

# Challenge Track non-incremental - fixed STP versions
[[ -n $OUT_SPACE_CHALL_NON_INC_FIXED ]] && \
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_FIXED" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --solvers $FIXED_SOLVERS_SQ

# Single Query Track - Best/Winners 2018
[[ -n $OUT_SPACE_SQ_2018 ]] && \
python $PREPARE "$IN_SPACE_SQ" "$SOLVERS_CSV" "$OUT_SPACE_SQ_2018" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $SOLVERS_2018_SQ

# Incremental Track - Best/Winners 2018
[[ -n $OUT_SPACE_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC_2018" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC --solvers $SOLVERS_2018_INC

# Challenge Track non-incremental - Best/Winners 2018
[[ -n $OUT_SPACE_CHALL_NON_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_CHALL_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_2018" -t single_query_challenge -w --select "$SELECT_CHALL_NON_INC" --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --solvers $SOLVERS_2018_SQ

# Challenge Track incremental - Best/Winners 2018
[[ -n $OUT_SPACE_CHALL_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_CHALL_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC_2018" -t incremental_challenge -w --select "$SELECT_CHALL_INC" --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --solvers $SOLVERS_2018_INC

# Unsat Core Track - Best/Winners 2018
[[ -n $OUT_SPACE_UC_2018 ]] && \
python $PREPARE "$IN_SPACE_UC" "$SOLVERS_CSV" "$OUT_SPACE_UC_2018" -t unsat_core --select "$SELECT_UC" -w --nc $NON_COMPETITIVE_SOLVERS_UC --solvers $SOLVERS_2018_UC

