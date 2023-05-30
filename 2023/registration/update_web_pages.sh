#!/bin/sh

# Update the web pages from the solvers_division_final.csv.
# You should have checked out the smt-comp.github.io repository into the
# same directory as smt-comp

YEAR=2023
NYSE_DATE=2023-05-30
NYSE_VALUE="15078.6900"  # NYSE opening value, e.g., 12345.6789
LOGICS="../divisions.json"
DIVISIONS="../new-divisions.json"

mkdir -p ../../../smt-comp.github.io/_participants_$YEAR

../../tools/prep/extract_data_from_solvers_divisions.py -d $LOGICS solvers_divisions_all.csv ../../../smt-comp.github.io/_participants_$YEAR $YEAR
../../tools/prep/make_participants_md.py -d $DIVISIONS -y $YEAR -n "$NYSE_DATE;$NYSE_VALUE" ../../../smt-comp.github.io/$YEAR/
