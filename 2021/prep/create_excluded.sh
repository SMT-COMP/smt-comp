#!/bin/bash

# Script to find benchmarks that should be removed from scoring, since they
# don't conform to the SMT-LIB standard or are in the wrong division.

if [ "$#" != 2 -o \! -d "$1"  -o \! -e "$2" ]; then
  echo "USAGE: create_excluded.sh <path-to-smtlib> <smtinterpol.jar>"
  echo "<path-to-smtlib> with three sub-directories"
  echo "  incremental: directory with of all directory benchmarks"
  echo "  non-incremental: directory with of all directory benchmarks"
  echo "<smtinterpol.jar> A jar file containing a recent version of"
  echo "  SMTInterpol for checking non-linearity.  This jar file can"
  echo "  be extracted from the uploaded solver."
  exit
fi

BENCHMARKDIR=$1
SMTINTERPOL=$(readlink -f $2)

# language independent sort order
LANG=C
export LANG

# We search for non-linear benchmarks using SMTInterpol

(cd $BENCHMARKDIR;
 find incremental/*L[IR]* -name \*.smt2 | \
	while read benchmark; do
		echo '(echo "'$benchmark'")'
		echo '(include "'$benchmark'")'
		echo '(reset)'
      	done | \
	java -jar $SMTINTERPOL -script LinearArithmeticChecker 2>/dev/null | \
	grep -v '^success\|unknown\|".*"$' |\
        sort
) > excluded_incremental_nonlinear.txt


(cd $BENCHMARKDIR;
 find non-incremental/*L[IR]* -name \*.smt2 | \
	while read benchmark; do
		echo '(echo "'$benchmark'")'
		echo '(include "'$benchmark'")'
		echo '(reset)'
      	done | \
	java -jar $SMTINTERPOL -script LinearArithmeticChecker 2>/dev/null | \
	grep -v '^success\|unknown\|".*"$' |\
	sort
) > excluded_nonincremental_nonlinear.txt

# We search for benchmarks containing '(forall ' or '(exists ' in quantifier free divisions.

(cd $BENCHMARKDIR; 
 grep -l -E '\((exists|forall) ' -R non-incremental/QF_* | sort
) > excluded_nonincremental_quantifiers.txt


(cd $BENCHMARKDIR; find non-incremental/*FP -name \*.smt2 | \
	xargs egrep -l 'to_fp.*[0-9]\.[0-9]' | sort
) > excluded_nonincremental_fp.txt
(cd $BENCHMARKDIR; find incremental/*FP -name \*.smt2 | \
	xargs egrep -l 'to_fp.*[0-9]\.[0-9]' | sort
) > excluded_incremental_fp.txt

cat excluded_*incremental_*.txt | sort -u > SMT-LIB_excluded.txt

