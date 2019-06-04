#!/usr/bin/env python3

from argparse import ArgumentParser
from extract_data_from_solvers_divisions import g_logics_all as g_logics_all
import sys
import os

def getLogicYaml(logics_indexed_by_tracks):
    logics = {}
    for track in logics_indexed_by_tracks:
        for l in logics_indexed_by_tracks[track]:
            if l not in logics:
                logics[l] = []
            logics[l].append(track)

    logic_fields = []
    for l in logics:
        sub_logic_fields = "- name: {}\n  tracks:\n{}".format(
                l, "\n".join(
                    map(lambda x: "  - {}".format(x), logics[l])))
        logic_fields.append(sub_logic_fields)
    logic_fields_str = "\n".join(logic_fields)
    return logic_fields_str

if __name__ == '__main__':
    logics_md_str = getLogicYaml(g_logics_all)
    print(logics_md_str)

