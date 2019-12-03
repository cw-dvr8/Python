#!/usr/bin/env python3

"""
Program: create_synapse_table_from_schema.py

Purpose: Use a JSON validation schema to generate a Synapse table to be
         used by the dccvalidator.

Input parameters: Full pathname to the JSON validation schema
                  new_table OR overwrite_table
                  new_table parameters: Synapse parent project ID, table name
                  overwrite_table parameters: Synapse ID of the table to be overwritten

Outputs: Synapse table

Execution (new table): create_synapse_table_from_schema.py --json_schema_file <JSON schema>
                       new_table --parent_synapse_id <parent project Synapse ID>
                       --synapse_table_name <table name>

Execution (overwrite table): create_synapse_table_from_schema.py --json_schema_file <JSON schema>
                             overwrite_table --table_synapse_id <Synapse table ID>

"""

import argparse
import os
from urllib.parse import urldefrag
import pandas as pd
import synapseclient
from synapseclient import Column, Schema, Table
import schema_tools


def process_schema(json_schema_file):
    """
    Function: process_schema

    Purpose: Load the JSON schema into a dictionary, resolve any remote
             references, and convert into a Pandas dataframe suitable to use
             to create Synapse tables.

    Arguments: JSON schema file reference

    Returns: Pandas dataframe
    """

    ref_module_dict = {}

    ref_location_dict, json_schema = schema_tools.load_and_deref(json_schema_file)

    # Derive the name of the annotations module from the reference location.
    for schema_key in ref_location_dict:
        ref_doc, _ = urldefrag(ref_location_dict[schema_key])
        _, ref_file = os.path.split(ref_doc)
        ref_module_dict[schema_key] = os.path.splitext(ref_file)[0]

    ref_module_df = pd.DataFrame(list(ref_module_dict.items()),
                                 columns=["key", "module"])

    defs_df, values_df = schema_tools.get_definitions_values(json_schema)

    # Combine the definitions with the modules, and then with the possible
    # values.
    defs_mod_df = pd.merge(defs_df, ref_module_df, how="left", on="key")
    table_df = pd.merge(defs_mod_df, values_df, how="left", on="key")

    # Rename JSON "type" to Synapse "columnType" and drop unnecessary columns.
    table_df.rename(columns={"type":"columnType"}, inplace=True)
    table_df.drop("required", axis=1, inplace=True)

    # Change the column type to upper case. Also, Synapse does not have a
    # "number" type, so change any occurances of "number" to "double".
    table_df["columnType"] = table_df["columnType"].str.upper()
    table_df.loc[table_df["columnType"] == "NUMBER", "columnType"] = "DOUBLE"

    return table_df


def process_new_table(args, syn):
    """
    Function: process_new_table

    Purpose: Create an annotations table with the specified name under the
             specified Synapse parent ID using the specified JSON schema. This
             function is called when the "new_table" option is specified when
             the program is called.

    Arguments: JSON schema file reference
               Synapse parent ID
               Synapse table name
               A Synapse client object
    """

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
    table_schema = Schema(name=args.synapse_table_name,
                          columns=dcc_column_names,
                          parent=args.parent_synapse_id)
    dcc_table = syn.store(Table(table_schema, syn_table_df))


def process_overwrite_table(args, syn):
    """
    Function: process_overwrite_table

    Purpose: Overwrite the specified annotations table with data contained in
             the specified JSON schema. This function is called when the
             "overwrite_table" option is specified when the program is called.

    Arguments: JSON schema file reference
               Synapse ID of the table to be overwritten
               A Synapse client object
    """

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
