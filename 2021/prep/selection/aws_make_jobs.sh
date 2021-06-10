#!/bin/sh

../../../tools/prep/aws_make_jobs.py \
    -s ./final/cloud-map.csv \
    -t cloud \
    ../../registration/solvers_divisions_final.csv \
    > cloud-jobs.txt

../../../tools/prep/aws_make_jobs.py \
    -s ./final/parallel-map.csv \
    -t parallel \
    ../../registration/solvers_divisions_final.csv \
    > parallel-jobs.txt

