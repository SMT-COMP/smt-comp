#!/bin/sh

# Update the web pages from the solvers_division_final.csv.
# You should have checked out the smt-comp.github.io repository into the
# same directory as smt-comp

NYSE_ON_MAY27="11787.5646"
DIVISIONS="../divisions.json"

../../tools/prep/extract_data_from_solvers_divisions.py -d $DIVISIONS solvers_divisions_final.csv ../../../smt-comp.github.io/_participants_2020 2020
../../tools/prep/make_participants_md.py -d $DIVISIONS -y 2020 -n "2020-05-27;$NYSE_ON_MAY27" ../../../smt-comp.github.io/2020/
