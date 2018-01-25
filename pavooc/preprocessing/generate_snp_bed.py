'''
Create one SNP bed file for each cancercellline
'''

import os
import pandas as pd
from pavooc.config import CELLLINES_PATH, MUTATION_BED_FILE, MUTATIONS_FILE


def _mutation_bed_row(mutation):
    return ['chr{}'.format(mutation.Chromosome),
            mutation.Start_position - 1,
            mutation.End_position,
            '{}->{}'.format(mutation.Reference_Allele,
                            mutation.Tumor_Seq_Allele1)[:25],
            0,
            mutation.Strand,
            mutation.Start_position - 1,
            mutation.End_position,
            ','.join([str(v) for v in [255, 0, 0]]),
            1,
            1 + mutation.End_position - mutation.Start_position,
            0]


def main():
    try:
        os.makedirs(CELLLINES_PATH)
    except FileExistsError:
        pass
    df = pd.read_csv(MUTATIONS_FILE, sep='\t')
    for cellline, mutations in df.groupby('Tumor_Sample_Barcode'):
        bed_file = MUTATION_BED_FILE.format(cellline)
        with open(bed_file, 'w') as f:
            for index, mutation in mutations.iterrows():
                data = _mutation_bed_row(mutation)
                f.write('\t'.join([str(v) for v in data]))
                f.write('\n')


if __name__ == "__main__":
    main()
