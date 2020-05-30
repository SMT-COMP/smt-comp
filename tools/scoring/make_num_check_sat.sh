#!/bin/sh

if [ "$#" != "1" ]; then
    echo "USAGE: ./make_num_check_sat.sh <smtlib dir>"
    echo "  <smtlib dir>: path to incremental smtlib directory"
    exit
fi

LANG=C
SMTLIB_DIR=$1

echo "benchmark,num_check_sat"
cd $SMTLIB_DIR
find . -name '*.smt2' | sort | while read file; do
   # convert logic to upper case;
   benchmark=$(echo $file | perl -pe 's!^\./([^/]*/)!\U$1\E!')
   num_check_sat=$(grep -o '(check-sat)' < "$file" | wc -l)
   echo "$benchmark,$num_check_sat"
done
