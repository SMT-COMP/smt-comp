#! /bin/bash

# Call with the directory of added new benchmarks
# e.g. benchmarks-pending/DONE/2019/non-incremental

echo "pair id,benchmark,benchmark id,solver,solver id,configuration,configuration id,status,cpu time,wallclock time,memory usage,result,expected" > new_single_query.csv 

pushd $1
find . -name '*smt2' | sed 's/\.\///' | sed 's/\(.*\)/x,\1,x,NEW,x,x,x,timeout (wallclock),5000,5000,0,starexec-unknown,starexec-unknown/g' > smtcomp-tmp 
popd
mv $1/smtcomp-tmp .
cat < smtcomp-tmp >> new_single_query.csv 
rm smtcomp-tmp
