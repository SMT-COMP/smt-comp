#!/bin/bash
#
# Bash script for producing a subset of benchmark set on StarExec.
#
# Typical usage scenario:
# You want to reduce a large set of SMT-LIB benchmarks to a very small set
# but retain a high diversity of benchmarks.
# This script allows you to pick n benchmarks from each benchmark folder.
# (Note that this does NOT necessarily give you n files per 
# "benchmark family" since a benchmark family consists of all benchmarks
# inside a top-level subfolder.)
#
# Naive solution for this problem:
# Download all benchmarks from StarExec (huge!), do some filering on your
# computer, and upload your subset (slow!)
#
# This script's solution for this problem:
# 1. Download an XML decription of the StarExec space that contains your 
#     benchmarks (download space xml).
#     Download the space xml without attributes (StarExec will ask you).
#     This script will not work "with attributes"!
# 2. Extract the ZIP archive and apply this script to the .xml file.
#     First argument: the .xml file. 
#     Second argument: number of remaining benchmarks per folder.
#     The result is written to stdout
# 3. Edit the space name and the description. Your strings have to match
#      the following pattern, otherwise StarExec will reject your upload
#         [^<>"')(&%+-]{0,1024}
# 4. Wrap your new .xml into a ZIP archive and upload it in your favorite
#     space (via the 'upload space xml' button).
# StarExec will now create a space that contains your subset of the 
# benchmarks.
#
# 2018-06-16 Matthias Heizmann (heizmann@informatik.uni-freiburg.de)
#

set -e
set -u

BENCHMARKS_PER_FOLDER="$2"

awk 'BEGIN { SIZE='"$BENCHMARKS_PER_FOLDER"'; CURRENT=0 } \
     /^\s*<Benchmark id=".*" name=".*"\/>\s*$/ { if (CURRENT<SIZE) print; CURRENT++; next } \
     { print; CURRENT=0 }' "$1"
