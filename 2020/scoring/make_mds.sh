#! /bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

OUTPUT=results

PREPARE="$SCRIPTDIR/../../tools/scoring/score.py"

RESULTS_SQ="$SCRIPTDIR/../results/Single_Query_Track.csv"
RESULTS_SQ_STRINGS="$SCRIPTDIR/../../2019/results/Single_Query_Track_strings.csv"
RESULTS_INC="$SCRIPTDIR/../results/Incremental_Track.csv"
RESULTS_UC="$SCRIPTDIR/../results/Unsat_Core_Track.csv"
RESULTS_MV="$SCRIPTDIR/../results/Model_Validation_Track.csv"

INC_NUM_CHECK_SAT="$SCRIPTDIR/../prep/SMT-LIB_incremental_benchmarks_num_check_sat.csv"

TIME=2400

SOLVERS_CSV="$SCRIPTDIR/../registration/solvers_divisions_final.csv"

GEN_SQ=
GEN_SQ_STRINGS=
GEN_INC=
GEN_UC=
GEN_MV=

while [ $# -gt 0 ]
do
  case $1 in
    -h|--help)
      echo -n "usage: $(basename $0) [<option>]"
      echo
      echo "Generate results .md files for website."
      echo
      echo "  options:"
      echo "    -h, --help     Print this message and exit"
      echo "    --sq           Single Query track (no strings)"
      echo "    --sq-strings   Single Query track (only strings)"
      echo "    --inc          Incremental track "
      echo "    --csq          Challenge track non-incremental "
      echo "    --cinc         Challenge track incremental "
      echo "    --uc           Unsat Core track "
      echo "    --mv           Model Validation track "
      echo
      exit
      ;;
    --sq)
      GEN_SQ=yes
      ;;
    --sq-strings)
      GEN_SQ_STRINGS=yes
      ;;
    --inc)
      GEN_INC=yes
      ;;
    --uc)
      GEN_UC=yes
      ;;
    --mv)
      GEN_MV=yes
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

mkdir -p $OUTPUT

[[ -n $GEN_SQ ]] && \
python3 $PREPARE -y 2020 --csv $RESULTS_SQ  -t $TIME --gen-md $OUTPUT -T sq -S $SOLVERS_CSV
[[ -n $GEN_SQ_STRINGS ]] && \
python3 $PREPARE -y 2020 --csv $RESULTS_SQ_STRINGS  -t $TIME --gen-md $OUTPUT -T sq -S $SOLVERS_CSV
[[ -n $GEN_INC ]] && \
python3 $PREPARE -y 2020 --csv $RESULTS_INC  -t $TIME --gen-md $OUTPUT -T inc -S $SOLVERS_CSV -i $INC_NUM_CHECK_SAT
[[ -n $GEN_UC ]] && \
python3 $PREPARE -y 2020 --csv $RESULTS_UC  -t $TIME --gen-md $OUTPUT -T uc -S $SOLVERS_CSV
[[ -n $GEN_MV ]] && \
python3 $PREPARE -y 2020 --csv $RESULTS_MV  -t $TIME --gen-md $OUTPUT -T mv -S $SOLVERS_CSV
