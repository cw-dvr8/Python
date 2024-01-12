def walk_dictionary(schema_obj, schema_output, parent_key, parent_comma):
    parent_prefix = ""
    parent_suffix = ""

    schema_obj_len = len(schema_obj)
    for key_number, (dict_key, dict_val) in enumerate(schema_obj.items()):
        schema_comma_val = set_comma_var(key_number, schema_obj_len)
        if key_number == 0:
            parent_prefix = parent_key + f"{{\n\"{dict_key}\" : "
        elif (key_number + 1) == schema_obj_len:
            parent_suffix = "}" + schema_comma_val + "\n" + parent_comma

        if isinstance(dict_val, dict):
            schema_output = walk_dictionary(dict_val, schema_output, parent_prefix, parent_suffix)

        elif isinstance(dict_val, list):

        else:
            if key_number == 0:
                schema_output += parent_key

