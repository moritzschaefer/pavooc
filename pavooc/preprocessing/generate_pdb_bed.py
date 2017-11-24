'''
Create a bed file for the exome
'''
import logging
import pandas as pd
from pavooc.config import PDB_BED_FILE
from pavooc.util import normalize_pid
from pavooc.data import gencode_exons, read_appris, pdb_list
from pavooc.pdb import pdb_mappings


def pdb_coordinates(pdb, pdb_exons):
    '''
    Generate the genome coordinates mapping for the given pdb
    :pdb: pdb data
    :returns: A tuple with all necessary data for a bed file
    '''
    try:
        strand = pdb_exons.strand.iloc[0]
    except IndexError:
        raise ValueError('No exons provided for pdb {}'.format(pdb.PDB))

    index = 0
    pdb_ranges = []

    # First normalize the exon coordinates of the given gene: First exon
    # should start with index 0
    if strand == '-':
        zero = pdb_exons.iloc[0].end
        assert zero == max(pdb_exons.end), ''
        pdb_exons.end, pdb_exons.start = zero - pdb_exons.start, \
            zero - pdb_exons.end
    else:
        zero = pdb_exons.iloc[0].start
        assert zero == min(pdb_exons.start)
        pdb_exons.start -= zero
        pdb_exons.end -= zero

    mappings = pdb_mappings(pdb.PDB, pdb.CHAIN, pdb.SP_PRIMARY)
    sp_start = min(mappings.keys())
    sp_end = max(mappings.keys())

    # Iterate over each exon (in order) and check in which interval the
    # Protein lies
    for _, exon in pdb_exons.iterrows():
        exon_length = (exon.end - exon.start)
        pdb_end = None
        if sp_start * 3 >= index:
            if sp_start * 3 < index + exon_length:  # first exon
                in_exon_start = sp_start * 3 - index
                pdb_start = exon.start + in_exon_start
            else:  # not in pdb-exons yet, go ahead
                index += exon_length
                continue
        else:
            in_exon_start = 0

        # Inside PDB exons, find end and add to array
        if sp_end * 3 <= index + exon_length:
            in_exon_end = (sp_end * 3) - index
            pdb_end = exon.start + in_exon_end
        else:
            in_exon_end = exon_length
        if strand == '+':
            pdb_ranges.append(
                (exon.start + in_exon_start - pdb_start,
                    exon.start + in_exon_end - pdb_start))
        else:
            pdb_ranges.insert(0,
                              (zero - (exon.start + in_exon_end),
                               zero - (exon.start + in_exon_start)))

        index += exon_length
        if pdb_end:
            break

    # TODO. this should NOT happen!!
    if not pdb_end:
        raise ValueError('transcript too small for PDB {}'.format(pdb.PDB))

    if strand == '-':
        pdb_start, pdb_end = zero - pdb_end, zero - pdb_start
        # inner bed coordinates should be relative to the pdb-start-coordinate
        pdb_ranges = [[r[0] - pdb_ranges[0][0], r[1] - pdb_ranges[0][0]]
                      for r in pdb_ranges]
    else:
        pdb_start += zero
        pdb_end += zero

    return [[pdb_exons.iloc[0]['seqname']][0],
            pdb_start,
            pdb_end,
            pdb.PDB,
            0,
            strand,
            pdb_start,
            pdb_end,
            ','.join([str(v) for v in [0, 255, 0]]),
            len(pdb_ranges),
            ','.join([str(r[1] - r[0]) for r in pdb_ranges]),
            ','.join([str(r[0]) for r in pdb_ranges])]


def main():
    with open(PDB_BED_FILE, 'w') as f:
        appris = read_appris()
        exons = gencode_exons()

        # filter out exons which dont belong to swissprot-transcripts
        # (makes dataprocessing easier)
        # TODO exons doesn't provide swissprot_id any more FIXME
        exons = exons.loc[exons.swissprot_id.map(
            lambda spid: type(spid) == str)].copy()
        exons.swissprot_id = exons.swissprot_id.map(normalize_pid)

        for _, pdb in pdb_list().iterrows():
            # find the transcript, that corresponds to the pdb
            gene_id = exons.loc[exons.swissprot_id
                                == pdb.SP_PRIMARY].gene_id.drop_duplicates()
            if len(gene_id) == 0:
                continue
            assert len(
                gene_id) == 1, 'PDB should correspond to one gene_id only'
            gene_id = gene_id.iloc[0]

            # TODO might be wrong in some circumstances TOIMPROVE
            # right now we take the longest transcript anyways
            # transcript_id = appris.loc[gene_id[:15]].transcript_id
            # if isinstance(transcript_id, pd.Series):
            #     logging.warning('Found {} canonical transcripts for {}. '
            #                     'Choosing first one'.format(
            #                         len(transcript_id), gene_id))
            #     transcript_id = transcript_id.iloc[0]

            # filter the exons for the corresponding transcript
            # TODO in  gencode_exons we could just not use the longest
            # transcript but one from appris...
            transcript_id = exons.transcript_id.drop_duplicates().iloc[0][:15]
            appris_ids = appris.loc[gene_id[:15]].transcript_id
            if isinstance(appris_ids, pd.Series):
                if (appris_ids != transcript_id).all():
                    print('transcript_id is not the primary one!')
                    print(appris_ids, transcript_id)
            else:
                if appris_ids != transcript_id:
                    print('transcript_id is not the primary one!')
                    print(appris_ids, transcript_id)

            pdb_exons = exons.loc[
                exons.gene_id == gene_id].copy().sort_values('exon_number')

            try:
                data = pdb_coordinates(pdb, pdb_exons)
            except ValueError as e:
                logging.warning(gene_id)
                logging.warning(e)
                continue
            else:
                f.write('\t'.join([str(v) for v in data]))
                f.write('\n')


if __name__ == "__main__":
    main()
