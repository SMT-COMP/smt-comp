#!/bin/bash

# the incremental benchmark file
file=$1

stats=$(grep "\<assert\>" "$file")

num_stats=$(echo "$stats" | wc -l)

echo "$file,$num_stats"
