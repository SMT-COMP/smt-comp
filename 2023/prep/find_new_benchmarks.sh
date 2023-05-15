#!/bin/bash

YEAR=2023

# new benchmarks were not clearly marked.  We use the family names to
# grep for new benchmarks.

# last year the script was broken and 2022 benchmarks were not included.
# we mark them as new as well.

grep -E '^\./[A-Z_]*/('$YEAR'|2022)' \
	< SMT-LIB_non_incremental_benchmarks_all.txt \
	> SMT-LIB_non_incremental_benchmarks_new.txt

grep -E '^\./[A-Z_]*/('$YEAR'|2022)' \
	< SMT-LIB_incremental_benchmarks_all.txt \
	> SMT-LIB_incremental_benchmarks_new.txt
