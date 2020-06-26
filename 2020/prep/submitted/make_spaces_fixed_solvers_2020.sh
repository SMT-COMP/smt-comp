#!/bin/bash

SOLVERS_CSV=../../registration/solvers_divisions_final.csv
MAKESPACES=./make_spaces.sh

MV_XML=model-validation-fixed.xml
UC_XML=unsat-core-fixed.xml
INC_XML=incremental-fixed.xml
SQ_XML=single-query-fixed.xml

echo "Note! This script is designed for year 2020."
echo "The script will not be safe next year."

FIXED_SOLVERS_CSV=$(mktemp)
csvgrep -c 7 -r '.*-fixed' ${SOLVERS_CSV} > ${FIXED_SOLVERS_CSV}

${MAKESPACES} --mv ${MV_XML} --solvdiv ${FIXED_SOLVERS_CSV} --include-nc
${MAKESPACES} --uc ${UC_XML} --solvdiv ${FIXED_SOLVERS_CSV} --include-nc
${MAKESPACES} --inc ${INC_XML} --solvdiv ${FIXED_SOLVERS_CSV} --include-nc
${MAKESPACES} --sq ${SQ_XML} --solvdiv ${FIXED_SOLVERS_CSV} --include-nc

rm ${FIXED_SOLVERS_CSV}

tar zcf ${MV_XML}.tar.gz ${MV_XML}
tar zcf ${UC_XML}.tar.gz ${UC_XML}
tar zcf ${INC_XML}.tar.gz ${INC_XML}
tar zcf ${SQ_XML}.tar.gz ${SQ_XML}

