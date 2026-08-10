import torch
import torch.nn as nn


class Network(nn.Module):
    def __init__(self, window_size, num_factors, hidden_size, dropout_prob):
        super(Network, self).__init__()
        self.window_size = window_size
        self.num_factors = num_factors
        self.hidden_size = hidden_size
        self.dropout_prob = dropout_prob
        self.cnn = CNN(window_size=self.window_size, in_features=self.num_factors, ot_features=self.hidden_size, dropout_prob=self.dropout_prob)
        self.rnn = RNN(window_size=self.window_size, hidden_size=self.hidden_size)
        self.fcn = FCN(hidden_size=self.hidden_size, dropout_prob=self.dropout_prob)

    def forward(self, x):
        # x: (batch_size, window_size, num_factors)
        x = torch.clamp(x, min=-5, max=5)
        x = self.cnn(x)  # (batch_size, window_size, hidden_size)
        x = self.rnn(x)  # (batch_size, hidden_size)
        x = self.fcn(x)  # (batch_size)
        return x


class CNN(nn.Module):
    def __init__(self, window_size, in_features, ot_features, dropout_prob):
        super(CNN, self).__init__()
        self.window_size = window_size
        self.in_features = in_features
        self.ot_features = ot_features
        self.dropout_prob = dropout_prob
        self.conv0 = nn.Conv1d(in_channels=self.in_features, out_channels=self.ot_features, kernel_size=1, padding=0)
        self.conv1 = nn.Conv1d(in_channels=self.in_features, out_channels=self.ot_features, kernel_size=2, padding=1)
        self.conv2 = nn.Conv1d(in_channels=self.ot_features, out_channels=self.ot_features, kernel_size=2, padding=1)
        self.activate = nn.ELU()
        self.dropout = nn.Dropout(p=self.dropout_prob)

    def forward(self, x):
        # x: (batch_size, window_size, in_features)
        x = x.permute(0, 2, 1)  # (batch_size, in_features, window_size)
        r = self.conv0(x)  # (batch_size, ot_features, window_size)
        x = self.conv1(x)  # (batch_size, hidden_size, window_size + 1)
        x = x[:, :, :self.window_size]  # (batch_size, hidden_size, window_size)
        x = self.activate(x)
        x = self.dropout(x)
        x = self.conv2(x)  # (batch_size, ot_features, window_size + 1)
        x = x[:, :, :self.window_size]  # (batch_size, ot_features, window_size)
        x = self.activate(x)
        x = self.dropout(x)
        x = self.activate(x + r)  # (batch_size, ot_features, window_size)
        x = x.permute(0, 2, 1)  # (batch_size, window_size, ot_features)
        return x


class RNN(nn.Module):
    def __init__(self, window_size, hidden_size):
        super(RNN, self).__init__()
        self.window_size = window_size
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size=self.hidden_size, hidden_size=self.hidden_size, batch_first=True)

    def forward(self, x):
        # x: (batch_size, window_size, hidden_size)
        x, _ = self.lstm(x)  # (batch_size, window_size, hidden_size)
        x = x[:, self.window_size - 1, :]  # (batch_size, hidden_size)
        return x


class FCN(nn.Module):
    def __init__(self, hidden_size, dropout_prob):
        super(FCN, self).__init__()
        self.hidden_size = hidden_size
        self.dropout_prob = dropout_prob
        self.dense = nn.Linear(in_features=self.hidden_size, out_features=1)
        self.dropout = nn.Dropout(p=self.dropout_prob)

    def forward(self, x):
        # x: (batch_size, hidden_size)
        x = self.dropout(x)
        x = self.dense(x)  # (batch_size, 1)
        x = x.squeeze(dim=1)  # (batch_size)
        return x


def main():
    network = Network(window_size=10, num_factors=1000, hidden_size=200, dropout_prob=0.1)
    for name, param in network.named_parameters():
        print(name, param.shape)

    num_params = sum([param.nelement() for param in network.parameters()])
    print('number of parameters: {}'.format(num_params))

    x = torch.rand(1, 10, 1000, dtype=torch.float)
    y = network(x)
    print(x.shape)
    print(y.shape)
    return None


if __name__ == '__main__':
    main()
