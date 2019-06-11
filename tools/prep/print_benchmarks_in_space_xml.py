#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import sys
import os
import re

g_xml_tree = None

def print_benchmarks(space, path):
    for s in space:
        if s.tag == 'Space':
            name = s.attrib['name']
            npath = os.path.join(path, name)
            print_benchmarks(s, npath)

        elif s.tag == 'Benchmark':
            name = s.attrib['name']
            npath = os.path.join(path, name)
            print(npath)

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="%s "\
                  "<space: xml>\n\n"
                  "-t <track> "\
                  "Add solvers from csv to space with divisions "\
                  "(and benchmarks)\nto upload as space xml to StarExec."\
                   % sys.argv[0])

    parser.add_argument("space_xml",
            help="the input space xml from the SMT-LIB space on StarExec "\
                    "(with divisions and benchmarks), top-level space: "\
                    "the divisions")

    parser.add_argument('-t',
            type=str, dest="track",
            help="SMT-COMP track name (one out of:"\
                    "'non-incremental', 'incremental'",
            required = True)

    args = parser.parse_args()

    if not os.path.exists(args.space_xml):
        die("file not found: {}".format(args.space_xml))

    g_xml_tree = ET.parse(args.space_xml)
    print_benchmarks(g_xml_tree.getroot(), os.path.join('/', args.track))
