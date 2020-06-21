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

# We search for benchmarks containing '(forall ' or '(exists ' in quantifier free divisions.

(cd $1/non-incremental; 
 grep -l -E '\((exists|forall) ' -R QF_*) | sort -u > blacklist_nonincremental_quantifiers.txt

# We search for two-dimensional arrays and arrays to Bool in non-incremental/ABV
# and for two-dimensional arrays in incremental/*a*lia

(cd $1/non-incremental; 
 grep -l -E '\(Array \(_ BitVec [0-9]*\) (\(Array |Bool)' -R ABV) | sort -u > blacklist_nonincremental_arraytype.txt
(cd $1/incremental; 
 grep -l -E '\(Array Int \(Array ' -R alia qf_alia qf_auflia) | \
 perl -pe 's/^[^\/]*/\U$&/' | sort -u > blacklist_incremental_arraytype.txt

