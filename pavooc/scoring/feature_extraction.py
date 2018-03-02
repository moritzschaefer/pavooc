import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from azimuth.features.featurization import featurize_data
from azimuth.util import concatenate_feature_sets

# TODO refactor!


def extract_features(Xdf, Y, gene_position, conservation_scores, order=2):
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

    conservation_scores.index = features['_nuc_pd_Order1'].index
    features['conservation_scores'] = conservation_scores
    y = Y['score_drug_gene_rank'].astype('float32').as_matrix()

    # we need the genes associated to the features to do cv data selection
    genes = features['conservation_scores'].index.get_level_values(
        1).to_series().reset_index(drop=True)

    combined_features, dim, dimsum, feature_names = concatenate_feature_sets(
        features)
    combined_features = combined_features.astype('float32')

    return combined_features, y, genes, feature_names


def normalize_features(X_train, X_test=None):
    '''
    '''
    # minmixscaler is fine, except, it only sees Gs in position 24,25
    # we need to add an artifical sequence which does not have GGs!
    # actually it doesnt matter as we transform the test set also anyways...
    scaler = MinMaxScaler()
    tmp = X_train[-2:, :120].copy()
    X_train[-2, :120] = 1.0
    X_train[-1, :120] = 0.0
    scaler.fit(X_train)
    X_train[-2:, :120] = tmp
    X_train = scaler.transform(X_train)
    # transform test based on training fit only!
    if isinstance(X_test, (np.ndarray, list)):
        X_test = scaler.transform(X_test)
        return X_train, X_test, scaler
    else:
        return X_train, scaler


def split_test_train_valid(combined_features, y, test_size=0.2, random_state=42, joint_scaling=False):
    '''
    :joint_scaling: If True, feature scaling is fitted with the complete set,
    instead of only the training set
    :returns: training and test set and validation fold of training test
    '''
    # normalize based on training set1

    # now split features in training/validation and test set
    if joint_scaling:
        copied, scaler = normalize_features(combined_features.copy())  # dont apply different scaling on X_test
    else:
        copied = combined_features
    X_train, X_test, y_train, y_test = train_test_split(
        copied, y, test_size=test_size, random_state=random_state)

    if not joint_scaling:
        X_train, X_test, scaler = normalize_features(X_train, X_test)

    # 25% of 80% are 20% of 100%
    np.random.seed(42)
    validation_indices = np.random.choice(
        X_train.shape[0], int(X_train.shape[0] * 0.25), replace=False)

    validation_fold = np.zeros(X_train.shape[0], dtype=bool)
    validation_fold[validation_indices] = True

    return X_train, X_test, y_train, y_test, validation_fold, scaler

# def combine_and_normalize_features(features, select_features=None,
#                                    normalize_features=True):
#     '''
#     Generate one normalized np matrix out of the dictionary of feature matrices
#     :features: dict of <featurename: matrix> pairs
#     :select_features: <list>Only select a subset of features
#     :returns: a matrix with all features and an array for the row names
#     '''
#     if select_features:
#         selected_features = dict((k, features[k]) for k in select_features)
#     else:
#         selected_features = features
#
#     if normalize_features:
#         scaler = StandardScaler()
#         combined_features = scaler.fit_transform(combined_features)
#
#     return combined_features, feature_names
