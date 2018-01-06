from torch import nn


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
        self.drop1 = nn.Dropout()
        self.fc3 = nn.Linear(self.hidden2, self.hidden3)
        self.relu3 = nn.ReLU()  # TODO try TANH
        self.drop2 = nn.Dropout()
        self.fc4 = nn.Linear(self.hidden3, self.hidden4)
        self.relu4 = nn.ReLU()
        self.drop3 = nn.Dropout()
        self.fc5 = nn.Linear(self.hidden4, self.hidden5)
        self.relu5 = nn.ReLU()
        self.fc6 = nn.Linear(self.hidden5, 1)  # output

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
