import torch
from torch.utils.data import DataLoader
from torch import nn
from torch.autograd import Variable
from torch.optim.lr_scheduler import MultiStepLR
from pycrayon import CrayonClient

import scipy.stats as st
import numpy as np

from pavooc.config import BATCH_SIZE

crayon = CrayonClient(hostname="localhost", port=8889)
from IPython.core.debugger import Tracer


def to_np(x):
    return x.data.cpu().numpy()


def train_predict(combined_features, y, validation_fold, model_class,
                  learning_rate, loss, epochs,
                  tensorboard_experiment=None):
    '''
    Train with the provided model and parameters. Validate with the
    validation set
    '''

    combined_validation_features = combined_features[validation_fold, :]
    combined_train_features = combined_features[(~validation_fold), :]
    train_labels = y[~validation_fold]
    validation_labels = y[validation_fold]
    train_dataset = torch.utils.data.TensorDataset(torch.from_numpy(
        combined_train_features), torch.from_numpy(train_labels))
    loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # first converge with normal features

    model = model_class(combined_features.shape[1])

    # Loss and Optimizer
    # TOOD add weight_decay to Adam
    criterion = loss
    if isinstance(learning_rate, dict):
        optimizer = torch.optim.Adam(model.parameters(),
                                     lr=learning_rate['initial'])
        scheduler = MultiStepLR(
            optimizer, milestones=learning_rate['milestones'],
            gamma=learning_rate['gamma'])
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    spearmans = []
    losses = []
    for epoch_idx in range(epochs):
        for batch_features, batch_targets in loader:
            optimizer.zero_grad()
            outputs = model(Variable(batch_features))

            loss = criterion(outputs, Variable(batch_targets.float()))
            loss.backward()
            optimizer.step()
        try:
            scheduler.step()
        except NameError:
            pass
        # Set to evaluation mode (to disable dropout layers)
        model.eval()

        predicted_labels = model(Variable(torch.from_numpy(
            combined_validation_features))).data.numpy()
        spearman = st.spearmanr(validation_labels, predicted_labels)[0]
        losses.append(loss.data[0])
        spearmans.append(spearman)
        l1 = np.abs(predicted_labels - validation_labels).sum()
        l2 = ((predicted_labels - validation_labels)**2).sum()

        # Set to training mode (to enable dropout layers)
        model.train()

        if tensorboard_experiment:
            # (1) Log the scalar values
            info = {
                'trainingloss': loss.data[0],
                'validation-spearman': spearman,
                'validation-l1':  l1.item(),
                'validation-l2': l2.item()
            }

            for tag, value in info.items():
                try:
                    tensorboard_experiment.add_scalar_value(
                        tag, value, step=epoch_idx + 1)
                except:
                    Tracer()()

            # (2) Log values and gradients of the parameters (histogram)
            # TODO do we have named parameters?
            for tag, value in model.named_parameters():
                tag = tag.replace('.', '/')

                tensorboard_experiment.add_histogram_value(
                    tag, to_np(value).flatten().tolist(), tobuild=True,
                    step=epoch_idx + 1)
                tensorboard_experiment.add_histogram_value(
                    f'{tag}/grad', to_np(value.grad).flatten().tolist(),
                    tobuild=True,
                    step=epoch_idx + 1)

    # print(spearmans)
    return losses, spearmans


def cv_train_test(genes, transformed_features, y, model_class, learning_rate,
                  epochs, loss=nn.MSELoss()):
    '''
    do one complete cross validation across all genes for the given model
    and configuration
    '''
    distinct_genes = genes.drop_duplicates()
    results = []
    experiment_name = f'{model_class.__name__}_{learning_rate}_' \
        f'{epochs}_{loss.__class__.__name__}'
    for i, gene in enumerate(distinct_genes):
        experiment_name_i = f'{experiment_name}_{i}|{gene}'
        try:
            # TODO back it up instead of deleting
            crayon.remove_experiment(experiment_name_i)
            print(f'Experiment {experiment_name_i} already existed. Deleting.')
        except ValueError:
            pass

        tensorboard_experiment = crayon.create_experiment(experiment_name_i)
        validation_fold = (genes == gene)
        losses, spearmans = train_predict(
            transformed_features, y, validation_fold, model_class,
            learning_rate, loss, epochs, tensorboard_experiment)
        # print('Trained on fold {}/{}. Test gene: {}. Spearman: {}'
        # .format(i, len(target_genes), gene, spearman))
        results.append(max(spearmans))

    return results
