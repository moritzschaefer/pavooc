import subprocess
import os

from pavooc.config import JAVA_RAM, FLASHFRY_DB_FILE, EXON_DIR
from pavooc.gencode import read_gencode


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
    for index, row in read_gencode().iterrows():
        if row['feature'] == 'gene':
            generate_exon_guides(row['gene_id'])


if __name__ == "__main__":
    main()
