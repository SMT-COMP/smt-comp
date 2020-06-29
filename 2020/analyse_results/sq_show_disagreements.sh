#!/bin/bash

(
	head -1 ../results/Single_Query_Track.csv
       	while read i; do 
		grep "$i" ../results/Single_Query_Track.csv
		echo
       	done < sq_disagreements
) | csvcut -c 'benchmark,solver,result,expected' | \
	cut -d/ -f2- | grep starexec-unknown$ | \
	grep -v starexec-unknown,starexec-unknown
