#!/bin/sh

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 base-result.csv [adjunct-result.csv [...]]"
    exit 1
fi

bname=$(csvcut $1 -c 2 |tail +2 |head -1 |cut -d '/' -f 1)

(
cat $1;
shift
while [[ $# -ne 0 ]]; do
    adjname=$(csvcut $1 -c 2|tail +2 |head -1 |cut -d '/' -f1)
    cat $1 |tail +2 |while read -r line; do
        echo ${line/${adjname}/${bname}};
    done
    shift
done
) |csvsort -c 2

