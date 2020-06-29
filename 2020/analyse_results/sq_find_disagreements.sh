#!/bin/bash

csvcut -c benchmark,result ../results/Single_Query_Track.csv | \
	cut -d'/' -f2- | sort -u | grep -v unknown | sort | cut -d, -f1 | \
	uniq -c | grep ' 2 ' |cut -c9- > sq_disagreements
