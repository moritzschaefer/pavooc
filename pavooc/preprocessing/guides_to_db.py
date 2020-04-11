'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
import time
import os
from multiprocessing import Pool

import mygene
import numpy as np
import pandas as pd
from requests.exceptions import ConnectionError
from skbio.sequence import DNA
from tqdm import tqdm

from pavooc.config import COMPUTATION_CORES, DEBUG, GENOME, GUIDES_FILE, DATADIR
from pavooc.data import (cellline_mutation_trees, chromosomes, cns_trees,
                         domain_interval_trees, gencode_exons, pdb_list,
                         pfam_mapping, read_gencode, cs_pfam_domains, gencode_cds_exons)
from pavooc.db import guide_collection
from pavooc.pdb import pdb_mappings
from pavooc.scoring import azimuth, flashfry  # , pavooc
from pavooc.util import aa_cut_position, normalize_pid, percent_peptide

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(asctime)s %(message)s')


mg = mygene.MyGeneInfo()


def _context_guide(exon_id, start, guide_direction, chromosome, context_length=5):
    '''
    :exon_id: ensembl id
    :start: bp position start of guide(!) relative to chromosome
    :guide_direction: either 'FWD' or 'RVS'
    :chromosome: the chromosome this is on
    :context_length: option to adjust padding in bps TODO: implement
    :returns: azimuth compliant context 30mers (that is 5bp+protospacer+5bp) in
        capital letters
    '''
    exon = gencode_exons().loc[exon_id]

    if isinstance(exon, pd.DataFrame):
        exon = exon[exon.seqname == chromosome]
        if len(exon.start.unique()) != 1:
            logging.error(f'azimuth.py: same exon_id with different starts {exon}')
        exon = exon.iloc[0]

    if guide_direction == 'RVS':
        start -= 3
    else:
        start -= 4

    seq = chromosomes()[exon['seqname']
                        ][start:start + 30].upper()

    # if the strands don't match, it needs to be reversed
    if guide_direction == 'RVS':
        seq = str(DNA(seq).reverse_complement())

    assert seq[25:27] == 'GG', \
        'the generated context is invalid (PAM) site. {}, {}, {}'.format(
        seq, exon['strand'], guide_direction)
    return seq


def filter_bad_guides(guides, score):
    # delete all guides with scores below 0.45 or with some sequence that hinder their function
    delete_indices = guides.index[(score < 0.45) |
                                  (guides.target.str.startswith('GGGGG')) |
                                  (guides.target.str.contains('TTTT'))]
    guides.drop(delete_indices, inplace=True)


def cns_affection(exons):
    '''
    :returns: boolean whether the gene is affected by a CNS or not
    '''
    if GENOME != 'hg19':
        return []
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
    if GENOME != 'hg19':
        return []
    mutations = [mut[2]['cellline'] for mut in
                 cellline_mutation_trees()[chromosome][position:position + 23]]
    return mutations


def pdbs_for_gene(gene_id):
    gencode = read_gencode()
    pdbs = pdb_list()
    try:
        protein_ids = gencode.loc[(gencode['gene_id'] == gene_id)
                                ]['swissprot_id'].drop_duplicates().replace("", float('NaN')).dropna()
    except KeyError:
        return pd.DataFrame()

    canonical_pids = np.unique([normalize_pid(pid)
                                for pid in protein_ids if pid]).astype('O')
    if len(canonical_pids) > 1:
        logging.warning('Gene {} has {} "canonical" protein ids: {}"'.format(
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
            lambda mappings: min(mappings.values()))
        gene_pdbs['end'] = gene_pdbs['mappings'].apply(
            lambda mappings: max(mappings.values()) + 1)  # end is contained
        gene_pdbs['mappings'] = gene_pdbs['mappings'].apply(
            lambda mappings: {str(key): value
                              for key, value in mappings.items()})

    return gene_pdbs


# TODO DRY with azimuth.py:20
def _absolute_position(row, chromosome):
    try:
        exon = gencode_exons().loc[row.exon_id]
    except KeyError:
        logging.warning('missing exon: {}'.format(row.exon_id))
        raise

    if isinstance(exon, pd.DataFrame):
        exon = exon[exon.seqname == chromosome]
        if len(exon.start.unique()) != 1:
            logging.error(f'same exon_id with different starts {exon}')

        exon = exon.iloc[0]

    return exon.start + row['start']


def get_cs_domains(chromosome, strand, gene_id, gene_start, gene_end):
    gencode = read_gencode()
    try:
        gene = gencode.loc[(gencode['gene_id'] == gene_id)]
        protein_id = gene['swissprot_id'].drop_duplicates().replace('',  float("NaN")).dropna().iloc[0]
        strand = gene.iloc[0]['strand']
        exons = gencode_exons().loc[gencode_exons().gene_id == gene_id]
        cds_exons = gencode_cds_exons().loc[gencode_cds_exons().gene_id == gene_id]
    except KeyError:
        logging.debug(f'KeyError for {gene_id}')
        return []

    logging.debug(f'{gene_id} uses protein "{protein_id}"')

    cs_domains = cs_pfam_domains()

    domains = cs_domains.loc[cs_domains['seq id'] == protein_id]

    # traverse the gene to map domains to genome positions
    # note: this spans over introns also..
    def _project_domain(domain):
        offset = 0
        align_start = (domain['alignment start']) * 3
        align_end = domain['alignment end'] * 3
        align_length = align_end - align_start

        for _, exon in cds_exons.sort_values('exon_number').iterrows():  # exons are sorted already
            exon_length = (exon.end - exon.start)
            if offset <= align_start and align_start < (offset + exon_length):  # align_start is within exon
                if strand == '+':
                    in_exon_start = exon.start + (align_start - offset)
                else:
                    in_exon_end = exon.end - (align_start - offset)
            if offset <= align_end and (offset + exon_length) >= align_end:  # align_end is within this exon
                if strand == '+':
                    in_exon_end = exon.start + (align_end - offset)
                    break
                else:
                    in_exon_start = exon.end  - (align_end - offset)
                    break

            offset += exon_length
        try:
            in_exon_start
        except NameError:
            print('warning nameError start!!')
            in_exon_start = cds_exons['start'].min()
        try:
            in_exon_end
        except NameError:
            in_exon_end = cds_exons['end'].max()
            print('warning nameError end!!')

        return {'name': domain['hmm name'],
                'start': in_exon_start,
                'end': in_exon_end}

    return ([_project_domain(domain) for index, domain in domains.iterrows()])


def get_domains(chromosome, strand, gene_id, gene_start, gene_end):
    if 'cs' in GENOME:
        return get_cs_domains(chromosome, strand, gene_id, gene_start, gene_end)
    domain_tree = domain_interval_trees()[chromosome]

    interval_domains = domain_tree[gene_start:gene_end]

    mygene_domains = None
    while mygene_domains is None:
        try:
            mygene_domains = mg.getgene(gene_id, 'pfam')['pfam']
        except TypeError:
            print(f'No MyGene information for {gene_id}')
            # wildcard
            mygene_domains = [domain[2][0] for domain in interval_domains]
        except KeyError:
            mygene_domains = []
        except ConnectionError:
            logging.warning('There was an error accessing mygene. Waiting 5 seconds and retrying')
            time.sleep(5)
        else:
            if type(mygene_domains) != list:
                mygene_domains = [mygene_domains]

    pfam_names = set(
        [pfam_mapping().loc[pfam_acc].PFAM_Name
            for pfam_acc in mygene_domains
            if pfam_acc in pfam_mapping().index])

    # filter for domains in the correct direction
    domains = [{'name': domain[2][0], 'start': domain[0], 'end': domain[1]}
               for domain in interval_domains
               if domain[2][1] == strand
               and domain[2][0] in pfam_names]

    return domains


def load_guides(gene_id, exons):
    chromosome = exons.iloc[0]['seqname']
    strand = exons.iloc[0]['strand']
    try:
        guides = pd.read_csv(GUIDES_FILE.format(
            gene_id), sep='\t', index_col=False)
    except Exception as e:
        logging.fatal('Couldn\'t load guides file for {}: {}'
                      .format(gene_id, e))
        return None

    guides['exon_id'] = guides['contig'].apply(lambda v: v.split(';')[0])

    # delete padding introduced before guide-finding (flashfry)
    guides['start'] -= 16
    guides['in_exon_start'] = guides['start']

    try:
        guides['start'] = guides.apply(
            lambda row: _absolute_position(row, chromosome), axis=1)
        guides['cut_position'] = guides.apply(
            lambda row: row['start'] +
            (7 if row['orientation'] == 'RVS' else 16),
            axis=1)
    except ValueError as e:  # guides is empty and apply returned a DataFrame
        logging.warning('no guides: {}'.format(e))
        raise ValueError('No guides')
    except KeyError as e:  # exon_id from guides doesnt exist
        logging.warning('. gene: {}'.format(e, gene_id))
        return None

    # AA number of canonical transcript cut position for each guide
    # TODO we should check early if no guides exist and just return None or so.
    guides['aa_cut_position'] = guides.apply(
        lambda row: aa_cut_position(row, exons), axis=1)

    gene_start = exons['start'].min()
    gene_end = exons['end'].max()
    guides['percent_peptide'] = guides.apply(
        lambda row: percent_peptide(row, gene_start, gene_end, strand),
        axis=1)

    guides['context'] = guides.apply(lambda row: _context_guide(
        row['exon_id'],
        row['start'],
        row['orientation'],
        chromosome), axis=1)

    # find CDS for transcript_id and filter start and end
    # this is a workaround, since I was too stupid to not just use the CDS (instead of exons) right away.. :/
    cds_exons = gencode_cds_exons().loc[gencode_cds_exons().gene_id == gene_id]
    filter_offguides = (cds_exons['start'].min() < guides.start) & (guides.start + 23 < cds_exons['end'].max())   # guides that are within the gene sequence
    if filter_offguides.sum() < len(guides):
        # print(f'Filtered {(~filter_offguides).sum()} guides outside of the CDS')
        pass
    guides = guides.loc[filter_offguides]

    return guides


def build_gene_document(gene, check_exists=True):
    '''
    Compute all necessary data (scores for example) and return a document for
    the gene
    '''

    gene_id, exons = gene
    chromosome = exons.iloc[0]['seqname']
    strand = exons.iloc[0]['strand']
    gene_symbol = exons.iloc[0]['gene_name']
    if check_exists and \
            guide_collection.find({'gene_id': gene_id, 'genome': GENOME}, limit=1).count() == 1:
        # item exists
        return None
    try:
        guides = load_guides(gene_id, exons)
    except ValueError:
        return None
    gene_start = exons['start'].min()
    gene_end = exons['end'].max()

    logging.info('calculating azimuth score for {}'.format(gene_id))
    try:
        azimuth_score = pd.Series(azimuth.score(
            guides, chromosome), index=guides.index)
    except ValueError as e:
        guides.to_csv(f'{gene_id}.csv')
        logging.error(
            f'Gene {gene_id} had problems. saved {gene_id}.csv. Error: {e}')
        azimuth_score = pd.Series(0, index=guides.index)
    logging.info('calculating pavooc score for {}'.format(gene_id))

    guides_file = GUIDES_FILE.format(gene_id)
    flashfry_scores = flashfry.score(guides_file)
    flashfry_scores.fillna(0, inplace=True)
    try:
        raise ValueError  # we don't want pavooc score for now..
        pavooc_score = pd.Series(pavooc.score(
            gene_id, guides), index=guides.index, dtype=np.float64)
    except ValueError:  # being raised when there are no conservation scores
        # logging.warning(f'No pavooc score for  {gene_id}')
        pavooc_score = pd.Series(-1, index=guides.index, dtype=np.float64)
        filter_bad_guides(guides, azimuth_score)
    else:
        filter_bad_guides(guides, pavooc_score)

    logging.info(
        'Insert gene {} with its data into mongodb'.format(gene_id))

    # transform dataframe to list of dicts and extract scores into
    # a nested format
    guides_list = [{
        **row[
            ['exon_id', 'start', 'orientation', 'otCount', 'target',
                'cut_position', 'aa_cut_position']].to_dict(),
        'mutations': guide_mutations(chromosome, row['start']),
        'scores': {**flashfry_scores.loc[index][
            ['Doench2014OnTarget', 'Doench2016CFDScore',
             'dangerous_GC', 'dangerous_polyT',
             'dangerous_in_genome', 'Hsu2013']].to_dict(),
            'azimuth': azimuth_score.loc[index],
            'pavooc': pavooc_score.loc[index]}
    } for index, row in guides.iterrows() if index in flashfry_scores.index]

    return {
        'gene_id': gene_id,
        'gene_symbol': gene_symbol,
        'cns': cns_affection(exons),
        'strand': strand,
        'pdbs': list(pdbs_for_gene(gene_id).T.to_dict().values()),
        'chromosome': exons.iloc[0]['seqname'],
        'exons': list(exons.reset_index()[['start', 'end', 'exon_id']]
                      .T.to_dict().values()),
        'domains': get_domains(chromosome, strand, gene_id, gene_start,
                               gene_end),
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
                    doc['genome'] = GENOME
                    guide_collection.insert_one(doc)
    else:
        for gene in tqdm(gencode_genes, total=len(gencode_genes)):
            doc = build_gene_document(gene)
            if doc:
                doc['genome'] = GENOME
                guide_collection.insert_one(doc)


def main():
    integrate()


if __name__ == "__main__":
    main()
