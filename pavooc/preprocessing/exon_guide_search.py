import subprocess
import logging
import os

from pavooc.config import JAVA_RAM, FLASHFRY_DB_FILE, EXON_DIR
from pavooc.gencode import read_gencode

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s')


def generate_exon_guides(gene):
    gene_file = os.path.join(EXON_DIR, gene)
    target_file = os.path.join(EXON_DIR, '{}.guides'.format(gene))
    subprocess.Popen([
            'java',
            '-Xmx{}g'.format(JAVA_RAM),
            '-jar', 'FlashFry-assembly-1.6.jar',
            '--analysis', 'discover',
            '--fasta', gene_file,
            '--output', target_file,
            '--maxMismatch', '5',
            '--positionOutput=true',
            '--database', FLASHFRY_DB_FILE
            ]).wait()


def main():
    relevant_genes = read_gencode()[
            (read_gencode()['feature'] == 'gene') &
            (read_gencode()['gene_type'] == 'protein_coding')
    ]
    i = 0
    for _, row in relevant_genes.iterrows():
        logging.info('{}/{} Generate guides for {}.'.format(
            i,
            len(relevant_genes),
            row['gene_id'])
        )
        generate_exon_guides(row['gene_id'])
        i += 1


if __name__ == "__main__":
    main()
