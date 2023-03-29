#!/usr/bin/env python3

from argparse import ArgumentParser
from extract_data_from_solvers_divisions import g_logics_all as g_logics_all
from extract_data_from_solvers_divisions import track_raw_names_to_pretty_names as tr_raw_to_pretty

import sys
import os

def getTrackYaml(logics_indexed_by_tracks, tr_raw_to_pretty):
    tracks = []
    for track in logics_indexed_by_tracks:
        tracks.append((track, tr_raw_to_pretty[track]))

    return "\n".join(map(lambda x: "- raw_name: {}\n  pretty_name: {}".format(x[0], x[1]), tracks))


if __name__ == '__main__':
    track_yaml_file = getTrackYaml(g_logics_all, tr_raw_to_pretty)
    print(track_yaml_file)

