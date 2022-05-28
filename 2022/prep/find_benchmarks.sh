#!/bin/bash

SCRAMBLER=`dirname $(readlink -f "$0")`/../../../scrambler/scrambler
YEAR=2022
LANG=C  # fix sorting
export LANG

if [ "$#" == 0 -o \! -d "$1" ]; then
  echo "USAGE: find_benchmarks.sh <path-to-smtlib>"
  echo "<path-to-smtlib> with three sub-directories"
  echo "  incremental: directory with of all directory benchmarks"
  echo "  non-incremental: directory with of all directory benchmarks"
  echo "  benchmarks-pending: directory with the benchmarks-pending directory"
  exit
fi

for track in incremental non-incremental; do
  utrack=$(echo $track | tr '-' '_')
  # find benchmarks and convert logic to upper-case
  (cd $1/$track; find -name \*.smt2) | perl -pe 's!^./[^/]*/!\U$&\E!' | sort > SMT-LIB_${utrack}_benchmarks_all.txt
  # find new benchmarks
  #(cd $1/pending-$YEAR/DONE/$track; find -name \*.smt2) | sort > SMT-LIB_${utrack}_benchmarks_new.txt
done

../../tools/selection/make_statuses_and_asserts.sh $SCRAMBLER $1/non-incremental > SMT-LIB_non_incremental_benchmarks_all_assertions.csv
../../tools/scoring/make_num_check_sat.sh $1/incremental > SMT-LIB_incremental_benchmarks_num_check_sat.csv
