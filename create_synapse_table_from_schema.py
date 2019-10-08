#!/usr/bin/env python3

"""
Program: create_dccvalidator_table_from_schema.py

Purpose: Use a JSON validation schema to generate a Synapse table to be
         used by the dccvalidator.

Input parameters: Full pathname to the JSON validation schema
                  ID of the Synapse parent project
                  Optional full pathname to the location of any definition
                      references.

Outputs: Synapse table

Execution: create_dccvalidator_table_from_schema.py <JSON schema>
               <parent project Synapse ID>

"""

import argparse
import json
import jsonref
import os
import pandas as pd
import synapseclient
from synapseclient import Column, Schema, Table
from urllib.parse import urldefrag

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("synapse_id", type=str,
                        help="Synapse ID of the parent project")

    args = parser.parse_args()

    ref_path_list = []
    ref_module_dict = {}

    table_df = pd.DataFrame()

    dccv_syn = synapseclient.Synapse()
    dccv_syn.login(silent=True)

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

    # Load the JSON schema. I am not de-referencing the schema at this point so that
    # a) I can get the reference paths in the event that the $ref statements
    # point to more than one location, and b) so that I can get the annotation module
    # name from the $ref in the original # schema. Also, start the schema at the
    # "properties" key to simplify the data # structure.
    json_schema = json.load(args.json_schema_file)["properties"]

    # Create a list of reference paths, and also a dictionary of annotation modules.
    for schema_key in json_schema:
        if "$ref" in json_schema[schema_key]:
            ref_doc, ref_frag = urldefrag(json_schema[schema_key]["$ref"])
            ref_path, ref_file = os.path.split(ref_doc)
            if ref_path not in ref_path_list:
                ref_path_list.append(ref_path)

            ref_module_dict[schema_key] = os.path.splitext(ref_file)[0]

    # If there are any $ref statements, cycle through the schema and de-reference
    # them. If there are not, start with the original schema.
    json_schema_deref = json_schema
    if len(ref_path_list) > 0:
        for ref_path in ref_path_list:
            json_schema_deref = jsonref.JsonRef.replace_refs(json_schema_deref, ref_path)


    # Build a Pandas dataframe out of the schema.
    for json_key in json_schema_deref:
        output_row = {}

        # Assemble the output row.
        output_row["key"] = json_key

        if json_key in ref_module_dict:
            output_row["module"] = ref_module_dict[json_key]

        if len(json_schema_deref[json_key].keys()) > 0:
            if "description" in json_schema_deref[json_key]:
                output_row["description"] = json_schema_deref[json_key]["description"]

            if "type" in json_schema_deref[json_key]:
                output_row["columnType"] = json_schema_deref[json_key]["type"]

            if "anyOf" in json_schema_deref[json_key]:
                for anyof_row in json_schema_deref[json_key]["anyOf"]:
                    if "const" in anyof_row:
                        output_row["value"] = anyof_row["const"]

                    if "description" in anyof_row:
                        output_row["valueDescription"] = anyof_row["description"]

                    if "source" in anyof_row:
                        output_row["source"] = anyof_row["source"]

                    table_df = table_df.append(output_row, ignore_index=True)
            else:
                table_df = table_df.append(output_row, ignore_index=True)
        else:
            table_df = table_df.append(output_row, ignore_index=True)

    # Build and populate the Synapse table.
    table_schema = Schema(name="dcc_PsychENCODE", columns=dcc_column_names, parent=args.synapse_id)
    dcc_table = dccv_syn.store(Table(table_schema, table_df))


if __name__ == "__main__":
    main()
