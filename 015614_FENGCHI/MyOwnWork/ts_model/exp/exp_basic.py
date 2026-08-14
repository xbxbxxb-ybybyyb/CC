import torch

from models.model import FeedForwardNN, SimpleRNN, LSTM, GRU, BiLSTM, BiGRU, CNN, Transformer
from models.hybrid_model import LSTMTransformer


class ExpBasic(object):
    def __init__(self, args):
        self.args = args
        self.model_dir = {
            'FeedForwardNN': FeedForwardNN,
            'SimpleRNN': SimpleRNN,
            'LSTM': LSTM,
            'GRU': GRU,
            'BiLSTM': BiLSTM,
            'BiGRU': BiGRU,
            'CNN': CNN,
            'Transformer': Transformer,
            'LSTMTransformer': LSTMTransformer,
        }
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model().to(self.device)

    def _build_model(self):
        raise NotImplementedError

    def _get_data(self, flag):
        pass

    def train(self):
        pass

    def validate(self):
        pass

    def test(self):
        pass
