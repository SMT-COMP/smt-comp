#! /bin/bash

# Call with the directory of added new benchmarks
# e.g. benchmarks-pending/DONE/2019/non-incremental

benchmarks_dir=$1

[ ! -d "$benchmarks_dir" ] && echo "Invalid benchmark directory" && exit 1
cd "$benchmarks_dir" || exit 1
find . -name '*smt2' | sed 's/\.\///'
