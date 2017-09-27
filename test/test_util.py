from nose.tools import raises, eq_
from pavooc.util import int_to_kmer, kmer_to_int


@raises(ValueError)
def test_dna_type_conversion_bad_parameter_length():
    kmer_to_int('ACCCT')


def test_dna_type_conversion():
    kmer = 'AACCTTGATCGTAGATCATG'
    eq_(kmer, int_to_kmer(kmer_to_int(kmer)))

