## Previous year's winners

Given the best solvers from last year, `best_solvers_to_csv.py` searches for them from the
corresponding year's registration csv file and produce csv lines
according to the new year's registration csv format so that the
best solvers are inserted as non-competitive entries in the
divisions they won.

Input:
 - old-registiation: the old registration csv
 - new-registration: the new registration csv
 - best-solvers: the best solvers csv with headers for division, and
   solver name, for each track.

The script only outputs the new lines, they are not automatically added
to `solvers_divisions.csv`.

See
[`get_last_year_best_solvers.sh`](../../2021/previous-best/get_last_year_best_solvers.sh)
on how to construct the input files.
