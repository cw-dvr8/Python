#!/usr/bin/env python3

"""
Program: synapse_folder_sizes.py

Purpose: Traverse a Synapse folder and determine the total size of the files
         it contains.

Input parameters: Root folder Synapse ID
                  Output file name

Outputs: csv file

Execution: synapse_folder_sizes.py <root folder Synapse ID>
               <output file>

"""

import argparse
import synapseclient
import synapseutils

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("folder_syn_id", type=str,
                        help="Root folder Synapse ID")
    parser.add_argument("output_file", type=argparse.FileType("w"),
                        help="Output .csv file (full path)")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    args.output_file.write("Synapse Folder, Total Size of Folder Files\n")

    total_file_size = 0

    syn_contents = synapseutils.walk(syn, args.folder_syn_id)
    for dirname, __, filelist in syn_contents:
        if len(filelist) > 0:
            dirsize = 0
            for __, syn_id in filelist:
                try:
                    file_handle = syn.restGET(f"/entity/{syn_id}/filehandles")
                except:
                    continue

                if "contentSize" in file_handle["list"][0].keys():
                    dirsize += file_handle["list"][0]["contentSize"]

            if dirsize > 0:
                total_file_size += dirsize

                args.output_file.write(f"{dirname[0]}, {dirsize}\n")


    args.output_file.write(f"Total size of {args.folder_syn_id} in bytes: {total_file_size}")

    args.output_file.close()


if __name__ == "__main__":
    main()
