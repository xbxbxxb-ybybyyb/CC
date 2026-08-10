import torch.nn as nn

__all__ = ['DNN']


class DNN(nn.Module):
    def __init__(self, input_size, hidden_size_list, dropout_prob):
        super(DNN, self).__init__()
        self.input_size = input_size
        self.hidden_size_list = hidden_size_list
        self.dropout_prob = dropout_prob
        self.h = nn.ModuleList()

        for i, j in zip((self.input_size,) + self.hidden_size_list[:-1], self.hidden_size_list):
            self.h.append(
                nn.Sequential(
                    nn.Linear(in_features=i, out_features=j, bias=True),
                    nn.ELU(),
                    nn.Dropout(p=self.dropout_prob),
                )
            )

        self.dense = nn.Linear(in_features=self.hidden_size_list[-1], out_features=1, bias=True)

    def forward(self, inputs):
        for m in self.h:
            inputs = m(inputs)
        outputs_raw = self.dense(inputs)
        outputs = outputs_raw.squeeze()
        return outputs
