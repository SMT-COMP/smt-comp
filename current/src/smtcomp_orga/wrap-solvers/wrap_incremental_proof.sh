#!/bin/sh

SOLVER_DIR=$1

test -e "${SOLVER_DIR}/bin/smtcomp_run_incremental" || cp -a "${SOLVER_DIR}/bin/starexec_run_"* "${SOLVER_DIR}/bin/smtcomp_run_incremental"
res=$?
cp -a wrapper_inc/* "${SOLVER_DIR}/bin"
cp -a wrapper_pe/* "${SOLVER_DIR}/bin"
if [ $res -ne 0 ]
then
    echo "ERROR: no default config"
    exit 1
fi
