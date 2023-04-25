#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import sys
import os
import re

from extract_data_from_solvers_divisions_split_challenge import COL_CHALLENGE_TRACK_SINGLE_QUERY
from extract_data_from_solvers_divisions_split_challenge import COL_CHALLENGE_TRACK_INCREMENTAL

COL_CHALLENGE_TRACK = 'Challenge Track'

REGEX_SINGLE_QUERY = '(.*) \(non-incremental\)'
REGEX_INCREMENTAL = '(.*) \(incremental\)'

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: %s <in-csv>" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        new_header = []
        for el in header:
            if el != COL_CHALLENGE_TRACK:
                new_header.append(el)
            else:
                new_header.append(COL_CHALLENGE_TRACK_SINGLE_QUERY)
                new_header.append(COL_CHALLENGE_TRACK_INCREMENTAL)

        new_rows = []
        old_rows = []
        for row in reader:
            old_rows.append(row)
            drow = zip(iter(header), iter(row))
            new_row = []
            for (head, data) in drow:
                if head == COL_CHALLENGE_TRACK:
                    logics = data.split(";")
                    single_query_logics = filter(lambda x: re.search(REGEX_SINGLE_QUERY, x), logics)
                    single_query_logics = map(lambda x: re.search(REGEX_SINGLE_QUERY, x).group(1), single_query_logics)
                    incremental_logics = filter(lambda x: re.search(REGEX_INCREMENTAL, x), logics)
                    incremental_logics = map(lambda x: re.search(REGEX_INCREMENTAL, x).group(1), incremental_logics)
                    single_query_logics_str = ';'.join(single_query_logics)
                    incremental_logics_str = ';'.join(incremental_logics)
                    new_row.append(single_query_logics_str)
                    new_row.append(incremental_logics_str)
                else:
                    new_row.append(data)

            new_rows.append(new_row)

    writer = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(new_header)
    for row in new_rows: writer.writerow(row)


