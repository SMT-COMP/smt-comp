#!/bin/bash

set -e
set -u

MAINTRACK_2017="$1"
MAINTRACK_2017_RERUN="$2"

# strip column header line, then remove all timeouts from the original
# main track results
tail -n +2 "$MAINTRACK_2017"|awk -F , '($8 !~ /timeout/)'

# strip column header line from the reruns
tail -n +2 "$MAINTRACK_2017_RERUN"
