"""

Program: create_variant_seqs.py

Purpose: Read in a variant table and a reference sequence, and use them to
         create a file of variant sequences.

Inputs: var_table_file (variant table)
        refseq_file (reference sequence file)
        out_file (output file)

Outputs: csv file

Execution: python3 create_variant_seqs.py <variant table file>
               <reference sequence file> <output file>

Note: The variant table file is expected to be a .csv file with the following
      format:
      Column 1: variant name/label
      Column 2: sequence position
      Column 3: reference value
      Column 4: variant value
"""

import argparse
import re
from csv import reader
from Bio import SeqIO

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("var_table_file", type=str,
                        help="Variant table file name")
    parser.add_argument("refseq_file", type=argparse.FileType("r"),
                        help="Reference sequence file name")
    parser.add_argument("out_file", type=argparse.FileType("w"),
                        help="Output file name")

    args = parser.parse_args()

    changes_dict = {}
    inserts_dict = {}
    nonvar_insert_dict = {}
    seq_dict = {}

    # Read the variant table into a dictionary with the variant name/label as
    # the key, pointing to a list of variant locations and changes for each
    # variant. Make sure to skip the first row since it is the header row.
    with open(args.var_table_file, "r") as vt:
        file_lines = reader(vt)
        skip_header = next(file_lines)

        if skip_header is not None:
            for val_list in file_lines:
                line_dict = {}
                variant_name = val_list.pop(0)
                line_dict["variant_pos"] = val_list.pop(0)
                line_dict["ref_val"] = val_list.pop(0)
                line_dict["variant_val"] = val_list.pop(0)

                if line_dict["ref_val"] == "+":
                    if variant_name not in inserts_dict:
                        inserts_dict[variant_name] = []
                    inserts_dict[variant_name].append(line_dict)
                    if line_dict["variant_pos"] not in nonvar_insert_dict:
                        nonvar_insert_dict[line_dict["variant_pos"]] = "-"
                else:
                    line_dict["variant_pos"] = int(line_dict["variant_pos"])
                    if variant_name not in changes_dict:
                        changes_dict[variant_name] = []
                    changes_dict[variant_name].append(line_dict)

    # Read in the reference sequence.
    ref_record = SeqIO.read(args.refseq_file, "fasta")
    ref_seq = str(ref_record.seq)
    seq_dict[ref_record.id] = list(ref_seq)

    # Process the changes (including deletions) first. Since Python is
    # 0-indexed, the position to be changed is one less than the position
    # listed for the variants in the file.
    for variant in changes_dict:
        seq_dict[variant] = list(ref_seq)
        for change_rec in changes_dict[variant]:
            seq_dict[variant][change_rec["variant_pos"] - 1] = change_rec["variant_val"]

    # Process the insertions. This is done as a separate step in order to
    # include the reference sequence in the processing.
    for seq in seq_dict:
        working_insert_dict = nonvar_insert_dict.copy()
        if seq in inserts_dict:
            for insert_rec in inserts_dict[seq]:
                working_insert_dict[insert_rec["variant_pos"]] = insert_rec["variant_val"]
        for insert_pos in sorted(working_insert_dict, reverse=True):
            int_pos = int(re.sub("[^\d]", "", insert_pos)) - 1
            seq_dict[seq].insert(int_pos, working_insert_dict[insert_pos])

        seq_dict[seq] = "".join(seq_dict[seq])
        args.out_file.write(f">{seq}\n")
        args.out_file.write(f"{seq_dict[seq]}\n")

    args.out_file.close()

if __name__ == "__main__":
    main()
