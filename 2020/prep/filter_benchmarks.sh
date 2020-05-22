#!/bin/bash

# script to filter out broken benchmarks from the incremental track.

### function filter_benchmark
# Filters the benchmarks that occur in the given file.
# arg $1: the file containing the benchmarks that should be removed
# stdin: the file that should be filtered
# stdout: the filtered file
filter_benchmark () {
    perl -e '
    %filter=();
    $filtername=pop @ARGV;
    open FILTER, "<$filtername";
    while (<FILTER>) {
        $filter{$_} = 1;
    }
    while (<>) {
        print $_ if (!$filter{$_});
    }
    ' $1
}


filter_benchmark "SMT-LIB_incremental_broken_fp.txt" < SMT-LIB_incremental_benchmarks_all.txt > SMT-LIB_incremental_benchmarks_all_filtered.txt
filter_benchmark "SMT-LIB_incremental_broken_fp.txt" < SMT-LIB_incremental_benchmarks_new.txt > SMT-LIB_incremental_benchmarks_new_filtered.txt
