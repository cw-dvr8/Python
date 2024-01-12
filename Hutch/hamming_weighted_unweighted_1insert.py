"""
Program: hamming_weighted_unweighted_1insert.py

Purpose: Calculate the weighted and unweighted Hamming distances between
         viral lineages and vaccines with one insert.

Input parameters: Fasta file containing the lineage sequences
                  Fasta file containing the vaccine sequences
                  File containing the AA weighted Hamming distances
                  Output file

Ouptputs: File with one line per lineage containing the weighted and
          unweighted Hamming distances for each vaccine.

Execution: python hamming_weighted_unweighted_1insert.py <lineage seq file>
           <vaccine seq file> <AA weights file> <output file>

Notes: 1) The AA weighted Hamming distances file should be a csv matrix with
          one row for each amino acid and one column for each amino acid, with
          the Hamming distance for each pair at the intersection.
       2) Do not use this program for vaccines with more than one insert, as
          those require different calculations.
"""

import argparse
import pandas as pd
from Bio import SeqIO

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("lineage_fp", type=argparse.FileType("r"),
                        help="Lineage sequence file")
    parser.add_argument("vaccine_fp", type=argparse.FileType("r"),
                        help="Vaccine sequence file")
    parser.add_argument("weights_fp", type=argparse.FileType("r"),
                        help="Weighted Hamming distance file")
    parser.add_argument("outfile_fp", type=argparse.FileType("w"),
                        help="Output file")

    args = parser.parse_args()

    lin_dist_df = pd.DataFrame()
    lin_dict_list = []
    vacc_dict = {}

    # Read in the weighted Hamming distance table.
    hamming_table_df = pd.read_csv(args.weights_fp)

    # Read in the vaccine sequences.
    for vacc_rec in SeqIO.parse(args.vaccine_fp, "fasta"):
        vacc_dict[vacc_rec.id] = list(str(vacc_rec.seq))

    # Read in the lineage sequences and compare them to the vaccine sequences to
    # calculate the weighted and unweighted Hamming distances.
    for lin_rec in SeqIO.parse(args.lineage_fp, "fasta"):
        lin_seq = list(str(lin_rec.seq))
        lin_dict = {}
        lin_dict["Lineage"] = lin_rec.id
        lin_seq_length = len(lin_seq)

        for vaccine in vacc_dict:
            vacc_seq = vacc_dict[vaccine]
            vacc_seq_length = len(vacc_seq)

            # If the lineage and vaccine sequences are different lengths, only
            # do comparisons for the length of the shorter sequence.
            compare_length = lin_seq_length if lin_seq_length < vacc_seq_length else vacc_seq_length

            lin_dict[f"{vaccine} Hamming distance (weighted)"] = 0
            lin_dict[f"{vaccine} Hamming distance (unweighted)"] = 0

            for i in range(compare_length):
                if lin_seq[i] != vacc_seq[i]:
                    lin_dict[f"{vaccine} Hamming distance (unweighted)"] += 1

                    weighted_dist = hamming_table_df.loc[hamming_table_df["aa1"] == lin_seq[i], vacc_seq[i]].values[0]
                    lin_dict[f"{vaccine} Hamming distance (weighted)"] += weighted_dist

#                    print(f"{lin_rec.id} {vaccine} {lin_seq[i]} {vacc_seq[i]}: {weighted_dist}")

        lin_dict_list.append(lin_dict)

    lin_dist_df = pd.DataFrame.from_records(lin_dict_list)

    lin_dist_df.to_csv(args.outfile_fp, index=False)
    args.outfile_fp.close()

if __name__ == "__main__":
    main()
