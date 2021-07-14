#!/bin/bash

# Download Jobs from StarExec
DOWNLOAD=0

# Jobs in the order "competition best-of non-competing"
Single_Query="47304 47543 47546"
Incremental="47350 47540 47689"
Model_Validation="47305 47542 47727"
Unsat_Core="47790 47815"

for track in Single_Query Incremental Model_Validation Unsat_Core; do
    OUTPUT="${track}_Track.csv"
    rm -f $OUTPUT
    for id in ${!track}; do
	if [ "$DOWNLOAD" == "1" -o \! -d "Job${id}" ]; then
	    wget -OJob${id}_info.zip "https://www.starexec.org/starexec/secure/download?type=job&id=${id}&returnids=true&getcompleted=false"
	    unzip Job${id}_info.zip
	fi
	INPUT="Job${id}/Job${id}_info.csv"
        if [ -e $OUTPUT ]; then
	    # sanity check: head must be equal
	    diff <(head -1 $INPUT) <(head -1 $OUTPUT)
	    tail -n +1 $INPUT >> $OUTPUT
	else
	    cat $INPUT > $OUTPUT
	fi
    done
done
