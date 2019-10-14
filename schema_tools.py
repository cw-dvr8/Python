#!/usr/bin/env python3

"""
Program: schema_tools.py

Purpose: Common functions used by validation or template generation programs.

"""

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
            ref_location = deref_object[0]
            json_schema["properties"][schema_key] = deref_object[1]
        else:
            json_schema["properties"][schema_key] = json_schema["properties"][schema_key]

    return(ref_location, json_schema)


"""
Function: values_list_keywords

Purpose: Return the current list of JSON keywords that designate a values list.

Arguments: None

"""

def values_list_keywords():
    return(["anyOf", "enum"])
