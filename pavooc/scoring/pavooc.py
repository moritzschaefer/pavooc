'''
pavooc scoring (CNN38)
'''


from skbio.sequence import DNA
import pandas as pd
import torch
from torch.autograd import Variable

from pavooc.data import read_gencode, cnn38_model, feature_scaler
from pavooc.preprocessing.extract_conservation_scores import find_guide_context, process_dataframe
from pavooc.scoring.azimuth import _context_guide
from pavooc.scoring.feature_extraction import extract_features


def score(gene_id, guides):
    '''
    Call the azimuth module model
    :guides: A dataframe with all relevant information for the guides
    TODO add amino acid cut position and percent peptides
    :returns: a list of scores
    '''
    if len(guides) == 0:
        return []

    gene = read_gencode()[read_gencode().gene_id == gene_id].iloc[0]

    contexts = guides.apply(lambda row: _context_guide(
        row['exon_id'],
        row['start'],
        row['orientation'],
        gene.seqname), axis=1)

    # TODO sense is probably relative to gene not to chromosome

    cut_positions = guides.apply(lambda row: (
        'hg19', gene.seqname, row['cut_position']), axis=1)
    conservation_scores = process_dataframe(cut_positions)

    # now build the azimuth-style feature data
    # TODO Strand might fail again..
    df = pd.DataFrame({
        'Sequence': guides.target,
        'Target': 'dummy',
        'Target gene': 'dummy',
        'score_drug_gene_rank': [0.5] * len(guides),  # no need
        'drug': 'dummy',
        '30mer': contexts,
        'Strand': ['sense' if orientation == 'FWD' else 'antisense' for orientation in guides.orientation],
        'Percent Peptide': guides.percent_peptide,
        'Amino Acid Cut position': guides.aa_cut_position
    })

    Xdf = df[['Sequence', 'Target', 'drug', '30mer', 'Strand']
             ].set_index(['Sequence', 'Target', 'drug'])
    gene_position = df[['Sequence', 'Target gene', 'drug', 'Percent Peptide',
                        'Amino Acid Cut position']].set_index(
        ['Sequence', 'Target gene', 'drug'])
    Y = df[['Sequence', 'Target gene', 'drug', 'score_drug_gene_rank']
           ].set_index(['Sequence', 'Target gene', 'drug'])
    conservation_scores.set_index(Xdf.index, inplace=True)

    combined_features, y, genes, feature_names = extract_features(
        Xdf, Y, gene_position, conservation_scores, order=1)

    transformed_features = feature_scaler().transform(combined_features)

    result = cnn38_model()(Variable(torch.from_numpy(
        transformed_features))).cpu().data.numpy()
    return result.reshape(-1)
