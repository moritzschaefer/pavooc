'''
Load azimuth over a python2 interpreter (it's python 2 :/)
'''

import pandas as pd
from skbio.sequence import DNA

from pavooc.data import gencode_exons, chromosomes, azimuth_model

from azimuth.model_comparison import predict as azimuth_predict


def _context_guide(exon_id, start_in_exon, strand, context_length=5):
    '''
    :exon_id: ensembl id
    :start_in_exon: bp position start of guide(!) relative to ensembl start
    :strand: either 'FWD' or 'RVS'
    :context_length: option to adjust padding in bps TODO: implement
    :returns: azimuth compliant context 30mers (that is 5bp+protospacer+5bp) in
        capital letters
    '''

    exon = gencode_exons().loc[exon_id]

    if isinstance(exon, pd.DataFrame):
        assert len(exon.start.unique()) == 1, \
                'same exon_id with different starts'
        exon = exon.iloc[0]

    exon_start = exon['start'] - 1  # gencode starts counting at 1 instead of 0
    # 20bp protospacer + 5bp padding at each side
    start = exon_start + start_in_exon - (5 if strand == 'FWD' else 2)
    end = exon_start + start_in_exon + 23 + (2 if strand == 'FWD' else 5)
    seq = chromosomes()[exon['seqname']][start:end].upper()

    if strand == 'RVS':
        seq = str(DNA(seq).reverse_complement())

    assert seq[26:28] == 'GG', 'the generated context is invalid (PAM) site'
    return seq


def score(guides):
    '''
    Call the azimuth module model
    :guides: A dataframe with all relevant information for the guides
    TODO add amino acid cut position and percent peptides
    :returns: a list of scores
    '''

    contexts = guides.apply(lambda row: _context_guide(
        row['exon_id'],
        row['start'],
        row['orientation']), axis=1)

    try:
        return azimuth_predict(contexts.values, model=azimuth_model())
    except AssertionError as e:
        import ipdb
        ipdb.set_trace()
