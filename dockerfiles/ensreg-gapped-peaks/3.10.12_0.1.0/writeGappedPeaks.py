"""

This script is aimed to create a bed file by intersecting two bed
files generated with GenRich. The expected input files correspond
to a broad peaks file and a narrow peaks file. The output file
will report gapped peaks: Enriched regions defined by narrow peaks
overlapping broad peaks.

"""

# ------------------------------------
# python modules
# ------------------------------------

import sys, os
import numpy as np
import pandas as pd
import pybedtools

nameScript = sys.argv[0]

try:
    broadPeaksFile = sys.argv[1]
except IndexError:
    raise SystemExit(f"Usage: {nameScript} </path/to/broadPeaksFile/broadPeaksFile.bed>" +
                     " </path/to/narrowPeaksFile/narrowPeaksFile.bed>" +
                     " </path/to/gappedPeaksFile/gappedPeaksFile.bed")
try:
    narrowPeaksFile = sys.argv[2]
except IndexError:
    raise SystemExit(f"Usage: {nameScript} </path/to/broadPeaksFile/broadPeaksFile.bed>" +
                     " </path/to/narrowPeaksFile/narrowPeaksFile.bed>" +
                     " </path/to/gappedPeaksFile/gappedPeaksFile.bed")
try:
    gappedPeaksFile = sys.argv[3]
except IndexError:
    raise SystemExit(f"Usage: {nameScript} </path/to/broadPeaksFile/broadPeaksFile.bed>" +
                     " </path/to/narrowPeaksFile/narrowPeaksFile.bed>" +
                     " </path/to/gappedPeaksFile/gappedPeaksFile.bed")
try:
    broadPeaks = pybedtools.BedTool(broadPeaksFile)
except IndexError:
    raise SystemExit(f"File {broadPeaksFile} doesn't exist")

try:
    narrowPeaks = pybedtools.BedTool(narrowPeaksFile)
except IndexError:
    raise SystemExit(f"File {narrowPeaksFile} doesn't exist")

if os.path.isfile(gappedPeaksFile):
    print("The %s file exists. It will be overwritten" % (gappedPeaksFile))


# ------------------------
# MISC functions
# ------------------------

def intersectBroadNarrow(broadPeaks, narrowPeaks):
    """ Intersect broad and narrow peaks for keeping
    all broad peaks containing at least one narrow
    peak. The equivalent command line with bedtools
    for doing this is
    bedtools intersect -F 1 -wa -wb -a broadPeaks.bed -b narrowPeaks.bed
    """
    intersectionPeaks = broadPeaks.intersect(narrowPeaks, F=1, wa=True,
                                             wb=True)
    intersectionPeaks = intersectionPeaks.sort()
    return (intersectionPeaks)


def parsingGappedPeaks(intersectionPeaks, header=['chrom', 'start', 'end',
                                                  'name', 'score', 'strand', 'AUC', 'pval', 'qval',
                                                  'summitPos', 'chromN', 'startN', 'endN', 'nameN',
                                                  'scoreN', 'strandN', 'AUCN', 'pvalN', 'qvalN',
                                                  'summitPosN']):
    """Parsing overlapped broad peaks in BED12+3 format like the ENCODE
    gappedPeaks format (https://genome.ucsc.edu/FAQ/FAQformat.html#format14)
    adapted for a better visualization in the ENSEMBL genome browser.
        +--------------+------+----------------------------------------+
        |field         |type  |description                             |
        +--------------+------+----------------------------------------+
        |chrom         |string|Name of the chromosome                  |
        +--------------+------+----------------------------------------+
        |chromStart    |int   |The starting position of the first      |
        |              |      |narrow peak overlapping with a broad    |
        |              |      |in the chromosome. The first base in a  |
        |              |      |chromosome is numbered 0.               |
        +--------------+------+----------------------------------------+
        |chromEnd      |int   |The ending position of the last narrow  |
        |              |      |peak overlapping the broad peak. The    |
        |              |      |chromEnd base is not included in the    |
        |              |      |display of the feature.                 |
        +--------------+------+----------------------------------------+
        |name          |string|Name given to the broad region          |
        |              |      |overlapping with at least one narrow    |
        |              |      |peak.                                   |
        +--------------+------+----------------------------------------+
        |score         |int   |Score of the broad peak reported by     |
        |              |      |GenRich.                                |
        +--------------+------+----------------------------------------+
        |strand        |char  |Strand of the broad peak reported by    |
        |              |      |GenRich. +/- denote strand or           |
        |              |      |orientation, '.' no orientation is      |
        |              |      |assigned.                               |
        +--------------+------+----------------------------------------+
        |thickStart    |int   |The starting position at which the      |
        |              |      |feature is drawn thickly. By default it |
        |              |      |will be 0 for gappedPeaks format.       |
        +--------------+------+----------------------------------------+
        |thickEnd      |int   |The ending position at which the feature|
        |              |      |is drawn thickly. By default it will be |
        |              |      |0 for gappedPeaks format                |
        +--------------+------+----------------------------------------+
        |itemRGB       |string| Not used. Set it as 0.                 |
        +--------------+------+----------------------------------------+
        |blockCount    |int   |The number of blocks in the BED line.   |
        |              |      |It is equal to the number of narrow     |
        |              |      |peaks contained in the broad region.    |
        +--------------+------+----------------------------------------+
        |blockSizes    |string|A comma-separated list of the block     |
        |              |      |sizes.                                  |
        +--------------+------+----------------------------------------+
        |blockStarts   |string| A comma-separated list of block starts.|
        +--------------+------+----------------------------------------+
        |signalValue   |float |Total area under the curve (AUC) for the|
        |(fc)          |      |broad region reported by GenRich.       |
        +--------------+------+----------------------------------------+
        |pValue        |float |Summit -log10(p-value) reported by      |
        |              |      |GenRich for the broad region.           |
        +--------------+------+----------------------------------------+
        |qValue        |float |Summit -log10(q-value) reported by      |
        |              |      |GenRich for the broad region. -1        |
        |              |      |indicates is not available (e.g. without|
        |              |      |-q).                                    |
        +--------------+------+----------------------------------------+
    """
    intersectionPeaksDF = intersectionPeaks.to_dataframe(disable_auto_names=True,
                                                         header=None, low_memory=False)
    intersectionPeaksDF.columns = header
    intersectionPeaksDF = intersectionPeaksDF.sort_values(['chromN', 'startN', 'endN'])
    gappedPeaks = intersectionPeaksDF.iloc[:, :10].copy()
    gappedPeaks = gappedPeaks.drop_duplicates()
    gappedPeaks.index = gappedPeaks.loc[:, 'name']
    gappedPeaksMD = gappedPeaks.loc[:, ['AUC', 'pval', 'qval', 'summitPos']]
    gappedPeaks = gappedPeaks.drop(['AUC', 'pval', 'qval', 'summitPos'], axis=1)
    gappedPeaks.loc[:, 'start'] = intersectionPeaksDF.groupby(['chrom', 'start',
                                                               'end'])['startN'].agg('min').to_list()
    gappedPeaks.loc[:, 'end'] = intersectionPeaksDF.groupby(['chrom', 'start',
                                                             'end'])['endN'].agg('max').to_list()
    intersectionPeaksDF.loc[:, 'startG'] = intersectionPeaksDF.groupby(['chrom', 'start',
                                                                        'end'])['startN'].transform(
        lambda x: x.min()).to_list()
    intersectionPeaksDF.loc[:, 'endG'] = intersectionPeaksDF.groupby(['chrom', 'start',
                                                                      'end'])['endN'].transform(
        lambda x: x.max()).to_list()
    intersectionPeaksDF.loc[:, 'blockSizes'] = (intersectionPeaksDF.loc[:, 'endN'] -
                                                intersectionPeaksDF.loc[:, 'startN']).astype(str)
    intersectionPeaksDF.loc[:, 'blockStarts'] = (intersectionPeaksDF.loc[:, 'startN'] -
                                                 intersectionPeaksDF.loc[:, 'startG']).astype(str)
    gappedPeaks.loc[:, 'thickStart'] = gappedPeaks.loc[:, 'start']
    gappedPeaks.loc[:, 'thickEnd'] = gappedPeaks.loc[:, 'end']
    gappedPeaks.loc[:, 'itemRGB'] = 0
    gappedPeaks.loc[:, 'blockCount'] = (intersectionPeaksDF.groupby(
        ['chrom', 'start', 'end']).size()).to_list()
    gappedPeaks.loc[:, 'blockSizes'] = (intersectionPeaksDF.groupby(['chrom', 'start',
                                                                     'end'])['blockSizes'].apply(','.join)).to_list()

    gappedPeaks.loc[:, 'blockStarts'] = (intersectionPeaksDF.groupby(['chrom', 'start',
                                                                      'end'])['blockStarts'].apply(','.join)).to_list()
    gappedPeaks.loc[:, 'AUC'] = gappedPeaksMD.loc[:, 'AUC']
    gappedPeaks.loc[:, 'pval'] = gappedPeaksMD.loc[:, 'pval']
    gappedPeaks.loc[:, 'qval'] = gappedPeaksMD.loc[:, 'qval']
    return (gappedPeaks)


# ------------------------------------#
# Main                               #
# ------------------------------------#

# Obtaining broad peaks overlapping narrow peaks
intersectionPeaks = intersectBroadNarrow(broadPeaks, narrowPeaks)

# Parsing the overlapped peaks to gapped peaks in bed 12+3 format
gappedPeaks = parsingGappedPeaks(intersectionPeaks)

# Generating the gappedPeaks.bed file
gappedPeaks.to_csv(gappedPeaksFile, sep='\t', header=False, index=False)