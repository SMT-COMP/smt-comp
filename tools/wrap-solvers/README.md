Wrap Solvers for SMT-COMP
==========================

This collection of scripts downloads, wraps and uploads solvers from StarExec
for SMT-COMP.

It used to require the
[StarExec command line tool](https://www.starexec.org/starexec/public/starexeccommand.jsp).

Since the StarExec command line tool is currently not working we have
a work around, where we manually download the solvers.


1. ~~Copy `login.sh.template` to `login.sh` and fill in your credentials~~.

   Create a subdirectoy called `download`, where you download all using the default setting.
   Rename the downloaded zip file to *ID*.zip, where *ID* is the solver id.

2. Copy a current binary of the
[trace executor](https://github.com/smt-comp/trace-executor)
into directory `wrapper_inc`

3. `./wrap_solvers.py <solvers: csv> [ --sq <space: id> ] [ --inc <space_inc: id> ] [ --mv <space_mv: id> ] [ --uc <space_uc: id> ]`

```
<solvers: csv>   is a csv file with the solver ids as in
                 2020/registration/solvers_divisions_final.csv

<space: id>      the StarExec space id of the solver space for non-incremental
                 solvers

<space_inc: id>  the StarExec space id of the solver space for incremental
                 solvers

<space_mv: id>   the StarExec space id of the solver space for model validation 
                 track solvers

<space_uc: id>   the StarExec space id of the solver space for unsat core 
                 track solvers
```

As of 2020, the solvers have to be uploaded manually.  So the space id
is currently ignored but some number must be given.  The wrapped
solvers are put into the directory upload and have to be uploaded
manually to the corresponding spaces.

Note that in SMT COMP 2020, we only wrap the incremental solvers.
