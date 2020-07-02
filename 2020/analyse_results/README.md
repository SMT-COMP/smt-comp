# Analysis Tools

These small scripts search for benchmarks where the solvers
disagreed during the competition.

## Constructing single-query disagreement mds

To construct mds suitable for reporting with the website, first run

```./sq_find_disagreements.sh```

then

```./sq_show_disagreements.sh > sq_disagreements.csv```

and then

```./sq_make_disagreement_md.py -i sq_disagreements.csv -s ../registration/solvers_divisions_final.csv -o ../../../smt-comp.github.io/_disagreements_2020```


