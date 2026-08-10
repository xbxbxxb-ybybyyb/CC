import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: (batch_size, seq_len, d_model)
        Returns:
            (batch_size, seq_len, d_model)
        """
        return x + self.pe[:x.size(1)]


class TransformerQNetwork(nn.Module):
    def __init__(self, factor_dim=824, d_model=128, num_actions=11, num_heads=4, num_layers=3):
        super().__init__()
        # 因子特征处理分支
        self.factor_embedding = nn.Sequential(
            nn.Linear(factor_dim, d_model),
            nn.LayerNorm(d_model)
        )
        self.pos_encoder = PositionalEncoding(d_model, max_len=15)

        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=num_heads,
            dim_feedforward=d_model * 4,
            #batch_first=True,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # 状态特征处理分支 (仓位 + 累积收益 + 夏普比率)
        self.state_proj = nn.Sequential(
            nn.Linear(2, d_model // 2),  # 3个状态特征
            nn.ReLU(),
            nn.Linear(d_model // 2, d_model)
        )

        # 门控融合模块
        self.fusion_gate = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.Sigmoid()
        )

        # Dueling架构输出头
        self.value_stream = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Linear(d_model, 1)
        )
        self.advantage_stream = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Linear(d_model, num_actions)
        )

    def forward(self, factor_seq, state):#position, cumulative_return, sharpe_ratio):
        """
        Args:
            factor_seq: (B, 15, 824)  历史15分钟因子序列
            position: (B, 1)          当前仓位 [-1, 1]
            cumulative_return: (B, 1) 累积收益率
            sharpe_ratio: (B, 1)      夏普比率
        Returns:
            q_values: (B, num_actions)
            state_value: (B, 1)
        """
        #exit(0)
        position = state[:,0:1]
        #cumulative_return = state[:, 1:2]
        sharpe_ratio = state[:, 1:2]
        # 1. 处理时序因子特征
        x = self.factor_embedding(factor_seq)  # (B,15,d_model)
        x = self.pos_encoder(x)  # 添加时序位置编码
        context = self.transformer(x)  # (B,15,d_model)
        pooled = context.mean(dim=1)  # (B,d_model)

        # 2. 处理状态特征
        state = torch.cat([position, sharpe_ratio], dim=-1)  # (B,3)

        state_feat = self.state_proj(state)  # (B,d_model)

        # 3. 门控特征融合
        gate = self.fusion_gate(torch.cat([pooled, state_feat], dim=-1))  # (B,d_model)
        fused = gate * pooled + (1 - gate) * state_feat  # (B,d_model)

        # 4. Dueling DQN输出
        value = self.value_stream(fused)  # (B,1)
        advantage = self.advantage_stream(fused)  # (B,num_actions)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        print(q_values.shape, value.shape)
        return q_values, value



if __name__ == '__main__':
    print(torch.cuda.is_available())
    input_dim = 824
    action_dim = 10
    batch_size = 32
    seq_len = 15
    # model = Dueling_DQN(input_dim, action_dim)
    # test_input = torch.randn(batch_size, input_dim)
    # output = model(test_input)
    # print(test_input.shape)
    # print(output.shape)
    model = TransformerQNetwork(factor_dim=824, num_actions=10, d_model=128, num_heads=4, num_layers=3)
    test_input = torch.randn(batch_size, 15, input_dim)
    tes_pos = torch.randn(batch_size, 1)
    tes_cumulative_return = torch.randn(batch_size, 1)
    tes_sharp_ratio = torch.randn(batch_size, 1)
    q, value = model(test_input, tes_pos,tes_cumulative_return,tes_sharp_ratio)
