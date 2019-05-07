"""
Program: bsmn_validation_report.py
Author: Cindy Molitor
Date: 07May2019
Purpose: Run validation checks on BSMN manifest files and report the results.
"""

import synapseclient
import pandas as pd
import json

def main()

    # Create an empty errors dataframe
    manifest_errors = pd.DataFrame()

    # Read in the JSON manifest config file. This file contains the following information:
    # - Synapse ID of the Grand Data Staged Submission Manifests table. This table contains the parent IDs of
    #   the uploaded manifests.
    # - The current acceptable prefixes for the manifest files, e.g. genomics_subject02
    with open('config_files/manifests.json', 'r') as config_file:
        config_data = json.load(config_file)

    # Log onto Synapse - assumes a .synapseConfig file exists in the user home folder
    syn = synapseclient.Synapse()
    syn.login()

    # Get the manifests from Synapse and read the data into dataframes
    # check that all three manifest files exist
    # check that the manifest file names are correct

    # subject data
    check_for_duplicates(subject_df, subjectkey, manifest_errors):
    check_for_duplicates(subject_df, src_subject_id, manifest_errors):
    check_for_duplicates(subject_df, sample_id_orginal, manifest_errors):
    check_for_duplicates(subject_df, sample_id_biorepository, manifest_errors):

    # nichd data
    check_for_duplicates(nichd_df, sample_id_original, manifest_errors):
    # check that subjectkey matches a subjectkey in the subject data
    # check that src_subject_id matches a src_subject_id in the subject data
    #
    # sample data
    # check that site is not NA
    # check that there is only one unique value of site in the file
    # check that site is in the grant???
    # check that subjectkey matches a subjectkey in the subject data
    # check that src_subject_id matches a src_subject_id in the subject data
    # check that sample_id_biorepository matches a sample_id_original in the nichd data

"""
Function: manage_errors
Purpose: Set the error_value column to the value in error and pare down the error dataframe to only contain the
         necessary columns.
Inputs: error_df - the dataframe containing any errors that have been found
        df_column - the column with the erroneous data
Output: Pared down error dataframe
"""

def manage_errors(error_df, df_column):
    error_df['error_value'] = error_df[df_column]
    error_df = error_df[['input_file', 'error_value', 'error_msg']]
    return error_df

"""
Function: check_for_duplicates
Purpose: checks the given manifest dataframe for duplicates in the given column
Inputs: manifest_df - the dataframe containing the manifest data to be checked
        df_column - the column of the dataframe to be checked
        error_df - the dataframe that will contain any errors that are found
Outputs: error dataframe
"""

def check_for_duplicates(manifest_df, df_column, error_df):
    manifest_df['dup_error'] = manifest_df.duplicated([df_column])
    error_rows = manifest_df.loc[manifest_df['dup_error']].copy()
    if not error_rows.empty:
        error_rows['error_msg'] = 'Duplicate ' + df_column + ' in file line ' + error_rows['file_row'].apply(str)
        error_df = error_df.append(manage_errors(error_rows, df_column))

    return error_df


manifest_df = pd.read_csv("testdata/genomics_subject02_test.csv", skiprows=1)

manifest_df['input_file'] = 'genomics_subject02_test.csv'

# The manifest files have two header rows, so add three to the dataframe index to get the file row index.
manifest_df['file_row'] = [x + 3 for x in manifest_df.index_tolist()]

manifest_df['dup_subjectkey'] = manifest_df.duplicated(['subjectkey'], keep=False)

if __name__ == '__main__':
    main()
