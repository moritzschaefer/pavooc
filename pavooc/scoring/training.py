import torch
from torch.utils.data import DataLoader
from torch import nn
from torch.autograd import Variable

import scipy.stats as st

from pavooc.config import BATCH_SIZE


def torch_cv_train_predict(combined_features, y, test_fold, model_class,
                           learning_rate, loss, epochs):
    '''
    Do one train/test step of a cross validation, given the fold, model,
    learning rate and loss
    '''

    combined_test_features = combined_features[test_fold.values, :]
    combined_train_features = combined_features[(~test_fold).values, :]
    train_labels = y[~test_fold]
    test_labels = y[test_fold]
    train_dataset = torch.utils.data.TensorDataset(torch.from_numpy(
        combined_train_features), torch.from_numpy(train_labels))
    loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # first converge with normal features

    model = model_class(combined_features.shape[1])

    # Loss and Optimizer
    criterion = loss
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

        # if (epoch_idx+1) % 5 == 0:
        #print (f'Epoch {epoch_idx+1}, Loss: {loss.data[0]:.4f}')
        if False:
            # if len(losses) > 0 and losses[-1] <= loss.data[0]: # TODO another criteria to jump out of local minima
            # print('Converged at epoch {} with training loss {} and validation spearman {}'.format(epoch_idx, losses[-1], spearmans[-1]))
            break
        else:
            losses.append(loss.data[0])

            predicted_labels = model(Variable(torch.from_numpy(
                combined_test_features))).data.numpy()
            spearmans.append(st.spearmanr(test_labels, predicted_labels)[0])

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
    for i, gene in enumerate(distinct_genes):
        test_fold = (genes == gene)
        losses, spearmans = torch_cv_train_predict(
            transformed_features, y, test_fold, model_class,
            learning_rate, loss, epochs)
        # print('Trained on fold {}/{}. Test gene: {}. Spearman: {}'
        # .format(i, len(target_genes), gene, spearman))
        results.append(max(spearmans))

    return results
