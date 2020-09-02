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

    ##### assay #####

    # Change ATACseq to be ATACSeq.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where assay = \'ATACseq\'')
    correction_df = correction.asDataFrame()

    correction_df["assay"] = 'ATACSeq'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change ERRBS to be errBisulfiteSeq.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where assay = \'ERRBS\'')
    correction_df = correction.asDataFrame()

    correction_df["assay"] = 'errBisulfiteSeq'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change Hi-C to be HI-C.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where assay = \'Hi-C\'')
    correction_df = correction.asDataFrame()

    correction_df["assay"] = 'HI-C'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change IsoSeq to be ISOSeq.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where assay = \'IsoSeq\'')
    correction_df = correction.asDataFrame()

    correction_df["assay"] = 'ISOSeq'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change NOMe-seq to be NOMe-Seq.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where assay = \'NOMe-seq\'')
    correction_df = correction.asDataFrame()

    correction_df["assay"] = 'NOMe-Seq'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    ##### dataType #####

    # Change DNA methylation to be chromatinActivity.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'DNA methylation\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'chromatinActivity'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change barcodes to be geneExpression.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'barcodes\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'geneExpression'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change chromatictivity to be chromatinActivity.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'chromatictivity\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'chromatinActivity'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change chromatinStructure to be chromatinActivity.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'chromatinStructure\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'chromatinActivity'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change counts to be geneExpression.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'counts\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'geneExpression'
    correction_df["dataSubtype"] = 'processed'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change genes to be geneExpression.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'genes\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'geneExpression'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change histone modification to be chromatinActivity.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'histone modification\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'chromatinActivity'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change IncRNA to be geneExpression.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'IncRNA\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'geneExpression'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change mRNA to be geneExpression.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where dataType = \'mRNA\'')
    correction_df = correction.asDataFrame()

    correction_df["dataType"] = 'geneExpression'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    ##### fileFormat #####

    # Change broadPeak to be bed broadPeak.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'broadPeak\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = 'bed broadPeak'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change bw to be bigwig.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'bw\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = 'bigwig'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change gappedPeak to be bed gappedPeak.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'gappedPeak\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = 'bed gappedPeak'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change gz to be zip.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'gz\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = 'zip'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change narrowPeak to be bed narrowPeak.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'narrowPeak\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = 'bed narrowPeak'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change qc to be missing.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where fileFormat = \'qc\'')
    correction_df = correction.asDataFrame()

    correction_df["fileFormat"] = ''

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    ##### nucleicAcidSource #####

    # Change Sorted nuclei to be sorted nuclei.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where nucleicAcidSource = \'Sorted nuclei\'')
    correction_df = correction.asDataFrame()

    correction_df["nucleicAcidSource"] = 'sorted nuclei'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    ##### study #####

    # Change HumanACC to be HumanFC.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where study = \'HumanACC\'')
    correction_df = correction.asDataFrame()

    correction_df["study"] = 'HumanFC'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change IncRNA to be lncRNA Pilot.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where study = \'IncRNA\'')
    correction_df = correction.asDataFrame()

    correction_df["study"] = 'lncRNA Pilot'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change IsoHub to be IsoHuB.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where study = \'IsoHub\'')
    correction_df = correction.asDataFrame()

    correction_df["study"] = 'IsoHuB'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    ##### tissue #####

    # Change ACC to be anterior cingulate cortex.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'ACC\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'anterior cingulate cortex'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change ACC,PFC to be anterior cingulate cortex,prefrontal cortex.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'ACC,PFC\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'anterior cingulate cortex,prefrontal cortex'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change DLPFC to be dorsolateral prefrontal cortex.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'DLPFC\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'dorsolateral prefrontal cortex'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change PFC to be prefrontal cortex.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'PFC\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'prefrontal cortex'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change mediodorsal nucleus of the thalamus to be medial dorsal nucleus of thalamus.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'mediodorsal nucleus of the thalamus\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'medial dorsal nucleus of thalamus'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change olfactory epithelium to be olfactory neuroepithelium.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'olfactory epithelium\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'olfactory neuroepithelium'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))

    # Change visual cortex to be primary visual cortex.
    correction = syn.tableQuery(f'select * from {PEC_FILE_VIEW_SYNID} where tissue = \'visual cortex\'')
    correction_df = correction.asDataFrame()

    correction_df["tissue"] = 'primary visual cortex'

    fv = syn.store(synapseclient.Table(correction.tableId, correction_df))



if __name__ == "__main__":
    main()
