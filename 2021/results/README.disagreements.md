Disagreements
=============

Single Query
------------

We collected all benchmarks on which at least one solver returned sat and and at least one solver returned unsat

```
cat Single_Query_Track.csv  |csvcut -c 2,12 |cut -d/ -f2- |grep sat$ | sort |uniq | cut -d, -f1 |uniq -c | grep -v '   1 ' | cut -c9- > sq-disagreements.txt
```

In `sq-disagreements-decision.csv` we provide the decision of the
status that we used to evaluate soundness of the solvers.  The
decisions were made, because:

1. For `QF_SLIA`, we manually investigated that the model given by cvc5
   is correct and these benchmarks are indeed sat.  The solver z3str4 was
   buggy.
2. For `QF_LIA`, the authors of opensmt confirmed the bug and fixed it.
3. For `QF_ABVFP`, `QF_BVFP`, `QF_FP`, the authors of COLIBRI confirmed the bug
   and fixed it. The new version agrees with the recorded decision.
4. For `QF_ABVFPLRA`, the last year's COLIBRI solver was unsound.  Again the
   new version of COLIBRI agrees with our decision.
5. For `UF`, the iProver team confirmed a problem with their solver, the
   fixed version of the solver returns unknown for the benchmarks.
6. For `UFDTLIRA`, the last year's Vampire solver disagrees with this years
   Vampire and or cvc4/5.  We therefore assume that Vampire was unsound.
7. For `LIA` and `UFNIA` there were some disagreements with Vampire, that were
   fixed by the Vampire team.
8. `UFNIA` also had other disagreements with Par4. In many cases we went
   with the majority vote.


Incremental
-----------

Two issues were found and resolved as follows:

1. In `QF_ABVFP`, Bitwuzla disaggreed with all other solvers on a few 
   benchmarks. The problem was confirmed by the authors and their fixed
   version agrees with the other solvers.
2. Also in `QF_ABVFP` and in `QF_BVFP`, mathsat disagrees with all other
   solvers on a few benchmarks.  We stick with the majority here.
