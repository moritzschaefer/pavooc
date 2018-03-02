'''
Issue: We only have hg38 conservations so we have to search the guide in the
corresponding gene and from there extract the conservation scores
In other words:
Problem: Ich weiß nicht an welcher Stelle die sgRNA ist!

Lösung:
- use only http://www.gencodegenes.org/releases/current.html
- Cut out the chromosomes semi-manually. Delete newlines etc.
- for each sgRNA, pick the right chromosome, search for the 30mer context
     - if antisense, reverse_complement the context
- make sure it found only one location
- make sure the location is in the range of the targeted gene
- if antisense, add 4
- if sense, add 16
- assert the pam position == GG or CC (in case of antisense)
- once we have the cut position, we can search the phyloP or phast for conservation scores.
- suggestion: use several features: 3bp-conservations to the left, 3bp-conservations to the right, median conservation, median, max, min of these
-
'''
import os
import re

from skbio.sequence import DNA
from gtfparse import read_gtf_as_dataframe
from intervaltree import IntervalTree
import numpy as np
import pandas as pd

from pavooc.config import DATADIR, CONSERVATION_FEATURES_FILE, \
        GENCODE_HG38_FILE, GENCODE_MM10_FILE, MOUSE_CHROMOSOMES
from pavooc.util import buffer_return_value
from pavooc.scoring.azimuth_dataset import load_dataset as azimuth_dataset
# from pavooc.scoring.achilles_dataset import load_dataset as achilles_dataset

HUMAN_CHROMOSOMES = ['chr{}'.format(v)
                     for v in range(1, 23)] + ['chrX', 'chrY']
# MOUSE_GENES = ('CD5', 'CD28', 'H2-K', 'CD45', 'THY1', 'CD43')
MOUSE_GENES = ('Cd5', 'Cd28', 'H2-K1', 'Ptprc', 'Thy1', 'Spn')


def cut_chromosomes(species='hg38'):
    chromosome_file = None
    try:
        os.makedirs(os.path.join(DATADIR, species))
    except FileExistsError:
        pass

    if species == 'hg38':
        filename = 'GRCh38.p10.genome.fa'
    else:
        filename = 'GRCm38.p5.genome.fa'

    with open(os.path.join(DATADIR, filename)) as f:
        line_iter = iter(f)
        try:
            while True:
                line = next(line_iter)
                if line[1:4] == 'chr':
                    if chromosome_file:
                        chromosome_file.close()
                    chromosome_file = open(
                        os.path.join(
                            DATADIR,
                            species,
                            line[1:line.find(' ')]),
                        'w')
                else:
                    chromosome_file.write(line.upper().strip())
        except StopIteration:
            pass
        chromosome_file.close()


@buffer_return_value
def read_mm10():
    print('read gencode')
    df = read_gtf_as_dataframe(GENCODE_MM10_FILE)

    return df


@buffer_return_value
def read_hg38():
    print('read gencode')
    df = read_gtf_as_dataframe(GENCODE_HG38_FILE)

    return df


@buffer_return_value
def human_chromosomes():
    print('Loading human chromosomes')
    species = 'hg38'
    return {
        c: open(os.path.join(DATADIR, species, c)).read()
        for c in HUMAN_CHROMOSOMES}


@buffer_return_value
def mouse_chromosomes():
    print('Loading mouse chromosomes')
    species = 'mm10'
    return {
        c: open(os.path.join(DATADIR, species, c)).read()
        for c in MOUSE_CHROMOSOMES}


def chromosomes(species='hg38'):
    '''
    Return dictionary with loaded chromosome data
    '''
    try:
        if species == 'hg38':
            return human_chromosomes()
        else:
            return mouse_chromosomes()
    except FileNotFoundError:
        print('need to create chromosome files first')
        cut_chromosomes(species)
        if species == 'hg38':
            return human_chromosomes()
        else:
            return mouse_chromosomes()


def cut_position_from_index(index, sense, chr_seq):
    if sense:
        # 4 padding before protospacer, then 16 protospacer bases
        cut_position = index + 4 + 16
        assert chr_seq[index + 4 + 21:index +
                       4 + 23] == 'GG', 'PAM sequence not found'
    else:
        cut_position = index + 3 + 3 + 4  # 3 padding, 3 PAM, 4 protospacer bs
        assert chr_seq[index + 3:index +
                       5] == 'CC', 'PAM sequence not found'
    return cut_position


def find_guide_context(gene, context, sense):
    '''
    :gene: symbol of the gene
    :context: 30mer
    :sense: boolean wether in sense or antisense
    :returns: (species, chromosome, cut_position) where cut_position is 0-base-index
    '''

    if gene in MOUSE_GENES:
        species = 'mm10'
        df = read_mm10()
    else:
        species = 'hg38'
        df = read_hg38()

    try:
        gene_data = df[((df.gene_name == gene) | (df.gene_id.map(lambda g: g[:15]) == gene[:15])) & (
            df.feature == 'gene')].iloc[0].copy()
    except IndexError:
        print(f'didnot find context {context} in gene {gene}. Sense: {sense}')
        return species, 'chrNaN', -1
    gene_data.start -= 1
    absolute_sense = (sense == (gene_data.strand == '+'))
    chromosome = gene_data.seqname
    # only if guide and gene strand are not the same
    if not absolute_sense:
        context = str(DNA(context).reverse_complement())
    chr_seq = chromosomes(species)[chromosome]

    index = chr_seq.find(context)
    while index != -1:
        cut_position = cut_position_from_index(index, absolute_sense, chr_seq)
        if cut_position >= gene_data.start and cut_position < gene_data.end:
            # it's inside the gene. go on
            break
        else:
            index = chr_seq.find(context, index + len(context))

    if index == -1:
        print(f'didnot find context {context} in gene {gene}. Sense: {sense}')
        return species, chromosome, -1

    return species, chromosome, cut_position


def pickle_return_value(func):
    import pickle

    def wrapper(*args, **kwargs):
        filename = os.path.join(DATADIR, f'buffered_{func.__name__}.pickle')
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            ret = func(*args, **kwargs)
            with open(filename, 'wb') as f:
                pickle.dump(ret, f)
            return ret

    return wrapper


@buffer_return_value
@pickle_return_value  # delete me later?
def index_phast_mm10():
    return _index_phast(MOUSE_CHROMOSOMES, '.phastCons60way.wigFix')


@buffer_return_value
@pickle_return_value  # delete me later?
def index_phast_hg38():
    return _index_phast(HUMAN_CHROMOSOMES, '.phastCons100way.wigFix')


def _index_phast(chromosome_names, filename_suffix):
    '''Find all headers and insert them into intervaltrees

    each line has 6 characters. example:
    0.123\n

    '''

    print('indexing phast headers')
    trees = {}
    base_count = 0
    start_file_pos = None
    for chromosome in chromosome_names:
        file_pos = 0
        with open(os.path.join(DATADIR, chromosome + filename_suffix)) as f:
            for line in f:
                file_pos += len(line)
                if line[:5] == 'fixed':
                    if start_file_pos:  # the first header is not an interval
                        try:
                            trees[chromosome]
                        except KeyError:
                            trees[chromosome] = IntervalTree()
                        trees[chromosome][start - 1:start -
                                          1 + base_count] = start_file_pos

                    start = int(re.search('start=(\d+)', line).groups()[0])
                    start_file_pos = file_pos
                    base_count = 0
                else:
                    base_count += 1
            trees[chromosome][start - 1:start -
                              1 + base_count] = start_file_pos
            base_count = 0
            start_file_pos = None
    return trees


def get_conservation_score_features(species, chromosome, position):
    '''
    The lookup seems a bit complicated. This comes from the fact, that the
    phast data comes in a somewhat difficult format..

    :trees: the interval trees of the conservation score intervals
    :species: mm10 or hg38
    :chromosome: The chromosome
    :position: The bp corrdinate position of interest in the chromosome
    '''
    features = []
    if position == -1:
        return None

    filename = f'{chromosome}.phastCons{"100way" if species=="hg38" else "60way"}.wigFix'

    with open(os.path.join(DATADIR, filename)) as f:
        for offset in range(-3, 4, 1):
            tree = index_phast_hg38() if species == 'hg38' else index_phast_mm10()
            lookup = tree[chromosome][position + offset]
            if len(lookup) != 1:
                print(f'found {len(tree[chromosome][position+offset])} positions for offset {chromosome}_{position}_{offset}')
                return None
            start, end, start_file_pos = lookup.pop()

            # multiply offset by 6 because every line has 6 characters (0.123\n)
            file_position = start_file_pos + ((position + offset - start) * 6)

            f.seek(file_position)
            features.append(float(f.read(5)))
    # now calculate median, max, min features
    return features + [np.median(features[1:-1]), np.min(features[1:-1]), np.max(features[1:-1])]


def process_dataframe(cut_positions):
    '''
    Calculate conservation scores for a given dataset
    '''

    scores = cut_positions.apply(lambda chromosome_cut_position:
                                 get_conservation_score_features(
                                     *chromosome_cut_position)
                                 )
    scores_df = pd.DataFrame.from_items(zip(scores.index, scores.values)).T
    scores_df.fillna(0.5, inplace=True)
    scores_df.columns = ['conservation1',
                         'conservation2',
                         'conservation3',
                         'conservation4',
                         'conservation5',
                         'conservation6',
                         'conservation7',
                         'conservationmedian',
                         'conservationmin',
                         'conservationmax'
                         ]
    return scores_df


def azimuth_scores():
    # first azimuth data
    Xdf, Y, gene_position, target_genes = azimuth_dataset()

    del Y, gene_position, target_genes  # don't use them without manipulation
    Xdf = Xdf.reset_index()
    # Xdf.drop(Xdf.index[
    #     Xdf.Target.isin(('CD5', 'CD28', 'H2-K', 'CD45', 'THY1', 'CD43'))],
    #          inplace=True)

    # human
    Xdf.loc[Xdf.Target == 'CD13', 'Target'] = 'ANPEP'
    Xdf.loc[Xdf.Target == 'CD15', 'Target'] = 'FUT4'
    Xdf.loc[Xdf.Target == 'CCDC101', 'Target'] = 'SGF29'
    # mouse
    Xdf.loc[Xdf.Target == 'CD45', 'Target'] = 'Ptprc'
    Xdf.loc[Xdf.Target == 'CD5', 'Target'] = 'Cd5'
    Xdf.loc[Xdf.Target == 'CD28', 'Target'] = 'Cd28'
    Xdf.loc[Xdf.Target == 'THY1', 'Target'] = 'Thy1'
    Xdf.loc[Xdf.Target == 'CD43', 'Target'] = 'Spn'
    Xdf.loc[Xdf.Target == 'H2-K', 'Target'] = 'H2-K1'

    cut_positions = Xdf.apply(lambda row: find_guide_context(
        row['Target'], row['30mer'], row['Strand'] == 'sense'), axis=1)

    scores_df = process_dataframe(cut_positions)
    scores_df.to_csv(CONSERVATION_FEATURES_FILE)


# def achilles_scores():
#     # now achilles dataset
#     Xdf, Y, gene_position, target_genes = achilles_dataset(drop_locus=False)
#
#     del Y, gene_position, target_genes  # don't use them without manipulation
#     Xdf = Xdf.reset_index()
#
#     cut_positions = Xdf.apply(lambda row: (
#         'hg38',
#         row['Locus'].split('_')[0],
#         int(row['Locus'].split('_')[1])), axis=1)
#
#     scores_df = process_dataframe(Xdf, cut_positions)
#     scores_df.to_csv(ACHILLES_CONSERVATION_FEATURES_FILE)


def main():
    azimuth_scores()


if __name__ == "__main__":
    main()
