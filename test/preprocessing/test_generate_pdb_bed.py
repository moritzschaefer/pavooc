from nose.tools import eq_
import pandas as pd

from pavooc.preprocessing.generate_pdb_bed import pdb_coordinates


def test_pdb_coordinates_forward_strand():
    # SP_BEG is corrected already. In file SP_BEG would be 6
    pdb = pd.Series({'SP_BEG': 5, 'SP_END': 34, 'PDB': 'ABC'})
    pdb_exons = pd.DataFrame({
        'start': [100, 130, 170, 500, 700],
        'end': [110, 150, 200, 600, 900],
        'strand': ['+'] * 5,
        'seqname': ['chrZ'] * 5
    })

    result = pdb_coordinates(pdb, pdb_exons)

    template = [
        'chrZ',
        135,
        542,
        'ABC',
        0,
        '+',
        135,
        542,
        ','.join([str(v) for v in [0, 255, 0]]),
        3,
        ','.join([str(v) for v in [15, 30, 42]]),
        ','.join([str(v) for v in [0, 35, 365]])
    ]
    for a, b in zip(result, template):
        eq_(a, b)


def test_pdb_coordinates_reverse_strand():
    # SP_BEG is corrected already. In file SP_BEG would be 6
    pdb = pd.Series({'SP_BEG': 5, 'SP_END': 16, 'PDB': 'ABC'})
    pdb_exons = pd.DataFrame({
        'start': [1000, 700, 300, 100],
        'end': [1010, 710, 350, 110],
        'strand': ['-'] * 4,
        'seqname': ['chrZ'] * 4
    })

    result = pdb_coordinates(pdb, pdb_exons)

    template = [
        'chrZ',
        322,
        705,
        'ABC',
        0,
        '-',
        322,
        705,
        ','.join([str(v) for v in [0, 255, 0]]),
        2,
        ','.join([str(v) for v in [28, 5]]),
        ','.join([str(v) for v in [0, 378]])
    ]
    for a, b in zip(result, template):
        eq_(a, b)
