## SMT-COMP 2021 cloud and parallel tracks instance selection

The SMT-COMP 2021 cloud and parallel tracks instance selection is
automated using the year-specific scripts starting with `aws_*` in 
```
2021/prep/selection
```
and the presumably more general scripts
```
tools/prep/aws_make_jobs.py
tools/prep/extract_aws_data_from_solvers_divisions.py
tools/selection/selection_additive.py
```

The instance selection is done by running, in `2021/prep/selection`,

```
./aws_make_selection.sh <smt-lib-root> <competition-root>
```

where `<smt-lib-root>` is a path to the smt-lib benchmarks and
`<competition-root>` is a path where the selected instances should be
placed.  Note that in 2021 the size of `<competition-root>` is roughly
1GB.

### Selection Scripts

`aws_make_selection.sh` -- the main entry point that constructs the
scrambled instances from smt-lib path hierarchy based on
`solvers_divisions_final.csv`, available divisions, and the seed

`aws_pick_instance_nums.py` -- constructs a json file that describes how
many instances from hard and unsolved benchmarks should be picked from
each logic based on available instances, participating solvers, and the
target number of instances.  The script will pick at least the
target number of instances while guaranteeing that 
1. If two logics have sufficiently many instances, the same number of
   instances will be picked from them.
2. If there are enough both hard and unsolved instances, roughly half of the
   picked instances will be hard and the other half unsolved.

`aws_scramble_and_rename.sh` -- Use the smt-comp scrambler to construct
and rename instances for the competition once the instance selection is
available.  The script produces the mapping from the original instance
names to the scrambled names for the recovery of the original instances.

`aws_select_final.py` -- makes the final selection of instances
given the selection numbers produced by `aws_pick_instance_nums.py`,
hard and unsolved instance lists, and the random seed.

`tools/prep/extract_aws_data_from_solvers_divisions.py` -- Compute the
competitive logics based on `solvers_divisions_final.csv`.

`tools/selection/selection_additive.py` -- A script that relies on
`tools/selection/selection.py` to classify the smt-lib benchmarks into
*hard*, *unsolved*, and *uninteresting* based on previous competition
result csvs.
 - A benchmark is *hard* if it was solved in a previous competition so
   that no solver solved it in less than a threshold seconds (but it
   might have been solved faster in another year).
 - A benchmark is *unsolved* if its solving was attempted in a previous
   year but it was not solved.
 - Otherwise, a benchmark is uninteresting.

### Job Scripts

As the name suggests, the parallel and cloud tracks are run in aws
environment by aws affiliated people.  To make running the jobs
hopefully easier for them, we provide scripts for "constructing" job
pairs.  These are not needed to do the selection, but they use files
generated by the selection.

`2021/prep/aws-spaces/aws_make_jobs.sh` -- constructs jobs, i.e., pairs
`<solver_name> <instance>` from `solvers_divisions_final.csv` and the
map files `final/{cloud,parallel}-map.csv`.

`tools/prep/aws_make_jobs.py` -- script for making the jobs, used by
`aws_make_jobs.sh`.
