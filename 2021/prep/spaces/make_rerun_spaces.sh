#!/bin/sh

MAKESPACE="../../../tools/prep/make_space_from_pairs.py"
JOBFINAL="../../results/Job47790/Job47790_info.csv"
JOBBESTOF="../../results/Job47815/Job47815_info.csv"

if [ \! -e "$JOBFINAL" -o \! -e "$JOBBESTOF" ]; then
    echo "Please download unsat core jobs:"
    echo "cd ../../results; ./join.sh"
    exit
fi

csvgrep -c status -m post-processor $JOBFINAL > final-uc-posterror.csv
csvgrep -c status -m post-processor $JOBBESTOF > bestof-2020-uc-posterror.csv

for i in final bestof-2020; do
    mkdir -p $i
    python3 $MAKESPACE $i-uc-posterror.csv > $i/uc-rerun.xml
    cd $i
    tar -czf uc-rerun.tar.gz uc-rerun.xml
    cd ..
done

sha256sum */uc-rerun.xml
