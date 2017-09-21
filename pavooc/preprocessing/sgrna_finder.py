'''
Find sgRNAs and save them in a CSV file
Corresponding Protospacers are saved to a separate CSV file

While this code, doesn't seem to be quite intuitive, it is designed
to fit into 8GB of memory.
'''

import os
import logging
import pickle

import numpy as np
from skbio.sequence import DNA

from pavooc.config import CHROMOSOMES, DATADIR, EXON_INTERVAL_TREE_FILE, \
        PROTOSPACER_POSITIONS_FILE

logging.basicConfig(level=logging.INFO)

EXON_FILE = os.path.join(DATADIR, 'exons/{}_{}')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')

with open(EXON_INTERVAL_TREE_FILE, 'rb') as f:
    exon_interval_tree = pickle.load(f)


def find_sgRNAs_for_chromosome(chromosome, protospacer_positions_file):
    '''
    Find all sgRNAs for a chromosome sequence
    As a side effect, save all protospacers along with their positions
    :chromosome: The name of the chromosome to search in
    :protospacer_positions_file: The file handle in which to save the
        protospacers
    :returns: a list of guide_positions
    '''

    guide_positions = []
    with open(CHROMOSOME_RAW_FILE.format(chromosome)) as chr_file:
        chr_sequence = DNA(chr_file.read().upper())
        for strand in ['+', '-']:
            # for the reverse strand, inversecomplement the chromosome
            if strand == '-':
                chr_sequence = chr_sequence.reverse_complement()
            # 20 Protospacer + 1 PAM-nucleotide, find overlapping sequences
            for guide_position in chr_sequence. \
                    find_with_regex('(?=([ACTG]{20})[ACTG]GG)'):

                # if backward strand, reverse the position to
                # a forward strand position
                if strand == '-':
                    position = len(chr_sequence) - guide_position.start
                    dsb_position = position - 17
                else:
                    position = guide_position.start
                    dsb_position = position + 17

                exons = exon_interval_tree[dsb_position]
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

                # save the found protospacer
                # TODO: maybe more data useful
                protospacer_positions_file.write('{},{},{},{}'.format(
                    chromosome,
                    strand,
                    position,
                    exons_string,
                    chr_sequence[guide_position])
                )
    return guide_positions


def find_sgRNAs():
    '''
    Search for PAMs and their positions of their corresponding sgRNAs
    Return the position just before the sgRNA, along with the strand direction.
    PAMs on the reverse strand are described similar:
    sgRNAs are along with protospacer sequences are saved in two CSV files
    Example:
    'tcg^acgtataaatatatcgatatNGG' would result in a tuple (3, '+')
    'atttgCCNgateagctcgatctattata^tgat' would result in a tuple (8, '-')
    '''
    guide_positions = []
    with open(PROTOSPACER_POSITIONS_FILE, 'w') as protospacer_positions_file:
        protospacer_positions_file.write(
                'chromosome,strand,guide_position,exons,protospacer\n')
        for chromosome in CHROMOSOMES:
            logging.info('find pams in {}'.format(chromosome))
            guide_positions.extend(
                    find_sgRNAs_for_chromosome(
                        chromosome,
                        protospacer_positions_file)
            )

    logging.info('Found {} sgRNA sites'.format(len(guide_positions)))
    with open(os.path.join(DATADIR, 'guide_positions.csv'), 'w') as f:
        f.write('chromosome,strand,position,exons\n')
        for guide_position in guide_positions:
            f.write(','.join(np.array(guide_position).astype(str)))
            f.write('\n')


if __name__ == "__main__":
    find_sgRNAs()
