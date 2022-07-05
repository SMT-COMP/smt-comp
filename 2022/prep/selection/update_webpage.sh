#!/bin/sh

YEAR=2022
DIVISIONS=../../new-divisions.json
BENCHMARKS_SQ=final/benchmark_selection_single_query
BENCHMARKS_INC=final/benchmark_selection_incremental
#BENCHMARKS_MV=final/benchmark_selection_model_validation
#BENCHMARKS_UC=final/benchmark_selection_unsat_core
#BENCHMARKS_PE=final/benchmark_selection_proof_exhibition
MAKE_DIVISION=../../../tools/selection/prepare_benchmark_ymls.py
OUTPUT_SOLVERS=../../../../smt-comp.github.io/_participants_$YEAR/
OUTPUT_DIVISIONS=../../../../smt-comp.github.io/_divisions_$YEAR/
NCDIR=non_competing
EXPERIMENTAL_CSV=../../experimental.csv


#mkdir -p $NCDIR
#
#../../../tools/prep/extract_data_from_solvers_divisions.py -d $DIVISIONS -c ../../registration/canon_solvers.json -n $NCDIR ../../registration/solvers_divisions_final.csv $OUTPUT_SOLVERS $YEAR
#
#$MAKE_DIVISION -d $DIVISIONS -y $YEAR --single_query $BENCHMARKS_SQ --incremental $BENCHMARKS_INC --model_validation $BENCHMARKS_MV --unsat_core $BENCHMARKS_UC --single_query-noncompetitive $NCDIR/single_query --incremental-noncompetitive $NCDIR/incremental --unsat_core-noncompetitive $NCDIR/unsat_core --model_validation-noncompetitive $NCDIR/model_validation $OUTPUT_DIVISIONS --experimental $EXPERIMENTAL_CSV

$MAKE_DIVISION -d $DIVISIONS -y $YEAR --single_query $BENCHMARKS_SQ --incremental $BENCHMARKS_INC --experimental $EXPERIMENTAL_CSV $OUTPUT_DIVISIONS
# --model_validation $BENCHMARKS_MV --unsat_core $BENCHMARKS_UC --proof_exhibition $BENCHMARKS_PE
