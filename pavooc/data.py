'''
Buffered data loading
'''
import os
import pickle
import logging

import pandas as pd
from gtfparse import read_gtf_as_dataframe
import azimuth
from intervaltree import IntervalTree

from pavooc.config import GENCODE_FILE, CHROMOSOMES, CHROMOSOME_RAW_FILE, \
        DATADIR
from pavooc.util import buffer_return_value


@buffer_return_value
def read_gencode():
    '''
    Buffered gencode
    '''
    return read_gtf_as_dataframe(GENCODE_FILE)


@buffer_return_value
def gencode_exons():
    '''
    Return the protein-coding exons from gencode, indexed by exon_id
    '''
    gencode = read_gencode()

    return gencode.loc[
            (gencode['feature'] == 'exon') &
            (gencode['gene_type'] == 'protein_coding')].set_index('exon_id')


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


@buffer_return_value
def chromosomes():
    '''
    Return dictionary with loaded chromosome data
    '''
    return {
            c: open(CHROMOSOME_RAW_FILE.format(c)).read()
            for c in CHROMOSOMES}


@buffer_return_value
def azimuth_model(nopos=True):
    azimuth_saved_model_dir = os.path.join(
            os.path.dirname(azimuth.__file__),
            'saved_models')
    if nopos:
        model_name = 'V3_model_nopos.pickle'
    else:
        model_name = 'V3_model_full.pickle'

    model_path = os.path.join(azimuth_saved_model_dir, model_name)
    with open(model_path, 'rb') as f:
        return pickle.load(f)


@buffer_return_value
def domain_interval_trees():
    '''
    Generate interval trees for all domains from Pfam
    '''
    logging.info('Building domain tree')
    trees = {chromosome: IntervalTree() for chromosome in CHROMOSOMES}
    domains = pd.read_csv(
            os.path.join(DATADIR, 'ucscGenePfam.txt'),
            sep='\t',
            header=None,
            names=[
                'bin', 'chrom', 'chromStart', 'chromEnd', 'name', 'score',
                'strand', 'thickStart', 'thickEnd', 'reserved', 'blockCount',
                'blockSizes', 'chromStarts'],
            index_col=False)

    domains = domains[domains['chrom'].isin(CHROMOSOMES)]

    for _, row in domains.iterrows():
        if row['chromEnd'] > row['chromStart']:
            for local_start, block_size in zip(
                    row['chromStarts'].split(',')[:-1],
                    row['blockSizes'].split(',')[:-1]):
                # TODO, DELETE, strand is for verification only
                trees[row['chrom']][
                        row['chromStart']+int(local_start):
                        row['chromStart']+int(local_start)+int(block_size)] = \
                                (row['name'], row['strand'])

    logging.info('Built domain tree with {} nodes'
                 .format(sum([len(tree) for tree in trees.values()])))

    return trees
