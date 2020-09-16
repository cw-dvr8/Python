#!/usr/bin/env python3

"""
Program: move_files_in_synapse.py

Purpose: Move files from one Synapse folder to another.

"""

import argparse
import synapseclient
import synapseutils


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("current_folder_synid", type=str,
                        help="Synapse ID of the folder where the files currently reside")
    parser.add_argument("new_folder_synid", type=str,
                        help="Synapse ID of the folder where the files should be moved")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Get the full list of files from the original Synapse folder.
    syn_contents = synapseutils.walk(syn, args.current_folder_synid)
    for __, __, filelist in syn_contents:
        for __, syn_id in filelist:

            # Move the file to the destination.
            syn.move(syn_id, args.new_folder_synid)

if __name__ == "__main__":
    main()
