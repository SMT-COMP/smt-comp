# Preparing the SMT-COMP spaces

## Generate a list of benchmarks and spaces

Download SMT-LIB repositories.  Make three subdirectories:

1. `non-incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/
2. `incremental` where you checkout the repositories from
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks-inc/
3. checkout the repository
    https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks-tmp/pending-2021
   to `pending-2021`.

You also need to checkout the scrambler repository in the same directory
as the smt-comp repository and build the scrambler with `make`.

Then run `./find_benchmarks.sh` on this directory. 

## Downloading the space XML files from starexec.

Go to the space for the current SMT-LIB release on Starexec.  For each
of the two subspaces choose `download space xml`.  Don't include benchmarks
attributes.  Extract the xml files from the downloaded zip file and put
them into this directory as `incremental-space.xml` and 
`non-incremental-space.xml`.
