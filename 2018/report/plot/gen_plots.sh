#! /bin/sh

base_dir=$(dirname "$0")
file_2018="$base_dir/../../csv/Main_Track.csv"
file_2017="$base_dir/2017-Main_Track.csv"
file_2016="$base_dir/../../../2016/csv/Main_Track.csv"
file_2015="$base_dir/../../../2015/csv/Main_Track.csv"
extract_script="$base_dir/extract_common_results.py"

[ -e $file_2018 ] || tar xvf "${file_2018%.*}.tar.xz" && mv Main_Track.csv $file_2018
[ -e $file_2017 ] || tar xvf "$file_2017.tar.xz"
[ -e $file_2016 ] || tar xvf "${file_2016%.*}.tar.xz" && mv Main_Track.csv $file_2016
[ -e $file_2015 ] || tar xvf "${file_2015%.*}.tar.xz" && mv Main_Track.csv $file_2015
python $extract_script -w $file_2018,$file_2017,$file_2016,$file_2015 2018,2017,2016,2015
make
