from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk


class sr1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'low_spot_if']
        super(sr1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_spot_if'] / data['close_spot_if'].shift(1) - 1
        vol = rtn.rolling(60, min_periods=30).std()
        vol[vol < 1e-8] = np.nan
        ret = data['close_spot_if'] / (data['low_spot_if'].shift(1).rolling(60, min_periods=30).min()) - 1
        sig = ret / vol
        sig = pd.Series(bk.move_rank(sig.values, 242 * 2, 121, axis=0), index=sig.index)
        sig = sig.rolling(5, min_periods=2).mean()
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
