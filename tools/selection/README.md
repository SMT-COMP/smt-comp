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
   years you also need the results CSV files from the previous year, which
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

    Note: If you want to filter benchmarks as set out in the rule document for
    the single query track you should also add `--filter results.csv`, where
    `results.csv` contains the track results from the previous competition.


