#!/usr/bin/env python

import os
import logging

from gtfparse import read_gtf_as_dataframe
from skbio.sequence import DNA

from pavooc.config import CHROMOSOMES, DATADIR

logging.basicConfig(level=logging.INFO)


GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
CHROMOSOME_FILE = os.path.join(DATADIR, '{}.fa')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')
EXON_DIR = os.path.join(DATADIR, 'exons/')

try:
    os.mkdir(EXON_DIR)
except OSError:
    pass

headerNames = ['bin', 'name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'score', 'name2', 'cdsStartStat', 'cdsEndStat', 'exonFrames']  # noqa
gencode = read_gtf_as_dataframe(GENCODE_FILE)


def generateRawChromosomes():
    # delete newlines from chromosomes
    logging.info('Convert chromosomes into raw form')
    for chromosome_number in CHROMOSOMES:
        chromosome_filename = CHROMOSOME_FILE.format(chromosome_number)
        with open(chromosome_filename) as chromosome_file:
            chromosome = chromosome_file.read()

        raw_chromose_file = CHROMOSOME_RAW_FILE.format(chromosome_number)
        with open(raw_chromose_file, 'w') as chromosome_file:
            chromosome_file.write(
                    chromosome[2+len(chromosome_number):].replace('\n', ''))


def generateExonFiles():
    logging.info('Generate gene_exon files')
    # for each exon create one file
    chromosomes_read = {c: open(CHROMOSOME_RAW_FILE.format(c)).read()
                        for c in CHROMOSOMES}
    for index, row in gencode.iterrows():
        if row['feature'] != 'exon':
            continue

        logging.debug('Generate file for gene {} with exon {}'
                      .format(row['gene_id'], row['exon_number']))
        try:
            chromosome = chromosomes_read[row['seqname']]
        except KeyError as e:
            logging.error('Failed to get data for chromosome "{}"'
                          .format(e.args[0]))
            continue

        exon = chromosome[row['start']:row['end']]

        exon_filename = os.path.join(
                EXON_DIR,
                '{}_{}'.format(row['gene_id'], row['exon_number']))
        if row.strand == '-':
            exon = str(DNA(exon.upper()).reverse_complement())

        with open(exon_filename, 'w') as exon_file:
            exon_file.write(exon)


if __name__ == "__main__":
    generateRawChromosomes()
    generateExonFiles()
