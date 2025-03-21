## Python

Storage space for my Python code that may or may not be in production.

## Syntax cheat-sheet

#### Convert ISO 8601 datetime string into a datetime object
    import dateutil.parser
    new_date = dateutil.parser.parse(string_date)

#### Create a complete file path using a directory and a file name
    from pathlib import Path
    file_path = Path(directory_var).joinpath(file_name_var)

#### Delete a key from a dictionary
    dict.pop("name_of_key", None)

#### Delete duplicates from a list (does not retain the original order)
    list2 = list(set(list1))

#### Delete None values from a dictionary
    new_dict = {k: v for k, v in dict.items() if v is not None}

#### Execute a Python script in ipython
    exec(open("python_script.py").read())

#### Get the character represented by an ordinal value
    ord_char = chr(ord(orig_char))

#### Get current date
    import datetime
    current_date = datetime.datetime.today()
    
#### Get difference in days between two datetime objects
    import datetime
    date_diff = dt_object2 - dt_object1
    date_diff.days

#### Get the longest string in a list of strings
    result = max(string_list, key=len)
    
#### Get the name of a file from a string containing the full path
    from pathlib import Path
    in_file = Path(full_path_var).name

#### Get the name of a file, excluding extension, from a string containing the full path
    from pathlib import Path
    in_file_no_ext = Path(full_path_var).stem

#### Get the ordinal value of a character
    char_ord = ord(orig_char)

#### Pandas - append data frames
    df1 = df1.append(df2, ignore_index=True, sort=False)

#### Pandas - append dictionary to data frame
    df = df.append(dictionary, ignore_index=True)

#### Pandas - check that a column contains a string
    (df["column_name"].notnull()) &
    (df["column_name"].str.contains("string"))

#### Pandas - check that a column does not contain a string
    (df["column_name"].notnull()) &
    (~df["column_name"].str.contains("string", na=False))

#### Pandas - convert a column to a list
    column_list = df["column"].tolist()

#### Pandas - convert a dataframe to a list of dictionaries
    dict_list = df.to_dict("records")

#### Pandas - convert values in a list column to string
    df["column_name"] = ["".join(i) if isinstance(i, list) else i for i in df["column_name"]]

#### Pandas - convert values in a string column to integer
    df["column_name"] = pd.to_numeric(df["column_name"], errors="coerce").astype(pd.Int64Dtype())

#### Pandas - count the number of occurences of each unique column value
    unique_values = df.groupby("column_name")["column_name"].count()

#### Pandas - count the total number of unique column values
    total_unique = df["column_name"].nunique()

#### Pandas - create new column based on current column values
    df.loc[df["current_column"] == "CurrentColumnValue", "new_column"] = "NewColumnValue"

#### Pandas - drop columns
    df.drop(["column1", "column2", etc.], axis=1, inplace=True)

#### Pandas - drop duplicate rows (keep first row and drop all others)
    df.drop_duplicates(keep="first", inplace=True)

#### Pandas - drop duplicate rows based on columns (keep first row and drop all others)
    df.drop_duplicates(["column1", "column2", "column3", etc.], keep="first", inplace=True)

#### Pandas - drop NaN
    df.dropna(axis=0, subset=["ColumnName"], inplace=True)

#### Pandas - get the first X columns in a dataframe
    df1 = df.iloc[:, :X]

#### Pandas - get only alphabetic characters from a string
    df["new_column"] = df["original_column"].str.replace("\d+", "", regex=True)

#### Pandas - get only numeric characters from a string
    df["new_column"] = df["original_column"].str.extract("(\d+)", expand=False)

#### Pandas - initialize empty data frame with column names
    df = pd.DataFrame(columns=["column1", "column2", "column3", etc.])

#### Pandas - keep specified columns
    df = df[["column1", "column2", etc.]]

#### Pandas - merge data frames (outer) with indicator
    new_df = pd.merge(df1, df2, how="outer",
                      left_on="df1_column", right_on="df2_column",
                      indicator=True)

#### Pandas - read_csv specifying utf-8 (get rid of special characters in the first column name)
    df = pd.read_csv(filehandle, encoding="utf-8")

#### Pandas - read_csv with tabs as delimiters
    df = pd.read_csv(filehandle, sep="\t")

#### Pandas - rename columns
    df = df.rename(columns={"OldColumnName1": "NewColumnName1", "OldColumnName2": "NewColumnName2", etc.})

#### Pandas - replace Greek letter mu with a "u"
    df["column"] = df["column"].str.replace('\xb5', 'u')

#### Pandas - replace NaN with empty string
    df.fillna("", inplace=True)

#### Pandas - replace NaN with None
    df2 = df1.where(df1.notnull(), None)

#### Pandas - split a column and take the first/last elements
    df["new_column"] = df["original_column"].str.split("split character").str[0]
    df["new_column"] = df["original_column"].str.split("split character").str[-1]

#### Pandas - strip unwanted characters from a column
    df["column_name"] = df["column_name"].str.strip("unwanted characters")

#### Pandas - write to an output file
    df.to_csv(filehandle, index=False)
    df.to_csv(filehandle, sep="\t", index=False)

#### Pandas - write to an output file in DOS without creating blank lines
    filehandle = open("filename", "w", newline="\n")
    df.to_csv(filehandle, index=False)

#### Pandas - write to standard output
    import sys
    df.to_csv(sys.stdout, index=False)

#### Reload a module in ipython
    from importlib import reload
    reload(module)

#### Remove all non-numeric characters in a string
    import re
    new_string = re.sub("[^\d]", "", old_string)

#### Remove duplicates from a list
    new_list = list(set(old_list))

#### Rename a key in a dictionary
    dictionary[new_key] = dictionary.pop(old_key)

#### Run a script from interactive Python (V3)
    exec(open("python script").read())

#### Set the random seed to the current datetime
    import random
    from datetime import datetime
    random.seed(datetime.now().timestamp())

#### Synapse login
    import synapseclient
    syn = synapseclient.Synapse()
    syn.login(silent=True)

#### Synapse walk a Synapse folder structure to get file SynIDs
    Synapse login (see above)
    import synapseutils
    syn_contents = synapseutils.walk(syn, folder_syn_id)
    for __, __, filelist in syn_contents:
        if len(filelist) > 0:
            for __, syn_id in filelist:
