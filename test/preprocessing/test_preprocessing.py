from nose.tools import eq_
import pandas as pd

from pavooc.preprocessing.preprocessing import exon_to_fasta


def test_exon_to_fasta():
    exon_id = 'ENSE00000880792'
    # data is not 100% real (second transcript is wrong)
    exon_data = pd.DataFrame({
        'start': [46663861, 46663861],
        'end': [46663969, 46663969],
        'seqname': ['chr22', 'chr22'],
        'strand': ['+', '+'],
        'transcript_id': ['ENST00000381031.3', 'ENST00000445282.2'],
        'exon_number': [1, 1]
        })

    result = exon_to_fasta(exon_id, exon_data)
    required = '''>ENSE00000880792;+;46663861;46663969;ENST00000381031.3:1,ENST00000445282.2:1
CGCCCCGCCCCGCCCCTTTCCGCGACCGCCCCGCCCACTCCCAGGAAGGCCCGGGTGCCCAGAGCTCGCGGTGGACTCCGACCCGGCGCAACATGGCCGCAGCCTCGCCTCTGCGCGACTGCCAGGTACACGGAGGCTGCC
'''

    eq_(result.split('\n')[0], required.split('\n')[0])
    eq_(result.split('\n')[1], required.split('\n')[1])

    eq_(result, required)
