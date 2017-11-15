from nose.tools import eq_
import pandas as pd

from pavooc.preprocessing.generate_guide_bed import guide_to_bed


# TODO verify this guide
def test_guide_to_bed():
    gene = {'exons': [{'start': 99, 'exon_id': 'exonid1'}, {
        'start': 4, 'exon_id': 'exonid2'}],
        'chromosome': 'chrA'}
    guide = pd.Series({'start': 5, 'target': 'ABC', 'exon_id': 'exonid1',
                       'orientation': 'FWD', 'score': 0.55})

    result = guide_to_bed(gene, guide)
    eq_(result,
        '\t'.join([
            'chrA', str(99 + 5), str(99 + 5 + 23),
            'ABC', '55', '+', str(99 + 5), str(99 + 23 + 5 ),
            '0,255,0', '1', '23', '0']))
