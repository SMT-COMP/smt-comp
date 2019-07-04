#! /bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

### Input space xml files
IN_SPACE_NON_INC="../non-incremental-space.xml"
IN_SPACE_INC="../incremental-space.xml"

### Benchmark selection
SELECT_SQ="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2019_no_strings"
SELECT_SQ_STRINGS="$SCRIPTDIR/../selection/single_query/benchmark_selection_single_query_2019_strings"

SELECT_INC="$SCRIPTDIR/../selection/incremental/benchmark_selection_incremental_2019"
SELECT_INC_UNKNOWN="$SCRIPTDIR/../selection/incremental/benchmark_selection_incremental_2019_status_unknown"
SELECT_CHALL_NON_INC="$SCRIPTDIR/../selection/challenge-non-incremental/benchmark_selection_challenge_non-incremental_2019"
SELECT_CHALL_INC="$SCRIPTDIR/../selection/challenge-incremental/benchmark_selection_challenge_incremental_2019"
SELECT_CHALL_INC_UNKNOWN="$SCRIPTDIR/../selection/challenge-incremental/benchmark_selection_challenge_incremental_2019_status_unknown"
SELECT_UC="$SCRIPTDIR/../selection/unsat_core/benchmark_selection_unsat_core_2019"
SELECT_MV="$SCRIPTDIR/../selection/model_validation/benchmark_selection_model_validation_2019"

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
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --exclude-solvers "$FIXED_SOLVERS_NON_COMPETITIVE_SQ,$SOLVERS_2018_SQ"
# Single Query Track - strings
[[ -n $OUT_SPACE_SQ_STRINGS ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ_STRINGS" -t single_query --select "$SELECT_SQ_STRINGS" -w --include-non-competitive
# Single Query Track - fixed STP versions
[[ -n $OUT_SPACE_SQ_FIXED_NC ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ_FIXED_NC" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $FIXED_SOLVERS_NON_COMPETITIVE_SQ
# Single Query Track - Best/Winners 2018
[[ -n $OUT_SPACE_SQ_2018 ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ_2018" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $SOLVERS_2018_SQ
# Single Query Track - fixed Colibri version
[[ -n $OUT_SPACE_SQ_FIXED ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_SQ_FIXED" -t single_query --select "$SELECT_SQ" -w --nc $NON_COMPETITIVE_SOLVERS_SQ --solvers $FIXED_SOLVERS_COMPETITIVE_SQ


# Incremental Track
[[ -n $OUT_SPACE_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC --exclude-solvers "$SOLVERS_2018_INC,$FIXED_SOLVERS_NON_COMPETITIVE_INC"
# Incremental Track for benchmarks with unknown status check-sat calls
[[ -n $OUT_SPACE_INC_UNKNOWN ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC_UNKNOWN" -t incremental --select "$SELECT_INC_UNKNOWN" -w --nc $NON_COMPETITIVE_SOLVERS_INC
# Incremental Track - fixed CVC4
[[ -n $OUT_SPACE_INC_FIXED ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC_FIXED" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC --solvers $FIXED_SOLVERS_NON_COMPETITIVE_INC
# Incremental Track - Best/Winners 2018
[[ -n $OUT_SPACE_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_INC_2018" -t incremental --select "$SELECT_INC" -w --nc $NON_COMPETITIVE_SOLVERS_INC --solvers $SOLVERS_2018_INC


# Challenge Track non-incremental
[[ -n $OUT_SPACE_CHALL_NON_INC ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --exclude-solvers "$FIXED_SOLVERS_NON_COMPETITIVE_SQ,$SOLVERS_2018_SQ"
# Challenge Track non-incremental - fixed STP versions
[[ -n $OUT_SPACE_CHALL_NON_INC_FIXED ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_FIXED" -t single_query_challenge --select "$SELECT_CHALL_NON_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --solvers $FIXED_SOLVERS_NON_COMPETITIVE_SQ
# Challenge Track non-incremental - Best/Winners 2018
[[ -n $OUT_SPACE_CHALL_NON_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_NON_INC_2018" -t single_query_challenge -w --select "$SELECT_CHALL_NON_INC" --nc $NON_COMPETITIVE_SOLVERS_CHALL_NON_INC --solvers $SOLVERS_2018_SQ


# Challenge Track incremental
[[ -n $OUT_SPACE_CHALL_INC ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC" -t incremental_challenge --select "$SELECT_CHALL_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --exclude-solvers "$SOLVERS_2018_INC,$FIXED_SOLVERS_NON_COMPETITIVE_INC"
# Challenge Track incremental - unknown CVC4
[[ -n $OUT_SPACE_CHALL_INC_UNKNOWN ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC_UNKNOWN" -t incremental_challenge --select "$SELECT_CHALL_INC_UNKNOWN" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --solvers "$SOLVERS_INC"
# Challenge Track incremental - fixed CVC4
[[ -n $OUT_SPACE_CHALL_INC_FIXED ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC_FIXED" -t incremental_challenge --select "$SELECT_CHALL_INC" -w --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --solvers "$FIXED_SOLVERS_NON_COMPETITIVE_INC"
# Challenge Track incremental - Best/Winners 2018
[[ -n $OUT_SPACE_CHALL_INC_2018 ]] && \
python $PREPARE "$IN_SPACE_INC" "$SOLVERS_CSV" "$OUT_SPACE_CHALL_INC_2018" -t incremental_challenge -w --select "$SELECT_CHALL_INC" --nc $NON_COMPETITIVE_SOLVERS_CHALL_INC --solvers $SOLVERS_2018_INC


# Unsat Core Track
[[ -n $OUT_SPACE_UC ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_UC" -t unsat_core --select "$SELECT_UC" -w --nc $NON_COMPETITIVE_SOLVERS_UC --exclude-solvers "$SOLVERS_2018_UC"
# Unsat Core Track - Best/Winners 2018
[[ -n $OUT_SPACE_UC_2018 ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_UC_2018" -t unsat_core --select "$SELECT_UC" -w --nc $NON_COMPETITIVE_SOLVERS_UC --solvers $SOLVERS_2018_UC


# Model Validation Track
[[ -n $OUT_SPACE_MV ]] && \
python $PREPARE "$IN_SPACE_NON_INC" "$SOLVERS_CSV" "$OUT_SPACE_MV" -t model_validation --select "$SELECT_MV" -w
