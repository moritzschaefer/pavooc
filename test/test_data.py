from unittest import mock
from nose.tools import eq_

import pandas as pd


from pavooc.config import PROTEIN_ID_MAPPING_FILE
from pavooc.data import read_gencode


def mock_read_protein_id_mapping_csv(filename, *args, **kwargs):
    assert filename == PROTEIN_ID_MAPPING_FILE, \
        'this mock only fits for {}'.format(PROTEIN_ID_MAPPING_FILE)

    return pd.DataFrame({
        'swissprot_id': ['SP1', 'SP2', 'SOMETHINGELSE'],
        'ID_NAME': ['Ensembl_PRO', 'Ensembl_PRO', 'otherid'],
        'protein_id': ['PA', 'PB', 'ABC']})


def mock_read_gtf_as_dataframe(filename):
    # 'start' AND 'end' are included and are 1-indexed. to transform to proper
    # indexing, just do start-=1 and leave end as is.
    # in our case here, all exons are in-frame (dividable by 3)

    # gene 1 is a valid reverse strand gene with two transcripts
    # all these entries don't vary too much actually.. TODO merge them together
    gene1 = {
        'feature': 'gene', 'gene_id': 'GA', 'transcript_id': 'GA',
        'start': 10, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }

    gene1_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 10, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 25, 'end': 30, 'exon_id': 'EA1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript1_exon2 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 10, 'end': 18, 'exon_id': 'EA2', 'exon_number': '2',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript2 = {
        'feature': 'transcript', 'gene_id': 'GA', 'transcript_id': 'TA2',
        'start': 25, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA2',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript2_exon1 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA2',
        'start': 25, 'end': 30, 'exon_id': 'EA1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA2',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }

    # gene 2 is valid forward strand gene with one transcript which exists on
    # ENSEMBL AND HAVANA with minor difference in its single exon
    gene2 = {
        'feature': 'gene', 'gene_id': 'GB', 'transcript_id': 'GB',
        'start': 5, 'end': 10, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GB', 'transcript_id': 'TB1',
        'start': 5, 'end': 10, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': 'basic', 'protein_id': 'PB',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GB', 'transcript_id': 'TB1',
        'start': 5, 'end': 10, 'exon_id': 'EB1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': 'basic', 'protein_id': 'PB',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2E = {**gene2}
    gene2E['source'] = 'ENSEMBL'
    gene2_transcript1E = {**gene2_transcript1}
    gene2_transcript1E['source'] = 'ENSEMBL'
    gene2_transcript1_exon1E = {**gene2_transcript1_exon1}
    gene2_transcript1_exon1E['source'] = 'ENSEMBL'

    # gene 3 has only transcripts/exons which are not basic
    gene3 = {
        'feature': 'gene', 'gene_id': 'GC', 'transcript_id': 'GC',
        'start': 50, 'end': 70, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene3_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GC', 'transcript_id': 'TC1',
        'start': 50, 'end': 70, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene3_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GB', 'transcript_id': 'TC1',
        'start': 50, 'end': 70, 'exon_id': 'EC1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    df = pd.DataFrame([
        gene1,
        gene1_transcript1, gene1_transcript1_exon1, gene1_transcript1_exon2,
        gene1_transcript2, gene1_transcript2_exon1,
        gene2, gene2_transcript1, gene2_transcript1_exon1,
        gene2E, gene2_transcript1E, gene2_transcript1_exon1E,
        gene3, gene3_transcript1, gene3_transcript1_exon1
    ])

    # add unused keys
    for key in [
            'ccdsid', 'frame', 'gene_status', 'havana_gene',
            'havana_transcript', 'level', 'ont', 'transcript_name',
            'transcript_status']:
        df[key] = ''
    return df


@mock.patch('pandas.read_csv',
            side_effect=mock_read_protein_id_mapping_csv)
@mock.patch('gtfparse.read_gtf_as_dataframe',
            side_effect=mock_read_gtf_as_dataframe)
def test_read_gencode(mocked_gtf, mocked_csv):
    '''only
    Mocking read_gtf_as_dataframe to return a simplified dataframe,
    read_gencode should return only one copy of gene2
    '''

    df = read_gencode()

    # check that the correct columns are returned
    eq_(set(df.columns), {
        'feature', 'gene_id', 'transcript_id',
        'start', 'end', 'exon_id', 'exon_number',
        'gene_name', 'transcript_type', 'strand',
        'gene_type', 'tag', 'protein_id', 'swissprot_id',
        'score', 'seqname', 'source'})

    # gene 'GB' should have  zero entires for ENSEMBL
    # but 3 (gene, transcript, exon) for HAVANA
    eq_(len(df[(df.gene_id == 'GB') & (df.source == 'ENSEMBL')]), 0)
    eq_(len(df[(df.gene_id == 'GB') & (df.source == 'HAVANA')]), 3)

    # gene 'GC' should not be existent because it has no basic transcripts
    eq_(len(df[df.gene_id == 'GC']), 0)

    # start should be subtracted (just testing for one exon for simplicity)
    eq_(df[df.exon_id == 'EB1'].iloc[0].start, 4)
    # end should remain the same
    eq_(df[df.exon_id == 'EB1'].iloc[0].end, 10)

    # swissprot should be merged
    eq_(list(df[(df.protein_id == 'PA')].swissprot_id.drop_duplicates()),
        ['SP1'])
    eq_(list(df[(df.protein_id == 'PB')].swissprot_id.drop_duplicates()),
        ['SP2'])

    # no swissprot_id for a protein_id shouldn't delete that row
    assert (df.protein_id == 'PA2').any()
