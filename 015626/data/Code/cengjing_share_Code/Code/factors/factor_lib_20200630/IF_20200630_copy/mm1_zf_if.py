from factor_generator import FactorGenerator
import pandas as pd
import numpy as np


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


class mm1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        super(mm1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        sig = data['close_spot_if']
        sig = rolling_normalize(sig, window=60)
        sig = sig.rolling(20, min_periods=5).mean()
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
