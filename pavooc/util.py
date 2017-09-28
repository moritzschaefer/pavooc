
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
