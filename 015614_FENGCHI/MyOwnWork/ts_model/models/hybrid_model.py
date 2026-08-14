import torch.nn as nn


class LSTMTransformer(nn.Module):
    def __init__(self, input_dim, hidden_dim, lstm_layers, transformer_heads, transformer_layers, output_dim, dropout=0.5):
        super(LSTMTransformer, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, lstm_layers, dropout=dropout, batch_first=True)
        transformer_encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=transformer_heads,
            dim_feedforward=hidden_dim * 2,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(transformer_encoder_layer, num_layers=transformer_layers)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        transformer_input = lstm_out
        transformer_out = self.transformer_encoder(transformer_input)
        output = self.fc(transformer_out[:, -1, :])
        return output

