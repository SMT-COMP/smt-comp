#!/bin/bash

if false; then  # test jobs
for track in sq inc uc mv pe; do
    ./make_job.sh --$track --test-run --solvers ../../registration/solvers_divisions_prelim.csv
done

for track in sq inc mv uc; do
    ./make_job.sh --test-run --$track --extra 2 --solvers ../../registration/solvers_divisions_prelim2.csv --include-nc
done

./make_job.sh --test-run --pe --extra 2 --solvers ../../registration/solvers_divisions_prelimproof.csv

for track in sq mv inc; do
    ./make_job.sh --test-run --$track --extra 3 --solvers ../../registration/solvers_divisions_prelim3.csv --include-nc
done

./make_job.sh --test-run --inc --extra preprocessorfix --solvers ../../registration/solvers_divisions_incrementalfix.csv
fi

for track in sq inc mv uc pe; do
    ./make_job.sh --$track
done


IDS=$(csvcut -c "Config ID Single Query" ../../registration/solvers_divisions_noncompeting.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --sq --extra noncompeting --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Single Query" ../../registration/solvers_divisions_bestof_2021.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --sq --extra bestOf2021 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Model Validation" ../../registration/solvers_divisions_bestof_2021.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --mv --extra bestOf2021 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Unsat Core" ../../registration/solvers_divisions_bestof_2021.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --uc --extra bestOf2021 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Incremental" ../../registration/solvers_divisions_bestof_2021.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --inc --extra bestOf2021 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Model Validation" ../../registration/solvers_divisions_noncompeting.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --mv --extra noncompeting --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Incremental" ../../registration/solvers_divisions_noncompeting.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --inc --extra noncompeting --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Unsat Core" ../../registration/solvers_divisions_noncompeting.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --uc --extra noncompeting --solvers ../../registration/solvers_divisions_all.csv
