"""

Program: create_pte_peptides_by_position

Purpose: Generate PTE peptides from sequences.

Inputs: file_directory - directory containing the FASTA files with the
                         sequences to be used to generate the peptides
        cutoff - 10-mer frequency threshold cutoff (single-subtype sets are
                 usually .05, global sets are usually .15)
        outfile_fp - output file

Outputs: csv file

Execution: python3 create_pte_peptides_by_position.py <input file directory>
               <10-mer threshold cutoff> <output file>

Notes: The logic in this program is based on documentation from Craig
       Magaret from discussions with Fusheng Li, and also on Fusheng's
       Perl code global_last.pl.

"""
import argparse
import glob
from Bio import SeqIO
import pandas as pd

EXCLUDED_CODES = ["B", "J", "X", "Z", "#", "*", "$"]

def get_mers(in_seq, mer_length):
    mer_list = []

    while len(in_seq) >= mer_length:
        mer = in_seq[0: mer_length]
        in_seq = in_seq[1:]
        mer_list.append(mer)

    return(mer_list)

def get_mer_freqs(in_seq_list, mer_length):
    freq_dict = {}

    for seq in in_seq_list:
        mer_list = get_mers(seq, mer_length)

        # Create a list of mers that occur in the sequence. Note that the
        # frequency we are interested in is the number of sequences that
        # the mer is in, not how many times the mer occurs in total, therefore
        # the mer only needs to be counted once per sequence.
        uniq_mer_list = list(set(mer_list))
        for mer in uniq_mer_list:
            if mer in freq_dict:
                freq_dict[mer] += 1
            else:
                freq_dict[mer] = 1

    return(freq_dict)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("file_directory", type=str,
                        help="Directory containing alignment files")
    parser.add_argument("cutoff", type=float, help="Threshold cut-off")
    parser.add_argument("outfile_fp", type=argparse.FileType("w"),
                        help="Output file")

    args = parser.parse_args()

    # Loop through all of the sequences in all of the files and get the
    # complete list of 10-mer counts and 15-mers.
    filtered_mer10_dict = {}
    running_mer15_dict = {}
    num_seqs = 0
    for fasta_file in glob.glob(f"{args.file_directory}/*.fasta"):
        fasta_fp = open(fasta_file, "r")

        seq_list = []
        for seq_rec in SeqIO.parse(fasta_fp, "fasta"):
            seq = str(seq_rec.seq)
            seq_list.append(seq.replace("-",""))

            # Generate the 15-mers.
            start_pos = 0
            mer_15 = ""
            running_seq = seq
            while len(seq[start_pos:].replace("-", "")) >= 15:
                # If the current AA is a gap and the 15-mer is blank, the
                # start position should be advanced since 15-mers do not
                # start with gaps.
                if (running_seq[0] == "-") and (not mer_15):
                    start_pos += 1
                    running_seq = seq[start_pos:]
                else:
                    if running_seq[0] != "-":
                        mer_15 += running_seq[0]
                    if len(mer_15) == 15:
                        ignored_codes = [probcode for probcode in EXCLUDED_CODES if (probcode in mer_15)]
                        if ((not ignored_codes) and (mer_15 not in running_mer15_dict)
                             and (not mer_15.startswith("Q"))):
                            running_mer15_dict[mer_15] = start_pos + 1
                        mer_15 = ""
                        start_pos += 1
                        running_seq = seq[start_pos:]
                    else:
                        running_seq = running_seq[1:]
                    

        fasta_fp.close()

        num_seqs += len(seq_list)

        # Generate the 10-mers.
        mer10_dict = get_mer_freqs(seq_list, 10)
        for mer in mer10_dict:
            # Ignore any mers that contain ambiguous codes or special symbols.
            ignored_codes = [probcode for probcode in EXCLUDED_CODES if (probcode in mer)]
            if not ignored_codes:
                if mer in filtered_mer10_dict:
                    filtered_mer10_dict[mer] += mer10_dict[mer]
                else:
                    filtered_mer10_dict[mer] = mer10_dict[mer]

    print(f"Number of 15-Mers in list: {len(running_mer15_dict)}")

    # Get the list of 10-mers that meet the threshold criteria.
    cutoff_pte_list = []
    for mer in filtered_mer10_dict:
        filtered_mer10_dict[mer] = filtered_mer10_dict[mer] / num_seqs
        if (filtered_mer10_dict[mer] >= args.cutoff) and (mer not in cutoff_pte_list):
            cutoff_pte_list.append(mer)

    print(f"Number of cutoff 10-Mers: {len(cutoff_pte_list)}")

    # Get the peptides with the highest scores.
    ranked_15mer_df = pd.DataFrame()
    while (len(cutoff_pte_list) > 0) and (len(running_mer15_dict) > 0):
        mer15_dict_list = []
        no_10mers_list = []
        for mer in running_mer15_dict:
            mer15_dict = {}
            mer15_dict["mer15"] = mer
            mer15_dict["start_position"] = running_mer15_dict[mer]
            mer15_dict["mer10_sumfreqs"] = 0
            mer10_sublist = get_mers(mer, 10)
            mer15_dict["mer10_count"] = len(mer10_sublist)
            no_10mers = True
            for i in range(mer15_dict["mer10_count"]):
                mer15_dict[f"mer10_{i + 1}"] = None
                if mer10_sublist[i] in filtered_mer10_dict:
                    mer15_dict[f"mer10_{i + 1}"] = mer10_sublist[i]
                    mer15_dict["mer10_sumfreqs"] += filtered_mer10_dict[mer10_sublist[i]]
                    no_10mers = False

            mer15_dict_list.append(mer15_dict)
            if no_10mers:
                no_10mers_list.append(mer)

        # Delete 15-mers that contain no currently valid 10-mers.
        if no_10mers_list:
            for mer10 in no_10mers_list:
                running_mer15_dict.pop(mer10)

        mer15_df = pd.DataFrame.from_records(mer15_dict_list)
        mer15_df.sort_values(by=["mer10_sumfreqs"], inplace=True, ignore_index=True, ascending=False)
        top_mer_df = mer15_df.loc[mer15_df["mer10_sumfreqs"] == mer15_df["mer10_sumfreqs"].max()]

        # Take the first 15-mer that has the maximum value in case there is more
        # than one 15-mer with that value. I initially thought to pick one at
        # random, but that would make it difficult to reproduce the dataset as
        # there is no guarantee that the same 15-mer would be randomly selected
        # in later runs.
        single_mer = top_mer_df.iloc[0].copy(deep=True)

        # There are occasions where a 10-mer in the cutoff list never gets
        # used, specifically if it does not contain any ambigous codes or
        # special symbols, but the only 15-mer that contains it does. For
        # example, the sequence I used to test this program contains the 15-mer
        # LTPLCVTLDC#AS*Q. The 10-mer LTPLCVTLDC is in the 10-mer dictionary
        # since it does not contain any problematic codes, but the 15-mer is
        # not in the list of valid 15-mers, and in this case it is the only
        # 15-mer that contains LTPLCVTLDC so this 10-mer will never get
        # removed from the cutoff list. In cases like these, the maximum value
        # of summed 10-mers will be 0, so the rest of the 10-mers in the
        # cutoff list should be deleted at this point so that the loop will
        # terminate.
        if single_mer["mer10_sumfreqs"] == 0:
            cutoff_pte_list = []
        else:
            # Remove the 10-mers from the cutoff dictionary, and also from
            # the dictionary that contains all of the 10-mers. The removal
            # from the overall 10-mer dictionary is currently not in the
            # documentation, but is in the Perl program that Fusheng wrote,
            # and Craig Magaret has approved it.
            for j in range(mer15_dict["mer10_count"]):
                if single_mer[f"mer10_{j + 1}"] is not None:
                    if single_mer[f"mer10_{j + 1}"] in cutoff_pte_list:
                        cutoff_pte_list.remove(single_mer[f"mer10_{j + 1}"])
                    filtered_mer10_dict.pop(single_mer[f"mer10_{j + 1}"])

            # Remove the 15-mer from the 15-mer list.
            running_mer15_dict.pop(single_mer["mer15"])

            single_mer.at["PTE"] = len(cutoff_pte_list)
            single_mer.at["15mer"] = len(running_mer15_dict)
            ranked_15mer_df = pd.concat([ranked_15mer_df, single_mer.to_frame().T], ignore_index=True, sort=False)

    ranked_15mer_df["Pep_num"] = ranked_15mer_df.index + 1
    ranked_15mer_df["Pep"] = ranked_15mer_df.apply(lambda row: f"Pep{row.Pep_num}", axis=1)
    final_15mer_df = ranked_15mer_df[["Pep", "PTE", "start_position", "15mer", "mer15"]].copy(deep=True)
    final_15mer_df.sort_values(by=["start_position"], inplace=True, ignore_index=True)
    final_15mer_df.to_csv(args.outfile_fp, index=False)


if __name__ == "__main__":
    main()
