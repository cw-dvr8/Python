## Python

Storage space for my Sage python code that may or may not be in production.

## Syntax cheat-sheet

#### Pandas - append data frames
    df1 = df1.append(df2, ignore_index=True, sort=False)

#### Pandas - drop columns
    df.drop(["column1", "column2", etc.], axis=1, inplace=True)

#### Pandas - drop NaN
    df.dropna(axis=0, subset=["ColumnName"], inplace=True)

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

#### Synapse login
    import synapseclient
    syn = synapseclient.Synapse()
    syn.login(silent=True)
