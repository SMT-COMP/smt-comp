#!/bin/bash

# Implements a test for a SMT-LIB benchmark
#
# The test is that *every* check-sat command is preceded immediately
# by a (set-info :status sat) or (set-info :status unsat)
# The input file must be given as argument to the script
# If the input file does not pass the test, its name is printed to stdout
#
check=`pcregrep "^\(check-sat" $1 | wc -l`
status=`pcregrep -M "^\(set-info :status (sat|unsat).*\n\(check-sat" $1 | grep check-sat | wc -l`
if [ $check != $status ]; then
	echo $1
fi
