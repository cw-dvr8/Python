#!/usr/bin/env python3

"""
Program: create_excel_template_from_schema.py

Purpose: Use a JSON validation schema to generate an Excel workbook with
         the following structure:
         1) template
         2) dictionary
         3) possible column values

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the output template file
                  Optional full pathname to the location of any definition
                      references.

Outputs: Excel template workbook

Execution: create_excel_template_from_schema.py <JSON schema> <output file>
               --reference_path <definition reference path>

"""

import argparse
import json
import jsonref
from openpyxl import Workbook

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("output_file", type=str,
                        help="Full pathname for the output Excel file")
    parser.add_argument("--reference_path", type=str,
                        help="Full pathname location for references")

    args = parser.parse_args()

    bool_to_string = {True: "true", False: "false"}

    template_workbook = Workbook()

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

    # Get the schema keys into a list and then write them to the template worksheet. The 
    # template worksheet will only have one row, but will have multiple columns.
    template_ws = template_workbook.active
    template_ws.title = "Template"

    column_header_list = []
    for column_header in json_schema["properties"].keys():
        column_header_list.append(column_header)

    column_number = 1
    for header_value in column_header_list:
        template_ws.cell(1, column_number).value = header_value
        column_number += 1

    # Write the dictionary to the dictionary worksheet. For keys that have a values list or
    # a regex, write the possible values to the values worksheet.
    dictionary_ws = template_workbook.create_sheet()
    dictionary_ws.title = "Dictionary"
    dictionary_ws.cell(1, 1).value = "key"
    dictionary_ws.cell(1, 2).value = "description"

    values_ws = template_workbook.create_sheet()
    values_ws.title = "Values"
    values_ws.cell(1, 1).value = "key"
    values_ws.cell(1, 2).value = "description"
    values_ws.cell(1, 3).value = "valueDescription"
    values_ws.cell(1, 4).value = "source"

    dictionary_row_number = 2
    values_row_number = 2

    for json_key in json_schema["properties"]:

        # Dictionary worksheet
        dictionary_ws.cell(dictionary_row_number, 1).value = json_key
        if "description" in json_schema["properties"][json_key]:
            dictionary_ws.cell(dictionary_row_number, 2).value = json_schema["properties"][json_key]["description"]
        dictionary_row_number += 1

        # Values worksheet
        if "pattern" in json_schema["properties"][json_key]:
            values_ws.cell(values_row_number, 1).value = json_key
            values_ws.cell(values_row_number, 2).value = json_schema["properties"][json_key]["pattern"]
            values_row_number += 1

        elif "anyOf" in json_schema["properties"][json_key]:
            for anyof_row in json_schema["properties"][json_key]["anyOf"]:
                if "const" in anyof_row:
                    values_ws.cell(values_row_number, 1).value = json_key

                    # If the value is a Boolean, we have to convert it to a string; otherwise
                    # Excel will force it into all-caps, i.e. (TRUE, FALSE) and this is not
                    # what we want.
                    if isinstance(anyof_row["const"], bool):
                        converted_value = bool_to_string.get(anyof_row["const"], anyof_row["const"])
                    else:
                        converted_value = anyof_row["const"]
                    values_ws.cell(values_row_number, 2).value = converted_value

                    if "description" in anyof_row:
                        values_ws.cell(values_row_number, 3).value = anyof_row["description"]
                    if "source" in anyof_row:
                        values_ws.cell(values_row_number, 4).value = anyof_row["source"]
                    values_row_number += 1

    template_workbook.save(args.output_file)


if __name__ == "__main__":
    main()
