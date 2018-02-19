import subprocess
import tempfile
import os

import pandas as pd

from pavooc.config import GUIDES_FILE, SCORES_FILE, JAVA_RAM, \
        COMPUTATION_CORES, FLASHFRY_DB_FILE, FLASHFRY_EXE


def score(guides_file):
    '''
    Generates the scores implemented by flashfry
    :returns: a dataframe with the scores
    '''

    scores_file = tempfile.NamedTemporaryFile(delete=False)
    scores_file.close()
    result = subprocess.run([
        'java',
        '-Xmx{}M'.format(int((1024 * float(JAVA_RAM)) //
                             int(COMPUTATION_CORES))),
        '-jar', FLASHFRY_EXE,
        '--analysis', 'score',
        '--input', guides_file,
        '--output', scores_file.name,
        '--scoringMetrics',
        'doench2014ontarget,doench2016cfd,dangerous,hsu2013',
        '--database', FLASHFRY_DB_FILE
    ], stdout=subprocess.DEVNULL)

    if result.returncode != 0:
        raise RuntimeError(result)

    ret = pd.read_csv(scores_file.name, sep='\t', index_col=False)
    os.remove(scores_file.name)
    return ret

