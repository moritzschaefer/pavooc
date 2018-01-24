'''
This is the adaboost scoring from azimuth, just with train/test split instead
of CV
'''
import numpy as np
from azimuth.models.ensembles import adaboost_on_fold as azimuth_adaboost
from scipy.stats.mstats import spearmanr


def train_predict_adaboost(normalized_features, feature_selector, y, num_runs=20):
    # adaboost test
    selected_features = normalized_features[:, feature_selector]
    learn_options = {'V': 3, 'train_genes': np.array(['CD5', 'CD45', 'THY1', 'H2-K', 'CD28', 'CD43', 'CD33', 'CD13',
           'CD15', 'CCDC101', 'MED12', 'TADA2B', 'TADA1', 'HPRT1', 'CUL3',
           'NF1', 'NF2'], dtype=object), 'test_genes': np.array(['CD5', 'CD45', 'THY1', 'H2-K', 'CD28', 'CD43', 'CD33', 'CD13',
           'CD15', 'CCDC101', 'MED12', 'TADA2B', 'TADA1', 'HPRT1', 'CUL3',
           'NF1', 'NF2'], dtype=object), 'target_name': 'score_drug_gene_rank', 'testing_non_binary_target_name': 'ranks', 'include_pi_nuc_feat': True, 'gc_features': True, 'nuc_features': True, 'include_gene_position': True, 'include_NGGX_interaction': True, 'include_Tm': True, 'include_strand': False, 'include_gene_feature': False, 'include_gene_guide_feature': 0, 'extra pairs': False, 'weighted': None, 'training_metric': 'spearmanr', 'NDGC_k': 10, 'cv': 'gene', 'adaboost_loss': 'ls', 'include_gene_effect': False, 'include_drug': False, 'include_sgRNAscore': False, 'adaboost_alpha': 0.5, 'adaboost_CV': False, 'num_proc': 8, 'num_thread_per_proc': None, 'order': 2, 'normalize_features': True, 'all pairs': False, 'include_known_pairs': False, 'seed': None, 'flipV1target': False, 'num_genes_remove_train': None, 'include_microhomology': False, 'algorithm_hyperparam_search': 'grid', 'binary target name': 'score_drug_gene_threshold', 'rank-transformed target name': 'score_drug_gene_rank', 'raw target name': None, 'all_genes': np.array(['CD5', 'CD45', 'THY1', 'H2-K', 'CD28', 'CD43', 'CD33', 'CD13',
           'CD15', 'CCDC101', 'MED12', 'TADA2B', 'TADA1', 'HPRT1', 'CUL3',
           'NF1', 'NF2'], dtype=object), 'ground_truth_label': 'score_drug_gene_rank', 'method': 'AdaBoostRegressor', 'adaboost_version': 'python', 'adaboost_learning_rate': 0.1, 'adaboost_n_estimators': 100, 'adaboost_max_depth': 3}
    sps = []
    for _ in range(num_runs):
        indices = np.random.permutation(normalized_features.shape[0])
        train = indices[:3500]
        test = indices[3500:]
        predictions, model = azimuth_adaboost(None, train, test, y, None, selected_features, None, None, learn_options, False)
        sps.append(spearmanr(predictions, y[test])[0])
    return sps
