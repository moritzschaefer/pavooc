'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging
from multiprocessing import Pool

from pavooc.config import GUIDES_FILE, COMPUTATION_CORES
from pavooc.util import read_guides
from pavooc.db import guide_collection
from pavooc.data import gencode_exons, domain_interval_trees
from pavooc.scoring import azimuth

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s')


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
    # revert padding introduced before guide-finding (flashfry)
    guides['start'] -= 16

    guides['exon_id'] = guides['contig'].apply(lambda v: v.split(';')[0])
    # TODO add scores here and stuff
    # delete 16 due to padding in exon_files
    logging.info('calculating azimuth score for {}'.format(gene_id))
    try:
        guides['score'] = azimuth.score(guides)
    except Exception as e:
        import ipdb
        ipdb.set_trace()
    # TODO add amino acid cut position and percent peptides
    logging.info(
            'Insert gene {} with its data into mongodb'.format(gene_id))

    domain_tree = domain_interval_trees()[exons.iloc[0]['seqname']]

    interval_domains = domain_tree[exons['start'].min():exons['end'].max()]
    # filter for domains in the correct direction
    domains = [{'name': domain[2][0], 'start': domain[0], 'end': domain[1]}
               for domain in interval_domains
               if domain[2][1] == strand]

    return {
        'gene_id': gene_id,
        'strand': strand,
        'chromosome': exons.iloc[0]['seqname'],
        'exons': list(unique_exons.T.to_dict().values()),
        'domains': domains,
        'guides':
        list(guides[
            ['exon_id', 'start', 'orientation', 'otCount', 'score', 'target']
            ].T.to_dict().values()),
    }


def integrate():
    guide_collection.drop()

    if COMPUTATION_CORES > 1:
        with Pool(COMPUTATION_CORES) as pool:
            for doc in pool.imap_unordered(
                    build_gene_document,
                    gencode_exons.groupby('gene_id')):
                if doc:
                    guide_collection.insert_one(doc)
    else:
        for gene in gencode_exons.groupby('gene_id'):
            doc = build_gene_document(gene)
            if doc:
                guide_collection.insert_one(doc)


def main():
    integrate()


if __name__ == "__main__":
    main()
