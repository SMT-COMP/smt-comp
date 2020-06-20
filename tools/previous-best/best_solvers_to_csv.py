#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import re

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

if __name__ == '__main__':
    global g_args
    parse_args()

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
        for row in old_registration:
            if row[REG_NAME_COL] not in winners:
                continue
            # this is a winner row
            name = row[REG_NAME_COL]
            new_winner_row = []
            for col in new_header:
                if col in row:
                    if col == REG_SQDIVS_COL:
                        new_winner_row.append(";".join(winners[name][0]))
                    elif col == REG_UCDIVS_COL:
                        new_winner_row.append(";".join(winners[name][1]))
                    elif col == REG_INDIVS_COL:
                        new_winner_row.append(";".join(winners[name][2]))
                    elif col == REG_MVDIVS_COL:
                        new_winner_row.append(";".join(winners[name][3]))
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

            print(",".join(new_winner_row))

