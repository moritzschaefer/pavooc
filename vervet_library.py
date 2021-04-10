'''
Here I generate a sgRNA library for the Vervet monkey
'''
import numpy as np
import pandas as pd
import operator
from pavooc.db import guide_collection
from tqdm import tqdm

NUM_GUIDES = 4
DOMAIN_BONUS = 0.14
EARLY_EXON_BONUS = 0.08 # bonus if in the first helf of the exons
FACTOR_ONTARGET = 0.7
FACTOR_OFFTARGET = 0.3


def rate_guide(guide, domains, exons):
    domain_bonus = 0
    domain_name = ''
    for domain in domains:
        if guide['cut_position'] >= domain['start'] and guide['cut_position'] < domain['end']:
            domain_bonus = DOMAIN_BONUS
            domain_name = domain['name']

    early_exon_bonus = 0
    for i, exon in enumerate(exons):  # exons are sorted by exon_number
        if guide['cut_position'] >= exon['start'] and guide['cut_position'] <= exon['end']:
            if i <= len(exons) // 2:
                early_exon_bonus = EARLY_EXON_BONUS
            break

    # if 'contain_polyn' in guide['scores']:
    #     print(guide['scores']['contain_polyn'])
    # if 'noffscore' in guide['scores']:
    #     print(guide['scores']['noffscore'])

    penalty = 0
    if int(guide['scores'].get('contain_polyn', '0')) != 0:
        penalty -= 1
    if int(guide['scores'].get('noffscore', '0')) != 0:
        penalty -= 1

    return penalty + domain_bonus + early_exon_bonus + FACTOR_ONTARGET * guide['scores']['azimuth'] + FACTOR_OFFTARGET * (1-guide['scores']['Doench2016CFDScore']), domain_name

def pick_gene_guides(gene):
    guide_scores = [(guide, *rate_guide(guide, gene['domains'], gene['exons'])) for guide in gene['guides']]
    guide_scores.sort(key=operator.itemgetter(1), reverse=True)

    return guide_scores[:NUM_GUIDES * 2]

def main():
    dfs = []
    for gene in tqdm(guide_collection.find()):
        guides = pick_gene_guides(gene)
        dfs.append(pd.DataFrame({
            'gene_symbol': gene['gene_symbol'],
            'guide_sequence': [g[0]['target'] for g in guides],
            'guide_score': [g[1] for g in guides],
            'guide_domain_target': [g[2] for g in guides],
            'guide_cut_position': np.array([g[0]['cut_position'] for g in guides]).astype(int),
            'guide_orientation': [g[0]['orientation'] for g in guides],
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

    df.to_csv('vervet_library.csv')
    print(df.gene_id.value_counts().value_counts())
if __name__ == '__main__':
    main()

