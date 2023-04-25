Using score.py
==============

To generate markdowns as used in the website, for example:

   ```
   $ ./score.py -c ../../2021/results/Single_Query_Track.csv -y 2021 -t 1200 -S ../../2021/registration/solvers_divisions_final.csv -T sq -D ../../2021/new-divisions.json --gen-md test
   ```

To get bestof of a given query in a given year:

```
 $ ./score.py -y YEAR -S SOLVERS_CSV -t 1200 -c RESULTS_OF_TRACK_CSV -D DIVISONS_MAP -T TRACK --bestof OUTPUT_CSV
 ```
