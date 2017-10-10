'''
_context_guide in the scoring.azimuth module extracts the (forward-sequence)
from the genome given its exon and position in the exon. This function has
important value and will eventually be extracted to util.py or so.

The test is rather complex because we have to test 4 cases (for each one of
them it is different to extract the sequence given the information):

1. ENSG00000251357.4.guides positive strand FWD (line 2), subtract the 16
and im good to go
2. ENSG00000251357.4.guides positive strand RVS (line 6), just the same as
in the first case (just reverse complement it)
3. ENSG00000268538.1.guides negative strand FWD (line 2), forward on backward
strand, is backward on forward strand (so it is opposite!).
exon['end']+16-start_in_exon. Thats your not-included last bp (because
gencode starts counting at 1). name it <end>. then get
reverse_complement[end-23:end]
4. ENSG00000268538.1.guides negative strand RVS (line 15). same as last, but
dont reverse_complement

'''
from unittest.mock import patch
from nose.tools import eq_
import pandas as pd
from pavooc.scoring.azimuth import _context_guide

exon_ids = [
        'ENSE00003649242.1',
        'ENSE00003682782.1',
        'ENSE00003192729.1',
        'ENSE00003192729.1']  # we can handle identical exon_ids
guide_directions = [
        'FWD',
        'RVS',
        'FWD',
        'RVS']
gencode_mock = pd.DataFrame(
        {
            # taken from .guides file
            'seqname': ['chr22', 'chr22', 'chr22', 'chr22'],
            'strand': ['+', '+', '-', '-'],
            'start': [24236959, 24210668, 30814212, 30814212],
            'end': [24237131, 24210828, 30814469, 30814469],
        },
        index=exon_ids)

# 16 needs to be subtracted to account for the padding added in preprocessing
start_in_exons = [3-16, 10-16, 7-16, 67-16]  # taken from .guides file
contexts = [
        'CGCGCCCTTTCCTCGCAGTACATCGCGGTG',
        'CATTGGTGAATTCCTGAATGTGCTGTGGAC',  # reverse-complemented as necessary
        'CCTTCAGATACTAAAGAGAAGATAGAGGGG',  # reverse-complemented as necessary
        'ATTGACCCAAGGTCACAGAGCCTGTAGGAG'
        ]


# mock gencode_exons to speed up test
@patch('pavooc.scoring.azimuth.gencode_exons', return_value=gencode_mock)
def test__context_guide(gencode_exons_mock):
    'return the correct guides'
    for exon_id, guide_direction, start_in_exon, context in \
            zip(exon_ids, guide_directions, start_in_exons, contexts):
        computed = _context_guide(exon_id, start_in_exon, guide_direction)
        eq_(computed, context)
