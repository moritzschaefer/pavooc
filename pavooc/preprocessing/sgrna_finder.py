'''
Find sgRNAs and save them in a CSV file
Corresponding Protospacers are saved to a separate CSV file

While this code, doesn't seem to be quite intuitive, it is designed
to fit into 8GB of memory.
'''

import os
import logging
import pickle

from skbio.sequence import DNA

from pavooc.config import CHROMOSOMES, DATADIR, EXON_INTERVAL_TREE_FILE

from pavooc.db import sgRNA_collection

logging.basicConfig(level=logging.INFO)

EXON_FILE = os.path.join(DATADIR, 'exons/{}_{}')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')

with open(EXON_INTERVAL_TREE_FILE, 'rb') as f:
    exon_interval_tree = pickle.load(f)


def find_sgRNAs_for_chromosome(chromosome):
    '''
    Find all sgRNAs for a chromosome sequence
    Save the sgRNAs along with their positions and included exons
    :chromosome: The name of the chromosome to search in
    :returns: number of located sgRNAs
    '''
    count = 0
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

                # save the sgRNA
                doc = {
                        'chromosome': chromosome,
                        'strand': strand,
                        'position': int(position),  # convert from np.int64
                        'exons': [exon[2] for exon in exons],
                        'protospacer': str(chr_sequence[guide_position].
                                           reverse_complement())
                }
                sgRNA_collection.insert_one(doc)
                count += 1
    return count


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
    sgRNA_count = 0
    sgRNA_collection.drop()
    logging.info('Old sgRNA collection deleted')
    for chromosome in CHROMOSOMES:
        logging.info('find pams in {}'.format(chromosome))
        sgRNA_count += find_sgRNAs_for_chromosome(chromosome)

    logging.info('Found {} sgRNA sites'.format(sgRNA_count))


if __name__ == "__main__":
    find_sgRNAs()
