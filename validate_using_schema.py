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
from schema_tools import convert_bool_to_string, convert_string_to_bool, convert_string_to_numeric
from schema_tools import load_and_deref, validate_object, values_list_keywords

# This function is necessary when references are allowed to contain multiple
# types. It has been decided as of now that multiple types will not be allowed,
# but I am leaving this in anticipation of that decision being reversed in the
# future.

def convert_to_boolean(data_row, val_schema):

    values_list_keys = values_list_keywords()
    converted_row = dict()

    # We only want to convert strings into Booleans if the field has a controlled
    # values list and has more than one possible type, e.g. True, False, "Unknown".
    # In that instance, we want to convert a string true/false to a Boolean true/false
    # while ignoring case (true, TRUE, False, FaLsE, etc.).
    for rec_key in data_row:
            
        # Pass the row through if:
        # a) the key is not in the schema, i.e. the site put extra columns in the file;
        # b) the value is not a string;
        # c) the value is a string but there are no other alternative types/values for it in the schema
        if ((rec_key not in val_schema["properties"])
            or (not(isinstance(data_row[rec_key], str)))
            or ((isinstance(data_row[rec_key], str))
                and not(any(value_key in val_schema["properties"][rec_key] for value_key in values_list_keys)))):
            converted_row[rec_key] = data_row[rec_key]

        else:
            # If it is possible for the key to contain a number and the string value is some sort of number,
            # convert the string into a number.
            vkey = list(set(values_list_keys).intersection(val_schema[rec_key]))[0]
            number_is_possible = False
            for schema_values in val_schema["properties"][rec_key][vkey]:
                if ("type" in schema_values) and (schema_values["type"] in ["integer", "number"]):
                    number_is_possible = True
                    break

            if number_is_possible:
                returned_value = convert_string_to_numeric(data_row[rec_key])
                if not(isinstance(returned_value, str)):
                    converted_row[rec_key] = returned_value
                else:
                    converted_row[rec_key] = convert_string_to_bool(data_row[rec_key])

            else:
                converted_row[rec_key] = convert_string_to_bool(data_row[rec_key])

    return converted_row


def convert_from_boolean(data_row, val_schema):

    values_list_keys = values_list_keywords()
    converted_row = dict()

    for rec_key in data_row:
            
        # Pass the row through if:
        # a) the key is not in the schema, i.e. the site put extra columns in the file;
        # b) the value is not a Boolean;
        # c) the value is a Boolean but there are no other alternative types/values for it in the schema
        if ((rec_key not in val_schema["properties"])
            or (not(isinstance(data_row[rec_key], bool)))
            or ((isinstance(data_row[rec_key], bool))
                and not(any(value_key in val_schema["properties"][rec_key] for value_key in values_list_keys)))):
            converted_row[rec_key] = data_row[rec_key]

        else:
            # We only want to convert Booleans into strings if the field has a controlled
            # values list and has more than one possible type, e.g. "true", "false", "Unknown".
            # In that instance, we want to convert a Boolean True/False to a string true/false.
            vkey = list(set(values_list_keys).intersection(val_schema["properties"][rec_key]))[0]
            string_is_possible = False
            for schema_values in val_schema["properties"][rec_key][vkey]:
                if ("const" in schema_values) and (isinstance(schema_values["const"], str)):
                    string_is_possible = True
                    break

            if string_is_possible:
                converted_row[rec_key] = convert_bool_to_string(data_row[rec_key])
            else:
                converted_row[rec_key] = data_row[rec_key]

    return converted_row


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("validation_obj_file", type=argparse.FileType("r"),
                        help="Full pathname for the object to be validated")
    parser.add_argument("--manifest_file", action="store_true",
                        help="Is the object to be validated a manifest file?")

    args = parser.parse_args()

    row_error = ""
    validation_errors = ""
    data_dict_list = []

    # Load the JSON schema and create a validator..
    _, json_schema = load_and_deref(args.json_schema_file)
    schema_validator = jsonschema.Draft7Validator(json_schema)

    # If the object to be validated is a manifest file, read it into a pandas
    # dataframe.  Otherwise, read it into JSON.
    if args.manifest_file:
        data_file_df = pd.read_csv(args.validation_obj_file)

        # Pandas reads in empty fields as nan. Replace nan with None.
        data_file_df = data_file_df.replace({pd.np.nan: None})

        data_dict_list = data_file_df.to_dict(orient="records")

        # The first row of a manifest file (csv) that contains actual data will
        # be row 2 (header is line 1), so add 2 to the python row counter.
        first_data_row = 2

    else:
        json_file_dict = json.load(args.validation_obj_file)
        data_dict_list.append(json_file_dict)

        # A JSON file is considered to only have one row of data.
        first_data_row = 1

    for row_number, data_record in enumerate(data_dict_list):

        # Remove any None values from the dictionary - it simplifies the coding of the
        # JSON validation schema.
        clean_record = {k: data_record[k] for k in data_record if data_record[k] is not None}

        # We are not currently allowing multiple types in reference definitions, so convert
        # Booleans to strings if the key is also allowed to contain string values.
        converted_clean_record = convert_from_boolean(clean_record, json_schema)

        row_text = f"Row {row_number + first_data_row}:"
        row_error = validate_object(schema_validator, converted_clean_record, prepend_text=row_text)

        if row_error:
            validation_errors += row_error

    print(validation_errors)
    

if __name__ == "__main__":
    main()
