#!/bin/sh

SCORE=../../tools/scoring/score.py
JOINSCORE=../../tools/scoring/join_results.sh
COLORDER=../previous-best/unify_column_order.py
SOLVERSDIVS=../registration/solvers_divisions_final.csv

RESULTS=_results_2020/
WEBSITE_RESULTS=../../../smt-comp.github.io/_results_2020/

INCREMENTALCHECKSATS=SMT-LIB_incremental_benchmarks_num_check_sat.csv
INC_ORIG=incremental/Job_info_orig.csv
INC_2019=incremental/Job_info_2019.csv
INC_JOIN=incremental/Job_info.csv

MV_ORIG=model-validation/Job_info_orig.csv
MV_2019=model-validation/Job_info_2019.csv
MV_JOIN=model-validation/Job_info.csv

UC_ORIG=unsat-core/Job_info_orig.csv
UC_2019=unsat-core/Job_info_2019.csv
UC_JOIN=unsat-core/Job_info.csv

SQ_ORIG=single-query/Job_info_orig.csv
SQ_2019=single-query/Job_info_2019.csv
SQ_JOIN=single-query/Job_info.csv

PROCESS_INC="false"
PROCESS_UC="false"
PROCESS_MV="false"
PROCESS_SQ="false"

MV_FIX_PATTERN='s/\([^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,\)\(.*\)$/\1"\2"/g'
function fixModelValCsv {
    sed ${MV_FIX_PATTERN} < $1
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
      shift
      PROCESS_SQ="true"
      ;;
    --inc)
      shift
      PROCESS_INC="true"
      ;;
    --uc)
      shift
      PROCESS_UC="true"
      ;;
    --mv)
      shift
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

mkdir -p ${RESULTS}

if [[ ${PROCESS_INC} == "true" ]]; then
    echo "Joining inc info"
    ${JOINSCORE} ${INC_ORIG} ${INC_2019} > ${INC_JOIN}

    echo "Computing inc scores"
    ${SCORE} -T inc -S ${SOLVERSDIVS} -t 1200 -y 2020 \
        -c ${INC_JOIN} -i ${INCREMENTALCHECKSATS} \
        --gen-md ${RESULTS}
fi

if [[ ${PROCESS_MV} == "true" ]]; then
    echo "Fixing mv csvs"
    TMP_MV_ORIG_FIXED=$(mktemp).mv_orig_fixed
    TMP_MV_2019_FIXED=$(mktemp).mv_2019_fixed

    fixModelValCsv ${MV_ORIG} > ${TMP_MV_ORIG_FIXED}
    fixModelValCsv ${MV_2019} > ${TMP_MV_2019_FIXED}

    echo "Joining mv info"
    ${JOINSCORE} ${TMP_MV_ORIG_FIXED} ${TMP_MV_2019_FIXED} > ${MV_JOIN}

    rm ${TMP_MV_ORIG_FIXED} ${TMP_MV_2019_FIXED}

    echo "Computing mv scores"
    ${SCORE} -T mv -S ${SOLVERSDIVS} -t 1200 -y 2020 \
        -c ${MV_JOIN} --gen-md ${RESULTS}
fi

if [[ ${PROCESS_UC} == "true" ]]; then
    TMP_UC_2019_ORDERED=$(mktemp).uc_2019_ordered

    echo "Reordering mv 2019 columns according to original"
    ${COLORDER} -o ${UC_ORIG} -a ${UC_2019} > ${TMP_UC_2019_ORDERED}

    echo "Joining uc info"
    ${JOINSCORE} ${UC_ORIG} ${TMP_UC_2019_ORDERED} > ${UC_JOIN}

    rm ${TMP_UC_2019_ORDERED}

    echo "Computing uc scores"
    ${SCORE} -T uc -S ${SOLVERSDIVS} -t 1200 -y 2020 \
        -c ${UC_JOIN} --gen-md ${RESULTS}
fi

if [[ ${PROCESS_SQ} == "true" ]]; then
    echo "Joining sq info"
    ${JOINSCORE} ${SQ_ORIG} ${SQ_2019} > ${SQ_JOIN}

    echo "Computing sq scores"
    ${SCORE} -T sq -S ${SOLVERSDIVS} -t 1200 -y 2020 \
        -c ${SQ_JOIN} --gen-md ${RESULTS}
fi

cp ${RESULTS}/*.md ${WEBSITE_RESULTS}
