#! /bin/bash

function get_abs_path {
  echo $(cd $(dirname $1); pwd)/$(basename $1)
}

function check_seed_ok {
    seed_file=$1
    if [ -e ${seed_file} ]; then
        seed=$(cat ${seed_file})
        [ -n "${seed}" ] && \
            [ ${seed} -eq ${seed} ] 2>/dev/null && \
            [ ${seed} -gt 0 ] && \
            return 0
    else
       echo "Missing seed file in ${seed_file}";
    fi
    return 1
}


function getLogics {
    track=$1
    $PYTHON ${GET_LOGICS} \
        -d ../../new-divisions.json \
        -t $1 \
        ../../registration/solvers_divisions_final.csv
}

function preselect {
    mode=$1
    output=$2
    logics=$3
    $PYTHON $SELECT_PRE \
        --justification "$FILTER_CSV_2020" \
        --justification "$FILTER_CSV_2019" \
        --justification "$FILTER_CSV_2018" \
        --benchmarks "$BENCHMARKS" \
        --print-stats \
        --out "${output}" \
        --prefix "/non-incremental/" \
        --logic "${logics}" \
        --selection-mode ${mode}
}

function genlogics {
    instances=$1
    cat ${instances} \
        |sed 's,/non-incremental/\([^/]*\)/.*,\1,g' \
        |sort |uniq -c > ${instances}-logics
}

function picknums {
    hard_logics=$1
    unsolved_logics=$2
    numbers=$3
    ${PICKNUM} \
        ${hard_logics} \
        ${unsolved_logics} \
        ${MIN_BENCHMARKS} \
        > ${numbers}
}

function selectfinal {
    numbers=$1
    hard_benchmarks=$2
    unsolved_benchmarks=$3
    final_selection=$4

    ${PYTHON} ${SELECT_FINAL} \
        ${numbers} \
        ${hard_benchmarks} \
        ${unsolved_benchmarks} \
        ${SEED} \
        > ${final_selection}
}

COMPETITION_SEED="../../COMPETITION_SEED"
OUT_CLOUD="final/benchmark_selection_cloud"
SELECTION_NUMBERS_CLOUD="final/benchmark_selection_cloud_numbers.json"
SELECTION_CLOUD="final/benchmark_selection_cloud.txt"
OUT_PARALLEL="final/benchmark_selection_parallel"
SELECTION_NUMBERS_PARALLEL="final/benchmark_selection_parallel_numbers.json"
SELECTION_PARALLEL="final/benchmark_selection_parallel.txt"

MIN_BENCHMARKS=400

SCRIPTDIR=`get_abs_path $(dirname "$0")`
GET_LOGICS=${SCRIPTDIR}/../../../tools/prep/extract_aws_data_from_solvers_divisions.py
SELECT_PRE="$SCRIPTDIR/../../../tools/selection/selection_additive.py"
PICKNUM="${SCRIPTDIR}/aws_pick_instance_nums.py" 
SELECT_FINAL="${SCRIPTDIR}/aws_select_final.py"
AWS_SCRAMBLER="${SCRIPTDIR}/aws_scramble_and_rename.sh"

BENCHMARKS="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
FILTER_CSV_2018="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"
FILTER_CSV_2019="$SCRIPTDIR/../../../2019/results/Single_Query_Track.csv"
FILTER_CSV_2020="$SCRIPTDIR/../../../2020/results/Single_Query_Track.csv"

CLOUD_LOGICS=$(getLogics cloud)
PARALLEL_LOGICS=$(getLogics parallel)

# Note that python2 and python3 disagree on random choice function.
# Always use python3 to get reproducible results.
if ! check_seed_ok ${COMPETITION_SEED}; then
    echo "Invalid seed"
    exit 1;
fi

SEED=$(cat ${COMPETITION_SEED})
PYTHON=python3

if [ $# != 2 ]; then
    echo "Usage: $0 <smt-lib-root> <competition-root>"
    exit 1
fi

smt_lib_root=$1
competition_root=$2

mkdir -p final

printf "+++++++++++\n\nCLOUD TRACK\n\n"

preselect hard-only ${OUT_CLOUD}-hard ${CLOUD_LOGICS}
preselect unsolved-only ${OUT_CLOUD}-unsolved ${CLOUD_LOGICS}

sort ${OUT_CLOUD}-unsolved > ${OUT_CLOUD}-unsolved.sorted
mv ${OUT_CLOUD}-unsolved.sorted ${OUT_CLOUD}-unsolved
sort ${OUT_CLOUD}-hard > ${OUT_CLOUD}-hard.sorted
mv ${OUT_CLOUD}-hard.sorted ${OUT_CLOUD}-hard

genlogics ${OUT_CLOUD}-unsolved
genlogics ${OUT_CLOUD}-hard

picknums ${OUT_CLOUD}-hard-logics ${OUT_CLOUD}-unsolved-logics ${SELECTION_NUMBERS_CLOUD}

selectfinal ${SELECTION_NUMBERS_CLOUD} ${OUT_CLOUD}-hard ${OUT_CLOUD}-unsolved ${SELECTION_CLOUD}

printf "+++++++++++\n\nPARALLEL TRACK\n\n"

preselect hard-only ${OUT_PARALLEL}-hard ${PARALLEL_LOGICS}
preselect unsolved-only ${OUT_PARALLEL}-unsolved ${PARALLEL_LOGICS}

genlogics ${OUT_PARALLEL}-unsolved
genlogics ${OUT_PARALLEL}-hard

sort ${OUT_PARALLEL}-unsolved > ${OUT_PARALLEL}-unsolved.sorted
mv ${OUT_PARALLEL}-unsolved.sorted ${OUT_PARALLEL}-unsolved
sort ${OUT_PARALLEL}-hard > ${OUT_PARALLEL}-hard.sorted
mv ${OUT_PARALLEL}-hard.sorted ${OUT_PARALLEL}-hard

picknums ${OUT_PARALLEL}-hard-logics ${OUT_PARALLEL}-unsolved-logics ${SELECTION_NUMBERS_PARALLEL}

selectfinal ${SELECTION_NUMBERS_PARALLEL} ${OUT_PARALLEL}-hard ${OUT_PARALLEL}-unsolved ${SELECTION_PARALLEL}

echo "Scrambling benchmarks..."

${AWS_SCRAMBLER} ${smt_lib_root} \
    ${SELECTION_PARALLEL} \
    ${competition_root}/parallel \
    ${SEED} > final/parallel-map.csv

${AWS_SCRAMBLER} ${smt_lib_root} \
    ${SELECTION_CLOUD} \
    ${competition_root}/cloud \
    ${SEED} > final/cloud-map.csv

