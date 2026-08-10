import torch
import torch.nn as nn


class Network(nn.Module):
    def __init__(self, window_size, num_factors, hidden_size, dropout_prob):
        super(Network, self).__init__()
        self.window_size = window_size
        self.num_factors = num_factors
        self.hidden_size = hidden_size
        self.dropout_prob = dropout_prob

        self.linear1 = nn.Linear(in_features=self.num_factors, out_features=self.hidden_size)
        self.linear2 = nn.Linear(in_features=self.hidden_size, out_features=self.hidden_size // 2)
        self.linear3 = nn.Linear(in_features=self.hidden_size // 2, out_features=1)
        self.activate = nn.ELU()
        self.dropout = nn.Dropout(p=self.dropout_prob)

    def forward(self, x):
        # x: (batch_size, window_size, num_factors)
        x = torch.clamp(x, min=-5, max=5)
        x = x[:, self.window_size - 1, :]  # (batch_size, num_factors)
        x = self.linear1(x)  # (batch_size, hidden_size)
        x = self.activate(x)
        x = self.dropout(x)
        x = self.linear2(x)  # (batch_size, hidden_size / 2)
        x = self.activate(x)
        x = self.dropout(x)
        x = self.linear3(x)  # (batch_size, 1)
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
