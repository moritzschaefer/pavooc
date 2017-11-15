'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
from multiprocessing import Pool

from tqdm import tqdm
import numpy as np
import pandas as pd

from pavooc.config import GUIDES_FILE, COMPUTATION_CORES
from pavooc.util import read_guides, normalize_pid
from pavooc.db import guide_collection
from pavooc.data import gencode_exons, domain_interval_trees, pdb_data, \
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
    for canonical_exon in canonical_exons:
        if guide.cut_position >= canonical_exon['start'] and \
                guide.cut_position < canonical_exon['end']:
            return (bp_position +
                    (guide.cut_position - canonical_exon['start'])) // 3

        exon_length_bp = (canonical_exon['end'] - canonical_exon['start'])
        bp_position += exon_length_bp
    return -1


def compute_canonical_exons(gene_id, exons):
    try:
        transcript_id = read_appris().loc[gene_id[:15]].transcript_id

        cexons = exons.loc[
            exons.transcript_id.map(lambda t: t[:15]) == transcript_id]. \
            reset_index()[
            ['start', 'end', 'exon_id']]
        return list(cexons.T.to_dict().values())
    except Exception as e:
        logging.error('Failed finding canonical exons: {}'.format(e))
    return []


def pdbs_for_gene(gene_id):
    gencode = read_gencode()
    pdbs = pdb_data()
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

    try:
        return list(pdbs.loc[pdbs.SP_PRIMARY.isin(canonical_pids)].T.
                    to_dict().values())
    except Exception as e:
        import ipdb
        ipdb.set_trace()


def _cut_position(row):
    exon = gencode_exons().loc[row.exon_id]

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

    return {
        'gene_id': gene_id,
        'strand': strand,
        'pdbs': pdbs_for_gene(gene_id),
        'chromosome': exons.iloc[0]['seqname'],
        'canonical_exons': canonical_exons,
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
