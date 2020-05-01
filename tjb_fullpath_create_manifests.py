import re
import os
import pandas as pd
import synapseclient
import synapseutils

syn = synapseclient.Synapse()
syn.login(silent=True)

SAMPLE_FILES_DIR = "/home/cmolitor/temp/bsmn_reprocessing/tjb_raw_sample_lists"
SAMPLE_FILES_FOLDER_ID = "syn21819948"

OUTPUT_DIRECTORY = "/home/cmolitor/temp/bsmn_reprocessing/manifest_files"
OUTPUT_FILE_SUFFIX = "reprocessed_fullpath.csv"

S3_LOCATION_FILE = "/home/cmolitor/temp/bsmn_reprocessing/s3_locations.csv"

TJB_COMPARISON_FILE = "/home/cmolitor/temp/bsmn_reprocessing/tjb_comparison_confirmed.csv"

REPROCESSED_ID_FILE = "/home/cmolitor/temp/bsmn_reprocessing/reprocessed_sampleID.csv"

FILE_SAMPLE_COLUMNS = ["file_sample_id", "data_file", "data_file_path"]
DATAFILE_COLUMNS = ["data_file1_bsmn_location", "data_file2_bsmn_location", "data_file3_bsmn_location", "data_file4_bsmn_location"]
SAMPLE_MANIFEST_COLUMNS = ["subjectkey", "experiment_id", "src_subject_id", "interview_age",
                           "interview_date", "sample_description", "sample_id_original",
                           "organism", "sample_amount", "sample_unit", "data_code", "data_file1_type",
                           "data_file1", "data_file2_type", "data_file2", "data_file3_type",
                           "data_file3", "data_file4_type", "data_file4", "storage_protocol",
                           "data_file_location", "biorepository", "patient_id_biorepository",
                           "sample_id_biorepository", "cell_id_original", "cell_id_biorepository",
                           "comments_misc", "site", "rat280", "rat230", "gqn", "seq_batch"]

FILE_EXTENSIONS = [".cram", ".cram.crai", ".flagstat.txt", ".ploidy_2.vcf.gz",
                   ".ploidy_2.vcf.gz.tbi", ".ploidy_12.vcf.gz", ".ploidy_12.vcf.gz.tbi",
                   ".ploidy_50.vcf.gz", ".ploidy_50.vcf.gz.tbi",".unmapped.bam"]

SYN_GUID_SAMPLES = "syn20822548"

datafile_df = pd.DataFrame()
expanded_sample_df = pd.DataFrame()

# Get the LIVE sample file from the GUID API and split it into separate lines
# per file to make it easier to compare to Taejeong's sample files.
guid_sample_file = open(syn.get(SYN_GUID_SAMPLES).path)
guid_sample_df = pd.read_csv(guid_sample_file)
guid_sample_df.columns = guid_sample_df.columns.str.lower()

for col_var in DATAFILE_COLUMNS:
    datafile_df = datafile_df.append(guid_sample_df, ignore_index=True)
    datafile_df["orig_file"] = datafile_df[col_var]
    datafile_df.dropna(subset=["orig_file"], how="all", inplace=True)
    expanded_sample_df = expanded_sample_df.append(datafile_df, ignore_index=True, sort=False)
    datafile_df = pd.DataFrame()

expanded_sample_df["orig_file"] = expanded_sample_df["orig_file"].str.lstrip("<![CDATA[").str.rstrip("]]>")
expanded_sample_df["guid_data_file"] = expanded_sample_df["orig_file"].apply(os.path.basename)

paths = expanded_sample_df.orig_file.to_list()
paths = [re.sub("/\w:/", "/", x) for x in paths] 
expanded_sample_df.orig_file = paths

# Get a list of the sample list files from Taejeong
sample_lists = synapseutils.syncFromSynapse(syn, entity=SAMPLE_FILES_FOLDER_ID,
                                            path=SAMPLE_FILES_DIR)

tjb_sample_df_list = []

for list_file in sample_lists:
    tjb_sample_file = open(list_file.path)
    tjb_sample_df = pd.read_csv(tjb_sample_file, sep="\t", names=FILE_SAMPLE_COLUMNS)
    tjb_sample_df_list.append(tjb_sample_df)

tjb_all_samples_df = pd.concat(tjb_sample_df_list, axis=0, ignore_index=True)

# Create the data file list including the correct sample ID by merging on the
# full path name.
fullpath_merge_df = pd.merge(expanded_sample_df, tjb_all_samples_df, how="outer",
                             left_on="orig_file", right_on="data_file_path",
                             indicator=True) 

fullpath_sample_df = fullpath_merge_df.loc[fullpath_merge_df["_merge"] == "both"]

# There were several files that could not be merged on the full path name
# but could be merged on just the file name.  I sent this list to TJ, and
# he reviewed it and returned a list of files confirming the file
# corresponded to the NDA path name that I had found.
nopath_df = fullpath_merge_df.loc[fullpath_merge_df["_merge"] == "right_only"].copy()
nopath_df = nopath_df[["data_file", "file_sample_id"]]

tjb_confirmed_df = pd.read_csv(open(TJB_COMPARISON_FILE, "r"))
tjb_confirmed_df.drop("sample_id_original", axis=1, inplace=True)

filename_merge_df = pd.merge(nopath_df, tjb_confirmed_df, how="inner", on="data_file")

filename_sample_df = pd.merge(filename_merge_df, expanded_sample_df, how="inner",
                              left_on="nda_data_file_path", right_on="orig_file")

sample_info_df = pd.concat([fullpath_sample_df, filename_sample_df], axis=0, ignore_index=True, sort=False)

# Since the same sample ID can be used for multiple files, create an index
# field that can be carried along and used in later mergings. If this is not
# done, you will wind up with a many-to-many merge situation if you only
# merge on sample ID.
sample_info_df["sample_index"] = sample_info_df.index

# Keep the fields that are going to be needed to populate all of the fields
# in the new sample manifests except for the data file information.
sample_info_df = sample_info_df[["biorepository", "cell_id_original", "comments_misc", "data_code",
                                 "data_file_location", "experiment_id", "organism",
                                 "patient_id_biorepository", "sample_amount", "sample_description",
                                 "sample_id_biorepository", "sample_id_original", "sample_unit",
                                 "seq_batch", "site", "src_subject_id", "storage_protocol",
                                 "subjectkey", "collection_id", "file_sample_id", "sample_index",
                                 "data_file"]]

file_list_df_small = sample_info_df[["file_sample_id", "sample_index"]]

fileext_df = pd.DataFrame()

# Create files with the necessary extensions to match the resubmitted files.
for file_ext in FILE_EXTENSIONS:
    ext_df = pd.DataFrame()
    ext_df = file_list_df_small.copy()
    ext_df["name"] = ext_df["file_sample_id"] + file_ext

    fileext_df = fileext_df.append(ext_df, ignore_index=True)

fileext_df = fileext_df.drop_duplicates(subset=["name"])
fileext_df.drop("file_sample_id", axis=1, inplace=True)

# Read in the data downloaded from Kenny's reprocessed grant data table and get
# the S3 scratch button location from the ID.
reprocessed_df = pd.read_csv(open(REPROCESSED_ID_FILE, "r"))
reprocessed_df = reprocessed_df[["name", "id", "sample_id_used"]]

# Read in the file containing the file S3 scratch bucket location information.
# I pregenerated this file because it takes a long time to run. The snippet of
# code that generated it is:
# location_list = []
# synid_list = reprocessed_df["id"].tolist()
# for syn_id in synid_list:
#     location_dict = {}
#     file_handle = syn._getEntityBundle(syn_id)["fileHandles"][0]
#     location_dict["id"] = syn_id
#     location_dict["key"] = file_handle["key"]
#     location_dict["bucketName"] = file_handle["bucketName"]
#     location_list.append(location_dict)
# location_df = pd.DataFrame(location_list)
#
# ...and then dump it to a csv.
s3_location_df = pd.read_csv(open(S3_LOCATION_FILE, "r"))
s3_location_df["data_file1_type"] = s3_location_df["key"].str.rsplit(".", 1).str[-1]
s3_location_df["data_file1"] = s3_location_df["key"].str.split("/", 1).str[1]

reprocessed_s3_df = pd.merge(reprocessed_df, s3_location_df, how="inner", on="id")

# Compare the reprocessed file to the list of file names generated above to 
# weed out any of the created names that don't actually have files to go with them.
reprocessed_files_df = pd.merge(fileext_df, reprocessed_s3_df, how="right",
                                on="name")

# Merge the file list with the sample information.
reprocessed_files_sample_df = pd.merge(reprocessed_files_df, sample_info_df, how="inner",
                                       left_on=["sample_id_used", "sample_index"],
                                       right_on=["sample_id_original", "sample_index"])

# Break the files out by collection and write out the manifests.
collection_list = reprocessed_files_sample_df["collection_id"].tolist()
collection_list = list(set(collection_list))

for collection_id in collection_list:
    int_collection_id = int(collection_id)
    output_df = pd.DataFrame(columns = SAMPLE_MANIFEST_COLUMNS)
    collection_df = reprocessed_files_sample_df.loc[reprocessed_files_sample_df["collection_id"] == collection_id].copy()
    output_df = output_df.append(collection_df, sort=False)
    output_df.drop(["sample_index", "name", "id", "sample_id_used", "bucketName",
                    "key", "collection_id", "file_sample_id", "data_file"], axis=1, inplace=True)
    output_df["interview_age"] = 999
    output_df["interview_date"] = pd.to_datetime('today').date()
    collection_output_file = f"{OUTPUT_DIRECTORY}/coll{int_collection_id}_{OUTPUT_FILE_SUFFIX}"
    with open(collection_output_file, "w") as output_file:
        output_df.to_csv(output_file, index=False)

