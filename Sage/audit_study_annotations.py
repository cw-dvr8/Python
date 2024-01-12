#!/usr/bin/env python3

"""
Program: audit_study_annotations.py

Purpose: Audit the annotations of a specified assay for a specified study.

Input parameters: SynID for the fileview
                  Name (including organization) of the validation schema
                  Study name
                  Assay name
                  Output filename

Outputs: Output csv file

Execution: audit_study_annotations.py <fileview SynID> <validation schema>
               <study name> <assay name> <output file>

"""

import argparse
import jsonschema
import pandas as pd
import synapseclient
import schema_tools

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("fileview_synid", type=str,
                        help="Synapse ID of the fileview")
    parser.add_argument("val_schema", type=str,
                        help="Name (including organization) of the validation schema")
    parser.add_argument("study_name", type=str,
                        help="Name of the study to be audited")
    parser.add_argument("assay_name", type=str,
                        help="Name of the assay to be audited")
    parser.add_argument("output_file", type=str,
                        help="Output csv file base name")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    row_error = ""
    error_dict = {}
    val_error_df = pd.DataFrame()

    # Get the JSON validation schema, dereference it, and create a validator.
    deref_schema = syn._waitForAsync("/schema/type/validation/async", {"$id": args.val_schema})

    schema_validator = jsonschema.Draft7Validator(deref_schema["validationSchema"])

    # Query the fileview. Get everything and then subset further down because
    # it can be problematic to do the study/assay query from the fileview.
    query_stmt = f'SELECT * FROM {args.fileview_synid}'
    query_nan_df = syn.tableQuery(query_stmt).asDataFrame()

    # Pandas reads in empty fields as nan. Replace nan with None.
    query_df = query_nan_df.where(query_nan_df.notnull(), None).copy()

    # Get the specific study/assay combination query.
    study_assay_df = query_df.loc[(query_df["study"].notnull()) &
                                  (query_df["study"].str.contains(f'"{args.study_name}"')) &
                                  (query_df["assay"].notnull()) &
                                  (query_df["assay"] == f'{args.assay_name}')].copy()

    # Synapse returns values from type StringList as strings that include 
    # double quotes and brackets, so strip those characters out.

    data_dict_list = study_assay_df.to_dict(orient="records")

    for data_record in data_dict_list:

        # Remove any None values from the dictionary - it simplifies the
        # coding of the JSON validation schema.
        clean_record = {k: data_record[k] for k in data_record if data_record[k] is not None}

        # Synapse returns values from type StringList as strings that include 
        # double quotes and brackets, so strip those characters out.
        for key in clean_record:
            if isinstance(clean_record[key], str):
                clean_record[key] = clean_record[key].strip('["]')

        schema_errors = schema_validator.iter_errors(clean_record)

        row_error = schema_tools.validation_errors(schema_errors)

        if row_error:
            error_dict["SynID"] = clean_record["id"]
            error_dict["parentId"] = clean_record["parentId"]
            error_dict["returned_error"] = row_error
            val_error_df = val_error_df.append(error_dict, ignore_index=True)

    # The validator returns a single string for all of the errors found for
    # each record, so turn the string into a list and then explode it.
    val_error_df["errormsg"] = val_error_df["returned_error"].str.split("\n")
    val_error_df = val_error_df.explode("errormsg")

    # Because of the way that pandas reads information into dataframes, the
    # validators will throw errors if a column contains all numbers but is
    # defined as a string in the validation schema. Since they are defined as
    # strings in the schema because the column is allowed to potentiall hold
    # string values, delete string type errors.
    val_final_error_df = val_error_df.loc[(val_error_df["errormsg"].notnull()) &
                                          (~val_error_df["errormsg"].str.contains("is not of type 'string'", na=False))]

    # Write out the list of unique errors.
    output_file_name = f"{args.output_file}_unique_errors.csv"
    error_file = open(output_file_name, "w")
    unique_errors = val_final_error_df.groupby("errormsg")["errormsg"].count()
    unique_errors.to_csv(error_file)
    error_file.close()

    # Write out the list of unique errors by Synapse parent ID.
    output_file_name = f"{args.output_file}_SynParent_errors.csv"
    error_file = open(output_file_name, "w")
    syn_parent_errors = val_final_error_df.groupby(["parentId", "errormsg"])["errormsg"].count()
    syn_parent_errors.to_csv(error_file)
    error_file.close()


if __name__ == "__main__":
    main()
