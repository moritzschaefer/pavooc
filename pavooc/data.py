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
    DATADIR, PROTEIN_ID_MAPPING_FILE, PDB_LIST_FILE, APPRIS_FILE
from pavooc.util import buffer_return_value

logging.basicConfig(level=logging.INFO)


@buffer_return_value
def read_gencode():
    '''
    TODO: simple test
    Buffered gencode read with HAVANA/ENSEMBL merged
    Returns the gencode dataframe but with havana and ensembl merged
    '''
    df = read_gtf_as_dataframe(GENCODE_FILE)
    df.protein_id = df.protein_id.map(lambda v: v[:15])

    protein_id_mapping = pd.read_csv(
        PROTEIN_ID_MAPPING_FILE,
        sep='\t',
        header=None,
        names=['swissprot_id', 'ID_NAME', 'protein_id'],
        dtype={'swissprot_id': str, 'ID_NAME': str, 'protein_id': str},
        index_col=False)
    protein_id_mapping = protein_id_mapping[
            protein_id_mapping.ID_NAME == 'Ensembl_PRO'][
                    ['swissprot_id', 'protein_id']]

    df = df.merge(protein_id_mapping, how='left', on='protein_id')

    mixed_ids = df[['gene_id', 'source']].drop_duplicates()

    counts = mixed_ids.gene_id.value_counts()
    duplicate_ids = counts.index[counts == 2]
    return df.drop(df.index[
        df.gene_id.isin(duplicate_ids) &
        (df.source == 'ENSEMBL')])


def gencode_gene_ids():
    '''
    Returns a pandas Series of valid protein coding gene ids
    '''
    gencode = read_gencode()

    # TODO adjust filter!
    # 1. check that it contains a tag==basic transcript!
    # 2.

    relevant_genes = gencode[
        (gencode['feature'] == 'gene') &
        (gencode['gene_type'] == 'protein_coding') &
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
        #  (gencode['tag'].isin(['CCDS', 'basic'])) &  # TODO is this correct?
        (gencode['protein_id']) &
        (gencode['seqname'].isin(CHROMOSOMES)) &
        (gencode['gene_type'] == 'protein_coding')][[
            'seqname', 'start', 'end', 'strand', 'transcript_id',
            'swissprot_id', 'gene_id', 'gene_name', 'exon_id', 'exon_number']]\
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

    logging.info('Built exon tree. {} zero size exons not included'
                 .format(len(drop_exons)))

    for _, exon in prepared.iterrows():
        exon_intervals = list(tree[exon.start:exon.end])
        relevant_exons = [
            e for e in exon_intervals if e[2][0] == exon.gene_id
        ]
        # only the exon itself was found
        if len(relevant_exons) == 1:
            continue

        # delete all but the smallest
        smallest_i = np.argmin([i[1] - i[0] for i in relevant_exons])

        for i, e in enumerate(relevant_exons):
            if i != smallest_i:
                drop_exons.add(e[2][1])
    logging.info('Found {} overlapping exons inside genes. Deleting'
                 .format(len(drop_exons)))
    return prepared.drop(list(drop_exons))

# There the start and end coordinates for each mapping are provided in the last 6 columns: RES_BEG/RES_END are for residue numbers matching the SEQRES of the PDB files (from 1 to n), PDB_BEG/PDB_END for the residue numbers as they appear in ATOM lines (i.e. can have insertion codes, can have jumps etc) and SP_BEG/SP_END are the UniProt coordinates (SP is for swissprot the old name of UniProt).
#
# Regarding mappings of ATOM lines residue number to SEQRES numbers it is easy to find them in the mmCIF or XML files provided by the PDB. The pdbx_poly_seq_scheme section contains the mapping. See for instance the corresponding file for 2zhq: ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/mmCIF/zh/2zhq.cif.gz


@buffer_return_value
def pdb_data():
    df = pd.read_csv(PDB_LIST_FILE, sep=',', skiprows=1, index_col=False)

    return df[[
        'PDB', 'CHAIN', 'SP_PRIMARY', 'PDB_BEG',
        'PDB_END', 'SP_BEG', 'SP_END']]


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


@buffer_return_value
def read_appris():
    return pd.read_csv(
        APPRIS_FILE,
        sep='\t',
        header=None,
        names=['gene_symbol', 'gene_id', 'transcript_id', 'ccds_id', 'type'],
        index_col=False).set_index('gene_id')
