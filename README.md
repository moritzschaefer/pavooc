# PAVOOC

Prediction and visualization of on- and off-targets for CRISPR

# Run it

Run

    python -m pavooc.data_integration.downloader

to download all the required datasets,

# Conventions

- All sequences are saved in gene-relative direction ('-'-strands are reverse-complemented).
- Ensembl gene IDs are used

# Datasources

What follows is a list of used datasets

## Reference genome GRCh37

http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/

## UCSC Pfam

Preprocessed Pfam data which maps protein domains to ucsc coordinates.

ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/ucscGenePfam.{sql,txt.gz}

## Gene annotations (exons included)

http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/refGene.txt.gz
  `bin` smallint(5) unsigned NOT NULL,  `name` varchar(255) NOT NULL,  `chrom` varchar(255) NOT NULL,  `strand` char(1) NOT NULL,  `txStart` int(10) unsigned NOT NULL,  `txEnd` int(10) unsigned NOT NULL,  `cdsStart` int(10) unsigned NOT NULL,  `cdsEnd` int(10) unsigned NOT NULL,  `exonCount` int(10) unsigned NOT NULL,  `exonStarts` longblob NOT NULL,  `exonEnds` longblob NOT NULL,  `score` int(11) default NULL,  `name2` varchar(255) NOT NULL,  `cdsStartStat` enum('none','unk','incmpl','cmpl') NOT NULL,  `cdsEndStat` enum('none','unk','incmpl','cmpl') NOT NULL,  `exonFrames` longblob NOT NULL,

## Protein data

http://www.uniprot.org/downloads

## Cancer cell line per-gene expression data

https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_byGene_2013-12-03.txt.gz
