# This script has been written to compute the scores of SMT-COMP
# It is purposefully trying to be flexible to changes in the scoring
# mechanisms. It can be used to apply scoring schemes from different
# years of the competition to different sets of data.
#
# This script requires the pandas data analysis framework
#
# @author Giles Reger
# @date May 2019

# Data processing library pandas
import numpy as np
import pandas as pd

# Options parsing
import optparse

import sys
import csv
import math


############################
# Helper functions

all_solved_verdicts = pd.Series(['sat','unsat'])
sat_solved_verdicts = pd.Series(['sat'])
unsat_solved_verdicts = pd.Series(['unsat'])


def log(string):
  # turn this on to debug stuff 
  if(False):
    print(string)

# project out the main columns for printing
def view(data):
  return data[['benchmark','solver','result']]


# adds columns for division and family to data
# also does some tidying of benchmark column for specific years of the competition
# edit this function if you want to edit how families are added
def addDivisonFamilyInfo(data,fam):

  # Remove OtherDivision from benchmark name (2018)
  data['benchmark'] = data['benchmark'].str.replace('Other Divisions/','')
  # Remove Datatype divisions from benchmark name (2017)
  data['benchmark'] = data['benchmark'].str.replace('Datatype Divisions/','')

  # Extract divisions and as another column
  data['division'] = data['benchmark'].str.split('/').str[0]
  # Extract family as another column
  # This depends on the fam option. The 'top' option takes the top directory and the 'bot' option takes the
  # bottom directory. The rules have always specified 'top' but the scoring scripts for many years actually
  # implemented 'top'. The scripts allow you to choose.
  if fam=="top":
    log("Using top-level directories for fam")
    # Take top-level sub-directories as family
    data['family'] = np.where(data['benchmark'].str.count('/')>1,data['benchmark'].str.split('/').str[1], '-')
  elif fam=="bot":
    log("Using bottom-level directories for fam")
    # Take immediate super-directory as family
    data['family'] = data.benchmark.apply(lambda x : x[(1+x.index('/')):(x.rfind('/'))])
  else:
    print("fam option not supported: "+str(fam))
    sys.exit(0)
  return data


# drop from data any rows that contain benchmarks
# where two sound solvers disagree on the result and the
# result is unknown
def removeDisagreements(data):

  # First find unsound solvers e.g. those that disagree with the expected status
  # these solvers are ignored in the following
  unsound_solvers = data[(data.expected!="starexec-unknown") & (data.result!="starexec-unknown") & (data.result != data.expected)]['solver'].unique()

  log("Removing disagreements...")
  unknown = data[(data.expected == "starexec-unknown")] 
  for b,rows in unknown.groupby('benchmark'):
    frows = rows[(~rows.solver.isin(unsound_solvers))]
    if len(frows[(frows.result=='sat')]) > 0 and len(frows[(frows.result=='unsat')]) > 0:
       log("Removing "+b)
       log(view(rows))
       data = data[(data.benchmark!=b)]
  return data

# Returns true if the solver is competitive in the year
# This function depends on an external file 'noncompetitive.csv' which is
# provided and maintained for the official competition data
def competitive(year,solver):
  with open('noncompetitive.csv',mode='r') as f:
    reader = csv.reader(f)
    for rows in reader:
      if str(year)==rows[0] and str(solver)==rows[1]:
        return False
  return True


# Use the names in the file name_lookups.csv to rename the names of solvers
# This is used to print nice output. If you want to change how a solver
# appears in output you should update name_lookups.csv
def rename_solvers(data):
  with open('name_lookup.csv',mode='r') as f:
    reader = csv.reader(f)
    lookup = {rows[0]:rows[1] for rows in reader}
    data.solver = data.solver.apply(lambda x : lookup[x] if x in lookup else x)
    return data

# Use the names in the file name_lookups.csv to rename the given solver
# This is used to print nice output. If you want to change how a solver
# appears in output you should update name_lookups.csv
def solver_str(solver):
  with open('name_lookup.csv',mode='r') as f:
    reader = csv.reader(f)
    lookup = {rows[0]:rows[1] for rows in reader}
    if solver in lookup:
      return lookup[solver] 
    return solver 


# compute family scores
# this is based on the presentation in the SMT-COMP 2017 rules document
# but this is basically the same in all rules documents
def get_family_scores(data):
  if data.empty:
    return {}

  # the 'raw' score is alpha_b for b in the family
  raw_fam_scores = {}
  for family,fdata in data.groupby('family'):
    Fb = len(fdata.benchmark.unique())
    alpha_b = (1.0 + math.log(Fb))/Fb
    raw_fam_scores[family] = alpha_b

  # compute total of all family scores
  # this is the sum in the definition of alpha_b_prime
  score_sum = 0
  one_solver = data.iloc[0].solver
  for family, raw_score in raw_fam_scores.items():
    #size of family * its raw score
    cnt = len(data[(data.family==family) & (data.solver==one_solver)])
    score_sum += cnt*raw_score
  
  # now we get the actual family scores by dividing through
  family_scores = {family: raw_fam_scores[family]/score_sum  for family in raw_fam_scores}
  
  #for family in family_scores:
  #  print(family+": "+str(family_scores[family]))

  return family_scores

# Selects the winners (e.g. rank 0) from the results for a division and year
# Returns these as a list (there may be more than one)
def select(results, division, year):
  return results[(results.division==division) & (results.year==year) & (results.Rank==0)]['solver'].tolist()

# The same as select but turns the winners into a pretty string
def select_str(results, division, year):
  winners = select(results,division,year)
  winners_strs = sorted(map(lambda s: solver_str(s) if competitive(year,s) else "["+solver_str(s)+"]", winners))
  return " ".join(winners_strs)

# Checks the winners recorded in new_results against an existing winners.csv file
# This was used to validate this script against previous results computed by
# other scripts
def check_winners(new_results,year):
  #First load the previous files from a winners file, which should be a CSV 
  old_winners = pd.read_csv("winners.csv")
  divisions = new_results.division.unique()
  for div in divisions:
    old = old_winners[old_winners.Division==div][year].max()
    if str(old)!="nan" and str(old)!="-":
      old_list = old.split()
      new = [ solver_str(s) for s in select(new_results,div,year)]
      #if no old stuff appears in new stuff then Diff
      if (all(map(lambda o: o not in new,old_list))):
        print ("Diff in "+div+" old "+str(old)+" new "+ str(new))

# Turns a set of results into a nice LaTeX table, making some assumptions about the contents
# TODO: make more generic
def rows_to_latex(results):
 print("\\begin{tabular}{r@{\\hskip 1em}>{\\columncolor[gray]{.95}[.25em][.5em]}c@{\\hskip 1em}>{\\columncolor[gray]{.95}[.5em][.5em]}c@{\\hskip 1em}>{\\columncolor[gray]{.95}[.5em][.5em]}c@{\\hskip 1em}>{\\columncolor[gray]{.95}[.5em][0.25em]}c}") 
 print("\\toprule")
 print("\\rc")
 print("Division         &  2015                 &  2016                    &  2017                  &  2018                      \\\\")
 
 divisions = results.division.unique()
 for div in divisions:
   print(div+"	& "+ select_str(results,div,"2015") +"  & "+ select_str(results,div,"2016") +"  & "+ select_str(results,div,"2017") +"  & "+ select_str(results,div,"2018") + "  \\\\") 
 print("\\bottomrule")
 print("\\end{tabular}")

############################
# Scoring functions

# used to sort rows in results tables, follows standard ordering used throughout scoring 
# where we prefer fewer errors, then more corrects, then lower wall-time, then lower cpu time
def row_key(row):
  [year,division,solver,nsolved,error,correct,wall_total,cpu_total] = row
  return (error,-correct,wall_total,cpu_total)

# Checks if a row is competitive
def competitive_row(row):
  [year,division,solver,nsolved,error,correct,wall_total,cpu_total,rank] = row
  return competitive(year,solver) 

# This is the main scoring function that takes lots of paramters that allows it to capture
# different scoring schemes
# set wclock_limit to filter out results with higher wclock limits (useful for comparing results from different years with different time limits)
# set solved_verdicts to focus on a single verdict
# set use_families to decide whether to use the notion of family used in 2016-8
# set skip_unknowns to ignore problems with unknown results as done prior to 2017
# set sequential to apply the wallclock limit to the cpu time 
def score(data, wclock_limit, solved_verdicts,year,division,use_families,skip_unknowns,sequential):
  log("Score for "+str(year)+" in "+str(division))

  benchmark_num = len(data.benchmark.unique())
  log("Computing scores for "+division)
  log("... with "+str(benchmark_num)+" benchmarks") 

  family_scores = get_family_scores(data) if use_families else {}

  rows = []

  for solver, sdata in data.groupby('solver'):
    log("Computing scores for "+solver)
    nsolved = len(sdata[(sdata.result.isin(solved_verdicts))])
    error = 0.0
    correct = 0.0
    wall_total = 0.0
    cpu_total = 0.0
    for family, sfdata in sdata.groupby('family'):
      modifier = family_scores[family] if use_families else 1
      
      sf_wrong = len(sfdata[(sfdata.result!="starexec-unknown") & (sfdata.result != sfdata.expected) & (sfdata.expected != "starexec-unknown")])
      rf_solved = sfdata[(sfdata.result.isin(solved_verdicts)) & ((sfdata.expected=="starexec-unknown") | (sfdata.result==sfdata.expected) ) & (sfdata.wallclock_time <= wclock_limit)]
      if skip_unknowns: 
        rf_solved = sfdata[(sfdata.result.isin(solved_verdicts)) & (sfdata.result==sfdata.expected) & (sfdata.wallclock_time <= wclock_limit)]

      if sequential:
        rf_solved = sfdata[(sfdata.result.isin(solved_verdicts)) & ((sfdata.expected=="starexec-unknown") | (sfdata.result==sfdata.expected) ) & (sfdata.cpu_time <= wclock_limit)]
        if skip_unknowns: 
          rf_solved = sfdata[(sfdata.result.isin(solved_verdicts)) & (sfdata.result==sfdata.expected) & (sfdata.cpu_time <= wclock_limit)]

      sf_solved = len(rf_solved)

      this_mod = benchmark_num*modifier if use_families else 1

      error += sf_wrong*this_mod
      correct += sf_solved*this_mod
      #wall_total += rf_solved.wallclock_time.sum()*modifier
      for d in rf_solved.wallclock_time:
        wall_total += modifier*d
      cpu_total += rf_solved.cpu_time.sum()*modifier

      #log("... "+str(error)+","+str(correct)+","+str(wall_total)+","+str(cpu_total)+" with "+str(modifier))

    psolved = 100.0 * (float(nsolved)/benchmark_num) 
    row = [year,division,solver,psolved,error,correct,wall_total,cpu_total]
    rows.append(row)
    log("Row: "+str(row))

  # After computing a row per solver we then sort and rank them
  # Note that competitive solvers cannot get awarded a rank and merely
  # get the current rank without increasing it
  rows.sort(key=row_key)
  rank = 0
  for row in rows:
    row.append(rank)
    competitive = competitive_row(row)
    row.append(competitive)
    if competitive:
      rank+=1
  return rows

############################
# Processing

# Compute the virtual best solver from some data
# E.g. for each benchmark only keep the solver that solved it fastest
def virtual_best_solver_filter(data,year):
  data['competitive'] = data.apply(lambda x: competitive(year,x['solver']),axis=1)
  non_com = data[data['competitive']==True]
  sorted = non_com.sort_values(by='wallclock_time')
  result = sorted.groupby('benchmark_id', as_index=False).first()
  return result


# This function processes a CSV file containing many divisions and computes all of the scores
# It has some similar options to the scoring function but some others as well.
# The new options are as follows (for others, see scoring function)
# Set disagreements if you want to remove disagreements - the only reason not to do this is that it is expensive, so just when testing
# Set division if you only want to compute the results for fixed divisions (; separated list e.g. "UF;BV"), set this to "-" if you want to run for all divisions 
def process_csv(csv,family,division,disagreements,year,time_limit,verdicts,use_families,skip_unknowns,sequential):

  log("Process "+str(csv)+" with "+str((family,division,disagreements,year,time_limit,use_families,skip_unknowns,sequential,verdicts)))

  # Load CSV file
  data = pd.read_csv(csv)

  # Remove spaces from columns for ease (other functions rely on this)
  cols = data.columns
  cols = cols.map(lambda x: x.replace(' ', '_'))
  data.columns = cols

  data = addDivisonFamilyInfo(data,family)

  if division != "-":
    divisions = division.split(';')
    data = data[(data.division.isin(divisions))]

  #TODO: add options to select global ranking outputs
  #data = virtual_best_solver_filter(data)

  if disagreements:
    data = removeDisagreements(data)

  # Now for each division compute the score
  rows = []
  for division,div_data in data.groupby('division'):
    log("Compute for "+division)
    res=score(div_data,time_limit,verdicts,str(year),division,use_families,skip_unknowns,sequential)
    rows+=res
    

  results = pd.DataFrame(rows,columns= ['year','division','solver','psolved','error','correct','wall','cpu','Rank','competitive'])

  #print(results)
  return results


# This function runs with specific values for certain years but keeps some options open to allow
# us to try diferent things
# Assumes csv files for different years are stored in a hardcoded place. TODO: make more generic
def run(family,division,verdicts,tlimit,bytotal,sequential,skip_unknowns):

  df15 = process_csv("csvs/2015.csv",family,division,False,2015,min(2400,tlimit),verdicts,False,skip_unknowns,sequential)
  df16 = process_csv("csvs/2016.csv",family,division,False,2016,min(2400,tlimit),verdicts,(not bytotal),skip_unknowns,sequential)
  df17 = process_csv("csvs/2017.csv",family,division,True,2017,min(1200,tlimit),verdicts,(not bytotal),skip_unknowns,sequential)
  df18 = process_csv("csvs/2018.csv",family,division,True,2018,min(1200,tlimit),verdicts,(not bytotal),skip_unknowns,sequential)

  results = pd.concat([df15,df16,df17,df18],ignore_index=True)

  return results

# Checks winners for a fixed number of years
# TODO: make more generic
def check_all_winners(results):

  print("Check differences")
  print("2015")
  check_winners(results,"2015") 
  print("2016")
  check_winners(results,"2016") 
  print("2017")
  check_winners(results,"2017") 
  print("2018")
  check_winners(results,"2018") 

def winners(data):
  top = data.copy()
  #res =  top[(data.Rank==0) & (data.competitive==True)]
  res =  top[(data.Rank==0)]
  return res

# Finds the difference between two sets of results, allows us to compare two scoring mechanisms
# This was useful when preparing the SMT-COMP journal paper and for discussing how scoring rules
# could be changed
def project(normal,other):
  normal = rename_solvers(normal)
  other = rename_solvers(other)
  different = pd.concat([normal,other],keys=['normal','other']).drop_duplicates(keep=False,subset=['year','division','solver','Rank'])
  if different.empty:
    return different
  other_different = different.loc['other']
  return other_different


# Computes the new global ranking based on the distance between
# the winner of a division and the second solver in a division
def biggest_lead_ranking(data,thing):
	for division,div_data in data.groupby('division'):
	 div_data = div_data[div_data['competitive']==True]
	 if len(div_data)>2:
	  #try:
	    first = div_data[(div_data.Rank==0) & (div_data['competitive']==True)].max()
	    second = div_data[(div_data.Rank==1) & (div_data['competitive']==True)].max()
	    pdif = ((1+first.correct) / (1+second.correct)) 
	    print(thing+" "+str(pdif)+" in " +division+" for "+solver_str(first.solver)+" and "+solver_str(second.solver))
	  #except:
  	    #print("zz Error in "+division+" with "+thing)

 
# TODO: Slightly different from that in rules document, update 
def vbs_winners(data):
  print(data)
  winners = data.sort_values('psolved').groupby('solver').first()
  winners = winners.sort_values('psolved').groupby('year').tail(3)
  print(winners)


if __name__ == "__main__":

# Set up options for script
  parser = optparse.OptionParser()
  #parser.add_option('-c','--csv',action="store",dest="csv",help="csv file destination")
  parser.add_option('-f','--family_choice',action="store",dest="family",help="Choose top for the default family as sub-directory and bot for family as smallest dir",default="bot")
  parser.add_option('-d','--division_only',action="store",dest="division",help="Restrict attention to a single division",default="-")
  parser.add_option('-s','--sequential',action="store",dest="sequential",help="Compute sequential scores",default=False)

  options, args = parser.parse_args()
  #if not options.csv:
  #  parser.error("You must provide a csv file using -c")
  
  print("PARALLEL")
  normal = run(options.family,options.division,all_solved_verdicts,2400,False,options.sequential,False)
  check_all_winners(normal)
  rows_to_latex(normal)
  #vbs_winners(normal)
  #biggest_lead_ranking(normal,"a_normal")

  print("UNSAT")
  unsat = run(options.family,options.division,unsat_solved_verdicts,2400,False,options.sequential,False)
  #biggest_lead_ranking(unsat,"b_unsat")
  unsat_new = project(winners(normal),winners(unsat))
  rows_to_latex(unsat_new)
  #vbs_winners(unsat)

  print("SAT")
  sat = run(options.family,options.division,sat_solved_verdicts,2400,False,options.sequential,False)
  #biggest_lead_ranking(sat,"c_sat")
  sat_new = project(winners(normal),winners(sat))
  rows_to_latex(sat_new)
  #vbs_winners(sat)

  print("24s")
  twenty_four = run(options.family,options.division,all_solved_verdicts,24,False,options.sequential,False)
  #biggest_lead_ranking(twenty_four,"d_24")
  twenty_four_new = project(winners(normal),winners(twenty_four))
  rows_to_latex(twenty_four_new)
  #vbs_winners(twenty_four)

  #print("Total Solved")
  #by_total_scored  = run(options.family,options.division,all_solved_verdicts,2400,True,options.sequential,False)
  #biggest_lead_ranking(by_total_scored,"e_total")
  #by_total_scored_new = project(winners(normal),winners(by_total_scored))
  #rows_to_latex(by_total_scored_new)

  #print("Without unknowns")
  #without_unknowns  = run(options.family,options.division,all_solved_verdicts,2400,False,options.sequential,True)
  #without_unknowns_new = project(winners(normal),winners(without_unknowns))
  #rows_to_latex(without_unknowns_new)
