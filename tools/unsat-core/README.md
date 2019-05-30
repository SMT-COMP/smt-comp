## Unsat-core track scripts

This directory contains scripts for helping the construction of the unsat-core job.

### Extracting the Number of Assertions

extract-num-asrts.sh extracts the number of assertions from zipped
starexec spaces containing .smt2 benchmarks.  The script creates a set
of batch jobs (for exmample for a slurm-based cluster) in the form of
shell scripts.  The jobs, once run, produce a file containing the path
to the .smt2 file and the number of assertions.

#### Example

```
$ ./extract-num-asrts.sh scripts results /path/to/LIA.zip /path/to/NIA.zip
$ for file in scripts/*.sh; do sbatch $file; sleep 1; done
...
$ cat results/*.res.out |head
./LIA/psyco/135.smt2 3
./LIA/psyco/101.smt2 11
./LIA/psyco/115.smt2 6
./LIA/psyco/132.smt2 4
./LIA/psyco/188.smt2 1
./LIA/psyco/056.smt2 10
./LIA/psyco/008.smt2 2
./LIA/psyco/020.smt2 2
./LIA/psyco/098.smt2 8
./LIA/psyco/106.smt2 1

$ cat results/*.res.out > count-asrts-results-comb.list
'''

### Enriching a Job XML File with the Number of Assertions

add_field_xml.py inserts an attribute/value pair into a benchmark using
directory strutcture to identify the space of the benchmark.  The
attribute name is provided as an argument and the scripts writes the
produced xml to a file given as an argument.  The script needs a space
xml as input (in the example below called ./non-incremental.xml), and
a file containing the spaces as a directory structure together with the
value of the attribute (below called count-asrts-results-comb.list).

#### Example

```
$ ./add_field_xml.py ./non-incremental.xml count-asrts-results-comb.list num_asrts non-incremental-with-asrt-counts.xml
'''

### Constructing the job xml

The file constructed by add_field_xml.py can be provided to the script
prepare_space_xml.py to produce a space xml file that can be uploaded to
starexec.

