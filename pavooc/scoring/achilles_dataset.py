import pandas as pd
from skbio.sequence import DNA
from gtfparse import read_gtf_as_dataframe

from pavooc.config import ACHILLES_GUIDE_ACTIVITY_SCORES_FILE, \
    ACHILLES_GUIDE_MAPPING, CHROMOSOME_RAW_FILE, GENCODE_HG38_FILE
from pavooc.scoring.missing_gene_id_mappings import GENE_ID_MAPPING


def _first_or_none(x):
    try:
        return x.iloc[0]
    except IndexError:
        return None


def _find_context(guide, chromosome, position):
    '''
    :returns: the 30mer context, 'sense' or 'antisense', percent peptide and
    amino acid cut position
    '''
    OFFSET = 50
    if isinstance(position, str):
        position = int(position)
    with open(CHROMOSOME_RAW_FILE.format(chromosome)) as f:
        f.seek(position - OFFSET)
        seq = f.read(2 * OFFSET + 20).upper()
        index = seq.find(guide)
        if index == -1:
            rev_seq = str(DNA(seq).reverse_complement())
            rev_index = rev_seq.find(guide)
            assert rev_index >= 0, f'guide not found.. {chromosome} {position}'
            ret = rev_seq[rev_index - 4:rev_index + 23 + 3]
        else:
            ret = seq[index - 4:index + 23 + 3]
        if ret[25:27] != 'GG':
            print(
                f'gg required... {chromosome} {position} {guide}. Dropping :/')
            return None, None
        return ret, 'sense' if index == -1 else 'antisense'


def load_dataset(drop_locus=True):
    '''
    Load and prepare the achilles dataset to be processed be azimuth feature
    extraction
    :returns: Xdf, Y, gene_position, target_genes as in azimuth.load_dataset
    '''
    activity_scores = pd.read_csv(
        ACHILLES_GUIDE_ACTIVITY_SCORES_FILE, sep='\t')
    guide_map = pd.read_csv(ACHILLES_GUIDE_MAPPING, sep='\t')
    guide_map.dropna(inplace=True)
    guide_map.rename(index=str, columns={'Gene': 'Target'}, inplace=True)
    guide_map = guide_map.groupby('Guide').first()
    activity_scores.dropna(inplace=True)
    activity_scores.set_index('Guide', inplace=True)
    df = guide_map.join(activity_scores)

    # TODO why hg38 and not 37
    hg38 = read_gtf_as_dataframe(GENCODE_HG38_FILE)
    hg38 = hg38.loc[(hg38.feature == 'gene')]
    # remove duplicate gene names (chrX, chrY) by using first one
    # this might be inaccurate but shouldn't have a big impact.
    # It affects around 60 datapoints only (out of 70000)
    hg38 = hg38.groupby('gene_name').first().reset_index()

    # fix wrong gene names
    hg38['gene_id'] = hg38['gene_id'].apply(lambda v: v[:15])
    merged_mapping = GENE_ID_MAPPING.merge(
        hg38[['gene_id', 'gene_name']], how='inner', on='gene_id')
    df.Target = df.Target.apply(
            lambda gene: gene if (gene == hg38.gene_name).any()
            else _first_or_none(
                merged_mapping.loc[merged_mapping.symbol == gene].gene_name))
    df.dropna(inplace=True)
    #

    contexts = df.apply(lambda row: _find_context(
        row.name, *row.Locus.split('_')[:2]), axis=1)

    df['30mer'] = [c[0] for c in contexts]
    df['Strand'] = [c[1] for c in contexts]
    df.dropna(inplace=True)
    Y = pd.DataFrame({'score_drug_gene_rank': df['Activity']}, index=df.index)

    # calculate percent peptide and 'Amino Acid Cut position'
    df_positions = df.merge(
        hg38[['gene_name', 'start', 'end']],
        left_on='Target', right_on='gene_name')
    nt_cut_position = df_positions.Locus.map(lambda v: int(v.split('_')[1]))
    pp = (100.0 * (nt_cut_position - df_positions.start) /
          (df_positions.end - df_positions.start))
    # 'Amino Acid Cut position' is just a very stupid heuristic because I am
    # too lazy to calculate the real value
    aacp = (pp / 100.0) * ((df_positions.end - df_positions.start) / 100)

    df.drop(['Activity'], axis=1, inplace=True)
    if drop_locus:
        df.drop(['Locus'], axis=1, inplace=True)
    gene_position = pd.DataFrame(
        {'Percent Peptide': pp, 'Amino Acid Cut position': aacp})
    gene_position.set_index(df.index, inplace=True)
    df.index.name = 'Sequence'
    df['drug'] = 'nodrug'
    target_genes = df['Target'].drop_duplicates()
    df.reset_index(inplace=True)
    df.set_index(['Sequence', 'Target', 'drug'], inplace=True)

    return df, Y, gene_position, target_genes
