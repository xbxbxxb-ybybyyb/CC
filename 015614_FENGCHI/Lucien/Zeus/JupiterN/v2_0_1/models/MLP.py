# coding: utf-8
# Author：fengchi863
# Date ：2023/12/14 13:07

import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, input_dim, hiddens, dropout):
        super(MLP, self).__init__()
        layers = []
        hiddens = [input_dim] + hiddens
        for i in range(len(hiddens) - 1):
            layers.append(nn.Linear(hiddens[i], hiddens[i + 1]))
            layers.append(nn.BatchNorm1d(hiddens[i + 1]))
            layers.append(nn.ReLU(inplace=True))

        layers.append(nn.Dropout(dropout))
        self.layers = nn.Sequential(*layers)
        self.out = nn.Linear(hiddens[-1], 1)
        self.apply(self.init_weights)

    def forward(self, x):
        b, n = x.shape
        x = self.layers(x)
        x = self.out(x)
        return x.reshape(b)

    @staticmethod
    def init_weights(module):
        classname = module.__class__.__name__
        if classname.find('BatchNorm') != -1:
            nn.init.normal_(module.weight.data, 0.0, 0.02)
            nn.init.constant_(module.bias.data, 0)
        elif classname.find('Linear') != -1:
            nn.init.normal_(module.weight.data, 0.0, 0.02)
            nn.init.constant_(module.bias.data, 0)