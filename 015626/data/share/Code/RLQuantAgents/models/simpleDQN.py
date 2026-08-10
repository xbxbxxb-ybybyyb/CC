import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class SimpleQNetwork(nn.Module):
    def __init__(self, factor_dim=824, d_model=256, num_actions=21, num_heads=4, num_layers=3):
        super().__init__()
        self.factor_embedding = nn.Sequential(
            nn.Linear(factor_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU()
        )
        self.state_embedding = nn.Sequential(
            nn.Linear(2, d_model // 4)
        )
        self.action_head = nn.Linear(d_model+d_model // 4, num_actions)
        self.value_head = nn.Linear(d_model+d_model // 4, 1)

    def forward(self, factor_seq, state):
        #x = factor_seq.permute(0, 2, 1)
        #x1 = factor_seq.view(x.size(0), -1)
        x2 = self.factor_embedding(factor_seq[:, -1, :])
        position = state[:, 0:1]
        # cumulative_return = state[:, 0:1]
        volatility = state[:, 1:2]
        #x3 = self.state_embedding(state[:, ])
        state = torch.cat([position, volatility], dim=-1) # B,2
        state_embed = self.state_embedding(state)
        x2 = torch.cat([x2, state_embed], dim=-1)
        value = self.value_head(x2)  # (B,1)
        advantage = self.action_head(x2)  # (B,num_actions)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values, value, x2, value, advantage
