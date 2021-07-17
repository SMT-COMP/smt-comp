#!/bin/bash
PYTHON=python3

FORCE_STATUS_COMPUTATION=0
Cloud="cloud"
Parallel="parallel"

smtlib_root=$1

for track in Cloud Parallel; do
    echo -n "$track: "
    InstanceMap="../prep/selection/final/${!track}-map.csv"

    if [ ! -e $InstanceMap ]; then
        echo "Mapping between competition and smt-lib names not"\
            "found in $InstanceMap";
        exit 1
    fi

    InstanceStatuses="${!track}-track/aws-instance-statuses.csv"

    if [ "$FORCE_STATUS_COMPUTATION" == "1" -o \! -e "$InstanceStatuses" ]; then

        if [ $# != "1" ]; then
            echo "Instance statuses not available.  Please uncompress"\
                 "them to $InstanceStatuses or provide the path to smtlib-base"\
                 "as argument."
            echo "Usage: $0 <path-to-smtlib>"
            exit 1
        fi
        $PYTHON ./aws-extract-starexec-status.py -m $InstanceMap -p $smtlib_root \
            > ${InstanceStatuses}
        cd ${!track}-track
        tar zcf aws-instance-statuses.tar.gz aws-instance-statuses.csv
        cd ..
    fi

    echo ${!track}-track/results.csv

    echo "Removing duplicate instances and fixing cvc5-gg PARSE_ERRORs to timeouts"
    for name in $(csvcut -c 'smtlib name' \
            ../prep/selection/final/${!track}-map.csv \
            |sort |uniq -d); do
        csvgrep -c 'smtlib name' -m "$name" \
            ../prep/selection/final/${!track}-map.csv \
            |csvcut -c 'competition name' \
            |tail -1 \
            |sed "s!\(.*\)!${!track}_new\1!g"
    done \
    |csvgrep -c 'benchmark' -i -f /dev/stdin ${!track}-track/results.csv \
    |awk -F, '
        BEGIN {OFS=","}
        {
            if ($2 == "cvc5gg" && $3 == "PARSE_ERROR" && $4 ~ "UNSATISFIABLE") {
                $3 = "TIMEOUT"; $4 = ""
            }
            print
        }
    ' \
    |unix2dos > ${!track}-track/results-cleaned.csv


    ./mapResults.py \
        -r ${!track}-track/results-cleaned.csv \
        -m ../prep/selection/final/${!track}-map.csv \
        -s ${!track}-track/aws-instance-statuses.csv \
        -p "${!track}_new" \
        -n ../prep/aws-spaces/aws_solver_name_to_solver_id.csv \
        -q "Competition - $track Track" \
        > raw-results-${!track}.csv
done
