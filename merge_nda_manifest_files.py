#!/usr/bin/env python3

"""
Program: merge_nda_manifest_files.py

Purpose: Merge NDA manifest files in the current directory that contain the specified string
         together into the specified file.

Input parameters: String in the file names to look for
                  Output file name

Outputs: Output file

Execution: merge_nda_manifest_files.py <file string> <output file>
"""

import argparse
import glob
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file_string", type=str,
                        help="String to search for in the file name")
    parser.add_argument("output_file", type=argparse.FileType('w'), 
                        help="Name of the output file")

    args = parser.parse_args()

    file_search_string = f"*{args.file_string}*"
    file_list = glob.glob(file_search_string)

    if len(file_list) == 0:
        raise Exception(f'No files in this directory contain the string "{args.file_string}"')
    else:
        print(file_list)

    # NDA manifest files contain two header lines:
    #
    # <NDA manifest type> <NDA manifest file version>
    # <column label 1>, <column label 2>, etc.
    #
    # Set a flag that will indicate whether the header line has already been written
    # to the output file.
    header_line = False

    for file_name in file_list:
        with open(file_name) as source_file:

            if header_line:
                next(source_file)
                next(source_file)
            else:
                header_line = True

            for line in source_file:
                args.output_file.write(line)

        source_file.close()

    args.output_file.close()

if __name__ == "__main__":
    main()
