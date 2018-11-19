import pickle
import os
import logging
import copy
import pandas as pd

from sklearn.externals import joblib

import torch
# from torch.utils.data import DataLoader
from torch import nn, cuda

from torch.autograd import Variable
from torch.optim.lr_scheduler import MultiStepLR
from pycrayon import CrayonClient
from tensorboardX import SummaryWriter

import scipy.stats as st
import numpy as np

from pavooc.scoring.feature_extraction import extract_features, \
    split_test_train_valid, normalize_features
from pavooc.scoring.azimuth_dataset import load_dataset
from pavooc.scoring.dataloader import DataLoader
from pavooc.config import BATCH_SIZE, WEIGHTS_DIR, \
    CONSERVATION_FEATURES_FILE, SCALER_FILE, DATADIR

if cuda.is_available():
    import torch.backends.cudnn as cudnn
    cudnn.benchmark = True

try:
    crayon = CrayonClient(hostname="localhost", port=8889)
except (ValueError, RuntimeError):
    crayon = None

try:
    os.mkdir(WEIGHTS_DIR)
except FileExistsError:
    pass


def to_np(x):
    return x.data.cpu().numpy()


def _init_model(feature_length, model_class, loss, learning_rate):
    model = model_class(feature_length)
    optimizer_class = torch.optim.Adam

    # Loss and Optimizer
    criterion = loss
    if cuda.is_available():
        model.cuda()
        criterion = criterion.cuda()
    if isinstance(learning_rate, dict):
        optimizer = optimizer_class(model.parameters(),
                                    lr=learning_rate['initial'])
        scheduler = MultiStepLR(
            optimizer, milestones=learning_rate['milestones'],
            gamma=learning_rate['gamma'])
    else:
        optimizer = optimizer_class(model.parameters(), lr=learning_rate)
        scheduler = None

    return model, criterion, optimizer, scheduler


def train_predict(combined_features, y, validation_fold, model_class,
                  learning_rate, loss, epochs,
                  tensorboard_experiment=None):
    '''
    Train with the provided model and parameters. Validate with the
    validation set
    '''
    try:
        experiment_name = tensorboard_experiment.xp_name
    except AttributeError:
        experiment_name = tensorboard_experiment
        writer = SummaryWriter(log_dir=f'runs/{experiment_name}')
    combined_train_features = combined_features[(~validation_fold), :]

    validation_tensor = torch.from_numpy(combined_features[validation_fold, :])
    training_tensor = torch.from_numpy(combined_train_features)
    if cuda.is_available():
        validation_variable = Variable(
            validation_tensor.cuda(), requires_grad=False)  # cuda(async=True) causes SyntaxError :/
        training_variable = Variable(
            training_tensor.cuda(), requires_grad=False)  # cuda(async=True) causes SyntaxError :/
    else:
        validation_variable = Variable(validation_tensor, requires_grad=False)
        training_variable = Variable(training_tensor, requires_grad=False)

    train_labels = y[~validation_fold]
    validation_labels = y[validation_fold]
    if cuda.is_available():
        train_dataset = torch.utils.data.TensorDataset(
            training_tensor.cuda(),
            torch.from_numpy(train_labels).cuda())
    else:
        train_dataset = torch.utils.data.TensorDataset(
            training_tensor, torch.from_numpy(train_labels))
    loader = DataLoader(train_dataset, BATCH_SIZE)
    # if cuda.is_available():
    #     loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
    #                         num_workers=8, pin_memory=True)
    # else:
    #     loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # first converge with normal features

    model, criterion, optimizer, scheduler = _init_model(
        combined_features.shape[1], model_class, loss, learning_rate)

    spearmans = []
    losses = []
    for epoch_idx in range(epochs):
        for batch_features, batch_targets in loader:
            if cuda.is_available():
                batch_features = batch_features.cuda()  # cuda(async=True) causes SyntaxError :/
                batch_targets = batch_targets.float().cuda()  # cuda(async=True) causes SyntaxError :/
            else:
                batch_targets = batch_targets.float()
            optimizer.zero_grad()
            outputs = model(Variable(batch_features))

            loss2 = criterion(outputs, Variable(batch_targets))
            loss2.backward()
            optimizer.step()
        try:
            scheduler.step()
        except (NameError, AttributeError):
            pass

        if ((epoch_idx + 1) % 10) == 0:
            # Set to evaluation mode (to disable dropout layers)
            model.eval()

            # predict validation and training scores
            predicted_labels = model(validation_variable).cpu().data.numpy()
            predicted_training_labels = model(
                training_variable).cpu().data.numpy()

            # validation scores
            spearman = st.spearmanr(validation_labels, predicted_labels)[0]
            if not (np.isfinite(predicted_labels).all()):
                logging.error(
                    'Model is buggy. some predicted label is not a number, reinitialize')
                model, criterion, optimizer, scheduler = _init_model(
                    combined_features.shape[1], model_class, loss, learning_rate)
                continue
            l1 = np.abs(predicted_labels - validation_labels).mean()
            l2 = ((predicted_labels - validation_labels)**2).mean()

            # training scores
            training_spearman = st.spearmanr(
                train_labels, predicted_training_labels)[0]
            if np.isnan(training_spearman):
                logging.error('Model is buggy. spearman is nan, reinitialize')
                model, criterion, optimizer, scheduler = _init_model(
                    combined_features.shape[1], model_class, loss, learning_rate)
                continue

            training_loss = criterion(
                Variable(torch.from_numpy(predicted_training_labels),
                         requires_grad=False),
                Variable(torch.from_numpy(train_labels),
                         requires_grad=False)).data[0]
            if not (np.isfinite(predicted_training_labels).all()):
                logging.error(
                    'Model is buggy. predicted training labels are non number somehow, reinitialize')
                model, criterion, optimizer, scheduler = _init_model(
                    combined_features.shape[1], model_class, loss, learning_rate)
                continue
            training_l1 = np.abs(
                predicted_training_labels - train_labels).mean()
            training_l2 = (
                (predicted_training_labels - train_labels)**2).mean()

            losses.append(training_loss)
            spearmans.append(spearman)

            # Set to training mode (to enable dropout layers)
            model.train()

            info = {
                'training-spearman': training_spearman,
                'trainingloss': training_loss,
                'training-l1': training_l1.item(),
                'training-l2': training_l2.item(),
                'validation-spearman': spearman,
                'validation-l1':  l1.item(),
                'validation-l2': l2.item()
            }

            if tensorboard_experiment:
                # (1) Log the scalar values

                for tag, value in info.items():
                    try:
                        tensorboard_experiment.add_scalar_value(
                            tag, value, step=epoch_idx + 1)
                    except AttributeError:
                        # tensorboard_experiment is a string and doesnt have
                        # add_scalar_value. fall back to tensorboard pytorch
                        writer.add_scalar(tag, value, epoch_idx + 1)

                    except Exception as e:
                        logging.fatal('caught exception adding scalar value '
                                      'to crayon: {}'.format(e))

            # only save weights if there was no better experiment before
            if spearman == max(spearmans):
                torch.save(model.state_dict(), '{}/{}_weights.torch'.format(
                    WEIGHTS_DIR, experiment_name))
                best_model = model_class(combined_features.shape[1])
                best_model.load_state_dict(copy.deepcopy(model.state_dict()))

    best_model.eval()
    return losses, spearmans, best_model


def cv_train_test(genes, transformed_features, y, model_class, learning_rate,
                  epochs, loss=nn.MSELoss(), folds='gene'):
    '''
    do one complete cross validation across all genes for the given model
    and configuration
    '''
    distinct_genes = genes.drop_duplicates()
    results = []
    experiment_name = '{}_{}_{}_{}'.format(
        model_class.__name__, learning_rate, epochs, loss.__class__.__name__)

    if folds == 'gene':
        validation_folds = [(genes == gene) for gene in distinct_genes]
    else:
        validation_folds = folds
    for i, validation_fold in enumerate(validation_folds):
        experiment_name_i = '{}_cv|{}'.format(experiment_name, i)
        try:
            # TODO back it up instead of deleting
            if crayon:
                crayon.remove_experiment(experiment_name_i)
                print('Experiment {} already existed. Deleting.'.format(
                    experiment_name_i))
        except ValueError:
            pass

        if crayon:
            tensorboard_experiment = crayon.create_experiment(
                experiment_name_i)
        else:
            tensorboard_experiment = experiment_name_i
        losses, spearmans, model = train_predict(
            transformed_features, y, validation_fold, model_class,
            learning_rate, loss, epochs, tensorboard_experiment)
        # print('Trained on fold {}/{}. Test gene: {}. Spearman: {}'
        # .format(i, len(target_genes), gene, spearman))
        results.append(max(spearmans))

    return results


def generate_final_model():
    Xdf, Y, gene_position, target_genes = load_dataset()
    conservation_scores = pd.read_csv(CONSERVATION_FEATURES_FILE, index_col=0)

    combined_features, y, genes, feature_names = extract_features(
        Xdf, Y, gene_position, conservation_scores, order=1)
    normalized_features, scaler = normalize_features(combined_features)
    X_train, X_test, y_train, y_test, validation_fold, _ = split_test_train_valid(
        combined_features, y, joint_scaling=True)

    joblib.dump(scaler, SCALER_FILE)

    tensorboard_experiment = 'final'
    L = normalized_features.shape[0]
    indices = np.random.permutation(L)
    validation_fold = np.array([i in indices[:750] for i in range(L)])


    losses, spearmans, model = train_predict(
        normalized_features, y, validation_fold, CNN38,
        0.003, nn.MSELoss(), 10000, tensorboard_experiment)

    torch.save(model.state_dict(), os.path.join(DATADIR, 'cnn38.torch'))
