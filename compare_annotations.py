#!/usr/bin/env python3

"""
Program: compare_annotations.py

Purpose: Compare the individualID and specimenID annotations on files in two
         different Synapse folders.

Input parameters:
    folder1 - Synapse ID for folder containing the first set of files
    folder2 - Synapse ID for folder containing the second set of files
    output_file - Results output file

Outputs: File containing the differences between the two sets of files.

Execution: compare_annotations.py <folder 1 SynID> <folder 2 SynID>
               <output file name>

Notes: This program assumes that the files do not have multiple annotations
       in the individualID or specimenID keys.

"""

import argparse
import pandas as pd
import synapseclient
import synapseutils

syn = synapseclient.Synapse()
syn.login(silent=True)

def get_annotations(folder_synid, result_file):

    syn_files_df = pd.DataFrame()

    # Get the list of files and their annotations from the specified Synapse ID.
    syn_contents = synapseutils.walk(syn, folder_synid)
    for __, __, filelist in syn_contents:
        for filename, syn_id in filelist:
            syn_dict = {}
            syn_dict["filename"] = filename
            syn_dict.update(syn.getAnnotations(syn_id))

            if ("individualID" in syn_dict) and ("specimenID" in syn_dict):
                syn_files_df = syn_files_df.append(syn_dict, ignore_index=True)
            else:
                result_file.write(f"individualID and/or specimenID annotations are missing from {filename}\n")

    if len(syn_files_df) > 0:
        # Replace NaN values with missing.
        syn_files_df.fillna("", inplace=True)

        syn_files_df["individualID"] = [",".join(map(str, idval)) for idval in syn_files_df["individualID"]]
        syn_files_df["specimenID"] = [",".join(map(str, idval)) for idval in syn_files_df["specimenID"]]

        syn_files_df = syn_files_df[["filename", "individualID", "specimenID"]]

    return(syn_files_df)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("folder1", type=str,
                        help="SynID for the folder containing the first set of files")
    parser.add_argument("folder2", type=str,
                        help="SynID for the folder containing the second set of files")
    parser.add_argument("output_file", type=argparse.FileType("w"),
                        help="Name of the results output file")

    args = parser.parse_args()

    folder1_files_df = get_annotations(args.folder1, args.output_file)
    folder1_files_df = folder1_files_df.rename(columns={"filename": "f1_filename"})

    folder2_files_df = get_annotations(args.folder2, args.output_file)
    folder2_files_df = folder2_files_df.rename(columns={"filename": "f2_filename"})

    if (len(folder1_files_df) > 0) and (len(folder2_files_df) > 0):
        all_files_df = pd.merge(folder1_files_df, folder2_files_df, how="outer",
                                on=["individualID", "specimenID"], indicator=True)

        missing_f2_df = all_files_df.loc[all_files_df["_merge"] == "left_only"].copy()
        missing_f2_df = missing_f2_df[["individualID", "specimenID", "f1_filename"]]
 
        if len(missing_f2_df) > 0:
            args.output_file.write(f"\n\nindividualID/specimenID combos in {args.folder1} not present in {args.folder2}:\n")
            missing_f2_df.to_csv(args.output_file, index=False)

        missing_f1_df = all_files_df.loc[all_files_df["_merge"] == "right_only"].copy()
        missing_f1_df = missing_f1_df[["individualID", "specimenID", "f2_filename"]]

        if len(missing_f1_df) > 0:
            args.output_file.write(f"\n\nindividualID/specimenID combos in {args.folder2} not present in {args.folder1}:\n")
            missing_f1_df.to_csv(args.output_file, index=False)

    args.output_file.close()


if __name__ == "__main__":
    main()
