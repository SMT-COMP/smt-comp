#!/usr/bin/env python3

# Data processing library pandas
import numpy
import pandas

# We need higher precisions for some of the reduction scores of the unsat-core
# track.
pandas.set_option('display.precision', 16)

# Options parsing
from argparse import ArgumentParser

import json
import os
import sys
import csv
import math
import time
import datetime

# StarExec result strings
RESULT_UNKNOWN = 'starexec-unknown'
RESULT_SAT = 'sat'
RESULT_UNSAT = 'unsat'

columns = [ "benchmark", "millisecond", "result" ]

# csmtscq: cloud version of opensmt cube and conquer solver.
# csmtscqf: "fixed" cloud version of the opensmt cube and conquer solver (submitted 7/29)
# csmtsp: cloud version of the opensmt portfolio solver
# cvc5-cloud: the cloud version of cvc5
# psmtscq: parallel version of opensmt cube and conquer solver.
# psmtscqf: "fixed" parallel version of the opensmt cube and conquer solver (submitted 7/29)
# psmtsp: parallel version of the opensmt portfolio solver
# vampire-cloud: cloud version of the vampire solver
# vampire-parallel: parallel version of the vampire solver.

vampire = {
      "solver_id": "39081",
      "configuration_id": "659685",
    "name": "Vampire"
}

smtscq = {
      "solver_id": "1",
      "configuration_id": "1",
    "name": "SMTSCQ"
}

smtscqf = {
      "solver_id": "2",
      "configuration_id": "2",
    "name": "SMTSCQF"
}

smtsp = {
      "solver_id": "3",
      "configuration_id": "3",
    "name": "SMTSP"
}

cvc5 = {
      "solver_id": "4",
      "configuration_id": "4",
    "name": "CVC5"
}


files = {
    "../raw-results-cloud.csv": [
        { "file": "vampire-cloud-smt.csv",
          "solver": vampire
        },
        { "file": "csmtscq-smt.csv",
          "solver": smtscq
        },
        { "file": "csmtscqf-smt.csv",
          "solver": smtscqf
        },
        { "file": "csmtsp-smt.csv",
          "solver": smtsp
        },
        { "file": "cvc5-cloud-smt.csv",
          "solver": cvc5
        },
    ],
  "../raw-results-parallel.csv": [
        { "file": "vampire-parallel-smt.csv",
          "solver": vampire
        },
        { "file": "psmtscq-smt.csv",
          "solver": smtscq
        },
        { "file": "psmtscqf-smt.csv",
          "solver": smtscqf
        },
        { "file": "psmtsp-smt.csv",
          "solver": smtsp
        }
  ]
}

def main():

    expected = pandas.read_csv("../../prep/SMT-LIB_non_incremental_benchmarks_all_assertions.csv",index_col="benchmark",sep=",")

    cloud_map = pandas.read_csv("../../prep/selection/final/cloud-map.csv",index_col="competition name",sep=",")

    for track in files:
       print(track)
       datas=[]
       for file in files[track]:
           print("  ",file["file"])
           data=pandas.read_csv(file["file"],names=columns)
           def map_row(r):
               r["cpu time"] = r["millisecond"] / 1000.
               r["wallclock time"] = r["cpu time"]
               r["result"] = r["result"].strip()
               r["solver"] = file["solver"]["name"]
               r["solver id"] = file["solver"]["solver_id"]
               r["configuration id"] = file["solver"]["configuration_id"]
               benchmark = r["benchmark"]
               benchmark_competition_name   = benchmark.removeprefix("/home/mww/satcomp/benchmarks/smtcomp/cloud")
               # print(benchmark_competition_name)
               # print(cloud_map.to_string())
               # print(cloud_map.loc[benchmark_competition_name[0]]["smtlib name"])
               benchmark_smtlib_name = cloud_map.loc[benchmark_competition_name]["smtlib name"].replace("/non-incremental/","./")
               r["benchmark"] = benchmark_smtlib_name
               # print("### data ###\n",data)
               # print("### initial ###\n",benchmark)
               # print("### step 1 ###\n",benchmark_competition_name)
               # print("### bench[0] ###\n",benchmark_smtlib_name)
               # print("### step 2 ###\n",benchmark_smtlib_name)
               # print("### expected ###\n",expected)
               r["expected"] = expected.loc[benchmark_smtlib_name]["status"]
               r["status"] = "complete"
               return r
           datas.append(data.apply(map_row,axis=1))
           # for r in data.iloc:
           #     r = r.copy()
           #     print(r)
           #     datas.append(r)
       datas = pandas.concat(datas)
       datas.to_csv(track,index=False)

if __name__ == "__main__":
    main()
