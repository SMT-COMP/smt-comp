Workflow for problem selection
==============================

Follow these steps per track:

1. Get list of new benchmarks added this year and the list of all benchmarks
   in this year's SMT-LIB release.

   Hopefully the new benchmarks are nicely stored in the SMT-LIB pending
   directory structure such as `benchmarks-pending/DONE/2019/non-incremental`.

   Run:
   ```
     sh prepare_benchmark_list.sh <path-to-new-benchmarks> > benchmarks_new.txt
     sh prepare_benchmark_list.sh <path-to-all-benchmarks> > benchmarks_all.txt
   ```

   Each benchmark must be in one line starting with the logic string.
   From 2019 onwards the benchmark lists will appear in the repository under
   `<year>/prep/`.

2. Edit selection parameters in `selection.py` if you need to. It has some
   hard-coded values based on the competition rules document. Read the
   comments to see if you want to update these.

3. To filter out uninteresting benchmarks based on the results of previous
   years you also need the results CSV files from the previous years, which
   are archived in the repository under `<year>/csv`. If you want to use a
   different set of base benchmarks then you can use any StarExec results CSV
   file.

4. You will also need a seed value for the pseudo-random selection.

5.  With these inputs you should run:

    ```
      python selection.py --benchmarks benchmarks_all.txt --new-benchmarks benchmarks_new.txt -s <seed> --out <outfile>
    ```

    to print the names of the selected problems into the supplied out file.
    These can be used with the space preperation scripts to prepare a
    competition space.

    Note: If you want to filter benchmarks as set out in the rule
    document for the single query track you should also add `--filter
    results.csv`, where `results.csv` contains the track results from
    the previous competition.  You may add several of these files by
    providing multiple times --filter <file.csv>

6.  To make the selection for unsat core track, you need the statuses
    and the number of assertions from the non-incremental smt-lib
    benchmarks.
    The number of assertions can be computed for instance with the
    [scrambler](https://github.com/SMT-COMP/scrambler).  For example:
    ```
    $ echo "benchmark,number of asserts" > asrt-count.csv
    $ for file in $(find . -name '*.smt2'); do
        n_asrts=$(~/src/scrambler/scrambler -count-asserts true < $file 2>&1 1>/dev/null |sed -n 's/^; Number of assertions: \([0-9][0-9]*\)/\1/p'); echo "$file,$n_asrts";
    done >> asrt-count.csv
    ```
    This will take some time.

    The statuses can be obtained with the following one-liner:
    ```
    $ echo "benchmark,status" > statuses.csv; for file in $(find . -name '*.smt2'); do echo -n "${file},"; grep '([ \t]*set-info[ \t][ \t]*:status[ \t].*[ \t]*)' $file |sed -n 's/.*[ \t]\(unsat\|sat\|unknown\).*/\1/p'; done >> statuses.csv
    ```

    The two results should be combined into one file

    ```
    $ ./combine_statuses_and_asrts.py -a asrt-count.csv -s statuses.csv > asrts-statuses.csv
    ```

    and the unsat core selection can now be done with

    ```
    $ ./selection.py -b benchmarks_all.txt -n benchmarks_new.txt --unsat asrts-statuses.csv -s >seed> -o <outfile>
    ```
