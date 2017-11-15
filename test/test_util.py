# from unittest import mock
# from test.helpers import mock_read_gtf_as_dataframe
from nose.tools import raises, eq_
from pavooc.util import int_to_kmer, kmer_to_int, normalize_pid


@raises(ValueError)
def test_dna_type_conversion_bad_parameter_length():
    kmer_to_int('ACCCT')


def test_dna_type_conversion():
    kmer = 'AACCTTGATCGTAGATCATG'
    eq_(kmer, int_to_kmer(kmer_to_int(kmer)))


def test_normalize_pid():
    eq_(normalize_pid('ABC-1'), 'ABC')
    eq_(normalize_pid('ABC-1AB'), 'ABC')
    eq_(normalize_pid('ABC'), 'ABC')
    eq_(normalize_pid('ABC-'), 'ABC')


# TODO mocking doesnt work
# @mock.patch('pavooc.data.read_gtf_as_dataframe',
#             side_effect=mock_read_gtf_as_dataframe)
# def test_guide_info(gtf_mock):
#     exon_id = 'EA1'
#     start_in_exon = 2
#     guide_info(exon_id, start_in_exon, 'FWD')
#
#     guide_info(exon_id, start_in_exon, 'RVS')
#     pass
