#!/usr/bin/env python

from urllib.request import urlretrieve
from urllib.error import HTTPError
import gzip
import logging
import os
import subprocess

from pavooc.config import CHROMOSOMES, DATADIR

URLS=['http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/{}.fa.gz'.format(c) for c in CHROMOSOMES]  + [  # noqa
    'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz',  # noqa
    'https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_byGene_2013-12-03.txt.gz'  # noqa
    'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/ucscGenePfam.txt.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz'  # noqa
]

logging.basicConfig(level=logging.INFO)


def download_unzip(url):
    download_filename = os.path.basename(url)

    if os.path.exists(os.path.join(DATADIR, download_filename)):
        logging.warn('{} already exists. Skipping download. Delete files first \
                to force download'.format(download_filename))
        return
    logging.info('downloading {}'.format(url))

    try:
        urlretrieve(url, os.path.join(DATADIR, download_filename))
    except HTTPError:
        subprocess.Popen(['curl', '-o',
                          os.path.join(DATADIR, download_filename),
                          url]).wait()

    logging.info('unpacking {}'.format(download_filename))
    if download_filename[-3:] == '.gz':
        with gzip.open(os.path.join(DATADIR, download_filename), 'rb') as gz_file:
            file_content = gz_file.read()
        with open(os.ptah.join(DATADIR, download_filename[:-3]), 'wb') as datafile:
            datafile.write(file_content)


def main():
    for url in URLS:
        download_unzip(url)


if __name__ == "__main__":
    main()
