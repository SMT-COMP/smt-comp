#!/bin/bash

mkdir -p logics

TRACKS="single_query incremental unsat_core model_validation proof_exhibition cloud parallel"
MVREGEX="QF_(AX?)?(UF)?(BV)?(FP)?(DT)?([NL][IR]*A|[IR]DL)?"

cat SMT-LIB_incremental_benchmarks_all.txt | cut -d/ -f2 | uniq > logics/track_incremental
cat SMT-LIB_non_incremental_benchmarks_all.txt | cut -d/ -f2 | uniq > logics/track_single_query
cp logics/track_single_query logics/track_unsat_core
cp logics/track_single_query logics/track_proof_exhibition
cp logics/track_single_query logics/track_cloud
cp logics/track_single_query logics/track_parallel
grep -E "^$MVREGEX$" logics/track_single_query > logics/track_model_validation

(
COMMA1=""
echo '{'
for track in $TRACKS; do
    echo $COMMA1
    echo "\"track_$track\" :"
    jq -R '.' < logics/track_${track} | jq --slurp
    COMMA1=","
done
echo '}'
) | jq > ../divisions.json


(
COMMA1=""
echo '{'
for track in $TRACKS; do
    echo $COMMA1
    echo "\"track_$track\":{"
    COMMA2=""
    > logics/all
    if [ "$track" = "model_validation" ];then
        TRACKS_REGEX=divisions-regex-mv.txt
    else
        TRACKS_REGEX=divisions-regex.txt
    fi
    while read division regex
    do
        if grep -E "^$regex$" < logics/track_${track} > logics/division; then
            echo $COMMA2
            echo "\"$division\": "
            jq -R '.' < logics/division | jq --slurp
            COMMA2=","
            cat logics/division >> logics/all
        fi
        rm -f logics/division
    done < $TRACKS_REGEX
    echo '}'
    COMMA1=","
    # the following command checks whether each logic occurs exactly once.
    # it prints differences to stderr.
    LANG=C sort logics/all | diff -u0 logics/track_${track} - >&2
    rm logics/all
done
echo '}'
) | jq > ../new-divisions.json
