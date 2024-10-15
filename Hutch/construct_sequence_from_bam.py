"""
Program: construct_sequence_from_bam.py

Purpose: Inspect the reads from a BAM file and output a series of csv files
         containing the actual position in the sequence, the sequence position
         (may be different from the actual position because of insertions), the
         NT/AA located at that position, the read starting position, and the
         read ending position. Then read these files back in and use them to
         construct a sequence.

Input parameters: BAM file name
                  Position/values file directory
                  Output fasta file name
                  Sequence ID
                  Optional reference sequence

Outputs: csv file

Execution: python construct_sequence_from_bam.py <BAM file name>
               <position/values file name> <fasta file name>
               <sequence ID>
           
           With optional reference sequence:
           python construct_sequence_from_bam.py <BAM file name>
               <position/values file directory> <fasta file name>
               <sequence ID> --ref_seq <reference sequence name>

Notes: This program requires a virtual environment in order to run.

       If the BAM file contains alignments for more than one reference
       sequence, a reference sequence must be included in the program input
       parameters to avoid mixing NTs/AAs from different organisms to create
       the sequence.

       This program outputs/inputs position/values files because coding it
       to create a Pandas dataframe while processing the BAM file reads
       can cause the program to run for 24+ hours for some of the larger BAM
       files. It also breaks the position/values data into separate files
       based on positions because it is quicker to process several smaller
       files than it is to process one file of several million lines.

"""

import argparse

def create_seq(bam_file, pv_file_dir, fasta_file, seq_id, ref_seq):
    import os
    from pathlib import Path
    import pandas as pd
    import pysam

    SAM_FLAG_LIST = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
    SAM_ERROR_FLAG_LIST = [2048, 1024, 512, 256, 4]

    bam_fp = pysam.AlignmentFile(bam_file, "rb")

    pv_outfile = Path(fasta_file).stem.replace(".fasta", "")
    pv_file_dict = {}
    pv_file_list = []

    # If a reference sequence name is provided, check to make sure that the
    # reference sequence for the current read contains that sequence name. If
    # it does not, skip to the next read.
    for file_read in bam_fp.fetch():
        if ref_seq:
            if ref_seq not in file_read.reference_name:
                continue

        read_flag_list = []
        read_flag = file_read.flag

        if read_flag == 0:
            read_flag_list.append(0)
        else:
            for sam_flag in SAM_FLAG_LIST:
                if read_flag - sam_flag >= 0:
                    read_flag_list.append(sam_flag)
                    read_flag = read_flag - sam_flag
                    if read_flag == 0:
                        break

        if not list(set(read_flag_list).intersection(SAM_ERROR_FLAG_LIST)):
            # BAM start positions are 0-based. Note that SAM start positions
            # are 1-based.
            read_start_pos = file_read.reference_start

            working_read = file_read.query_sequence

            # Construct the read string according to the CIGAR string.
            cigar_read = ""
            read_abs_pos = 0
            for ccode, clength in file_read.cigartuples:
                # 0 indicates a match.
                if ccode == 0:
                    cigar_read = cigar_read + working_read[read_abs_pos: read_abs_pos + clength]
                    read_abs_pos = read_abs_pos + clength
                # 1 indicates an insertion.
                elif ccode == 1:
                    cigar_read = cigar_read + f"|{working_read[read_abs_pos: read_abs_pos + clength]}|"
                    read_abs_pos = read_abs_pos + clength
                # 2 indicates a deletion.
                elif ccode == 2:
                    cigar_read = cigar_read + (clength * "-")
                # We do not care about any other codes.
                else:
                    read_abs_pos = read_abs_pos + clength

            framed_working_read = cigar_read
            sequence_pos = read_start_pos
            actual_pos = read_start_pos

            insertion_flag = False
            for i in range(len(framed_working_read)):
                if framed_working_read[i] != "|":
                    pos_value = framed_working_read[i]
                    ref_seq_name = file_read.reference_name
                    read_start = read_start_pos
                    read_end = read_start_pos + (len(framed_working_read) - 1)

                    # Each position/values file will contain no more than 2000
                    # positions. Note that this does NOT mean that the file
                    # will contain only 2000 records, as there may be multiple
                    # records per position.
                    file_number = int(sequence_pos/2000)
                    if file_number not in pv_file_dict:
                        pv_outfile_name = f"{pv_file_dir}/{pv_outfile}{file_number}.csv"
                        pv_file_list.append(pv_outfile_name)
                        pv_file_dict[file_number] = open(pv_outfile_name, "w")
                        pv_file_dict[file_number].write("actual_pos,sequence_pos,pos_value,ref_seq_name,read_start,read_end\n")
                    pv_file_dict[file_number].write(f"{actual_pos},{sequence_pos},{pos_value},{ref_seq_name},{read_start},{read_end}\n")

                    if not ((i + 1) == len(framed_working_read)):
                        # If the next position is not in an insertion,
                        # increment the position by 1.
                        if ((not insertion_flag and framed_working_read[i+1] != "|")
                            or (insertion_flag and framed_working_read[i+1] == "|")):
                            sequence_pos = int(sequence_pos) + 1
                        # If the next position is in an insertion, increment
                        # the position by .001.
                        elif ((insertion_flag and framed_working_read[i+1] != "|") or
                              (not insertion_flag and framed_working_read[i+1] == "|")):
                            sequence_pos = round(sequence_pos + .001, 3)
                    actual_pos += 1
                else:
                    if insertion_flag:
                        insertion_flag = False
                    else:
                        insertion_flag = True

    # Close all of the position/values files.
    for fn in pv_file_dict:
        pv_file_dict[fn].close()

    print("Starting to build sequence")
    fasta_seq = ""
    prev_pos = -1

    for pvf in pv_file_list:

        # Read in the BAM file information to construct the sequence. Note that
        # constructing the Pandas dataframe directly from the information as it
        # is read from the BAM file causes the program to take hours to run.
        pos_values_fp = open(pvf, "r")
        pos_values_df = pd.read_csv(pos_values_fp)
        if ref_seq:
            pos_values_df = pos_values_df.loc[pos_values_df["ref_seq_name"].str.contains(ref_seq)]

        seq_pos_list = list(set(pos_values_df["sequence_pos"].tolist()))
        # We have to make sure that the position is a float value in order to
        # be able to run checks further down.
        seq_pos_list = [float(i) for i in seq_pos_list]
        seq_pos_list.sort()


        # Start constructing the sequence.
        for pos in seq_pos_list:
            # If the interval between the current position and the previous
            # position is greater than 1, it means that there are no reads
            # covering the intervening positions between the two reads, so set
            # them to gaps (-).
            if int(pos - prev_pos) > 1:
                fasta_seq = fasta_seq + ((int(pos - prev_pos) - 1) * "-")
            prev_pos = pos

            use_position = True
            # Check to see if the position is an insertion, as those are handled
            # differently. Insertion positions are followed with a decimal, e.g.
            # 15.001.
            if not pos.is_integer():
                pos_cover_df = pos_values_df.loc[(pos_values_df["read_start"] <= int(pos)) & (pos_values_df["read_end"] >= int(pos) + 1)]
                num_cover_reads = len(pos_cover_df)
                insertion_df = pos_cover_df.loc[pos_cover_df["pos_value"] == pos]
                num_cover_insertions = len(insertion_df)
                # Only use the insertion in the sequence if over half the reads
                # have an insertion at that position.
                if num_cover_insertions/num_cover_reads <= 0.5:
                    use_position = False

            pos_df = pos_values_df.loc[pos_values_df["sequence_pos"] == pos]

            if use_position:
                # If the most frequent NT is a gap (-), check to see if the next
                # most frequent character is within a certain threshold of it (I
                # am choosing .75). If so, use that NT instead of the gap in the
                # sequence.
                nt_counts = pos_df["pos_value"].value_counts()
                if (nt_counts.index[0] == "-") and (len(nt_counts) > 1) and (nt_counts[1]/nt_counts[0] >= 0.75):
                    nt_value = nt_counts.index[1]
                else:
                    nt_value = nt_counts.index[0]

                fasta_seq = fasta_seq + nt_value

        pos_values_fp.close()
        # Clean up the position/values directory.
        os.remove(pvf)

    print("About to write sequence")
    fasta_fp = open(fasta_file, "w")
    fasta_fp.write(f">{seq_id}\n")
    fasta_fp.write(f"{fasta_seq}\n")
    fasta_fp.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("bam_file", type=str, help="BAM file name")
    parser.add_argument("pos_dir", type=str,
                        help="Output position/values directory")
    parser.add_argument("fasta_file", type=str, help="Output fasta file name")
    parser.add_argument("seq_id", type=str, help="Sequence ID")
    parser.add_argument("--ref_seq", type=str,
                        help="Reference sequence to use")

    args = parser.parse_args()

    create_seq(args.bam_file, args.pos_dir, args.fasta_file, args.seq_id, args.ref_seq)

if __name__ == "__main__":
    main()
