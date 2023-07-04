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

# cvc5, vampire, iprover, z3-owl

vampire = {
    "solver_id": "44484",
    "configuration_id": "741777",
    "name": "Vampire"
}

cvc5 = {
    "solver_id": "44737",
    "configuration_id": "741788",
    "name": "cvc5"
}

iprover = {
    "solver_id": "44768",
    "configuration_id": "741808",
    "name": "iProver"  
}

z3owl = {
    "solver_id": "44715",
    "configuration_id": "741784",
    "name": "Z3-Owl"  
}


files = [
    {
      "name" : "cloud",
      "dst" : "../raw-results-cloud.csv",
      "pairs" : "cloud-pairs.csv.gz",
      "solvers" : [
        { "file": "cloud-vampire.adjust-smt.csv.gz",
          "solver": vampire
        },
        { "file": "cloud-cvc5.adjust-smt.csv.gz",
          "solver": cvc5
        },

    ]},
  {
      "name" : "parallel",
      "dst" : "../raw-results-parallel.csv",
      "pairs" : "parallel-pairs.csv.gz",
      "solvers" : [
        { "file": "parallel-vampire.adjust-smt.csv.gz",
          "solver": vampire
        },
        { "file": "parallel-iprover.adjust-smt.csv.gz",
          "solver": iprover
        },
        { "file": "parallel-z3-owl.adjust-smt.csv.gz",
          "solver": z3owl
        },
  ]}
]
#AWS side:
# SAT, UNSAT represent SAT and UNSAT answers, respectively.
# TIMED_OUT is a timeout
# UNKNOWN means that the solver explicitly reported UNKNOWN.
# ERROR means that the solver explicitly reported ERROR while processing
# FAILURE means that the solver crashed, and the infrastructure reported FAILURE.

def convert_result(r):
  if r == "sat":
    return "sat"
  elif r == "unsat":
    return "unsat"
  else:
    return "starexec-unknown"

def main():

    expected = pandas.read_csv("../../prep/SMT-LIB_non_incremental_benchmarks_all_assertions.csv",index_col="benchmark",sep=",")


    for track in files:
       print(track)
       ipairs = pandas.read_csv(track["pairs"],compression='gzip',sep=",")
       pairs={}
       for i,j in ipairs.iterrows():
         #print(j.get("input file"),j.get("original name"))
         pairs[j.get("input file")]=j.get("original name")
       #print(pairs)
       datas=[]
       for file in track["solvers"]:
           print("  ",file["file"])
           data=pandas.read_csv(file["file"],compression='gzip',names=columns,header=0)
           def map_row(r):
               out=pandas.Series(dtype=str)
               out["cpu time"] = r["millisecond"] / 1000.
               out["wallclock time"] = out["cpu time"]
               out["result"] = convert_result(r["result"].strip())
               out["solver"] = file["solver"]["name"]
               out["solver id"] = file["solver"]["solver_id"]
               out["configuration id"] = file["solver"]["configuration_id"]
               benchmark = r["benchmark"]
               benchmark_competition_name = benchmark.removeprefix("/home/mww/smtcomp/2023/benchmarks/aws_selection_2023/"+track["name"])
               #print(benchmark_competition_name)
               # print(cloud_map.to_string())
               # print(cloud_map.loc[benchmark_competition_name[0]]["smtlib name"])
               benchmark_smtlib_name = pairs[benchmark_competition_name].replace("/non-incremental/","./")
               out["benchmark"] = benchmark_smtlib_name
               # print("### data ###\n",data)
               #print("### initial ###\n",benchmark)
               # print("### step 1 ###\n",benchmark_competition_name)
               # print("### bench[0] ###\n",benchmark_smtlib_name)
               #print("### step 2 ###\n",benchmark_smtlib_name)
               # print("### expected ###\n",expected)
               out["expected"] = expected.at[benchmark_smtlib_name,"status"]
               out["status"] = "complete"
               return out
           datas.append(data.apply(map_row,axis=1))
           # for r in data.iloc:
           #     r = r.copy()
           #     print(r)
           #     datas.append(r)
       datas = pandas.concat(datas)
       datas.to_csv(track["dst"],index=False)

if __name__ == "__main__":
    main()
