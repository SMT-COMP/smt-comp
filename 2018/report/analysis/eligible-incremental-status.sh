#!/bin/bash

# the incremental benchmark file
file=$1

stats=$(grep "set-info" "$file" | grep ":status")

num_stats=$(echo "$stats" | wc -l)
eligible=$(echo "$stats" | grep "unknown" -m 1 -n)

if [ -z "$eligible" ]; then
  eligible="$num_stats"
else
  eligible=$(echo "$eligible" | cut -d ':' -f 1)
  eligible=$((eligible - 1))
fi

echo "$file,$num_stats,$eligible"
