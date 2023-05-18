import csv,os,sys
import requests
from bs4 import BeautifulSoup

from smtcomp_orga.prep.solver_csv import *



# def main():
#     dir="data/registration"
#     input=os.path.join(dir,"solvers_divisions.csv")
#     output=os.path.join(dir,"solvers_divisions_prelim.csv")
    
#     with open(input) as file:
#         lines = list(csv.DictReader(file, delimiter=','))
        
#         for line in lines:
#             ids=line[COL_PRELIMINARY_SOLVER_ID].split(';')
#             for track in OPT_tracks:

def main():
    id=sys.argv[1]
    URL = "https://www.starexec.org/starexec/secure/details/solver.jsp?id="+id
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
            
    
    for i in soup.find_all(name="td",id="configItem"):
        a = i.a
        id=a["href"].replace("/starexec/secure/details/configuration.jsp?id=","")
        print(a.text.strip()," : ",id)
        