#!/usr/bin/env python3

"""
Program: schema_tools.py

Purpose: Common functions used by validation or template generation programs.

"""

"""
Function: convert_bool_to_string

Purpose: Convert a value from the Python Boolean representation (True/False)
         into a lower case string representation (true/false).

Arguments: A variable that might contain a Python Boolean value

Returns: Either a) a string representation of a Boolean value if
         the value passed in was a Python Boolean, or b) the original
         value if it was not.

"""

def convert_bool_to_string(input_value):
    string_conversion = {True: "true", False: "false"}

    # Make sure that the input value is a Boolean. Passing a string in
    # will probably not matter, but passing a number into the conversion
    # will convert any 0/1 values into false/true.
    if isinstance(input_value, bool):
        return_value = string_conversion.get(input_value, input_value)
    else:
       return_value = input_value

    return(return_value)


"""
Function: convert_string_to_bool

Purpose: Convert a string true/false value into a Python Boolean value (True/False)

Arguments: A variable that might contain a true/false value

Returns: Either a) a Boolean value if the value contained a string
         true/false value, or b) the original value if it did not.

"""

def convert_string_to_bool(input_value):
    bool_conversion = {"TRUE": True, "FALSE": False}

    if isinstance(input_value, str):
        return_value = bool_conversion.get(input_value.upper(), input_value)
    else:
       return_value = input_value

    return(return_value)


"""
Function: convert_string_to_numeric

Purpose: Convert a string numeric value into the appropriate numeric typ (either
         integer or float).

Arguments: A variable that might contain a string representation of a number.

Returns: Either a) a number, or b) the original value if the string was not a number.

"""


def convert_string_to_numeric(input_value):

    if input_value.isnumeric():
        return_value = int(input_value)
    elif input_value.replace(".", "", 1).isnumeric():
        return_value = float(input_value)
    else:
       return_value = input_value

    return(return_value)



"""
Function: load_and_deref

Purpose: Load the JSON validation schema and resolve any $ref statements.

Arguments: JSON schema file handle

Returns: The full path of the object reference, and a dereferenced JSON schema in
         dictionary form

"""

def load_and_deref(schema_file_handle):

    import json
    import jsonschema

    ref_location_dict = {}

    # Load the JSON schema. I am not using jsonref to resolve the $refs on load 
    # so that the $refs can point to different locations. I formerly had to pass in
    # a reference path when I was using jsonref, so all of the modules accessed by
    # the $ref statements had to live in the same location.
    json_schema = json.load(schema_file_handle)

    # Create a reference resolver from the schema.
    ref_resolver = jsonschema.RefResolver.from_schema(json_schema)

    # Resolve any references in the schema.
    for schema_key in json_schema["properties"]:
        if "$ref" in json_schema["properties"][schema_key]:
            deref_object = ref_resolver.resolve(json_schema["properties"][schema_key]["$ref"])
            ref_location_dict[schema_key] = deref_object[0]
            json_schema["properties"][schema_key] = deref_object[1]
        else:
            json_schema["properties"][schema_key] = json_schema["properties"][schema_key]

    return(ref_location_dict, json_schema)


"""
Function: values_list_keywords

Purpose: Return the current list of JSON keywords that designate a values list.

Arguments: None

"""

def values_list_keywords():
    return(["anyOf", "enum"])
