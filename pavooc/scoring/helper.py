import numpy as np
from pycrayon import CrayonClient
from scipy.stats import spearmanr

import torch
from torch.autograd import Variable

from pavooc.scoring.training import train_predict


crayon = CrayonClient(hostname="localhost", port=8889)


def run_model(combined_features, y, validation_fold, model_class, loss,
              learning_rate, epochs, feature_selector):
    if isinstance(learning_rate, dict):
        learning_rate_str = '|'.join(
            [str(v) for v in learning_rate['milestones']])
    else:
        learning_rate_str = str(learning_rate)
    experiment_name = '{}_{}_{}_{}_{}'.format(
        model_class.__name__, learning_rate_str, epochs,
        loss.__class__.__name__, np.sum(feature_selector))
    try:
        # TODO back it up instead of deleting
        crayon.remove_experiment(experiment_name)
        print('Experiment {} already existed. Deleting.'.
              format(experiment_name))
    except ValueError:
        pass

    tensorboard_experiment = crayon.create_experiment(experiment_name)
    losses, spearmans, model = train_predict(
        combined_features[:,
                          feature_selector], y, validation_fold, model_class,
        learning_rate, loss, epochs, tensorboard_experiment)
    return losses, spearmans, model


def run_models(combined_features, y, validation_fold, configs):
    '''
    Run CV for all models and configurations in configs.
    :returns: (losses, spearmans, bestmodel)
    '''
    results = []
    for i, config in enumerate(configs):
        print(i + 1)
        results.append(run_model(combined_features,
                                 y, validation_fold, **config))

    return results


def train_predict_n_shuffles(
        model_class, normalized_features,
        feature_selector, y, num_runs=20,
        learning_rate=0.0003, epochs=6000):
    sps = []
    test_sps = []
    models = []
    for i in range(num_runs):
        indices = np.random.permutation(normalized_features.shape[0])
        train_validate = indices[:4000]
        validation = np.random.permutation(4000)[:1000]
        test = indices[4000:]
        losses, predictions, model = run_model(
                normalized_features[train_validate, :],
                y[train_validate],
                np.array([x in validation for x in range(4000)]),
                model_class,
                torch.nn.MSELoss(),
                0.0003, 6002, feature_selector, str(i))
        sps.append(np.max(predictions))
        predicted_labels = model(
                Variable(
                    torch.from_numpy(
                        normalized_features[test, :][:, feature_selector])
                    )
                ).cpu().data.numpy()
        test_sps.append(spearmanr(predicted_labels, y[test])[0])
        models.append(model)
    print(sps, test_sps, models)
