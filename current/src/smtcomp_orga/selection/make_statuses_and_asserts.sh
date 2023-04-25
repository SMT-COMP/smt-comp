#!/bin/sh

if [ "$#" != "2" ]; then
    echo "USAGE: ./make_status_asserts.sh <scrambler> <smtlib dir>"
    echo "  <scrambler>:  path to scrambler binary, compiled from "
    echo "                https://github.com/smt-comp/scrambler"
    echo "  <smtlib dir>: path to smtlib directory (either incremental or non-incremental"
    exit
fi

SCRAMBLER=$1
SMTLIB_DIR=$2
LANG=C

echo "benchmark,number of asserts,status"
cd $SMTLIB_DIR
find . -name '*.smt2' | sort | while read file; do
   n_asrts=$($SCRAMBLER -count-asserts true < "$file" 2>&1 >/dev/null | \
             sed -n 's/^; Number of assertions: \([0-9][0-9]*\)/\1/p')
   status=$(grep '([ \t]*set-info[ \t][ \t]*:status[ \t].*[ \t]*)' < "$file" | \
	    sed -n 's/.*[ \t]\(unsat\|sat\|unknown\).*/\1/p')
   echo "$file,$n_asrts,$status"
done
