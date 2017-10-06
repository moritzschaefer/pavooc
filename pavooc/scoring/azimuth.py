'''
Load azimuth over a python2 interpreter (it's python 2 :/)
'''

from skbio.sequence import DNA

from pavooc.data import read_gencode, chromosomes, azimuth_model

from azimuth.model_comparison import predict as azimuth_predict
import azimuth



def _context_guide(exon_id, start_in_exon, strand, context_length=5):
    '''
    :exon_id: ensembl id
    :start_in_exon: bp position relative to ensembl start
    :strand: either 'FWD' or 'RVS'
    :context_length: option to adjust padding in bps
    :returns: azimuth compliant context 30mers (that is 5bp+protospacer+5bp) in
        capital letters
    '''

    exon = read_gencode().loc[
            (read_gencode().exon_id == exon_id) &
            (read_gencode().feature == 'exon')].iloc[0]

    start = exon['start'] + start_in_exon - (5 if strand == 'FWD' else 2)
    end = exon['start'] + start_in_exon + 23 + (2 if strand == 'FWD' else 5)
    seq = chromosomes()[exon['seqname']][start:end]

    if strand == 'RVS':
        return str(DNA(seq.upper()).reverse_complement())
    else:
        return seq.upper()


def score(guides):
    '''
    :guides: A dataframe with all relevant information for the guides
    Call the azimuth module model
    TODO add amino acid cut position and percent peptides
    :returns: a list of scores
    '''

    contexts = guides.apply(lambda row: _context_guide(
        row['exon_id'],
        row['start'],
        row['orientation']), axis=1)

    try:
        return azimuth_predict(contexts, model=azimuth_model())
    except AssertionError:
        import ipdb
        ipdb.set_trace()
