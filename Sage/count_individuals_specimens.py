#!/usr/bin/env python3

"""
Program: count_individuals_specimens.py

Purpose: Count the number of individuals and specimens per assay in a Synapse
         folder.

Input parameters:
    folder_synapse_id - Folder Synapse ID containing the files to be counted

Outputs: To terminal

Execution: count_individuals_specimens.py <Synapse folder ID>

"""

import argparse
import sys
import pandas as pd
import synapseclient
import synapseutils

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("folder_synapse_id", type=str,
                        help="Synapse ID of the folder containing the files to be counted")

    args = parser.parse_args()

    syn_file_df = pd.DataFrame()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Get the list of files to be annotated from the Synapse parent ID.
    syn_contents = synapseutils.walk(syn, args.folder_synapse_id)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:
            syn_dict = {}
            syn_dict["syn_id"] = syn_id
            syn_dict.update(syn.get_annotations(syn_id))

            # getAnnotations returns the annotations as lists, but individualID
            # and specimenID need to be strings. If neither are in the
            # current annotations, then do not add the file info to the
            # dataframe.
            if ("individualID" in syn_dict) or ("specimenID" in syn_dict):
                character_id_var = ""
                if "individualID" in syn_dict:
                    syn_dict["individualID"] = character_id_var.join(syn_dict["individualID"])
                if "specimenID" in syn_dict:
                    syn_dict["specimenID"] = character_id_var.join(syn_dict["specimenID"])
                if "assay" in syn_dict:
                    syn_dict["assay"] = character_id_var.join(syn_dict["assay"])
                if "tissue" in syn_dict:
                    syn_dict["tissue"] = character_id_var.join(syn_dict["tissue"])

                syn_file_df = syn_file_df.append(syn_dict, ignore_index=True)

    # Perform counts.
    assay_count = syn_file_df.groupby("assay")["assay"].count()
    assay_count.to_csv(sys.stdout, header=False)

    tissue_count = syn_file_df.groupby("tissue")["tissue"].count()
    tissue_count.to_csv(sys.stdout, header=False)

    individuals_unique = syn_file_df["individualID"].nunique()
    print(f"Number of unique individuals: {individuals_unique}\n")

    biospecimens_unique = syn_file_df["specimenID"].nunique()
    print(f"Number of unique biospecimens: {biospecimens_unique}\n")


if __name__ == "__main__":
    main()
