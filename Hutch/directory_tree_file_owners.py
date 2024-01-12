#!/usr/local/apps/bin/python3

"""
Program: directory_tree_file_owners.py

Purpose: Traverse the specified directory tree and get the owners and
         modification dates of all of the subdirectories and files.

Input Parameters: Directory to traverse
                  Output file name

Outputs: csv file

Execution: directory_tree_file_owners.py <directory to traverse> <output file>

NOTE: This program flushes the buffer for every directory, and therefore should
      be used when the directory to be inventoried is very large in order to
      avoid memory issues.

"""

import argparse
from csv import DictWriter
from datetime import datetime
import getpass
import os
import subprocess

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('dir_tree_root', type=str, help='Directory tree root')
    parser.add_argument('output_file', type=argparse.FileType('w'),
                        help='Output .csv file')

    args = parser.parse_args()

    # Create a list of subdirectories that the program should ignore.
    EXCLUDE_DIRS = set(['.snapshot', '.svn'])
    COLUMN_LIST = ['directory', 'file', 'owner', 'mod_date', 'file_size_bytes']

    file_object = DictWriter(args.output_file, fieldnames=COLUMN_LIST)
    for (root, dirs, files) in os.walk(args.dir_tree_root, topdown=True):
        catalog_entry_dict = {}
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
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
        file_object.writerow(catalog_entry_dict)

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
                    file_object.writerow(catalog_entry_dict)

        args.output_file.flush()
        os.fsync(args.output_file.fileno())

    args.output_file.close()

if __name__ == '__main__':
    main()
