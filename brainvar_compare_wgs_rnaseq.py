#!/usr/bin/env python3

"""
Program: brainvar_compare_wgs_rnaseq.py

Purpose: Compare the individalID annotations from the WGS files to those of
         the RNAseq files to see if there are any missing.

"""

import pandas as pd
import synapseclient
import synapseutils

WGS_SYN_ID = "syn18454751"
RNASEQ_SYN_ID = "syn21905192"

def get_individualIDs(assay_folder_synid):

    assay_df = pd.DataFrame()

    # Get the full list of files from the original Synapse folder.
    syn_contents = synapseutils.walk(syn, assay_folder_synid)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:
            file_annot_dict = syn.getAnnotations(syn_id)

            # getAnnotations returns the annotations as a dictionary of lists,
            # but individualID needs to be a string, so convert it.
            if "individualID" in file_annot_dict:
                character_id_var = ""
                file_annot_dict["individualID"] = character_id_var.join(file_annot_dict["individualID"])

                id_dict = {key: file_annot_dict[key] for key in file_annot_dict.keys()
                                                         & {"individualID"}}

                id_df = pd.DataFrame(id_dict.items(), columns=["key", "individualID"])
                id_df.drop("key", axis=1, inplace=True)

                assay_df = assay_df.append(id_df, ignore_index=True)

    assay_df.drop_duplicates(subset=["individualID"], keep="first", inplace=True)

    return assay_df

syn = synapseclient.Synapse()
syn.login(silent=True)

# Get the IDs for both assays.
wgs_id_df = get_individualIDs(WGS_SYN_ID)
rnaseq_id_df = get_individualIDs(RNASEQ_SYN_ID)

# Merge the two assay ID lists together and check the differences.
all_ids_df = pd.merge(wgs_id_df, rnaseq_id_df, how="outer", on="individualID", indicator=True)

missing_wgs_df = all_ids_df.loc[all_ids_df["_merge"] == "right_only"]
missing_rnaseq_df = all_ids_df.loc[all_ids_df["_merge"] == "left_only"]
