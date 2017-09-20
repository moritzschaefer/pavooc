'''
Find sgRNAs and save them in a CSV file
'''

import os
import logging

import numpy as np
from skbio.sequence import DNA
from intervaltree import IntervalTree
from gtfparse import read_gtf_as_dataframe

from pavooc.config import CHROMOSOMES, DATADIR

logging.basicConfig(level=logging.INFO)

EXON_FILE = os.path.join(DATADIR, 'exons/{}_{}')
GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')


def exon_interval_tree():
    '''
    Generate an exon interval tree
    '''
    logging.info('Building exon tree')
    tree = IntervalTree()
    gencode = read_gtf_as_dataframe(GENCODE_FILE)
    for index, row in gencode.iterrows():
        if row['feature'] == 'exon':
            if row['end'] > row['start']:
                tree[row['start']:row['end']] = \
                    (row['gene_id'], row['exon_number'])

    logging.info('Built exon tree with {} nodes'.format(len(tree)))

    return tree


def find_sgRNAs():
    '''
    Search for PAMs and return positions of their corresponding sgRNAs
    Return the position just before the sgRNA, along with the strand direction.
    PAMs on the reverse strand are described similar:
    Example:
    'tcg^acgtataaatatatcgatatNGG' would result in a tuple (3, '+')
    'atttgCCNgateagctcgatctattata^tgat' would result in a tuple (8, '-')
    :returns: A list of tuples (chromosome, strand, position, exons).
    '''
    exon_tree = exon_interval_tree()
    guide_positions = []
    for chromosome in CHROMOSOMES:
        logging.info('find pams in {}'.format(chromosome))
        with open(CHROMOSOME_RAW_FILE.format(chromosome)) as chr_file:
            chr_sequence = DNA(chr_file.read().upper())
            for strand in ['+', '-']:
                # for the reverse strand, inversecomplement the chromosome
                if strand == '-':
                    chr_sequence = chr_sequence.reverse_complement()
                # 20 Protospacer + 1 PAM-nucleotide, find overlapping sequences
                for guide_position in chr_sequence. \
                        find_with_regex('(?=(.{21}GG))'):

                    # if backward strand, reverse the position to
                    # a forward strand position
                    if strand == '-':
                        position = len(chr_sequence) - guide_position.start
                        dsb_position = position - 17
                    else:
                        position = guide_position.start
                        dsb_position = position + 17

                    exons = exon_tree[dsb_position]
                    exons_string = ';'.join(['{}_{}'.format(exon[2][0],
                                                            exon[2][1])
                                             for exon in exons])
                    if exons:
                        guide_positions.append((chromosome,
                                                strand,
                                                position,
                                                exons_string
                                                )
                                               )

    logging.info('Found {} sgRNA sites'.format(len(guide_positions)))
    return guide_positions


def save_sgRNAs(guide_positions):
    with open(os.path.join(DATADIR, 'guide_positions.csv'), 'w') as f:
        f.write('chromosome,strand,position,exons\n')
        for guide_position in guide_positions:
            f.write(','.join(np.array(guide_position).astype(str)))
            f.write('\n')


if __name__ == "__main__":
    save_sgRNAs(find_sgRNAs())
