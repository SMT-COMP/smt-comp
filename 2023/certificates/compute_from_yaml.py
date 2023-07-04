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
        if self.get("uc_seq") and self.get("uc_par"): l.append("\\uc")
        else:
            if self.get("uc_seq"): l.append("\\uc\\textsuperscript\\seq")
            if self.get("uc_par"): l.append("\\uc\\textsuperscript\\paral")
        if self.get("mv_seq") and self.get("mv_par"): l.append("\\mv")
        else:
            if self.get("mv_seq"): l.append("\\mv\\seq")
            if self.get("mv_par"): l.append("\\mv\\paral")
        if self.get("cloud"): l.append("\\cloud")
        if self.get("parallel"): l.append("\\paralTrack")
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
    
    def isNotEmpty(self):
        return self.biggest.isNotEmpty() and self.largest.isNotEmpty()

class info:
    def __init__(self) -> None:
        self.overall = overall()
        self.divisions = defaultdict(category)
        self.logics = defaultdict(category)
    
    def latex(self,name):
        l=[]
        for (k,v) in sorted(self.divisions.items()):
            withtrack(l,k,v)
        s_for_divisions=("s" if len(l)>=2 else "")
        divisions = ", ".join(l)

        l=[]
        for (k,v) in sorted(self.logics.items()):
            withtrack(l,k,v)
        s_for_logics=("s" if len(l)>=2 else "")
        logics = ", ".join(l)
        
        return "\\MakeOnePage{{{name}}}{{{overall}}}{{{divisions}}}{{{logics}}}{{{s_for_divisions}}}{{{s_for_logics}}}"\
            .format(name=name,overall=self.overall.latex(),divisions=divisions,logics=logics,
                    s_for_divisions=s_for_divisions,s_for_logics=s_for_logics)
    
    def isNotEmpty(self):
        return self.overall.isNotEmpty() \
        or any(cat.isNotEmpty() for _,cat in self.divisions.items()) \
        or any(cat.isNotEmpty() for _,cat in self.logics.items())
    
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
    
    # if yaml["track"] == "track_cloud":
    #     select(solvers[yaml["winner_par"]],"cloud")
        
    # if yaml["track"] == "track_parallel":
    #     select(solvers[yaml["winner_par"]],"parallel")


def select_division(division,logics):
    def select(solver,track):
        for v,_ in logics[0].items():
            solver.logics[v].update(track,None)
        solver.divisions[division].update(track,True)
    return select

def add_logic(logics,list,track):
    for v,_ in list[0].items():
        logics[v,track] = True
    

def parse_pretty_names(solvers,pretty_names):
    with open(pretty_names, newline='') as input:
        input = csv.DictReader(input)
        
        for row in input:
            solvers[row["Solver Name"]].members = int(row["Members"])

def parse_experimental_division(solvers,experimental_division):
    res={}
    with open(experimental_division, newline='') as input:
        input = csv.DictReader(input)
        
        for row in input:
            res[(row["division"],"track_"+row["track"])] = True
    return res

def main(website_results,input_for_certificates,pretty_names,experimental_division):
    solvers=defaultdict(info)
    
    parse_pretty_names(solvers,pretty_names)
    solvers["-"].members = 0
    
    # Remove experimental division
    experimental_divisions=parse_experimental_division(solvers,experimental_division)

    existing_logics={}
    delayed_logic=[] #we wait to know which logic are competitive
 
    list_dir = list(os.listdir(website_results))
    list_dir.sort()
    for result in list_dir:
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
                if not (result["division"],result["track"]) in experimental_divisions:
                    update(solvers,select_division(result["division"],result["logics"]),result)
                    add_logic(existing_logics,result["logics"],result["track"])
                else:
                    print("experimental division:", result["division"],result["track"])
            else:
                delayed_logic.append(result)
                
    for result in delayed_logic:
        if (result["division"],result["track"]) in existing_logics:
            update(solvers,(lambda x,k: x.logics[result["division"]].update(k,True)),result)
        else:    
            print("experimental logic:", result["division"],result["track"])

    
    #print the result
    with open(input_for_certificates, 'w', newline='') as output:
        for (key,value) in solvers.items():
            if value.isNotEmpty() and value.members != 0:
                print("solver: ",key,"(",value.members,")")
                if True:
#                for i in range(0,value.members):
                    output.write(value.latex(key))
                    output.write("\n\\newpage\n")
                    output.flush()
            else:
                print("solver: ",key,"( no certificate )")
            

main("../../../smt-comp.github.io/_results_2023",
     "input_for_certificates.tex",
     "solvers_pretty_name.csv",
     "../experimental.csv"
     )
