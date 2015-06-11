#!/bin/bash

#
# finds all benchmarks files in the current directory that contain a division
# operation on bit-vectors and prints their path to stdout
#

egrep -r -l 'bvudiv|bvurem|bvsdiv|bvsrem|bvsmod' .
