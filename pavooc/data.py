'''
Buffered data loading
'''
import logging
import os
import pickle
from itertools import chain

import pandas as pd
# import torch
from gtfparse import read_gtf_as_dataframe
from intervaltree import IntervalTree
from sklearn.externals import joblib

import azimuth
from pavooc.config import (APPRIS_FILE, BASEDIR, CHROMOSOME_RAW_FILE,
                           CHROMOSOMES, CNS_FILE, DATADIR, GENCODE_FILE,
                           MUTATIONS_FILE, PDB_LIST_FILE,
                           PROTEIN_ID_MAPPING_FILE, SCALER_FILE)
# from pavooc.scoring.models import CNN38
from pavooc.util import buffer_return_value

logging.basicConfig(level=logging.INFO)

# TODO 'ENSG00000101464.6' for example has a CDS-feature with a protein_id
# but its exon-feature has no protein_id assigned. Is it good to filter it
# out though?


def _filter_best_transcript(gene):
    appris_values = set(chain.from_iterable(gene.tag.apply(
        lambda v: [x for x in v.split(',') if 'appris' in x]).values))
    for appris_type in ['appris_principal',
                        'appris_candidate_longest',
                        'appris_candidate']:
        if appris_type in appris_values:
            transcript_id = gene[gene.tag.str.contains(
                appris_type)].iloc[0].transcript_id
            break
    else:
        transcript_id = gene[gene.feature == 'transcript'].transcript_id
        # if len(transcript_id) > 1:
        #     print(gene.gene_id.iloc[0])
        transcript_id = transcript_id.iloc[0]

    return gene[(gene.feature == 'gene') |
                (gene.transcript_id == transcript_id)]


@buffer_return_value
def pfam_mapping():
    df = pd.read_csv(os.path.join(DATADIR, 'pdb_pfam_mapping.txt'), sep='\t')
    df = df[['PFAM_ACC', 'PFAM_Name']].drop_duplicates()
    df.index = df['PFAM_ACC'].apply(lambda row: row[:7])
    return df


@buffer_return_value
def pfam_pdb_mapping():
    df = pd.read_csv(os.path.join(DATADIR, 'pdb_pfam_mapping.txt'), sep='\t')
    return df


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
    df.exon_id = df.exon_id.map(lambda v: v[:15])
    df.gene_id = df.gene_id.map(lambda v: v[:15])
    df.transcript_id = df.transcript_id.map(lambda v: v[:15])

    # only take protein_coding genes/transcripts/exons
    df = df[
        (df['gene_type'] == 'protein_coding') &
        (df['feature'].isin(['gene', 'transcript', 'exon', 'UTR'])) &
        (df['seqname'].isin(CHROMOSOMES))]
    # drop all transcripts and exons that have no protein_id
    df.drop(df.index[(df.protein_id == '') & (
        df.feature.isin(['exon', 'transcript', 'UTR']))], inplace=True)

    # only take exons and transcripts which contain a basic-tag
    non_basic_transcripts = (df['feature'].isin(['transcript', 'exon', 'UTR'])) & \
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

    # drop alternative_3or5_UTR transcripts
    # df = df.drop(df.index[df.tag.str.contains('alternative_')])

    # drop all genes which have no transcripts
    valid_genes = df[df['feature'] == 'transcript'].gene_id.drop_duplicates()
    # double check, there are no orphan-exons or so
    assert set(valid_genes) == \
        set(df[df['feature'] == 'exon'].gene_id.drop_duplicates())
    df.drop(df.index[~df.gene_id.isin(valid_genes)], inplace=True)

    # select best transcript
    df = df.groupby('gene_id').apply(_filter_best_transcript)
    df.reset_index(level=0, drop=True, inplace=True)

    return df[[
        'feature', 'gene_id', 'transcript_id',
        'start', 'end', 'exon_id', 'exon_number',
        'gene_name', 'transcript_type', 'strand',
        'gene_type', 'tag', 'protein_id', 'swissprot_id',
        'score', 'seqname', 'source']]


@buffer_return_value
def celllines():
    with open(os.path.join(BASEDIR, 'pavooc/server/celllines.txt')) as f:
        return [line.strip() for line in f.readlines()]


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


def compute_canonical_exons(gene):
    exons = gene[gene.feature == 'exon']
    utrs = []
    for index, row in gene[gene.feature == 'UTR'].iterrows():
        utrs.extend(list(range(row.start, row.end)))
    utrs = set(utrs)

    sorted_exons = exons.sort_values('exon_number')
    result_exons = []

    for index, exon in sorted_exons.iterrows():
        exon_positions = set(range(exon.start, exon.end))
        filtered = (exon_positions - utrs)
        try:
            end = max(filtered) + 1
            start = min(filtered)
        except ValueError:
            continue
        else:
            new_exon = exon.copy()
            new_exon.start = start
            new_exon.end = end
            result_exons.append(new_exon)

    df = pd.DataFrame(result_exons)
    # df.index.name = 'exon_id'
    try:
        return df.reset_index()[[
            'seqname', 'start', 'end', 'strand', 'transcript_id',
            'swissprot_id', 'gene_id', 'gene_name', 'exon_id', 'exon_number']]
    except KeyError:
        logging.error(
            f'fixme at data.py canonical_exons: {gene.iloc[0].gene_id}')
        return


@buffer_return_value
def gencode_exons():
    '''

    Return the protein-coding exons from gencode, indexed by exon_id

    Deletes UTR (untranslated region)
    :returns: DataFrame with unique exons
    '''
    gencode = read_gencode()

    prepared = gencode.groupby('gene_id').apply(compute_canonical_exons)

    return prepared.set_index('exon_id')

    # OLD: (we now use simply appris principal)
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
def feature_scaler():
    return joblib.load(SCALER_FILE)


@buffer_return_value
def azimuth_model(nopos=False):
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
def cnn38_model():
    model = CNN38(160)
    model.load_state_dict(torch.load(os.path.join(DATADIR, 'cnn38.torch')))
    return model


# TODO delete
@buffer_return_value
def read_appris():
    return pd.read_csv(
        APPRIS_FILE,
        sep='\t',
        header=None,
        names=['gene_symbol', 'gene_id', 'transcript_id', 'ccds_id', 'type'],
        index_col=False).set_index('gene_id')
