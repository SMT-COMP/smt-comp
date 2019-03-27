#!/bin/bash

set -e
set -u

# virtual best solver

# only keep the best (highest number of reduction) result for each benchmark

# Column  3: benchmark id
#         6: status
#         7: result

awk -F , '$6=="complete" && $7=="unsat"' "$1"|
    sort -t , -k 3,3n -k 9,9n|
    sort -t , -k 3,3n -u
