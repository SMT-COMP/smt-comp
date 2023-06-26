#!/usr/bin/python3

import sys
import csv
from typing import Any
import frontmatter
import os
from collections import defaultdict
 

    
track= {
    "track_incremental": "\\inc",   
}

class category(dict):
    def latex(self):
        l=[]
        if self.get("sq_seq"): l.append("\\seq")
        if self.get("sq_par"): l.append("\\paral")
        if self.get("sq_sat"): l.append("\\sat")
        if self.get("sq_unsat"): l.append("\\unsat")
        if self.get("sq_24"): l.append("\\fast")
        if self.get("inc"): l.append("\\inc")
        if self.get("uc_seq"): l.append("\\uc\\seq")
        if self.get("uc_par"): l.append("\\uc\\paral")
        if self.get("mv_seq"): l.append("\\mv\\seq")
        if self.get("mv_par"): l.append("\\mv\\paral")
        if self.get("cloud"): l.append("\\cloud")
        return ",".join(l)
    
    def isNotEmpty(self):
        for _,v in self.items():
            if v:
                return True
        return False
    
    def update (self, name, value) -> None:
        if self.get(name,False) is None:
            return
        else:
            self[name] = value


def withtrack(l,name,category):
    if category.isNotEmpty():
      l.append("\\withtrack{{{name}}}{{{category}}}"\
            .format(name=name.replace("_","\\_"),category=category.latex()))

class overall:
    
    def __init__(self) -> None:
        self.biggest = category()
        self.largest = category()

    def latex(self):
        l=[]
        withtrack(l,"Biggest Lead",self.biggest)
        withtrack(l,"Largest Contribution",self.largest)
        return ", ".join(l)
    
    def __str__(self):
        return self.latex()

class info:
    def __init__(self) -> None:
        self.overall = overall()
        self.divisions = defaultdict(category)
        self.logics = defaultdict(category)
    
    def latex(self,name):
        l=[]
        for (k,v) in self.divisions.items():
            withtrack(l,k,v)
        divisions = ", ".join(l)

        l=[]
        for (k,v) in self.logics.items():
            withtrack(l,k,v)
        logics = ", ".join(l)
        
        return "\\MakeOnePage{{{name}}}{{{overall}}}{{{divisions}}}{{{logics}}}"\
            .format(name=name,overall=self.overall.latex(),divisions=divisions,logics=logics)
    
    def __str__(self) -> str:
        return str(self.overall)
    
    def __repr__(self) -> str:
        return str(self.overall)

def update(solvers,select,yaml):
    if yaml["track"] == "track_single_query":
        select(solvers[yaml["winner_seq"]],"sq_seq")
        select(solvers[yaml["winner_par"]],"sq_par")
        select(solvers[yaml["winner_sat"]],"sq_sat")
        select(solvers[yaml["winner_unsat"]],"sq_unsat")
        select(solvers[yaml["winner_24s"]],"sq_24")

    if yaml["track"] == "track_incremental":
        select(solvers[yaml["winner_par"]],"inc")

    if yaml["track"] == "track_unsat_core":
        select(solvers[yaml["winner_par"]],"uc_par")
        select(solvers[yaml["winner_seq"]],"uc_seq")
    
    if yaml["track"] == "track_model_validation":
        select(solvers[yaml["winner_par"]],"mv_par")
        select(solvers[yaml["winner_seq"]],"mv_seq")
    
    if yaml["track"] == "track_cloud":
        select(solvers[yaml["winner_par"]],"cloud")

def select_division(division,logics):
    def select(solver,track):
        for v,_ in logics[0].items():
            solver.logics[v].update(track,None)
        solver.divisions[division].update(track,True)
    return select
    

def main():
    website_results = sys.argv[1]
    input_for_certificates = sys.argv[2]
    solvers=defaultdict(info)
 
    for result in os.listdir(website_results):
        file = os.path.join(website_results,result)
        if not os.path.isfile(file):
            break

        
        result = frontmatter.load(file)
        
        if result["layout"] == "results_summary":
            print("Useless: ",file)
            continue
        
        if result.get("recognition") == "biggest_lead":
            update(solvers,(lambda x,k: x.overall.biggest.update(k,True)),result)
        
        elif result.get("recognition") == "largest_contribution":
            update(solvers,(lambda x,k: x.overall.largest.update(k,True)),result)
            
        else:          
            if "logics" in result:
                update(solvers,select_division(result["division"],result["logics"]),result)
            else:
                update(solvers,(lambda x,k: x.logics[result["division"]].update(k,True)),result)
    
    #print the result
    with open(input_for_certificates, 'w', newline='') as output:
        for (key,value) in solvers.items():
            print("solver: ",key)
            output.write(value.latex(key))
            output.write("\n\\newpage\n")
            output.flush()
            

main()
