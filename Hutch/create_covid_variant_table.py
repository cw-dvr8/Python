"""

Program: create_covid_variant_table.py

Purpose: Read a spreadsheet of variant mutations and create a table for each
         variant containing the variant name, the position of the mutation,
         the reference amino acid at that position, and the variant amino
         acid at that position.

Inputs: None

Outputs: csv file

Execution: python3 create_covid_variant_table.py

Note: The spreadsheet of variant mutations needs some hand editing because
      the WHO labels often contain non-ASCII characters (i.e. Greek letters)
      and some of the variants are not labeled as baseline. The following
      needs to be done to the spreadsheet before this program can be run:

      1) The WHO label must be edited to contain the exact value desired in
         the output csv file, and all Greek letters and other non-ASCII
         characters must be removed.
      2) A column named "Process" must be added to the spreadsheet, and must
         contain the letter "Y" for all of the rows that should be processed
         by this program.
"""

import re
import pandas as pd

def main():
    IN_FILE = "/compbio/projects/cindy/covid_variant_table/data/Variants_Table_2022-02-22_designated_rows.xlsx"
    OUT_FILE = "/compbio/projects/cindy/covid_variant_table/adata/COVID_variant_table_20220314.csv"

    variant_file = open(IN_FILE, "rb")
    variant_spreadsheet_df = pd.read_excel(variant_file)

    vtable_file = open(OUT_FILE, "w")
    vtable_file.write("WHOLabel,position,refAA,variantAA\n")

    # The columns of interest in this spreadsheet are columns 3 - 6 (2 - 5 in
    # Python since the numbering starts at 0).
    # column 3 - WHO designation
    # column 4 - Most common Pango lineage designation for the form of Spike
    # column 5 - Most common Spike backbones of variant form
    # column 6 - An indicator I added to the spreadsheet to designame the
    #            rows that I want to process (contains a Y for the desired rows)
    variant_df = variant_spreadsheet_df.iloc[:, 2:6]

    baseline_row_df = variant_df.loc[variant_df.iloc[:, 3] == "Y"].copy()
    baseline_row_df["variant_list"] = baseline_row_df.iloc[:, 2].str.split(",")

    for index, row in baseline_row_df.iterrows():
        for variant in row["variant_list"]:
            variant_label = re.sub(r"[^A-Za-z0-9 _]+", "", row[0])
            variant = variant.replace(" ", "")
            variant_pos = re.sub("\D", "", variant)
            ref_aa = variant[0]
            variant_aa = re.sub("\d", "", variant[1:])

            # For insertions, the mutation position should be augmented with
            # a descending lower-case alphabetic character, e.g. "67a",
            # "143c". If there is more than one insertion, each once should
            # be on its own line.
            if ref_aa == '+':
                pos_letter = "a"
                for insert_pos in range(0, len(variant_aa)):
                    vtable_file.write(f"{variant_label},{variant_pos}{pos_letter},{ref_aa},{variant_aa[insert_pos]}\n")
                    pos_letter = chr(ord(pos_letter) + 1)
            else:
                vtable_file.write(f"{variant_label},{variant_pos},{ref_aa},{variant_aa}\n")

    vtable_file.close()

if __name__ == "__main__":
    main()
