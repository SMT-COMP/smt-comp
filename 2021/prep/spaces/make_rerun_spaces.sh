#!/bin/sh

MAKESPACE="../../../tools/prep/make_space_from_pairs.py"

csvgrep -c status -m post-processor ../../results/Job47790/Job47790_info.csv > final-uc-posterror.csv
csvgrep -c status -m post-processor ../../results/Job47815/Job47815_info.csv > bestof-2020-uc-posterror.csv

for i in final bestof-2020; do
    python3 $MAKESPACE $i-uc-posterror.csv > $i/uc-rerun.xml
    cd $i
    tar -cvzf uc-rerun.tar.gz uc-rerun.xml
    cd ..
done
