#!/bin/bash

if [ "$#" == 0 -o \! -d "$1" ]; then
  echo "USAGE: find_broken_fp.sh <path-to-smtlib>"
  echo "<path-to-smtlib> with three sub-directories"
  echo "  incremental: directory with of all directory benchmarks"
  echo "  non-incremental: directory with of all directory benchmarks"
  echo "  benchmarks-pending: directory with the benchmarks-pending directory"
  exit
fi

# find all benchmarks contains to_fp with a decimal in an FP logic
# (these should have been categorized as FPLRA)
# fix the name to upper case and add ./ to beginning using perl regex.
(cd $1/incremental; find *[fF][pP] -name \*.smt2 | \
	xargs egrep  'to_fp.*[0-9]\.[0-9]' | cut -d ':' -f1 | uniq | \
	perl -pe 's!^[^/]*/!./\U$&\E!'|sort) > SMT-LIB_incremental_broken_fp.txt
