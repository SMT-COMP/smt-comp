#! /bin/bash

jobs="28689 28725 28843 28773 28726"

# 21932 datatype division manually split

#cd /Users/sylvain/strass/smtcomp/2016/

if [ "$1" = "-g" ]; then
for j in $jobs; do ./fetchJob.sh $j ; done
else
echo NOT UPDATING JOB STATUS
fi

jobsapp="16245"

# if [ "$1" != "-n" ]; then
# for j in $jobsapp; do ./fetchJobApp.sh $j ; done
# else
# echo NOT UPDATING JOB STATUS
# fi

jobsucore="16327"

# if [ "$1" != "-n" ]; then
# for j in $jobsucore; do ./fetchJobUcore.sh $j ; done
# else
# echo NOT UPDATING JOB STATUS
# fi

jobsunknown="16264"

#rm  -rf results
#mkdir results
#rm  -rf results-app
#mkdir results-app
#rm -rf results-ucore
#mkdir results-ucore


dt=`date +%s`
ds=`date`
echo Version $dt $ds
wall=1200

#echo "Main track"
#./competition $dt $wall
#echo "App track"
#./compute_app_html $dt $wall
#echo "Ucore track"
#./compute_ucore_html $dt $wall
#echo "Exp track"
#./compute_exp_html $dt $wall

sed -e s/DDD/$dt/ < results-control-template.shtml > results/results-control.shtml
sed -e s/DDD/$dt/ < toc-template.shtml > results/results-toc.shtml

#DIR=~/svn/smtcomp-code/smtcomp-web/2017
#cp results/results-*.shtml $DIR
#cp results-app/results-*.shtml $DIR
#cp results-ucore/results-*.shtml $DIR
#cp results-exp/results-*.shtml $DIR
#cd $DIR 
echo "Id79L7txvh" 
#echo p | svn --non-interactive --trust-server-cert up
#./$DIR/smtcomp-code/tools/toSF selig 2017

