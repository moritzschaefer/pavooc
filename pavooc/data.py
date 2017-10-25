'''
Buffered data loading
'''
import os
import pickle
import logging

import numpy as np
import pandas as pd
from gtfparse import read_gtf_as_dataframe
import azimuth
from intervaltree import IntervalTree

from pavooc.config import GENCODE_FILE, CHROMOSOMES, CHROMOSOME_RAW_FILE, \
    DATADIR
from pavooc.util import buffer_return_value

logging.basicConfig(level=logging.INFO)


@buffer_return_value
def read_gencode():
    '''
    Buffered gencode
    '''
    return read_gtf_as_dataframe(GENCODE_FILE)


def gencode_gene_ids():
    '''
    Returns a pandas Series of valid protein coding gene ids
    '''
    gencode = read_gencode()

    relevant_genes = gencode[
            (gencode['feature'] == 'gene') &
            (gencode['source'] == 'ENSEMBL') &
            (gencode['gene_type'] == 'protein_coding') &
            (gencode['protein_id']) &
            (gencode['seqname'].isin(CHROMOSOMES))
    ]
    return relevant_genes.gene_id.drop_duplicates()


@buffer_return_value
def gencode_exons():
    '''
    Return the protein-coding exons from gencode, indexed by exon_id
    Delete duplicates
    Delete overlapping exons
    :returns: DataFrame with unique exons
    '''
    gencode = read_gencode()

    prepared = gencode.loc[
        (gencode['feature'] == 'exon') &
        (gencode['protein_id']) &
        (gencode['seqname'].isin(CHROMOSOMES)) &
        (gencode['source'] == 'ENSEMBL') &
        (gencode['gene_type'] == 'protein_coding')][[
            'seqname', 'start', 'end', 'strand',
            'gene_id', 'gene_name', 'exon_id']] \
        .drop_duplicates() \
        .set_index('exon_id')
    logging.info('Dropped exon duplicates. Now building interval tree')

    # alternative: sort by gene_id, start, end, check with next line if overlap

    # remove overlap:
    tree = IntervalTree()
    drop_exons = set()
    for _, exon in prepared.iterrows():
        try:
            tree[exon.start:exon.end] = (exon.gene_id, exon.name)
        except ValueError as e:
            drop_exons.add(exon.name)

    logging.info('Built exon tree. {} zero size exons not included'.format(len(drop_exons)))

    for _, exon in prepared.iterrows():
        exon_intervals = list(tree[exon.start:exon.end])
        relevant_exons = [
                e for e in exon_intervals if e[2][0] == exon.gene_id
                ]
        # only the exon itself was found
        if len(relevant_exons) == 1:
            continue

        # delete all but the smallest
        smallest_i = np.argmin([i[1]-i[0] for i in relevant_exons])

        for i, e in enumerate(relevant_exons):
            if i != smallest_i:
                drop_exons.add(e[2][1])
    logging.info('Found {} overlapping exons inside genes. Deleting'.format(len(drop_exons)))
    return prepared.drop(list(drop_exons))


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
                    row['chromStart'] + int(local_start):
                    row['chromStart'] + int(local_start) + int(block_size)] = \
                    (row['name'], row['strand'])

    logging.info('Built domain tree with {} nodes'
                 .format(sum([len(tree) for tree in trees.values()])))

    return trees
