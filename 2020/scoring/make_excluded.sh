#!/bin/sh

LANG=C

for i in incremental nonincremental; do
	sort blacklist_${i}.txt > benchmark_excluded_${i}_2020
	tar -cvJf benchmark_excluded_${i}_2020.tar.xz benchmark_excluded_${i}_2020
done
