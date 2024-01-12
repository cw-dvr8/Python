#!/usr/bin/env python3

"""
Program: BrainVar_file_info.py

Purpose: Walks through the BrainVar fastq file and prints the Synapse file
         name, the name of the file as it was uploaded, and the annotations
         for files where the Synapse file name and the uploaded file name
         do not match.

Background: A user alerted us to the fact that the name of the file on Synapse
            for syn11286037 is PEC_HSB_Yale-UCSF_mRNA_RiboZero_HSB148-R1.fastq.gz,
            but downloads as 148eqtIH_S25_L004_R1_001.fastq.gz. We want this
            information so that Sirisha Pochareddy at Yale can confirm that
            the metadata is still correct for this file and others like it.
"""

import pandas as pd
import synapseclient
import synapseutils

syn = synapseclient.Synapse()
syn.login(silent=True)

BRAINVAR_FASTQ_FOLDER_ID = "syn21905192"

file_list = []
character_var = ""

syn_contents = synapseutils.walk(syn, BRAINVAR_FASTQ_FOLDER_ID)
for __, __, filelist in syn_contents:
    for __, syn_id in filelist:
        bundle_dict = {}
        print(syn_id)
        bundle = syn._getEntityBundle(syn_id)
        bundle_dict["synapse_file_name"] = bundle["entity"]["name"]
        bundle_dict["file_name"] = bundle["fileHandles"][0]["fileName"]

        annotation_dict = {}
        for bkey in bundle["annotations"]["stringAnnotations"].keys():
            annotation_dict[bkey] = character_var.join(bundle["annotations"]["stringAnnotations"][bkey])

        bundle_dict.update(annotation_dict)
        file_list.append(bundle_dict)

file_list_df = pd.DataFrame(file_list)
diff_list_df = file_list_df.loc[file_list_df["synapse_file_name"] != file_list_df["file_name"]]

with open("output/BrainVar_File_Annotations.csv", "w") as output_file:
    diff_list_df.to_csv(output_file, index=False)
