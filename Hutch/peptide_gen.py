"""
Program: peptide_gen.py

Purpose: Create Excel spreadsheets containing peptides generated from sequence
         files, with an indicator as to whether they match the peptide in the
         same position in a reference sequence.  The sequence and the reference
         sequence can be in either two different files, or one file containing
         both.  One spreadsheet will contain the peptides generated from all of
         the sequences, and the other will consolidate the peptides into a
         single column with another column indicating which sequences contain
         them.

Input parameters: See the docstring in the main() module.

Outputs: Excel files

Execution: See the docstring in the main() module.

"""

from Bio import SeqIO
import click
import pandas as pd

def create_peptides(pep_length, pep_overlap, pep_file_root, ref_record, comp_record_list):

    """
    Function: create_peptides

    Purpose: Create peptides from the reference and target sequence and
             compare them to find the new peptides in the target
             sequence.

    Inputs: pep_length - desired peptide length
            pep_overlap - desired peptide overlap
            pep_file_root - output file root name
            ref_record - reference sequence record, generated either from a SeqIO.read
                         call or an iteration of a SeqIO.parse call
            comp_record_list - target sequence records

    Outputs: Excel files
    """

    output_fp = open(f"{pep_file_root}.xlsx", "wb")
    consolidated_output_fp = open(f"{pep_file_root}_consolidated.xlsx", "wb")

    peptide_df = pd.DataFrame()
    consolidated_peptide_dict = {}
    start_pos_increment = pep_length - pep_overlap

    valid_aa_codes = set("ACDEFGHIKLMNPQRSTVWY-")

    ref_id = ref_record.id
    ref_seq = str(ref_record.seq).replace("*", "")

    # Stop execution if there are any invalid amino acid codes in the reference
    # sequence.
    code_compare = list(set(ref_seq) - valid_aa_codes)
    if code_compare:
        print(f"\nInvalid AA codes in reference sequence: {code_compare}\n")
        raise SystemExit(0)

    for comp_record in comp_record_list:
        comp_id = comp_record.id
        comp_seq = str(comp_record.seq).replace("*", "")

        # Stop execution if there are any invalid amino acid codes in the
        # comparison sequence.
        code_compare = list(set(comp_seq) - valid_aa_codes)
        if code_compare:
            print(f"\nInvalid AA codes in reference sequence {comp_id}: {code_compare}\n")
            raise SystemExit(0)

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

            if start_pos not in consolidated_peptide_dict:
                consolidated_peptide_dict[start_pos] = {}

            if new_ref_peptide not in consolidated_peptide_dict[start_pos]:
                consolidated_peptide_dict[start_pos][new_ref_peptide] = {}
                consolidated_peptide_dict[start_pos][new_ref_peptide]["in_seqs"] = ref_id

            if new_comp_peptide not in consolidated_peptide_dict[start_pos]:
                consolidated_peptide_dict[start_pos][new_comp_peptide] = {}
                consolidated_peptide_dict[start_pos][new_comp_peptide]["in_seqs"] = comp_id
            else:
                consolidated_peptide_dict[start_pos][new_comp_peptide]["in_seqs"] = f"{consolidated_peptide_dict[start_pos][new_comp_peptide]['in_seqs']}|{comp_id}"
                

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

    peptide_df.to_excel(output_fp, sheet_name="Peptides", index=False)
    output_fp.close()

    consolidated_peptide_list = []
    for start_pos in consolidated_peptide_dict:
        for peptide in consolidated_peptide_dict[start_pos]:
            peptide_dict = {}
            peptide_dict["Start Position"] = start_pos
            peptide_dict["Stop Position"] = start_pos + (pep_length - 1)
            peptide_dict["Peptide"] = peptide
            peptide_dict["Contained In"] = consolidated_peptide_dict[start_pos][peptide]["in_seqs"]
            consolidated_peptide_list.append(peptide_dict)

    consolidated_peptide_df = pd.DataFrame.from_records(consolidated_peptide_list)
    consolidated_peptide_df.to_excel(consolidated_output_fp, sheet_name="Consolidated Peptides", index=False)
    consolidated_output_fp.close()


@click.argument("seq_fp", type=click.File("r"))
@click.argument("outfile_root", type=str)
@click.argument("overlap", type=int)
@click.argument("mer_length", type=int)
@click.group()
@click.pass_context
def main(ctx, mer_length, overlap, outfile_root, seq_fp):
    """
    \b
    Purpose: Create Excel spreadsheets containing peptides generated from
             sequence files, with an indicator as to whether they match the
             peptide in the same position in a reference sequence.  The
             sequence and the reference sequence can be in either two different
             files, or one file containing both.  One spreadsheet will contain
             the peptides generated from all of the sequences, and the other
             will consolidate the peptides into a single column with another
             column indicating which sequences contain them.

    \b
    Input parameters: Length of the desired peptide
                      Length of the overlap between peptides
                      Root name of the output file
                      Name of the input sequence fasta file
                      single-file OR two-files
    \b
    single-file parameter: Reference sequence ID

    \b
    two-files parameter: Name of the reference sequence file

    \b
    Execution (single-file):
        python peptide_gen.py <peptide length> <overlap>
            <output file root name> <sequence file> single-file
            <reference sequence ID>
    NOTE: Do not include the angle brackets with the parameters.

    \b
    Execution (two-files):
        python peptide_gen.py <peptide length> <overlap>
            <output file root name> <sequence file> two-files
            <reference sequence file>
    NOTE: Do not include the angle brackets with the parameters.

    """
    ctx.obj = {"mer_length": mer_length,
               "overlap": overlap,
               "outfile_root": outfile_root,
               "seq_fp": seq_fp}


@main.command()
@click.pass_context
@click.argument("refseq_id", type=str)
def single_file(ctx, refseq_id):
    """
    The reference sequences is in the alignment FASTA file.
    """

    comp_record_list = []

    for seq_record in SeqIO.parse(ctx.obj["seq_fp"], "fasta"):
        if seq_record.id == refseq_id:
            ref_record = seq_record
        else:
            comp_record_list.append(seq_record)

    create_peptides(ctx.obj["mer_length"], ctx.obj["overlap"], ctx.obj["outfile_root"],
                    ref_record, comp_record_list)


@main.command()
@click.pass_context
@click.argument("ref_fp", type=click.File("r"))
def two_files(ctx, ref_fp):
    """
    The reference sequences is in a separate FASTA file.
    """

    comp_record_list = []

    ref_record = SeqIO.read(ref_fp, "fasta")
    for seq_record in SeqIO.parse(ctx.obj["seq_fp"], "fasta"):
        comp_record_list.append(seq_record)

    create_peptides(ctx.obj["mer_length"], ctx.obj["overlap"], ctx.obj["outfile_root"],
                    ref_record, comp_record_list)


if __name__ == "__main__":
    main()
