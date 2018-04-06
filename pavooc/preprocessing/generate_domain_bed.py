import os
import pandas as pd

from pavooc.config import DATADIR, DOMAIN_BED_FILE


def main():
    df = pd.read_csv(os.path.join(DATADIR, 'ucscGenePfam.txt'), sep='\t',
                     header=0, names=['q1', 'chr', 'start', 'end', 'name',
                                      'q2', 'strand', 'q3', 'q4', 'q5',
                                      'q6', 'lengths', 'starts'])
    df['zero'] = 0
    df['color'] = '255,0,0'
    df['block_count'] = df.starts.apply(lambda starts: starts.count(','))
    df['starts'] = df.starts.apply(lambda starts: starts.rstrip(','))
    df['lengths'] = df.lengths.apply(lambda lengths: lengths.rstrip(','))
    out = df[['chr', 'start', 'end', 'name', 'zero', 'strand', 'start',
              'end', 'color', 'block_count', 'lengths', 'starts']]
    out.to_csv(DOMAIN_BED_FILE, sep='\t', header=False, index=False)


if __name__ == "__main__":
    main()
