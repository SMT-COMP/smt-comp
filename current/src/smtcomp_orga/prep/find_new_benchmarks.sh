#!/bin/bash

YEAR=2022

# new benchmarks were not clearly marked.  We use the family names to
# grep for new benchmarks.

grep -E '^\./[A-Z_]*/($YEAR|2021(0304-uhbexamples|0304-Y86|1.*))' \
	< SMT-LIB_non_incremental_benchmarks_all.txt \
	> SMT-LIB_non_incremental_benchmarks_new.txt

grep -E '^\./[A-Z_]*/($YEAR|20210110-Coffin)' \
	< SMT-LIB_incremental_benchmarks_all.txt \
	> SMT-LIB_incremental_benchmarks_new.txt
