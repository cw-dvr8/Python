#!/usr/bin/env python3

"""
Program: brainvar_rnaseq_files.py

Purpose: Use an assay metadata file from Sirisha Pochareddy at Yale to move
         RNAseq files from the Yale-ASD study folder to the BrainVar study
         folder on Synapse based on specimen ID.

"""

import pandas as pd
import synapseclient
import synapseutils

ASSAY_METADATA_FILE = "/home/cmolitor/temp/BrainVar_assay_rnaSeq.csv"
CURRENT_BAM_SYNID = "syn7067068"
CURRENT_FASTQ_SYNID = "syn11227080"
NEW_BAM_SYNID = "syn21899400"
NEW_FASTQ_SYNID = "syn21899401"
NEW_STUDY = "BrainVar"
NEW_GRANT = "U01MH116488"
NEW_PI = "Nenad Sestan"

def move_files(orig_folder_synid, dest_folder_synid):

    # Get the full list of files from the original Synapse folder.
    syn_contents = synapseutils.walk(syn, orig_folder_synid)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:
            file_annot_dict = syn.getAnnotations(syn_id)

            # getAnnotations returns the annotations as a dictionary of lists,
            # but specimenID needs to be a string, so convert it.
            if "specimenID" in file_annot_dict:
                character_id_var = ""
                file_annot_dict["specimenID"] = character_id_var.join(file_annot_dict["specimenID"])

                if file_annot_dict["specimenID"] in move_specid_list:
                    # Copy the file to the destination.
                    syn.move(syn_id, dest_folder_synid)

                    # Update the annotations.
                    file_annot_dict["study"] = [NEW_STUDY]
                    file_annot_dict["PI"] = [NEW_PI]
                    file_annot_dict["grant"] = [NEW_GRANT]
                    syn_file = syn.get(syn_id, downloadFile=False)
                    syn_file.annotations = file_annot_dict
                    syn_file = syn.store(syn_file, forceVersion=False)


syn = synapseclient.Synapse()
syn.login(silent=True)

# Read the assay metadata file from Sirisha to get the specimen IDs.
assay_metadata_df = pd.DataFrame(pd.read_csv(ASSAY_METADATA_FILE), columns=["specimenID"])

move_specid_list = assay_metadata_df["specimenID"].tolist()

# Move the bam files from the current Synapse folder to the new one.
move_files(CURRENT_BAM_SYNID, NEW_BAM_SYNID)

# Move the fastq files from the current Synapse folder to the new one.
move_files(CURRENT_FASTQ_SYNID, NEW_FASTQ_SYNID)
