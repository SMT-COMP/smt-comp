#!/bin/bash

SCORE=../../tools/scoring/score.py
JOINSCORE=../../tools/scoring/join_results.sh
COLORDER=../previous-best/unify_column_order.py
SOLVERSDIVS=../registration/solvers_divisions_final.csv
PATCH_CSV=../../tools/scoring/patch_csv.py

RESULTS=../results

INC_ORIG_IN=${RESULTS}/incremental/Job_info_orig.csv
INC_2019_IN=${RESULTS}/incremental/Job_info_2019.csv
INC_FIXED_IN=${RESULTS}/incremental/Job_info_fixed.csv
INC_OUT=${RESULTS}/Incremental_Track.csv

MV_ORIG_IN=${RESULTS}/model-validation/Job_info_orig.csv
MV_2019_IN=${RESULTS}/model-validation/Job_info_2019.csv
MV_FIXED_IN=${RESULTS}/model-validation/Job_info_fixed.csv
MV_OUT=${RESULTS}/Model_Validation_Track.csv

UC_ORIG_IN=${RESULTS}/unsat-core/Job_info_orig.csv
UC_2019_IN=${RESULTS}/unsat-core/Job_info_2019.csv
UC_FIXED_IN=${RESULTS}/unsat-core/Job_info_fixed.csv
UC_OUT=${RESULTS}/Unsat_Core_Track.csv

# The SQ 2019 job has already the fixed solvers as well
SQ_ORIG_IN=${RESULTS}/single-query/Job_info_orig.csv
SQ_2019_IN=${RESULTS}/single-query/Job_info_2019.csv
SQ_PATCH=SQ-wrong-sat-result.csv
SQ_OUT=${RESULTS}/Single_Query_Track.csv

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
    ${JOINSCORE} ${INC_ORIG_IN} ${INC_2019_IN} ${INC_FIXED_IN} > ${INC_OUT}
fi

if [[ ${PROCESS_MV} == "true" ]]; then
    TMP_MV_2019_ORDERED=$(mktemp -t mv_2019_ordered.XXXXXX)
    TMP_MV_FIXED_ORDERED=$(mktemp -t mv_fixed_ordered.XXXXXX)

    echo "Adding the error column to mv 2019"
    ${COLORDER} -o ${MV_ORIG_IN} -a ${MV_2019_IN} > ${TMP_MV_2019_ORDERED}
    echo "Adding the error column to mv fixed"
    ${COLORDER} -o ${MV_ORIG_IN} -a ${MV_FIXED_IN} > ${TMP_MV_FIXED_ORDERED}

    echo "Fixing mv csvs"

    TMP_MV_ORIG_FIXED=$(mktemp -t mv_orig_fixed.XXXXXX)
    TMP_MV_2019_FIXED=$(mktemp -t mv_2019_fixed.XXXXXX)
    TMP_MV_FIXED_FIXED=$(mktemp -t mv_fixed_fixed.XXXXXX)

    fixModelValCsv ${MV_ORIG_IN} > ${TMP_MV_ORIG_FIXED}
    fixModelValCsv ${TMP_MV_2019_ORDERED} > ${TMP_MV_2019_FIXED}
    fixModelValCsv ${TMP_MV_FIXED_ORDERED} > ${TMP_MV_FIXED_FIXED}

    echo "Joining mv info"
    ${JOINSCORE} ${TMP_MV_ORIG_FIXED} \
        ${TMP_MV_2019_FIXED} ${TMP_MV_FIXED_FIXED} > ${MV_OUT}

    rm ${TMP_MV_ORIG_FIXED} ${TMP_MV_2019_FIXED} \
        ${TMP_MV_2019_ORDERED} \
        ${TMP_MV_FIXED_FIXED} ${TMP_MV_FIXED_ORDERED}
fi

if [[ ${PROCESS_UC} == "true" ]]; then
    TMP_UC_2019_ORDERED=$(mktemp -t uc_2019_ordered.XXXXXX)

    echo "Reordering uc 2019 columns according to original"
    ${COLORDER} -o ${UC_ORIG_IN} -a ${UC_2019_IN} > ${TMP_UC_2019_ORDERED}
    echo "Reordering uc fixed columns according to original"
    ${COLORDER} -o ${UC_ORIG_IN} -a ${UC_FIXED_IN} > ${TMP_UC_2019_ORDERED}

    echo "Joining uc info"
    ${JOINSCORE} ${UC_ORIG_IN} ${TMP_UC_2019_ORDERED} ${TMP_UC_FIXED_ORDERED} > ${UC_OUT}

    rm ${TMP_UC_2019_ORDERED} ${TMP_UC_FIXED_ORDERED}
fi

if [[ ${PROCESS_SQ} == "true" ]]; then
    echo "Removing solver ID 24160 from 2019"
    TMP_SQ_NO24160=$(mktemp -t fixed.XXXXXX)
    TMP_SQ_PATCHED=$(mktemp -t patched.XXXXXX)
    csvgrep -i -c "solver id" -m 24160 ${SQ_2019_IN} > ${TMP_SQ_NO24160}

    echo "Patching wrongly classified results"
    ${PATCH_CSV} -o ${SQ_ORIG_IN} -p ${SQ_PATCH} > ${TMP_SQ_PATCHED}
    #diff -u0 ${SQ_ORIG_IN} ${TMP_SQ_PATCHED}

    echo "Joining sq info"
    ${JOINSCORE} ${TMP_SQ_PATCHED} ${TMP_SQ_NO24160} > ${SQ_OUT}

    rm ${TMP_SQ_NO24160} ${TMP_SQ_PATCHED}
fi
