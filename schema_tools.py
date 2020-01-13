#!/usr/bin/env python3

"""
Program: schema_tools.py

Purpose: Common functions used by validation or template generation programs.

"""

VALUES_LIST_KEYWORDS = ["anyOf", "enum"]


def convert_bool_to_string(input_value):

    """
    Function: convert_bool_to_string

    Purpose: Convert a value from the Python Boolean representation (True/False)
             into a lower case string representation (true/false).

    Arguments: A variable that might contain a Python Boolean value

    Returns: Either a) a string representation of a Boolean value if
             the value passed in was a Python Boolean, or b) the original
             value if it was not.
    """
    string_conversion = {True: "true", False: "false"}

    # Make sure that the input value is a Boolean. Passing a string in
    # will probably not matter, but passing a number into the conversion
    # will convert any 0/1 values into false/true.
    if isinstance(input_value, bool):
        return_value = string_conversion.get(input_value, input_value)
    else:
        return_value = input_value

    return return_value


def convert_numeric_to_string(input_value):

    """
    Function: convert_numeric_to_string

    Purpose: Convert a value from the Python numeric representation (float/int)
             into a string representation.

    Arguments:
        input_value - A variable that might contain a Python numeric value

    Returns: Either a) a string representation of a numeric value if
             the value passed in was a Python numeric, or b) the original
             value if it was not.
    """

    # Make sure that the input value is numeric so that it does not
    # inadvertently convert another type. If the Boolean check is not
    # included, it will return a string representation of a Boolean value,
    # i.e. "True"/"False".
    if ((isinstance(input_value, (float, int)))
            and (not isinstance(input_value, bool))):
        return_value = str(input_value)
    else:
        return_value = input_value

    return return_value



def convert_string_to_bool(input_value):
    """
    Function: convert_string_to_bool

    Purpose: Convert a string true/false value into a Python Boolean value (True/False)

    Arguments: A variable that might contain a true/false value

    Returns: Either a) a Boolean value if the value contained a string
             true/false value, or b) the original value if it did not.
    """
    bool_conversion = {"TRUE": True, "FALSE": False}

    if isinstance(input_value, str):
        return_value = bool_conversion.get(input_value.upper(), input_value)
    else:
        return_value = input_value

    return return_value


def convert_string_to_numeric(input_value):
    """
    Function: convert_string_to_numeric

    Purpose: Convert a string numeric value into the appropriate numeric type
             (either integer or float).

    Arguments: A variable that might contain a string representation of a
               numeric value.

    Returns: Either a) a numeric value, or b) the original value if the string
             was not numeric.
    """
    if input_value.isnumeric():
        return_value = int(input_value)
    elif input_value.replace(".", "", 1).isnumeric():
        return_value = float(input_value)
    else:
        return_value = input_value

    return return_value


def convert_from_other(data_row, val_schema, func_to_run):
    """
    Function: convert_from_other

    Purpose: Converts non-string values to string representations.

    This function in used by JSON validation programs in cases where a JSON
    schema reference is not allowed to contain multiple types and values that
    can contain more than one type are coerced to strings. In cases where a
    reference is defined as a string and a value is read as Boolean (True/
    False) or numeric (float/int), it will fail validation.

    Input parameters:
        data_row - a dictionary representing a single row of data
        val_schema - the JSON validation schema representing the structure
                     of the data row.
        func_to_run - the function to be run to do the conversion.

    Returns: A dictionary representing the data row, with non-string values
             converted to strings.
    """
    converted_row = dict()

    for rec_key in data_row:
        schema_val = val_schema["properties"][rec_key]

        # Pass the row through if:
        # a) the key is not in the schema, i.e. the site put extra columns in
        #    the file;
        # b) the value is a string;
        # c) the value is not a string but there are no other alternative
        #    types/values for it in the schema
        if ((rec_key not in val_schema["properties"])
                or (isinstance(data_row[rec_key], str))
                or ((not isinstance(data_row[rec_key], str))
                    and (not any(value_key in schema_val for value_key in VALUES_LIST_KEYWORDS)))):
            converted_row[rec_key] = data_row[rec_key]

        else:
            # We only want to convert other types into strings if the field has
            # a controlled values list and has more than one possible type,
            # e.g. "true", "false", "Unknown". In that instance, we want to
            # convert a Boolean True/False to a string true/false.
            vkey = list(set(VALUES_LIST_KEYWORDS).intersection(schema_val))[0]
            for schema_values in schema_val[vkey]:
                if ("const" in schema_values) and (isinstance(schema_values["const"], str)):
                    converted_row[rec_key] = func_to_run(data_row[rec_key])
                    break
                else:
                    converted_row[rec_key] = data_row[rec_key]

    return converted_row


def convert_string_to_other(data_row, val_schema, type_list, func_to_run):
    """
    Function: convert_string_to_other

    Purpose: Converts string representations of another type to the actual
             type value.

    This function in used by JSON validation programs in cases where a JSON
    schema reference is allowed to contain multiple types. In cases where a
    reference is defined as both a string and something else (Boolean,
    integer, number), the non-string values will be read as strings and will
    therefore fail validation if the string representation is not enumerated
    as a possible value.

    Input parameters:
        data_row - a dictionary representing a single row of data
        val_schema - the JSON validation schema representing the structure
                     of the data row.
        type_list - a list of the types to be converted to. This is a list
                    because a numeric value can be an integer or a number
                    (Python float).
        func_to_run - the function to be run to do the conversion.

    Returns: A dictionary representing the data row, with string values
             converted to the specified type values.
    """
    converted_row = dict()

    for rec_key in data_row:
        schema_val = val_schema["properties"][rec_key]

        # Pass the row through if:
        # a) the key is not in the schema, i.e. the site put extra columns in the file;
        # b) the value is not a string;
        # c) the value is a string but there are no other alternative
        #    types/values for it in the schema
        if ((rec_key not in val_schema["properties"])
                or (not isinstance(data_row[rec_key], str))
                or ((isinstance(data_row[rec_key], str))
                    and (not any(value_key in schema_val for value_key in VALUES_LIST_KEYWORDS)))):
            converted_row[rec_key] = data_row[rec_key]

        else:
            vkey = list(set(VALUES_LIST_KEYWORDS).intersection(schema_val))[0]
            for schema_values in schema_val[vkey]:
                if ("type" in schema_values) and (schema_values["type"] in type_list):
                    converted_row[rec_key] = func_to_run(data_row[rec_key])
                    break
                else:
                    converted_row[rec_key] = data_row[rec_key]

    return converted_row


def get_definitions_values(json_schema):
    """
    Function: get_definitions_values

    Purpose: Return pandas dataframes of schema properties needed to generate
             templates.

    Input parameters: File object pointing to the JSON schema file

    Returns: A dataframe of key types, definitions, required keys, and maximum
             sizes
                 definitions_df["key"] - string
                 definitions_df["type"] - string
                 definitions_df["description"] - string
                 definitions_df["required"] - Boolean
                 definitions_df["maximumSize"] - integer

             A dataframe of key values lists
                 values_df["key"] - string
                 values_df["value"] - string
                 values_df["valueDescription"] - string
                 values_df["source"] - string
    """
    import pandas as pd

    definitions_columns = ["key", "type", "description", "required", "maximumSize"]
    definitions_df = pd.DataFrame(columns=definitions_columns)
    values_columns = ["key", "value", "valueDescription", "source"]
    values_df = pd.DataFrame(columns=values_columns)

    for schema_key in json_schema["properties"].keys():
        definitions_dict = {}
        definitions_dict["key"] = schema_key
        schema_values = json_schema["properties"][schema_key]

        if schema_values:
            if "type" in schema_values:
                definitions_dict["type"] = schema_values["type"]

            if "description" in schema_values:
                definitions_dict["description"] = schema_values["description"]

            if "maximumSize" in schema_values:
                definitions_dict["maximumSize"] = schema_values["maximumSize"]

            if ("required" in json_schema) and (schema_key in json_schema["required"]):
                definitions_dict["required"] = True
            else:
                definitions_dict["required"] = False

            definitions_df = definitions_df.append(definitions_dict, ignore_index=True)

            values_dict = {}
            if "pattern" in schema_values:
                values_dict["key"] = schema_key
                values_dict["value"] = schema_values["pattern"]
                values_df = values_df.append(values_dict, ignore_index=True)

            elif any([value_key in schema_values for value_key in VALUES_LIST_KEYWORDS]):
                vkey = list(set(VALUES_LIST_KEYWORDS).intersection(schema_values))[0]
                for value_row in schema_values[vkey]:
                    values_dict["key"] = schema_key

                    if "const" in value_row:
                        values_dict["value"] = value_row["const"]

                    if "description" in value_row:
                        values_dict["valueDescription"] = value_row["description"]

                    if "source" in value_row:
                        values_dict["source"] = value_row["source"]

                    values_df = values_df.append(values_dict, ignore_index=True)
                    values_dict = {}

    return(definitions_df, values_df)


def get_schema_properties(json_schema):
    """
    Function: get_schema_properties

    Purpose: Return dictionaries of schema properties needed to generate templates.

    Input parameters: File object pointing to the JSON schema file

    Returns: A dictionary of key types, definitions, required keys, and maximum sizes
                 definitions_dict[key]["type"] - string
                 definitions_dict[key]["description"] - string
                 definitions_dict[key]["required"] - Boolean
                 definitions_dict[key]["maximumSize"] - integer

             A dictionary of key values lists
                 values_dict[key][list index]["value"] - string
                 values_dict[key][list index]["valueDescription"] - string
                 values_dict[key][list index]["source"] - string
    """

    import collections

    definitions_dict = collections.defaultdict(dict)
    definitions_keys = ["type", "description", "required", "maximumSize"]
    values_dict = collections.defaultdict(list)
    values_keys = ["value", "valueDescription", "source"]

    for schema_key in json_schema["properties"].keys():
        definitions_dict[schema_key] = dict.fromkeys(definitions_keys)
        schema_values = json_schema["properties"][schema_key]

        if schema_values:
            if "type" in schema_values:
                definitions_dict[schema_key]["type"] = schema_values["type"]

            if "description" in schema_values:
                definitions_dict[schema_key]["description"] = schema_values["description"]

            if "maximumSize" in schema_values:
                definitions_dict[schema_key]["maximumSize"] = schema_values["maximumSize"]

            if ("required" in json_schema) and (schema_key in json_schema["required"]):
                definitions_dict[schema_key]["required"] = True
            else:
                definitions_dict[schema_key]["required"] = False

            if "pattern" in schema_values:
                values_dict[schema_key].append({"value": schema_values["pattern"],
                                                "valueDescription": "",
                                                "source": ""})

            elif any([value_key in schema_values for value_key in VALUES_LIST_KEYWORDS]):
                vkey = list(set(VALUES_LIST_KEYWORDS).intersection(schema_values))[0]
                for value_row in schema_values[vkey]:
                    key_values_dict = dict.fromkeys(values_keys)

                    if "const" in value_row:
                        key_values_dict["value"] = value_row["const"]

                    if "description" in value_row:
                        key_values_dict["valueDescription"] = value_row["description"]

                    if "source" in value_row:
                        key_values_dict["source"] = value_row["source"]

                    values_dict[schema_key].append(key_values_dict)

    return(definitions_dict, values_dict)


def load_and_deref(schema_file_handle):
    """
    Function: load_and_deref

    Purpose: Load the JSON validation schema and resolve any $ref statements.

    Arguments: JSON schema file handle

    Returns: A dictionary containing the full path of the object reference, and a
             dereferenced JSON schema in dictionary form
    """
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


def set_comma_val(element_number, object_length):
    """
    Function: set_comma_val

    Purpose: Given the enumerated value of an element in an iterable object and
             the length of the object, determine whether the element is the
             last one in the object. If not, return a comma.

             Note that enumerated values start at 0, so it is necessary to add
             1 to them in order to compare them to the length.

             This function is used by other functions that create JSON schemas
             from Python dictionaries.

    Arguments: element_number: the number of the current element in the object
               object_length: the length of the object

    Returns: - a comma, if the element is not the last one in the object
             - a character null value if the element is the last one in the
               object.
    """
    if (element_number + 1) < object_length:
        comma_val = ","
    else:
        comma_val = ""

    return comma_val


def validation_errors(schema_errors, **kwargs):
    """
    Function: validation_errors

    Purpose: Create an output error message for errors found using a
             jsonschema validator

    If the issue is a violation of the object properties, e.g. a type
    different than what has been defined or a value that is not in the
    enumerated list of allowed values, the first value in the
    relative_schema_path deque (0) is going to be "properties" and the second
    value is going to be the name of the object in error. This is useful to
    have because the error message will print the violation but not the object
    causing it.

    If the problem is a relational issue (i.e. an object that is conditionally
    required based on the value of other objects is  missing), the error
    message will contain the name of the object. The relative_schema_path deque
    will contain the constraint that was violated, but nothing useful for
    identifying the object, so only the error message is pertinent.

    Arguments: The deque output of the jsonschema validator
               Any text to be prepended to the error string

    Returns: A string containing any errors found during validation
    """

    prepend_string = ""
    error_string = ""

    for in_string in kwargs.values():
        prepend_string += in_string

    for error in schema_errors:
        if error.relative_schema_path[0] == "properties":
            error_string += f"{prepend_string}{error.relative_schema_path[1]}: {error.message}\n"
        else:
            error_string += f"{prepend_string}{error.message}\n"

    return error_string


def walk_schema(schema_obj, schema_output, first_call):
    """
    Function: walk_schema

    Purpose: Recursively walk through the schema dictionary and construct
             output to be written to a JSON schema file. The recursion is
             necessary because a schema dictionary can have varying levels of
             nested dictionaries and lists.

             There are operations that only get performed the first time the
             function is called, so the first_call parameter should always be
             set to True when called in open code.

    Arguments: schema_obj: The Python dictionary representation of a JSON
                           schema
               schema_output: A character string for the output that gets
                              appended to
               first_call: A Boolean value designating whether the current
                           iteration is the first call to the function. It is
                           internally set to False in all subsequent calls.

    Returns: A character string of output
    """
    # The top level of any structure fed into this function is a dictionary,
    # so start the output structure with an opening curly brace.
    schema_output += "{\n"

    schema_obj_len = len(schema_obj)
    for key_number, (obj_key, obj_val) in enumerate(schema_obj.items()):

        # All of the elements of the dictionary, list, etc. are separated by
        # commas. However, the last element has no need for a comma.
        obj_comma = set_comma_val(key_number, schema_obj_len)

        if isinstance(obj_val, dict):
            schema_output += f"\"{obj_key}\" : "
            schema_output = walk_schema(obj_val, schema_output, False)
            schema_output += f"}}{obj_comma}\n"

        elif isinstance(obj_val, list):
            list_len = len(obj_val)
            for element_number, element_val in enumerate(obj_val):
                element_comma = set_comma_val(element_number, list_len)

                if element_number == 0:
                    schema_output += f"\"{obj_key}\" : [\n"

                # Lists in the data structure are either going to be lists of
                # dictionaries, e.g. in enum statements or if statements, or
                # lists of items, e.g. in required statements.
                if isinstance(element_val, dict):
                    schema_output = walk_schema(element_val, schema_output, False)
                    schema_output += f"}}{element_comma}\n"

                    if (element_number + 1) == list_len:
                        schema_output += f"]{obj_comma}\n"

                else:
                    schema_output += f"\"{element_val}\"{element_comma}\n"

                    if (element_number + 1) == list_len:
                        schema_output += f"]{obj_comma}\n"

        else:
            schema_output += f"\"{obj_key}\" : "

            # Do not put quotes around numeric values (integers or floats).
            # Since Boolean values are not enumerated in the reference
            # definitions unless they are not true Boolean values, they should
            # be quoted.
            if isinstance(obj_val, (str, bool)):
                schema_output += f"\"{obj_val}\"{obj_comma}\n"
            else:
                schema_output += f"{obj_val}{obj_comma}\n"

    # If we are exiting the initial call to the function, close the final
    # iteration.
    if first_call:
        schema_output += "}\n"

    return schema_output
