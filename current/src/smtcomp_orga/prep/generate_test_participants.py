#!/usr/bin/env python3
import sys
import datetime
import random
from extract_data_from_solvers_divisions import g_logics_all as g_logics_all
from extract_data_from_solvers_divisions import TRACK_SINGLE_QUERY_RAW as TRACK_SINGLE_QUERY_RAW
from extract_data_from_solvers_divisions import TRACK_INCREMENTAL_RAW as TRACK_INCREMENTAL_RAW
from extract_data_from_solvers_divisions import TRACK_UNSAT_CORE_RAW as TRACK_UNSAT_CORE_RAW
from extract_data_from_solvers_divisions import TRACK_MODEL_VALIDATION_RAW as TRACK_MODEL_VALIDATION_RAW

def genName():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    nameLen = int(random.random() * 6) + 2
    name = ""
    for i in range(0, nameLen):
        name += letters[int(random.random()*len(letters))]
    return name

def genDomain():
    domains = ["com", "org", "ch", "uk", "de", "bz", "pt", "fi", "mz"]
    domain = "%s.%s" % (genName(), \
            domains[int(random.random()*len(domains))])
    return domain

def genEmail():
    first = genName()
    last = genName()
    url = genDomain()
    return "%s.%s@%s" % (first, last, url)

def genUrl():
    return "/".join(["https:/", genDomain(), genName()])

def genStarexecUrl():
    return "https://www.starexec.org/starexec/secure/details/solver.jsp?id=%d" % int(random.random()*50000)

def genOrigSolver():
    if (random.random() < 0.5):
        return "%s %d" % (genName(), int(random.random()*50000))
    else:
        return ""

def genWrappedTools():
    wrapped_tools = []
    if (random.random() < 0.1):
        for i in range(0, int(5*random.random())+1):
            wrapped_tools.append(genName())
    return " ".join(wrapped_tools)

def genDerivSource():
    if (random.random() < 0.2):
        return genName()
    else:
        return ""

def genSQAndUC():
    tracks = []
    if (random.random() < 0.2):
        tracks.append("Single-Query Track")
    if (random.random() < 0.2):
        tracks.append("Unsat Core Track")

    if len(tracks) == 0:
        return ""
    else:
        return ";".join(tracks)

def genLogics(track):
    n_logics = len(g_logics_all[track])
    logics = g_logics_all[track][:]
    n_chosen_logics = int(random.random() * n_logics) + 1
    while (len(logics) > n_chosen_logics):
        logics.pop(int(random.random() * len(logics)))
    return ";".join(logics)

def genContributors():
    n_contributors = int(random.random()*10)
    contributors = []
    for i in range(0, n_contributors):
        contributors.append("%s %s" % (genName(), genName()))

    return ", ".join(contributors)

els = ['tstamp', 'email', 'solver', 'solverUrl', 'solverDescr', \
    'solverDescrTitle', 'starexecUrl', 'originalSolver', \
    'wrappedTools', 'derivedTool', 'logics_participation', 'incrementalLogics', \
    'modelValLogics', 'contributors', 'seed']

def getCompetitor(c):
    entry = []

    for el in els:
        if (isinstance(c[el], list)):
            entry.append(",".join(map(lambda x: '"%s"' % x, c[el])))
        else:
            entry.append('"%s"' % c[el])

    return ",".join(entry)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Script for generating random participants, possibly"\
            "useful for testing whether the participants generation"\
            "works smoothly.  Does not generate the csv header.")
        print("Usage: %s num-participants" % sys.argv[0])
        sys.exit(1)


    for i in range(0, int(sys.argv[1])):
        c = {}
        c['tstamp'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S %p GMT+2")
        c['email'] = genEmail()
        c['solver'] = genName()
        c['solverUrl'] = genUrl()
        c['solverDescr'] = genUrl()
        c['solverDescrTitle'] = genName()
        c['starexecUrl'] = genStarexecUrl()
        c['originalSolver'] = genOrigSolver()
        c['wrappedTools'] = genWrappedTools()
        c['derivedTool'] = genDerivSource()
        logics_participation = ["" for i in g_logics_all[TRACK_SINGLE_QUERY_RAW]]

        for i in range(0, len(logics_participation)):
            logics_participation[i] = genSQAndUC()
        c['logics_participation'] = logics_participation
        c['incrementalLogics'] = genLogics(TRACK_INCREMENTAL_RAW)
        c['modelValLogics'] = genLogics(TRACK_MODEL_VALIDATION_RAW)
        c['contributors'] = genContributors()
        c['seed'] = int(random.random()*100000)

        comptor = getCompetitor(c)
        print(comptor)
