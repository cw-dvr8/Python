#!/usr/bin/env python3

"""
Program: fix_annotations_20200828.py

Purpose: Fix annotation issues found in the High Value Keys pre-portal audit.

Execution: fix_annotations_20200828.py

"""

import synapseclient
from synapseclient import Table

PEC_FILE_VIEW_SYNID = 'syn20821313'

def main():

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # I ran into problems querying the file view with a where clause, so just
    # get the entire fileview and then query the dataframe.

    fileview_keys = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID}')
    fileview_df = fileview_keys.asDataFrame()

    ##### assay #####

    print("assay\n")

    # Change ATACseq to be ATACSeq.
    correction_df = fileview_df.loc[fileview_df["assay"] == 'ATACseq'].copy()
    correction_df["assay"] = 'ATACSeq'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change ERRBS to be errBisulfiteSeq.
    correction_df = fileview_df.loc[fileview_df["assay"] == 'ERRBS'].copy()
    correction_df["assay"] = 'errBisulfiteSeq'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change Hi-C to be HI-C.
    correction_df = fileview_df.loc[fileview_df["assay"] == 'Hi-C'].copy()
    correction_df["assay"] = 'HI-C'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change IsoSeq to be ISOSeq.
    correction_df = fileview_df.loc[fileview_df["assay"] == 'IsoSeq'].copy()
    correction_df["assay"] = 'ISOSeq'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change NOMe-seq to be NOMe-Seq.
    correction_df = fileview_df.loc[fileview_df["assay"] == 'NOMe-seq'].copy()
    correction_df["assay"] = 'NOMe-Seq'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    ##### dataType #####

    print("dataType\n")

    # Change DNA methylation to be chromatinActivity.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["DNA methylation"]'].copy()
    correction_df["dataType"] = '["chromatinActivity"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change barcodes to be geneExpression.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["barcodes"]'].copy()
    correction_df["dataType"] = '["geneExpression"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change chromatictivity to be chromatinActivity.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["chromatictivity"]'].copy()
    correction_df["dataType"] = '["chromatinActivity]"'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change chromatinStructure to be chromatinActivity.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["chromatinStructure]"'].copy()
    correction_df["dataType"] = '["chromatinActivity]"'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change counts to be geneExpression.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["counts"]'].copy()
    correction_df["dataType"] = '["geneExpression"]'
    correction_df["dataSubtype"] = 'processed'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change genes to be geneExpression.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["genes"]'].copy()
    correction_df["dataType"] = '["geneExpression"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change histone modification to be chromatinActivity.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["histone modification"]'].copy()
    correction_df["dataType"] = '["chromatinActivity"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change IncRNA to be geneExpression.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["IncRNA"]'].copy()
    correction_df["dataType"] = '["geneExpression"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change mRNA to be geneExpression.
    correction_df = fileview_df.loc[fileview_df["dataType"] == '["mRNA"]'].copy()
    correction_df["dataType"] = '["geneExpression"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    ##### fileFormat #####

    print("fileFormat\n")

    # Change broadPeak to be bed broadPeak.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'broadPeak'].copy()
    correction_df["fileFormat"] = 'bed broadPeak'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change bw to be bigwig.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'bw'].copy()
    correction_df["fileFormat"] = 'bigwig'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change gappedPeak to be bed gappedPeak.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'gappedPeak'].copy()
    correction_df["fileFormat"] = 'bed gappedPeak'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change gz to be zip.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'gz'].copy()
    correction_df["fileFormat"] = 'zip'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change narrowPeak to be bed narrowPeak.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'narrowPeak'].copy()
    correction_df["fileFormat"] = 'bed narrowPeak'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change qc to be missing.
    correction_df = fileview_df.loc[fileview_df["fileFormat"] == 'qc'].copy()
    correction_df["fileFormat"] = ''

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    ##### nucleicAcidSource #####

    print("nucleicAcidSource\n")

    # Change Sorted nuclei to be sorted nuclei.
    correction_df = fileview_df.loc[fileview_df["nucleicAcidSource"] == 'Sorted nuclei'].copy()
    correction_df["nucleicAcidSource"] = 'sorted nuclei'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    ##### study #####

    print("study\n")

    # Change HumanACC to be HumanFC.
    correction_df = fileview_df.loc[fileview_df["study"] == '["HumanACC"]'].copy()
    correction_df["study"] = '["HumanFC"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change IncRNA to be lncRNA Pilot.
    correction_df = fileview_df.loc[fileview_df["study"] == '["IncRNA"]'].copy()
    correction_df["study"] = '["lncRNA Pilot"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change IsoHub to be IsoHuB.
    correction_df = fileview_df.loc[fileview_df["study"] == '["IsoHub"]'].copy()
    correction_df["study"] = '["IsoHuB"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    ##### tissue #####

    print("tissue\n")

    # Change ACC to be anterior cingulate cortex.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["ACC"]'].copy()
    correction_df["tissue"] = '["anterior cingulate cortex"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change ACC,PFC to be anterior cingulate cortex, prefrontal cortex.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["ACC,PFC"]'].copy()
    correction_df["tissue"] = '["anterior cingulate cortex, prefrontal cortex"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change DLPFC to be dorsolateral prefrontal cortex.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["DLPFC"]'].copy()
    correction_df["tissue"] = '["dorsolateral prefrontal cortex"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change PFC to be prefrontal cortex.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["PFC"]'].copy()
    correction_df["tissue"] = '["prefrontal cortex"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change mediodorsal nucleus of the thalamus to be medial dorsal nucleus of thalamus.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["mediodorsal nucleus of the thalamus"]'].copy()
    correction_df["tissue"] = '["medial dorsal nucleus of thalamus"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change olfactory epithelium to be olfactory neuroepithelium.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["olfactory epithelium"]'].copy()
    correction_df["tissue"] = '["olfactory neuroepithelium"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))

    # Change visual cortex to be primary visual cortex.
    correction_df = fileview_df.loc[fileview_df["tissue"] == '["visual cortex"]'].copy()
    correction_df["tissue"] = '["primary visual cortex"]'

    fv = syn.store(synapseclient.Table(fileview_keys.tableId, correction_df))



if __name__ == "__main__":
    main()
