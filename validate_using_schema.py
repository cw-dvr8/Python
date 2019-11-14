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
    first_data_row = None

    # Load the JSON schema and create a validator..
    _, json_schema = schema_tools.load_and_deref(args.json_schema_file)
    schema_validator = jsonschema.Draft7Validator(json_schema)

    # Attempt to read the file to be validated as a JSON file.
    try:
        json_file_dict = json.load(args.validation_obj_file)
        data_dict_list.append(json_file_dict)

    except:
        # If the attempt to read the file as JSON fails, attemp to read it as
        # a csv.
        try:
            args.validation_obj_file.seek(0)
            data_file_df = pd.read_csv(args.validation_obj_file)

            # Pandas reads in empty fields as nan. Replace nan with None.
            data_file_df = data_file_df.replace({pd.np.nan: None})

            data_dict_list = data_file_df.to_dict(orient="records")

            # The first line of a manifest file (csv) that contains actual data
            # will be row 2 (header is line 1).
            first_data_row = 2

        except:
            raise Exception ("Problem with file to be validated") from None

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

        if first_data_row:
            line_number = "Line " + str(first_data_row + line_number) + ": "
            row_error = schema_tools.validation_errors(schema_errors,
                                                   line_prepend=line_number)
        else:
            row_error = schema_tools.validation_errors(schema_errors)

        if row_error:
            validation_errors += row_error

    print(validation_errors)
    

if __name__ == "__main__":
    main()
