from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


class ss1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'high_spot_if']
        super(ss1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_spot_if'] / data['close_spot_if'].shift(5) - 1
        vol = rtn.rolling(250, min_periods=30).std()
        vol[vol < 1e-8] = np.nan
        ret = data['close_spot_if'] / (data['high_spot_if'].shift(5).rolling(250, min_periods=30).max()) - 1
        sig = ret / vol
        sig = pd.Series(bk.move_rank(sig.values, 242 * 5, 121, axis=0), index=sig.index)
        sig = rolling_normalize(sig, 242 * 5)
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
