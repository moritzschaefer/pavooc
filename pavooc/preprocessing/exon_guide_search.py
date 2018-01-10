import subprocess
import logging
import os
import pickle
import re
from tqdm import tqdm
from multiprocessing import Pool

import pandas as pd
import numpy as np

from pavooc.config import JAVA_RAM, FLASHFRY_DB_FILE, EXON_DIR, \
    GUIDES_FILE, SCORES_FILE, COMPUTATION_CORES
from pavooc.data import read_gencode, exon_interval_trees
from pavooc.scoring import flashfry

logging.basicConfig(level=logging.WARN,
                    format='%(levelname)s %(asctime)s %(message)s')

PATTERN = re.compile(
    r'(?P<protospacer>\w{23})_(?P<occurences>\d+)_(?P<mismatch_count>\d+)'
    r'<(?P<off_loci>.*)>'
    # r'<(chr[\d\w]{1,2}):(\d+)\\\^(.)(\\\|(chr[\d\w]{1,2}):(\d+)\\\^(.))*>'
)


def off_targets_relevant(off_targets, gene_id, mismatches):
    '''
    :off_targets: string containing all off targets to check for relevance
    :gene_id: The gene_id of the on-target
    :mismatches: dictionary to keep statistics of mismatches
    :returns: boolean wether off_targets are relevant or not
    '''
    in_exons_summary = False
    result = PATTERN.match(off_targets)
    assert bool(result), off_targets  # check that pattern is valid
    for off_locus in result.group('off_loci').split('\\|'):
        # in flashfry, the position is always the left-handside
        # (in forward strand direction)
        try:
            chromosome, rest = off_locus.split(':')
            position, strand = rest.split('\\^')
        except:
            import ipdb
            ipdb.set_trace()
        if strand == 'F':
            position = int(position) + 17
        elif strand == 'R':
            position = int(position) + 6
        else:
            raise ValueError('strand must be either R or F but is {}'
                             .format(strand))
        in_exons = exon_interval_trees()[chromosome][position]

        try:
            mismatches[(
                bool(in_exons),
                int(result.group('mismatch_count'))
            )] += int(result.group('occurences'))
        except KeyError:
            mismatches[(
                bool(in_exons),
                int(result.group('mismatch_count'))
            )] = int(result.group('occurences'))
        # either, we sort out guides, that cut the same gene while
        # cutting another gene which might sort out many good guides
        # (depends on the design of FF). Right now:
        # Disallow guides only if that off_target is away from the gene
        # That is the correct solution!
        if bool(in_exons) and \
                np.all([exon[0] != gene_id for exon in in_exons]):
            in_exons_summary = True

    # if there is an exact in-extron match which is not in this gene
    return result.group('mismatch_count') == 0 and in_exons_summary


def flashfry_guides(gene_id):
    '''
    Generates the flashfry guides with off-targets for a gene
    :returns: The filename of the files with the generated guides
    '''
    gene_file = os.path.join(EXON_DIR, gene_id)

    target_file = GUIDES_FILE.format(gene_id)
    result = subprocess.run([
        'java',
        '-Xmx{}M'.format(int((1024 * float(JAVA_RAM)) //
                             int(COMPUTATION_CORES))),
        '-jar', 'FlashFry-assembly-1.7.jar',
        '--analysis', 'discover',
        '--fasta', gene_file,
        '--output', target_file,
        '--maxMismatch', '5',
        '--maximumOffTargets', '1500',
        '--positionOutput=true',
        '--database', FLASHFRY_DB_FILE
    ], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        raise RuntimeError(result)
    return target_file


def generate_exon_guides(gene_id):
    '''
    :gene_id:
    :returns: tuple (overflow count, mismatches)
    '''

    logging.info('Generate guides for {}.'.format(gene_id))
    mismatches = {}
    overflow_count = 0

    target_file = flashfry_guides(gene_id)

    # now read the file, analyze and delete unnecessary guides
    data = pd.read_csv(
        target_file,
        index_col=False,
        sep='\t',
        dtype={
            'contig': str,
            'start': int,
            'stop': int,
            'target': str,
            'context': str,
            'overflow': str,
            'orientation': str,
            'otCount': int, 'offTargets': str
        }
    )

    delete_indices = set()

    for index, row in data.iterrows():
        if row['overflow'] == 'OVERFLOW':
            overflow_count += 1
            delete_indices.add(index)

        if row['otCount'] == 0:
            continue

        # check if the DSB is really inside the exon
        # (we padded the exons by 16bps on both sides)
        # row.start is in padded coordinates
        exon_data = row['contig'].split(';')
        exon_length = int(exon_data[3]) - int(exon_data[2])

        if (row['orientation'] == 'FWD' and
                row['start'] + 16 > exon_length + 16) or \
            (row['orientation'] == 'RVS' and
                row['start'] < 10):
            delete_indices.add(index)
            continue

        # check for off_target duplicates inside the exome
        for off_targets in row['offTargets'].split(','):
            if off_targets_relevant(off_targets, gene_id, mismatches):
                delete_indices.add(index)

    data.drop(delete_indices, inplace=True)
    data.reset_index(inplace=True, drop=True)

    # delete position_markers (they are incompatible with the scoring)
    data['offTargets'] = data['offTargets'].map(
        lambda ot: re.sub('<.*?>', '', ot))
    data.to_csv(target_file, sep='\t', index=False)

    return overflow_count, mismatches


def main():
    mismatches = {}
    overflow_count = 0
    gene_ids = read_gencode().gene_id.drop_duplicates()
    if COMPUTATION_CORES > 1:
        with Pool(COMPUTATION_CORES) as pool:
            for partial_overflow_count, partial_mismatches in tqdm(
                    pool.imap_unordered(
                        generate_exon_guides,
                        gene_ids),
                    total=len(gene_ids)):
                overflow_count += partial_overflow_count
                for key in partial_mismatches:
                    try:
                        mismatches[key] += partial_mismatches[key]
                    except KeyError:
                        mismatches[key] = partial_mismatches[key]
    else:
        # debuggable
        for gene_id in tqdm(gene_ids, total=len(gene_ids)):
            partial_overflow_count, partial_mismatches = \
                generate_exon_guides(gene_id)
            overflow_count += partial_overflow_count
            for key in partial_mismatches:
                try:
                    mismatches[key] += partial_mismatches[key]
                except KeyError:
                    mismatches[key] = partial_mismatches[key]

    # save anaysis data
    print('Overflow count: {}'.format(overflow_count))
    print(mismatches)


if __name__ == "__main__":
    main()
