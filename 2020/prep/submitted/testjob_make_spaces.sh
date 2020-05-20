./make_spaces.sh --mv model_validation/mv_2020_testjob2.xml --uc unsat_core/uc_2020_testjob2.xml --inc incremental/inc_2020_testjob2.xml --sq single_query/sq_2020_testjob2.xml

cd single_query
tar -cvzf sq_2020_testjob2.xml.tar.gz sq_2020_testjob2.xml
cd ..

cd incremental
tar -cvzf inc_2020_testjob2.xml.tar.gz inc_2020_testjob2.xml
cd ..

cd model_validation
tar -cvzf mv_2020_testjob2.xml.tar.gz mv_2020_testjob2.xml
cd ..

cd unsat_core
tar -cvzf uc_2020_testjob2.xml.tar.gz uc_2020_testjob2.xml
cd ..
