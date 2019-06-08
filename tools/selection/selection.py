#!/usr/bin/env python

import sys, random, os.path

# Options parsing
import optparse

def read_data(data_file_names,verdict):

  logics = {}   # maps logics to a dict mapping solvers to a {(problem,family):(status,expected_status,time)} dict
  
  # loading
  for name in data_file_names:
    with open(name,"r") as f:
     #Remove header
     first=True
     for line in f:
        if first:
          first=False
          continue 

        _,prob,_,solver,_,config,_,_,time,_,memory,status,expected = line.split(",")[:13]

        if verdict != "any" and expected != verdict:
           continue

        solver_name = solver+"_"+config
        logic = prob.split("/")[0]
        # Required due to how data was run in 2018 and 2017
        if logic == "Other Divisions" or logic == "Datatype Divisions":
          logic = prob.split("/")[1]
          prob = "/".join(prob.split("/")[1:])

        if logic in logics:
       	  solvers = logics[logic]
        else:
       	  solvers = {}
       	  logics[logic] = solvers

        if solver_name in solvers:
           results = solvers[solver_name]
        else:
          results = {}
          solvers[solver_name] = results 
            
        family = "/".join(prob.split("/")[:-1])
        results[(prob,family)] = (status.strip(),expected.strip(),float(time)) 

  return logics

if __name__ == "__main__":
  

# Set up options for script
  parser = optparse.OptionParser()
  parser.add_option('-s','--seed',action="store",dest="seed",help="Specify seed")
  parser.add_option('-o','--old_csv',action="store",dest="old_csv",help="Specify the old csv containing previous years results")
  parser.add_option('-n','--new_csv',action="store",dest="new_csv",help="Specify the new csv containing new problems")
  parser.add_option('-f','--filter',action="store",dest="filter",help="Select whether you want to filter by previous years results",default=False)
  parser.add_option('-x','--out',action="store",dest="out",help="Optionally give an output file to print selected benchmark names",default="")
  parser.add_option('-v','--verdict',action="store",dest="verdict",help="Restrict problems to those with this verdict",default="any")

  options, args = parser.parse_args()

  if (not options.seed) or (not options.old_csv) or (not options.new_csv): 
    print("You need to provide a --seed, --old_csv, and --new_csv, you may also select --filter")
    sys.exit(0)

  if options.out!="" and os.path.isfile(options.out):
    print("Output file "+options.out+" already exists")
    sys.exit(0)

  #================================================================

  # Set up random object
  random.seed(options.seed) 

  # Load data on previous years results and new divisions
  # The new csv file should contain the same columns as we get
  # from StarExec with a solver called NEW but as if we had timed out e.g. 
  # x,<logic/family/path>,x,NEW,x,x,x,timeout (wallclock),5000,5000,0,starexec-unknown,unsat
  # the problem is described in the <logic/family/path> bit
  # one could put the correct status as the expected value but this script does not
  # currently use it 
  data =read_data([options.old_csv,options.new_csv],options.verdict)

  # Set time limit for interestingness. The default here is 1 second
  time_limit = 1 

  # This is used to predict the amount of time the resulting problem
  # selection will take using this number nodes. 
  #nodes = 150
  #starexec_time_limit = 1200
  
  # The rules give the following rules for the number of selected benchmarks
  # (a) If a logic contains < 300 instances, all instances will be selected
  # (b) If a logic contains between 300 and 600, a subset of 300 will be selected
  # (c) If a logic contains > 600 then 50% will be selected 
  # The following three variables represent the parameters in these rules so that
  # they can be modified if needed
  lower = 300
  upper = 600
  percent = 0.5 

  #================================================================

  # count up the time taken to run all logics
  # this assumes the same number of participants for divisions 
  # as in previous years
  #all_time = 0

  for (logic,solvers) in sorted(data.items()):

     # place eligible problems here
     eligible = set()
     new_families = {} 
       
     # map from problem to set of solvers solving it
     solved_by = {}
     #run_in = {}

     # used for statistics
     count = 0
     total = 0

     for (solver,results) in sorted(solvers.items()):
      if solver == "NEW_x":
        for ((prob,fam),(stat,expected,time)) in results.items(): 
          count = count+1
          eligible.add(prob)
          if fam not in new_families:
            new_families[fam] = set()
          new_families[fam].add(prob)
      else:
        total = total + len(results)
        for ((prob,fam),(stat,expected,time)) in results.items(): 
          #if prob not in run_in:
          #  run_in[prob] = 0
          #run_in[prob] = run_in[prob] + min(time,starexec_time_limit)
          # It's solved if it has a unsat/sat result, is solved within the time limit
          # and the solution is sound. We don't check for disagreements on unknowns here
          if (stat=="unsat" or stat=="sat") and (time<=time_limit) and (expected=="starexec-unknown" or stat==expected):
           if prob not in solved_by:
             solved_by[prob] = set()
           solved_by[prob].add(solver)

     competing_solvers = set(solvers.keys())
     if 'NEW_x' in competing_solvers:
       competing_solvers.remove('NEW_x') 
     for (prob,ss) in solved_by.items(): 
      if options.filter:
         # add problem if not all solvers solve it
         if len(ss) < len(competing_solvers):
          count = count+1
          eligible.add(prob)
      else:
         count = count+1
         eligible.add(prob) 

       # Set to True to print statistics on the reduction acheived by ignoring uninteresting 
     if False:
         per = "{0:.2f}".format(100.0 * float(total-count) / float(total))
         print logic.ljust(15),":",str(count).ljust(6),("\t (out of "+str(total)+")").ljust(20),(" "+per+"% removed   ")

     #if count != len(eligible):
     #  print "Something went wrong"
     #  print "count is "+str(count)+" but eligible is "+str(len(eligible))
     #  sys.exit(0)

     #Perform selection
     # Note that this only really makes sense for particular parameters
     # percent*upper should equal lower

     # This first check would allow us to place a minimum size but for now
     # just ignores 'empty' divisions
     count = len(eligible)
     if count > 0:
      if count <= lower: 
        select = count 
      elif count > lower and count <= upper:
        select = lower 
      else:
        select = int(percent*count)

      #for prob in eligible:
      #  print "Eligible: "+prob

      print "For ",logic.ljust(15), " selected ",str(select)
      selected = set()

      for (fam,problems) in new_families.items():
        select = select-1
        prob = random.choice(tuple(problems)) 
        eligible.remove(prob)
        selected.add(prob)
        #print "Select "+prob+" from new family "+fam

      while len(selected) < select: 
        prob = random.choice(tuple(eligible))
        eligible.remove(prob)
        selected.add(prob)

      # Uncomment this to print out the selected problems
      if options.out != "":
        with open(options.out,"a") as f:
          for prob in selected:
            f.write(prob+"\n")
