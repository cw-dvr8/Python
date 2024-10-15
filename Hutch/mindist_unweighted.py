# Program: mindist_unweighted.py
#
# Purpose: For each file of aligned participant sequences, calculates a
#          consensus sequence for each subject, measures the pairwise Hamming
#          distances between each sequence and the consensus sequence, and
#          selects the sequence with the shortest distance between them.
#
# Input parameters: See the docstring in the main() module.
#
# Outputs: - fasta file containing the mindist sequence for each participant
#          - fasta file containing the consensus sequence for each participant
#          - csv file containing the Hamming distance for each sequence
#
# Execution: See the docstring in the main() module.
#
# Notes:

import sys
sys.path.append('/bioinfo/toolbox/bioinfo_library/python/module_libraries')

import glob
import json
import os
import random
from Bio import SeqIO
import click
import pandas as pd
from cjm_module_library import df_consensus
from cjm_module_library import df_consensus_seed

@click.command()
@click.argument("json_fp", type=click.File("r"))
def main(json_fp):
    """
    \b
    Purpose: For each file of aligned participant sequences, calculates a
             consensus sequence for each subject, measures the pairwise
             distances between each sequence and the consensus sequence, and
             selects the sequence with the shortest distance between them.

    \b
    Input parameters: Name of the JSON file containing the necessary
                      parameters.

    \b
    JSON file parameters:
        participant_file_dir - The directory containing the participant
                               sequences.
        refseq - (optional) The reference sequence identifier, if the reference
                 sequence is included in the participant sequences.
        random_seed - (optional) The number to use to set the seed for
                                 random selections. If no seed is provided,
                                 there is no guarantee that this program will
                                 generate the same output if it is run multiple
                                 times over the same data.
        consensus_id_format - The format of the ID, derived from sequence IDs,
                              that will be used as the sequence IDs for the
                              consensus sequences.
        output_consensus_fasta - The output file that the consensus sequences
                                 will be written to.
        output_sequence_fasta - The output file that the participant sequences
                                will be written to.
        output_sequence_stats - The csv file that the sequence statistics will
                                be written to.

    \b
    Execution: python mindist_unweighted.py <JSON file>
    NOTE: Do not include the angle brackets with the parameter.

    """


    # Initialize the dictionaries and lists.
    seq_dict = {}
    consensus_seq_list = []

    json_dict = json.load(json_fp)

    out_cons_fp = open(json_dict["output_consensus_fasta"], "w")
    out_seq_fp = open(json_dict["output_sequence_fasta"], "w")
    out_stat_fp = open(json_dict['output_sequence_stats'], "w")
    out_stat_fp.write("sequence_id,unweighted_hamming_distance")

    # Get the list of sequence files.
    seq_file_list = glob.glob(f"{json_dict['participant_file_dir']}/*.fasta")
    for seq_file in seq_file_list:

        # If the file is empty, skip to the next file.
        if os.path.getsize(seq_file) == 0:
            print(f"File {seq_file} is empty.")
            continue

        seq_length = 0
        bad_file = False
        seq_dict = {}
        consensus_seq_list = []
        min_seq_dict = {}
        with open(seq_file, "r") as seq_fp:
            for seq_rec in SeqIO.parse(seq_fp, "fasta"):
                # If the file includes a reference sequence, ignore it.
                if "refseq" in json_dict:
                    if json_dict["refseq"] in seq_rec.id:
                        continue

                seq = str(seq_rec.seq)

                # All of the sequences in the file must be the same length.
                if seq_length == 0:
                    seq_length = len(seq)
                elif seq_length != len(seq):
                    print(f"File {seq_fp.name} has sequences of different lengths. Sequences in the file must be aligned.")
                    bad_file = True
                    break

                seq_dict[seq_rec.id] = seq
                consensus_seq_list.append(list(seq))

        # If the file is bad, skip to the next file.
        if bad_file:
            continue

        # Use the consensus sequence list to create a dataframe, and then pass
        # the dataframe to the function that finds the consensus sequence.
        consensus_seq_df = pd.DataFrame(consensus_seq_list)
        if "random_seed" in json_dict:
            consensus_seq = df_consensus_seed(consensus_seq_df, json_dict["random_seed"])
        else:
            consensus_seq = df_consensus(consensus_seq_df)

        consensus_id = seq_rec.id[: len(json_dict["consensus_id_format"])]
        out_cons_fp.write(f">{consensus_id}\n{consensus_seq}\n")

        # Cycle through the sequences in the file and get the one closest to the
        # consensus sequence.
        min_score = 0
        min_seq_dict = {}
        for seq_id in seq_dict:
            distance = 0
            for nt in range(len(seq_dict[seq_id])):
                if seq_dict[seq_id][nt] != consensus_seq[nt]:
                    distance += 1

            out_stat_fp.write(f"{seq_id},{distance}\n")
            if distance not in min_seq_dict:
                min_seq_dict[distance] = []

            min_seq_dict[distance].append(seq_id)

        minval = min(list(min_seq_dict.keys()))
        if len(min_seq_dict[minval]) == 1:
            minval_seq_id = min_seq_dict[minval][0]
        else:
            # If there is more than one sequence with the minimum distance,
            # pick one of them at random.
            if "random_seed" in json_dict:
                random.seed(json_dict["random_seed"])
            minval_seq_id = random.choice(min_seq_dict[minval])

        minval_seq = seq_dict[minval_seq_id]

        out_seq_fp.write(f">{minval_seq_id}\n{minval_seq}\n")

    out_cons_fp.close()
    out_seq_fp.close()
    out_stat_fp.close()


if __name__ == "__main__":
    main()
