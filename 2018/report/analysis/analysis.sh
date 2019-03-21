#!/bin/bash

set -e
set -u

################################################################################
# INPUT FILES: modify paths as needed
################################################################################

MAINTRACK_2014="../../../2014/csv/combined.csv"
MAINTRACK_2015="../../../2015/csv/Main_Track.csv"
MAINTRACK_2016="../../../2016/csv/Main_Track.csv"
MAINTRACK_2017="../../../2017/csv/Main_Track.csv"
MAINTRACK_2017_RERUN="../../../2017/csv/Main_Track_Rerun_Timeouts.csv"
MAINTRACK_2018="../../../2018/csv/Main_Track.csv"

APPLICATION_2015="../../../2015/csv/Application_Track.csv"
APPLICATION_2016="../../../2016/csv/Application_Track.csv"
APPLICATION_2017="../../../2017/csv/Application_Track.csv"
APPLICATION_2018="../../../2018/csv/Application_Track.csv"

################################################################################
# check that all input files exist
################################################################################

for FILE in "$MAINTRACK_2014" "$MAINTRACK_2015" "$MAINTRACK_2016" "$MAINTRACK_2017" "$MAINTRACK_2017_RERUN" "$MAINTRACK_2018" "$APPLICATION_2015" "$APPLICATION_2016" "$APPLICATION_2017" "$APPLICATION_2018"
do
    if [[ ! -f "$FILE" ]]; then
        echo "Error: $FILE is not a regular file."
        exit 1
    fi
done

################################################################################
# some generated files
################################################################################

MT_2014="2014_Main_Track.csv"
MT_2015="2015_Main_Track.csv"
MT_2016="2016_Main_Track.csv"
MT_2017="2017_Main_Track.csv"
MT_2018="2018_Main_Track.csv"

AP_2015="2015_Application_Track.csv"
AP_2016="2016_Application_Track.csv"
AP_2017="2017_Application_Track.csv"
AP_2018="2018_Application_Track.csv"

################################################################################

### Main track

# the 2014 data lacks a "memory usage" column; we add one (with value
# 0.0) for uniformity
while IFS=, read PAIR_ID BENCHMARK BENCHMARK_ID SOLVER SOLVER_ID CONFIG CONFIG_ID STATUS CPU_TIME WALL_TIME RESULT EXPECTED
do
    echo $PAIR_ID,$BENCHMARK,$BENCHMARK_ID,$SOLVER,$SOLVER_ID,$CONFIG,$CONFIG_ID,$STATUS,$CPU_TIME,$WALL_TIME,0.0,$RESULT,$EXPECTED
done < "$MAINTRACK_2014" > "$MT_2014"

# strip column header line
tail -n +2 "$MAINTRACK_2015" > "$MT_2015"

# strip column header line
tail -n +2 "$MAINTRACK_2016" > "$MT_2016"

# in 2017, main track job-pairs that timed out were re-run with a
# longer time limit, resulting in two separate result files that we
# merge now
./merge-2017-main-track-reruns.sh "$MAINTRACK_2017" "$MAINTRACK_2017_RERUN" > "$MT_2017"
# some main track job pairs were run in sub-spaces on StarExec; we
# remove those sub-space names from the benchmark path (for
# uniformity)
sed -i -e 's:,Datatype Divisions/:,:' "$MT_2017"
sed -i -e 's:,Other Divisions/:,:' "$MT_2017"
sed -i -e 's:,Rerun Timeouts/:,:' "$MT_2017"
sed -i -e 's:,Rerun Timeouts Datatype Divisions/:,:' "$MT_2017"

# in 2018, some main track job pairs were run in sub-spaces on
# StarExec; we remove those sub-space names from the benchmark path
# (for uniformity)
tail -n +2 "$MAINTRACK_2018"|sed -e 's:,Other Divisions/:,:' > "$MT_2018"

### Application track

# strip column header line of application track files
tail -n +2 "$APPLICATION_2015" > "$AP_2015"
tail -n +2 "$APPLICATION_2016" > "$AP_2016"
tail -n +2 "$APPLICATION_2017" > "$AP_2017"
tail -n +2 "$APPLICATION_2018" > "$AP_2018"

# delete track name column for application track files
sed -i -e 's:,Competition Application Track/:,:' "$AP_2016"
sed -i -e 's:,Competition - Application Track/:,:' "$AP_2017"
sed -i -e 's:,Competition - Application Track/:,:' "$AP_2018"

################################################################################

# identify common sets of benchmarks
./common-benchmarks.sh "$MT_2014" "$MT_2015" > Main_Track_Common_Benchmarks_2014_2015.csv
./common-benchmarks.sh "$MT_2015" "$MT_2016" > Main_Track_Common_Benchmarks_2015_2016.csv
./common-benchmarks.sh "$MT_2016" "$MT_2017" > Main_Track_Common_Benchmarks_2016_2017.csv
./common-benchmarks.sh "$MT_2017" "$MT_2018" > Main_Track_Common_Benchmarks_2017_2018.csv
./common-benchmarks.sh "$MT_2015" "$MT_2016" "$MT_2017" "$MT_2018" > Main_Track_Common_Benchmarks_2015_2016_2017_2018.csv

./common-benchmarks.sh "$AP_2015" "$AP_2016" > Application_Track_Common_Benchmarks_2015_2016.csv
./common-benchmarks.sh "$AP_2016" "$AP_2017" > Application_Track_Common_Benchmarks_2016_2017.csv
./common-benchmarks.sh "$AP_2017" "$AP_2018" > Application_Track_Common_Benchmarks_2017_2018.csv
./common-benchmarks.sh "$AP_2015" "$AP_2016" "$AP_2017" "$AP_2018" > Application_Track_Common_Benchmarks_2015_2016_2017_2018.csv

################################################################################

# determine parallelism
./parallelism.sh "$MT_2015" > Main_Track_Parallelism_2015.csv
./parallelism.sh "$MT_2016" > Main_Track_Parallelism_2016.csv
./parallelism.sh "$MT_2017" > Main_Track_Parallelism_2017.csv
./parallelism.sh "$MT_2018" > Main_Track_Parallelism_2018.csv

./parallelism.sh "$AP_2015" > Application_Track_Parallelism_2015.csv
./parallelism.sh "$AP_2016" > Application_Track_Parallelism_2016.csv
./parallelism.sh "$AP_2017" > Application_Track_Parallelism_2017.csv
./parallelism.sh "$AP_2018" > Application_Track_Parallelism_2018.csv

################################################################################

# identify unsound solvers
./unsound-solvers-main.sh "$MT_2014" > Main_Track_Unsound_Solvers_2014.csv
./unsound-solvers-main.sh "$MT_2015" > Main_Track_Unsound_Solvers_2015.csv
./unsound-solvers-main.sh "$MT_2016" > Main_Track_Unsound_Solvers_2016.csv
./unsound-solvers-main.sh "$MT_2017" > Main_Track_Unsound_Solvers_2017.csv
./unsound-solvers-main.sh "$MT_2018" > Main_Track_Unsound_Solvers_2018.csv

./unsound-solvers-app.sh "$AP_2015" > Application_Track_Unsound_Solvers_2015.csv
./unsound-solvers-app.sh "$AP_2016" > Application_Track_Unsound_Solvers_2016.csv
./unsound-solvers-app.sh "$AP_2017" > Application_Track_Unsound_Solvers_2017.csv
./unsound-solvers-app.sh "$AP_2018" > Application_Track_Unsound_Solvers_2018.csv

################################################################################

# remove unsound solvers
./remove-unsound-solvers.sh Main_Track_Unsound_Solvers_2014.csv "$MT_2014" > 2014_Main_Track.sound.csv
./remove-unsound-solvers.sh Main_Track_Unsound_Solvers_2015.csv "$MT_2015" > 2015_Main_Track.sound.csv
./remove-unsound-solvers.sh Main_Track_Unsound_Solvers_2016.csv "$MT_2016" > 2016_Main_Track.sound.csv
./remove-unsound-solvers.sh Main_Track_Unsound_Solvers_2017.csv "$MT_2017" > 2017_Main_Track.sound.csv
./remove-unsound-solvers.sh Main_Track_Unsound_Solvers_2018.csv "$MT_2018" > 2018_Main_Track.sound.csv

./remove-unsound-solvers.sh Application_Track_Unsound_Solvers_2015.csv "$AP_2015" > 2015_Application_Track.sound.csv
./remove-unsound-solvers.sh Application_Track_Unsound_Solvers_2016.csv "$AP_2016" > 2016_Application_Track.sound.csv
./remove-unsound-solvers.sh Application_Track_Unsound_Solvers_2017.csv "$AP_2017" > 2017_Application_Track.sound.csv
./remove-unsound-solvers.sh Application_Track_Unsound_Solvers_2018.csv "$AP_2018" > 2018_Application_Track.sound.csv

################################################################################

# identify conflicts (between sound solvers)
./conflicts.sh 2014_Main_Track.sound.csv > Main_Track_Conflicts_2014.csv
./conflicts.sh 2015_Main_Track.sound.csv > Main_Track_Conflicts_2015.csv
./conflicts.sh 2016_Main_Track.sound.csv > Main_Track_Conflicts_2016.csv
./conflicts.sh 2017_Main_Track.sound.csv > Main_Track_Conflicts_2017.csv
./conflicts.sh 2018_Main_Track.sound.csv > Main_Track_Conflicts_2018.csv

################################################################################

# count unique solutions (by sound solvers)
./unique-solutions.sh solver-groups.txt 2015_Main_Track.sound.csv > Main_Track_Unique_Solutions_2015.csv
./unique-solutions.sh solver-groups.txt 2016_Main_Track.sound.csv > Main_Track_Unique_Solutions_2016.csv
./unique-solutions.sh solver-groups.txt 2017_Main_Track.sound.csv > Main_Track_Unique_Solutions_2017.csv
./unique-solutions.sh solver-groups.txt 2018_Main_Track.sound.csv > Main_Track_Unique_Solutions_2018.csv

################################################################################

# In 2017 and 2018, main track job-pairs were run with a (reduced)
# time limit of 1200 s. We impose this limit also on earlier years, by
# keeping only job pairs with a wall time ($10) up to the limit.
awk -F , '($10 <= 1200)' 2014_Main_Track.sound.csv > 2014_Main_Track.1200s.csv
awk -F , '($10 <= 1200)' 2015_Main_Track.sound.csv > 2015_Main_Track.1200s.csv
awk -F , '($10 <= 1200)' 2016_Main_Track.sound.csv > 2016_Main_Track.1200s.csv
awk -F , '($10 <= 1200)' 2017_Main_Track.sound.csv > 2017_Main_Track.1200s.csv
awk -F , '($10 <= 1200)' 2018_Main_Track.sound.csv > 2018_Main_Track.1200s.csv

################################################################################

# virtual best solver (sound solvers only, with a time limit of 1200 s)
./virtual-best-solver-main.sh 2014_Main_Track.1200s.csv > 2014_Main_Track.vbs.csv
./virtual-best-solver-main.sh 2015_Main_Track.1200s.csv > 2015_Main_Track.vbs.csv
./virtual-best-solver-main.sh 2016_Main_Track.1200s.csv > 2016_Main_Track.vbs.csv
./virtual-best-solver-main.sh 2017_Main_Track.1200s.csv > 2017_Main_Track.vbs.csv
./virtual-best-solver-main.sh 2018_Main_Track.1200s.csv > 2018_Main_Track.vbs.csv

./virtual-best-solver-app.sh 2015_Application_Track.sound.csv > 2015_Application_Track.vbs.csv
./virtual-best-solver-app.sh 2016_Application_Track.sound.csv > 2016_Application_Track.vbs.csv
./virtual-best-solver-app.sh 2017_Application_Track.sound.csv > 2017_Application_Track.vbs.csv
./virtual-best-solver-app.sh 2018_Application_Track.sound.csv > 2018_Application_Track.vbs.csv

################################################################################
