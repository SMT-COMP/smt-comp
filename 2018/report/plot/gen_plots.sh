#! /bin/sh

base_dir=$(dirname "$0")
file_2017="$base_dir/2017-Main_Track.csv"
extract_script="$base_dir/extract_common_results.py"

[ -e $file_2017 ] || tar xvf "$file_2017.tar.xz"
python $extract_script -w $base_dir/../../csv/Main_Track.csv,$file_2017,$base_dir/../../../2016/csv/Main_Track.csv,$base_dir/../../../2015/csv/Main_Track.csv 2018,2017,2016,2015
make
