#!/usr/bin/env python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import sys
import os
import re

def die(msg):
    print("error: {}".format(msg))
    sys.exit(1)


def readXml(tmpl_str):
    tmpl_tree = ET.fromstring(tmpl_str)
    return tmpl_tree

def pp(el):
    print("{}\n".format(ET.tostring(el).decode('UTF-8')))

def addElems(base, file_list, name):
    for el in base:
        if el.tag == 'Space' and ('name' in el.attrib and el.attrib['name'] == name):
            for f in file_list:
                f_el = readXml(open(f).read())
                for child in f_el:
                    if child.tag == 'Space':
                        el.append(child)

            break

    return base

usage_str = """
\n
Wraps the space xmls inside the template xml's Space tag with name
given as an argument <name> and produces the resulting xml to stdout.

Usage:

  %s -n <name> <template: xml> <space: xml> [<space: xml> [...]]

Example:

  %s -n non-incremental template.xml QF_AUF.xml

"""

template_xml_help_str = """
The template xml.  Needs have as a top-level child a tag <Space ...
name=<name> />
"""

space_xml_help_str = """
A space xml.  All top-level children that have the tag Space will be
inserted."""

if __name__ == '__main__':
    s = usage_str % (sys.argv[0], sys.argv[0])
    parser = ArgumentParser(usage = s)

    parser.add_argument("template_xml", \
            help=template_xml_help_str)
    parser.add_argument("space_xmls", metavar="space", type=str, \
            nargs='+', help=space_xml_help_str)
    parser.add_argument("-n", type=str, dest="name", \
            help = "either 'incremental' or 'non-incremental'", \
            required=True)

    args = parser.parse_args()

    if not os.path.exists(args.template_xml):
        die("File not fond: {}".format(args.template_xml))


    tmpl_str = open(args.template_xml).read()
    base_el = readXml(tmpl_str)

    addElems(base_el, args.space_xmls, args.name)

    sys.stdout.write("{}".format(ET.tostring(base_el, method="html").decode('UTF-8')))

