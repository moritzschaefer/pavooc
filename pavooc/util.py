import pandas as pd


def kmer_to_int(kmer):
    '''Transform a 20bp DNA sequence to a 64 bit integer'''
    code = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

    if len(kmer) != 20:
        raise ValueError('Only 20mers supported')

    v = 0
    for i, c in enumerate(str(kmer)):
        v <<= 2
        v += code[c]

    return v


def int_to_kmer(v):
    '''Transform a 64 bit integer to a 20mer DNA sequence'''
    code = ['A', 'C', 'G', 'T']

    kmer = ''

    for i in range(20):
        kmer = code[v & 3] + kmer
        v >>= 2

    return kmer


def buffer_return_value(func):
    def wrapper(*args, **kwargs):
        if isinstance(wrapper.buffer, type(None)):
            wrapper.buffer = func(*args, **kwargs)
        return wrapper.buffer

    wrapper.buffer = None

    return wrapper


def read_guides(guides_file):
    '''
    Read a guides file (CSV format)
    :guides_file: Filename of the guides file
    :returns: Pandas dataframe
    '''
    pass


def normalize_pid(pid):
    '''
    Cut the '-n' part of a protein id if existent
    :returns: The protein id without the isoform identifier
    '''

    dash_position = pid.find('-')
    if dash_position >= 0:
        return pid[:dash_position]
    else:
        return pid


def percent_peptide(guide, gene_start, gene_end, strand):
    if strand == '+':
        return 100.0 * (guide.start - gene_start) / (gene_end - gene_start)
    else:
        return 100.0 * (gene_end - guide.start) / (gene_end - gene_start)


def aa_cut_position(guide, canonical_exons):
    '''
    iterate over canonical exons, incrementing AA counter, looking for
    whether the cut_position is inside one of them or not.
    :returns: either the AA cut-position ith the canonical exon sequence
        or -1

    '''
    bp_position = 0
    for index, canonical_exon in canonical_exons.iterrows():
        if guide.cut_position >= canonical_exon['start'] and \
                guide.cut_position < canonical_exon['end']:
            if canonical_exon.strand == '+':
                return (bp_position +
                        (guide.cut_position - canonical_exon['start'])) // 3
            else:
                return (bp_position +
                        (canonical_exon['end'] - guide.cut_position)) // 3

        exon_length_bp = (canonical_exon['end'] - canonical_exon['start'])
        bp_position += exon_length_bp
    return -1
