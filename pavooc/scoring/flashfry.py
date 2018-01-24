import subprocess

import pandas as pd

from pavooc.config import GUIDES_FILE, SCORES_FILE, JAVA_RAM, \
        COMPUTATION_CORES, FLASHFRY_DB_FILE


def score(gene_id):
    '''
    Generates the scores implemented by flashfry
    :returns: a dataframe with the scores
    '''

    guides_file = GUIDES_FILE.format(gene_id)
    scores_file = SCORES_FILE.format(gene_id)
    result = subprocess.run([
        'java',
        '-Xmx{}M'.format(int((1024 * float(JAVA_RAM)) //
                             int(COMPUTATION_CORES))),
        '-jar', 'FlashFry-assembly-1.7.jar',
        '--analysis', 'score',
        '--input', guides_file,
        '--output', scores_file,
        '--scoringMetrics',
        'doench2014ontarget,doench2016cfd,dangerous,hsu2013',
        '--database', FLASHFRY_DB_FILE
    ], stdout=subprocess.DEVNULL)

    if result.returncode != 0:
        raise RuntimeError(result)

    return pd.read_csv(scores_file, sep='\t', index_col=False)
