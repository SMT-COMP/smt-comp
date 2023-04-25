#!/usr/bin/env python3

from argparse import ArgumentParser


import csv
import json

import sys
import os
import re

try:
    import yaml
except ModuleNotFoundError:
    print("PyYAML not installed.  Please run\n\n$ sudo pip3 install pyyaml\n\n")
    sys.exit(1)

def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

class Logic:
    def __init__(self, name, descr, tracks):
        self.name = name
        self.descr = descr
        self.tracks = tracks

    def toYamlIndex(self):
        tr_str_list = []
        for tr in self.tracks:
            tr_str_list.append("    - name: %s\n      results: %s" %\
                    (tr[0], tr[1]))
        tr_str = "\n".join(tr_str_list)
        return """
- name: %s
  tracks:
%s""" %     (self.name, tr_str)

def addMd(logics, md, p):
    base = os.path.basename(md).replace(".md", "")
    md_path = "%s.html" % os.path.join(p[1:], base)

    yml_docs = filter(lambda x: x != None, yaml.load_all(open(md).read()))
    for yml in yml_docs:
        logic = yml['division']
        track = yml['track']
        if logic not in logics:
            logics[logic] = Logic(logic, "", [])
        logics[logic].tracks.append((track, md_path))

def getMds(p):
    return map(lambda x: os.path.join(p, x), filter(lambda x: x[-3:] == ".md", os.listdir(p)))

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="%s [<md-path: md> [<md-path: md> [...]]]"\
                    "\n\n"\
                    "Produce an index using the result mds found "\
                    "in the md-paths" % sys.argv[0])
    parser.add_argument (
            "md_paths",
            metavar="md-path",
            type=str,
            nargs='*',
            help="the main csv from solver registrations")

    args = parser.parse_args()

    paths = list(args.md_paths)
    for p in paths:
        if not os.path.exists(p):
            die("path not found: {}".format(p))

    logics = {}
    for p in paths:
        mds = getMds(p)
        for md in mds:
            track = os.path.basename(os.path.dirname("%s/" % p))
            addMd(logics, md, track)

    yaml_idx_list = []
    for l in logics:
        logic = logics[l]
        yaml_idx_list.append(logic.toYamlIndex())

    print("\n".join(yaml_idx_list))
