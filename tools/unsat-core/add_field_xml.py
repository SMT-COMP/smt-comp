#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import csv
import sys
import os
import re

g_xml_tree = None
g_divisions = {}

# Print error message and exit.
def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)


# Parse the lines of the form
# ./<space>/<space>/.../<name>.smt2 <prop>

def read_lines(lines):
    els = []
    r = [None, {}]
    for l in lines:
        (path, prop) = l.split()
        path_split = path.split("/")
        assert(path_split[-1][-len(".smt2"):] == ".smt2")

        n = r
        for space in path_split[1:]:
            subspaces = n[1]
            if space not in subspaces:
                subspaces[space] = [None, {}]
            n = subspaces[space]
        n[0] = prop
    return r

# Traverse space and add result to the benchmark.
def add_result_to_benchmark(space, results, attrib_name):
    spaces = space.findall('Space')
    if len(spaces) > 0:
        for s in spaces:
            name = s.attrib['name']
            add_result_to_benchmark(s, results[1][name], attrib_name)
    else:
        benchmarks = space.findall("Benchmark")
        for benchmark in benchmarks:

            benchmark_name = benchmark.attrib["name"]
            new_field_value = results[1][benchmark_name][0]

            ET.SubElement(
                    benchmark,
                    'Attribute',
                    attrib = {
                        "name": attrib_name,
                        "value": new_field_value})

# Parse xml and the attribute file to be added
def add_attrib(attribute_file, attribute_name):
    global g_xml_tree
    root = g_xml_tree.getroot()
    space = root.find('.//Space[@name="non-incremental"]')

    attr_root = read_lines(open(attribute_file).readlines())
    add_result_to_benchmark(space, attr_root, attribute_name)

if __name__ == '__main__':
    parser = ArgumentParser(
            usage="%s <space_xml> <result> <name> <output>\n\n"\
                  "Add the value in result with tag name to xml-xpace" % sys.argv[0])
    parser.add_argument ("space_xml",
            help="the input space xml from the SMT-LIB space on StarExec "\
                    "(with divisions and benchmarks), top-level space: "\
                    "non-incremental or incremental")
    parser.add_argument ("result",
            help="the file containing the spaces as paths and the value for each space")
    parser.add_argument ("name",
            help="The name used for the tag")
    parser.add_argument ("output",
            help="The output xml file")
    args = parser.parse_args()

    if not os.path.exists(args.space_xml):
        die("file not found: {}".format(args.space_xml))
    if not os.path.exists(args.result):
        die("file not found: {}".format(args.result))

    g_xml_tree = ET.parse(args.space_xml)
    add_attrib(args.result, args.name)
    g_xml_tree.write(args.output)
