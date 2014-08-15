#!/usr/bin/env python
"""Create an optimized regex for matching robot user agents based on the data
compiled by http://user-agent-string.info/"""
# Standard library
import argparse
import re
import urllib
from xml.dom.minidom import parse
# Third-party
import trie


uasparser_xml_uri = "http://user-agent-string.info/rpc/get_data.php"
uasparser_xml_query = "key=free&format=xml&download=y"
download_xml_url = "%s?%s" % (uasparser_xml_uri, uasparser_xml_query)
downloaded_xml_file = "uasparser.xml"
others = ["curl", "gsa-crawler", "wget"]
default_xml_file = ""
re_trailing_version = re.compile(r"""
    (?P<robot>.{4})         # robot name
    [/ ][0-9][.][0-9].*     # trailing version
    """, re.VERBOSE)


def parser_setup():
    """Instantiate, configure, and return an argarse instance."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-f", "--file",
                    help="File containing UASparser data in xml format (if "
                    "omitted, the file will be downloaded)")
    args = ap.parse_args()
    return args


def download_uasparser_xml(xml_url, xml_file):
    """Download "Data for UASparser" in XML format."""
    urllib.urlretrieve(xml_url, xml_file)


def add_others_to_robots(robots, others_list):
    """Add others to robots set."""
    for other in others_list:
        robots.add(other)
    return robots


def add_xml_names_to_robots(robots, xml_file):
    """Add robots from "Data for UASparser" in XML format to robots set."""
    dom = parse(xml_file)
    for robot in dom.getElementsByTagName("robot"):
        for node in robot.childNodes:
            if node.localName == "family":
                family = node.firstChild.data.strip()
            if node.localName == "name":
                name = node.firstChild.data.strip()
        # Use the family title instead of the name, if it is long enough
        if len(family) > 3:
            name = family
        # Remove trailing versions (length protected in regex)
        name_new = re_trailing_version.search(name)
        if name_new:
            name = name_new.group("robot")
        if name.endswith(" b"):
            name = name.rstrip(" b")
        robots.add(name.strip())
    return robots


def create_optmized_robots_regex(robots):
    """Create an optimized regex from list of robots using a trie."""
    optimized_robots = trie.Trie()
    for robot in sorted(robots):
        optimized_robots.add(robot)
    return optimized_robots.regexp()


def main():
    robots = set()
    # Command Line Options
    args = parser_setup()

    if args.file:
        xml_file = args.file
    else:
        download_uasparser_xml(download_xml_url, downloaded_xml_file)
        xml_file = downloaded_xml_file

    robots = add_others_to_robots(robots, others)
    robots = add_xml_names_to_robots(robots, xml_file)
    optibots = create_optmized_robots_regex(robots)
    print optibots


if __name__ == "__main__":
    main()
