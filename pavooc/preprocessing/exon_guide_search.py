import subprocess
import logging
import os
import re
from tqdm import tqdm
from multiprocessing import Pool
import tempfile

import pandas as pd
import numpy as np

from azimuth.model_comparison import predict as azimuth_predict
from pavooc.config import JAVA_RAM, FLASHFRY_DB_FILE, EXON_DIR, \
    GUIDES_FILE, COMPUTATION_CORES, FLASHFRY_EXE, CRISPR_MODE
from pavooc.data import read_gencode, exon_interval_trees, chromosomes, \
    azimuth_model, gencode_exons
from pavooc.preprocessing.guides_to_db import guide_mutations
from pavooc.scoring import flashfry
from pavooc.util import aa_cut_position, percent_peptide

logging.basicConfig(level=logging.WARN,
                    format='%(levelname)s %(asctime)s %(message)s')

PATTERN = re.compile(
    r'(?P<protospacer>\w{23})_(?P<occurences>\d+)_(?P<mismatch_count>\d+)'
    r'<(?P<off_loci>.*)>'
    # r'<(chr[\d\w]{1,2}):(\d+)\\\^(.)(\\\|(chr[\d\w]{1,2}):(\d+)\\\^(.))*>'
)


def gene_names_similar(gene_a, gene_b):
    gc = read_gencode()
    name_a = gc[gc.gene_id == gene_a].iloc[0].gene_name
    name_b = gc[gc.gene_id == gene_b].iloc[0].gene_name
    if name_a[:-1] in name_b or name_b[:-1] in name_a:
        return True
    else:
        return False


# TODO maybe improve this heuristic
def off_targets_relevant(off_targets, gene_id, mismatches):
    '''
    ATM just check whether there is a zero mismatch OT in another gene

    :off_targets: string containing all off targets to check for relevance
    :gene_id: The gene_id of the on-target
    :mismatches: dictionary to keep statistics of mismatches
    :returns: boolean wether off_targets are relevant or not
    '''
    result = PATTERN.match(off_targets)
    assert bool(result), off_targets  # check that pattern is valid
    if int(result.group('mismatch_count')) > 0:
        return False

    for off_locus in result.group('off_loci').split('|'):
        # in flashfry, the position is always the left-handside
        # (in forward strand direction)
        try:
            chromosome, rest = off_locus.split(':')
            position, strand = rest.split('^')
        except:
            from IPython.core.debugger import set_trace
            set_trace()
        if strand == 'F':
            position = int(position) + 17
        elif strand == 'R':
            position = int(position) + 6
        else:
            raise ValueError('strand must be either R or F but is {}'
                             .format(strand))
        if CRISPR_MODE == 'knockout':
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
            # (either, we sort out guides, that cut the same gene while
            # cutting another gene which might sort out many good guides)
            # (depends on the design of FF). Right now:
            # Disallow guides only if that off_target is away from the gene
            # np.all, because np.any would make this relevant if it was on the
            # same gene, when there is another exon on the reverse strand
            # furthermore check if this is in an isozyme
            if bool(in_exons) and \
                    np.all([not gene_names_similar(exon[2][0], gene_id)
                            for exon in in_exons]):
                return True

    return False


def flashfry_guides(seq_file, target_file):
    '''
    Generates the flashfry guides with off-targets for a gene
    :returns: The filename of the files with the generated guides
    '''

    result = subprocess.run([
        'java',
        '-Xmx{}M'.format(int((1024 * float(JAVA_RAM)) //
                             int(COMPUTATION_CORES))),
        '-jar', FLASHFRY_EXE,
        '--analysis', 'discover',
        '--fasta', seq_file,
        '--output', target_file,
        '--maxMismatch', '5',
        '--maximumOffTargets', '1500',
        '--positionOutput=true',
        '--database', FLASHFRY_DB_FILE
    ], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        raise RuntimeError(result)
    return target_file


def generate_edit_guides(gene_id, chromosome, edit_position, offset=200):
    '''
    I hope they all have the same index..
    :chromosome: e.g. 'chr12'
    :edit_position: edit_position in chromosome
    :offset: number of nucleotides before and after the edit_position to look for guides
    :returns: A tuple (sequence, before_guides, after_guides) with all scored guides before and after the edit_position
    '''
    seq_file = tempfile.NamedTemporaryFile(delete=False)
    target_file = tempfile.NamedTemporaryFile(delete=False)
    target_file.close()
    seq_file.write(
        bytes(f'>{chromosome}:{gene_id}:{edit_position-offset}-{edit_position+offset}\n', 'ascii'))
    seq_start = edit_position - offset
    seq = chromosomes()[chromosome][seq_start:edit_position + offset]
    seq_file.write(bytes(seq, 'ascii'))
    seq_file.close()

    exons = gencode_exons()[gencode_exons().gene_id == gene_id]

    generate_guides(gene_id, seq_file.name,
                    target_file.name, check_in_exon=False)
    os.remove(seq_file.name)

    # TODO from here on DRY with guides_to_db:build_gene_document

    try:
        guides = pd.read_csv(target_file.name, sep='\t', index_col=False)
    except Exception as e:
        logging.fatal('Couldn\'t load guides file for {}'
                      .format(target_file.name))
        raise

    flashfry_scores = flashfry.score(target_file.name)
    flashfry_scores.fillna(0, inplace=True)

    # delete all guides with incomplete context (at the border of the sequence)
    guides = guides[guides.context.apply(len) == 35]
    guides['start'] += seq_start

    gene_start = exons['start'].min()
    gene_end = exons['end'].max()
    strand = exons.strand.iloc[0]

    try:
        guides['cut_position'] = guides.apply(
            lambda row: row['start'] +
            (7 if row['orientation'] == 'RVS' else 16), axis=1)
        guides['aa_cut_position'] = guides.apply(
            lambda row: aa_cut_position(row, exons), axis=1)
        guides['percent_peptide'] = guides.apply(
            lambda row: percent_peptide(row, gene_start, gene_end, strand),
            axis=1)
    except ValueError as e:  # guides is empty and apply returned a DataFrame
        logging.warn('no guides: {}'.format(e))
        guides['cut_position'] = []
        guides['aa_cut_position'] = []
        guides['percent_peptide'] = []

    logging.info('calculating azimuth score for {}'.format(gene_id))
    try:
        guides.context = guides.context.apply(lambda c: c[2:32])
        azimuth_score = pd.Series(
            azimuth_predict(guides['context'].values, model=azimuth_model()),
            index=guides.index)
    except ValueError as e:
        guides.to_csv(f'{gene_id}.csv')
        logging.error(
            f'Gene {gene_id} had problems. saved {gene_id}.csv. Error: {e}')
        azimuth_score = pd.Series(0, index=guides.index)

    # delete all guides with scores below 0.57
    # TODO use something more sophisticated
    guides.drop(guides.index[azimuth_score < 0.45], inplace=True)

    before_guides = []
    after_guides = []

    # TODO does the index really match????
    for index, guide in guides.iterrows():
        converted = {**guide,
                     'mutations': guide_mutations(chromosome, guide['start']),
                     'scores': {
                         'azimuth': azimuth_score.loc[index],
                         **flashfry_scores.loc[index][[
                             'Doench2016CFDScore', 'Hsu2013']].to_dict()}}
        if guide.cut_position < edit_position:
            before_guides.append(converted)
        else:
            after_guides.append(converted)

    os.remove(target_file.name)
    # TODO convert to dataframes?
    return seq, before_guides, after_guides


def generate_exon_guides(gene_id):
    seq_file = os.path.join(EXON_DIR, gene_id)
    target_file = GUIDES_FILE.format(gene_id)
    return generate_guides(gene_id, seq_file, target_file, check_in_exon=True)


def generate_guides(gene_id, seq_file, target_file, check_in_exon):
    '''
    Find and prepare guides for a given region
    :gene_id: Needed to check for off targets. Off targets in the same gene
    dont matter
    :seq_file: the provided sequence region as FASTA file
    :target_file: the prepared guides
    :returns: tuple (overflow count, mismatches)
    '''

    logging.info('Generate guides for {}.'.format(gene_id))
    mismatches = {}
    overflow_count = 0

    flashfry_guides(seq_file, target_file)

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

        if check_in_exon:
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
            partial_overflow_count, partial_mismatches = generate_exon_guides(
                gene_id)
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
