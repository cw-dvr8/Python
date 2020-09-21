#!/usr/bin/env python3

"""
Program: change_download_as.py

Purpose: Change the file metadata in the designated Synapse folder such that
         the 'Download file as' name matches the 'Synapse name'.

Execution: change_download_as.py <SynID of folder containing the files>

Note: This program only modifies files residing in the folder specified. It
      does not modify files that might be in any sub-folders.

"""

import argparse
import synapseclient
import synapseutils


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("folder_synid", type=str,
                        help="Synapse ID of the folder containing the files with metadata to be modified")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Get the full list of files from the original Synapse folder.
    syn_contents = synapseutils.walk(syn, args.folder_synid)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:

            # Move the file to the destination.
            syn_file = syn.get(syn_id, downloadFile=False)
            syn_file = synapseutils.changeFileMetaData(syn, syn_file, syn_file['name'])

        break

if __name__ == "__main__":
    main()
