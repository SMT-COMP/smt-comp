# Table of contents

- [Table of contents](#table-of-contents)
- [Installation](#installation)
- [New year](#new-year)
- [Preparing the SMT-COMP spaces](#preparing-the-smt-comp-spaces)
  - [Generate a list of benchmarks and spaces](#generate-a-list-of-benchmarks-and-spaces)
  - [Downloading the space XML files from starexec.](#downloading-the-space-xml-files-from-starexec)
  - [Creating divisions.](#creating-divisions)
  - [\[LATER\] Retrieve SQ statuses for unknown non-incremental benchmarks](#later-retrieve-sq-statuses-for-unknown-non-incremental-benchmarks)
- [Registration](#registration)


# Installation

Compilation:
 * `pip install --upgrade build`
 * `python3 -m build`
 * `pip3 install --editable .`

 Adding new command in `pyproject.toml`

# New year

* copy current to year n-1
* remove current/data
* Fix the dates
* commit



# Preparing the SMT-COMP spaces

The data are in directory `data/prep`, 

Goal:
  * Downloading the benchmarks
  * Gathering information from the benchmarks

## Generate a list of benchmarks and spaces

Download SMT-LIB repositories (git-lfs is needed) in a directory of your choice,
200Go free is needed. This directory will be referenced as `$SMTLIB_DIR`, and is
composed of three subdirectories:

1. `non-incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/
2. `incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks-inc/

The points 1. and 2. are automated with `smtcomp-orga-download $SMTLIB_DIR`.

You also need to checkout the scrambler repository alongside the
smt-comp repository and build the scrambler with `make`.

```
git clone https://github.com/SMT-COMP/scrambler.git ../../scrambler
make -C ../../scrambler
```

The scrambler binary is supposed to be in $SCRAMBLER

* Then run `find_benchmarks.sh $SMTLIB_DIR $SCRAMBLER data/prep/` in the directory of this README.
* Then run `find_new_benchmarks.sh data/prep/`


## Downloading the space XML files from starexec.

Go to the space for the current SMT-LIB release on Starexec.  For each
of the two subspaces choose `download space xml`.  Don't include benchmarks
attributes. Extract the xml files from the downloaded zip file and put
them into the directory `data/prep` as `incremental.xml` and
`non-incremental.xml`.

## Creating divisions.

To ensure the logics match those of SMT-LIB, we now create the division files
from the list of benchmarks.  The command `create-divisions.sh data/prep` does
this.  You need to supply a regex for every division to match the logics in this
division.  The script will check that the logics are partitioned into the
divisions and report any logic that is missing or that was assigned to two
divisions. The files `data/divisions.json` and `data/new_divisions.json` are
created by the script.

## [LATER] Retrieve SQ statuses for unknown non-incremental benchmarks

One should:
1 - Download the job information from the finished StarExec job.

2 - Run the scoring script on it as if to compute the final results for SQ, but
    with the --solved-benchs option, which will output a CSV with a list of
    solved unknown benchmarks and the results produced. For example:

```
smtcomp-orga-score --solved-benchs -c /path/to/SomeJob_info.csv -y 2022 -t 1200 -S /path/to/registration/solvers_divisions_final.csv -T sq -D /path/to/new-divisions.json
```
3 - Run `smtcomp-orga-merge_benchmarks_with_sq_statuses $PATH_CSV_SQ_STATUSES`, which will
    supplement `SMT-LIB_non_incremental_benchmarks_all_assertions.csv` with the
    SQ statuses and generate
    `SMT-LIB_non_incremental_benchmarks_all_assertions_sqSolved.csv`

The resulting CSV will have two new columns: `sqSatRes` and `sqUnsatRes`. For
each benchmark the former (resp. the latter) has the number of solvers who said
"sat" (resp. unsat) for it. No distinction about solvers being sound or not is
made for that computation.

# Registration

In directory `data/registration`

Steps to produce this directory:

1. Download the google form results, and put it as `data/registration/SMT-COMP_System_Registation.csv`
2. Edits manually to fix wrong entries.
3. run `smtcomp-orga-extract_data_from_submission -d data/divisions.json 2023 "data/registration/SMT-COMP System Registration.csv" data/registration/solvers_divisions.csv`
4. fix problems, check availability of solvers, contact solver authors.
5. move resulting solvers_divisions.csv to solvers_divisions_all.csv
6. during preliminary copy solvers_divisions_all.csv to solvers_divisions_prelim.csv
7. run `make_starexec_solvers_xml.sh data/registration/`
8. upload solvers.zip to starexec, check for problems.
9. checkout github pages to correct directory, create empty `_participants_2023`
10. run `./update_web_pages.sh`
11. check for problems.
12. publish.
