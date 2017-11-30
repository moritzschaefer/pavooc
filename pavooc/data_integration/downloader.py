#!/usr/bin/env python

from urllib.request import urlretrieve
from urllib.error import HTTPError
import gzip
import logging
import os
import subprocess
import ftplib
import re
from multiprocessing.dummy import Queue, Process
import time
import tarfile

from pavooc.config import CHROMOSOMES, DATADIR, SIFTS_FILE, SIFTS_TARBALL, \
    BASEDIR, S3_BUCKET_URL

URLS = ['http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/{}.fa.gz'.format(c) for c in CHROMOSOMES] + [  # noqa
    'ftp://ftp.ebi.ac.uk/pub/databases/msd/sifts/flatfiles/csv/pdb_chain_uniprot.csv.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz',  # noqa
    'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz',  # noqa
    'https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_2013-12-03.seg.txt',  # noqa
    'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/ucscGenePfam.txt.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz',  # noqa
    'http://apprisws.bioinfo.cnio.es/pub/current_release/datafiles/homo_sapiens/GRCh37/appris_data.principal.txt',  # noqa
    'http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed',
    'http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.chrom.sizes'
]

logging.basicConfig(level=logging.INFO)


def file_download(url, target):
    '''
    Download a file with either urlretrieve or with curl

    '''

    try:
        urlretrieve(url, target)
    except HTTPError:
        result = subprocess.run(['curl', '-o',
                                 target,
                                 url])
        if result.returncode != 0:
            raise RuntimeError(result.stderr)


def download_unzip(url):
    download_filename = os.path.basename(url)
    download_target = os.path.join(DATADIR, download_filename)

    if os.path.exists(os.path.join(DATADIR, download_filename)):
        logging.warn('{} already exists. Skipping download. Delete files first \
                to force download'.format(download_filename))
        return
    logging.info('downloading {}'.format(url))

    # check if file exists on our S3 bucket first, then download from source
    try:
        file_download(S3_BUCKET_URL.format(download_filename), download_target)
    except RuntimeError as e:
        print('download failed with error {}'.format(e))
        file_download(url, download_target)

    logging.info('unpacking {}'.format(download_filename))
    if download_filename[-3:] == '.gz':
        with gzip.open(os.path.join(DATADIR, download_filename), 'rb') as gz_file:
            file_content = gz_file.read()
        with open(os.path.join(DATADIR, download_filename[:-3]), 'wb') as datafile:
            datafile.write(file_content)


def download_ftp(queue):
    ftp = ftplib.FTP("ftp.ebi.ac.uk")
    ftp.login()
    ftp.cwd('/pub/databases/msd/sifts/xml')
    while not queue.empty():
        filename = queue.get()
        if not re.match('[0-9a-z]{4}\.xml\.gz', filename):
            continue
        target_filename = SIFTS_FILE.format(filename)
        if os.path.exists(target_filename):
            continue
        with open(target_filename, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
    ftp.quit()


def download_sifts():
    # download all sift files

    # first try to download a tarball containing all the sift xmls

    if not os.path.exists(SIFTS_TARBALL):
        try:
            urlretrieve(
                S3_BUCKET_URL.format('sifts.tar'),
                SIFTS_TARBALL)
        except RuntimeError:
            logging.warning('failed downloading sifts tarball')
        else:
            tf = tarfile.TarFile(SIFTS_TARBALL)
            tf.extractall(BASEDIR)  # the tarball contains directory data/sifts

    try:
        os.mkdir(SIFTS_FILE.format(''))
    except FileExistsError:
        pass
    ftp = ftplib.FTP("ftp.ebi.ac.uk")
    ftp.login()
    ftp.cwd('/pub/databases/msd/sifts/xml')
    filenames = ftp.nlst()  # get filenames within the directory
    ftp.quit()  # This is the “polite” way to close a connection
    filename_queue = Queue()
    for filename in filenames:
        filename_queue.put(filename)

    ftp_processes = [Process(target=download_ftp, args=(
        filename_queue,)) for _ in range(10)]
    for process in ftp_processes:
        process.start()

    while not filename_queue.empty():
        print('{}/{} sifts downloaded'.format(len(filenames) -
                                              filename_queue.qsize(), len(filenames)))
        time.sleep(1)

    for process in ftp_processes:
        process.join()


def main():
    for url in URLS:
        download_unzip(url)

    download_sifts()


if __name__ == "__main__":
    main()
