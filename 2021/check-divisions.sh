#!/bin/bash

diff -s <(jq 'map_values(sort)' < divisions.json) \
        <(jq 'map_values(values | flatten | sort)' < new-divisions.json)
