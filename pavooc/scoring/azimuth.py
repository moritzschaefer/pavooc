'''
Load azimuth over a python2 interpreter (it's python 2 :/)
'''

from skbio.sequence import DNA
import pandas as pd
import logging

from pavooc.data import chromosomes, azimuth_model, gencode_exons

from azimuth.model_comparison import predict as azimuth_predict


def _context_guide(exon_id, start, guide_direction, context_length=5):
    '''
    :exon_id: ensembl id
    :start: bp position start of guide(!) relative to chromosome
    :guide_direction: either 'FWD' or 'RVS'
    :context_length: option to adjust padding in bps TODO: implement
    :returns: azimuth compliant context 30mers (that is 5bp+protospacer+5bp) in
        capital letters
    '''
    exon = gencode_exons().loc[exon_id]

    if isinstance(exon, pd.DataFrame):
        if len(exon.start.unique()) != 1:
            logging.error(f'same exon_id with different starts {exon}')
        exon = exon.iloc[0]

    if guide_direction == 'RVS':
        start -= 3
    else:
        start -= 4

    seq = chromosomes()[exon['seqname']
                        ][start:start + 30].upper()

    # if the strands don't match, it needs to be reversed
    if guide_direction == 'RVS':
        seq = str(DNA(seq).reverse_complement())

    assert seq[25:27] == 'GG', \
        'the generated context is invalid (PAM) site. {}, {}, {}'.format(
        seq, exon['strand'], guide_direction)
    return seq


def score(guides):
    '''
    Call the azimuth module model
    :guides: A dataframe with all relevant information for the guides
    TODO add amino acid cut position and percent peptides
    :returns: a list of scores
    '''
    if len(guides) == 0:
        return []

    contexts = guides.apply(lambda row: _context_guide(
        row['exon_id'],
        row['start'],
        row['orientation']), axis=1)

    try:
        return azimuth_predict(contexts.values, model=azimuth_model())
    except AssertionError as e:
        import ipdb
        ipdb.set_trace()
