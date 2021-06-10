#!/usr/bin/env sh

../../../tools/prep/extract_aws_data_from_solvers_divisions.py -d ../../new-divisions.json -t cloud ../../registration/solvers_divisions_final.csv
../../../tools/prep/extract_aws_data_from_solvers_divisions.py -d ../../new-divisions.json -t parallel ../../registration/solvers_divisions_final.csv
