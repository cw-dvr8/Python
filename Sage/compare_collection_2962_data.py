import pandas as pd

# Get the GUID API sample data.
live_sample_file = open("/home/cmolitor/temp/nda-manifests-genomics_sample03-LIVE.csv", "r")
live_sample_df = pd.read_csv(live_sample_file)
live_2962_df = live_sample_df.loc[live_sample_df["collection_id"] == 2962]
live_2962_df.columns = map(str.lower, live_2962_df.columns)
live_2962_df = live_2962_df[["subjectkey", "experiment_id", "collection_id"]]

# Get the Submission API sample data.
orig_sample_file = open("/home/cmolitor/temp/nda-manifests-genomics_sample-ORIGINAL.csv", "r")
orig_sample_df = pd.read_csv(orig_sample_file)
orig_2962_df = orig_sample_df.loc[orig_sample_df["collection_id"] == 2962]
orig_2962_df.columns = map(str.lower, orig_2962_df.columns)
orig_2962_df = orig_2962_df[["subjectkey", "experiment_id", "collection_id", "submission_id"]]

# Get the union of the two dataframes and look for rows that are only in the
# Submission API sample data.
all_2962_df = pd.merge(live_2962_df, orig_2962_df, how="outer", on=["subjectkey", "experiment_id", "collection_id"],
                       indicator=True)
orig_only_df = all_2962_df.loc[all_2962_df["_merge"] == "right_only"]
