#!/bin/bash

# Download Jobs from StarExec even if they already exist
FORCE_DOWNLOAD=0

# Jobs in the order "competition best-of non-competing"
sq="59410 59554 59586 59599"
inc="59572 59598 59666"
mv="59579 59619 59702"
uc="59592 59620 59700"
pe="59571"

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

        if [ "$track" == "mv" ]; then
            TMPINPUT_FIXED=${TMPDIR}/input_fixed.csv
            echo -n "(fix column)"
            ./fix_starexec_custom_column.py $INPUT $TMPINPUT_FIXED
            if [ -e ./fix-results-$id.csv.gz ]; then
                TMPINPUT=${TMPDIR}/input_merged.csv
                echo -n "(merge with fixed dolmen)"
                ./merge_local_results_mv.py ./fix-results-$id.csv.gz $TMPINPUT_FIXED $TMPINPUT
            else
                TMPINPUT=$TMPINPUT_FIXED
            fi
        else
            TMPINPUT=$INPUT
        fi

        if [ -e $OUTPUT ]; then
            TMPFILE=${TMPDIR}/job.csv
            $COLORDER -o $OUTPUT -a $TMPINPUT > $TMPFILE

            # sanity check: head must be equal now
            diff <(head -1 $TMPFILE) <(head -1 $OUTPUT)
            eval tail -n +2 $TMPFILE $FILTER >> $OUTPUT
            rm $TMPFILE
        else
            # convert all files to same line ending
            cat $TMPINPUT > $OUTPUT
        fi
    done
    echo
done
