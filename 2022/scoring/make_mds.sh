#!/bin/bash

SCRIPTDIR=`dirname $(readlink -f "$0")`

YEAR=2022
SCORE="$SCRIPTDIR/../../tools/scoring/score.py"
SOLVERS_CSV="$SCRIPTDIR/../registration/solvers_divisions_all.csv"
OUTPUT="$SCRIPTDIR/../../../smt-comp.github.io/_results_$YEAR"
TIME=1200
INC_NUM_CHECK_SAT="$SCRIPTDIR/../prep/SMT-LIB_incremental_benchmarks_num_check_sat.csv"

GEN_SQ=
GEN_INC=
GEN_UC=
GEN_MV=
GEN_PE=
GEN_CT=
GEN_PT=

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
      echo "    --all          All tracks"
      echo "    --sq           Single Query track (no strings)"
      echo "    --inc          Incremental track "
      echo "    --uc           Unsat Core track "
      echo "    --mv           Model Validation track "
      echo "    --pe           Proof Exhibition track "
      echo "    --cloud        Cloud track "
      echo "    --parallel     Parallel track "
      echo
      exit
      ;;
    --all)
      GEN_SQ=yes
      GEN_INC=yes
      GEN_UC=yes
      GEN_MV=yes
      GEN_PE=yes
      GEN_CT=yes
      GEN_PT=yes
      ;;
    --sq)
      GEN_SQ=yes
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
    --pe)
      GEN_PE=yes
      ;;
    --cloud)
      GEN_CT=yes
      ;;
    --parallel)
      GEN_PT=yes
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

PE_DIVISIONS=$(jq -r '.track_proof_exhibition | keys[]' <  ../new-divisions.json  | tr '\n' , | sed s/,$//)

[[ -n $GEN_SQ ]] && echo SQ && \
$PYTHON $SCORE -y $YEAR --csv results-sq.csv  -t $TIME --gen-md $OUTPUT -T sq -S $SOLVERS_CSV -D ../new-divisions.json
[[ -n $GEN_INC ]] && echo INC && \
$PYTHON $SCORE -y $YEAR --csv results-inc.csv -t $TIME --gen-md $OUTPUT -T inc -S $SOLVERS_CSV -i $INC_NUM_CHECK_SAT -D ../new-divisions.json
[[ -n $GEN_UC ]] && echo UC && \
$PYTHON $SCORE -y $YEAR --csv results-uc.csv  -t $TIME --gen-md $OUTPUT -T uc -S $SOLVERS_CSV -D ../new-divisions.json
[[ -n $GEN_MV ]] && echo MV && \
$PYTHON $SCORE -y $YEAR --csv results-mv.csv  -t $TIME \
    --gen-md $OUTPUT -T mv -S $SOLVERS_CSV -D ../new-divisions.json \
    --expdivs QF_FPArith
[[ -n $GEN_PE ]] && echo PE && \
$PYTHON $SCORE -y $YEAR --csv results-pe.csv  -t $TIME \
    --gen-md $OUTPUT -T pe -S $SOLVERS_CSV -D ../new-divisions.json \
    --expdivs $PE_DIVISIONS
[[ -n $GEN_CT ]] && echo CT && \
$PYTHON $SCORE -y $YEAR --csv results-cloud.csv  -t $TIME --gen-md $OUTPUT -T ct -S $SOLVERS_CSV -D ../new-divisions.json
[[ -n $GEN_PT ]] && echo PT &&\
$PYTHON $SCORE -y $YEAR --csv results-parallel.csv  -t $TIME --gen-md $OUTPUT -T pt -S $SOLVERS_CSV -D ../new-divisions.json

