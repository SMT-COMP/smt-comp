#! /bin/bash

# Call with the directory of added new benchmarks
# e.g. benchmarks-pending/DONE/2019/non-incremental

echo "pair id,benchmark,benchmark id,solver,solver id,configuration,configuration id,status,cpu time,wallclock time,memory usage,result,expected" > new.csv 

pushd $1
grep -rc assert . | grep -v ":1" | grep "smt2" | sed 's/smt2:.*/smt2/' | while read line; do grep -l "(set-info :status unsat)" $line; done  | sed 's/\.\///' | sed 's/\(.*\)/x,\1,x,NEW,x,x,x,timeout (wallclock),5000,5000,0,starexec-unknown,starexec-unknown/g' > smtcomp-tmp
popd
mv $1/smtcomp-tmp .
cat < smtcomp-tmp >> new_unsat.csv
rm smtcomp-tmp
