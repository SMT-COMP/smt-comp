#!/bin/bash

# Implements a test for a SMT-LIB benchmark
#
# The test is the *first* check-sat command is preceded immediately
# by a (set-info :status sat) or (set-info :status unsat)
# The input file must be given as argument to the script
# If the input file does not pass the test, its name is printed to stdout
#
grep -m 1 -B 1 "(check-sat)" $1 | head -n 1 | pcregrep "\(set-info :status (sat|unsat)\)" > /dev/null
if [ $? -ne 0 ]; then
	echo $1
fi
