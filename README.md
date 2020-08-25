## Python

Storage space for my Sage python code that may or may not be in production.

## Syntax cheat-sheet

#### Convert ISO 8601 datetime string into a datetime object
    import dateutil.parser
    new_date = dateutil.parser.parse(string_date)

#### Get current date
    import datetime
    current_date = datetime.datetime.today()
    
#### Get difference in days between two datetime objects
    import datetime
    date_diff = dt_object2 - dt_object1
    date_diff.days

#### Pandas - append data frames
    df1 = df1.append(df2, ignore_index=True, sort=False)

#### Pandas - append dictionary to data frame
    df = df.append(dictionary, ignore_index=True)

#### Pandas - count the number of occurences of each unique column value
    unique_values = df.groupby("column_name")["column_name"].count()

#### Pandas - count the total number of unique column values
    total_unique = df["column_name"].nunique()

#### Pandas - create new column based on current column values
    df.loc[df["current_column"] == "CurrentColumnValue", "new_column"] = "NewColumnValue"

#### Pandas - drop columns
    df.drop(["column1", "column2", etc.], axis=1, inplace=True)

#### Pandas - drop NaN
    df.dropna(axis=0, subset=["ColumnName"], inplace=True)

#### Pandas - initialize empty data frame with column names
    df = pd.DataFrame(columns=["column1", "column2", "column3", etc.])

#### Pandas - keep specified columns
    df = df[["column1", "column2", etc.]]

#### Pandas - merge data frames (outer) with indicator
    new_df = pd.merge(df1, df2, how="outer",
                      left_on="df1_column", right_on="df2_column",
                      indicator=True)

#### Pandas - read_csv with tabs as delimiters
    df = pd.read_csv(filehandle, sep="\t")

#### Pandas - rename columns
    df = df.rename(columns={"OldColumnName1": "NewColumnName1", "OldColumnName2": "NewColumnName2", etc.})

#### Pandas - replace NaN with empty string
    df.fillna("", inplace=True)

#### Pandas - replace NaN with None
    df2 = df1.where(df1.notnull(), None)

#### Pandas - write to an output file
    df.to_csv(filehandle, index=False)
    df.to_csv(filehandle, sep="\t", index=False)

#### Pandas - write to standard output
    import sys
    df.to_csv(sys.stdout, index=False)

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
