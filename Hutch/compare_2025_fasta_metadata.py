from Bio import SeqIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

subj_fastafile1 = "/Volumes/bioinfo/sponsors/nih/covpn/covpn3008_ubuntu/data/fasta/20250117/CoVPN3008_VSEQUV_20241003_SEQUENCE_A.fasta"
subj_fastafile2 = "/Volumes/bioinfo/sponsors/nih/covpn/covpn3008_ubuntu/data/fasta/20250117/CoVPN3008_VSEQUV_20241127_SEQUENCE_A.fasta"
subj_fastafile3 = "/Volumes/bioinfo/sponsors/nih/covpn/covpn3008_ubuntu/data/fasta/20250117/CoVPN3008_VSEQUV_20250115_SEQUENCE_A.fasta"

def read_fasta_files(fasta_file, fasta_file_name):

    fasta_list = []
    with open(fasta_file, "r") as sf_fp:
        for seq_rec in SeqIO.parse(sf_fp, "fasta"):
            fasta_dict = {}
            fasta_dict["file_name"] = fasta_file_name
            fasta_dict["guspec"] = seq_rec.id
            fasta_dict["seq"] = str(seq_rec.seq)
            fasta_dict["seq_length"] = len(str(seq_rec.seq))
            fasta_dict["num_N"] = str(seq_rec.seq).count("N")
            fasta_list.append(fasta_dict)

    output_df = pd.DataFrame.from_records(fasta_list)
    return output_df

fasta_df = pd.DataFrame()
fasta_df = pd.concat([fasta_df, read_fasta_files(subj_fastafile1, "CoVPN3008_VSEQUV_20241003_SEQUENCE_A.fasta")], ignore_index=True)
fasta_df = pd.concat([fasta_df, read_fasta_files(subj_fastafile2, "CoVPN3008_VSEQUV_20241127_SEQUENCE_A.fasta")], ignore_index=True)
fasta_df = pd.concat([fasta_df, read_fasta_files(subj_fastafile3, "CoVPN3008_VSEQUV_20250115_SEQUENCE_A.fasta")], ignore_index=True)

# Plot the sequence length and the number of N's in the sequences.
count_len_df = fasta_df.groupby(["seq_length"], as_index=False)["seq"].count()
count_len_plot = count_len_df.plot(x="seq_length", y="seq")
count_len_plot.set_xlabel("Sequence Length")
count_len_plot.set_ylabel("Number of Sequences")
count_len_plot.axvline(x=np.nanmean(count_len_df["seq_length"]), color="r", label="Mean")
count_len_plot.axvline(x=np.nanmedian(count_len_df["seq_length"]), color="y", label="Median")
count_len_plot.set_title("CoVPN 3008 UW Sequence Lengths")
h, l = count_len_plot.get_legend_handles_labels()
count_len_plot.legend(handles=[hi for hi in h[1:]], labels=[li for li in l[1:]])
# plt.show()
plt.savefig("covpn3008_sequence_lengths.png")

count_N_df = fasta_df.groupby(["num_N"], as_index=False)["seq"].count()
count_N_plot = count_N_df.plot(x="num_N", y="seq", legend=False)
count_N_plot.set_xlabel("Number of N's")
count_N_plot.set_ylabel("Number of Sequences")
count_N_plot.axvline(x=np.nanmean(count_N_df["num_N"]), color="r", label="Mean")
count_N_plot.axvline(x=np.nanmedian(count_N_df["num_N"]), color="y", label="Median")
count_N_plot.set_title("CoVPN 3008 UW Number of N's")
h, l = count_N_plot.get_legend_handles_labels()
count_N_plot.legend(handles=[hi for hi in h[1:]], labels=[li for li in l[1:]])
# plt.show()
plt.savefig("covpn3008_sequence_NumNs.png")

metadata_file = "/Volumes/bioinfo/sponsors/nih/covpn/covpn3008_ubuntu/data/fasta/20250117/CoVPN3008_VSEQUV_20250116.txt"
metadata_fp = open(metadata_file, "r")
metadata_df = pd.read_csv(metadata_fp, sep="\t")
no_seq_df = metadata_df.loc[metadata_df["COMMENTS"] == "guspec cannot be sequenced"]
