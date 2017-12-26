import pandas as pd
from sklearn.preprocessing import StandardScaler
from azimuth.features.featurization import featurize_data
from azimuth.util import concatenate_feature_sets

from pavooc.config import CONSERVATION_FEATURES_FILE

# TODO refactor!


def extract_features(Xdf, Y, gene_position, order=2):
    learn_options = {
        'nuc_features': True,
        'num_proc': 1,
        'order': order,
        'gc_features': True,
        'include_pi_nuc_feat': True,
        "include_gene_position": True,
        "include_NGGX_interaction": True,
        "include_Tm": True,
        'include_known_pairs': False,
        'include_microhomology': False,
        'ignore_gene_level_for_inner_loop': True,  # <- what?
        "include_strand": False,
        "include_gene_feature": False,
        "include_gene_guide_feature": 0,
        "include_gene_effect": False,
        "include_drug": False,
        "include_sgRNAscore": False,
        "normalize_features": False
    }

    features = featurize_data(
        Xdf, learn_options, Y, gene_position,
        pam_audit=True, length_audit=True)

    conservation_scores = pd.read_csv(CONSERVATION_FEATURES_FILE, index_col=0)
    conservation_scores.index = features['_nuc_pd_Order1'].index
    features['conservation_scores'] = conservation_scores
    y = Y['score_drug_gene_rank'].astype('float32').as_matrix()


    # we need the genes associated to the features to do cv data selection
    genes = features['conservation_scores'].index.get_level_values(
        1).to_series().reset_index(drop=True)

    return features, y, genes


def combine_and_normalize_features(features, select_features=None, normalize_features=True):
    '''
    Generate one normalized np matrix out of the dictionary of feature matrices
    :features: dict of <featurename: matrix> pairs
    :select_features: <list>Only select a subset of features
    :returns: a matrix with all features and an array for the row names
    '''
    if select_features:
        selected_features = dict((k, features[k]) for k in select_features)
    else:
        selected_features = features

    combined_features, dim, dimsum, feature_names = concatenate_feature_sets(
        selected_features)
    combined_features = combined_features.astype('float32')
    if normalize_features:
        scaler = StandardScaler()
        combined_features = scaler.fit_transform(combined_features)

    return combined_features, feature_names
