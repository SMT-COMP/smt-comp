#!/bin/bash

set -e
set -u

# print a list of benchmarks that occur in *every* argument file

declare -A BENCHMARKS

# count how often each benchmark name occurs
for FILE in "$@"
do
    OIFS="$IFS"
    IFS=$'\n'
    for NAME in $(awk -F , '{print $2;}' "$FILE"|sort -u)
    do
        if [[ ${BENCHMARKS[$NAME]+isset} ]]; then
            BENCHMARKS[$NAME]=$(( ${BENCHMARKS[$NAME]} + 1 ))
        else
            BENCHMARKS[$NAME]=1
        fi
    done
    IFS="$OIFS"
done

# print those benchmark names that occur $# times (and sort them)
for NAME in "${!BENCHMARKS[@]}"
do
    if [[ ${BENCHMARKS[$NAME]} -eq "$#" ]]; then
        echo "$NAME"
    fi
done|LC_ALL=C sort
