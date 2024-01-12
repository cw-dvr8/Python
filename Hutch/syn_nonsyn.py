"""
Program: syn_nonsyn.py

Purpose: Create from BAM files lists of positions that have either synonymous
         or nonsynonymous amino acids based on the read codons at those
         positions.

Input parameters: Directory containing the BAM files
                  File (including path) containing the reference sequence
                  File containing the PTID/visit lookups based on the
                      GUSPEC
                  File containing the locations of the different sequence
                      regions
                  Output file directory

Outputs: File containing the positions found in the BAM files that contain
             synonymous or nonsynonymous codons
         Summary file containing the total read depth of the positions, the
             number of synonymous codons at the position, and the number of
             nonsynonymous codons at the position.

Execution: python syn_nonsyn.py

Note: The summary file does not contain insertion or frame shift positions.
"""

import argparse
import glob
import os
import re
from Bio import SeqIO
from Bio.Seq import Seq
import pandas as pd
import pysam

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("bam_dir", type=str,
                        help="BAM file directory without a trailing /")
    parser.add_argument("refseq_file", type=argparse.FileType("r"),
                        help="Reference sequence file")
    parser.add_argument("lookup_file", type=argparse.FileType("r"),
                        help="PTID/visit lookup file")
    parser.add_argument("regions", type=argparse.FileType("r"),
                        help="Sequence region file")
    parser.add_argument("output_dir", type=str, help="Output file directory")

    args = parser.parse_args()

    SAM_FLAG_LIST = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
    SAM_ERROR_FLAG_LIST = [2048, 1024, 512, 256, 4]

    STOP_CODONS = ["TAG", "TAA", "TGA"]

    ref_record = SeqIO.read(args.refseq_file, "fasta")
    ref_seq = str(ref_record.seq)

    seq_regions_df = pd.read_csv(args.regions)

    ptid_sample_df = pd.read_csv(args.lookup_file, sep="\t")

    bamfile_list = glob.glob(f"{args.bam_dir}/*.bam")
    for bamfile in bamfile_list:

        bam_fp = pysam.AlignmentFile(bamfile, "rb")

        # Convert the file name from a byte string to a regular string.
        bam_file_path = bam_fp.filename.decode("utf-8")
        sample_id = os.path.basename(bam_file_path).split(".")[0]
        ptid = ptid_sample_df.loc[ptid_sample_df["GUSPEC"] == sample_id, "PTID"].values[0]
        visitno = ptid_sample_df.loc[ptid_sample_df["GUSPEC"] == sample_id, "VISITNO"].values[0]

        output_codons_fp = open(f"{args.output_dir}/{ptid}_{visitno}_{sample_id}_synonymous_nonsynonymous_codons.csv", "w")
        output_codons_fp.write("PTID,visitno,position,region,mutant_codon,mutant_aa,ref_codon,ref_aa,seq_allele_depth,syn_nonsyn\n")
        output_totals_fp = open(f"{args.output_dir}/{ptid}_{visitno}_{sample_id}_codon_totals.csv", "w")
        output_totals_fp.write("PTID,visitno,position,total_depth,num_synonymous,num_non_synonymous\n")

        pos_mutation_dict = {}
        pos_total_dict = {}

        for read in bam_fp.fetch():
            read_flag_list = []
            read_flag = read.flag
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
                insertion_flag = False

                # BAM start positions are 0-based. Note that SAM start positions
                # are 1-based.
                read_start_pos = read.reference_start

                working_read = read.query_sequence

                # Get rid of any soft clips.
                find_start_clip = re.findall("^\d+S", read.cigarstring)
                if find_start_clip:
                    start_clip = int(re.sub("[^\d]", "", find_start_clip[0]))
                    working_read = working_read[start_clip:]

                find_end_clip = re.findall("[0-9]+S$", read.cigarstring)
                if find_end_clip:
                    end_clip = int(re.sub("[^\d]", "", find_end_clip[0]))
                    working_read = working_read[:len(working_read) - end_clip]

                cigar_noclips = re.sub("[0-9]+S", "", read.cigarstring)
                cigar_noclips = re.sub("[0-9]+H", "", cigar_noclips)

                # Construct the read string according to the CIGAR string.
                cigar_read = ""
                stop_pos = 0
                cigar_codes = re.findall("[0-9]+.", cigar_noclips)
                for ind_code in cigar_codes:
                    start_pos = stop_pos
                    ccode = re.sub("[\d]", "", ind_code)
                    ccount = int(re.sub("[^\d]", "", ind_code))
                    if ccode not in ["D", "I"]:
                        stop_pos = stop_pos + ccount
                        cigar_read = cigar_read + working_read[start_pos : stop_pos]
                    elif ccode == "D":
                        cigar_read = cigar_read + (ccount * "-")
                    else:
                        stop_pos = stop_pos + ccount
                        cigar_read = cigar_read + f"|{working_read[start_pos: stop_pos]}|"

                framed_working_read = cigar_read

                # Advance the read until it starts on reading frame 1.
                while read_start_pos % 3 > 0:
                    read_start_pos += 1
                    framed_working_read = framed_working_read[1:]

                # Advancing the read to a reading frame 1 position could
                # potentially cause it to start in the middle of an insertion.
                # For example, if the original read was A|GT|ACCT and started
                # on read frame 2, advancing it to the next read frame 1
                # position would result in a read GT|ACCT. Check that the
                # number of | characters in the read is odd. If it is, assume
                # that the read starts with a cut-off  insertion and advance it
                # to the next position past the first |.
                if framed_working_read.count("|") % 2 == 1:
                    end_insertion = framed_working_read.index("|")
                    framed_working_read = framed_working_read[end_insertion + 1:]

                ref_pos = read_start_pos

                while len(framed_working_read.replace("|", "")) >= 3:
                    read_codon = framed_working_read[0:3]
                    ref_codon = ref_seq[ref_pos : ref_pos + 3]
                    frame0_insertion = False

                    if "|" in read_codon:
                        insertion_seq = re.search("\|(.*?)\|", framed_working_read).group(1)

                        # Find the indexes of the first and last pipe that
                        # demarcate the insertion. Note that while str.find()
                        # could be used to find the first pipe, str.rfind()
                        # cannot be used to find the last pipe because some
                        # reads have more than one insertion.
                        pipe_match_list = list(re.finditer(r"(\|)", framed_working_read))
                        # first_pipe_pos = framed_working_read.find("|")
                        # last_pipe_pos = framed_working_read.rfind("|")
                        first_pipe_pos, __ = pipe_match_list[0].span()
                        last_pipe_pos, __ = pipe_match_list[1].span()
                        insertion_count = 0
                        if first_pipe_pos != 0:
                            read_codon = framed_working_read[0:first_pipe_pos]
                        elif len(insertion_seq) >= 3:
                            frame0_insertion = True
                        else:
                            read_codon = ""

                        framed_working_read = framed_working_read[last_pipe_pos + 1:]
                        if frame0_insertion:
                            read_codon = framed_working_read[0:3]
                            framed_working_read = framed_working_read[3:]

                        while len(read_codon) < 3:
                            if len(insertion_seq) >= 1:
                                read_codon += insertion_seq[0]
                                insertion_count += 1
                                if len(insertion_seq) > 1:
                                    insertion_seq = insertion_seq[1:]
                                else:
                                    insertion_seq = ""
                            else:
                                read_codon += framed_working_read[0]
                                framed_working_read = framed_working_read[1:]

                        if insertion_count < 3:
                            frame_shift_codon = framed_working_read[0:insertion_count]
                            frame_shift_length = len(frame_shift_codon)
                            frame_shift_pos = ref_pos + (3 - frame_shift_length)
                            if frame_shift_pos not in pos_mutation_dict:
                                pos_mutation_dict[frame_shift_pos] = {}
                            if frame_shift_codon not in pos_mutation_dict[frame_shift_pos]:
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon] = {}
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["ref_codon"] = frame_shift_length * "-"
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["ref_aa"] = "#"
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["read_aa"] = "#"
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["seq_allele_depth"] = 1
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["syn_nonsyn"] = "N"
                            else:
                                pos_mutation_dict[frame_shift_pos][frame_shift_codon]["seq_allele_depth"] += 1

                            framed_working_read = framed_working_read[insertion_count:]

                        if len(insertion_seq) >= 3:
                            insertion_origin_pos = (ref_pos + first_pipe_pos) - 1
                            insertion_pos = insertion_origin_pos + (insertion_count * .001) + .001
                            insertion_flag = True

                    else:
                        framed_working_read = framed_working_read[3:]

                    if insertion_flag:
                        while len(insertion_seq) >= 3:
                            if insertion_pos not in pos_mutation_dict:
                                pos_mutation_dict[insertion_pos] = {}

                            insertion_codon = insertion_seq[0:3]
                            if insertion_codon not in pos_mutation_dict[insertion_pos]:
                                pos_mutation_dict[insertion_pos][insertion_codon] = {}
                                pos_mutation_dict[insertion_pos][insertion_codon]["ref_codon"] = "---"
                                pos_mutation_dict[insertion_pos][insertion_codon]["ref_aa"] = "X"
                                pos_mutation_dict[insertion_pos][insertion_codon]["read_aa"] = Seq(insertion_codon).translate()
                                pos_mutation_dict[insertion_pos][insertion_codon]["seq_allele_depth"] = 1
                                pos_mutation_dict[insertion_pos][insertion_codon]["syn_nonsyn"] = "N"
                            else:
                                pos_mutation_dict[insertion_pos][insertion_codon]["seq_allele_depth"] += 1

                            insertion_pos = round((insertion_pos + .003), 3)
                            insertion_seq = insertion_seq[3:]
                            if len(insertion_seq) < 3:
                                insertion_flag = False

                    if ref_pos not in pos_total_dict:
                        pos_total_dict[ref_pos] = {}
                        pos_total_dict[ref_pos]["total_depth"] = 1
                        pos_total_dict[ref_pos]["total_synon"] = 0
                        pos_total_dict[ref_pos]["total_nonsynon"] = 0
                    else:
                        pos_total_dict[ref_pos]["total_depth"] += 1

                    if read_codon != ref_codon:
                        ref_aa = Seq(ref_codon).translate()
                        if "-" in read_codon:
                            read_aa = "X"
                        else:
                            read_aa = Seq(read_codon).translate()

                        if ref_pos not in pos_mutation_dict:
                            pos_mutation_dict[ref_pos] = {}

                        if read_codon not in pos_mutation_dict[ref_pos]:
                            pos_mutation_dict[ref_pos][read_codon] = {}
                            pos_mutation_dict[ref_pos][read_codon]["ref_codon"] = ref_codon
                            pos_mutation_dict[ref_pos][read_codon]["ref_aa"] = ref_aa
                            pos_mutation_dict[ref_pos][read_codon]["read_aa"] = read_aa
                            pos_mutation_dict[ref_pos][read_codon]["seq_allele_depth"] = 1
                        else:
                            pos_mutation_dict[ref_pos][read_codon]["seq_allele_depth"] += 1

                        if read_aa == ref_aa:
                            pos_mutation_dict[ref_pos][read_codon]["syn_nonsyn"] = "S"
                            pos_total_dict[ref_pos]["total_synon"] += 1
                        else:
                            pos_mutation_dict[ref_pos][read_codon]["syn_nonsyn"] = "N"
                            pos_total_dict[ref_pos]["total_nonsynon"] += 1

                    ref_pos += 3

        for position in sorted(pos_mutation_dict.keys()):
            for codon in pos_mutation_dict[position]:
                seq_region1 = seq_regions_df.loc[(seq_regions_df["start"] <= position) & (seq_regions_df["stop"] >= position), "region"]
                seq_region2 = seq_regions_df.loc[(seq_regions_df["start"] <= position + 2) & (seq_regions_df["stop"] >= position + 2), "region"]
                if not seq_region1.empty:
                    gene_region1 = seq_region1.item()
                else:
                    gene_region1 = ""
                if not seq_region2.empty:
                    gene_region2 = seq_region2.item()
                else:
                    gene_region2 = ""

                if (gene_region1 == gene_region2):
                    gene_region = gene_region1
                elif gene_region1 == "":
                    gene_region = gene_region2
                elif gene_region2 == "":
                    gene_region = gene_region1
                else:
                    gene_region = f"{gene_region1}/{gene_region2}"

                output_codons_fp.write(f"{ptid},{visitno},{position+1},{gene_region},{codon},{pos_mutation_dict[position][codon]['read_aa']},{pos_mutation_dict[position][codon]['ref_codon']},{pos_mutation_dict[position][codon]['ref_aa']},{pos_mutation_dict[position][codon]['seq_allele_depth']},{pos_mutation_dict[position][codon]['syn_nonsyn']}\n")

        for position in sorted(pos_total_dict.keys()):
            output_totals_fp.write(f"{ptid},{visitno},{position+1},{pos_total_dict[position]['total_depth']},{pos_total_dict[position]['total_synon']},{pos_total_dict[position]['total_nonsynon']}\n")

        output_codons_fp.close()
        output_totals_fp.close()


if __name__ == "__main__":
    main()
