#!/bin/bash

SCORE="../../tools/scoring/score.py"
BESTTOCSVS="../../tools/previous-best/best_solvers_to_csv.py"

SINGLE_QUERY_RESULTS_2019="../../2019/results/Single_Query_Track.csv"
INCREMENTAL_RESULTS_2019="../../2019/results/Incremental_Track.csv"
UNSAT_CORE_RESULTS_2019="../../2019/results/Unsat_Core_Track.csv"
MODEL_VALIDATION_RESULTS_2019="../../2019/results/Model_Validation_Track.csv"

INCREMENTAL_NUM_CHECKSATS_2019="../../2019/prep/incremental_num_check_sat.csv"

SOLVERS_DIVISIONS_2019="../../2019/registration/solvers_divisions_final.csv"
SOLVERS_DIVISIONS_2020="../../2020/registration/solvers_divisions_final.csv"

SOLVERS_DIVISIONS_SUGGESTIONS="solvers_divisions_suggestions.csv"

# $1 - track for score.py (either sq, inc, mv, or uc)
# $2 - old result file (csv)
# $3 - path to the last-year winners csv (will be overwritten)
# $4 - the result csv of the track given in $1
# $5 - if nonempty, the number of check-sats for the incremental script
function getBest {
    bestof_par=$(mktemp).csv;
    bestof_seq=$(mktemp).csv;

    if [ -z $5 ]; then
        inc_arg=""
    else
        inc_arg="-i $5"
    fi

    ${SCORE} -T $1 -y 2019 -t $2 -c $4 -S ${SOLVERS_DIVISIONS_2019} \
        -b ${bestof_par} $(echo ${inc_arg}) > /dev/null
    ${SCORE} -T $1 -y 2019 -t $2 -c $4 -S ${SOLVERS_DIVISIONS_2019} \
        -b ${bestof_seq} -s $(echo ${inc_arg}) > /dev/null

    header=$(cat ${bestof_par} |head -1)

    echo ${header} > $3
    (cat ${bestof_par} |tail +2; cat ${bestof_seq} |tail +2) |sort |uniq >> $3
    rm ${bestof_par} ${bestof_seq}
}

bestof_sq=bestof_sq.csv;
getBest sq 2400 ${bestof_sq} ${SINGLE_QUERY_RESULTS_2019}

bestof_in=bestof_inc.csv;
getBest inc 2400 ${bestof_in} ${INCREMENTAL_RESULTS_2019} ${INCREMENTAL_NUM_CHECKSATS_2019}

bestof_uc=bestof_uc.csv;
getBest uc 2400 ${bestof_uc} ${UNSAT_CORE_RESULTS_2019}

bestof_mv=bestof_mv.csv;
getBest mv 2400 ${bestof_mv} ${MODEL_VALIDATION_RESULTS_2019}

${BESTTOCSVS} \
    -s ${bestof_sq} \
    -u ${bestof_uc} \
    -i ${bestof_in} \
    -m ${bestof_mv} \
    -o ${SOLVERS_DIVISIONS_2019} \
    -n ${SOLVERS_DIVISIONS_2020} \
    -y 2019 \
    -O ${SOLVERS_DIVISIONS_SUGGESTIONS}

echo "Suggestions written to ${SOLVERS_DIVISIONS_SUGGESTIONS}."
echo "Check and add them to ${SOLVERS_DIVISIONS_2020}."
