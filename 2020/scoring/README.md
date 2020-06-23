### Compute the scores for the website by combining different jobs

The script `compute_scores.sh` constructs `.md` files for the 2020
competition website by combining several jobs for the four tracks.

The script assumes that the website repository is placed in the same
folder as the main smt-comp repository.

To construct the scores, first

 - create to this folder the directories `incremental`,
   `model-validation` `unsat-core` and `single-query`, and then
 - place in them the `Job*_info.csv` files from starexec so that the
   main job is called `Job_info_orig.csv` and the best-of-2019 job is
   called `Job_info_2019.csv`.

The scores are then computed by running

```./compute_scores.sh --sq --inc --uc --mv```

Note that this might take a few hours to finish.

The script automatically copies the resulting `.md`s to
`<website>/_results_2020/` at the end.
