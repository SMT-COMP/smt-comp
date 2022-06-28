#!/bin/sh

# Create solvers.zip file to link solvers into a fresh space.
#
# Create a new space in starexec, move to that space, open Sub spaces,
# choose "Upload Sub Spaces" and upload the solvers.zip file.

INPUT_FILE="solvers_divisions.csv"
SOLVER_ID="Preliminary Solver ID"

mkdir -p download
csvcut -c "$SOLVER_ID","Solver Name" $INPUT_FILE | tail -n +2 | perl -ne '/(.*),(.*)/ and $id=$1 and $name=$2; while ($id =~ s/(\d+)(\([^)]*\))?//) { print "$1\n" }' | sort -u | while read ID; do 
    echo downloading ${ID}...
    test -e download/${ID}.zip || curl -o download/${ID}.zip 'https://www.starexec.org/starexec/secure/download?type=solver&id='${ID}
    test -e download/solver-${ID}.html || curl -o download/solver-${ID}.html 'https://www.starexec.org/starexec/secure/details/solver.jsp?id='${ID}
done
