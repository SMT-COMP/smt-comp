#!/bin/sh

# Update the web pages from the solvers_division_final.csv.
# You should have checked out the smt-comp.github.io repository into the
# same directory as smt-comp

YEAR=2021
NYSE_DATE=2021-06-15
NYSE_VALUE=""   # NYSE opening value, e.g., 12345.6789
DIVISIONS="../divisions.json"

../../tools/prep/extract_data_from_solvers_divisions.py -d $DIVISIONS solvers_divisions_final.csv ../../../smt-comp.github.io/_participants_$YEAR $YEAR
../../tools/prep/make_participants_md.py -d $DIVISIONS -y $YEAR -n "$NYSE_DATE;$NYSE_VALUE" ../../../smt-comp.github.io/$YEAR/
