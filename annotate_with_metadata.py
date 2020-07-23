#!/usr/bin/env python3

"""
Program: annotate_with_metadata.py

Purpose: Merge individual, biospecimen, and assay metadata files together and
         use them to annotate data files.

Input parameters:
    individual_synapse_id - Synapse ID for the individual metadata file
    biospecimen_synapse_id - Synapse ID for the biospecimen metadata file
    assay_synapse_id - Synapse ID for the assay metadata file
    parent_synapse_id - Parent Synapse ID containing the files to be annotated

Outputs: File annotations on Synapse

Execution: annotate_with_metadata.py <individual metadata file Synapse ID>
               <biospecimen metadata file Synapse ID>
               <assay metadata file Synapse ID> <Synapse parent ID>

"""

import argparse
import json
import urllib.request
import pandas as pd
import synapseclient
import synapseutils

# Only some of the individual metadata keys will be used for annotating files.
# INDIVIDUAL_KEYS = ["individualID", "individualIdSource", "primaryDiagnosis", "reportedGender"]
INDIVIDUAL_KEYS = ["individualID"]

PEC_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/sysbioDCCjsonschemas/master/PsychENCODE/psychENCODE_schema.json"

def main():

    parser = argparse.ArgumentParser()
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

    # Read in the PsychENCODE JSON schema in order to use it to look for
    # non-Sage keys added by the contributor.
    with urllib.request.urlopen(PEC_SCHEMA_URL) as pec_json_url:
        pec_schema = json.loads(pec_json_url.read().decode())

    pec_schema_keys = pec_schema["properties"].keys()

    # Download the metadata files from Synapse and read their contents into
    # dataframes.
    individual_df = pd.read_csv(open(syn.get(args.individual_synapse_id).path))
    individual_df = individual_df[INDIVIDUAL_KEYS]

    biospecimen_df = pd.read_csv(open(syn.get(args.biospecimen_synapse_id).path))

    assay_df = pd.read_csv(open(syn.get(args.assay_synapse_id).path))

    # The individual and biospecimen files both contain the individual ID.
    # The biospecimen and assay files both contain a specimen ID.
    ind_biosamp_df = pd.merge(individual_df, biospecimen_df, how="inner",
                              on="individualID")

    pec_annot_df = pd.merge(ind_biosamp_df, assay_df, how="inner",
                            on="specimenID")

    # Convert NaN to a blank string.
    pec_annot_df.fillna("", inplace=True)

    # Get rid of any extraneous columns that were added by the site.
    bad_keys = set(pec_annot_df.keys()).difference(pec_schema_keys)
    for key in bad_keys:
        pec_annot_df.drop(key, axis=1, inplace=True)

    # Get the list of files to be annotated from the Synapse parent ID.
    syn_contents = synapseutils.walk(syn, args.parent_synapse_id)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:
            syn_dict = {}
            syn_dict["syn_id"] = syn_id
            syn_dict.update(syn.getAnnotations(syn_id))

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

                syn_file_df = syn_file_df.append(syn_dict, ignore_index=True)

    # Replace NaN values with missing.
    syn_file_df.fillna("", inplace=True)

    # Merge the synapse files (with the current annotations) with the new
    # annotations from the metadata files.
    annotation_df = pd.merge(pec_annot_df, syn_file_df, how="inner",
                             on=["individualID", "specimenID", "assay"])

    # Create a list of the annotations dictionaries, and then use it to
    # create a dictionary with the Synapse id as a key.
    annot_dict_list = annotation_df.to_dict(orient="records")

    for annot_rec in annot_dict_list:
        annotation_dict[annot_rec["syn_id"]] = annot_rec
        del annotation_dict[annot_rec["syn_id"]]["syn_id"]

    # Use the dictionary to annotate the files.
    for synkey in annotation_dict:
        syn_file = syn.get(synkey, downloadFile=False)
        syn_file.annotations = annotation_dict[synkey]
        syn_file = syn.store(syn_file, forceVersion=False)


if __name__ == "__main__":
    main()
