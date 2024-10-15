"""
Program: map_sequence_alignment.py

Purpose: Create a position map between a reference sequence and the same
         reference sequence in an alignment.  This is done by figuring out
         where the insertions in the specified reference sequence by looking
         for where the gaps are in the specified reference sequence.

Inputs: Alignment file name
        Sequence ID to map
        Output file name

Outputs: csv file

Usage: map_sequence_alignment.py <alignment file> <seq ID to map>
           <output file name>

Notes:

"""

import argparse
from Bio import SeqIO

def get_seq_map(align_fp, align_seq_id, outfile_fp):

    ALPHA_LIST = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                  "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
                  "y", "z"]

    ref_map_dict = {}

    outfile_fp.write("seq_position,actual_seq_position,position_value\n")

    gap_pos_list = [0]
    curr_ref_pos = 1

    for seq_rec in SeqIO.parse(align_fp, "fasta"):
        seq_id = seq_rec.id
        if seq_id == align_seq_id:
            align_seq = str(seq_rec.seq)

            for i in range(len(align_seq)):
                curr_pos_char = f"{curr_ref_pos}"

                if align_seq[i] == "-":
                    # The algorithm here is to create a list that contains an
                    # element for insertion position letter. For gap regions of
                    # 26 or less, the gap position list will only have one
                    # element that will be incremented for each gap. This
                    # element will go from 0 to 25 and corresponds to the
                    # elements of the ALPHA_LIST above. The reference positions
                    # will look like 12a, 12b, 12c, etc. For gap regions that
                    # have numbers in the range of 27 - 702, a second element
                    # will be inserted at the front of the list to track the
                    # second element necessary to correctly denote the gap
                    # positions, and these positions will look like 12aa, 12px,
                    # 12zs, etc. For each new letter position needed (aaa, pxrs,
                    # etc.), a new element will be inserted at the front of the
                    # list to track it.
                    new_gap_pos = False
                    j = 0

                    # Loop through the gap position list and append letters to
                    # the reference position as necessary.
                    while j < len(gap_pos_list):
                        curr_pos_char += ALPHA_LIST[gap_pos_list[j]]
                        j += 1

                    # We now have to work backwards through the gap position
                    # list because the last element in the list is the one that
                    # updates the fastest. For example, if the list contained
                    # the elements [12, 7, 19], this would corresponds to a
                    # position suffix of mht, so suffix for the next immediate
                    # gap position would be mhu, or [12, 7, 20]. Recall that
                    # Python uses 0-based indexing.
                    rj = 1
                    while rj <= len(gap_pos_list):
                        rj_idx = len(gap_pos_list) - rj
                        gap_pos_list[rj_idx] += 1

                        # If the current position element is less than 26, i.e.
                        # is between a and z, there is no need to increment
                        # previous position elements. For example, going from
                        # mht to mhu does not require the second element (the h)
                        # to change.
                        if gap_pos_list[rj_idx] < 26:
                            break

                        else:
                            # Reset the current position element to 0 (i.e. a).
                            gap_pos_list[rj_idx] = 0
                            rj += 1

                            # If the current element is the first one in the
                            # list, set a flag to insert a new element at the
                            # beginning of the list. For example, if the
                            # previous position suffix is zz (list elements
                            # [25, 25]), a new position element needs to be
                            # added to expand the suffix to aaa (list elements
                            # [0, 0, 0]).
                            if rj > len(gap_pos_list):
                                new_gap_pos = True

                    if new_gap_pos:
                        gap_pos_list.insert(0, 0)
                        new_gap_pos = False

                ref_map_dict[curr_pos_char] = (i + 1)
                outfile_fp.write(f"{curr_pos_char},{ref_map_dict[curr_pos_char]},{align_seq[i]}\n")

                if ((i + 1) < len(align_seq)) and (align_seq[i+1] != "-"):
                    curr_ref_pos += 1
                    gap_pos_list = [0]

    outfile_fp.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("align_fp", type=argparse.FileType("r"),
                        help="Aligned sequence file")
    parser.add_argument("align_seq_id", type=str,
                        help="Sequence ID to map")
    parser.add_argument("outfile_fp", type=argparse.FileType("w"),
                        help="Output file")
 
    args = parser.parse_args()

    get_seq_map(args.align_fp, args.align_seq_id, args.outfile_fp)


if __name__ == "__main__":
    main()
