#!/bin/bash

# Download Jobs from StarExec even if they already exist
FORCE_DOWNLOAD=0

# Jobs in the order "competition best-of non-competing"
Single_Query="47304 47543 47546"
Incremental="47350 47540 47689"
Model_Validation="47305 47542 47727"
Unsat_Core="47790 47815 47866 47867"

COLORDER=../../tools/process-results/unify_column_order.py

for track in Single_Query Incremental Model_Validation Unsat_Core; do
    echo -n "$track:"
    OUTPUT="${track}_Track.csv"
    # rm -f $OUTPUT
    for id in ${!track}; do
        if [ "$FORCE_DOWNLOAD" == "1" -o \! -d "Job${id}" ]; then
            curl -o Job${id}_info.zip "https://www.starexec.org/starexec/secure/download?type=job&id=${id}&returnids=true&getcompleted=false"
            unzip Job${id}_info.zip
        fi
        INPUT="Job${id}/Job${id}_info.csv"
        echo -n " Job${id}"
        if [ -e $OUTPUT ]; then
            TMPFILE=$(mktemp --suffix=.csv)
            $COLORDER -o $OUTPUT -a $INPUT > $TMPFILE

            # For rerun jobs, remove one `/` to make all benchmark
            # paths on the same level
            FILTER=
            if [ "$id" == "47866" -o $id == "47867" ]; then
                FILTER="| sed -e 's!Unsat Core Rerun/!Unsat Core Rerun !'"
            fi

            # sanity check: head must be equal now
            diff <(head -1 $TMPFILE) <(head -1 $OUTPUT)
            eval tail -n +2 $TMPFILE $FILTER >> $OUTPUT
            rm $TMPFILE
        else
            # convert all files to same line ending
            dos2unix -q -n $INPUT $OUTPUT
        fi
    done
    echo
done
