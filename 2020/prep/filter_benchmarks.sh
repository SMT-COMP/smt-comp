#!/bin/bash

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
