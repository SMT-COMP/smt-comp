#!/bin/bash

JOBDIR=$1

sed -e 's/^\/incremental\/\(.*\)\/\([^\/]*\)$/\1 \2/' < ../prep/selection/final/benchmark_selection_incremental |\
while read dir file; do
	paste $JOBDIR/Job*_output/*Incremental*/$dir/*/$file/*.txt |\
		grep -E '(\bsat.*unsat|unsat.*\bsat)' &&\
		echo "... in $dir/$file"
done
