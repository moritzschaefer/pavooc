import subprocess
import logging
import os
import pickle
import re

import pandas as pd
import numpy as np

from pavooc.config import JAVA_RAM, FLASHFRY_DB_FILE, EXON_DIR, \
        EXON_INTERVAL_TREES_FILE, CHROMOSOMES, GUIDES_FILE
from pavooc.gencode import read_gencode

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s')

pattern = re.compile(
        r'(?P<protospacer>\w{23})_(?P<occurences>\d+)_(?P<mismatch_count>\d+)'
        r'<(?P<off_loci>.*)>'
        # r'<(chr[\d\w]{1,2}):(\d+)\\\^(.)(\\\|(chr[\d\w]{1,2}):(\d+)\\\^(.))*>'
        )

with open(EXON_INTERVAL_TREES_FILE, 'rb') as f:
    exon_interval_trees = pickle.load(f)


def generate_exon_guides(gene, mismatches):
    # TODO refactor!
    overflow_count = 0
    gene_file = os.path.join(EXON_DIR, gene)

    target_file = GUIDES_FILE.format(gene)
    subprocess.Popen([
            'java',
            '-Xmx{}g'.format(JAVA_RAM),
            '-jar', 'FlashFry-assembly-1.6.jar',
            '--analysis', 'discover',
            '--fasta', gene_file,
            '--output', target_file,
            '--maxMismatch', '5',
            '--maximumOffTargets', '1500',
            '--positionOutput=true',
            '--database', FLASHFRY_DB_FILE
            ]).wait()

    # now read the file, analyze and manipulate it
    data = pd.read_csv(
            target_file,
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

    data['delete'] = [False] * len(data)

    for index, row in data.iterrows():
        if row['overflow'] == 'OVERFLOW':
            overflow_count += 1
            data.loc[index, 'delete'] = True

        if row['otCount'] == 0:
            continue

        # check if the DSB is really inside the exon
        # (we padded the exons by 16bps on both sides)
        exon_data = row['contig'].split(';')
        padded_exon_length = int(exon_data[3]) - int(exon_data[2])
        if (row['orientation'] == 'FWD' and
                row['stop']+10 > padded_exon_length) or \
            (row['orientation'] == 'RVS' and
                row['start'] < 10):
            data.loc[index, 'delete'] = True
            continue

        # off-target statistics
        for off_targets in row['offTargets'].split(','):
            result = pattern.match(off_targets)
            assert bool(result), off_targets

            in_exons_summary = False

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
                in_exons = exon_interval_trees[chromosome][position]

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
                        np.all([exon[0] != gene for exon in in_exons]):
                    in_exons_summary = True

            # if there is an exact in-extron match which is not in this gene
            if result.group('mismatch_count') == 0 and in_exons_summary:
                data.loc[index, 'delete'] = True

    data[~data['delete']].to_csv(target_file, sep='\t')

    return overflow_count


def main():
    relevant_genes = read_gencode()[
            (read_gencode()['feature'] == 'gene') &
            (read_gencode()['gene_type'] == 'protein_coding') &
            (read_gencode()['seqname'].isin(CHROMOSOMES))
    ]
    i = 0
    mismatches = {}
    overflow_count = 0
    for _, row in relevant_genes.iterrows():
        logging.info('{}/{} Generate guides for {}.'.format(
            i,
            len(relevant_genes),
            row['gene_id'])
        )
        overflow_count += generate_exon_guides(row['gene_id'], mismatches)
        i += 1

    # save anaysis data
    print('Overflow count: {}'.format(overflow_count))
    print(mismatches)


if __name__ == "__main__":
    main()
