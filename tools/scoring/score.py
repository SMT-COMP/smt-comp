# This script has been written to compute the scores of SMT-COMP
# It is purposefully trying to be flexible to changes in the scoring
# mechanisms. It can be used to apply scoring schemes from different
# years of the competition to different sets of data.
#
# This script requires the pandas data analysis framework
#
# @author Giles Reger, Aina Niemetz
# @date 2019

# Data processing library pandas
import numpy as np
import pandas as pd

# Options parsing
from argparse import ArgumentParser

import os
import sys
import csv
import math
import time

g_args = None
g_non_competitive = {}

############################
# Helper functions

all_solved_verdicts = pd.Series(['sat','unsat'])
sat_solved_verdicts = pd.Series(['sat'])
unsat_solved_verdicts = pd.Series(['unsat'])

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def log(string):
    print("[score] {}".format(string))

# project out the main columns for printing
def view(data):
  return data[['benchmark','solver','result']]


# adds columns for division and family to data
# also does some tidying of benchmark column for specific years of the competition
# edit this function if you want to edit how families are added
def addDivisonFamilyInfo(data,fam):
    global g_args

    # Remove OtherDivision from benchmark name (2018)
    data['benchmark'] = data['benchmark'].str.replace('Other Divisions/','')
    # Remove Datatype divisions from benchmark name (2017)
    data['benchmark'] = data['benchmark'].str.replace('Datatype Divisions/','')

    # Extract divisions and as another column
    data['division'] = data['benchmark'].str.split('/').str[0]
    # Extract family as another column
    # This depends on the fam option. The 'top' option takes the top directory and the 'bot' option takes the
    # bottom directory. The rules have always specified 'top' but the scoring scripts for many years actually
    # implemented 'bot'. The scripts allow you to choose.
    if fam == "top":
        if g_args.log: log("Using top-level directories for fam")
        # Take top-level sub-directories as family
        data['family'] = np.where(data['benchmark'].str.count('/')>1,data['benchmark'].str.split('/').str[1], '-')
    elif fam == "bot":
        if g_args.log: log("Using bottom-level directories for fam")
        # Take immediate super-directory as family
        data['family'] = data.benchmark.apply(lambda x : x[(1+x.index('/')):(x.rfind('/'))])
    else:
        die ("family option not supported: {}".format(fam))
    return data


# Drop any rows that contain benchmarks with status unknown where two otherwise
# sound solvers disagree on the result
def removeDisagreements(data):
    global g_args
    # First find unsound solvers e.g. those that disagree with the expected status
    # these solvers are ignored in the following
    unsound_solvers = set(data[(data.expected != "starexec-unknown")
                               & (data.result != "starexec-unknown")
                               & (data.result != data.expected)]['solver'])
 
    if g_args.log: log("Removing disagreements...")
    unknown = data[(data.expected == "starexec-unknown")
                   & (~data.solver.isin(unsound_solvers))
                   & ((data.result == 'sat')
                      | (data.result == 'unsat'))]
    exclude = set()
    for b,rows in unknown.groupby('benchmark'):
        res = set(rows.result.tolist())
        if 'sat' in res and 'unsat' in res:
            if g_args.log: log("Removing "+b)
            if g_args.log: log(view(rows))
            exclude.add(b)
    data = data[~(data.benchmark.isin(exclude))]
    return data

# Returns true if the solver is competitive in the given year.
# This function depends on an external file 'noncompetitive.csv' which is
# provided and maintained for the official competition data
def competitive(year, solver):
    global g_non_competitive
    solvers = g_non_competitive.get(year)
    return not solvers or solver not in solvers

def read_competitive():
    global g_non_competitive
    with open('noncompetitive.csv', mode='r') as f:
        reader = csv.reader(f)
        for rows in reader:
            year = rows[0]
            solver = rows[1]

            if year not in g_non_competitive:
                g_non_competitive[year] = set()
            g_non_competitive[year].add(solver)


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

# Main scoring function that allows it to capture different scoring schemes.
# division       : the division to compute the scores for
# data           : the results data of this division
# wclock_limit   : the wallclock time limit
# year           : the string identifying the year of the results
# verdicts       : a pd.Series created with
#                  - ['sat', 'unsat'] to consider all solved instances
#                  - ['sat'] to consider only sat instances
#                  - ['unsat'] to consider only unsat instances
# use_families   : use weighted scoring scheme (as used from 2016-2018)
# skip_unknowns  : skip benchmarks with status unknown (as done prior to 2017)
def score(division,
          data,
          wclock_limit,
          verdicts,
          year,
          use_families,
          skip_unknowns):
    global g_args
    if g_args.log: log("Score for {} in {}".format(year, division))

    benchmark_num = len(data.benchmark.unique())
    if g_args.log: log("Computing scores for {}".format(division))
    if g_args.log: log("... with {} benchmarks".format(benchmark_num))

    family_scores = get_family_scores(data) if use_families else {}

    rows = []

    all_wrong = data[(data.result != "starexec-unknown")
                     & (data.result != data.expected)
                     & (data.expected != "starexec-unknown")]

    data = data[(data.result.isin(set(verdicts)))]

    if g_args.sequential:
        data = data[(data.cpu_time <= wclock_limit)]
    else:
        data = data[(data.wallclock_time <= wclock_limit)]

    if skip_unknowns:
        data = data[(data.result == data.expected)]
    else:
        data = data[(data.expected == "starexec-unknown")
                    | (data.result == data.expected)]

    for solver, sdata in data.groupby('solver'):
        if g_args.log: log("Computing scores for "+solver)
        nsolved = len(sdata)
        error = 0.0
        correct = 0.0
        wall_total = 0.0
        cpu_total = 0.0
        wrong_solver = all_wrong[all_wrong.solver == solver]
        for family, sfdata in sdata.groupby('family'):
            modifier = family_scores[family] if use_families else 1

            sf_wrong = len(wrong_solver[wrong_solver.family == family])
            sf_solved = len(sfdata)

            this_mod = benchmark_num * modifier if use_families else 1

            error += sf_wrong * this_mod
            correct += sf_solved * this_mod
            wall_total += sfdata.wallclock_time.sum() * modifier
            cpu_total += sfdata.cpu_time.sum() * modifier
            #if g_args.log: log("... {}, {}, {}, {} with {}".format(\
            #       error, correct, wall_total, cpu_total, modifier))

        psolved = 100.0 * (float(nsolved) / benchmark_num)
        assert psolved > 0
        row = [year, division, solver, psolved, error, correct,
               wall_total, cpu_total]
        rows.append(row)
        if g_args.log: log("Row: {}".format(row))

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


# Process a CSV file with results of one track.
# csv          : the input csv
# disagreements: set to True to remove disagreements
# year         : the string identifying the year of the results
# verdicts     : a pd.Series created with
#                - ['sat', 'unsat'] to consider all solved instances
#                - ['sat'] to consider only sat instances
#                - ['unsat'] to consider only unsat instances
# use_families : use weighted scoring scheme
# skip_unknowns: skip benchmarks with status unknown
def process_csv(csv,
                disagreements,
                year,
                time_limit,
                verdicts,
                use_families,
                skip_unknowns):
    global g_args
    if g_args.log:
        log("Process {} with family: '{}', divisions: '{}', "\
            "disagreements: '{}', year: '{}', time_limit: '{}', "\
            "use_families: '{}', skip_unknowns: '{}', sequential: '{}', "\
            "verdicts: '{}'".format(
            csv,
            g_args.family,
            g_args.divisions,
            disagreements,
            year,
            time_limit,
            g_args.use_families,
            skip_unknowns,
            g_args.sequential,
            verdicts))

    # Load CSV file
    data = pd.read_csv(csv)

    # Remove spaces from columns for ease (other functions rely on this)
    cols = data.columns
    cols = cols.map(lambda x: x.replace(' ', '_'))
    data.columns = cols

    data = addDivisonFamilyInfo(data, g_args.family)

    # -: consider all divisions
    # else list with divisions to consider
    if g_args.divisions != "-":
        divisions = g_args.divisions
        data = data[(data.division.isin(divisions))]

    #TODO: add options to select global ranking outputs
    #data = virtual_best_solver_filter(data)

    start = time.time() if g_args.show_timestamps else None
    if disagreements:
        data = removeDisagreements(data)
    if g_args.show_timestamps:
        log('time disagreements: {}'.format(time.time() - start))

    start = time.time() if g_args.show_timestamps else None
    # Now for each division compute the score
    rows = []
    for division, division_data in data.groupby('division'):
        if g_args.log: log("Compute for {}".format(division))
        res = score(division,
                    division_data,
                    time_limit,
                    verdicts,
                    year,
                    use_families,
                    skip_unknowns)
        rows+=res
    if g_args.show_timestamps:
        log('time score: {}'.format(time.time() - start))

    results = pd.DataFrame(rows,columns= [
        'year', 'division', 'solver', 'psolved', 'error', 'correct', 'wall',
        'cpu', 'Rank','competitive'])
    return results


# This function runs with specific values for certain years but keeps some
# options open to allow us to try diferent things
def gen_results_for_report_aux(verdicts, time_limit, bytotal, skip_unknowns):
    global g_args
    dataframes = []
    dataframes.append(
            process_csv(
                g_args.csv['2015'][0],
                False,
                '2015',
                min(g_args.csv['2015'][1], time_limit),
                verdicts,
                False,
                skip_unknowns))
    dataframes.append(
            process_csv(
                g_args.csv['2016'][0],
                False,
                '2016',
                min(g_args.csv['2016'][1], time_limit),
                verdicts,
                not bytotal,
                skip_unknowns))
    dataframes.append(
            process_csv(
                g_args.csv['2017'][0],
                True,
                '2017',
                min(g_args.csv['2017'][1], time_limit),
                verdicts,
                not bytotal,
                skip_unknowns))
    dataframes.append(
            process_csv(
                g_args.csv['2018'][0],
                True,
                '2018',
                min(g_args.csv['2018'][1], time_limit),
                verdicts,
                not bytotal,
                skip_unknowns))
    return pd.concat(dataframes, ignore_index=True)


def gen_results_for_report():
    global g_args

    print("PARALLEL")
    start = time.time() if g_args.show_timestamps else None
    normal = gen_results_for_report_aux(
            all_solved_verdicts, 2400, False, False)
    check_all_winners(normal)
    rows_to_latex(normal)
    #vbs_winners(normal)
    #biggest_lead_ranking(normal,"a_normal")
    if g_args.show_timestamps:
        log('time parallel: {}'.format(time.time() - start))

    print("UNSAT")
    start = time.time() if g_args.show_timestamps else None
    unsat = gen_results_for_report_aux(
            unsat_solved_verdicts, 2400, False, False)
    #biggest_lead_ranking(unsat,"b_unsat")
    unsat_new = project(winners(normal), winners(unsat))
    rows_to_latex(unsat_new)
    #vbs_winners(unsat)
    if g_args.show_timestamps:
        log('time unsat: {}'.format(time.time() - start))

    print("SAT")
    start = time.time() if g_args.show_timestamps else None
    sat = gen_results_for_report_aux(
            sat_solved_verdicts, 2400, False, False)
    #biggest_lead_ranking(sat,"c_sat")
    sat_new = project(winners(normal),winners(sat))
    rows_to_latex(sat_new)
    #vbs_winners(sat)
    if g_args.show_timestamps:
        log('time sat: {}'.format(time.time() - start))

    print("24s")
    start = time.time() if g_args.show_timestamps else None
    twenty_four = gen_results_for_report_aux(
            all_solved_verdicts, 24, False, False)
    #biggest_lead_ranking(twenty_four,"d_24")
    twenty_four_new = project(winners(normal),winners(twenty_four))
    rows_to_latex(twenty_four_new)
    #vbs_winners(twenty_four)
    if g_args.show_timestamps:
        log('time 24s: {}'.format(time.time() - start))

    #print("Total Solved")
    #by_total_scored  = gen_results_for_report_aux(
    #        all_solved_verdicts, 2400, True, False)
    #biggest_lead_ranking(by_total_scored,"e_total")
    #by_total_scored_new = project(winners(normal),winners(by_total_scored))
    #rows_to_latex(by_total_scored_new)

    #print("Without unknowns")
    #without_unknowns  = gen_results_for_report_aux(
    #         all_solved_verdicts, 2400, False, True)
    #without_unknowns_new = project(winners(normal),winners(without_unknowns))
    #rows_to_latex(without_unknowns_new)

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


def parse_args():
    global g_args
    parser = ArgumentParser()
    parser.add_argument ("-c", "--csv",
                         metavar="path[,path...]",
                         help="list of input csvs with results from StarExec")
    parser.add_argument ("-y", "--year",
                         metavar="year[,year...]",
                         help="list of years matching given input csvs")
    parser.add_argument ("-t", "--time",
                         metavar="time[,time...]",
                         help="list of time limits matching given input csvs")
    parser.add_argument("-f", "--family-choice",
                        action="store",
                        dest="family",
                        default="bot",
                        help="Choose notion of benchmark family"\
                              "('top' for top-most directory, "\
                              "'bot' for bottom-most directory")
    parser.add_argument("-d", "--division-only",
                        metavar="division[,division...]",
                        action="store",
                        dest="divisions",
                        default="-",
                        help="Restrict attention to a single division")
    parser.add_argument("-s", "--sequential",
                        action="store_true",
                        dest="sequential",
                        default=False,
                        help="Compute sequential scores")
    parser.add_argument("-w", "--weighted",
                        action="store_true",
                        dest="use_families",
                        default=False,
                        help="Use weighted scoring scheme")
    parser.add_argument("-u", "--skip-unknowns",
                        action="store_true",
                        dest="skip_unknowns",
                        default=False,
                        help="Skip benchmarks with unknown status")
    parser.add_argument("--report",
                        action="store_true",
                        default=False,
                        help="Produce results for JSat 2015-2018 submission")
    parser.add_argument("--show-timestamps",
                        action="store_true",
                        default=False,
                        help="Log time for computation steps")
    parser.add_argument("-l", "--log",
                        action="store_true",
                        default=False,
                        help="Enable logging")
    g_args = parser.parse_args()

    if not g_args.csv:
        die ("Missing input csv(s).")
    if not g_args.year:
        die ("Missing input year(s).")
    if not g_args.time:
        die ("Missing input time(s).")

    g_args.csv = g_args.csv.split(',') if g_args.csv else []
    g_args.year = g_args.year.split(',') if g_args.year else []
    g_args.time = g_args.time.split(',') if g_args.time else []
    g_args.time = [int(t) for t in g_args.time]

    if len(g_args.year) != len(g_args.csv):
        die ("Number of given years and csv files does not match.")
    if len(g_args.time) != len(g_args.csv):
        die ("Number of given time limits and csv files does not match.")

    if g_args.report:
        assert '2015' in g_args.year
        assert '2016' in g_args.year
        assert '2017' in g_args.year
        assert '2018' in g_args.year

    tmp = zip (g_args.csv, g_args.time)
    g_args.csv = dict(zip(g_args.year, tmp))

    if g_args.divisions != "-":
        g_args.divisions = g_args.divisions.split(',')


def main():
    global g_args
    parse_args()
    read_competitive()


    if g_args.report:
        for year in g_args.csv:
            csv = g_args.csv[year][0]
            if not os.path.exists(csv):
                die("Given csv does not exist: {}".format(csv))
        gen_results_for_report()
    else:
        data = []
        for year in csvs:
            csv, time_limit = csvs[year]
            if not os.path.exists(csv):
                die("Given csv does not exist: {}".format(csv))
            data.append(
                process_csv(
                         csv,
                        True,
                        year,
                        time_limit,
                        all_solved_verdicts))
        result = pd.concat(data, ignore_index = True)
        print(result)


if __name__ == "__main__":
    main()

