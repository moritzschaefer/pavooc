'''
load guides-files (filtered FlashFry output) and integrate
into mongoDB
'''
import logging

import pandas as pd

from pavooc.config import GUIDES_FILE
from pavooc.db import guide_collection
from pavooc.gencode import gencode_exons_gene_grouped


def integrate():
    guide_collection.drop()
    for gene_id, exons in gencode_exons_gene_grouped():

        # TODO, we can get transcription-ids here (as in preprocessing.py)
        unique_exons = exons.groupby('exon_id').first().reset_index()[
                ['start', 'end', 'exon_id', 'strand']]

        try:
            guides = pd.read_csv(GUIDES_FILE.format(gene_id), sep='\t')
        except Exception as e:
            logging.fatal('Couldn\'t load guides file for {}: {}'
                          .format(gene_id, e))
            continue
        guides['exon_id'] = guides['contig'].apply(lambda x: x.split(';'[0]))
        # TODO add scores here and stuff
        guide_collection.insert_one({
            'gene_id': gene_id,
            'chromosome': exons.iloc[0]['seqname'],
            'exons': list(unique_exons.T.to_dict().values()),
            'guides': list(guides[['exon_id', 'start', 'orientation', 'otCount']].T.to_dict().values()),
            'score': -1.0
            })


def main():
    integrate()


if __name__ == "__main__":
    main()
