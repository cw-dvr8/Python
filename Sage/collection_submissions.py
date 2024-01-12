#!/usr/bin/env python3

"""
Program: collection_submissions.py

Purpose: Get the completed submissions for each BSMN NDA collection.

Input parameters: File containing the user's NDA credentials (full path)
                  Output file name
                  Optional Synapse ID of the table containing the collection
                      ID. The default is syn10802969 (Grant Data Summaries)
                  Optional column name containing the collection ID. The
                      default is "nda collection".

Outputs: csv file

Notes: This script expects the user to have login credentials for Synapse.

Execution: collection_submissions.py <NDA credentials file> <output file>
               --synapse_id <Synapse ID> --column_name <column name>
"""

import argparse
import json
import logging
import pandas as pd
import requests
import synapseclient
import sys
sys.path.insert(0, "/home/cmolitor/bsmn_validation/develop_ndasynapse")
import ndasynapse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Synapse ID of the Grant Data Summaries table
COLLECTION_ID_LOCATION = "syn10802969"
COLLECTION_ID_COLUMN = "nda collection"

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("nda_credentials", type=argparse.FileType('r'), 
                        help="File containing NDA user credentials (full path)")
    parser.add_argument("out_file", type=argparse.FileType('w'), 
                        help="Output .csv file (full path)")
    parser.add_argument("--synapse_id", type=str, default=COLLECTION_ID_LOCATION,
                        help="Synapse ID for the entity containing the collection ID")
    parser.add_argument("--column_name", type=str, default=COLLECTION_ID_COLUMN,
                        help="Column containing the collection ID")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    config = json.load(args.nda_credentials)

    # If the file containing the NDA credentials file has other sections,
    # grab the one for the 'nda' entry.
    if 'nda' in config.keys():
        config = config['nda']

    syn_table_query = f'SELECT distinct "{args.column_name}" from {args.synapse_id}'

    try:
        table_results_df = syn.tableQuery(syn_table_query).asDataFrame()
    except Exception as syn_query_error:
        raise syn_query_error

    # The link to the NDA collection will have a format similar to
    # https://ndar.nih.gov/edit_collection.html?id=<NDA collection ID>
    collection_id_list = (table_results_df[args.column_name].str.split("=", n=1).str[1]).tolist()
    logger.debug(collection_id_list)

    args.out_file.write("collection_id, submission_id, file_user_path, size, md5sum, file_remote_path\n")

    for coll_id in collection_id_list:

        # The NDASubmission class returns a list of dictionaries, with each dictionary
        # including the file content (['files']), the collection ID (['collection_id']),
        # and the submission ID (['submission_id']).
        submission_file_list = ndasynapse.nda.NDASubmission(config, collection_id=coll_id).submission_files

        for list_entry in submission_file_list:
            for assoc_file in list_entry['files'].associated_files:
                args.out_file.write(f"{coll_id}, {list_entry['submission_id']}, \
                                      {assoc_file['name']['file_user_path']}, {assoc_file['name']['size']}, \
                                      {assoc_file['name']['md5sum']}, \
                                      {assoc_file['name']['file_remote_path']}\n")

    args.out_file.close()

if __name__ == "__main__":
    main()
