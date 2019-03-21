#!/bin/bash

set -e
set -u

# virtual best solver

# only keep the best (highest number of correct answers) result for each
# benchmark

# Column  3: benchmark id
#         8: status
#        10: wall time
#        14: correct answers

awk -F , '$8=="complete"' "$1"|
    sort -t , -k 3,3n -k 10,10n|
    sort -t , -k 3,3n -u
