#! /bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/score/score.py"

RESULTS_SQ="$SCRIPTDIR/../../2019/results/single_query/Single_Query_Track.csv"
RESULTS_SQ_STRINGS="$SCRIPTDIR/../../2019/results/single_query/Single_Query_Track_strings.csv"
RESULTS_INC="$SCRIPTDIR/../../2019/results/incremental/Incremental_Track.csv"
RESULTS_CHALL_SQ="$SCRIPTDIR/../../2019/results/challenge_non_incremental/Challenge_Track_non-incremental.csv"
RESULTS_CHALL_INC="$SCRIPTDIR/../../2019/results/challenge_incremental/Challenge_Track_incremental.csv"
RESULTS_UC="$SCRIPTDIR/../../2019/results/unsat_core/Unsat_Core_Track.csv"
RESULTS_MV="$SCRIPTDIR/../../2019/results/model_validation/Model_Validation_Track.csv"

INC_NUM_CHECK_SAT="$SCRIPTDIR/../../2019/prep/incremental_num_check_sat.csv"

TIME=2400
TIME_CHALL=43200

SOLVERS_CSV="$SCRIPTDIR/../../2019/registration/solvers_divisions_final.csv"

GEN_SQ=
GEN_SQ_STRINGS=
GEN_INC=
GEN_CHALL_SQ=
GEN_CHALL_INC=
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
    --csq)
      GEN_CHALL_SQ=yes
      ;;
    --cinc)
      GEN_CHALL_INC=yes
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

[[ -n $GEN_SQ ]] && \
python score.py -y 2019 --csv $RESULTS_SQ  -t $TIME --gen-md results -T sq -S $SOLVERS_CSV
[[ -n $GEN_SQ_STRINGS ]] && \
python score.py -y 2019 --csv $RESULTS_SQ_STRINGS  -t $TIME --gen-md results -T sq -S $SOLVERS_CSV
[[ -n $GEN_INC ]] && \
python score.py -y 2019 --csv $RESULTS_INC  -t $TIME --gen-md results -T inc -S $SOLVERS_CSV -i $INC_NUM_CHECK_SAT
[[ -n $GEN_CHALL_SQ ]] && \
python score.py -y 2019 --csv $RESULTS_CHALL_SQ  -t $TIME_CHALL --gen-md results -T chall_sq -S $SOLVERS_CSV
[[ -n $GEN_CHALL_INC ]] && \
python score.py -y 2019 --csv $RESULTS_CHALL_INC  -t $TIME_CHALL --gen-md results -T chall_inc -S $SOLVERS_CSV -i $INC_NUM_CHECK_SAT
[[ -n $GEN_UC ]] && \
python score.py -y 2019 --csv $RESULTS_UC  -t $TIME --gen-md results -T uc -S $SOLVERS_CSV
[[ -n $GEN_MV ]] && \
python score.py -y 2019 --csv $RESULTS_MV  -t $TIME --gen-md results -T mv -S $SOLVERS_CSV --exp-tracks mv 
