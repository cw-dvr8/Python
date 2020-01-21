# Output from running collection_submissions.py
collection_file = open("/home/cmolitor/temp/collection_files.csv", "r")
collection_df = pd.read_csv(collection_file)
collection_df.columns = [col.strip() for col in collection_df.columns]
collection_df["file_remote_path"] = collection_df["file_remote_path"].str.strip()
collection_df["file_user_path"] = collection_df["file_user_path"].str.strip()
collection_df["remote_file"] = collection_df["file_remote_path"].apply(os.path.basename)

# Tab-delimited file (improperly named) that Yifan sent me
missing_file = open("/home/cmolitor/temp/files_to_find.20200120.sort.csv", "r")
missing_df = pd.read_csv(missing_file, names=["sampleID", "remote_file"], sep="\t")

found_file_df = pd.merge(missing_df, collection_df, how="left", on="remote_file")

with open("/home/cmolitor/temp/found_files_2966.csv", "w") as out_file:
    found_file_df.to_csv(out_file, index=False)
