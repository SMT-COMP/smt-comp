#!/bin/sh

SCORE=../../tools/scoring/score.py
JOINSCORE=../../tools/scoring/join_results.sh
COLORDER=../previous-best/unify_column_order.py
SOLVERSDIVS=../registration/solvers_divisions_final.csv

INC_ORIG_IN=incremental/Job_info_orig.csv
INC_2019_IN=incremental/Job_info_2019.csv
INC_OUT=../results/Incremental_Track.csv

MV_ORIG_IN=model-validation/Job_info_orig.csv
MV_2019_IN=model-validation/Job_info_2019.csv
MV_OUT=../results/Model_Validation_Track.csv

UC_ORIG_IN=unsat-core/Job_info_orig.csv
UC_2019_IN=unsat-core/Job_info_2019.csv
UC_OUT=../results/Unsat_Core_Track.csv

SQ_ORIG_IN=single-query/Job_info_orig.csv
SQ_2019_IN=single-query/Job_info_2019.csv
SQ_OUT=../results/Single_Query_Track.csv

PROCESS_INC="false"
PROCESS_UC="false"
PROCESS_MV="false"
PROCESS_SQ="false"

function fixModelValCsv {
    perl -pe 's/(([^,]*,){15})([^"].*)\r$/$1"$3"/' < $1
}

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
      echo "Join outputs from different jobs."
      echo
      echo "  options:"
      echo "    -h, --help    Print this message and exit"
      echo "    --sq          Single Query track"
      echo "    --inc         Incremental track"
      echo "    --uc          Unsat Core track"
      echo "    --mv          Model Validation track"
      echo
      exit
      ;;
    --sq)
      PROCESS_SQ="true"
      ;;
    --inc)
      PROCESS_INC="true"
      ;;
    --uc)
      PROCESS_UC="true"
      ;;
    --mv)
      PROCESS_MV="true"
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

if [[ ${PROCESS_INC} == "true" ]]; then
    echo "Joining inc info"
    ${JOINSCORE} ${INC_ORIG_IN} ${INC_2019_IN} > ${INC_OUT}
fi

if [[ ${PROCESS_MV} == "true" ]]; then
    TMP_MV_2019_ORDERED=$(mktemp).mv_2019_ordered

    echo "Adding the error column to mv 2019"
    ${COLORDER} -o ${MV_ORIG_IN} -a ${MV_2019_IN} > ${TMP_MV_2019_ORDERED}

    echo "Fixing mv csvs"
    TMP_MV_ORIG_FIXED=$(mktemp).mv_orig_fixed
    TMP_MV_2019_FIXED=$(mktemp).mv_2019_fixed

    fixModelValCsv ${MV_ORIG_IN} > ${TMP_MV_ORIG_FIXED}
    fixModelValCsv ${TMP_MV_2019_ORDERED} > ${TMP_MV_2019_FIXED}

    echo "Joining mv info"
    ${JOINSCORE} ${TMP_MV_ORIG_FIXED} ${TMP_MV_2019_FIXED} > ${MV_OUT}

    rm ${TMP_MV_ORIG_FIXED} ${TMP_MV_2019_FIXED} ${TMP_MV_2019_ORDERED}
fi

if [[ ${PROCESS_UC} == "true" ]]; then
    TMP_UC_2019_ORDERED=$(mktemp).uc_2019_ordered

    echo "Reordering uc 2019 columns according to original"
    ${COLORDER} -o ${UC_ORIG_IN} -a ${UC_2019_IN} > ${TMP_UC_2019_ORDERED}

    echo "Joining uc info"
    ${JOINSCORE} ${UC_ORIG_IN} ${TMP_UC_2019_ORDERED} > ${UC_OUT}

    rm ${TMP_UC_2019_ORDERED}
fi

if [[ ${PROCESS_SQ} == "true" ]]; then
    echo "Removing solver ID 24160 from 2019"
    TMP_SQ_NO24160=$(mktemp).fixed
    csvgrep -i -c "solver id" -m 24160 ${SQ_2019_IN} > ${TMP_SQ_NO24160}

    echo "Joining sq info"
    ${JOINSCORE} ${SQ_ORIG_IN} ${TMP_SQ_NO24160} > ${SQ_OUT}

    rm ${TMP_SQ_NO24160}
fi
