'''
Create one SNP bed file for each cancercellline
'''

import os
import pandas as pd
from pavooc.config import CELLLINES_PATH, CNS_BED_FILE, CNS_FILE


def _cns_bed_row(cns):
    return ['chr{}'.format(cns.Chromosome),
            cns.Start - 1,
            cns.End,
            '{:.1f}-fold-{}'.format(2 * (2 ** cns.Segment_Mean), 'amplification' if 2 * (2 ** cns.Segment_Mean) > 1 else 'depletion'),
            0,
            '+',
            cns.Start - 1,
            cns.End,
            ','.join([str(v) for v in [255, 0, 0]]),
            1,
            1 + cns.End - cns.Start,
            0]


def main():
    try:
        os.makedirs(CELLLINES_PATH)
    except FileExistsError:
        pass
    df = pd.read_csv(CNS_FILE, sep='\t')
    df.End = df.End.astype('int64')
    for cellline, cnss in df.groupby('CCLE_name'):
        bed_file = CNS_BED_FILE.format(cellline)
        with open(bed_file, 'w') as f:
            for index, cns in cnss.iterrows():
                data = _cns_bed_row(cns)
                f.write('\t'.join([str(v) for v in data]))
                f.write('\n')


if __name__ == "__main__":
    main()
