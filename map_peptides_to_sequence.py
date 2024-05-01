"""
Program: map_peptides_to_sequence.py

Purpose: Create a position map for a list of peptides to the unaligned
         sequence that they originate from.

Input parameters: See the docstring in the main() module.

Outputs: Output file containing the peptides with start and end positions
         relative to the sequence that they originated from.

Execution: See the docstring in the main() module.

Notes:

"""

import os
from Bio import SeqIO
import click
import pandas as pd

@click.command()
@click.argument("pep_fp", type=click.File("r"))
@click.argument("pep_file_sep", type=str)
@click.argument("pep_seq_col", type=str)
@click.argument("seq_fp", type=click.File("r"))
@click.argument("out_fp", type=click.File("w"))
def main(pep_fp, pep_file_sep, pep_seq_col, seq_fp, out_fp):
    """
    \b
    Purpose: Create a position map for a list of peptides to the unaligned
             sequence that they originate from.

    \b
    Input parameters: Peptide file name, including full path
                      Peptide file separator - tabs must be passed in using $'\\t'
                      Peptide sequence column name in the peptide file - names
                          with spaces must be surrounded in quotes
                      File containing the unaligned originating sequence
                      New peptide output file

    \b
    Execution (in-alignment):
        python map_peptides_to_sequence.py <peptide file> <peptide file separator>
            <pep_seq_col> <sequence fasta file> <output file>
    NOTE: Do not include the angle brackets with the parameters

    NOTE: The originating sequence should not have any gaps.

    """

    seq_record = SeqIO.read(seq_fp, "fasta")
    seq = str(seq_record.seq)

    pep_df = pd.read_csv(pep_fp, sep=pep_file_sep)
    pep_list = pep_df[pep_seq_col].tolist()
    pep_noseq_list = []
    pep_pos_dict = {}

    for pep in pep_list:
        pep_length = len(pep)
        pep_start_pos = None

        for i in range(len(seq)):
            # Check that the remaining length of the sequence is less than or
            # equal to the length of the peptide.
            if pep_length <= len(seq[i:]):
                if seq[i : i + pep_length] == pep:
                    # Remember that Python is 0-based and we need the
                    # peptide position to be 1-based.
                    pep_start_pos = i + 1
                    break

        if pep_start_pos is None:
            pep_noseq_list.append(pep)
        else:
            pep_pos_dict[pep_start_pos] = pep

    if pep_pos_dict:
        pep_keys = list(pep_pos_dict.keys())
        pep_keys.sort()
        sorted_pep_pos_dict = {k: pep_pos_dict[k] for k in pep_keys}
        out_fp.write("peptide,peptide_pos")
        for pkey in pep_keys:
            out_fp.write(f"\n{sorted_pep_pos_dict[pkey]},{pkey}")

        out_fp.close()

    if pep_noseq_list:
        inpep_filename = os.path.basename(pep_fp.name)
        inpep_basename = os.path.splitext(os.path.basename(pep_fp.name))[0]
        inseq_filename = os.path.basename(seq_fp.name)
        outfile_dir = os.path.dirname(out_fp.name)
        outfile_name = f"{outfile_dir}/{inpep_basename}_problem_peptides.csv"
        problem_fp = open(outfile_name, "w")
        problem_fp.write(f"Peptides from {inpep_filename} not found in sequence fasta file {inseq_filename}\n")
        error_df = pep_df.loc[pep_df[pep_seq_col].isin(pep_noseq_list)]
        error_df.to_csv(problem_fp, index=False)

        problem_fp.close()


if __name__ == "__main__":
    main()
