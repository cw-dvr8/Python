"""
Program: bsmn_validation_report.py
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

    # Get the manifests from Synapse.
    synapse_query = ('select * from ' + config_data['manifest_file_view_id']
                     + ' where parentId="' + args.parentId + '"')
    manifest_files = syn.tableQuery(synapse_query)
    manifest_file_df = manifest_files.asDataFrame()
    manifest_file_df['file_row'] = [x + 1 for x in manifest_file_df.index_tolist()]
    manifest_file_df['input_source'] = 'Grant Data Staged Submission Manifests table'
    manifest_errors = verify_submission_data(manifest_file_df, manifest_errors)



    # check that all three manifest files exist
    # check that the manifest file names are correct

    # subject data
    manifest_errors = check_for_duplicates(subject_df, subjectkey, manifest_errors)
    manifest_errors = check_for_duplicates(subject_df, src_subject_id, manifest_errors)
    manifest_errors = check_for_duplicates(subject_df, sample_id_orginal, manifest_errors)
    manifest_errors = check_for_duplicates(subject_df, sample_id_biorepository, manifest_errors)

    # nichd data
    manifest_errors = check_for_duplicates(nichd_df, sample_id_original, manifest_errors)
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
    error_df = error_df[['input_source', 'error_value', 'error_msg']]

    return error_df

"""
Function: check_for_duplicates
Purpose: Checks the given dataframe for duplicates in the given column
Inputs: file_df - the dataframe containing the manifest data to be checked
        df_column - the column of the dataframe to be checked
        error_df - the dataframe that will contain any errors that are found
Outputs: error dataframe
"""

def check_for_duplicates(file_df, df_column, error_df):
    file_df['dup_error'] = file_df.duplicated([df_column], keep=False)
    error_rows = file_df.loc[file_df['dup_error']].copy()
    if not error_rows.empty:
        error_rows['error_msg'] = 'Duplicate ' + df_column + ' in file line ' + error_rows['file_row'].apply(str)
        error_df = error_df.append(manage_errors(error_rows, df_column))

    return error_df


"""
Function: check_for_missing
Purpose: Checks the given column in the given dataframe for missing values
Inputs: manifest_df - the dataframe containing the manifest data to be checked
        df_column - the column of the dataframe to be checked
        error_df - the dataframe that will contain any errors that are found
Outputs: error dataframe
"""

def check_for_missing(file_df, df_column, error_df):
    file_df['missing_error'] = file_df[df_column].isnull()
    error_rows = file_df.loc[file_df['missing_error']].copy()
    if not error_rows.empty:
        error_rows['error_msg'] = ('Missing value for ' + df_column + ' in file line '
                                   + error_rows['file_row'].apply(str))
        error_df = error_df.append(manage_errors(error_rows, df_column))

    return error_df


"""
Function: check_for_multiple_values
Purpose: Checks that the given column in the given dataframe does not contain multiple values
Inputs: manifest_df - the dataframe containing the manifest data to be checked
        df_column - the column of the dataframe to be checked
        error_df - the dataframe that will contain any errors that are found
Outputs: error dataframe
"""

def check_for_multiple_values(file_df, df_column, error_df):
    unique_values = file_df[df_column].unique()
    if len(unique_values) > 1:
        error_rows = file_df.copy()
        error_rows['error_msg'] = 'The ' + df_column + ' column contains multiple values'
        error_df = error_df.append(manage_errors(error_rows, df_column))

    return error_df


"""
Function: verify_submission_data
Purpose: Makes sure that there is the correct number of files, and verifies some of the metadata
Inputs: file_df - the dataframe holding the file metadata
        error_df - the dataframe that will contain any errors that are found
Outputs: error dataframe
"""

def verify_submission_data(file_df, error_df)

    # Check that the number of files in the submission equals the number of files specified in the config file.
    num_files_expected = len(config_data['file_name_prefixes']
    num_files_received = len(file_df)
    if num_files_expected != num_files_received:
        file_error_rows = file_df.copy()
        file_error_rows['error_msg'] = ('Number of files expected: ' + str(num_files_expected) 
                                        + '   Number of files received: ' + str(num_files_received)
        error_df = error_df.append(manage_errors(error_rows, 'name'))

    # Check that the values of nda_short_name are valid.
    short_name_list = list(config_data['file_name_prefixes'].values())
    error_rows = file_df[~file_df.nda_short_name.isin(short_name_list)]
    if not error_rows.empty:
        error_rows['error_msg'] = ('nda_short_name in submission line ' + error_rows['file_row'].apply(str)
                                   + ' is not valid')
        error_df = error_df.append(manage_errors(error_rows, df_column))
 
    # Check that the individual file types were only uploaded once.
    error_df = check_for_duplicates(file_df, nda_short_name, error_df)

    # Check that there are no missing values in nda_short_name.
    error_df = check_for_missing(file_df, nda_short_name, error_df))

    # Check that there are no missing values in grant.
    error_df = check_for_missing(file_df, grant, error_df))

    # Check that the grant column contains a single value across submission files.
    error_df = check_for_multiple_values(file_df, grant, error_df)

    return error_df


manifest_df = pd.read_csv("testdata/genomics_subject02_test.csv", skiprows=1)

manifest_df['input_source'] = 'genomics_subject02_test.csv'

# The manifest files have two header rows, so add three to the dataframe index to get the file row index.
manifest_df['file_row'] = [x + 3 for x in manifest_df.index_tolist()]


if __name__ == '__main__':
    main()
