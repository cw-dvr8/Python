#!/usr/bin/env python3

"""
Program: check_individualIDs.py

Purpose: Check the individualID annotations for files in the specified Synapse
         folder against the individualID column in the specified individual
         metadata file.

Input parameters:
    individual_synapse_id - Synapse ID for the individual metadata file
    parent_synapse_id - Parent Synapse ID containing the files to be checked

Outputs: Report on files with no corresponding individualIDs

Execution: check_individualIDs.py <individual metadata file Synapse ID>
               <Synapse parent ID>

"""

import argparse
import sys
import pandas as pd
import synapseclient
import synapseutils

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("individual_synapse_id", type=str,
                        help="Synapse ID for the individual metadata file")
    parser.add_argument("parent_synapse_id", type=str,
                        help="Parent Synapse ID containing the files to be annotated")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    syn_file_df = pd.DataFrame()

    # Download the metadata file from Synapse and read its contents into a
    # dataframe.
    individual_df = pd.read_csv(open(syn.get(args.individual_synapse_id).path))
    individual_df = individual_df[["individualID"]]

    # Convert NaN to a blank string.
    individual_df.fillna("", inplace=True)

    # Get the list of files to be annotated from the Synapse parent ID.
    syn_contents = synapseutils.walk(syn, args.parent_synapse_id)
    for __, __, filelist in syn_contents:
        for filename, syn_id in filelist:
            syn_dict = {}
            syn_dict["filename"] = filename
            syn_dict.update(syn.getAnnotations(syn_id))

            # getAnnotations returns the annotations as lists, but individualID
            # needs to be a string. If it is not in the current annotations,
            # then do not add the file info to the dataframe.
            if ("individualID" in syn_dict):
                character_id_var = ""
                syn_dict["individualID"] = character_id_var.join(syn_dict["individualID"])

                syn_file_df = syn_file_df.append(syn_dict, ignore_index=True)

    syn_file_df = syn_file_df[["filename", "individualID"]]

    # Replace NaN values with missing.
    syn_file_df.fillna("", inplace=True)

    # Merge the synapse files (with the current annotations) with the
    # individualID from the metadata file.
    id_check_df = pd.merge(individual_df, syn_file_df, how="outer",
                           on=["individualID"], indicator=True)

    no_match_df = id_check_df.loc[id_check_df["_merge"] == "right_only"].copy()
    no_match_df.drop(["_merge"], axis=1, inplace=True)
    no_match_df.to_csv(sys.stdout, index=False)


if __name__ == "__main__":
    main()
