#! /usr/bin/env python

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import os

def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)

def trav_space(space):
    spaces = space.findall('Space')
    for s in spaces: trav_space(s)
    benchmarks = space.findall('Benchmark')
    for b in benchmarks[1:]: space.remove(b)

if __name__ == "__main__":
    parser = ArgumentParser(
            usage="filter_test_benchmarks " \
                  "<infile: space_xml> <outfile: space_xml>\n\n"
                  "Filter space to only keep one (the first) benchmark " \
                  "in each space\n" \
                  "with benchmarks (for testing purposes).")
    parser.add_argument ("infile", help="the input space xml from StarExec")
    parser.add_argument ("outfile", help="the filtered output space xml")
    args = parser.parse_args()

    if not os.path.exists(args.infile):
        die("file not found: {}".format(args.infile))

    tree = ET.parse(args.infile)
    root = tree.getroot()
    incremental_space = root.find('.//Space[@name="incremental"]')
    non_incremental_space = root.find('.//Space[@name="non-incremental"]')
    for space in [incremental_space, non_incremental_space]:
        if space: trav_space(space)
    tree.write(args.outfile)
