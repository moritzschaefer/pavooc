from unittest import mock
from nose.tools import eq_

import pandas as pd


from pavooc.config import PROTEIN_ID_MAPPING_FILE
from pavooc import data

from test.helpers import mock_read_gtf_as_dataframe

# mock chromosomes
data.CHROMOSOMES = ['chrA']


def mock_read_protein_id_mapping_csv(filename, *args, **kwargs):
    assert filename == PROTEIN_ID_MAPPING_FILE, \
        'this mock only fits for {}'.format(PROTEIN_ID_MAPPING_FILE)

    return pd.DataFrame({
        'swissprot_id': ['SP1', 'SP2', 'SOMETHINGELSE'],
        'ID_NAME': ['Ensembl_PRO', 'Ensembl_PRO', 'otherid'],
        'protein_id': ['PA', 'PB', 'ABC']})



@mock.patch('pandas.read_csv',
            side_effect=mock_read_protein_id_mapping_csv)
@mock.patch('gtfparse.read_gtf_as_dataframe',
            side_effect=mock_read_gtf_as_dataframe)
def test_read_gencode(mocked_gtf, mocked_csv):
    '''only
    Mocking read_gtf_as_dataframe to return a simplified dataframe,
    read_gencode should return only one copy of gene2
    '''

    df = data.read_gencode()

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

    # TODO test that non protein_coding gene_types are ignored


@mock.patch('pandas.read_csv',
            side_effect=mock_read_protein_id_mapping_csv)
@mock.patch('pavooc.data.read_gtf_as_dataframe',
            side_effect=mock_read_gtf_as_dataframe)
def test_gencode_exons(mocked_gtf, mocked_csv):
    df = data.gencode_exons()
    eq_(set(df.index), {'EA1', 'EA2', 'EB1'})
    eq_(df.index.name, 'exon_id')
    print(df)
    eq_(len(df), 4)  # EA1 does exist twice

# TODO test domain_interval_trees
