#!/bin/bash

set -e
set -u

# CPU time over wall time (for each solver)

# $1: CSV file

# Column  4: solver name
#         5: solver id
#         9: cpu time
#        10: wall time
awk -F , '{SOLVER[$5]=$4; CPU_TIME[$5]+=$9; WALL_TIME[$5]+=$10} END {for (SOLVER_ID in SOLVER) printf("%s,%s,%.1f\n", SOLVER_ID, SOLVER[SOLVER_ID], CPU_TIME[SOLVER_ID]/WALL_TIME[SOLVER_ID])}' "$1"|sort -t , -k 2,2f

awk -F , '{CPU_TIME+=$9; WALL_TIME+=$10} END {printf("Total,Total,%.1f\n", CPU_TIME/WALL_TIME)}' "$1"
