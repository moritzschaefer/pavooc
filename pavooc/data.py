'''
Buffered data loading
'''
import os
import pickle

from gtfparse import read_gtf_as_dataframe
import pandas as pd
import azimuth

from pavooc.config import GENCODE_FILE, CHROMOSOMES, CHROMOSOME_RAW_FILE
from pavooc.util import buffer_return_value


def read_gencode():
    '''
    Buffered gencode
    '''
    if not isinstance(read_gencode.buffered, pd.DataFrame):
        read_gencode.buffered = read_gtf_as_dataframe(GENCODE_FILE)
    return read_gencode.buffered


read_gencode.buffered = None


# TODO annotation to buffer output automatically
@buffer_return_value
def gencode_exons():
    '''
    Return the exons from gencode, indexed by exon_id
    '''
    gencode = read_gencode()

    return gencode.loc[gencode['feature'] == 'exon'].set_index('exon_id')


def gencode_exons_gene_grouped():
    '''
    Returns a pandas Groupby object, grouped by gene
    '''
    gencode = read_gencode()
    gencode = gencode[
            (gencode['gene_type'] == 'protein_coding') &
            (gencode['seqname'].isin(CHROMOSOMES)) &
            (gencode['feature'] == 'exon')]

    return gencode.groupby('gene_id')


def chromosomes():
    '''
    Return dictionary with loaded chromosome data
    '''
    if not chromosomes.buffered:
        chromosomes.buffered = {
                c: open(CHROMOSOME_RAW_FILE.format(c)).read()
                for c in CHROMOSOMES}
    return chromosomes.buffered


chromosomes.buffered = None


def azimuth_model(nopos=True):
    import ipdb
    ipdb.set_trace()
    if not azimuth_model.buffered:
        azimuth_saved_model_dir = os.path.join(
                os.path.dirname(azimuth.__file__),
                'saved_models')
        if nopos:
            model_name = 'V3_model_nopos.pickle'
        else:
            model_name = 'V3_model_full.pickle'

        model_path = os.path.join(azimuth_saved_model_dir, model_name)
        with open(model_path, 'rb') as f:
            azimuth_model.buffered = pickle.load(f)

    return azimuth_model.buffered


azimuth_model.buffered = None
