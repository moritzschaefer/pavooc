'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
from multiprocessing import Pool
import json

from tqdm import tqdm
import numpy as np
import pandas as pd

from pavooc.config import GUIDES_FILE, COMPUTATION_CORES
from pavooc.pdb import pdb_mappings
from pavooc.util import read_guides, normalize_pid
from pavooc.db import guide_collection
from pavooc.data import gencode_exons, domain_interval_trees, pdb_list, \
    read_gencode, read_appris
from pavooc.scoring import azimuth

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s')


def aa_cut_position(guide, canonical_exons):
    '''
    iterate over canonical exons, incrementing AA counter, looking for
    whether the cut_position is inside one of them or not.
    :returns: either the AA cut-position ith the canonical exon sequence
        or -1

    # TODO does this work for REVERSE strand?
    '''
    bp_position = 0
    for index, canonical_exon in canonical_exons.iterrows():
        if guide.cut_position >= canonical_exon['start'] and \
                guide.cut_position < canonical_exon['end']:
            return (bp_position +
                    (guide.cut_position - canonical_exon['start'])) // 3

        exon_length_bp = (canonical_exon['end'] - canonical_exon['start'])
        bp_position += exon_length_bp
    return -1


def compute_canonical_exons(gene_id, exons):
    try:
        return exons.reset_index()[['start', 'end', 'exon_id']]
    except Exception as e:
        logging.error('Failed finding canonical exons: {}'.format(e))
    return pd.DataFrame()


def pdbs_for_gene(gene_id):
    gencode = read_gencode()
    pdbs = pdb_list()
    protein_ids = gencode.loc[(gencode['gene_id'] == gene_id)
                              ]['swissprot_id'].drop_duplicates().dropna()

    canonical_pids = np.unique([normalize_pid(pid)
                                for pid in protein_ids if pid]).astype('O')
    if len(canonical_pids) > 1:
        logging.warn('Gene {} has {} "canonical" protein ids: {}"'.format(
            gene_id,
            len(canonical_pids),
            canonical_pids
        ))

    gene_pdbs = pdbs.loc[pdbs.SP_PRIMARY.isin(
        canonical_pids)][['PDB', 'SP_PRIMARY', 'CHAIN']].copy()
    gene_pdbs.columns = ['pdb', 'swissprot_id', 'chain']

    if len(gene_pdbs) > 0:
        # mappings from swissprot-coordinate to pdb-index
        gene_pdbs['mappings'] = gene_pdbs.apply(
            lambda row: pdb_mappings(row.pdb, row.chain, row.swissprot_id),
            axis=1)

        empty_mappings = gene_pdbs['mappings'].apply(len) == 0
        if empty_mappings.any():
            logging.warning('No PDB mapping for {}'.format(
                gene_pdbs[empty_mappings].pdb))
            gene_pdbs.drop(gene_pdbs.index[empty_mappings], inplace=True)

        gene_pdbs['start'] = gene_pdbs['mappings'].apply(
            lambda mappings: min(mappings.keys()))
        gene_pdbs['end'] = gene_pdbs['mappings'].apply(
            lambda mappings: max(mappings.keys()))
        gene_pdbs['mappings'] = gene_pdbs['mappings'].apply(
            lambda mappings: {str(key): value
                              for key, value in mappings.items()})

    return gene_pdbs


def _cut_position(row):
    try:
        exon = gencode_exons().loc[row.exon_id]
    except KeyError:
        import ipdb
        ipdb.set_trace()

    if isinstance(exon, pd.DataFrame):
        assert len(exon.start.unique()) == 1, \
            'same exon_id with different starts'
        exon = exon.iloc[0]

    return exon.start + row['start'] + \
        (7 if row['orientation'] == 'RVS' else 16)


def build_gene_document(gene):
    '''
    Compute all necessary data (scores for example) and return a document for
    the gene
    '''
    gene_id, exons = gene
    strand = exons.iloc[0]['strand']
    gene_symbol = exons.iloc[0]['gene_name']
    try:
        guides = read_guides(GUIDES_FILE.format(gene_id))
    except Exception as e:
        logging.fatal('Couldn\'t load guides file for {}: {}'
                      .format(gene_id, e))
        return None
    # TODO, we can get transcription-ids here (as in preprocessing.py)
    unique_exons = exons.groupby('exon_id').first().reset_index()[
        ['start', 'end', 'exon_id']]

    # delete padding introduced before guide-finding (flashfry)
    guides['start'] -= 16

    guides['exon_id'] = guides['contig'].apply(lambda v: v.split(';')[0])

    try:
        guides['cut_position'] = guides.apply(_cut_position, axis=1)
    except ValueError as e:  # guides is empty and apply returned a DataFrame
        print('no guides: {}'.format(e))
        guides['cut_position'] = []
    # TODO add scores here and stuff
    logging.info('calculating azimuth score for {}'.format(gene_id))
    guides['score'] = azimuth.score(guides)
    # TODO add amino acid cut position and percent peptides
    logging.info(
        'Insert gene {} with its data into mongodb'.format(gene_id))

    domain_tree = domain_interval_trees()[exons.iloc[0]['seqname']]

    interval_domains = domain_tree[exons['start'].min():exons['end'].max()]
    # filter for domains in the correct direction
    domains = [{'name': domain[2][0], 'start': domain[0], 'end': domain[1]}
               for domain in interval_domains
               if domain[2][1] == strand]

    canonical_exons = compute_canonical_exons(gene_id, exons)
    # AA number of canonical transcript cut position for each guide
    try:
        guides['aa_cut_position'] = guides.apply(
            lambda row: aa_cut_position(row, canonical_exons), axis=1)
    except ValueError:  # guides is empty and apply returned a DataFrame
        guides['aa_cut_position'] = []

    # delete all guides with scores below 0.5
    # TODO use something more sophisticated
    guides.drop(guides.index[guides['score'] < 0.5], inplace=True)

    return {
        'gene_id': gene_id,
        'gene_symbol': gene_symbol,
        'strand': strand,
        'pdbs': list(pdbs_for_gene(gene_id).T.to_dict().values()),
        'chromosome': exons.iloc[0]['seqname'],
        'canonical_exons': list(canonical_exons.T.to_dict().values()),
        'exons': list(unique_exons.T.to_dict().values()),
        'domains': domains,
        'guides':
        list(guides[
            ['exon_id', 'start', 'orientation', 'otCount', 'score', 'target',
                'cut_position', 'aa_cut_position']
        ].T.to_dict().values()),
    }


def integrate():
    guide_collection.drop()

    if COMPUTATION_CORES > 1:
        with Pool(COMPUTATION_CORES) as pool:
            for doc in tqdm(pool.imap_unordered(
                    build_gene_document,
                    gencode_exons().groupby('gene_id'))):
                if doc:
                    guide_collection.insert_one(doc)
    else:
        for gene in tqdm(gencode_exons().groupby('gene_id')):
            doc = build_gene_document(gene)
            if doc:
                guide_collection.insert_one(doc)


def main():
    integrate()


if __name__ == "__main__":
    main()
