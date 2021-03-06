#!/usr/bin/env python3

"""
Program: annotate_with_metadata.py

Purpose: Merge individual, biospecimen, and assay metadata files together and
         use them to annotate data files.

Input parameters:
    annotations_table_synapse_id - Synapse ID for the annotations table
    individual_synapse_id - Synapse ID for the individual metadata file
    biospecimen_synapse_id - Synapse ID for the biospecimen metadata file
    assay_synapse_id - Synapse ID for the assay metadata file
    parent_synapse_id - Parent Synapse ID containing the files to be annotated

Outputs: File annotations on Synapse

Execution: annotate_with_metadata.py <annotations table Synapse ID>
               <individual metadata file Synapse ID>
               <biospecimen metadata file Synapse ID>
               <assay metadata file Synapse ID> <Synapse parent ID>

Notes: This program does not currently work with multi-individual or
       multi-specimen files.

"""

import argparse
import json
import pandas as pd
import synapseclient
import synapseutils

# Only some of the individual metadata keys will be used for annotating files.
INDIVIDUAL_KEYS = ["individualID", "species"]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("annotations_table_synapse_id", type=str,
                        help="Synapse ID for the consortium annotations table")
    parser.add_argument("individual_synapse_id", type=str,
                        help="Synapse ID for the individual metadata file")
    parser.add_argument("biospecimen_synapse_id", type=str,
                        help="Synapse ID for the biospecimen metadata file")
    parser.add_argument("assay_synapse_id", type=str,
                        help="Synapse ID for the assay metadata file")
    parser.add_argument("parent_synapse_id", type=str,
                        help="Parent Synapse ID containing the files to be annotated")

    args = parser.parse_args()

    syn_file_df = pd.DataFrame()
    annot_dict_list = []
    annotation_dict = {}

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Create a query statement for the consortium annotations table in order
    # to get the list of valid annotations.
    query_stmt = f'SELECT key FROM {args.annotations_table_synapse_id}'
    valid_keys_df = syn.tableQuery(query_stmt).asDataFrame()
    valid_keys_df.drop_duplicates(keep="first", inplace=True)
    valid_keys_list = valid_keys_df["key"].tolist()

    # Download the metadata files from Synapse and read their contents into
    # dataframes. If all of the individual IDs are numeric, they will be
    # read in as numbers so make sure they are character.
    individual_df = pd.read_csv(open(syn.get(args.individual_synapse_id).path))
    individual_df = individual_df[INDIVIDUAL_KEYS]
    individual_df["individualID"] = individual_df["individualID"].astype(str)

    biospecimen_df = pd.read_csv(open(syn.get(args.biospecimen_synapse_id).path))
    biospecimen_df["individualID"] = biospecimen_df["individualID"].astype(str)

    assay_df = pd.read_csv(open(syn.get(args.assay_synapse_id).path))

    # The individual and biospecimen files both contain the individual ID.
    # The biospecimen and assay files both contain a specimen ID.
    ind_biosamp_df = pd.merge(individual_df, biospecimen_df, how="inner",
                              on="individualID")

    all_annot_df = pd.merge(ind_biosamp_df, assay_df, how="inner",
                            on="specimenID")

    # Convert NaN to None.
    all_annot_df = all_annot_df.where(pd.notnull(all_annot_df), None)

    # Get rid of any extraneous columns that were added by the site.
    bad_keys = set(all_annot_df.keys()).difference(valid_keys_list)
    for key in bad_keys:
        all_annot_df.drop(key, axis=1, inplace=True)

    # Get the list of files to be annotated from the Synapse parent ID.
    syn_contents = synapseutils.walk(syn, args.parent_synapse_id)
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

                # If all of the individual IDs are numeric, Synapse will read
                # them as floats.
                if "individualID" in syn_dict:
                    individualID = ""
                    for indID in syn_dict["individualID"]:
                        if isinstance(indID, float):
                            individualID += str(int(indID))
                        else:
                            individualID += indID
                    syn_dict["individualID"] = individualID
                if "specimenID" in syn_dict:
                    syn_dict["specimenID"] = character_id_var.join(syn_dict["specimenID"])
                if "assay" in syn_dict:
                    syn_dict["assay"] = character_id_var.join(syn_dict["assay"])

                syn_file_df = syn_file_df.append(syn_dict, ignore_index=True)

    # Replace NaN values with None.
    syn_file_df = syn_file_df.where(pd.notnull(syn_file_df), None)

    # libraryID has been added to the file manifest, but use the one in the
    # assay metadata instead.
    if "libraryID" in syn_file_df.columns:
        syn_file_df.drop(["libraryID"], axis=1, inplace=True)

    # Merge the synapse files (with the current annotations) with the new
    # annotations from the metadata files.
    annotation_df = pd.merge(all_annot_df, syn_file_df, how="inner",
                             on=["individualID", "specimenID", "assay"])

    # Create a list of the annotations dictionaries, and then use it to
    # create a dictionary with the Synapse id as a key.
    annot_dict_list = annotation_df.to_dict(orient="records")

    # Get rid of any annotations where the key is empty.
    clean_annot_dict_list = []
    for annotation in annot_dict_list:
        for annotkey in annotation:
            # Synapse returns empty lists, so set any keys with empty lists to
            # None.
            if isinstance(annotation[annotkey], list):
                if (len(annotation[annotkey]) == 1) & ("" in annotation[annotkey]):
                    annotation[annotkey] = None
        annotation = {k: v for k, v in annotation.items() if v is not None}
        clean_annot_dict_list.append(annotation)

    for annot_rec in clean_annot_dict_list:
        annotation_dict[annot_rec["syn_id"]] = annot_rec
        del annotation_dict[annot_rec["syn_id"]]["syn_id"]

    # Use the dictionary to annotate the files.
    for synkey in annotation_dict:
        syn_file = syn.get(synkey, downloadFile=False)
        syn_file.annotations = annotation_dict[synkey]
        syn_file = syn.store(syn_file, forceVersion=False)


if __name__ == "__main__":
    main()
