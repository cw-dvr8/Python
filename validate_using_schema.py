#!/usr/bin/env python3

"""
Program: validate_using_schema.py

Purpose: Validate an object using a JSON Draft 7 schema. If the object to
         be validated is a manifest file, it is assumed to be a csv file.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the object to be validated
                  Optional flag to indicate that the object is a
                      manifest file.

Outputs: Terminal output

Execution: validate_using_schema.py <JSON schema> <object to be validated>
               --manifest_file

"""

import argparse
import json
import jsonschema
import pandas as pd
import schema_tools

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("validation_obj_file", type=argparse.FileType("r"),
                        help="Full pathname for the object to be validated")

    args = parser.parse_args()

    row_error = ""
    validation_errors = ""
    data_dict_list = []

    # Load the JSON schema and create a validator..
    _, json_schema = schema_tools.load_and_deref(args.json_schema_file)
    schema_validator = jsonschema.Draft7Validator(json_schema)

    # Attempt to read the file to be validated as a JSON file.
    try:
        data_dict_list.append(json.load(args.validation_obj_file))

        # The first record in a JSON file will be 1. Note that records in a
        # JSON file can span multiple lines.
        first_record = 1

    except json.JSONDecodeError:
        # If the attempt to read the file as JSON fails, attemp to read it as
        # a csv. json.load apparently positions the file position to the end
        # of the file so it is necessary to reset the file position to the
        # beginning in order to attempt to read it as a csv.
        args.validation_obj_file.seek(0)
        data_file_df = pd.read_csv(args.validation_obj_file)

        # Pandas reads in empty fields as nan. Replace nan with None.
        data_file_df = data_file_df.replace({pd.np.nan: None})

        data_dict_list = data_file_df.to_dict(orient="records")

        # The first line of a manifest file (csv) that contains actual data
        # will be row 2 (header is line 1). Records in csv files will not span
        # multiple lines.
        first_record = 2

    for line_number, data_record in enumerate(data_dict_list):

        # Remove any None values from the dictionary - it simplifies the
        # coding of the JSON validation schema.
        clean_record = {k: data_record[k] for k in data_record if data_record[k] is not None}

        # We are not currently allowing multiple types in reference
        # definitions, so convert Booleans to strings if the key is also
        # allowed to contain string values.
        converted_clean_record = schema_tools.convert_from_other(clean_record,
                                           json_schema,
                                           schema_tools.convert_bool_to_string)

        schema_errors = schema_validator.iter_errors(converted_clean_record)

        record_number = "Record " + str(first_record + line_number) + ": "
        row_error = schema_tools.validation_errors(schema_errors,
                                                   line_prepend=record_number)

        if row_error:
            validation_errors += row_error

    print(validation_errors)


if __name__ == "__main__":
    main()
