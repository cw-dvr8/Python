"""
Program: map_ref_peptides.py

Purpose: Create a position map from the original peptide start positions to a
         reference sequence.

Input parameters: See the docstring in the main() module.

Outputs: Output file containing the column "abs_start_pos", which is the
         absolute position for the peptide start position within the
         reference sequence.

Execution: See the docstring in the main() module.

Notes:

"""

from Bio import SeqIO
import click
import pandas as pd

def get_map(ref_seq):

    ALPHA_LIST = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                  "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
                  "y", "z"]

    ref_map_dict = {}

    gap_pos_list = [0]
    curr_ref_pos = 1
    for i in range(len(ref_seq)):
        curr_pos_char = f"{curr_ref_pos}"

        if ref_seq[i] == "-":
            # The algorithm here is to create a list that contains an element
            # for insertion position letter. For gap regions of 26 or less, the
            # gap position list will only have one element that will be
            # incremented for each gap. This element will go from 0 to 25 and
            # corresponds to the elements of the ALPHA_LIST above. The
            # reference positions will look like 12a, 12b, 12c, etc. For gap
            # regions that have numbers in the range of 27 - 702, a second
            # element will be inserted at the front of the list to track the
            # second element necessary to correctly denote the gap positions,
            # and these positions will look like 12aa, 12px, 12zs, etc. For
            # each new letter position needed (aaa, pxrs, etc.), a new element
            # will be inserted at the front of the list to track it.
            new_gap_pos = False
            j = 0

            # Loop through the gap position list and append letters to the
            # reference position as necessary.
            while j < len(gap_pos_list):
                curr_pos_char += ALPHA_LIST[gap_pos_list[j]]
                j += 1

            # We now have to work backwards through the gap position list
            # because the last element in the list is the one that updates
            # the fastest. For example, if the list contained the elements
            # [12, 7, 19], this would corresponds to a position suffix of
            # mht, so suffix for the next immediate gap position would be mhu,
            # or [12, 7, 20]. Recall that Python used 0-based indexing.
            rj = 1
            while rj <= len(gap_pos_list):
                rj_idx = len(gap_pos_list) - rj
                gap_pos_list[rj_idx] += 1

                # If the current position element is less than 26, i.e. is
                # between a and z, there is no need to increment previous
                # position elements. For example, going from mht to mhu does
                # not require the second element (the h) to change.
                if gap_pos_list[rj_idx] < 26:
                    break

                else:
                    # Reset the current position element to 0 (i.e. a).
                    gap_pos_list[rj_idx] = 0
                    rj += 1

                    # If the current element is the first one in the list, set
                    # a flag to insert a new element at the beginning of the
                    # list. For example, if the previous position suffix is
                    # zz (list elements [25, 25]), a new position element
                    # needs to be added to expand the suffix to aaa (list
                    # elements [0, 0, 0]).
                    if rj > len(gap_pos_list):
                        new_gap_pos = True

            if new_gap_pos:
                gap_pos_list.insert(0, 0)
                new_gap_pos = False

        ref_map_dict[curr_pos_char] = (i + 1)

        if ((i + 1) < len(ref_seq)) and (ref_seq[i+1] != "-"):
            curr_ref_pos += 1
            gap_pos_list = [0]

    return ref_map_dict


def output_map(ref_map_dict, pep_fp, pep_file_sep, pep_start, out_fp):
    pep_df = pd.read_csv(pep_fp, sep=pep_file_sep)

    # Convert the peptide start position column to a string because the
    # reference dictionary index is a string.
    pep_df[pep_start] = pep_df[pep_start].apply(str)
    pep_df["abs_start_pos"] = pep_df[pep_start].map(ref_map_dict)
    pep_df.dropna(axis=0, subset=["abs_start_pos"], inplace=True)
    pep_df["abs_start_pos"] = pep_df["abs_start_pos"].astype(int)

    pep_df.to_csv(out_fp, index=False)
    out_fp.close()


@click.argument("out_fp", type=click.File("w"))
@click.argument("pep_start", type=str)
@click.argument("pep_file_sep", type=str)
@click.argument("pep_fp", type=click.File("r"))
@click.group()
@click.pass_context
def main(ctx, pep_fp, pep_file_sep, pep_start, out_fp):
    """
    \b
    Purpose: Create a position map from the original peptide start positions
             to a reference sequence. The output file will contain the column
             "abs_start_pos", which is the absolute position for the peptide
             start position within the reference sequence.

    \b
    Input parameters: Peptide file name, including full path
                      Peptide file separator - tabs must be passed in using $'\\t'
                      Peptide start position variable
                      New peptide output file
                      in-alignment OR in-reference, plus parameters

    \b
    in-alignment parameters: Alignment file, including full path
                             Reference sequence ID

    \b
    in-reference parameter: Reference file name, including full path

    \b
    Execution (in-alignment):
        python map_ref_peptide.py <peptide file> <peptide file separator>
            <peptide start position variable> <output file>
            in-alignment <alignment file name> <reference sequence ID>
    NOTE: Do not include the angle brackets with the parameters

    \b
    Execution (in-reference):
        python map_ref_peptide.py <peptide file> <peptide file separator>
            <peptide start position variable> <output file>
            in-reference <reference file name>
    NOTE: Do not include the angle brackets with the parameters

    """
    ctx.obj = {"pep_fp": pep_fp,
               "pep_file_sep": pep_file_sep,
               "pep_start": pep_start,
               "out_fp": out_fp}


@main.command()
@click.pass_context
@click.argument("ref_fp", type=click.File("r"))
def in_reference(ctx, ref_fp):
    """
    The reference sequence is in its own FASTA file.
    """

    ref_record = SeqIO.read(ref_fp, "fasta")
    ref_seq = str(ref_record.seq)

    ref_map_dict = get_map(ref_seq)
    output_map(ref_map_dict, ctx.obj["pep_fp"], ctx.obj["pep_file_sep"],
               ctx.obj["pep_start"], ctx.obj["out_fp"])


@main.command()
@click.pass_context
@click.argument("align_fp", type=click.File("r"))
@click.argument("ref_id", type=str)
def in_alignment(ctx, align_fp, ref_id):
    """
    The reference sequence is part of an alignment FASTA file.
    """

    for seq_rec in SeqIO.parse(align_fp, "fasta"):
        if seq_rec.id == ref_id:
            ref_seq = str(seq_rec.seq)
            break

    ref_map_dict = get_map(ref_seq)
    output_map(ref_map_dict, ctx.obj["pep_fp"], ctx.obj["pep_file_sep"],
               ctx.obj["pep_start"], ctx.obj["out_fp"])


if __name__ == "__main__":
    main()
