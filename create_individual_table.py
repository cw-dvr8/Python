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
               --individual_schema <individual schema registered in Synapse>

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
                              "PMI", "pH"]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_fileview_syn_id", type=str,
                        help="Metadata file view Synapse ID")
    parser.add_argument("individual_table_syn_id", type=str,
                        help="Synapse ID of the table to write the individuals to")
    parser.add_argument("--individual_schema", type=str,
                        help="Optional - Individual schema registered in Synapse")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    if args.individual_schema is not None:
        ind_schema = syn.restGET(f"/schema/type/registered/{args.individual_schema}")
        ind_columns = ind_schema["properties"].keys()
        individuals_df = pd.DataFrame(columns=ind_columns)
    else:
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

    for indcolumn in individuals_df.columns:
        individuals_df[indcolumn] = individuals_df[indcolumn].astype("str")
        individuals_df.loc[individuals_df[indcolumn] == "nan", indcolumn] = ""

    individuals_df = individuals_df[["individualID", "individualIdSource", "species", "reportedGender",
                                     "sexChromosome", "race", "ethnicity", "genotypeInferredAncestry",
                                     "familialRelationship", "IQ", "BMI", "primaryDiagnosis", 
                                     "primaryDiagnosisDetail", "otherDiagnosis", "otherDiagnosisDetail",
                                     "familyHistory", "ageOnset", "neuropathDescription", "dementia",
                                     "CDR", "Braak", "otherMedicalDx", "otherMedicalDetail", "ageDeath",
                                     "ageDeathUnits", "causeDeath", "mannerDeath", "postmortemTox",
                                     "postmortemToxSource", "medRecordTox", "PMICertain", "PMI", "pH",
                                     "sourceSynID"]]
    synapse_table = syn.get(args.individual_table_syn_id)
    results = syn.tableQuery(f"select * from {synapse_table.id}")
    delete_out = syn.delete(results)
    table_out = syn.store(Table(synapse_table.id, individuals_df))


if __name__ == "__main__":
    main()
