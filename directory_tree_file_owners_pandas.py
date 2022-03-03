#!/usr/local/apps/bin/python3

"""
Program: directory_tree_file_owners.py

Purpose: Traverse the specified directory tree and get the owners and
         modification dates of all of the subdirectories and files.

Input Parameters: Directory to traverse
                  Output file name

Outputs: csv file

Execution: directory_tree_file_owners.py <directory to traverse> <output file>

NOTE: This version of the program uses dataframes to build the inventory. It
      may run into memory issues if the directory to be inventoried is very
      large.

"""

import argparse
from datetime import datetime
import getpass
import os
import subprocess
import pandas as pd

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('dir_tree_root', type=str, help='Directory tree root')
    parser.add_argument('output_file', type=argparse.FileType('w'),
                        help='Output .csv file')

    args = parser.parse_args()

    catalog_df = pd.DataFrame()
    catalog_entry_dict = {}

    # Create a list of subdirectories that the program should ignore.
    exclude_dirs = set(['.snapshot', '.svn'])

    for (root, dirs, files) in os.walk(args.dir_tree_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        dir_stat = os.stat(root)
        process_output = subprocess.run(['getent', 'passwd', str(dir_stat.st_uid)], capture_output=True, text=True)
        if process_output.returncode == 0:
            user_name = process_output.stdout.split(':')[4]
        else:
            user_name = 'username unavailable'
        mod_date = datetime.fromtimestamp(dir_stat.st_mtime).date()

        # Write the directory out on its own line.
        catalog_entry_dict['directory'] = root
        catalog_entry_dict['file'] = ''
        catalog_entry_dict['owner'] = user_name
        catalog_entry_dict['mod_date'] = mod_date
        catalog_entry_dict['file_size_bytes'] = None
        catalog_df = catalog_df.append(catalog_entry_dict, ignore_index=True)

        if files:
            for f in files:
                full_file_path = f'{root}/{f}'

                # Make sure the file is a file and not a symlink because
                # the program will error out on symlinked files.
                if os.path.isfile(full_file_path):
                    file_stat = os.stat(full_file_path)
                    process_output = subprocess.run(['getent', 'passwd', str(file_stat.st_uid)], capture_output=True, text=True)
                    if process_output.returncode == 0:
                        user_name = process_output.stdout.split(':')[4]
                    else:
                        user_name = 'username unavailable'
                    mod_date = datetime.fromtimestamp(file_stat.st_mtime).date()
                    catalog_entry_dict['file'] = f
                    catalog_entry_dict['owner'] = user_name
                    catalog_entry_dict['mod_date'] = mod_date
                    catalog_entry_dict['file_size_bytes'] = file_stat.st_size
                    catalog_df = catalog_df.append(catalog_entry_dict, ignore_index=True)

    catalog_df.to_csv(args.output_file, index=False)
    args.output_file.close()

if __name__ == '__main__':
    main()
