all: csv plot

csv:
	./gen_common_results.py ../analysis/2014_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2014_2015.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2014_2015.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Main_Track.vbs.csv ../analysis/Common_Benchmarks_2015_2016_2017_2018.csv

plot: 2014 2015 2016 2017 years

2014:
	mkdir -p pdf
	Rscript cactus_plot.r 60000 67070 "Virtual Best Solver (VBS) 2014-2015" "results-files/2015_Main_Track_vbs_2014_2015.csv" "results-files/2014_Main_Track_vbs_2014_2015.csv" "VBS-2015" "VBS-2014"

2015:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 154238 "Virtual Best Solver (VBS) 2015-2016" "results-files/2016_Main_Track_vbs_2015_2016.csv" "results-files/2015_Main_Track_vbs_2015_2016.csv" "VBS-2016" "VBS-2015"

2016:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 145236 "Virtual Best Solver (VBS) 2016-2017" "results-files/2017_Main_Track_vbs_2016_2017.csv" "results-files/2016_Main_Track_vbs_2016_2017.csv" "VBS-2017" "VBS-2016"

2017:
	mkdir -p pdf
	Rscript cactus_plot.r 190000 226429 "Virtual Best Solver (VBS) 2017-2018" "results-files/2018_Main_Track_vbs_2017_2018.csv" "results-files/2017_Main_Track_vbs_2017_2018.csv" "VBS-2018" "VBS-2017"

years:
	mkdir -p pdf
	Rscript cactus_plot.r 136000 145062 "Virtual Best Solver (VBS) 2015-2018" "results-files/2018_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2017_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2016_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2015_Main_Track_vbs_2015_2016_2017_2018.csv" "VBS-2018" "VBS-2017" "VBS-2016" "VBS-2015"

clean:
	rm -r pdf
	rm -r results-files
