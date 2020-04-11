'''
Load azimuth over a python2 interpreter (it's python 2 :/)
'''

import pandas as pd
import logging

from pavooc.data import azimuth_model

from azimuth.model_comparison import predict as azimuth_predict




def score(guides, chromosome):
    '''
    Call the azimuth module model
    :guides: A dataframe with all relevant information for the guides
    TODO add amino acid cut position and percent peptides
    :returns: a list of scores
    '''
    if len(guides) == 0:
        return []

    # workaround error for 'N' nucleotides
    errors = guides.context.apply(lambda c: 'N' in c)
    contexts = guides.context.apply(lambda c: c.replace('N', 'A'))

    try:
        results = azimuth_predict(
                contexts.values,
                aa_cut=guides.aa_cut_position.values,
                percent_peptide=guides.percent_peptide.values,
                model=azimuth_model())
        results[errors] = 0
        return results
    except AssertionError as e:
        import ipdb
        ipdb.set_trace()
