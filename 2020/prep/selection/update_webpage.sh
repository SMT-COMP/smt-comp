#!/bin/sh

YEAR=2020
DIVISIONS=../../divisions.json
BENCHMARKS_SQ=final/benchmark_selection_single_query
BENCHMARKS_INC=final/benchmark_selection_incremental
BENCHMARKS_MV=final/benchmark_selection_model_valalidation
BENCHMARKS_UC=final/benchmark_selection_unsat_core
MAKE_DIVISION=../../../tools/selection/prepare_benchmark_ymls.py
OUTPUT=../../../../smt-comp.github.io/_divisions_$YEAR/
NC=non-competing
BENCHMARKS_INC=final/benchmark_selection_incremental
BENCHMARKS_MV=final/benchmark_selection_model_validation
BENCHMARKS_UC=final/benchmark_selection_unsat_core


mkdir -p non_competing

../../../tools/prep/extract_data_from_solvers_divisions.py -d $DIVISIONS -c ../../registration/canon_solvers.json -n non_competing ../../registration/solvers_divisions_final.csv ~/work/smtcomp/smt-comp.github.io/_participants_$YEAR $YEAR

$MAKE_DIVISION -d $DIVISIONS -y $YEAR --single_query $BENCHMARKS_SQ --incremental $BENCHMARKS_SQ --model_validation $BENCHMARKS_MV --unsat_core $BENCHMARKS_UC --single_query-noncompetitive non_competing/single_query --incremental-noncompetitive non_competing/incremental --unsat_core-noncompetitive non_competing/unsat_core --model_validation-noncompetitive non_competing/model_validation $OUTPUT
