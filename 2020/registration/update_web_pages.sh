#!/bin/sh

# Update the web pages from the solvers_division_final.csv.
# You should have checked out the smt-comp.github.io repository into the
# same directory as smt-comp

NYSE_ON_MAY26="0"

../../tools/prep/extract_data_from_solvers_divisions.py solvers_divisions_final.csv ../../../smt-comp.github.io/_participants_2020 2020
../../tools/prep/make_participants_md.py -y 2020 -n "2020-05-26;$NYSE_ON_MAY26" ../../../smt-comp.github.io/2020/
