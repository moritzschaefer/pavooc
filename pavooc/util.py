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
    return pd.read_csv(
        guides_file,
        sep='\t',
        dtype={
            'contig': str,
            'start': int,
            'stop': int,
            'target': str,
            'context': str,
            'overflow': str,
            'orientation': str,
            'otCount': int, 'offTargets': str
        }
    )


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


def guide_info(exon_id, start_in_exon, guide_direction):
    '''
    Return all necessary information for a given guide to determine its
    sequence, cut position and so on.
    :exon_id: The id of the exon in which the guide resides
    :start_in_exon: How many basepairs inside the exon it starts
    :guide_direction: One of {'FWD', 'RVS'}. determines wether the guide is in
    forward direction, relative to its exon, or in reverse.
    :returns: A tuple (exon, start, absolute_reverse, cut_position) containing
    the exon object, the start position in the chromosome, wether the guide
    is in reverse direction relative to the absolute forward strand and where
    the guide cuts
    '''
    # TODO hard to test!
    from pavooc.data import gencode_exons  # noqa # bugfix of circular import
    exon = gencode_exons().loc[exon_id]

    if isinstance(exon, pd.DataFrame):
        assert len(exon.start.unique()) == 1, \
            'same exon_id with different starts'
        exon = exon.iloc[0]

    exon_start = exon['start'] - 1  # gencode starts counting at 1 instead of 0
    # 20bp protospacer + 5bp padding at each side (or so for azimuth..)
    if exon['strand'] == '+':
        # if guide_direction == 'FWD':
        start = exon_start + start_in_exon
    else:
        start = exon['end'] - start_in_exon - 23

    # if the strands don't match, it needs to be reversed
    absolute_reverse = (guide_direction == 'RVS') != (exon['strand'] == '-')
    if absolute_reverse:
        cut_position = start + 7
    else:
        cut_position = start + 16

    return exon, start, absolute_reverse, cut_position
