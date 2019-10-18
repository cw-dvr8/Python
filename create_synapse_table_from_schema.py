#!/usr/bin/env python3

"""
Program: create_dccvalidator_table_from_schema.py

Purpose: Use a JSON validation schema to generate a Synapse table to be
         used by the dccvalidator.

Input parameters: Full pathname to the JSON validation schema
                  ID of the Synapse parent project
                  Synapse table name

Outputs: Synapse table

Execution: create_dccvalidator_table_from_schema.py <JSON schema>
               <parent project Synapse ID>

"""

import argparse
import os
import pandas as pd
from schema_tools import convert_bool_to_string, load_and_deref, values_list_keywords
import synapseclient
from synapseclient import Column, Schema, Table
from urllib.parse import urldefrag


def process_schema(json_schema_file):

    values_list_keys = values_list_keywords()

    table_df = pd.DataFrame()
    ref_module_dict = {}

    # Load the JSON schema. Start at the "properties" level to simplify the data structure.
    ref_location_dict, json_schema = load_and_deref(json_schema_file)
    json_schema = json_schema["properties"]

    # Get the annotations module from the reference location for each key.
    for schema_key in ref_location_dict:
        ref_doc, ref_frag = urldefrag(ref_location_dict[schema_key])
        ref_path, ref_file = os.path.split(ref_doc)
        ref_module_dict[schema_key] = os.path.splitext(ref_file)[0]

    # Build a Pandas dataframe out of the schema.
    for json_key in json_schema:
        output_row = {}

        # Assemble the output row.
        output_row["key"] = json_key

        if json_key in ref_module_dict:
            output_row["module"] = ref_module_dict[json_key]

        if len(json_schema[json_key].keys()) > 0:
            if "description" in json_schema[json_key]:
                output_row["description"] = json_schema[json_key]["description"]

            if "type" in json_schema[json_key]:
                output_row["columnType"] = json_schema[json_key]["type"]

            if "maximumSize" in json_schema[json_key]:
                output_row["maximumSize"] = json_schema[json_key]["maximumSize"]

            # A values list could be designated with different keys depending on the
            # schema.
            if any([value_key in json_schema[json_key] for value_key in values_list_keys]):
                vkey = list(set(values_list_keys).intersection(json_schema[json_key]))[0]
                for values_row in json_schema[json_key][vkey]:
                    if "const" in values_row:
                        # Run the value through a function that will convert any Python
                        # Boolean values to a lower case string representation. If the
                        # value is not a Python Boolean, the function returns the original
                        # value.
                        output_row["value"] = convert_bool_to_string(values_row["const"])

                    if "description" in values_row:
                        output_row["valueDescription"] = values_row["description"]

                    if "source" in values_row:
                        output_row["source"] = values_row["source"]

                    table_df = table_df.append(output_row, ignore_index=True)
            else:
                table_df = table_df.append(output_row, ignore_index=True)
        else:
            table_df = table_df.append(output_row, ignore_index=True)

    return(table_df)


def process_new_table(args, syn):

    # Define column names for the synapse table.
    dcc_column_names = [
        Column(name="key", columnType="STRING", maximumSize=100),
        Column(name="description", columnType="STRING", maximumSize=250),
        Column(name="columnType", columnType="STRING", maximumSize=50),
        Column(name="maximumSize", columnType="DOUBLE"),
        Column(name="value", columnType="STRING", maximumSize=250),
        Column(name="valueDescription", columnType="LARGETEXT"),
        Column(name="source", columnType="STRING", maximumSize=250),
        Column(name="module", columnType="STRING", maximumSize=100)]

    syn_table_df = process_schema(args.json_schema_file)

    # Build and populate the Synapse table.
    table_schema = Schema(name=args.synapse_table_name, columns=dcc_column_names, parent=args.parent_synapse_id)
    dcc_table = syn.store(Table(table_schema, syn_table_df))


def process_overwrite_table(args, syn):

    syn_table_df = process_schema(args.json_schema_file)

    # Delete the old records from the Synapse table and then write out the
    # new ones.
    dcc_val_table = syn.get(args.table_synapse_id)
    results = syn.tableQuery(f"select * from {dcc_val_table.id}")
    delete_out = syn.delete(results)

    table_out = syn.store(Table(dcc_val_table.id, syn_table_df))


def main():

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json_schema_file", type=argparse.FileType("r"),
                               help="Full pathname for the JSON schema file")

    parser = argparse.ArgumentParser(parents=[parent_parser], add_help=True)

    subparsers = parser.add_subparsers()

    parser_new_table = subparsers.add_parser("new_table", help="New table help")
    parser_new_table.add_argument("--parent_synapse_id", type=str,
                                  help="Synapse ID of the parent project")
    parser_new_table.add_argument("--synapse_table_name", type=str,
                                  help="Name of the Synapse table")
    parser_new_table.set_defaults(func=process_new_table)

    parser_overwrite_table = subparsers.add_parser("overwrite_table", help="Overwrite table help")
    parser_overwrite_table.add_argument("--table_synapse_id", type=str,
                                        help="Synapse ID of the table to be overwritten")
    parser_overwrite_table.set_defaults(func=process_overwrite_table)

    args = parser.parse_args()

    dccv_syn = synapseclient.Synapse()
    dccv_syn.login(silent=True)

    args.func(args, dccv_syn)


if __name__ == "__main__":
    main()
