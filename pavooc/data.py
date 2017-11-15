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
        (df['seqname'].isin(CHROMOSOMES))]

    # drop all transcripts and exons that have no protein_id
    df.drop(df.index[(df.protein_id == '') & (
        df.feature.isin(['exon', 'transcript']))], inplace=True)

    # only take exons and transcripts which contain a basic-tag
    non_basic_transcripts = (df['feature'].isin(['transcript', 'exon'])) & \
        ~(df['tag'].str.contains('basic'))
    df.drop(df.index[non_basic_transcripts], inplace=True)

    # drop all genes which have no transcripts
    valid_genes = df[df['feature'] == 'transcript'].gene_id.drop_duplicates()
    # double check, there are no orphan-exons or so
    assert set(valid_genes) == \
        set(df[df['feature'] == 'exon'].gene_id.drop_duplicates())
    df = df[df.gene_id.isin(valid_genes)]

    # add swissprot id mappings
    protein_id_mapping = pd.read_csv(
        PROTEIN_ID_MAPPING_FILE,
        sep='\t',
        header=None,
        names=['swissprot_id', 'ID_NAME', 'protein_id'],
        dtype={'swissprot_id': str, 'ID_NAME': str, 'protein_id': str},
        index_col=False)
    # TODO  "P63104-1        Ensembl_PRO     ENSP00000309503"
    # is not recognized for example (due to the '-1')
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

    return df[[
        'feature', 'gene_id', 'transcript_id',
        'start', 'end', 'exon_id', 'exon_number',
        'gene_name', 'transcript_type', 'strand',
        'gene_type', 'tag', 'protein_id', 'swissprot_id',
        'score', 'seqname', 'source']]


@buffer_return_value
def gencode_exons():
    '''
    Return the protein-coding exons from gencode, indexed by exon_id
    Delete duplicates (note that the same exon_id can appear twice with
    different transcripts) TODO is this good?
    Delete overlapping exons
    :returns: DataFrame with unique exons
    '''
    gencode = read_gencode()

    prepared = gencode.loc[gencode['feature'] == 'exon'][[
        'seqname', 'start', 'end', 'strand', 'transcript_id',
        'swissprot_id', 'gene_id', 'gene_name', 'exon_id', 'exon_number']] \
        .drop_duplicates() \
        .set_index('exon_id')
    logging.info('Dropped exon duplicates. Now building interval tree')

    # alternative: sort by gene_id, start, end, check with next line if overlap
    # remove overlapping exons
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
    if len(drop_exons) > 0:
        prepared.drop(list(drop_exons), inplace=True)

    return prepared

# There the start and end coordinates for each mapping are provided in the last 6 columns: RES_BEG/RES_END are for residue numbers matching the SEQRES of the PDB files (from 1 to n), PDB_BEG/PDB_END for the residue numbers as they appear in ATOM lines (i.e. can have insertion codes, can have jumps etc) and SP_BEG/SP_END are the UniProt coordinates (SP is for swissprot the old name of UniProt).
#
# Regarding mappings of ATOM lines residue number to SEQRES numbers it is easy to find them in the mmCIF or XML files provided by the PDB. The pdbx_poly_seq_scheme section contains the mapping. See for instance the corresponding file for 2zhq: ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/mmCIF/zh/2zhq.cif.gz


@buffer_return_value
def pdb_data():
    df = pd.read_csv(PDB_LIST_FILE, sep=',', skiprows=1, index_col=False)
    df['SP_BEG'] -= 1
    df['SP_END'] -= 1

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
