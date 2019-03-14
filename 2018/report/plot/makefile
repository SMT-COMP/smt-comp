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

plot:
	mkdir -p pdf
	Rscript cactus_plot.r 60000 "VBS 2014-2015" "results-files/2014_Main_Track_vbs_2014-2015.csv" "results-files/2015_Main_Track_vbs_2014-2015.csv" "VBS-2014 (2014-2015)" "VBS-2015 (2014-2015)"
	Rscript cactus_plot.r 130000 "VBS 2015-2016" "results-files/2015_Main_Track_vbs_2015-2016.csv" "results-files/2016_Main_Track_vbs_2015-2016.csv" "VBS-2015 (2015-2016)" "VBS-2016 (2015-2016)"
	Rscript cactus_plot.r 130000 "VBS 2016-2017" "results-files/2016_Main_Track_vbs_2016-2017.csv" "results-files/2017_Main_Track_vbs_2016-2017.csv" "VBS-2016 (2016-2017)" "VBS-2017 (2016-2017)"
	Rscript cactus_plot.r 190000 "VBS 2017-2018" "results-files/2017_Main_Track_vbs_2017-2018.csv" "results-files/2018_Main_Track_vbs_2017-2018.csv" "VBS-2017 (2017-2018)" "VBS-2018 (2017-2018)"

clean:
	rm -r pdf
	rm -r results-files
