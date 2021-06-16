#!/bin/sh

SELECTION=final

mkdir -p ${SELECTION}

../../../tools/prep/aws_make_jobs.py \
    -s ../selection/final/cloud-map.csv \
    -t cloud \
    ../../registration/solvers_divisions_final.csv \
    > ${SELECTION}/cloud-jobs.txt

../../../tools/prep/aws_make_jobs.py \
    -s ../selection/final/parallel-map.csv \
    -t parallel \
    ../../registration/solvers_divisions_final.csv \
    > ${SELECTION}/parallel-jobs.txt

