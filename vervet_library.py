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

    return domain_bonus + early_exon_bonus + FACTOR_ONTARGET * guide['scores']['azimuth'] + FACTOR_OFFTARGET * (1-guide['scores']['Doench2016CFDScore']), domain_name

def pick_gene_guides(gene):
    guide_scores = [(guide, *rate_guide(guide, gene['domains'], gene['exons'])) for guide in gene['guides']]
    guide_scores.sort(key=operator.itemgetter(1), reverse=True)

    return guide_scores[:NUM_GUIDES]

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
    pd.concat(dfs).reset_index(drop=True).to_csv('vervet_library.csv')


if __name__ == '__main__':
    main()

