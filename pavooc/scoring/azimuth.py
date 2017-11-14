'''
Load azimuth over a python2 interpreter (it's python 2 :/)
'''

from skbio.sequence import DNA

from pavooc.data import chromosomes, azimuth_model
from pavooc.util import guide_info

from azimuth.model_comparison import predict as azimuth_predict


def _context_guide(exon_id, start_in_exon, guide_direction, context_length=5):
    '''
    :exon_id: ensembl id
    :start_in_exon: bp position start of guide(!) relative to ensembl start
    :guide_direction: either 'FWD' or 'RVS'
    :context_length: option to adjust padding in bps TODO: implement
    :returns: azimuth compliant context 30mers (that is 5bp+protospacer+5bp) in
        capital letters
    '''
    exon, chromosome_start, absolute_reverse, _ = guide_info(
        exon_id, start_in_exon, guide_direction)

    if absolute_reverse:
        chromosome_start -= 3
    else:
        chromosome_start -= 4

    seq = chromosomes()[exon['seqname']
                        ][chromosome_start:chromosome_start + 30].upper()

    # if the strands don't match, it needs to be reversed
    if absolute_reverse:
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
