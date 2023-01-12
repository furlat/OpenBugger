#!/usr/bin/env python3

import argparse
import json

from openbugger.parse import python2ast


def read_file_to_string(filename):
    with open(filename, "rt") as fd:
        return fd.read()


def main(filename):
    json_tree = python2ast(filename)
    return json.dumps(json_tree, separators=(",", ":"), ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the python file to parse as an ast")
    args = parser.parse_args()
    main(args.filename)
