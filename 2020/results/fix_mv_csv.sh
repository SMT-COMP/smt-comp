#!/bin/bash

# There is a starexec bug that columns containing , are not quoted
# This bug triggers for model validation, where the last (16th) column
# may contain ,.  We fix it by quoting everything after the 15th comma.
perl -i -pe 's/(([^,]*,){15})([^"].*)\r$/$1"$3"/' Model_Validation_Track.csv
