all: csv plot

csv: csv-main csv-app
plot: plot-main plot-app

csv-main:
	./gen_common_results.py ../analysis/2014_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2014_2015.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2014_2015.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2015_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2016_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2017_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Main_Track.vbs.csv ../analysis/Main_Track_Common_Benchmarks_2015_2016_2017_2018.csv

csv-app:
	./gen_common_results.py ../analysis/2015_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016.csv
	./gen_common_results.py ../analysis/2016_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2015_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2016_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2017_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Application_Track.vbs.csv ../analysis/Application_Track_Common_Benchmarks_2015_2016_2017_2018.csv

plot-main: 2014-main 2015-main 2016-main 2017-main years-main
plot-app: 2015-app 2016-app 2017-app years-app

2014-main:
	mkdir -p pdf
	Rscript cactus_plot.r 60000 67070 "Virtual Best Solver (VBS) Main Track 2014-2015" "results-files/2015_Main_Track_vbs_2014_2015.csv" "results-files/2014_Main_Track_vbs_2014_2015.csv" "VBS-2015" "VBS-2014"

2015-main:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 154238 "Virtual Best Solver (VBS) Main Track 2015-2016" "results-files/2016_Main_Track_vbs_2015_2016.csv" "results-files/2015_Main_Track_vbs_2015_2016.csv" "VBS-2016" "VBS-2015"

2015-app:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 154238 "Virtual Best Solver (VBS) Application Track 2015-2016" "results-files/2016_Application_Track_vbs_2015_2016.csv" "results-files/2015_Application_Track_vbs_2015_2016.csv" "VBS-2016" "VBS-2015"

2016-main:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 145236 "Virtual Best Solver (VBS) Main Track 2016-2017" "results-files/2017_Main_Track_vbs_2016_2017.csv" "results-files/2016_Main_Track_vbs_2016_2017.csv" "VBS-2017" "VBS-2016"

2016-app:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 145236 "Virtual Best Solver (VBS) Application Track 2016-2017" "results-files/2017_Application_Track_vbs_2016_2017.csv" "results-files/2016_Application_Track_vbs_2016_2017.csv" "VBS-2017" "VBS-2016"
2017-main:
	mkdir -p pdf
	Rscript cactus_plot.r 190000 226429 "Virtual Best Solver (VBS) Main Track 2017-2018" "results-files/2018_Main_Track_vbs_2017_2018.csv" "results-files/2017_Main_Track_vbs_2017_2018.csv" "VBS-2018" "VBS-2017"

2017-app:
	mkdir -p pdf
	Rscript cactus_plot.r 190000 226429 "Virtual Best Solver (VBS) Application Track 2017-2018" "results-files/2018_Application_Track_vbs_2017_2018.csv" "results-files/2017_Application_Track_vbs_2017_2018.csv" "VBS-2018" "VBS-2017"

years-main:
	mkdir -p pdf
	Rscript cactus_plot.r 136000 145062 "Virtual Best Solver (VBS) Main Track 2015-2018" "results-files/2018_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2017_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2016_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2015_Main_Track_vbs_2015_2016_2017_2018.csv" "VBS-2018" "VBS-2017" "VBS-2016" "VBS-2015"

years-app:
	mkdir -p pdf
	Rscript cactus_plot.r 136000 145062 "Virtual Best Solver (VBS) Application Track 2015-2018" "results-files/2018_Application_Track_vbs_2015_2016_2017_2018.csv" "results-files/2017_Application_Track_vbs_2015_2016_2017_2018.csv" "results-files/2016_Application_Track_vbs_2015_2016_2017_2018.csv" "results-files/2015_Application_Track_vbs_2015_2016_2017_2018.csv" "VBS-2018" "VBS-2017" "VBS-2016" "VBS-2015"

clean:
	rm -r pdf
	rm -r results-files
