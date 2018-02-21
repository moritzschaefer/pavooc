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
    DATADIR, PROTEIN_ID_MAPPING_FILE, PDB_LIST_FILE, APPRIS_FILE, \
    MUTATIONS_FILE, CNS_FILE, BASEDIR
from pavooc.util import buffer_return_value

logging.basicConfig(level=logging.INFO)

# TODO 'ENSG00000101464.6' for example has a CDS-feature with a protein_id
# but its exon-feature has no protein_id assigned. Is it good to filter it
# out though?


@buffer_return_value
def read_gencode():
    '''
    Buffered gencode read with HAVANA/ENSEMBL merged
    Swissprot IDs are merged and start-end indexing is adjusted
    Returns relevant columns only
    Returns the gencode dataframe but with havana and ensembl merged
    '''

    df = read_gtf_as_dataframe(GENCODE_FILE)
    df.exon_number = df.exon_number.apply(pd.to_numeric, errors='coerce')
    df.protein_id = df.protein_id.map(lambda v: v[:15])

    # only take protein_coding genes/transcripts/exons
    df = df[
        (df['gene_type'] == 'protein_coding') &
        (df['feature'].isin(['gene', 'transcript', 'exon', 'UTR'])) &
        (df['seqname'].isin(CHROMOSOMES))]
    # drop all transcripts and exons that have no protein_id
    df.drop(df.index[(df.protein_id == '') & (
        df.feature.isin(['exon', 'transcript']))], inplace=True)

    # only take exons and transcripts which contain a basic-tag
    non_basic_transcripts = (df['feature'].isin(['transcript', 'exon'])) & \
        ~(df['tag'].str.contains('basic'))
    df.drop(df.index[non_basic_transcripts], inplace=True)

    # add swissprot id mappings
    protein_id_mapping = load_protein_mapping()
    protein_id_mapping = protein_id_mapping[
        protein_id_mapping.ID_NAME == 'Ensembl_PRO'][
        ['swissprot_id', 'protein_id']]

    df = df.merge(protein_id_mapping, how='left', on='protein_id')

    # delete ENSEMBL entries which come from both, HAVANA and ENSEMBL
    mixed_ids = df[['gene_id', 'source']].drop_duplicates()

    counts = mixed_ids.gene_id.value_counts()
    duplicate_ids = counts.index[counts == 2]
    df.drop(df.index[
        df.gene_id.isin(duplicate_ids) &
        (df.source == 'ENSEMBL')], inplace=True)

    # fix indexing
    df.start -= 1

    # TODO Note that this deletes some genes
    # use the first APPRIS transcript
    # first_apprises = read_appris().groupby('gene_id').first()
    logging.debug('# of genes: {}'.format(
        len(df.gene_id.drop_duplicates())))
    df = df[(df.feature == 'gene') | (df.tag.str.contains('appris_principal'))]
    # df = df[df.transcript_id.map(
    #     lambda tid: tid[:15]).isin(first_apprises.transcript_id)]
    # TODO shouldnt have changed... so it doesnt make sense here
    logging.debug('# of genes after selecting for appris transcript_id: {}'
                  .format(len(df.gene_id.drop_duplicates())))

    # make sure there is only one transcript
    first_transcripts = df[df.feature == 'transcript'].groupby(
        'gene_id').first().transcript_id
    invalid_elements = df.feature.isin(['transcript', 'exon', 'UTR']) & \
        ~(df.transcript_id).isin(first_transcripts)
    logging.debug(f'{invalid_elements.sum()} elements to delete because '
                  f'not in first transcript')
    df.drop(df.index[invalid_elements], inplace=True)
    logging.debug(
        f'# of genes after deleting secondary transcripts: '
        f'{len(df.gene_id.drop_duplicates())}')

    # drop all genes which have no transcripts
    valid_genes = df[df['feature'] == 'transcript'].gene_id.drop_duplicates()
    # double check, there are no orphan-exons or so
    assert set(valid_genes) == \
        set(df[df['feature'] == 'exon'].gene_id.drop_duplicates())
    df.drop(df.index[~df.gene_id.isin(valid_genes)], inplace=True)

    return df[[
        'feature', 'gene_id', 'transcript_id',
        'start', 'end', 'exon_id', 'exon_number',
        'gene_name', 'transcript_type', 'strand',
        'gene_type', 'tag', 'protein_id', 'swissprot_id',
        'score', 'seqname', 'source']]


@buffer_return_value
def celllines():
    with open(os.path.join(BASEDIR, 'pavooc/server/celllines.txt')) as f:
        return [line.strip() for line in f.readlines()][:100]


def load_protein_mapping():
    # TODO  "P63104-1        Ensembl_PRO     ENSP00000309503"
    # is not recognized for example (due to the '-1')
    return pd.read_csv(
        PROTEIN_ID_MAPPING_FILE,
        sep='\t',
        header=None,
        names=['swissprot_id', 'ID_NAME', 'protein_id'],
        dtype={'swissprot_id': str, 'ID_NAME': str, 'protein_id': str},
        index_col=False)


@buffer_return_value
def gencode_exons():
    '''

    Return the protein-coding exons from gencode, indexed by exon_id
    Return only the exons for the longest transcript for each gene

    Delete overlapping exons
    :returns: DataFrame with unique exons
    '''
    gencode = read_gencode()

    prepared = gencode.loc[gencode['feature'] == 'exon'][[
        'seqname', 'start', 'end', 'strand', 'transcript_id',
        'swissprot_id', 'gene_id', 'gene_name', 'exon_id', 'exon_number']] \
        .drop_duplicates().copy()

    # # Use longest transcript only
    # prepared['length'] = prepared['end'] - prepared['start']
    # transcripts_lengths = prepared.groupby(
    #     ['gene_id', 'transcript_id']).sum().length
    # longest_transcripts = transcripts_lengths[
    #     transcripts_lengths ==
    #     transcripts_lengths.groupby(level=0).transform('max')]
    #
    # prepared = prepared[prepared.transcript_id.isin(
    #     longest_transcripts.index.get_level_values(1))]

    return prepared.set_index('exon_id')


@buffer_return_value
def cns_trees():
    trees = {chromosome: IntervalTree() for chromosome in CHROMOSOMES}
    df = pd.read_csv(CNS_FILE, sep='\t')
    df.Chromosome = df.Chromosome.map(lambda c: f'chr{c}')
    for _, cns in df.iterrows():
        try:
            trees[cns.Chromosome][cns.Start - 1:
                                  cns.End] = \
                {'type': 2 * (2 ** cns.Segment_Mean),
                 'cellline': cns.CCLE_name}
        except KeyError:
            pass
    return trees


@buffer_return_value
def cellline_mutation_trees():
    trees = {chromosome: IntervalTree() for chromosome in CHROMOSOMES}
    df = pd.read_csv(MUTATIONS_FILE, sep='\t')
    df.Chromosome = df.Chromosome.map(lambda c: f'chr{c}')
    for _, mutation in df.iterrows():
        try:
            trees[mutation.Chromosome][mutation.Start_position - 1:
                                       mutation.End_position] = \
                {'type': mutation.Variant_Type,
                 'cellline': mutation.Tumor_Sample_Barcode}
        except KeyError:
            pass
    return trees


@buffer_return_value
def exon_interval_trees():
    '''
    Generate an exon interval tree
    '''
    logging.info('Building exon tree')
    trees = {chromosome: IntervalTree() for chromosome in CHROMOSOMES}
    relevant_exons = gencode_exons()
    for _, row in relevant_exons.iterrows():
        if row['end'] > row['start']:
            # end is included, start count at 0 instead of 1
            trees[row['seqname']][row['start'] - 1:row['end']
                                  ] = (row['gene_id'], row['exon_number'])

    logging.info('Built exon tree with {} nodes'
                 .format(sum([len(tree) for tree in trees.values()])))

    return trees


@buffer_return_value
def pdb_list():
    df = pd.read_csv(PDB_LIST_FILE, sep=',', skiprows=1, index_col=False)
    return df[['PDB', 'CHAIN', 'SP_PRIMARY']]


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
                    row['chromStart'] + int(local_start) + int(block_size)] = (row['name'], row['strand'])

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
