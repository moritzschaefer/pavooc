from unittest.mock import patch
from nose.tools import eq_
import pandas as pd
from pavooc.scoring.azimuth import _context_guide


# mock gencode_exons to speed up test
@patch('pavooc.scoring.azimuth.gencode_exons')
def test__context_guide(gencode_exons_mock):
    exon_id = 'ENSE00000657802'
    start_in_exon = -10
    gencode_exons_mock.return_value = pd.DataFrame(
            {
                'seqname': ['chr22'],
                'start': [51043990],
            },
            index=[exon_id])
    guide = _context_guide(exon_id, start_in_exon, 'FWD')
    eq_(guide, 'CTCCCCCAACGGCAGGTTCATCCCGCGGCA')
