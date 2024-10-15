"""
Program: remove_artifact_sequences.py

Purpose: Remove the artifacts from the participant sequence files by using a
         list of artifacts.

Input parameters: See the docstring in the main() module.

Outputs: 1) Participant sequence files without the artifacts
         2) csv file containin the sequence file name, the number of artifacts,
            the number of sequences in the original file, and the number of
            sequences in the modified file.

Execution: See the docstring in the main() module.

Notes:

"""

from csv import DictReader
import glob
import json
import os
from Bio import SeqIO
import click

@click.command()
@click.argument("json_fp", type=click.File("r"))
def main(json_fp):
    """
    \b
    Purpose: Remove the artifacts from the participant sequence files by using a
             list of artifacts.

    \b
    Input parameters: Name of the JSON file containing the necessary
                      parameters.

    \b
    JSON file parameters: artifact_file - Name of the csv file containing the
                                          artifacts to be removed.
                          gene (optional) - The gene for the artifacts to be
                                            removed (e.g. REN, GP)
                          pid_format - Format of the participant identifier.
                          pid_source_column - The column containing the
                                              participant identifier.
                          artifact_seq_column - The column containing the
                                                artifact identifier.
                          sequence_file_dir - The directory containing the
                                              participant sequences.
                          modified_sequence_file_dir - The directory to write
                                                       the modified sequences
                                                       to.

    \b
    Execution:
        python remove_artifact_sequences.py <JSON file>
    NOTE: Do not include the angle brackets with the parameter

   """

    json_dict = json.load(json_fp)

    artifact_dict = {}
    # Read in the artifact file.
    with open(json_dict["artifact_file"], "r") as a_fp:
        reader = DictReader(a_fp)
        for row in reader:
            sample_pid = row[json_dict["pid_source_column"]][:len(json_dict["pid_format"])]
            if "gene" in json_dict:
                if json_dict["gene"] in row[json_dict["pid_source_column"]]:
                    if sample_pid not in artifact_dict:
                        artifact_dict[sample_pid] = []

                    artifact_dict[sample_pid].append(row[json_dict["artifact_seq_column"]])
            else:
                if sample_pid not in artifact_dict:
                    artifact_dict[sample_pid] = []

                artifact_dict[sample_pid].append(row[json_dict["artifact_seq_column"]])

    # Get the list of all of the sequence files so that the ones that do not have
    # artifacts will still get copied into the new directory.
    full_file_list = glob.glob(f"{json_dict['sequence_file_dir']}/*.fasta")

    artifact_stats_dict = {}
    for fasta_file in full_file_list:
        fasta_file_name = os.path.basename(fasta_file)
        fasta_file_pid = fasta_file_name[:len(json_dict["pid_format"])]

        seq_fp = open(fasta_file, "r")
        output_file_name = f"{json_dict['modified_sequence_file_dir']}/{fasta_file_name}"
        outfile_fp = open(f"{output_file_name}", "w")

        artifact_stats_dict[fasta_file_name] = {}
        artifact_stats_dict[fasta_file_name]["num_artifacts"] = 0
        artifact_stats_dict[fasta_file_name]["num_seqs_orig_file"] = 0
        artifact_stats_dict[fasta_file_name]["num_seqs_mod_file"] = 0

        if fasta_file_pid in artifact_dict:
            for seq_rec in SeqIO.parse(seq_fp, "fasta"):
                artifact_stats_dict[fasta_file_name]["num_seqs_orig_file"] += 1
                if seq_rec.id not in artifact_dict[fasta_file_pid]:
                    outfile_fp.write(f">{seq_rec.id}\n{seq_rec.seq}\n")
                    artifact_stats_dict[fasta_file_name]["num_seqs_mod_file"] += 1
                else:
                    artifact_stats_dict[fasta_file_name]["num_artifacts"] += 1
        else:
            # I tried to use shutil methods to just copy files that do not
            # have artifacts, but got some weird permission errors so those
            # files are just copied line by line.
            for seq_rec in SeqIO.parse(seq_fp, "fasta"):
                artifact_stats_dict[fasta_file_name]["num_seqs_orig_file"] += 1
                outfile_fp.write(f">{seq_rec.id}\n{seq_rec.seq}\n")
                artifact_stats_dict[fasta_file_name]["num_seqs_mod_file"] += 1

        seq_fp.close()
        outfile_fp.close()

    # Write out the stats for the modified files.
    with open(f"{json_dict['modified_sequence_file_dir']}/artifact_removal_stats.csv", "w") as stats_fp:
        stats_fp.write("seq_file,num_artifacts,num_original_seqs,num_final_seqs\n")
        for fasta_file_name in artifact_stats_dict:
            stats_fp.write(f"{fasta_file_name},{artifact_stats_dict[fasta_file_name]['num_artifacts']},{artifact_stats_dict[fasta_file_name]['num_seqs_orig_file']},{artifact_stats_dict[fasta_file_name]['num_seqs_mod_file']}\n")


if __name__ == "__main__":
    main()
