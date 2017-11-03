'''
Create a bed file for the exome
'''
import logging
import pandas as pd
from pavooc.config import PDB_BED_FILE
from pavooc.data import gencode_exons, read_appris, pdb_data


def pdb_coordinates(pdb, pdb_exons):
    '''
    Generate the genomes coordinates for the given pdb
    :pdb: pdb data
    :returns: A tuple with all necessary data for a bed file
    '''
    strand = pdb_exons.strand.iloc[0]

    index = 0
    pdb_ranges = []

    # map the AA sequence to the bp-sequence in the exons
    if strand == '-':
        zero = pdb_exons.iloc[0].end
        assert zero == max(pdb_exons.end), ''
        pdb_exons.end, pdb_exons.start = zero - pdb_exons.start, zero - pdb_exons.end
    else:
        zero = pdb_exons.iloc[0].start
        assert zero == min(pdb_exons.start)
        pdb_exons.start -= zero
        pdb_exons.end -= zero

    for _, exon in pdb_exons.iterrows():
        exon_length = (exon.end - exon.start)
        pdb_end = None
        if pdb.SP_BEG * 3 >= index:
            if pdb.SP_BEG * 3 < index + exon_length:  # first exon
                in_exon_start = pdb.SP_BEG * 3 - index
                pdb_start = exon.start + in_exon_start
            else:  # not in pdb-exons yet
                index += exon_length
                continue
        else:
            in_exon_start = 0

        if pdb.SP_END * 3 <= index + exon_length:
            in_exon_end = (pdb.SP_END * 3) - index
            pdb_end = exon.start + in_exon_end
        else:
            in_exon_end = exon_length
        if strand == '+':
            pdb_ranges.append(
                (exon.start + in_exon_start + zero,
                    exon.start + in_exon_end + zero))
        else:
            pdb_ranges.insert(0,
                              (zero - (exon.start + in_exon_end),
                               zero - (exon.start + in_exon_start)))
            print(pdb_ranges[0])

        index += exon_length
        if pdb_end:
            break
    if strand == '-':
        pdb_start, pdb_end = zero - pdb_end, zero - pdb_start
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
        import ipdb
        ipdb.set_trace()
        appris = read_appris()
        exons = gencode_exons()
        for _, pdb in pdb_data().iterrows():
            gene_id = exons.loc[exons.swissprot_id ==
                                pdb.SP_PRIMARY].gene_id.drop_duplicates()
            if len(gene_id) == 0:
                continue

            assert len(gene_id) == 1, \
                'PDB should correspond to one gene_id only'

            transcript_id = appris.loc[gene_id[0][:15]].transcript_id
            if isinstance(transcript_id, pd.Series):
                logging.warning('Found {} canonical transcripts for {}. '
                                'Choosing first one'.format(
                                    len(transcript_id), gene_id[0]))
                transcript_id = transcript_id.iloc[0]

            pdb_exons = exons.loc[exons.transcript_id.map(lambda v: v[:15]) ==
                                  transcript_id].copy().sort_values('exon_number')

            data = pdb_coordinates(pdb, pdb_exons)

            f.write('\t'.join([str(v) for v in data]))
            f.write('\n')


if __name__ == "__main__":
    main()
