# A script that counts the ratio of different status problems appearing
# in results files. This was used to prepare the SMT-COMP journal paper
# and could form the basis of other similar analyses.
#
# This script requires the pandas data analysis framework
#
# @author Giles Reger
# @date May 2019

# Data processing library pandas
import numpy as np
import pandas as pd
import sys
import csv

# Options parsing
import optparse

import math


############################
def addDivisionInfo(data):

  # Remove OtherDivision from benchmark name (2018)
  data['benchmark'] = data['benchmark'].str.replace('Other Divisions/','')
  # Remove Datatype divisions from benchmark name (2017)
  data['benchmark'] = data['benchmark'].str.replace('Datatype Divisions/','')
  # Extract divisions and as another column
  data['division'] = data['benchmark'].str.split('/').str[0]
  return data

def process_csv(csv,year,unknown):

  # Load CSV file
  data = pd.read_csv(csv)

  # Remove spaces from columns for ease
  cols = data.columns
  cols = cols.map(lambda x: x.replace(' ', '_'))
  data.columns = cols

  #only grab the benchmarks and their expected value
  data = data[['benchmark','expected']]
  data = data.drop_duplicates(subset='benchmark',keep='first')

  # extract division as separate column
  data = addDivisionInfo(data)
  
  print(year)
  total = len(data)
  round_it = lambda x : str(int(round(100*(x/total))))
  if unknown:
    print("("+round_it(len(data[(data.expected=="sat")]))+":"+round_it(len(data[(data.expected=="unsat")]))+":"+round_it(len(data[(data.expected=="starexec-unknown")]))+")")
  else:
    print("("+round_it(len(data[(data.expected=="sat")]))+":"+round_it(len(data[(data.expected=="unsat")]))+")")

  all = data.groupby('division').count()[['expected']]
  unsat = data[(data.expected=="unsat")].groupby('division').count()[['expected']]
  sat = data[(data.expected=="sat")].groupby('division').count()[['expected']]

  all.columns=['all']
  unsat.columns=['unsat']
  sat.columns=['sat']

  together = pd.concat([all,unsat,sat],axis=1,sort=True)
  together = together.fillna(0).astype({"unsat":int,"sat":int})
  together['unsat_p'] = together[['unsat','all']].apply(lambda x : int(round(100*(x[0]/x[1]))), axis=1)
  together['sat_p'] = together[['sat','all']].apply(lambda x : int(round(100*(x[0]/x[1]))), axis=1)

  if unknown:
    together['unknown_p'] = together[['unsat','sat','all']].apply(lambda x : int(round(100*((x[2]-(x[0]+x[1]))/x[2]))),axis=1)
    together[year] = together[['all','sat_p','unsat_p','unknown_p']].apply(lambda x : str(x[0])+" ("+str(x[1])+":"+str(x[2])+":"+str(x[3])+")", axis=1)
  else:
    together[year] = together[['all','sat_p','unsat_p']].apply(lambda x : str(x[0])+" ("+str(x[1])+":"+str(x[2])+")", axis=1)

  return together[[year]]


def rows_to_latex(results):

 divisions = results.division.unique()
 for div in sorted(divisions):
   print(div+"  & ")

def run():

  df15 = process_csv("csvs/2015.csv","2015",False)
  df16 = process_csv("csvs/2016.csv","2016",False)
  df17 = process_csv("csvs/2017.csv","2017",True)
  df18 = process_csv("csvs/2018.csv","2018",True)

  results = pd.concat([df15,df16,df17,df18],axis=1)
  results = results.fillna('-')

  print(results)




if __name__ == "__main__":

  run()
