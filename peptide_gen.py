"""
Program: peptide_gen.py

Purpose: Create an Excel spreadsheet containing peptides generated from
         sequence files, with an indicator as to whether they match
         the peptide in the same position in a reference sequence.
         The sequence and the reference sequence can be in either
         two different files, or one file containing both.

Input parameters: Length of peptide
                  Peptide overlap
                  Output file name (.xlsx)
                  Sequence file name
                  single_file parameters: reference sequence ID
                  two_files parameters: reference sequence file name

Outputs: Excel file

Execution (single file): python peptide_gen.py -length <length> -overlap <overlap>
                         -out_file <output file name>
                         -seq_file <sequence file name> single_file
                         -refseq <reference sequence ID>

Execution (two files): python peptide_gen.py -length <length> -overlap <overlap>
                       -out_file <output file name>
                       -seq_file <sequence file name> two_files
                       -ref_file <reference sequence file name>
"""

import argparse
from Bio import SeqIO
import pandas as pd

def create_peptides(pep_length, pep_overlap, pep_file, ref_record, comp_record_list):

    """
    Function: create_peptides

    Purpose: Create peptides from the reference and target sequence and
             compare them to find the new peptides in the target
             sequence.

    Inputs: pep_length - desired peptide length
            pep_overlap - desired peptide overlap
            pep_file - output file
            ref_record - reference sequence record, generated either from a SeqIO.read
                         call or an iteration of a SeqIO.parse call
            comp_record_list - target sequence records

    Outputs: Excel file
    """

    peptide_df = pd.DataFrame()
    start_pos_increment = pep_length - pep_overlap

    ref_id = ref_record.id
    ref_seq = str(ref_record.seq)
    for comp_record in comp_record_list:
        comp_id = comp_record.id
        comp_seq = str(comp_record.seq)
        comp_newpeptide_string = comp_id + " New Peptide"

        peptide_dict_list = []
        start_pos = 1
        length_remaining = len(ref_seq)
        current_pos = 0
        ref_counter = 0
        comp_counter = 0
        end_of_sequence = False

        while not end_of_sequence:
            peptide_dict = {}
            new_ref_peptide = ""
            new_comp_peptide = ""
            num_residues = 0

            # If the length of the sequence at the current position is less than
            # the desired sequence length, start at the end of the sequence and
            # backtrack to create the peptide until it is the desired length,
            # and then set the loop controller to True. Note that only the
            # length of the reference sequence is checked because the target
            # sequence has been aligned to the reference sequence.

            if len(ref_seq[current_pos :]) < pep_length:
                num_residues = 0
                for c in reversed(ref_seq):
                    if c.isalpha():
                        new_ref_peptide = c + new_ref_peptide
                        num_residues += 1

                    if num_residues == pep_length:
                        break

                num_residues = 0
                for c in reversed(ref_seq):
                    if c.isalpha():
                        new_comp_peptide = c + new_comp_peptide
                        num_residues += 1

                    if num_residues == pep_length:
                        break

                start_pos = ((start_pos - start_pos_increment)
                             + (pep_length - len(ref_seq[current_pos :].replace("-", ""))))
                end_of_sequence = True

            else:
                # Construct the peptides beginning at the current position. If
                # there are gaps, continue past them to the next residue.

                while num_residues < pep_length:
                    if ref_seq[ref_counter].isalpha():
                        new_ref_peptide = new_ref_peptide + ref_seq[ref_counter]
                        ref_counter += 1
                    else:
                        while not ref_seq[ref_counter].isalpha():
                            ref_counter += 1
                        new_ref_peptide = new_ref_peptide + ref_seq[ref_counter]
                        ref_counter += 1

                    if comp_seq[comp_counter].isalpha():
                        new_comp_peptide = new_comp_peptide + comp_seq[comp_counter]
                        comp_counter += 1
                    else:
                        while not comp_seq[comp_counter].isalpha():
                            comp_counter += 1
                        new_comp_peptide = new_comp_peptide + comp_seq[comp_counter]
                        comp_counter += 1

                    num_residues += 1

            # Create a dictionary structure for the peptide information and then
            # append it to a list of dictionaries. This list will be used later
            # to create a pandas dataframe because it is easier to dump an
            # Excel file from pandas.

            peptide_dict["Start Position"] = start_pos
            peptide_dict["Stop Position"] = start_pos + (pep_length - 1)
            peptide_dict[ref_id] = new_ref_peptide
            peptide_dict[comp_id] = new_comp_peptide
            if new_comp_peptide == new_ref_peptide:
                peptide_dict[comp_newpeptide_string] = ""
            else:
                peptide_dict[comp_newpeptide_string] = "new peptide"
            peptide_dict_list.append(peptide_dict)

            # If the length of the reference sequence at the current position
            # (excluding gaps) is the desired peptide length, set the loop
            # controller to True.

            if len(ref_seq[current_pos :].replace("-", "")) == pep_length:
                end_of_sequence = True
            else:

                # Get the next peptide starting positions if there are no insertions.
                if ref_seq.count("-", current_pos, current_pos + start_pos_increment) == 0:
                    ref_counter = current_pos + start_pos_increment

                    # If the first character in the next peptide for the target sequence
                    # is a gap, figure out how many gaps there are and then back up the
                    # start.
                    if comp_seq[current_pos + start_pos_increment] == '-':
                        start_gaps = 0
                        while comp_seq[current_pos + start_pos_increment + start_gaps] == '-':
                            start_gaps += 1

                        backtrack_pos = current_pos + start_pos_increment
                        while start_gaps > 0:
                            backtrack_pos -= 1
                            if comp_seq[backtrack_pos].isalpha():
                                start_gaps -= 1

                        comp_counter = backtrack_pos

                    else:
                        comp_counter = current_pos + start_pos_increment

                    current_pos = current_pos + start_pos_increment

                # If there are insertions within the span of the next peptide, figure out
                # where to skip to.
                else:
                    non_overlap_residues = 0
                    while (non_overlap_residues < start_pos_increment) or (ref_seq[current_pos] == '-'):
                        if ref_seq[current_pos].isalpha():
                            non_overlap_residues += 1 
                        current_pos += 1

                    ref_counter = current_pos
                    comp_counter = current_pos

                start_pos = start_pos + start_pos_increment

        # Create a dataframe of the peptides and then dump it to an Excel file.
        # I am creating the dataframe from a list of dictionaries instead of
        # appending to a dataframe as I go because the dataframe append
        # method has been deprecated and this is the easiest way I have
        # found to replace that functionality. It is also easier to write
        # an Excel file from pandas than it is to write it as I go.

        peptide_dict_df = pd.DataFrame()
        peptide_dict_df = pd.DataFrame.from_records(peptide_dict_list)

        if peptide_df.empty:
            peptide_df = peptide_dict_df.copy()
        else:
            peptide_dict_df.drop([ref_id], axis=1, inplace=True)
            peptide_df = pd.merge(peptide_df, peptide_dict_df, how="left", on=["Start Position", "Stop Position"])

    peptide_df.to_excel(pep_file, sheet_name="Peptides", index=False)
    pep_file.close()

def process_single_file(args):

    """
    Function: process_single_file

    Purpose: Read through the sequences contained in a single file,
             determine which is the reference and which is the target,
             and call the create_peptides function. Note that this
             program currently does not handle files with multiple
             target sequences.

    Inputs: args - object containing the arguments passed into the
                   program
    """

    comp_record_list = []

    for seq_record in SeqIO.parse(args.seq_file, "fasta"):
        if seq_record.id == args.refseq_id:
            ref_record = seq_record
        else:
            comp_record_list.append(seq_record)

    create_peptides(args.length, args.overlap, args.out_file, ref_record, comp_record_list)

def process_two_files(args):

    """
    Function: process_two_files

    Purpose: Read in the fasta file containing the reference sequence
             and the fasta file containing the target sequence, and
             call the create_peptides function. Note that this
             program currently does not handle files with multiple
             target sequences.

    Inputs: args - object containing the arguments passed into the
                   program
    """

    comp_record_list = []

    ref_record = SeqIO.read(args.ref_file, "fasta")
    for seq_record in SeqIO.parse(args.seq_file, "fasta"):
        comp_record_list.append(seq_record)

    create_peptides(args.length, args.overlap, args.out_file, ref_record, comp_record_list)

"""
Function: main
"""
def main():

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-length", type=int, default=None, required=True,
                               help="Peptide length")
    parent_parser.add_argument("-overlap", type=int, default=None, required=True,
                               help="Peptide overlap")
    parent_parser.add_argument("-out_file", type=argparse.FileType("wb"), required=True,
                               help="Output file")
    parent_parser.add_argument("-seq_file", type=argparse.FileType("r"), required=True,
                               help="Input sequence fasta file")

    parser = argparse.ArgumentParser(parents=[parent_parser], add_help=True)

    subparsers = parser.add_subparsers(dest="cmd", description="subparser description")

    parser_single_file = subparsers.add_parser("single_file", help="Process single file",
                                               description="subparser description")
    parser_single_file.add_argument("-refseq_id", type=str, required=True,
                                    help="Reference sequence")
    parser_single_file.set_defaults(func=process_single_file)

    parser_two_files = subparsers.add_parser("two_files", help="Process two files",
                                             description="subparser description")
    parser_two_files.add_argument("-ref_file", type=argparse.FileType("r"), required=True,
                                  help="Input reference sequence fasta file")
    parser_two_files.set_defaults(func=process_two_files)

    args = parser.parse_args()

    args.func(args)

if __name__ == "__main__":
    main()
