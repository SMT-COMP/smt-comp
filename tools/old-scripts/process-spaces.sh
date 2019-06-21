#!/bin/bash

#
# processes SMT-LIB space XML for some logics and produces a
# SMT-COMP space XML for each logic
# 
# must be run on a directory where space XML have been expanded,
# e.g. QF_UFLIA_XML/ QF_UFLIRA_XML/ etc.
# - a file remove.txt contains the id of all benchmarks that need
# to be removed.
# - in each directory, the original XML file must have been renamed 
# space.xml before the call
# - in each directory, an XML file is produced and compacted, it is
# ready to be uploaded to Star-Exec.
#

for dir in *_XML; do
	logic=`echo $dir | sed s/_XML//`
	xml="$logic".xml
	tgz="$xml".tgz
	(cd $dir;
		ln -s ../remove.txt;
		mv $xml space.xml;
		filter-unknown.py < space.xml > $xml;
		tar cvzf $tgz $xml;
		rm remove.txt)
done
