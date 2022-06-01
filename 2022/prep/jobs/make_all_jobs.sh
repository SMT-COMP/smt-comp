#!/bin/bash

for track in sq inc uc mv pe; do
    ./make_job.sh --$track
done

