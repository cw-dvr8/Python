import pandas as pd
import os

datafile_list = ["DATA_FILE1", "DATA_FILE2", "DATA_FILE3", "DATA_FILE4"]
new_guid_2966_df = pd.DataFrame()
guid_file_df = pd.DataFrame()

# Output from Kenny's daily BSMN GUID sample manifest dump - this file has up to four
# files per row, so need to split it so that each file is its own row.
guid_sample_file = open("/home/cmolitor/temp/nda-manifests-genomics_sample03-LIVE.csv", "r")
guid_sample_df = pd.read_csv(guid_sample_file)
guid_sample_2966_df = guid_sample_df.loc[guid_sample_df["collection_id"] == 2966]
for col_var in datafile_list:
    new_guid_2966_df["experiment_id"] = guid_sample_2966_df["EXPERIMENT_ID"]
    new_guid_2966_df["sample_id_original"] = guid_sample_2966_df["SAMPLE_ID_ORIGINAL"]
    new_guid_2966_df["data_file"] = guid_sample_2966_df[col_var]

    # Not all rows in the sample file have four files, so delete records where
    # there is no file.
    new_guid_2966_df.dropna(subset=["data_file"], how="all", inplace=True)
    guid_file_df = guid_file_df.append(new_guid_2966_df, ignore_index=True)

guid_file_df["file_name"] = guid_file_df["data_file"].apply(os.path.basename)
guid_file_df["file_name"] = guid_file_df["file_name"].str.strip("]]>")

# comma-separated file that Yifan sent me
missing_file = open("/home/cmolitor/temp/files_to_find.20200120.sort.csv", "r")
missing_df = pd.read_csv(missing_file)
missing_df.columns = [col.strip() for col in missing_df.columns]

# Do a left join to get all of the files in the missing dataframe and turn the
# indicator on to create the _merge variable, which indicates whether the file
# name has a match in the other dataframe.
all_files_df = pd.merge(missing_df, guid_file_df, how="left", on="file_name", indicator=True)

found_file_df = all_files_df.loc[all_files_df["_merge"] == "both"]

with open("/home/cmolitor/temp/found_files_2966.csv", "w") as out_found_file:
    found_file_df.to_csv(out_found_file, index=False)

# Get any that are still missing
not_found_df = all_files_df.loc[all_files_df["_merge"] == "left_only"]

with open("/home/cmolitor/temp/not_found_files_2966.csv", "w") as out_not_found_file:
    found_file_df.to_csv(out_not_found_file, index=False)
