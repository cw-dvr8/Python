"""
Program: gen_protein_seqs.py

Purpose: Take a full sequence and use a protein region to create a sequence
         that reflects the protein region.

Input parameters: File containing the full sequences
                  File containing sequences of the protein region
                  Name of the protein of interest

Outputs: Fasta file containing protein region sequences

Execution: python gen_protein_seqs.py <sequence file> <protein region file>
           <protein>

Note: The output file is written to the same directory as the input sequence
      file, and the name of the file is the name of the sequence file with
      the protein appended to it.
"""

import argparse
import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("seq_file", type=argparse.FileType("r"),
                        help="Sequence file")
    parser.add_argument("region_file", type=argparse.FileType("r"),
                        help="Protein region file")
    parser.add_argument("protein", type=str, help="Desired protein")

    args = parser.parse_args()

    region_rec_list = []

    protein_found = False
    for seq_rec in SeqIO.parse(args.region_file, "fasta"):
        if seq_rec.id == args.protein:
            protein_found = True
            protein_seq = str(seq_rec.seq)

            start_pos = re.search(r"[A-Z]", protein_seq).start()

            # The regex finditer method finds each occurence of the desired
            # string. The following code cycles through all of the alphabetic
            # characters in the sequence. When the loop ends, the aa_match
            # object contains the information for the last character in the
            # sequence.
            for aa_match in re.finditer(r"[A-Z]", protein_seq):
                pass
            end_pos = aa_match.start()

    if protein_found:
        output_file = f"{args.seq_file.name.replace('.fasta', '')}_{args.protein}.fasta"
        with open(output_file, "w") as out_seq_file:
            for seq_rec in SeqIO.parse(args.seq_file, "fasta"):
                full_seq = str(seq_rec.seq)
                seq_region = full_seq[start_pos: end_pos + 1]
                region_rec = SeqRecord(Seq(seq_region), id=seq_rec.id, description="")
                region_rec_list.append(region_rec)

            SeqIO.write(region_rec_list, output_file, "fasta")

    else:
        print(f"Protein {args.protein} not found in {args.region_file.name}")

if __name__ == "__main__":
    main()
