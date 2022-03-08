"""
Program: change_ptid_to_pubid.py

Purpose: Get the PUBID from a look-up table and use it to replace
         the PTID in a data file.

Input parameters: Look-up file name
                  Data file name
                  Output file name

Outputs: Tab-delimited text file

Execution: python change_ptid_to_pubid.py <look-up file>
               <data file> <output file>

"""

import argparse
import pandas as pd

"""
Function: main
"""
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("lookup_file", type=argparse.FileType("r"),
                        help="Look-up file")
    parser.add_argument("data_file", type=argparse.FileType("r"),
                        help="Data file")
    parser.add_argument("out_file", type=argparse.FileType("w"),
                        help="Output file")

    args = parser.parse_args()

    lookup_df = pd.read_csv(args.lookup_file)
    ids_df = lookup_df[["ptid", "pubid"]].copy()
    ids_df["ptid"] = ids_df["ptid"].str.replace("-", "")
    ids_df =ids_df.rename(columns={"ptid": "PTID", "pubid": "PUBID"})

    data_df = pd.read_csv(args.data_file, sep="\t")
    data_df["PTID"] = data_df["PTID"].astype(str)

    combined_df = pd.merge(data_df, ids_df, how="left", on="PTID", indicator=True)
    column_list = combined_df.columns.values.tolist()
    column_list.remove("PUBID")
    column_list.remove("_merge")
    new_column_list = ["PUBID" if header == "PTID" else header for header in column_list]
    combined_df = combined_df[new_column_list]

    combined_df.to_csv(args.out_file, sep="\t", index=False)

    no_pubid_df = combined_df.loc[combined_df["PUBID"] == ""]
    if len(no_pubid_df) > 0:
        print("PTIDs without PUBIDs\n")
        print(no_pubid_df["PTID"])

if __name__ == "__main__":
    main()
