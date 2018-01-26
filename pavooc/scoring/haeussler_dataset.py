'''
This is a combined dataset from Haeussler et al.
In this dataset 'Target' is the dataset, not the gene!
'''

import pandas as pd
from gtfparse import read_gtf_as_dataframe
import io
from intervaltree import IntervalTree
from itertools import product
import logging

from pavooc.data import exon_interval_trees, read_gencode
from pavooc.util import buffer_return_value
from pavooc.config import HAEUSSLER_SCORES_FILE, \
    CHROMOSOME_RAW_FILE, GENCODE_MM10_FILE


MOUSE_CHROMOSOMES = ['chr{}'.format(v)
                     for v in range(1, 20)] + ['chrX', 'chrY']
@buffer_return_value
def mouse_gene_intervals():
    df = read_gtf_as_dataframe(GENCODE_MM10_FILE)
    df = df[df.feature == 'gene' & df.feature_type == 'protein_coding']
    print(len(df))
    trees = {chromosome_strand: IntervalTree() for chromosome_strand in product(MOUSE_CHROMOSOMES, ['+', '-'])}
    for _, row in df.iterrows():
        if row['end'] > row['start']:
            # end is included, start count at 0 instead of 1
            trees[row['seqname'] + row['strand']][row['start'] - 1:row['end']
                                  ] = (row['gene_id'])

    logging.info('Built mouse exon tree with {} nodes'
                 .format(sum([len(tree) for tree in trees.values()])))

    return trees


def _calculate_gene_start_end(df):
    df['start'] = 0
    df['end'] = 0
    for index, row in df.iterrows():
        if row.db == 'hg19':
            exons = exon_interval_trees()[row.chromosome][row.cut_position]
            for exon in exons:
                if (exon.strand == '+') == (row.Strand == 'sense'):
                    gene = read_gencode()[
                            (read_gencode().gene_id == exon.gene_id) &
                            (read_gencode().feature == 'gene')]
                    if len(gene) != 1:
                        print('found more than one gene for ID: {}'.format(
                            gene))
                    gene = gene.iloc[0]

                    df[index].start = gene.start
                    df[index].end = gene.end
                    break
            else:
                print('no gene found for row {}'.format(row))
        if row.db == 'mm9':
            strand = '+' if row.Strand == 'sense' else '-'
            start, end, gene_ids = mouse_gene_intervals()[row.chromosome + strand][row]
            if len(gene_ids) != 1:
                print('error: found more than one gene: {}, row: {}'.format(gene, row))
            df[index].start = start
            df[index].end = end



def load_dataset():
    '''
    Load and prepare the haeussler dataset (combination of "all" other datasets)

    :returns: Xdf, Y, gene_position, target_genes as in azimuth.load_dataset
    '''
    processed = io.StringIO()
    with open(HAEUSSLER_SCORES_FILE) as f:
        for line in f:
            values = line.split('\t')
            processed.write('\t'.join(values[:7]))
            processed.write('\n')

    df = pd.read_csv(
        processed, sep='\t')

    # filter zebrafish and all that stuff
    df[df.db.isin(['hg19', 'mm9'])]

    df.rename(index=str, columns={'dataset': 'Target gene', 'seq': 'Sequence'},
              inplace=True)
    df.Sequence = df.Sequence.map(lambda v: v[:20])

    df['30mer'] = df['longSeq100Bp'].map(lambda v: v[26:26 + 30])
    df['100mer'] = df['longSeq100Bp']
    df['Strand'] = df.position.map(
        lambda v: 'sense' if v[-1] == '+' else 'antisense')
    df['chromosome'] = df.position.map(lambda v: v.split(':')[0])
    df['cut_position'] = df.position.map(lambda v: int(re.search('.*:(\d+)-', v).groups()[0])+30+16)
    df['drug'] = 'nodrug'
    target_genes = df['Target'].drop_duplicates()
    df.set_index(['Sequence', 'Target gene', 'drug'], inplace=True)

    Y = pd.DataFrame({'score_drug_gene_rank': df['modFreq']}, index=df.index)

    # calculate percent peptide and 'amino acid cut position'

    _calculate_gene_start_end(df)
    pp = (100.0 * (df.cut_position - df.start) /
          (df.end - df.start))
    # TODO!!!!
    # 'Amino Acid Cut position' is just a very stupid heuristic because I am
    # too lazy to calculate the real value
    aacp = (pp / 100.0) * ((df.end - df.start) / 100)

    gene_position = pd.DataFrame({'Percent Peptide': pp, 'Amino Acid Cut position': aacp}, index=df.index)
    df.index.rename(['Sequence', 'Target', 'drug'], inplace=True)

    return df, Y, gene_position, target_genes
