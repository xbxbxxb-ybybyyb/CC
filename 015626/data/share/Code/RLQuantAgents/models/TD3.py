import torch
import torch.nn as nn
from copy import deepcopy
class Actor(nn.Module):
    def __init__(self, factor_dim:int, state_dim: int, d_model: int, num_actions:int):
        super(Actor, self).__init__()
        self.factor_embedding = nn.Sequential(
            nn.Linear(factor_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU()
        )
        self.state_embedding = nn.Sequential(
            nn.Linear(2, d_model // 4)
        )
        self.action_head = nn.Linear(d_model + d_model // 4, num_actions)

    def forward(self, factor_seq, state):
        # x = factor_seq.permute(0, 2, 1)
        # x1 = factor_seq.view(x.size(0), -1)
        # x2 = self.factor_embedding(x1)
        x2 = self.factor_embedding(factor_seq[:, -1, :])
        position = state[:, 0:1]
        # cumulative_return = state[:, 0:1]
        volatility = state[:, 1:2]
        #x3 = self.state_embedding(state[:, ])
        state = torch.cat([position, volatility], dim=-1) # B,2
        state_embed = self.state_embedding(state)
        x2 = torch.cat([x2, state_embed], dim=-1)
        action = self.action_head(x2)

        return action.tanh()

class CriticTwin(nn.Module):
    def __init__(self, factor_dim, state_dim, d_model, action_dim):
        super(CriticTwin, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.factor_embedding = nn.Sequential(
            nn.Linear(factor_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU()
        )

    def forward(self, state, action):
        values = self.get_q_values(state=state, action=action)
        value = values.mean(dim=-1, keepdim=True)
        return value

    def get_q_values(self, factor_seq, state, action):

        values = self.net(torch.cat(()))
        return values

class TD3Agent(nn.Module):
    def __init__(self, net_dims=256, state_dim=824, action_dim=1):
        super(TD3Agent, self).__init__()
        """
        Twin Delayed DDPG Algorithm
        """
        self.act = Actor(net_dims, state_dim, action_dim)
        self.cri = CriticTwin(net_dims, state_dim, action_dim)
        self.act_target = deepcopy(self.act)
        self.cri_target = deepcopy(self.cri)
        self.act_optimizer = torch.optim.Adam(self.act.parameters(), self.learning_rate)
        self.cri_optimizer = torch.optim.Adam(self.cri.parameters(), self.learning_rate)

    def __forward__(self):
        pass


if __name__ == '__main__':
    pass