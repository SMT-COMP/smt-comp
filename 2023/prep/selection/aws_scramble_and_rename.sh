#!/bin/sh

SCRAMBLER=../../../../scrambler/scrambler

if [ $# != 4 ]; then
    echo "Usage: ${0} <smt-lib-root> <selection> <output-dir> <seed>"
    exit 1
fi

smtlib_root=$1
selection=$2
outputdir=$3
seed=$4

i=0

TMPQUEUE=$(mktemp "aws_scramble_parallelXXXXX.list")

if [ -z ${KEEP_INTERMEDIARY_FILES+x} ]; then
    trap "rm -rf ${TMPQUEUE}" EXIT
else
    >&2 echo "Intermediary file is $TMPQUEUE"
fi


echo "smtlib name,competition name"
for file in $(cat ${selection}); do
    srcfilesysname=${smtlib_root}/${file}
    logic=$(echo ${file} |awk 'BEGIN {FS="/"} {print $3}')
    mkdir -p ${outputdir}/non-incremental/${logic}
    ofile=/non-incremental/${logic}/$(printf "smt-comp-%03d.smt2" ${i})
    dstfilesysname=${outputdir}/${ofile}
    echo "${file},${ofile}"
    if [ -z ${DONT_SCRAMBLE+x} ]; then
       echo "${SCRAMBLER} -seed ${seed} < ${srcfilesysname} > ${dstfilesysname}" >> $TMPQUEUE
    else
       ln ${srcfilesysname} ${dstfilesysname}
    fi
    i=$(($i+1))
done

if [ -z ${DONT_SCRAMBLE+x} ]; then
    cat $TMPQUEUE | parallel
fi