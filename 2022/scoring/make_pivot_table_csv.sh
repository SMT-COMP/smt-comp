#/bin/sh -eu

python3 ../../tools/results_visualization/aggregations.py --csv results-sq.csv --solvers ../registration/solvers_divisions_all.csv --out ../../../smt-comp.github.io/2022/sq.csv --divisions-map ../new-divisions.json --time 1200
