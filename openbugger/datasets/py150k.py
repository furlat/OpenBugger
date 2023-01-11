# https://www.sri.inf.ethz.ch/py150
import argparse
import json
import logging
import os


def convert_ast_to_datapoint(ast_json_str: str) -> dict:
    """Convert the input AST json string to a datapoint dictionary."""
    ast = json.loads(ast_json_str.strip())
    # Perform any necessary transformations or calculations on the ast here
    return ast


def main():
    parser = argparse.ArgumentParser(description="Generate datapoints from ASTs")
    parser.add_argument(
        "--input_filepath", "-i", help="Filepath containing the ASTs to be parsed"
    )
    parser.add_argument(
        "--output_filepath",
        "-o",
        default="/tmp/new_datapoints.json",
        help="Filepath for the output datapoints",
    )

    args = parser.parse_args()
    if os.path.exists(args.output_filepath):
        os.remove(args.output_filepath)

    logging.info("Loading ASTs from: {}".format(args.input_filepath))
    with open(args.input_filepath, "r") as input_file, open(
        args.output_filepath, "w"
    ) as output_file:
        for ast_json_str in input_file:
            datapoint = convert_ast_to_datapoint(ast_json_str)
            output_file.write(json.dumps(datapoint))
    logging.info("Wrote datapoints to: {}".format(args.output_filepath))
