'''
Here I generate a CRISPRa sgRNA library for the Vervet monkey
'''
import numpy as np
import pandas as pd
import operator
from pavooc.db import guide_collection
from pavooc.data import gencode_cds_exons, read_gencode
from tqdm import tqdm


NUM_GUIDES = 4
FACTOR_ONTARGET = 0.8
FACTOR_OFFTARGET = 0.2


def rate_guide(guide, gene_id):
    position_bonus = 0
    guide_pos = guide['start']

    df = read_gencode()
    gene = df.loc[(df.gene_id == gene_id) & (df['feature'] == 'gene')].iloc[0]

    if guide['orientation'] == 'RVS':
        guide_pos += 23

    if gene['strand'] == '+':
        tss_distance = gene['start'] - guide_pos
    elif gene['strand'] == '-':
        tss_distance = guide_pos - gene['end']
    else:
        raise ValueError(f'strand cannot be {gene["strand"]}')

    assert tss_distance <= 260, f"tss_distance too large: {tss_distance}, {gene['gene_id']}, {guide['start']}"
    assert tss_distance >= 60, f"tss_distance too small: {tss_distance}, {gene['gene_id']}, {guide['start']}"

    # everything between 115 and 185 is top scoring
    distance_from_optimal = max(0, abs(150 - tss_distance) - 35)

    penalty = distance_from_optimal / 40.0

    if int(guide.get('contain_polyn', '0')) != 0:
        penalty += 1
    if int(guide.get('noffscore', '0')) != 0:
        penalty += 2
        assert 'Doench2016CFDScore' not in guide['scores'], "off-target score found in guide but shouldnt be"
        guide['scores']['Doench2016CFDScore'] = 1
        assert int(guide['proper_filter']) == 0, "proper_filter does not find noffscore"
    else:
        assert int(guide['proper_filter']) == 1, "proper_filter does not fit noffscore(1)"


    return FACTOR_ONTARGET * guide['scores']['azimuth'] + FACTOR_OFFTARGET * (1-guide['scores']['Doench2016CFDScore']) - penalty, tss_distance


def pick_gene_guides(gene):
    guide_scores = [(guide, *rate_guide(guide, gene['gene_id'])) for guide in gene['guides']]
    guide_scores.sort(key=operator.itemgetter(1), reverse=True)

    return guide_scores[:NUM_GUIDES*2]


def main():
    dfs = []
    for gene in tqdm(guide_collection.find(no_cursor_timeout=True)):
        guides = pick_gene_guides(gene)
        dfs.append(pd.DataFrame({
            'gene_symbol': gene['gene_symbol'],
            'guide_sequence': [g[0]['target'] for g in guides],
            'guide_score': [g[1] for g in guides],
            'guide_orientation': [g[0]['orientation'] for g in guides],
            'guide_tss_distance': [g[2] for g in guides],
            'guide_start_pos': [g[0]['start'] for g in guides],
            'gene_id': gene['gene_id'],
            'chromosome': gene['chromosome'],
            'gene_strand': gene['strand'],
        }))
    df = pd.concat(dfs).reset_index(drop=True)

    protospacer = df['guide_sequence'].apply(lambda s: s[:-3])

    duplicated = protospacer.duplicated(keep=False)

    print(f'{duplicated.sum()} / {len(duplicated)} are duplicated and are deleted')
    df = df.loc[~duplicated]

    # select the first 4 guides. As rows are sorted by key, head gives the 4 highest  # TODO double check by looking at the first 10 genes
    df = df.groupby('gene_id').head(NUM_GUIDES).reset_index(drop=True)

    # count how many have a value smaller than 0.
    print(f'{(df.guide_score < 0).sum()} / {len(df)} guides have a score <0')

    df.to_csv('vervet_library_activation.csv')


if __name__ == '__main__':
    main()
