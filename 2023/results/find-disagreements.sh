#!/bin/bash -eu

#benchmark,solver,configuration,status,cpu time,wallclock time,memory usage,result,expected

INPUT=${1:-raw-results-sq.csv}
CUTWHAT=${2:-2,4,12,13}

cat $INPUT | csvcut -c benchmark,result | grep -v -e starexec-unknown -e '--' | sort |uniq | cut -d, -f1 |uniq -c |grep -v ' 1 '  | cut -c 9- > disagreeing-sq.txt

COMMA=""
PATTERN=""
while read bench; do
    PATTERN="$PATTERN$COMMA$bench"
    COMMA="|"
done < disagreeing-sq.txt
# remove the non informative result and select the problematic files
cat $INPUT | grep -v -e ",starexec-unknown," | grep -E ",($PATTERN)," | LANG=C sort -t, -k 1 | csvcut -c$CUTWHAT


# Solver with answers different from the others
#| grep -v -E "vampire_4.8_smt_pre|iProver-3.8-Final|z3-Owl-Final|OSTRICH 1.3 SMT-COMP|UltimateIntBlastingWrapper\+SMTInterpol|Z3-Noodler"
