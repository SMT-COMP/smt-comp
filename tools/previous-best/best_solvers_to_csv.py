#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import re
import json

WINNER_NAME_COL = 'name'
WINNER_DIV_COL = 'division'

REG_NAME_COL = 'Solver Name'

REG_SQDIVS_COL = "Single Query Track"
REG_INDIVS_COL = "Incremental Track"
REG_MVDIVS_COL = "Model Validation Track"
REG_UCDIVS_COL = "Unsat Core Track"
REG_COMPETING_COL = "Competing"
REG_SEED_COL = "Seed"
REG_NAME_COL = "Solver Name"

RAW_TRACK_NAMES = {
    REG_SQDIVS_COL : "track_single_query",
    REG_INDIVS_COL : "track_incremental",
    REG_MVDIVS_COL : "track_model_validation",
    REG_UCDIVS_COL : "track_unsat_core"
}

# The naming convention: entrants from previous years are prepended with
# the year.
def adjustName(name, old_year):
    mo = re.match('^([1-9][0-9][0-9][0-9])-.*', name)
    if mo:
        return name
    else:
        return "%d-%s" % (old_year, name)

# Return a quoted version of the string if it contains commas
def quoteIfHasComma(entry):
    quotes = ['"', "'"]
    if ',' in entry and \
            entry[0] not in quotes and \
            entry[-1] not in quotes:
        return '"%s"' % entry
    else:
        return entry

def parse_args():
    global g_args

    parser = ArgumentParser()

    parser.add_argument("-O", "--output",
            action="store",
            dest="outfile",
            default="/dev/stdout",
            required=False,
            help="The output file")
    parser.add_argument("-d", "--divisions",
            action="store",
            dest="divisions",
            default=None,
            required=False,
            help="The json file mapping 2021 divisions to smtlib-logics")

    required = parser.add_argument_group("required arguments")
    required.add_argument("-s", "--single-query",
            action="store",
            dest="sq_winners",
            required=True,
            help="The csv containing single-query winners")
    required.add_argument("-u", "--unsat-core",
            action="store",
            dest="uc_winners",
            required=True,
            help="The csv containing unsat-core winners")
    required.add_argument("-i", "--incremental",
            action="store",
            dest="in_winners",
            required=True,
            help="The csv containing incremental winners")
    required.add_argument("-m", "--model-validation",
            action="store",
            dest="mv_winners",
            required=True,
            help="The csv containing model validation winners")
    required.add_argument("-o", "--old-registration",
            action="store",
            dest="old_registration",
            required=True,
            help="The registration csv file where the winners are from")
    required.add_argument("-n", "--new-registration",
            action="store",
            dest="new_registration",
            required=True,
            help="The registration csv file where the previous winners"\
                "would be placed")
    required.add_argument("-y", "--old-year",
            action="store",
            dest="old_year",
            required=True,
            type=int,
            help="The old result year (for renaming entries)")

    g_args = parser.parse_args()

# return a dictionary that maps
# track -> logic -> D
# where D is the set of logics in the track's division that contains
# logic
def constructLogicToDivisionLogicsMap(trackDivLogic):
    logicToDivisionLogics = dict()
    for track in trackDivLogic:
        assert track not in logicToDivisionLogics
        logicToDivisionLogics[track] = dict()
        for division in trackDivLogic[track]:
            for logic in trackDivLogic[track][division]:
                assert logic not in logicToDivisionLogics[track]
                logicToDivisionLogics[track][logic] = trackDivLogic[track][division]
    return logicToDivisionLogics


# Return a list of logics where this solver should be run as the
# best-of solver.  We run in two modes, for backwards compatibility:
# - If logicToDivisionLogics == None, then return logicList.
# - If logicToDivisionLogics != None, then return
#    \bigcup_{l \in logicList}
#      logicToDivisionLogics[track][logic] \cap
#      participated_logics
#
def getLogics(logicList, logicToDivisionLogics, track,
        participated_logics):
    if (not logicToDivisionLogics):
        # No mapping from logic to division logics -> no need to expand
        # set of logics for this solver
        return logicList

    track_raw = RAW_TRACK_NAMES[track]
    divLogicsSet = set()
    for logic in logicList:
        if logic not in logicToDivisionLogics[track_raw]:
            print("Logic %s does not exist in divisions" % logic)
        else:
            divLogicsSet.update(logicToDivisionLogics[track_raw][logic])

    divLogicsSet.intersection_update(participated_logics)
    return sorted(list(divLogicsSet))

if __name__ == '__main__':
    global g_args
    parse_args()

    logicToDivisionLogics = None
    if g_args.divisions:
        logicToDivisionLogics = \
                constructLogicToDivisionLogicsMap(json.loads(open(g_args.divisions).read()))

    winner_files= [g_args.sq_winners, g_args.uc_winners, \
            g_args.in_winners, g_args.mv_winners]

    winners = {}

    for i in range(0, len(winner_files)):
        f = winner_files[i]
        with open(f) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row[WINNER_NAME_COL]
                div = row[WINNER_DIV_COL]
                if name not in winners:
                    winners[name] = \
                            [[] for k in range(0, len(winner_files))]
                assert(i < len(winners[name]))
                winners[name][i].append(div)

    new_header = None
    with open(g_args.new_registration) as new_registration:
        new_registration = csv.DictReader(new_registration)
        new_header = next(new_registration)

    with open(g_args.old_registration) as old_registration:
        old_registration = csv.DictReader(open(g_args.old_registration))

        out = open(g_args.outfile, 'w')
        out.write("%s\n" % ",".join(list(new_header.keys())))
        for row in old_registration:
            if row[REG_NAME_COL] not in winners:
                continue
            # this is a winner row
            name = row[REG_NAME_COL]
            new_winner_row = []
            for col in new_header:
                if col in row:
                    if col in [REG_SQDIVS_COL, REG_UCDIVS_COL,
                            REG_INDIVS_COL, REG_MVDIVS_COL]:
                        if col == REG_SQDIVS_COL:
                            winning_logics = winners[name][0]
                        elif col == REG_UCDIVS_COL:
                            winning_logics = winners[name][1]
                        elif col == REG_INDIVS_COL:
                            winning_logics = winners[name][2]
                        elif col == REG_MVDIVS_COL:
                            winning_logics = winners[name][3]
                        participated_logics = row[col].split(";")
                        new_winner_row.append(";".join(
                            getLogics(winning_logics,\
                                logicToDivisionLogics,\
                                col,
                                participated_logics)))

                    elif col == REG_COMPETING_COL:
                        new_winner_row.append("no")
                    elif col == REG_SEED_COL:
                        new_winner_row.append("")
                    elif col == REG_NAME_COL:
                        new_winner_row.append(adjustName(name, \
                            g_args.old_year))
                    else:
                        new_winner_row.append(quoteIfHasComma(row[col]))
                else:
                    new_winner_row.append('')

            out.write("%s\n" % ",".join(new_winner_row))
        out.close()
