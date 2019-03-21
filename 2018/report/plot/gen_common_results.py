#! /usr/bin/env python3

import os
import sys
from argparse import ArgumentParser

results = {}
benchmarks = {}
common_benchmarks = set()

if __name__ == "__main__":
    try:
        aparser = ArgumentParser()
        aparser.add_argument \
              (
                "vbs_data",
                metavar="vbs data",
                help="VBS data file"
              )
        aparser.add_argument \
              (
                "common_benchmarks",
                metavar="common benchmarks",
                help="Common benchmarks files"
              )
        args = aparser.parse_args()

        path = "{}/results-files".format(os.getcwd())
        if not os.path.exists(path): os.mkdir(path)

        with open(args.common_benchmarks, 'r') as infile:
            lines = infile.readlines()
            for benchmark in lines:
                benchmark = benchmark.strip()
                assert(benchmark not in common_benchmarks)
                common_benchmarks.add(benchmark)

        year = args.vbs_data.split(sep='/')[-1]
        year = year.split(sep='.')[0]
        years = args.common_benchmarks.split('.')[-2]
        years = years.split('/')[-1]
        years = years.replace('Main_Track_Common_Benchmarks_', '')
        years = years.replace('Application_Track_Common_Benchmarks_', '')
        outfile_name = "{}/{}_vbs_{}.csv".format(path, year, years)
        with open(outfile_name, 'w') as outfile:
            with open(args.vbs_data, 'r') as infile:
                lines = infile.readlines()
                for line in lines:
                    cols = line.split(sep=',')
                    benchmark = cols[1]
                    if benchmark in common_benchmarks:
                        outfile.write(line)

    except BrokenPipeError:
        pass
