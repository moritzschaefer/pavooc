'''
non working models
'''


class CNN5(nn.Module):
    '''three layer CNN'''
    kernel_size = 2

    def __init__(self, input_size):
        super(CNN5, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=8, kernel_size=self.kernel_size)
        self.conv2 = nn.Conv1d(
            in_channels=8, out_channels=16, kernel_size=self.kernel_size)
        self.conv3 = nn.Conv1d(
            in_channels=16, out_channels=32, kernel_size=self.kernel_size)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 32*6

        # hidden layers, additional_features, conv output
        self.fc1 = nn.Linear((input_size) +
                             self._conv_output_dimension, 1)
        self.apply(models.weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        out = F.relu(self.conv1(conv_input))

        out = F.relu(self.conv2(out))
        out = F.max_pool1d(out, 2)  # TODO delete this dropout??

        out = F.relu(self.conv3(out))
        out = F.max_pool1d(out, 2)

        out = F.dropout(out, 0.5, self.training)

        return out.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features, additional_features = x.split(120, dim=1)
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers
        return self.fc1(torch.cat([x, convolution_output], 1))


class CNN6(nn.Module):
    '''three layer CNN'''
    kernel_size = 2

    def __init__(self, input_size):
        super(CNN6, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=8, kernel_size=self.kernel_size)
        self.conv2 = nn.Conv1d(
            in_channels=8, out_channels=32, kernel_size=self.kernel_size)
        self.conv3 = nn.Conv1d(
            in_channels=32, out_channels=64, kernel_size=self.kernel_size)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 6*64  # too much!

        # hidden layers, additional_features, conv output
        self.fc1 = nn.Linear((input_size) +
                             self._conv_output_dimension, 128)
        self.fc2 = nn.Linear(128, 1)
        self.apply(models.weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        out = F.relu(self.conv1(conv_input))

        out = F.relu(self.conv2(out))
        out = F.dropout(out, 0.4, self.training)

        out = F.relu(self.conv3(out))
        out = F.dropout(out, 0.6, self.training)
        out = F.max_pool1d(out, 4) # pool 3 or 4?

        return out.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features, additional_features = x.split(120, dim=1)
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers
        out = F.relu(self.fc1(torch.cat([x, convolution_output], 1)))

        out = F.dropout(out, 0.6, self.training)

        return self.fc2(out)


class CNN31(nn.Module):
    kernel_size = 5

    def __init__(self, input_size):
        super(CNN31, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=16, kernel_size=2)
        self.conv2 = nn.Conv1d(
            in_channels=16, out_channels=64, kernel_size=5)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 12 * 64

        # hidden layers, additional_features, conv output
        self.fc1 = nn.Linear((input_size) +
                             self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(models.weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)
        conv1_output = F.relu(self.conv1(conv_input))

        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.dropout(conv2_output, 0.6, self.training)
        conv2_output = F.max_pool1d(conv2_output, 2)

        return conv2_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features = x[:, :120]
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers
        out = F.relu(self.fc1(torch.cat(
            [x, convolution_output], 1)))

        out = F.dropout(out, 0.6, self.training)

        return self.fc2(out)


class CNN33(nn.Module):
    kernel_size = 5

    def __init__(self, input_size):
        super(CNN33, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=64, kernel_size=4)
        self.conv2 = nn.Conv1d(
            in_channels=64, out_channels=256, kernel_size=4)
        self.conv3 = nn.Conv1d(
            in_channels=256, out_channels=512, kernel_size=3)# zu viel..

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 512 * 1

        # hidden layers, additional_features, conv output

        self.pre_fc = nn.Linear(input_size, 128)
        self.fc1 = nn.Linear(128 + self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(models.weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.dropout(conv1_output, 0.2, self.training)
        conv1_output = F.max_pool1d(conv1_output, 2)

        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.dropout(conv2_output, 0.35, self.training)
        conv2_output = F.max_pool1d(conv2_output, 2)

        conv3_output = F.relu(self.conv3(conv2_output))
        conv3_output = F.dropout(conv3_output, 0.45, self.training)
        conv3_output = F.max_pool1d(conv3_output, 2)

        return conv3_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features = x[:, :120]
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers

        pre_output = self.pre_fc(x)
        pre_output = F.dropout(pre_output, 0.3, self.training)

        out = F.relu(self.fc1(torch.cat(
            [pre_output, convolution_output], 1)))

        out = F.dropout(out, 0.45, self.training)

        return self.fc2(out)


class CNN37(nn.Module):
    def __init__(self, input_size):
        super(CNN37, self).__init__()

        self.conv1 = nn.Conv1d(
            in_channels=4, out_channels=64, kernel_size=4, stride=2) # boost this?
        self.conv2 = nn.Conv1d(
            in_channels=64, out_channels=128, kernel_size=2)

        # 128 kernels, 30-3 => 27/2 => 13-3 => 10/2 => 5
        self._conv_output_dimension = 128 * 6

        # hidden layers, additional_features, conv output

        self.pre_fc = nn.Linear(input_size, 256)
        self.fc1 = nn.Linear(256 + self._conv_output_dimension, 32)
        self.fc2 = nn.Linear(32, 1)

        self.apply(models.weights_init)

    def _forward_convolution(self, nuc_features):

        conv_input = nuc_features.view(-1, 30, 4).permute(0, 2, 1)

        conv1_output = F.relu(self.conv1(conv_input))
        conv1_output = F.dropout(conv1_output, 0.25, self.training)

        conv2_output = F.relu(self.conv2(conv1_output))
        conv2_output = F.dropout(conv2_output, 0.4, self.training)
        conv2_output = F.max_pool1d(conv2_output, 2)
        return conv2_output.view(-1, self._conv_output_dimension)

    def forward(self, x):
        nuc_features = x[:, :120]
        nuc_features.contiguous()

        convolution_output = self._forward_convolution(nuc_features)
        # two fully connected hidden layers

        pre_output = self.pre_fc(x)
        pre_output = F.dropout(pre_output, 0.5, self.training)

        out = F.relu(self.fc1(torch.cat(
            [pre_output, convolution_output], 1)))

        out = F.dropout(out, 0.55, self.training)

        return self.fc2(out)
