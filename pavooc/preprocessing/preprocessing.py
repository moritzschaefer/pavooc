#!/usr/bin/env python

import os
import logging
import pickle

from gtfparse import read_gtf_as_dataframe
from skbio.sequence import DNA
from intervaltree import IntervalTree

from pavooc.config import CHROMOSOMES, EXON_INTERVAL_TREE_FILE, GENCODE_FILE, \
        GENOME_FILE, CHROMOSOME_FILE, CHROMOSOME_RAW_FILE, EXON_DIR

logging.basicConfig(level=logging.INFO)


try:
    os.mkdir(EXON_DIR)
except OSError:
    pass

headerNames = ['bin', 'name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'score', 'name2', 'cdsStartStat', 'cdsEndStat', 'exonFrames']  # noqa


def generate_raw_chromosomes():
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


def exon_interval_tree():
    '''
    Generate an exon interval tree
    '''
    gencode = read_gtf_as_dataframe(GENCODE_FILE)
    logging.info('Building exon tree')
    tree = IntervalTree()
    for index, row in gencode.iterrows():
        if row['feature'] == 'exon':
            if row['end'] > row['start']:
                tree[row['start']:row['end']] = \
                    (row['gene_id'], row['exon_number'])

    logging.info('Built exon tree with {} nodes'.format(len(tree)))

    return tree


def generateExonFiles():
    gencode = read_gtf_as_dataframe(GENCODE_FILE)
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


def combine_genome():
    '''
    Create a file genome.fa which combines all chromosome.fas
    bash:
    # for i in {1..22..1} X Y; do
    # cat chr${i}.fa >> genome.fa
    # done
    '''
    logging.info('Build all-in-one-file genome')
    with open(GENOME_FILE, 'w') as genome_file:
        for chromosome in CHROMOSOMES:
            with open(CHROMOSOME_FILE.format(chromosome)) as chr_file:
                genome_file.write(chr_file.read())


def main():
    generate_raw_chromosomes()
    combine_genome()

    # generateExonFiles()
    tree = exon_interval_tree()
    with open(EXON_INTERVAL_TREE_FILE, 'wb') as f:
        pickle.dump(tree, f)


if __name__ == "__main__":
    main()
