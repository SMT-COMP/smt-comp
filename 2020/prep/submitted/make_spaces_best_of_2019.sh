#!/bin/bash

SOLVERS_CSV=../../registration/solvers_divisions_final.csv
MAKESPACES=./make_spaces.sh

MV_XML=model-validation-best-of-2019.xml
UC_XML=unsat-core-best-of-2019.xml
INC_XML=incremental-best-of-2019.xml
SQ_XML=single-query-best-of-2019.xml

BEST_2019_SOLVERS_CSV=$(mktemp)
csvgrep -c 7 -r '^201[89]-.*$' ${SOLVERS_CSV} > ${BEST_2019_SOLVERS_CSV}

${MAKESPACES} --mv ${MV_XML} --solvdiv ${BEST_2019_SOLVERS_CSV} --include-nc
${MAKESPACES} --uc ${UC_XML} --solvdiv ${BEST_2019_SOLVERS_CSV} --include-nc
${MAKESPACES} --inc ${INC_XML} --solvdiv ${BEST_2019_SOLVERS_CSV} --include-nc
${MAKESPACES} --sq ${SQ_XML} --solvdiv ${BEST_2019_SOLVERS_CSV} --include-nc

rm ${BEST_2019_SOLVERS_CSV}

tar zcf ${MV_XML}.tar.gz ${MV_XML}
tar zcf ${UC_XML}.tar.gz ${UC_XML}
tar zcf ${INC_XML}.tar.gz ${INC_XML}
tar zcf ${SQ_XML}.tar.gz ${SQ_XML}

