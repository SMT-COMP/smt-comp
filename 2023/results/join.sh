#!/bin/bash -eu

# Download Jobs from StarExec even if they already exist
FORCE_DOWNLOAD=0

# Jobs in the order "competition best-of non-competing"
sq="59410 59554 59586 59599 59668"
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
        test -d "Job${id}"
        INPUT="Job${id}/Job${id}_info.csv"
        echo -n " Job${id}"

        if [ "$track" == "mv" ]; then
            TMPINPUT_NOQUOTE=${TMPDIR}/input_noquote.csv
            TMPINPUT_FIXED=${TMPDIR}/input_fixed.csv
            echo -n "(fix column)"
            tr -d '"' < $INPUT > $TMPINPUT_NOQUOTE
            ./fix_starexec_custom_column.py $TMPINPUT_NOQUOTE $TMPINPUT_FIXED
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
            eval tail -n +2 $TMPFILE >> $OUTPUT
            rm $TMPFILE
        else
            # convert all files to same line ending
            cat $TMPINPUT > $OUTPUT
        fi
    done
    echo
done
