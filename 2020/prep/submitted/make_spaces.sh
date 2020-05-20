#! /bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

# SOLVERS_SQ_CSV="$SCRIPTDIR/../../registration/sq-cvc4-yices.csv"
# SOLVERS_INC_CSV="$SCRIPTDIR/../../registration/inc-cvc4-yices.csv"
# SOLVERS_MV_CSV="$SCRIPTDIR/../../registration/mv-cvc4-yices.csv"
# SOLVERS_UC_CSV="$SCRIPTDIR/../../registration/uc-cvc4-yices.csv"

### Input space xml files
IN_SPACE_NON_INC="../non-incremental-space.xml"
IN_SPACE_INC="../incremental-space.xml"

### Benchmark selection
SELECT_SQ="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2020_testjob2"
SELECT_INC="$SCRIPTDIR/../selection/incremental/benchmark_selection_incremental_2020_testjob2"
SELECT_MV="$SCRIPTDIR/../selection/model_validation/benchmark_selection_model_validation_2020_testjob2"
SELECT_UC="$SCRIPTDIR/../selection/unsat_core/benchmark_selection_unsatcore_2020_testjob2"


### Fixed solver versions (non-competitive)
FIXED_SOLVERS_NON_COMPETITIVE_SQ="24281,24282"  # STP-mergesat-fixed,STP-portfolio-fixed
FIXED_SOLVERS_NON_COMPETITIVE_INC="24478"       # CVC4

### Fixed solver versions (competitive)
FIXED_SOLVERS_COMPETITIVE_SQ="24492"   # Colibri had an issue with the with the
                                       # original StarExec configuration file
                                       # that broke solver wrapping

### Best solvers 2018
# Main track
SOLVERS_2018_SQ="19771,19772,19775,19777,19783,19784,19788,19791,19792"
# Application track
SOLVERS_2018_INC="19991,19992,19993,19994,19995,19996"
# Unsat core track
SOLVERS_2018_UC="19793,19795,19796,19797,19827"

### Non-competitive solvers
# Z3,Boolector-ReasonLS,CVC4-SymBreak
NON_COMPETITIVE_SOLVERS_SQ="24192,24193,24160,$SOLVERS_2018_SQ,$FIXED_SOLVERS_NON_COMPETITIVE_SQ"
# Z3
NON_COMPETITIVE_SOLVERS_CHALL_NON_INC="24192,$SOLVERS_2018_SQ"
# Z3
NON_COMPETITIVE_SOLVERS_CHALL_INC="24017,24478,$SOLVERS_2018_INC"
# Z3,Boolector-ReasonLS
NON_COMPETITIVE_SOLVERS_INC="24017,23970,$SOLVERS_2018_INC,$FIXED_SOLVERS_NON_COMPETITIVE_INC"
# Z3
NON_COMPETITIVE_SOLVERS_UC="24202,$SOLVERS_2018_UC"

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
      echo "    --sq          <file> Single Query track (no strings) output xml"
      echo "    --sq-fixed    <file> Single Query track (no strings) output xml"
      echo "                         for fixed (non-competing) solvers"
      echo "    --sq-2018     <file> Single Query track (no strings) output xml"
      echo "                         for best solvers 2018"
      echo "    --sq-strings  <file> Single Query track (strings only) "
      echo "                         output xml"
      echo "    --inc         <file> Incremental track output xml"
      echo "    --inc-unknown <file> Incremental track for benchmarks with"
      echo "                         unknown status output xml"
      echo "    --inc-2018    <file> Incremental track output xml for best "
      echo "                         solvers 2018"
      echo "    --csq         <file> Challenge track non-incremental output xml"
      echo "    --csq-fixed   <file> Challenge track non-incremental for fixed "
      echo "                         competing solvers"
      echo "    --csq-fixednc <file> Challenge track non-incremental for fixed "
      echo "                         non-competing solvers"
      echo "    --csq-2018    <file> Challenge track non-incremental output xml"
      echo "                         for best solvers 2018"
      echo "    --cinc        <file> Challenge track incremental output xml"
      echo "    --cinc-fixed  <file> Challenge track incremental output xml"
      echo "                         for fixed (non-competitive) solvers"
      echo "    --cinc-2018   <file> Challenge track incremental output xml"
      echo "                         for best solvers 2018"
      echo "    --uc          <file> Unsat Core track output xml"
      echo "    --uc-2018     <file> Unsat Core track output xml for best "
      echo "                         solvers 2018"
      echo "    --mv          <file> Model Validation track output xml"
      echo
      exit
      ;;
    --sq)
      shift
      OUT_SPACE_SQ=$1
      ;;
    --sq-strings)
      shift
      OUT_SPACE_SQ_STRINGS=$1
      ;;
    --sq-fixed)
      shift
      OUT_SPACE_SQ_FIXED=$1
      ;;
    --sq-fixednc)
      shift
      OUT_SPACE_SQ_FIXED_NC=$1
      ;;
    --sq-2018)
      shift
      OUT_SPACE_SQ_2018=$1
      ;;
    --inc)
      shift
      OUT_SPACE_INC=$1
      ;;
    --inc-unknown)
      shift
      OUT_SPACE_INC_UNKNOWN=$1
      ;;
    --inc-fixed)
      shift
      OUT_SPACE_INC_FIXED=$1
      ;;
    --inc-2018)
      shift
      OUT_SPACE_INC_2018=$1
      ;;
    --csq)
      shift
      OUT_SPACE_CHALL_NON_INC=$1
      ;;
    --csq-fixed)
      shift
      OUT_SPACE_CHALL_NON_INC_FIXED=$1
      ;;
    --csq-2018)
      shift
      OUT_SPACE_CHALL_NON_INC_2018=$1
      ;;
    --cinc)
      shift
      OUT_SPACE_CHALL_INC=$1
      ;;
    --cinc-fixed)
      shift
      OUT_SPACE_CHALL_INC_FIXED=$1
      ;;
    --cinc-unknown)
      shift
      OUT_SPACE_CHALL_INC_UNKNOWN=$1
      ;;
    --cinc-2018)
      shift
      OUT_SPACE_CHALL_INC_2018=$1
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
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -p

# Incremental Track
[[ -n $OUT_SPACE_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" -t incremental --select "$SELECT_INC" -w

# Model Validation Track
[[ -n $OUT_SPACE_MV ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_MV" -t model_validation --select "$SELECT_MV" -p

# Unsat Core Track
[[ -n $OUT_SPACE_UC ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_UC" -t unsat_core --select "$SELECT_UC" -p
