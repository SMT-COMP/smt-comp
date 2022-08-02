#!/bin/bash

# Download Jobs from StarExec even if they already exist
FORCE_DOWNLOAD=0

# Jobs in the order "competition best-of non-competing"
sq="53368 53987 53946 54095"
inc="53370 53992 54094"
mv="53777 53989 54093"
uc="53812 53998 54121"
pe="53819"

COLORDER=../../tools/process-results/unify_column_order.py

TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

for track in sq inc mv uc pe; do
    echo -n "$track:"
    OUTPUT="raw-results-${track}.csv"
    rm -f $OUTPUT
    for id in ${!track}; do
        if [ "$FORCE_DOWNLOAD" == "1" -o \! -d "Job${id}" ]; then
            curl -o Job${id}_info.zip "https://www.starexec.org/starexec/secure/download?type=job&id=${id}&returnids=true&getcompleted=false"
            unzip Job${id}_info.zip
        fi
        INPUT="Job${id}/Job${id}_info.csv"
        echo -n " Job${id}"
        if [ -e $OUTPUT ]; then
            TMPFILE=${TMPDIR}/job.csv
            $COLORDER -o $OUTPUT -a $INPUT > $TMPFILE

            # sanity check: head must be equal now
            diff <(head -1 $TMPFILE) <(head -1 $OUTPUT)
            eval tail -n +2 $TMPFILE $FILTER >> $OUTPUT
            rm $TMPFILE
        else
            # convert all files to same line ending
            cat $INPUT > $OUTPUT
        fi
    done
    echo
done
