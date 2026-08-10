import torch
import torch.nn as nn


class Network(nn.Module):
    def __init__(self, window_size, num_factors):
        super(Network, self).__init__()
        self.window_size = window_size
        self.num_factors = num_factors

    def forward(self, x):
        # x: (batch_size, window_size, num_factors)
        x = torch.clamp(x, min=-5, max=5)
        x = x[:, self.window_size - 1, :]  # (batch_size, num_factors)
        x = torch.mean(x, dim=1)  # (batch_size)
        return x


def main():
    network = Network(window_size=10, num_factors=1000)
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
