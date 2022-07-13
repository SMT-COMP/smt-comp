# Preparing the SMT-COMP spaces

## Generate a list of benchmarks and spaces

Download SMT-LIB repositories (git-lfs is needed) in a directory of your choice,
200Go free is needed. This directory will be referenced as `$SMTLIB_DIR`, and is
composed of three subdirectories:

1. `non-incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/
2. `incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks-inc/
3. checkout the repository
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks-tmp/pending-2022
   to `pending-2022`. This year, this repository seems to be empty, though.
   I worked around by filtering new benchmarks by family names,
   see `./find_new_benchmarks.sh`

The points 1. and 2. are automated with `./download.py $SMTLIB_DIR`
which requires `gitlab` API `pip install --upgrade python-gitlab` (version 3.5.0
works).

You also need to checkout the scrambler repository alongside the
smt-comp repository and build the scrambler with `make`.

```
git clone https://github.com/SMT-COMP/scrambler.git ../../../scrambler
make -C ../../../scrambler
```

Then run `./find_benchmarks.sh $SMTLIB_DIR` in the directory of this README.

## Downloading the space XML files from starexec.

Go to the space for the current SMT-LIB release on Starexec.  For each
of the two subspaces choose `download space xml`.  Don't include benchmarks
attributes.  Extract the xml files from the downloaded zip file and put
them into this directory as `incremental.xml` and
`non-incremental.xml`.

## Creating divisions.

To ensure the logics match those of SMT-LIB, we now create the division
files from the list of benchmarks.  The script `./create_divisions.sh`
does this.  You need to supply a regex for every division to match the
logics in this division.  The script will check that the logics are
partitioned into the divisions and report any logic that is missing or
that was assigned to two divisions.

## Retrieve SQ statuses for unknown non-incremental benchmarks

One should:
1 - Download the job information from the finished StarExec job.

2 - Run the scoring script on it as if to compute the final results for SQ, but
    with the --solved-benchs option, which will output a CSV with a list of
    solved unknown benchmarks and the results produced

3 - Run `merge_benchmarks_with_sq_statuses.py $PATH_CSV_SQ_STATUSES`, which will
    supplement `SMT-LIB_non_incremental_benchmarks_all_assertions.csv` with the
    SQ statuses and generate
    `SMT-LIB_non_incremental_benchmarks_all_assertions_sqSolved.csv`

The resulting CSV will have two new columns: `sqSatRes` and `sqUnsatRes`. For
each benchmark the former (resp. the latter) has the number of solvers who said
"sat" (resp. unsat) for it. No distinction about solvers being sound or not is
made for that computation.
