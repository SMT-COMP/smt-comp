#!/bin/bash

# Script to find benchmarks that should be removed from scoring, since they
# don't conform to the SMT-LIB standard or are in the wrong division.

if [ "$#" == 0 -o \! -d "$1" ]; then
  echo "USAGE: find_benchmarks.sh <path-to-smtlib>"
  echo "<path-to-smtlib> with three sub-directories"
  echo "  incremental: directory with of all directory benchmarks"
  echo "  non-incremental: directory with of all directory benchmarks"
  echo "  benchmarks-pending: directory with the benchmarks-pending directory"
  exit
fi

BENCHMARKDIR=$1

# We search for benchmarks containing '(mod ' or '(div ' in linear arithmetic
# or '(forall ' or '(exists ' in quantifier free divisions.

(cd $1/non-incremental; 
 grep -l -E '\((mod|div) ' -R *LI*;
 grep -l -E '\((exists|forall) ' -R QF_*) > blacklist_nonincremental.txt


