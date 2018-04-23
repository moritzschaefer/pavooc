'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
from multiprocessing import Pool
import mygene

from tqdm import tqdm
import numpy as np
import pandas as pd
from skbio.sequence import DNA

from pavooc.config import GUIDES_FILE, COMPUTATION_CORES, DEBUG
from pavooc.pdb import pdb_mappings
from pavooc.util import normalize_pid, aa_cut_position, percent_peptide
from pavooc.db import guide_collection
from pavooc.data import gencode_exons, domain_interval_trees, pdb_list, \
    read_gencode, cellline_mutation_trees, cns_trees, pfam_mapping, chromosomes
from pavooc.scoring import azimuth, flashfry, pavooc


logging.basicConfig(level=logging.WARN,
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


def filter_bad_guides(guides, pavooc_score):
    # delete all guides with scores below 0.47 or with BsaI site or other
    # sequences, that hinder their function
    delete_indices = guides.index[(pavooc_score < 0.45) |
                                  (guides.target.str.startswith('GGGGG')) |
                                  (guides.target.str.contains('TTTT')) |
                                  (guides.target.str.contains('GGTCTC')) |
                                  (guides.target.str.contains('GAGACC'))]
    guides.drop(delete_indices, inplace=True)


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
        logging.warn('missing exon: {}'.format(row.exon_id))
        raise

    if isinstance(exon, pd.DataFrame):
        exon = exon[exon.seqname == chromosome]
        if len(exon.start.unique()) != 1:
            logging.error(f'same exon_id with different starts {exon}')

        exon = exon.iloc[0]

    return exon.start + row['start']


def get_domains(chromosome, strand, gene_id, gene_start, gene_end):
    domain_tree = domain_interval_trees()[chromosome]

    interval_domains = domain_tree[gene_start:gene_end]

    try:
        mygene_domains = mg.getgene(gene_id, 'pfam')['pfam']
    except TypeError:
        print(f'No MyGene information for {gene_id}')
        # wildcard
        mygene_domains = [domain[2][0] for domain in interval_domains]
    except KeyError:
        mygene_domains = []
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
        logging.warn('no guides: {}'.format(e))
        raise ValueError('No guides')
    except KeyError as e:  # exon_id from guides doesnt exist
        logging.warn('. gene: {}'.format(e, gene_id))
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
            guide_collection.find({'gene_id': gene_id}, limit=1).count() == 1:
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
    try:
        pavooc_score = pd.Series(pavooc.score(
            gene_id, guides), index=guides.index, dtype=np.float64)
    except ValueError:  # being raised when there are no conservation scores
        logging.warn(f'No pavooc score for  {gene_id}')
        pavooc_score = pd.Series(-1, index=guides.index, dtype=np.float64)

    guides_file = GUIDES_FILE.format(gene_id)
    flashfry_scores = flashfry.score(guides_file)
    flashfry_scores.fillna(0, inplace=True)

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
