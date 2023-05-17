#!/bin/bash

if true; then  # test jobs
for track in sq inc uc mv pe; do
    ./make_job.sh --$track --test-run --solvers ../../registration/solvers_divisions_prelim.csv
done

else

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

PREPARE_JOB_ARGS="--solvers 671399" ./make_job.sh --sq --extra noncompeting2 --solvers ../../registration/solvers_divisions_all.csv

fi
