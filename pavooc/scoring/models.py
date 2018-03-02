from torch import nn
import torch
from torch.nn.init import kaiming_normal, normal
import torch.nn.functional as F


def weights_init(m):
    if isinstance(m, (nn.Conv1d, nn.Linear)):
        kaiming_normal(m.weight.data)
        try:
            kaiming_normal(m.bias.data)
        except ValueError:
            normal(m.bias.data)


# TODO as seen here
# https://github.com/pytorch/examples/blob/master/mnist/main.py#L620
# we could also use F.relu instead of using whole layers
# Linear Regression Model
class LinearRegression(nn.Module):
    def __init__(self, input_size):
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(input_size, 1)

    def forward(self, x):
        out = self.linear(x)
        return out


class Net1(nn.Module):
    '''
    Net1 is a simple network consisting of one hidden layer with variable size
    '''

    def __init__(self, input_size):
        super(Net1, self).__init__()
        self.fc1 = nn.Linear(input_size, 300)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(300, 1)  # output layer

    def forward(self, x):
        out = self.fc1(x)
        # out = self.relu(out)
        out = self.fc2(out)
        return out


# TODO check for dead units!!
# TODO regularization?
class Net2(nn.Module):
    '''
    Net2 is a more complex network consisting of two hidden layers with 400
    and 300 neurons
    '''
    hidden1 = 400
    hidden2 = 300

    def __init__(self, input_size):
        super(Net2, self).__init__()
        self.fc1 = nn.Linear(input_size, self.hidden1)
        self.relu1 = nn.ReLU()  # TODO try TANH
        self.fc2 = nn.Linear(self.hidden1, self.hidden2)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(self.hidden2, 1)  # output

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        return out


# TODO check for dead units!!
# TODO regularization?
class Net3(nn.Module):
    '''
    Net3 is a neural network consisting of four hidden layers with sizes 400,
    300, 300 and 70
    '''
    layer_sizes = [400, 300, 300, 70]
    hidden1 = 400
    hidden2 = 300
    hidden3 = 300
    hidden4 = 70

    def __init__(self, input_size):
        super(Net3, self).__init__()
        self.fc1 = nn.Linear(input_size, self.hidden1)
        self.relu1 = nn.ReLU()  # TODO try TANH
        self.fc2 = nn.Linear(self.hidden1, self.hidden2)
        self.relu2 = nn.ReLU()  # TODO try TANH
        self.fc3 = nn.Linear(self.hidden2, self.hidden3)
        self.relu3 = nn.ReLU()  # TODO try TANH
        self.fc4 = nn.Linear(self.hidden3, self.hidden4)
        self.relu4 = nn.ReLU()
        self.fc5 = nn.Linear(self.hidden4, 1)  # output

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        out = self.relu3(out)
        out = self.fc4(out)
        out = self.relu4(out)
        out = self.fc5(out)
        return out


# TODO check for dead units!!
# TODO regularization?
class Net4(nn.Module):
    '''
    Net4 is a neural network consisting of five hidden layers with sizes 400,
    300, 200, 100 and 60
    '''
    hidden1 = 400
    hidden2 = 300
    hidden3 = 200
    hidden4 = 100
    hidden5 = 60

    def __init__(self, input_size):
        super(Net4, self).__init__()
        self.fc1 = nn.Linear(input_size, self.hidden1)
        self.relu1 = nn.ReLU()  # TODO try TANH
        self.fc2 = nn.Linear(self.hidden1, self.hidden2)
        self.relu2 = nn.ReLU()  # TODO try TANH
        self.fc3 = nn.Linear(self.hidden2, self.hidden3)
        self.relu3 = nn.ReLU()  # TODO try TANH
        self.fc4 = nn.Linear(self.hidden3, self.hidden4)
        self.relu4 = nn.ReLU()
        self.fc5 = nn.Linear(self.hidden4, self.hidden5)
        self.relu5 = nn.ReLU()
        self.fc6 = nn.Linear(self.hidden5, 1)  # output
        self.apply(weights_init)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        out = self.relu3(out)
        out = self.fc4(out)
        out = self.relu4(out)
        out = self.fc5(out)
        out = self.relu5(out)
        out = self.fc6(out)
        return out


# TODO check for dead units!!
# TODO regularization?
class Net5(nn.Module):
    '''
    Net5 is a neural network consisting of five hidden layers with sizes 400,
    300, 200, 100 and 60
    Furthermore there are three dropout layers
    '''
    hidden1 = 400
    hidden2 = 300
    hidden3 = 200
    hidden4 = 100
    hidden5 = 60

    # TODO try one more dropout after relu1
    def __init__(self, input_size):
        super(Net5, self).__init__()
        self.fc1 = nn.Linear(input_size, self.hidden1)
        self.relu1 = nn.ReLU()  # TODO try TANH
        self.fc2 = nn.Linear(self.hidden1, self.hidden2)
        self.relu2 = nn.ReLU()  # TODO try TANH
        self.drop1 = nn.Dropout(0.20)
        self.fc3 = nn.Linear(self.hidden2, self.hidden3)
        self.relu3 = nn.ReLU()  # TODO try TANH
        self.drop2 = nn.Dropout(0.15)
        self.fc4 = nn.Linear(self.hidden3, self.hidden4)
        self.relu4 = nn.ReLU()
        self.drop3 = nn.Dropout(0.15)
        self.fc5 = nn.Linear(self.hidden4, self.hidden5)
        self.relu5 = nn.ReLU()
        self.fc6 = nn.Linear(self.hidden5, 1)  # output
        self.apply(weights_init)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.drop1(out)
        out = self.fc3(out)
        out = self.relu3(out)
        out = self.drop2(out)
        out = self.fc4(out)
        out = self.relu4(out)
        out = self.drop3(out)
        out = self.fc5(out)
        out = self.relu5(out)
        out = self.fc6(out)
        return out

# TODO check for dead units!!
# TODO regularization?


class DynamicNet(nn.Module):
    '''
    DynamicNet is a nonworking network which can easily adapted by changing the
    layer_sizes array
    '''
    layer_sizes = [400, 300, 300, 70]

    def __init__(self, input_size):
        super(Net3, self).__init__()

        self.fcs = []
        self.relus = []
        last_size = input_size
        for i, size in enumerate(self.layer_sizes):
            self.fcs.append(nn.Linear(last_size, size))
            self.relus.append(nn.ReLU())
            last_size = size

        self.fcs.append(nn.Linear(last_size, 1))
        self.relus.append(None)

    def forward(self, x):
        out = x
        for fc, activation in zip(self.fcs, self.relus):
            out = fc(out)
            if activation:
                out = activation(out)

        return out


class CNN(nn.Module):
    kernel_size = 6

    def __init__(self, input_size):
        super(CNN, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=128, kernel_size=self.kernel_size)
        # self.conv2 = nn.Conv1d(
        #     in_channels=32, out_channels=64, kernel_size=self.kernel_size)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 25*32

        # hidden layers, additional_features, conv output
        self.fc1 = nn.Linear((input_size - 120) +
                             self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)
        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.max_pool1d(conv1_output, 4)

        # conv2_output = F.relu(self.conv2(conv1_output))
        # conv2_output = F.max_pool1d(conv2_output, 2)

        return conv1_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features, additional_features = x.split(120, dim=1)
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)

        # two fully connected hidden layers
        out = F.relu(self.fc1(torch.cat(
            [additional_features, convolution_output], 1)))

        return self.fc2(out)


class Deep1(nn.Module):
    '''
    A combination of an LSTM and Conv layers
    4 is the nucleotide encoding (4 bit per nucleotide)
    30 is the length of our input sequence
    120 is 4*30 the number of sequence features
    input_size is the number of total input_features.
    The first 120 have to be the sequence 1-hot-encodings
    '''
    lstm_hidden = 32
    kernel_size = 4

    def __init__(self, input_size):
        super(Deep1, self).__init__()

        self.lstm = nn.LSTM(input_size=4, hidden_size=self.lstm_hidden, num_layers=2,
                            dropout=0.18, bidirectional=False)  # TODO enable?

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=32, kernel_size=self.kernel_size)
        self.conv2 = nn.Conv1d(
            in_channels=32, out_channels=64, kernel_size=self.kernel_size)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 64 * 5

        # hidden layers, additional_features, conv output
        self.fc1 = nn.Linear(
            self.lstm_hidden + (input_size - 120) + self._conv_output_dimension, 64)
        self.fc2 = nn.Linear(64, 1)

        self.apply(weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)
        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.max_pool1d(conv1_output, 2)

        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.max_pool1d(conv2_output, 2)
        # TODO add dropout here

        return conv2_output.view(-1, self._conv_output_dimension)

    def _forward_lstm(self, nuc_features):
        # lstm needs form (seq_len, batch, input_size)
        lstm_input = nuc_features.view(-1, 30, 4).permute(1, 0, 2)

        # return only last seq-output. Form: (batch_size x lstm_hidden)
        lstm_output = self.lstm(lstm_input)[0][-1, :, :]
        return lstm_output

    def forward(self, x):
        nuc_features, additional_features = x.split(120, dim=1)
        nuc_features.contiguous()

        lstm_output = self._forward_lstm(nuc_features)
        convolution_output = self._forward_convolution(nuc_features)

        # two fully connected hidden layers
        out = F.relu(self.fc1(torch.cat(
            [lstm_output, additional_features, convolution_output], 1)))

        return self.fc2(out)


# try stride 2
class CNN38(nn.Module):
    def __init__(self, input_size):
        super(CNN38, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=128, kernel_size=4, stride=1)  # boost this?
        self.conv2 = nn.Conv1d(
            in_channels=128, out_channels=512, kernel_size=4)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 512 * 3

        # hidden layers, additional_features, conv output

        self.pre_fc = nn.Linear(input_size, 256)
        self.fc1 = nn.Linear(256 + self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.dropout(conv1_output, 0.4, self.training)


        conv1_output = F.max_pool1d(conv1_output, 3)
        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.dropout(conv2_output, 0.5, self.training)
        conv2_output = F.max_pool1d(conv2_output, 2)
        return conv2_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features = x[:, :120]
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers

        pre_output = self.pre_fc(x)
        pre_output = F.dropout(pre_output, 0.55, self.training)

        out = F.relu(self.fc1(torch.cat(
            [pre_output, convolution_output], 1)))

        out = F.dropout(out, 0.55, self.training)

        return self.fc2(out)


class CNN34(nn.Module):
    def __init__(self, input_size):
        super(CNN34, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=64, kernel_size=5)
        self.conv2 = nn.Conv1d(
            in_channels=64, out_channels=128, kernel_size=4)
        self.conv3 = nn.Conv1d(
            in_channels=128, out_channels=256, kernel_size=2) # TODO was 256

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 256 * 2

        # hidden layers, additional_features, conv output

        self.pre_fc = nn.Linear(input_size, 256)
        self.fc1 = nn.Linear(256 + self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.dropout(conv1_output, 0.3, self.training)
        conv1_output = F.max_pool1d(conv1_output, 2)

        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.dropout(conv2_output, 0.4, self.training)
        conv2_output = F.max_pool1d(conv2_output, 2)

        conv3_output = F.relu(self.conv3(conv2_output))
        conv3_output = F.dropout(conv3_output, 0.5, self.training)
        conv3_output = F.max_pool1d(conv3_output, 2)
        return conv3_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features = x[:, :120]
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers

        pre_output = F.relu(self.pre_fc(x))
        pre_output = F.dropout(pre_output, 0.5, self.training)

        out = F.relu(self.fc1(torch.cat(
            [pre_output, convolution_output], 1)))

        out = F.dropout(out, 0.55, self.training)

        return self.fc2(out)
