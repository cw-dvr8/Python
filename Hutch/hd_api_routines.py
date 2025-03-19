# Test code for creating dataverses and datasets on the Harvard Dataverse,
# and adding files to them.

import json
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset
from pyDataverse.models import Datafile
from pyDataverse.utils import read_file
base_url = "https://demo.dataverse.org"

# Connecting
# The api token should be read from a file in the user's home directory
# that contains the tokens for the target dataverse (i.e. Harvard Dataverse,
# demo dataverse). 
api = NativeApi(base_url, api_token)

# Checking the connection
api_response = api.get_info_version()
api_response.json()

# Create a dataverse. The metadata has to be type str.
# "Category" is actually "dataverseType". Acceptable values are
# DEPARTMENT, JOURNALS, LABORATORY, ORGANIZATIONS_INSTITUTIONS, RESEARCHERS,
# RESEARCH_GROUP, RESEARCH_PROJECTS, TEACHING_COURSES, UNCATEGORIZED. If
# "dataverseType" is missing or is not one of the above, it defaults to
# "Uncategorized".
json_fp = open("dataverse_metadata.json", "r")
dv_json_str = json.dumps(json.load(json_fp))
resp = api.create_dataverse(":root", dv_json_str)

# Create a nested dataverse, i.e. a dataverse within a dataverse
json_fp = open("nested_dataverse_metadata.json", "r")
dv_json_str = json.dumps(json.load(json_fp))
resp = api.create_dataverse("prog_dv", dv_json_str)

# Retrieve information from a dataverse
resp = api.get_dataverse("prog_dv")
resp.json()

# Create a dataset
ds = Dataset()
ds_filename = "hvtn_dataset_setup.json"
ds.from_json(read_file(ds_filename))
ds.validate_json()
resp = api.create_dataset("prog_dv", ds.json())
resp.json()

# Add a file to a dataset
df = Datafile()
df_json_fp = open("hvtn_files_upload.json", "r")
df_json_str = json.dumps(json.load(json_fp))
df_pid = "doi:10.70122/FK2/NAIM1N"
df_filename = "lanl_gag_seq.fasta"
resp = api.upload_datafile(df_pid, df_filename, df_json_str)
resp.json()
