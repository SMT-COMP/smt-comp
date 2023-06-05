#! /bin/bash -eux

export LANG=C.UTF-8

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
        ../../registration/solvers_divisions_all.csv
}

function createPairFile {
    track=$1
    $PYTHON ${CREATE_PAIR_FILE} \
         -t ${track} \
        ${SCRIPTDIR}/final/${track}-map.csv \
        ../../registration/solvers_divisions_all.csv \
        > ${competition_root}/${track}-pairs.csv
}


function preselect {
    mode=$1
    output=$2
    logics=$3
    $PYTHON $SELECT_PRE \
        --justification "$FILTER_CSV_2020" \
        --justification "$FILTER_CSV_2019" \
        --justification "$FILTER_CSV_2018" \
        --benchmarks "$BENCHMARKS_WITHOUT_BLACKLISTED" \
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
    track=$4
    ${PICKNUM} \
        ${hard_logics} \
        ${unsolved_logics} \
        ${MIN_BENCHMARKS} \
        -d ../../new-divisions.json \
        -t ${track} \
        --seed ${SEED} \
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
if ! check_seed_ok ${COMPETITION_SEED}; then
    echo "Invalid seed"
    exit 1;
fi

SEED=$(cat ${COMPETITION_SEED})

echo "Seed: $SEED"

SCRIPTDIR=`get_abs_path $(dirname "$0")`

TMPDIR=$(mktemp -d --tmpdir "aws_make_selection.tmp.XXX")

if [ -z ${KEEP_INTERMEDIARY_FILES+x} ]; then
    trap "rm -rf ${TMPDIR}" EXIT
else
    echo "Intermediary files are in $TMPDIR"
fi

OUT_CLOUD="${TMPDIR}/benchmark_selection_cloud"
SELECTION_NUMBERS_CLOUD="${TMPDIR}/benchmark_selection_cloud_numbers.json"
SELECTION_CLOUD="${SCRIPTDIR}/final/benchmark_selection_cloud"
OUT_PARALLEL="${TMPDIR}/benchmark_selection_parallel"
SELECTION_NUMBERS_PARALLEL="${TMPDIR}/benchmark_selection_parallel_numbers.json"
SELECTION_PARALLEL="${SCRIPTDIR}/final/benchmark_selection_parallel"

MIN_BENCHMARKS=400

GET_LOGICS=${SCRIPTDIR}/../../../tools/prep/extract_aws_data_from_solvers_divisions.py
SELECT_PRE="$SCRIPTDIR/../../../tools/selection/selection_additive.py"
PICKNUM="${SCRIPTDIR}/aws_pick_instance_nums.py" 
SELECT_FINAL="${SCRIPTDIR}/aws_select_final.py"
AWS_SCRAMBLER="${SCRIPTDIR}/aws_scramble_and_rename.sh"
FILTER_BLACKLISTED="${SCRIPTDIR}/aws_filter_blocklisted.sh"
CREATE_PAIR_FILE=${SCRIPTDIR}/../../../tools/prep/aws_create_pair_files.py

BENCHMARKS="$SCRIPTDIR/../SMT-LIB_non_incremental_benchmarks_all.txt"
BENCHMARKS_WITHOUT_BLACKLISTED="${TMPDIR}/SMT-LIB_non_incremental_benchmarks_all_without_blocklisted.txt"
FILTER_CSV_2018="$SCRIPTDIR/../../../2018/csv/Main_Track.csv"
FILTER_CSV_2019="$SCRIPTDIR/../../../2019/results/Single_Query_Track.csv"
FILTER_CSV_2020="$SCRIPTDIR/../../../2020/results/Single_Query_Track.csv"

BLACKLIST="$SCRIPTDIR/../SMT-LIB_excluded.txt"

# Note that python2 and python3 disagree on random choice function.
# Always use python3 to get reproducible results.
PYTHON=python3

CLOUD_LOGICS=$(getLogics cloud)
PARALLEL_LOGICS=$(getLogics parallel)

if [ $# != 2 ]; then
    echo "Usage: $0 <smt-lib-root> <competition-root>"
    exit 1
fi

smt_lib_root=$1
competition_root=$2

rm -rf ${competition_root}
mkdir -p final

echo "Filtering blocklisted benchmarks from non-incremental"

${FILTER_BLACKLISTED} ${BLACKLIST} ${BENCHMARKS} > ${BENCHMARKS_WITHOUT_BLACKLISTED}

printf "+++++++++++\n\nCLOUD TRACK\n\n"

preselect hard-only ${OUT_CLOUD}-hard ${CLOUD_LOGICS}
preselect unsolved-only ${OUT_CLOUD}-unsolved ${CLOUD_LOGICS}

sort ${OUT_CLOUD}-unsolved > ${OUT_CLOUD}-unsolved.sorted
mv ${OUT_CLOUD}-unsolved.sorted ${OUT_CLOUD}-unsolved
sort ${OUT_CLOUD}-hard > ${OUT_CLOUD}-hard.sorted
mv ${OUT_CLOUD}-hard.sorted ${OUT_CLOUD}-hard

genlogics ${OUT_CLOUD}-unsolved
genlogics ${OUT_CLOUD}-hard

picknums ${OUT_CLOUD}-hard-logics ${OUT_CLOUD}-unsolved-logics ${SELECTION_NUMBERS_CLOUD} cloud

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

picknums ${OUT_PARALLEL}-hard-logics ${OUT_PARALLEL}-unsolved-logics ${SELECTION_NUMBERS_PARALLEL} parallel

selectfinal ${SELECTION_NUMBERS_PARALLEL} ${OUT_PARALLEL}-hard ${OUT_PARALLEL}-unsolved ${SELECTION_PARALLEL}

echo "Scrambling benchmarks..."

${AWS_SCRAMBLER} ${smt_lib_root} \
    ${SELECTION_PARALLEL} \
    ${competition_root}/parallel \
    ${SEED} > ${SCRIPTDIR}/final/parallel-map.csv

${AWS_SCRAMBLER} ${smt_lib_root} \
    ${SELECTION_CLOUD} \
    ${competition_root}/cloud \
    ${SEED} > ${SCRIPTDIR}/final/cloud-map.csv

echo "Creating pair files"

createPairFile parallel
createPairFile cloud
