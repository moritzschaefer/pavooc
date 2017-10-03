from gtfparse import read_gtf_as_dataframe
import pandas as pd

from pavooc.config import GENCODE_FILE, CHROMOSOMES


def read_gencode():
    '''
    Buffered gencode
    '''
    if not isinstance(read_gencode.buffered, pd.DataFrame):
        read_gencode.buffered = read_gtf_as_dataframe(GENCODE_FILE)
    return read_gencode.buffered


read_gencode.buffered = None


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
