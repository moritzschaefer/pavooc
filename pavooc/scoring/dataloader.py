import torch
from torch import cuda
import numpy as np


class DataLoader(object):
    '''Simple data provider for datasets that
       fit in GPU memory completely.
       data: Dataset
       batch_size: batch size (default: 128)

       returns: batch-sized tensors. Iteration
       stops when epoch is completed.
       Every epoch a new suffle of the data is
       generated.

    '''

    def __init__(self, data, batch_size=128):
        self._n_examples = len(data)
        self.batch_index = 0
        self.batch_size = batch_size
        self._update_permutation()
        self.data = data

    def __iter__(self):
        return self

    def _update_permutation(self):
        '''Update the list of indices defining the order
           in which examples are provided. Meant to be
           called once an epoch.
        '''
        self.permutation = np.random.permutation(self._n_examples)

    def _get_batch(self):
        example_indices = self.permutation[self.batch_index:
                                           self.batch_index + self.batch_size]

        example_indices = torch.from_numpy(example_indices).long()
        if cuda.is_available():
            example_indices = example_indices.cuda()
        data_batch = torch.index_select(
            self.data.data_tensor, dim=0, index=example_indices)
        target_batch = torch.index_select(
            self.data.target_tensor, dim=0, index=example_indices)
        return data_batch, target_batch

    def __next__(self):
        if self.batch_index + self.batch_size > self._n_examples:
            self.batch_index = 0
            self._update_permutation()
            raise StopIteration
        else:
            batch = self._get_batch()
            self.batch_index += self.batch_size
            return batch
