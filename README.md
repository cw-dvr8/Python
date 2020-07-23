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

#### Pandas - read_csv with tabs as delimiters
    df = pd.read_csv(filehandle, sep="\t")

#### Pandas - rename columns
    df = df.rename(columns={"OldColumnName1": "NewColumnName1", "OldColumnName2": "NewColumnName2", etc.})

#### Synapse login
    syn = synapseclient.Synapse()
    syn.login(silent=True)
