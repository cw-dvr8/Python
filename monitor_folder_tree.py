#!/usr/bin/env python3

"""
Program: monitor_folder_tree.py

Purpose: Traverse a Synapse folder and determine if any changes have been made
         to the contents.

Input parameters: Root folder Synapse ID
                  SynID of the table to write the results to

Outputs: Synapse table

Execution: synapse_folder_sizes.py <root folder Synapse ID>
               <Synapse table ID>

"""

import argparse
import datetime
import dateutil.parser
import pytz
import pandas as pd
import synapseclient
from synapseclient import Table
import synapseutils

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("folder_syn_id", type=str,
                        help="Root folder Synapse ID")
    parser.add_argument("table_syn_id", type=str,
                        help="Synapse ID of the table to write the results to")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    current_unaware_dt = datetime.datetime.today()
    # Have to make the current date timezone-aware so that we can use it in
    # date arithmetic later.
    current_dt = pytz.utc.localize(current_unaware_dt)

    file_tree_df = pd.DataFrame()

    syn_contents = synapseutils.walk(syn, args.folder_syn_id)
    for dirname, __, filelist in syn_contents:
        if len(filelist) > 0:
            for __, syn_id in filelist:
                entity_dict = {}

                try:
                    file_entity = syn.restGET(f"/entity/{syn_id}")
                except:
                    continue

                if ("createdOn" in file_entity) and ("modifiedOn" in file_entity):
                    createdOn_dt = dateutil.parser.parse(file_entity["createdOn"])
                    modifiedOn_dt = dateutil.parser.parse(file_entity["modifiedOn"])
                    if (((current_dt - createdOn_dt).days <= 28) or
                        ((current_dt - modifiedOn_dt).days <= 28)):

                        if (modifiedOn_dt - createdOn_dt).days == 0:
                            entity_dict["Status"] = "New"
                        else:
                            entity_dict["Status"] = "Modified"
                        
                        # If the file is new, the modified date will be the same
                        # as the creation date so just use modified date to
                        # calculate the date range.
                        date_range = current_dt - modifiedOn_dt
                        if date_range.days <= 7:
                            entity_dict["When"] = "Within 7 days"
                        elif date_range.days <= 14:
                            entity_dict["When"] = "Within 14 days"
                        elif date_range.days <= 21:
                            entity_dict["When"] = "Within 21 days"
                        else:
                            entity_dict["When"] = "Within 28 days"

                        entity_dict["SynID"] = syn_id
                        entity_dict["CreatedBy"] = syn.restGET(f"/userProfile/{file_entity['createdBy']}")["userName"]
                        entity_dict["CreationDate"] = file_entity["createdOn"]
                        entity_dict["ModifiedBy"] = syn.restGET(f"/userProfile/{file_entity['modifiedBy']}")["userName"]
                        entity_dict["ModificationDate"] = file_entity["modifiedOn"]

                        file_tree_df = file_tree_df.append(entity_dict, ignore_index=True)

    synapse_table = syn.get(args.table_syn_id)
    results = syn.tableQuery(f"select * from {synapse_table.id}")
    delete_out = syn.delete(results)
    table_out = syn.store(Table(synapse_table.id, file_tree_df))


if __name__ == "__main__":
    main()
