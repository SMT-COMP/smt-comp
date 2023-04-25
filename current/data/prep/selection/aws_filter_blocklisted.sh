#!/bin/sh

if [ $# != 2 ]; then
    echo "Usage: $0 <blocklist> <all-benchmarks>"
    exit 1
fi

TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

BLOCKLIST_NONINCREMENTAL_STANDARDISED=${TMPDIR}/blocklist-non-incremental-standardised.txt

cat $1 |grep -v '^incremental/' |sed 's,non-incremental/,./,g' > ${BLOCKLIST_NONINCREMENTAL_STANDARDISED}

grep -F -f ${BLOCKLIST_NONINCREMENTAL_STANDARDISED} -v $2


