from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


class rt1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'low_spot_if']
        super(rt1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        sig = data['close_spot_if'] / data['low_spot_if'].rolling(60, min_periods=30).min()
        sig = pd.Series(bk.move_rank(sig.values, 242 * 2, 121, axis=0), index=sig.index)
        sig = sig.rolling(10, min_periods=2).mean()
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
