#!/bin/bash

set -e
set -u

# virtual best solver

# only keep the best (fastest, based on wall time) result for each benchmark

# Column  3: benchmark id
#         8: status
#        10: wall time
#        12: result

awk -F , '$8=="complete" && ($12=="sat" || $12=="unsat")' "$1"|
    sort -t , -k 3,3n -k 10,10n|
    sort -t , -k 3,3n -u
