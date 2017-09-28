#!/usr/bin/env python

import os
import logging
import pickle

from skbio.sequence import DNA
from intervaltree import IntervalTree

from pavooc.config import CHROMOSOMES, EXON_INTERVAL_TREE_FILE, \
        GENOME_FILE, CHROMOSOME_FILE, CHROMOSOME_RAW_FILE, EXON_DIR, \
        EXON_PADDING
from pavooc.gencode import read_gencode

logging.basicConfig(level=logging.INFO)


try:
    os.mkdir(EXON_DIR)
except OSError:
    pass


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
    logging.info('Building exon tree')
    tree = IntervalTree()
    for _, row in read_gencode().iterrows():
        if row['feature'] == 'exon':
            if row['end'] > row['start']:
                tree[row['start']:row['end']] = \
                    (row['gene_id'], row['exon_number'])

    logging.info('Built exon tree with {} nodes'.format(len(tree)))

    return tree


def generate_gene_files():
    logging.info('Generate gene files containing all exons')
    # for each exon create one file
    chromosomes_read = {c: open(CHROMOSOME_RAW_FILE.format(c)).read()
                        for c in CHROMOSOMES}
    gencode = read_gencode().copy()
    gencode = gencode[gencode['gene_type'] == 'protein_coding']

    for gene_id in gencode[(gencode['feature'] == 'gene')]['gene_id']:
        exons = gencode[(gencode['feature'] == 'exon') & (gencode['gene_id'] == gene_id)]
        # if gene_id == 'ENSG00000187634.6':
        #     import ipdb
        #     ipdb.set_trace()
        try:
            chromosome = chromosomes_read[exons.iloc[0]['seqname']]
        except KeyError as e:
            logging.error('Failed to get data for chromosome "{}"'
                          .format(e.args[0]))
            continue

        with open(os.path.join(EXON_DIR, gene_id), 'w') as gene_file:
            for exon_id, exon_group in exons.groupby('exon_id'):
                assert len(exon_group['start'].unique()) == 1
                assert len(exon_group['end'].unique()) == 1

                exon = exon_group.iloc[0]

                if exon['start'] < EXON_PADDING or \
                        exon['end'] + EXON_PADDING > len(chromosome):
                    logging.fatal('exon paddings overflowed chromosome ends. '
                                  'be careful with exon {}'.format(exon['exon_id']))

                exon_seq = chromosome[exon['start']-EXON_PADDING:exon['end']+EXON_PADDING]

                if exon.strand == '-':
                    exon_seq = str(DNA(exon_seq.upper()).reverse_complement())

                transcript_ids = ','.join(['{}:{}'.format(v.transcript_id, v.exon_number)
                                          for _, v in exon_group.iterrows()])

                logging.debug('Write exon {} to gene file {}'
                              .format(exon['exon_number'], exon['gene_id']))
                gene_file.write('>{} {}\n{}\n'.format(exon_id,
                                                      transcript_ids,
                                                      exon_seq))


        # group by start,end, check that exon_id is the same for each group
        # for each group
        # get all transcript_ids and exon_numbers, append them
        # check for duplicates
        # order by exon_id, save ">exonid transcript1:3,transcript2:1"
        # if both HAVANA AND ENSEMBL exist.. what then..?





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
    # generate_raw_chromosomes()
    # combine_genome()

    generate_gene_files()
    # tree = exon_interval_tree()
    # with open(EXON_INTERVAL_TREE_FILE, 'wb') as f:
    #     pickle.dump(tree, f)


if __name__ == "__main__":
    main()
