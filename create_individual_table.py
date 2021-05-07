#!/usr/bin/env python3

"""
Program: create_individual_table.py

Purpose: Create a Synapse table containing all of the individuals in a
         consortium. This includes any duplicates for individuals who were
         assayed by multiple members.

Input parameters: Synapse ID of the file view of the metadata files
                  SynID of the table to write the individuals to
                  Full name of the individual metadata schema registered in
                      Synapse - use default columns if not provided.

Outputs: Synapse table

Execution: create_individual_table.py <metadata file view Synapse ID>
               <Synapse individual table ID>
               <Synapse individual review table ID>

"""

import argparse
import pandas as pd
import synapseclient
from synapseclient import Table

DEFAULT_INDIVIDUAL_COLUMNS = ["individualID", "individualIdSource", "species", "reportedGender", "sexChromosome",
                              "race", "ethnicity", "genotypeInferredAncestry", "familialRelationship", "IQ", "BMI",
                              "primaryDiagnosis", "primaryDiagnosisDetail", "otherDiagnosis", "otherDiagnosisDetail",
                              "familyHistory", "ageOnset", "neuropathDescription", "dementia", "CDR", "Braak",
                              "otherMedicalDx", "otherMedicalDetail", "ageDeath", "ageDeathUnits", "causeDeath",
                              "mannerDeath", "postmortemTox", "postmortemToxSource", "medRecordTox", "PMICertain",
                              "PMI", "pH", "sourceSynID"]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_fileview_syn_id", type=str,
                        help="Metadata file view Synapse ID")
    parser.add_argument("individual_table_syn_id", type=str,
                        help="Synapse ID of the table to write the individuals to")
    parser.add_argument("review_table_syn_id", type=str,
                        help="Synapse ID of the review table to write the individuals to")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    individuals_df = pd.DataFrame(columns=DEFAULT_INDIVIDUAL_COLUMNS)

    individuals_df["altIndividualID"] = ""

    # Get the list of individual metadata files.
    query_stmt = f"SELECT * FROM {args.metadata_fileview_syn_id} where metadataType = 'individual'"
    indfile_df = syn.tableQuery(query_stmt).asDataFrame()
    indfile_list = indfile_df["id"].tolist()

    for indfile_id in indfile_list:
        indfile_df = pd.read_csv(open(syn.get(indfile_id, followLink=True).path))
        indfile_df["sourceSynID"] = indfile_id
        individuals_df = individuals_df.append(indfile_df, ignore_index=True, sort=False)

    # Currently, Synapse is having a problem reading Boolean values into
    # Boolean columns in tables, so convert all values into strings. Doing this
    # results in nan values were there are missing values, so replace nan
    # strings with blanks.
    for indcolumn in individuals_df.columns:
        individuals_df[indcolumn] = individuals_df[indcolumn].astype("str")
        individuals_df.loc[individuals_df[indcolumn] == "nan", indcolumn] = ""

    individuals_df = individuals_df[DEFAULT_INDIVIDUAL_COLUMNS]

    # Pull the individuals with duplicate entries out into a separate table for
    # review to determine which record to use.
    inddup_df = individuals_df[individuals_df.duplicated("individualID", keep=False)]

    # Get the records from the review table and merge with the duplicates to
    # weed out any that are already there.
    query_stmt = f'SELECT * FROM {args.review_table_syn_id}'
    review_df = syn.tableQuery(query_stmt).asDataFrame()
    for indcolumn in review_df.columns:
        review_df[indcolumn] = review_df[indcolumn].astype("str")
        review_df.loc[review_df[indcolumn] == "nan", indcolumn] = ""

    if len(review_df) == 0:
        newdups_df = inddup_df.copy()
    else:
        newdups_df = pd.merge(inddup_df, review_df, how="outer",
                              on=DEFAULT_INDIVIDUAL_COLUMNS, indicator=True)
        newdups_df = newdups_df.loc[newdups_df["_merge"] == "left_only"]
        newdups_df.drop(["_merge"], axis=1, inplace=True)

    if len(newdups_df) > 0:
        review_table = syn.get(args.review_table_syn_id)
        table_out = syn.store(Table(review_table.id, newdups_df))

    individuals_df.drop_duplicates(["individualID"], keep=False, inplace=True)

    # Get the rows from the review table that should be in the master clinical
    # table.
    clindups_df = review_df.loc[review_df["mainRecord"] == "True"].copy()
    clindups_df.drop(["mainRecord"], axis=1, inplace=True)
    individuals_df = individuals_df.append(clindups_df, ignore_index=True, sort=False)

    clinical_table = syn.get(args.individual_table_syn_id)
    results = syn.tableQuery(f"select * from {clinical_table.id}")
    delete_out = syn.delete(results)
    table_out = syn.store(Table(clinical_table.id, individuals_df))


if __name__ == "__main__":
    main()
