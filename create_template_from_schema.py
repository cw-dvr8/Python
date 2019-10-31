#!/usr/bin/env python3

"""
Program: create_template_from_schema.py

Purpose: Use a JSON validation schema to generate a csv template file. If
         a definitions file is also desired, it will be created with an
         '_definitions' added to the end of the file name before the
         extension.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the output template file
                  Optional flag to generate a definitions file

Outputs: csv template file

Execution: create_template_from_schema.py <JSON schema> <output file>
               --definitions

"""

import argparse
import csv
from schema_tools import get_schema_properties

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("output_file", type=argparse.FileType("w"),
                        help="Full pathname for the output file")
    parser.add_argument("--definitions", action="store_true",
                        help="Indicates that a definitions file should be generated also")

    args = parser.parse_args()

    # Define headers for the definitions file in case one is requested.
    definition_column_headers = ["key", "type", "description", "required", "possibleValue", "possibleValueDescription", "source"]

    definitions, values = get_schema_properties(args.json_schema_file)

    # Get the schema keys into a list and then write them to the output file.
    column_header_list = []
    for column_header in definitions.keys():
        column_header_list.append(column_header)

    template_writer = csv.writer(args.output_file, delimiter=",")
    template_writer.writerow(column_header_list)
    args.output_file.close()

    # Write the definitions file if one has been requested.
    if args.definitions:

        # Create the new output file name.
        output_file_name = args.output_file.name
        if output_file_name.find(".") != -1:
            dot_location = output_file_name.find(".")
            def_output_filename = output_file_name[: dot_location] + "_definitions" + output_file_name[dot_location :]
        else:
            def_output_filename = output_file_name + "_definitions"

        def_output_file = open(def_output_filename, "w")
        definitions_writer = csv.DictWriter(def_output_file, fieldnames=definition_column_headers)
        definitions_writer.writeheader()

        for json_key in definitions:
            output_row = {}

            # Assemble the output row.
            output_row["key"] = json_key
            output_row["type"] = definitions[json_key]["type"]
            output_row["description"] = definitions[json_key]["description"]
            output_row["required"] = definitions[json_key]["required"]
            if json_key in values:
                for value_row in values[json_key]:
                    output_row["possibleValue"] = value_row["value"]
                    output_row["possibleValueDescription"] = value_row["valueDescription"]
                    output_row["source"] = value_row["source"]
                    definitions_writer.writerow(output_row)
            else:
                definitions_writer.writerow(output_row)

        def_output_file.close()


if __name__ == "__main__":
    main()
