from unittest import mock
from nose.tools import eq_
import pandas as pd

from pavooc.preprocessing import preprocessing


preprocessing.chromosomes = lambda: {
        'chrA': 'AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTTUUVVXXYYZZ'}


def test_exon_to_fasta():
    exon_id = 'E1'
    # data is not 100% real (second transcript is wrong)
    exon_data = pd.DataFrame({
        'start': [20, 20],
        'end': [29, 29],
        'seqname': ['chrA', 'chrA'],
        'strand': ['+', '+'],
        'transcript_id': ['T1', 'T2'],
        'exon_number': [1, 1]
    })

    result = preprocessing.exon_to_fasta(exon_id, exon_data)
    required = '''>E1;+;20;29;T1:1,T2:1
CCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTTUUVVX
'''

    eq_(result.split('\n')[0], required.split('\n')[0])
    eq_(result.split('\n')[1], required.split('\n')[1])

    eq_(result, required)

    # TODO test reverse as well.
