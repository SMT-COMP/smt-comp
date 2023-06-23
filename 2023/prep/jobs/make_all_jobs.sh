#!/bin/bash

if false; then  # test jobs
for track in sq inc uc mv pe; do
    ./make_job.sh --$track --test-run --solvers ../../registration/solvers_divisions_prelim.csv
done

else

for track in sq inc uc mv pe; do
    ./make_job.sh --$track --solvers ../../registration/solvers_divisions_final.csv
done

./make_job.sh --include-nc --extra missinglogics --sq --solvers ../../registration/solvers_divisions_smtinterpol_missinglogics.csv
./make_job.sh --include-nc --extra missinglogics2 --sq --solvers ../../registration/solvers_divisions_cvc5_missinglogics.csv

IDS=$(csvcut -c "Config ID Single Query" ../../registration/solvers_divisions_bestof_2022.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --sq --extra bestOf2022 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Model Validation" ../../registration/solvers_divisions_bestof_2022.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --mv --extra bestOf2022 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Unsat Core" ../../registration/solvers_divisions_bestof_2022.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --uc --extra bestOf2022 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Incremental" ../../registration/solvers_divisions_bestof_2022.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --inc --extra bestOf2022 --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Single Query" ../../registration/solvers_divisions_fixed.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --sq --extra fixed --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Model Validation" ../../registration/solvers_divisions_fixed.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --mv --extra fixed --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Incremental" ../../registration/solvers_divisions_fixed.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --inc --extra fixed --solvers ../../registration/solvers_divisions_all.csv

IDS=$(csvcut -c "Config ID Unsat Core" ../../registration/solvers_divisions_fixed.csv | tail +2 | tr '\n' , | sed s/,$//)
PREPARE_JOB_ARGS="--solvers $IDS" ./make_job.sh --uc --extra fixed --solvers ../../registration/solvers_divisions_all.csv

fi
