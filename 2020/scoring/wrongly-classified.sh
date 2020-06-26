#!/bin/bash

# This script searches for Jobs where the solver first reported error or
# unsupported and then said sat.  These should be regarded as unknown, but
# the post-processor currently classifies them as sat.
# We create a new csv file with the pair ids and result starexec-unknown.

if [ "$#" == 0 -o \! -d "$1" ]; then
	echo "USAGE: wrongly-classified.sh <path-to-single-query-job-output>"
	exit
fi

(
echo 'pair id,benchmark,solver,configuration,result'
cd "$1"
find . -name \*.txt | 
while read file; do 
	perl -ne '$seenerr=1 if /\t(\(error|unsupported)/; 
	          if (/\tsat/ && $seenerr) {
			$ARGV =~ m(^\./(.*)/([^/]*)___([^/]*)/([^/]*\.smt2)/(\d+).txt$);
			$bench = "$1/$4";
			$solver = $2;
			$configuration = $3;
			$pairid = $5;
			print "$pairid,$bench,$solver,$configuration,starexec-unknown\n";
		  }' "$file"; 
done) > SQ-wrong-sat-result.csv
