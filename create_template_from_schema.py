#!/usr/bin/env python3

"""
Program: create_template_from_schema.py

Purpose: Use a JSON validation schema to generate a csv template file. If
         a definitions file is also desired, it will be created with an
         '_definitions' added to the end of the file name before the
         extension.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the output template file
                  Optional full pathname to the location of any definition
                      references.
                  Optional flag to generate a definitions file

Outputs: csv template file

Execution: create_template_from_schema.py <JSON schema> <output file>
               --reference_path <definition reference path>
               --definitions

"""

import argparse
import csv
import json
import jsonref

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("output_file", type=argparse.FileType("w"),
                        help="Full pathname for the output file")
    parser.add_argument("--reference_path", type=str,
                        help="Full pathname location for references")
    parser.add_argument("--definitions", action="store_true",
                        help="Indicates that a definitions file should be generated also")

    args = parser.parse_args()

    # Define headers for the definitions file in case one is requested.
    definition_column_headers = ["key", "type", "definition", "required", "rules", "possible values", "possible values definitions"]

    # Check to see if a reference path has been passed in. If it has, use jsonref to load
    # the validation schema.  If not, it is assumed that all of the keys are defined within
    # the schema. If they are not, it will not be possible to generate a definition for
    # those keys.
    #
    # For local files, the path that is passed in must be preceded by "file://". For remote
    # references, the full URL must be provided.
    if args.reference_path is not None:
        json_schema = jsonref.load(args.json_schema_file, base_uri=args.reference_path, jsonschema=True)
    else:
        json_schema = json.load(args.json_schema_file)

    # Get the schema keys into a list and then write them to the output file.
    column_header_list = []
    for column_header in json_schema["properties"].keys():
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

        for json_key in json_schema["properties"]:
            output_row = {}

            # Assemble the output row.
            output_row["key"] = json_key

            if len(json_schema["properties"][json_key].keys()) > 0:
                if "type" in json_schema["properties"][json_key]:
                    output_row["type"] = json_schema["properties"][json_key]["type"]

                if "description" in json_schema["properties"][json_key]:
                    output_row["definition"] = json_schema["properties"][json_key]["description"]

                if json_key in json_schema["required"]:
                    output_row["required"] = "Yes"

                if "pattern" in json_schema["properties"][json_key]:
                    output_row["rules"] = json_schema["properties"][json_key]["pattern"]

                if "anyOf" in json_schema["properties"][json_key]:
                    for anyof_row in json_schema["properties"][json_key]["anyOf"]:
                        if "const" in anyof_row:
                            if len(output_row) > 0:
                                output_row["possible values"] = anyof_row["const"]
                                if "description" in anyof_row:
                                    output_row["possible values definitions"] = anyof_row["description"]
                                definitions_writer.writerow(output_row)
                                output_row = {}
                            else:
                                output_row["possible values"] = anyof_row["const"]
                                if "description" in anyof_row:
                                    output_row["possible values definitions"] = anyof_row["description"]
                                definitions_writer.writerow(output_row)
                                output_row = {}
                else:
                    definitions_writer.writerow(output_row)

        def_output_file.close()


if __name__ == "__main__":
    main()
