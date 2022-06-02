# Preparing the competition jobs

The selection is done by the script `./make_selection.sh`.
You need to edit the script to switch between testing and final
selection.  These differ in the seed that is used and the percentage
of benchmarks included.

The selection is saved in the corresponding testing or final 
subdirectory.  There is one text file for each track, each containing
a list of selected benchmarks.

## Adapting the script

The single query track rules state that benchmarks that were solved
fast in previous competitions are excluded from the selection.  To
filter these, one has to provide the results of each competition as
CSV file, i.e., for every year one has to add one more filter rule.
This rule only applies to single query track.

## Filtering based on single-query results.

Since 2022 we filter unsat/sat benchmarks for unsat core and model
validation based on the single query results.  TODO: describe how
we did that, once we did it.