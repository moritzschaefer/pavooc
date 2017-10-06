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
