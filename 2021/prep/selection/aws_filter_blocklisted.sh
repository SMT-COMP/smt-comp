#!/bin/sh

if [ $# != 2 ]; then
    echo "Usage: $0 <blocklist> <all-benchmarks>"
    exit 1
fi

BLOCKLIST_NONINCREMENTAL_STANDARDISED=$(mktemp)_blocklist-non-incremental-standardised.txt

cat $1 |grep -v '^incremental/' |sed 's,non-incremental/,./,g' > ${BLOCKLIST_NONINCREMENTAL_STANDARDISED}

grep -F -f ${BLOCKLIST_NONINCREMENTAL_STANDARDISED} -v $2

rm ${BLOCKLIST_NONINCREMENTAL_STANDARDISED}

