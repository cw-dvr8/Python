#!/usr/bin/env python3

"""
Program: create_templates_from_schema.py

Purpose: Use a JSON validation schema to generate either csv file templates
         or an Excel workbook containing template worksheets.  The following
         will be generated as either separate files (csv) or worksheets
         within the workbook (Excel):
         - a blank template to use for data entry
         - a dictionary defining the columns in the template
         - a listing of allowable values for columns that use a controlled
           vocabulary list

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the output template file
                  Desired output - either csv or excel

Outputs: csv template file or Excel workbook

Execution: create_templates_from_schema.py <JSON schema> <output file>
             <csv/excel>

"""

import argparse
import pandas as pd
import schema_tools
import template_tools

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("output_file", type=str,
                        help="Full pathname for the output file")
    parser.add_argument("type_of_output", type=str,
                        help="Type of output (csv or excel")

    args = parser.parse_args()

    _, json_schema = schema_tools.load_and_deref(args.json_schema_file)
    definitions_df, values_df = schema_tools.get_definitions_values(json_schema)
    definitions_df = definitions_df[["key", "description"]]
    template_df = pd.DataFrame(columns=definitions_df["key"].tolist())

    if args.type_of_output == "csv":
        template_tools.template_csv(args.output_file, template_df,
                                    definitions_df, values_df)
    elif args.type_of_output == "excel":
        template_tools.template_excel(args.output_file, template_df,
                                      definitions_df, values_df)


if __name__ == "__main__":
    main()
