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
import pymongo

from pavooc.config import CHROMOSOMES, DATADIR, EXON_INTERVAL_TREES_FILE
from pavooc.db import sgRNA_collection
from pavooc.util import kmer_to_int

logging.basicConfig(level=logging.INFO)

EXON_FILE = os.path.join(DATADIR, 'exons/{}_{}')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')


# TODO exon_interval_tree changed. is now a dict
def process_sgRNA(guide_position, chr_sequence, strand, chromosome,
                  exon_interval_trees):
    # if backward strand, reverse the position to a forward strand position
    if strand == '-':
        position = len(chr_sequence) - guide_position.start
        dsb_position = position - 17
    else:
        position = guide_position.start
        dsb_position = position + 17

    exons = exon_interval_trees[chromosome][dsb_position]

    # save the sgRNA
    doc = {
            'chromosome': chromosome,
            'strand': strand,
            'position': int(position),  # convert from np.int64
            'exons': [exon[2] for exon in exons],
            'protospacer': str(chr_sequence[guide_position])
    }
    sgRNA_collection.insert_one(doc)


def find_sgRNAs():
    '''
    Search for PAMs and their positions of their corresponding sgRNAs
    Return the position just before the sgRNA, along with the strand direction.
    Save the sgRNAs along with their positions and included exons
    PAMs on the reverse strand are described similar:
    Example:
    'tcg^acgtataaatatatcgatatNGG' would result in a tuple (3, '+')
    'atttgCCNgateagctcgatctattata^tgat' would result in a tuple (8, '-')
    '''

    with open(EXON_INTERVAL_TREES_FILE, 'rb') as f:
        exon_interval_trees = pickle.load(f)
    sgRNA_count = 0
    sgRNA_dict = {}
    sgRNA_collection.drop()
    logging.info('Old sgRNA collection deleted')
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
                        find_with_regex('(?=([ACTG]{20})[ACTG]GG)'):

                    process_sgRNA(guide_position, chr_sequence, chromosome,
                                  strand, exon_interval_trees)
                    try:
                        sgRNA_dict[kmer_to_int(chr_sequence[guide_position])] += 1
                    except KeyError:
                        sgRNA_dict[kmer_to_int(chr_sequence[guide_position])] = 1
                    sgRNA_count += 1

    logging.info('Found {} sgRNA sites'.format(sgRNA_count))
    logging.info('Found {} distinct protospacers'.format(len(sgRNA_dict)))
    with open(os.path.join(DATADIR, 'sgRNA_dict.pkl')) as f:
        pickle.dump(sgRNA_dict, f)


def create_protospacer_index():
    logging.info('Create Protospacer index')
    sgRNA_collection.create_index([("chromosome", pymongo.DESCENDING),
                                   ("protospacer", pymongo.DESCENDING)])


def main():
    find_sgRNAs()
    create_protospacer_index()


if __name__ == "__main__":
    main()
