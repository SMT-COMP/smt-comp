all: csv plot

csv: csv-main csv-app
plot: plot-main plot-app plot-uc

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

gen-csv-app:
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

gen-csv-uc:
	./gen_common_results.py ../analysis/2016_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2016_2017.csv
	./gen_common_results.py ../analysis/2017_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2017_2018.csv
	./gen_common_results.py ../analysis/2016_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2017_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2016_2017_2018.csv
	./gen_common_results.py ../analysis/2018_Unsat_Core_Track.vbs.csv ../analysis/Unsat_Core_Track_Common_Benchmarks_2016_2017_2018.csv

awk-2015-app:
	rm -f results-files/Application_Track_vbs_2015_2016.csv
	awk -F ',' '{sum += $$14;}END{print "2015,"sum}' results-files/2015_Application_Track_vbs_2015_2016.csv >> results-files/Application_Track_vbs_2015_2016.csv
	awk -F ',' '{sum += $$14;}END{print "2016,"sum}' results-files/2016_Application_Track_vbs_2015_2016.csv >> results-files/Application_Track_vbs_2015_2016.csv

awk-2016-app:
	rm -f results-files/Application_Track_vbs_2016_2017.csv
	awk -F ',' '{sum += $$14;}END{print "2016,"sum}' results-files/2016_Application_Track_vbs_2016_2017.csv >> results-files/Application_Track_vbs_2016_2017.csv
	awk -F ',' '{sum += $$14;}END{print "2017,"sum}' results-files/2017_Application_Track_vbs_2016_2017.csv >> results-files/Application_Track_vbs_2016_2017.csv

awk-2017-app:
	rm -f results-files/Application_Track_vbs_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2017,"sum}' results-files/2017_Application_Track_vbs_2017_2018.csv >> results-files/Application_Track_vbs_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2018,"sum}' results-files/2018_Application_Track_vbs_2017_2018.csv >> results-files/Application_Track_vbs_2017_2018.csv

awk-years-app:
	rm -f results-files/Application_Track_vbs_2015_2016_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2015,"sum}' results-files/2015_Application_Track_vbs_2015_2016_2017_2018.csv >> results-files/Application_Track_vbs_2015_2016_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2016,"sum}' results-files/2016_Application_Track_vbs_2015_2016_2017_2018.csv >> results-files/Application_Track_vbs_2015_2016_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2017,"sum}' results-files/2017_Application_Track_vbs_2015_2016_2017_2018.csv >> results-files/Application_Track_vbs_2015_2016_2017_2018.csv
	awk -F ',' '{sum += $$14;}END{print "2018,"sum}' results-files/2018_Application_Track_vbs_2015_2016_2017_2018.csv >> results-files/Application_Track_vbs_2015_2016_2017_2018.csv

awk-2016-uc:
	rm -f results-files/Unsat_Core_Track_vbs_2016_2017.csv
	awk -F ',' '{sum += $$14;}END{print "2016,"sum}' results-files/2016_Unsat_Core_Track_vbs_2016_2017.csv >> results-files/Unsat_Core_Track_vbs_2016_2017.csv
	awk -F ',' '{sum += $$14;}END{print "2017,"sum}' results-files/2017_Unsat_Core_Track_vbs_2016_2017.csv >> results-files/Unsat_Core_Track_vbs_2016_2017.csv

awk-2017-uc:
	rm -f results-files/Unsat_Core_Track_vbs_2017_2018.csv
	awk -F ',' '{sum += $$9;}END{print "2017,"sum}' results-files/2017_Unsat_Core_Track_vbs_2017_2018.csv >> results-files/Unsat_Core_Track_vbs_2017_2018.csv
	awk -F ',' '{sum += $$9;}END{print "2018,"sum}' results-files/2018_Unsat_Core_Track_vbs_2017_2018.csv >> results-files/Unsat_Core_Track_vbs_2017_2018.csv

awk-years-uc:
	rm -f results-files/Unsat_Core_Track_vbs_2016_2017_2018.csv
	awk -F ',' '{sum += $$9;}END{print "2016,"sum}' results-files/2016_Unsat_Core_Track_vbs_2016_2017_2018.csv >> results-files/Unsat_Core_Track_vbs_2016_2017_2018.csv
	awk -F ',' '{sum += $$9;}END{print "2017,"sum}' results-files/2017_Unsat_Core_Track_vbs_2016_2017_2018.csv >> results-files/Unsat_Core_Track_vbs_2016_2017_2018.csv
	awk -F ',' '{sum += $$9;}END{print "2018,"sum}' results-files/2018_Unsat_Core_Track_vbs_2016_2017_2018.csv >> results-files/Unsat_Core_Track_vbs_2016_2017_2018.csv

awk-app: awk-2015-app awk-2016-app awk-2017-app awk-years-app
awk-uc: awk-2016-uc awk-2017-uc awk-years-uc

csv-app: gen-csv-app awk-app
csv-uc: gen-csv-uc awk-uc

plot-main: 2014-main 2015-main 2016-main 2017-main years-main
plot-app: 2015-app 2016-app 2017-app years-app
plot-uc: 2016-uc 2017-uc years-uc

2014-main:
	mkdir -p pdf
	Rscript cactus_plot.r 60000 67070 "Virtual Best Solver (VBS) Main Track 2014-2015" "results-files/2015_Main_Track_vbs_2014_2015.csv" "results-files/2014_Main_Track_vbs_2014_2015.csv" "VBS-2015" "VBS-2014"

2015-main:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 154238 "Virtual Best Solver (VBS) Main Track 2015-2016" "results-files/2016_Main_Track_vbs_2015_2016.csv" "results-files/2015_Main_Track_vbs_2015_2016.csv" "VBS-2016" "VBS-2015"

2016-main:
	mkdir -p pdf
	Rscript cactus_plot.r 130000 145236 "Virtual Best Solver (VBS) Main Track 2016-2017" "results-files/2017_Main_Track_vbs_2016_2017.csv" "results-files/2016_Main_Track_vbs_2016_2017.csv" "VBS-2017" "VBS-2016"

2017-main:
	mkdir -p pdf
	Rscript cactus_plot.r 190000 226429 "Virtual Best Solver (VBS) Main Track 2017-2018" "results-files/2018_Main_Track_vbs_2017_2018.csv" "results-files/2017_Main_Track_vbs_2017_2018.csv" "VBS-2018" "VBS-2017"

years-main:
	mkdir -p pdf
	Rscript cactus_plot.r 136000 145062 "Virtual Best Solver (VBS) Main Track 2015-2018" "results-files/2018_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2017_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2016_Main_Track_vbs_2015_2016_2017_2018.csv" "results-files/2015_Main_Track_vbs_2015_2016_2017_2018.csv" "VBS-2018" "VBS-2017" "VBS-2016" "VBS-2015"

2015-app:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Application Track 2015-2016" "results-files/Application_Track_vbs_2015_2016.csv" 35000000 1000000 "# Correct Answers" M

2016-app:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Application Track 2016-2017" "results-files/Application_Track_vbs_2016_2017.csv" 35000000 1000000 "# Correct Answers" M

2017-app:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Application Track 2017-2018" "results-files/Application_Track_vbs_2017_2018.csv" 35000000 1000000 "# Correct Answers" M

years-app:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Application Track 2015-2018" "results-files/Application_Track_vbs_2015_2016_2017_2018.csv" 35000000 1000000 "# Correct Answers" M

2016-uc:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Unsat Core Track 2016-2017" "results-files/Unsat_Core_Track_vbs_2016_2017.csv" 8000000 1000000 "# Reductions" "M"

2017-uc:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Unsat Core Track 2017-2018" "results-files/Unsat_Core_Track_vbs_2017_2018.csv" 8000000 1000000 "# Reductions" "M"

years-uc:
	mkdir -p pdf
	Rscript bar_plot.r "Virtual Best Solver (VBS) Unsat Core Track 2016-2018" "results-files/Unsat_Core_Track_vbs_2016_2017_2018.csv" 8000000 1000000 "# Reductions" "M"

clean:
	rm -r pdf
	rm -r results-files
