### Compute the scores for the website by combining different jobs

First you need to download the "job information" from StarExec. Make
sure the option "include ids" is checked. If the Job is public, you can
download using curl:

```curl -o Job${JOBID}_info.zip "https://www.starexec.org/starexec/secure/download?type=job&id=${JOBID}&returnids=true"```

Once results are downloaded form starexec, the scores are computed in
two phases.  First by combining the jobs, and by then processing them
into results taking into account benchmark blacklists.

In terms of scripts, the script `clean_and_join_csvs.sh` constructs
`.csv` files that can be processed by `make_mds.sh` for the final
scoring and reporting on the competition website.

The scripts assume that the website repository is placed in the same
folder as the main smt-comp repository.

#### Constructing the scores

Create to this folder the directories `incremental`, `model-validation`
`unsat-core` and `single-query`, and place in them the
`../results/<track>/Job*_info.csv`.
Files from starexec main job should be called `Job_info_orig.csv`,
best-of-2019 job is called `Job_info_2019.csv`, and the fixed job
`Job_info_fixed.csv`.

The joined files are then computed by running

```./clean_and_join_csvs.sh --sq --inc --uc --mv```

Note that this might take a few minutes to finish.

Finally, the `md`s can be created by running

```./make_mds.sh --all```

The `md`s are placed in `../results/_results_2020`.
