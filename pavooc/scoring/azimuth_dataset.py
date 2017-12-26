from azimuth.load_data import from_file
import numpy as np


def load_dataset():
    '''
    Load the default azimuth dataset

    :returns: Xdf, Y, gene_position, target_genes
    '''

    # Default azimuth learn options
    # TODO densify learn_options! only a few options are needed
    learn_options = {'V': 3,
                     'train_genes': np.array(
                         ['CD5', 'CD45', 'THY1', 'H2-K', 'CD28', 'CD43', 'CD33', 'CD13',
                          'CD15', 'CCDC101', 'MED12', 'TADA2B', 'TADA1', 'HPRT1', 'CUL3',
                          'NF1', 'NF2'], dtype=str),
                     'test_genes': np.array(
                         ['CD5', 'CD45', 'THY1', 'H2-K', 'CD28', 'CD43', 'CD33', 'CD13',
                          'CD15', 'CCDC101', 'MED12', 'TADA2B', 'TADA1', 'HPRT1', 'CUL3',
                                             'NF1',
                                             'NF2'],
                         dtype=str),
                     'testing_non_binary_target_name': 'ranks',
                     'include_pi_nuc_feat': True,
                     'gc_features': True,
                     'nuc_features': True,
                     'include_gene_position': True,
                     'include_NGGX_interaction': True,
                     'include_Tm': True,
                     'include_strand': False,
                     'include_gene_feature': False,
                     'include_gene_guide_feature': 0,
                     'extra pairs': False,
                     'weighted': None,
                     'training_metric': 'spearmanr',
                     'NDGC_k': 10,
                     'cv': 'gene',
                     'include_gene_effect': False,
                     'include_drug': False,
                     'include_sgRNAscore': False,
                     'adaboost_loss': 'ls',
                     'adaboost_alpha': 0.5,
                     'normalize_features': False,
                     'adaboost_CV': False,
                     'num_proc': 8,
                     'num_thread_per_proc': None,
                     'order': 2,
                     'all pairs': False,
                     'include_known_pairs': False,
                     'seed': 1,
                     'flipV1target': False,
                     'num_genes_remove_train': None,
                     'include_microhomology': False,
                     'algorithm_hyperparam_search': 'grid',
                     'binary target name': 'score_drug_gene_threshold',
                     'rank-transformed target name': 'score_drug_gene_rank',
                     'raw target name': None}
    return from_file(None, learn_options=learn_options)
