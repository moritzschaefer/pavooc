'''
Find PAM sites and save them in a CSV file
'''

import os

from skbio.sequence import DNA

from pavooc.config import CHROMOSOMES, DATADIR

EXON_FILE = os.path.join(DATADIR, 'exons/{}_{}')
GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')


def find_pams():
    '''
    Search for PAMs and return their positions.
    Return the position just before the PAM, along with the strand direction.
    PAMs on the reverse strand are described similar:
    Example:
    'tcg^GGNacgtataa' would result in a tuple (3, '+')
    'atttgNCC^gatgat' would result in a tuple (8, '-')
    :returns: A list of tuples (start, strand).
    '''
    guide_positions = []
    for chromosome in CHROMOSOMES:
        with open(CHROMOSOME_RAW_FILE.format(chromosome)) as chr_file:
            chr_sequence = DNA(chr_file.read())
            for strand in ['+', '-']:
                # for the reverse strand, inversecomplement the chromosome
                if strand == '-':
                    chr_sequence = str(chr_sequence.reverse_complement())
                # 20 Protospacer + 1 PAM-nucleotide
                for guide_position in chr_sequence.find_with_regex('GG.{21}'):
                    if strand == '-':
                        position = len(chr_sequence) - guide_position.start
                    else:
                        position = guide_position.start
                    guide_positions.append((chromosome, strand, position))
    return guide_positions
