# Generating Blacklists for SMT-LIB

The blacklists contain benchmarks that are not following the syntactic
restrictions of their respective divisions.  We distinguish these cases

1. Quantifiers in quantifier-free benchmarks.  This list was generated with
   `grep -l -R -E '\((exists|forall) ' QF_*`

2. Some division restrict the allowed array types, e.g. most A\*LIA
   logics only support the type `(Array Int Int)`.  We used the following
   script to find all array types used:

```
find . -name \*.smt2 | \
while read benchmark; do 
  perl -ne '$re=qr/\(Array( (\((?:(?>[^()]+)|(?2))*\)) (?2))\)/;
            while (/$re/) { print "$ARGV:$&\n" ; $_ =~s/$re/$1/}' 
       "$benchmark" | sort |uniq; 
done
```

   Then we manually inspected the list to find the bad array types:

   * `(Array Int (Array Int Int))` in `ALIA`, `QF_ALIA`, `QF_AUFLIA` (incremental)
   * `(Array (_ BitVec [0-9]*) Bool)` in `ABV` (non-incremental)
   * `(Array (_ BitVec [0-9]*) (Array (_ Bitvec [0-9]*) (_ Bitvec [0-9]*)))`
      in ABV (non-incremental)

   We grepped the for these array types to build the blacklists.

   We intentionally did not use any restrictions for logics that are not yet
   documented on the 
   [SMT-LIB web site](http://smtlib.cs.uiowa.edu/logics-all.shtml), in 
   particular, we allow any array type for `ABVFP`, `ABVFPLIA`, and all logics 
   containing `DT` (data types).

3. Benchmark using non-linear arithmetic in LIA/LIRA/LRA logics.  We use
   a new feature in smtinterpol to find these logics:

```
find *L[IR]* -name \*.smt2 | \
while read benchmark; do 
    echo '(echo "'$benchmark'")'
    echo '(include "'$benchmark'")'
    echo '(reset)'
done | \
    java -jar ~/smtinterpol-2.5-682-g35be1729.jar -script LinearArithmeticChecker \
      2>/dev/null > benchmark_nonincremental_nonlinear.txt
```

4. Benchmarks in non-incremental in which solvers disagree.  The list was
   created with

```
grep "... in " ../analyse_results/incremental_disagreements.txt | cut -c8-
```

   The benchmarks with disagreeing unsound solvers were removed from the list
   manually.
