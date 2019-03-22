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

cat "$1"| sort -t , -k 3,3n -k 14,14nr| sort -t , -k 3,3n -u
