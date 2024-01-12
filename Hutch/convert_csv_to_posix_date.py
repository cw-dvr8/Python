"""
Program Name: convert_csv_to_posix_date.py

Purpose: Convert the dates in the specified columns to POSIX dates.

Input Parameters: Input csv file
                  Output csv file
                  number(s) of the column(s) to be converted

Execution: convert_csv_to_posix_date.py <input file name> <output file name>
               <number(s) of column(s) to be converted>

"""

import argparse
import datetime as dt
import numpy as np
import pandas as pd

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", type=argparse.FileType('r'),
                        help="Input csv file")
    parser.add_argument("out_file", type=argparse.FileType('w'),
                        help="Output csv file")
    parser.add_argument("column_numbers", type=int, nargs="+",
                        help="Number(s) of the column(s) to be converted")

    args = parser.parse_args()

    infile_df = pd.read_csv(args.in_file)

    for colnum in args.column_numbers:
        infile_df.iloc[:,colnum] = pd.to_datetime(infile_df.iloc[:,colnum])
        infile_df.iloc[:,colnum] = np.round((infile_df.iloc[:,colnum] - dt.datetime(1970,1,1)).dt.total_seconds())

    infile_df.to_csv(args.out_file, index=False, line_terminator='\r\n')

if __name__ == "__main__":
    main()
