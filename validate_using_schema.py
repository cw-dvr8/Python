#!/usr/bin/env python3

"""
Program: validate_using_schema.py

Purpose: Validate an object using a JSON schema.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the object to be validated
                  Optional full pathname to the location of any definition
                      references.
                  Optional flag to indicate whether the object is a
                      manifest file.

Outputs: Terminal output

Execution: validate_using_schema.py <JSON schema> <object to be validated>
               --reference_path <definition reference path> --manifest_file

Notes: if the object to be validated is a manifest file, it is assumed to
       be a csv file.

"""

import argparse
import json
import jsonref
import jsonschema
from jsonschema import validate
import os
import pandas as pd

def validate_object(json_val_schema, reference_uri, object_to_validate):
    
    schema_validator = jsonschema.Draft7Validator(json_val_schema)

    schema_errors = schema_validator.iter_errors(object_to_validate)
    for error in schema_errors:

        # If a field in a .csv file is missing, the error is probably not easily
        # understood by non-programmers, so translate it into something more
        # clear.
        if "None is not of type" in error.message:
            error.message = "Column value cannot be missing"

        print(f"{error.relative_schema_path[1]}: {error.message}")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("validation_obj_file", type=argparse.FileType("r"),
                        help="Full pathname for the object to be validated")
    parser.add_argument("--reference_path", type=str,
                        help="Full pathname location for references")
    parser.add_argument("--manifest_file", action="store_true",
                        help="Is the object to be validated a manifest file?")

    args = parser.parse_args()

    # Check to see if a reference path has been passed in. If it has, use jsonref to load
    # the validation schema.  If not, use the json module.
    if args.reference_path is not None:
        if not (os.path.isdir(args.reference_path)):
            raise Exception(f"Reference directory: {args.reference_path} is not a valid directory")

        ref_uri = f"file://{args.reference_path}/"
        json_schema = jsonref.load(args.json_schema_file, base_uri=ref_uri, jsonschema=True)

    else:
        json_schema = json.load(args.json_schema_file)

    # If the object to be validated is a manifest file, read it into a pandas
    # dataframe.  Otherwise, read it into JSON.
    if args.manifest_file:
        data_file_df = pd.read_csv(args.validation_obj_file)

        # Pandas reads in empty fields as nan. Replace nan with None.
        data_file_df = data_file_df.replace({pd.np.nan: None})

        # Convert the dataframe to a list of dictionaries and loop through it.
        data_file_dict = data_file_df.to_dict(orient="records")
        for data_file_record in data_file_dict:
            validate_object(json_schema, ref_uri, data_file_record)
    
    else:
        val_json_obj = json.load(args.validation_obj_file)
        validate_object(json_schema, ref_uri, val_json_obj)

if __name__ == "__main__":
    main()
