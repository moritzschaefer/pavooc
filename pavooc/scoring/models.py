from torch import nn


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

    def __init__(self, input_size):
        super(Net3, self).__init__()

        self.fcs = []
        self.relus = []
        last_size = input_size
        for size in self.layer_sizes:
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
