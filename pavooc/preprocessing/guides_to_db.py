'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
from multiprocessing import Pool

from tqdm import tqdm
import numpy as np
import pandas as pd

from pavooc.config import GUIDES_FILE, COMPUTATION_CORES, DEBUG
from pavooc.pdb import pdb_mappings
from pavooc.util import normalize_pid
from pavooc.db import guide_collection
from pavooc.data import gencode_exons, domain_interval_trees, pdb_list, \
    read_gencode, cellline_mutation_trees, cns_trees
from pavooc.scoring import azimuth, flashfry

logging.basicConfig(level=logging.WARN,
                    format='%(levelname)s %(asctime)s %(message)s')


def cns_affection(exons):
    '''
    :returns: boolean whether the gene is affected by a CNS or not
    '''
    chromosome = exons.iloc[0].seqname
    start = exons.start.min()
    end = exons.end.max()
    return [v[2]['cellline'] for v in cns_trees()[chromosome][start:end]]


def guide_mutations(chromosome, position):
    '''
    :returns: an array of mutations. each mutation is presented as
    a dict with fields start, end and type
    '''
    # return [{'start': mut[0], 'end': mut[1], **mut[2]}
    #         for mut in
    #         cellline_mutation_trees[chromosome][position:position + 23]]
    # as long as other datais not necessary, we just return the cellline
    # TODO add CNS?
    mutations = [mut[2]['cellline'] for mut in
                 cellline_mutation_trees()[chromosome][position:position + 23]]
    return mutations


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


def _absolute_position(row):
    try:
        exon = gencode_exons().loc[row.exon_id]
    except KeyError:
        logging.warn('missing exon: {}'.format(row.exon_id))
        raise

    if isinstance(exon, pd.DataFrame):
        if len(exon.start.unique()) != 1:
            logging.error(f'same exon_id with different starts {exon}')
        exon = exon.iloc[0]

    return exon.start + row['start']


def build_gene_document(gene, check_exists=True):
    '''
    Compute all necessary data (scores for example) and return a document for
    the gene
    '''

    gene_id, exons = gene
    chromosome = exons.iloc[0]['seqname']
    if check_exists and \
            guide_collection.find({'gene_id': gene_id}, limit=1).count() == 1:
        # item exists
        return None
    strand = exons.iloc[0]['strand']
    gene_symbol = exons.iloc[0]['gene_name']
    try:
        guides = pd.read_csv(GUIDES_FILE.format(
            gene_id), sep='\t', index_col=False)
    except Exception as e:
        logging.fatal('Couldn\'t load guides file for {}: {}'
                      .format(gene_id, e))
        return None
    # TODO, we can get transcription-ids here (as in preprocessing.py)
    unique_exons = exons.groupby('exon_id').first().reset_index()[
        ['start', 'end', 'exon_id']]

    guides['exon_id'] = guides['contig'].apply(lambda v: v.split(';')[0])

    # delete padding introduced before guide-finding (flashfry)
    guides['start'] -= 16
    guides['in_exon_start'] = guides['start']

    try:
        guides['start'] = guides.apply(_absolute_position, axis=1)
        guides['cut_position'] = guides.apply(
            lambda row: row['start'] +
            (7 if row['orientation'] == 'RVS' else 16),
            axis=1)
    except ValueError as e:  # guides is empty and apply returned a DataFrame
        logging.warn('no guides: {}'.format(e))
        guides['start'] = []
        guides['cut_position'] = []
    except KeyError as e:  # exon_id from guides doesnt exist
        logging.warn('. gene: {}'.format(e, gene_id))
        return None

    logging.info('calculating azimuth score for {}'.format(gene_id))
    try:
        azimuth_score = pd.Series(azimuth.score(guides), index=guides.index)
    except ValueError as e:
        guides.to_csv(f'{gene_id}.csv')
        logging.error(
            f'Gene {gene_id} had problems. saved {gene_id}.csv. Error: {e}')
        azimuth_score = pd.Series(0, index=guides.index)
    # TODO add amino acid cut position and percent peptides
    logging.info(
        'Insert gene {} with its data into mongodb'.format(gene_id))

    domain_tree = domain_interval_trees()[chromosome]
    gene_start = exons['start'].min()
    gene_end = exons['end'].max()

    interval_domains = domain_tree[gene_start:gene_end]
    # filter for domains in the correct direction
    domains = [{'name': domain[2][0], 'start': domain[0], 'end': domain[1]}
               for domain in interval_domains
               if domain[2][1] == strand]

    # AA number of canonical transcript cut position for each guide
    try:
        guides['aa_cut_position'] = guides.apply(
            lambda row: aa_cut_position(row, exons), axis=1)
    except ValueError:  # guides is empty and apply returned a DataFrame
        guides['aa_cut_position'] = []


    guides_file = GUIDES_FILE.format(gene_id)
    flashfry_scores = flashfry.score(guides_file)
    flashfry_scores.fillna(0, inplace=True)

    # delete all guides with scores below 0.57
    # TODO use something more sophisticated
    guides.drop(guides.index[azimuth_score < 0.57], inplace=True)

    # transform dataframe to list of dicts and extract scores into
    # a nested format
    guides_list = [{
        **row[
            ['exon_id', 'start', 'orientation', 'otCount', 'target',
                'cut_position', 'aa_cut_position']].to_dict(),
        'mutations': guide_mutations(chromosome, gene_start + row['start']),
        'scores': {**flashfry_scores.loc[index][
            ['Doench2014OnTarget', 'Doench2016CFDScore',
             'dangerous_GC', 'dangerous_polyT',
             'dangerous_in_genome', 'Hsu2013']].to_dict(),
            'azimuth': azimuth_score.loc[index]}
    } for index, row in guides.iterrows() if index in flashfry_scores.index]

    return {
        'gene_id': gene_id,
        'gene_symbol': gene_symbol,
        'cns': cns_affection(exons),
        'strand': strand,
        'pdbs': list(pdbs_for_gene(gene_id).T.to_dict().values()),
        'chromosome': exons.iloc[0]['seqname'],
        'exons': list(unique_exons.T.to_dict().values()),
        'domains': domains,
        'guides': guides_list
    }


def integrate():
    # TODO make a CLI switch or so to drop or not drop..
    if DEBUG:
        guide_collection.drop()
    gencode_genes = gencode_exons().groupby('gene_id')

    if COMPUTATION_CORES > 1:
        with Pool(COMPUTATION_CORES) as pool:
            for doc in tqdm(pool.imap_unordered(
                    build_gene_document,
                    gencode_genes), total=len(gencode_genes)):
                if doc:
                    guide_collection.insert_one(doc)
    else:
        for gene in tqdm(gencode_genes, total=len(gencode_genes)):
            doc = build_gene_document(gene)
            if doc:
                guide_collection.insert_one(doc)


def main():
    integrate()


if __name__ == "__main__":
    main()
