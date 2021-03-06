#!/usr/bin/env python

import ftplib
import gzip
import logging
import os
import re
import subprocess
import tarfile
import time
from multiprocessing.dummy import Process, Queue
from urllib.error import HTTPError
from urllib.request import urlretrieve

from pavooc.config import (BASEDIR, CHROMOSOMES, DATADIR, GENOME,
                           HUMAN_CHROMOSOMES, MOUSE_CHROMOSOMES, S3_BUCKET_URL,
                           SIFTS_FILE, SIFTS_TARBALL, TRAIN_MODEL)

ESSENTIAL_URLS = [
    f'http://hgdownload.soe.ucsc.edu/goldenPath/{GENOME}/chromosomes/{c}.fa.gz'
    for c in (HUMAN_CHROMOSOMES if 'hg' in GENOME else MOUSE_CHROMOSOMES)
] + [  # noqa
    S3_BUCKET_URL.format('cnn38.torch'),
    S3_BUCKET_URL.format('scaler.pkl'),
    'ftp://ftp.ebi.ac.uk/pub/databases/msd/sifts/flatfiles/csv/pdb_chain_uniprot.csv.gz',  # noqa
    f'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/{"HUMAN_9606" if "hg" in GENOME else "MOUSE_10090"}_idmapping.dat.gz',  # noqa
    'ftp://ftp.ebi.ac.uk/pub/databases/Pfam/mappings/pdb_pfam_mapping.txt',
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz',  # noqa
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz',  # noqa
    f'ftp://hgdownload.cse.ucsc.edu/goldenPath/{GENOME}/database/ucscGenePfam.txt.gz',  # noqa
    'http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed',
    f'http://hgdownload.cse.ucsc.edu/goldenPath/{GENOME}/bigZips/{GENOME}.chrom.sizes',
    'http://portals.broadinstitute.org/achilles/datasets/19/download/guide_activity_scores.tsv',  # noqa
    'http://portals.broadinstitute.org/achilles/datasets/19/download/sgRNA_mapping.tsv',  # noqa
    'https://s3-eu-west-1.amazonaws.com/pstorage-npg-968563215/7195484/13059_2016_1012_MOESM14_ESM.tsv',
    'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz',  # noqa # NOTE that this is based on GRCh38!!
    # for conservation scores:
    'https://s3.eu-central-1.amazonaws.com/pavoocdata/mongodump.tar.gz',
    'https://s3.eu-central-1.amazonaws.com/pavoocdata/conservations_features.csv'
]  # noqa <- this is the same file as being computed in the pipeline

if GENOME == 'hg19':
    ESSENTIAL_URLS.append('ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz')
elif GENOME == 'hg38':
    ESSENTIAL_URLS.append('ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_30/gencode.v30.annotation.gtf.gz')
elif GENOME == 'mm10':
    ESSENTIAL_URLS.extend(['ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M21/gencode.vM21.annotation.gtf.gz',
                           'http://hgdownload.cse.ucsc.edu/goldenPath/mm10/bigZips/mm10.2bit'
    ])

if GENOME == 'hg19':
    ESSENTIAL_URLS.extend([
        'https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_2013-12-03.seg.txt',  # noqa
        'https://data.broadinstitute.org/ccle/ccle2maf_081117.txt',
    ])

EXTENDEND_URLS = [
    'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/phastCons100way/hg19.100way.phastCons/{}.phastCons100way.wigFix.gz'
    .format(c) for c in HUMAN_CHROMOSOMES
] + [
    'http://hgdownload.cse.ucsc.edu/goldenPath/mm10/phastCons60way/mm10.60way.phastCons/{}.phastCons60way.wigFix.gz'
    .format(c) for c in MOUSE_CHROMOSOMES
]

logging.basicConfig(level=logging.INFO)


def file_download(url, target):
    '''
    Download a file with either urlretrieve or with curl

    '''

    try:
        urlretrieve(url, target)
    except HTTPError:
        result = subprocess.run(['curl', '-f', '-o', target, url])
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
        # os.remove(os.path.join(DATADIR, download_filename))
        logging.warn('{} xists, delete \
                to force download'.format(download_filename))
        return
    logging.info('downloading {}'.format(url))

    # check if file exists on our S3 bucket first, then download from source
    # try:
    #     file_download(S3_BUCKET_URL.format(download_filename), download_target)
    # except RuntimeError as e:
    #     print('S3 download failed with error {}'.format(e))
    file_download(url, download_target)

    logging.info('unpacking {}'.format(download_filename))
    if download_filename[-3:] == '.gz':
        with gzip.open(os.path.join(DATADIR, download_filename),
                       'rb') as gz_file:
            file_content = gz_file.read()
        with open(os.path.join(DATADIR, download_filename[:-3]),
                  'wb') as datafile:
            datafile.write(file_content)
        download_filename = download_filename[:-3]

    if download_filename[-4:] == '.tar':
        tarfile.TarFile(download_target).extractall(path=DATADIR)
        os.remove(download_filename)


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
        try:
            with open(target_filename, 'wb') as f:
                ftp.retrbinary('RETR ' + filename, f.write)
        except:
            queue.put(filename)
            os.remove(target_filename)
    ftp.quit()


def download_sifts():
    # download all sift files

    # first try to download a tarball containing all the sift xmls

    if not os.path.exists(SIFTS_TARBALL):
        try:
            urlretrieve(S3_BUCKET_URL.format('sifts.tar'), SIFTS_TARBALL)
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

    ftp_processes = [
        Process(target=download_ftp, args=(filename_queue, ))
        for _ in range(10)
    ]
    for process in ftp_processes:
        process.start()

    try:
        while not filename_queue.empty():
            print('{}/{} sifts downloaded'.format(
                len(filenames) - filename_queue.qsize(), len(filenames)),
                end='\r')
            time.sleep(1)

        for process in ftp_processes:
            process.join()
    except KeyboardInterrupt:
        # TODO kill not supported by multiprocessing.dummy..
        for process in ftp_processes:
            process.kill()


def main(only_init=False):
    urls = ESSENTIAL_URLS
    if not only_init and TRAIN_MODEL:
        urls.extend(EXTENDEND_URLS)
        # because of duplicate names we have to download this one here separately to rename it
        for url in [
                'http://hgdownload.cse.ucsc.edu/goldenPath/hg38/phastCons100way/hg38.100way.phastCons/{}.phastCons100way.wigFix.gz'
                .format(c) for c in HUMAN_CHROMOSOMES
        ]:
            download_unzip(url, '.hg38')

    for url in urls:
        download_unzip(url)

    download_sifts()


if __name__ == "__main__":
    main()
