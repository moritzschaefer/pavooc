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

from pavooc.config import MOUSE_CHROMOSOMES, CHROMOSOMES, DATADIR, SIFTS_FILE, SIFTS_TARBALL, \
    BASEDIR, S3_BUCKET_URL

# needed so we download all conservation scores and training doesnt fail..
ALL_HUMAN_CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']

ESSENTIAL_URLS = ['http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/{}.fa.gz'.format(c) for c in CHROMOSOMES] + [  # noqa
    S3_BUCKET_URL.format('cnn38.torch'),
    S3_BUCKET_URL.format('scaler.pkl'),
    'ftp://ftp.ebi.ac.uk/pub/databases/msd/sifts/flatfiles/csv/pdb_chain_uniprot.csv.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz',  # noqa
    'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz',  # noqa

    'https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_2013-12-03.seg.txt',  # noqa
    'https://data.broadinstitute.org/ccle/ccle2maf_081117.txt',
    'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/ucscGenePfam.txt.gz',  # noqa
    'ftp://ftp.ebi.ac.uk/pub/databases/Pfam/mappings/pdb_pfam_mapping.txt',
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz',  # noqa
    # 'http://apprisws.bioinfo.cnio.es/pub/current_release/datafiles/homo_sapiens/GRCh37/appris_data.principal.txt',  # noqa
    'http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed',
    'http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.chrom.sizes',
    'http://portals.broadinstitute.org/achilles/datasets/19/download/guide_activity_scores.tsv',  # noqa
    'http://portals.broadinstitute.org/achilles/datasets/19/download/sgRNA_mapping.tsv',  # noqa
    'https://s3-eu-west-1.amazonaws.com/pstorage-npg-968563215/7195484/13059_2016_1012_MOESM14_ESM.tsv',
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz',  # noqa # NOTE that this is based on GRCh38!!
    # for conservation scores:
    'https://s3.eu-central-1.amazonaws.com/pavoocdata/mongodump.tar.gz',
    'https://s3.eu-central-1.amazonaws.com/pavoocdata/conservations_features.csv']  # noqa <- this is the same file as being computed in the pipeline

EXTENDEND_URLS = [
    'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_27/GRCh38.p10.genome.fa.gz',  # these seem to be inaccesible. need to download from gencode now
    'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M16/GRCm38.p5.genome.fa.gz'
] + ['http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phastCons100way/hg19.100way.phastCons/{}.phastCons100way.wigFix.gz'.format(c) for c in ALL_HUMAN_CHROMOSOMES] + [
        'http://hgdownload.cse.ucsc.edu/goldenPath/mm10/phastCons60way/mm10.60way.phastCons/{}.phastCons60way.wigFix.gz'.format(c) for c in MOUSE_CHROMOSOMES]

logging.basicConfig(level=logging.INFO)


def file_download(url, target):
    '''
    Download a file with either urlretrieve or with curl

    '''

    try:
        urlretrieve(url, target)
    except HTTPError:
        result = subprocess.run(['curl', '-f', '-o',
                                 target,
                                 url])
        if result.returncode != 0:
            raise RuntimeError(result.stderr)


def download_unzip(url, append_postfix=None):
    download_filename = os.path.basename(url)
    if append_postfix:
        if download_filename[-3:] == '.gz':
            download_filename = download_filename[:-3] + append_postfix + '.gz'
        else:
            download_filename = download_filename + append_postfix

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
        print('S3 download failed with error {}'.format(e))
        file_download(url, download_target)

    logging.info('unpacking {}'.format(download_filename))
    if download_filename[-3:] == '.gz':
        with gzip.open(os.path.join(DATADIR, download_filename), 'rb') as gz_file:
            file_content = gz_file.read()
        with open(os.path.join(DATADIR, download_filename[:-3]), 'wb') as datafile:
            datafile.write(file_content)
        download_filename = download_filename[:-3]

    if download_filename[-4:] == '.tar':
        tarfile.TarFile(os.path.join(DATADIR, download_filename)).extractall(path=DATADIR)


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
                                              filename_queue.qsize(), len(filenames)),
              end='\r')
        time.sleep(1)

    for process in ftp_processes:
        process.join()


def main(only_init=False):
    urls = ESSENTIAL_URLS
    if not only_init:
        urls.extend(EXTENDEND_URLS)

    for url in urls:
        download_unzip(url)

    if not only_init:
        # because of duplicate names we have to download this one here separately to rename it
        for url in ['http://hgdownload.cse.ucsc.edu/goldenPath/hg38/phastCons100way/hg38.100way.phastCons/{}.phastCons100way.wigFix.gz'.format(c) for c in ALL_HUMAN_CHROMOSOMES]:
            download_unzip(url, '.hg38')

    download_sifts()


if __name__ == "__main__":
    main()
