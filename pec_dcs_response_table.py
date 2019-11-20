#!/usr/bin/env python3

"""
Program: PEC_DCS_response_table.py

Purpose: Uses a downloaded tab-delimited text file of the PsychENCODE Data
         Contribution Survey
         (https://docs.google.com/spreadsheets/d/15ls8XVkLkKfb4PYooY17ZHGE7CtMDR-FWF5_u59QtFY/edit#gid=591716104)
         to create a table in Synapse.

         A tab delimited text file is necessary to prevent problems with text
         fields that contain commas.

Input parameters:
    dcs_file - Full pathname to the DCS text file
    synapse_id - Synapse ID for the table to write to

Outputs: Synapse DCS Response table

Execution: PEC_DCS_response_table.py <text file> <Synapse ID>

"""

import argparse
import pandas as pd
import synapseclient
from synapseclient import Table

def main():

    common_keys = ["rec_index", "Grant", "Contact PI", "Institution",
                   "Data Liaison", "Data Liaison Email", "Protein Targets"]
    assay_keys = ["rec_index", "Timepoint", "Species", "Individual ID Source",
                  "Life Stage", "Primary Diagnosis", "GWAS", "wholeGenomeSeq",
                  "rnaSeq", "ISOSeq", "ChIPSeq", "HiChIP", "STARRSeq",
                  "ATACSeq", "HiC", "CaptureC", "WGBS", "NOMeSeq", "Ribo-Seq",
                  "proteomics", "Assay Other", "Assay Other Describe",
                  "Specimen Other Describe", "Brain Regions",
                  "Sorted Cell Types", "Number Unique Donors",
                  "Number Specimens", "Protein Targets"]

    parser = argparse.ArgumentParser()
    parser.add_argument("dcs_file", type=argparse.FileType("r"),
                        help="Data Contribution Survey csv file")
    parser.add_argument("synapse_id", type=str,
                        help="Synapse Table ID")

    args = parser.parse_args()

    common_keys_list = []
    assay_t1_list = []
    assay_t2_list = []
    syn_table_df = pd.DataFrame()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Need to read in the file line by line so that we can parse the header,
    # as the number of assays may change. Excel surrounds text fields that
    # contain commas in double quotes, so get rid of them if necessary.
    for line_idx, dcs_line in enumerate(args.dcs_file):
        dcs_line = dcs_line.replace('"', '')
        record_list = dcs_line.split("\t")

        if line_idx == 0:
            # The 7th column contains the first timepoint and the 33rd column
            # contains the second timepoint.
            timepoint_1 = record_list[6]
            timepoint_2 = record_list[32]

        else:
            common_dict = {}
            common_dict["rec_index"] = line_idx
            common_dict["Protein Targets"] = record_list[58]
            for i in range(1, 6):
                common_dict[common_keys[i]] = record_list[i]

            common_keys_list.append(common_dict)

            assay_dict = {}
            assay_dict["rec_index"] = line_idx
            assay_dict["Timepoint"] = timepoint_1 + " - " + record_list[6]
            for i in range(7, 32):
                assay_dict[assay_keys[i - 5]] = record_list[i]

            assay_t1_list.append(assay_dict)

            assay_dict = {}
            assay_dict["rec_index"] = line_idx
            assay_dict["Timepoint"] = timepoint_2 + " - " + record_list[32]
            for i in range(33, 58):
                assay_dict[assay_keys[i - 31]] = record_list[i]

            assay_t2_list.append(assay_dict)

    common_keys_df = pd.DataFrame(common_keys_list)
    assay_df = pd.DataFrame(assay_t1_list).append(assay_t2_list, ignore_index=True)

    # Merge the common keys with the assay data.
    syn_table_df = pd.merge(assay_df, common_keys_df, on="rec_index")
    syn_table_df = syn_table_df.drop("rec_index", axis=1)

    # Write out to the Synapse table.
    pec_dcs_table = syn.get(args.synapse_id)
    _ = syn.store(Table(pec_dcs_table.id, syn_table_df))


if __name__ == "__main__":
    main()
