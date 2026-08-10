from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

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
        sig = ts_rank(sig, 242 * 2)
        sig = sig.rolling(5, min_periods=2).mean()
        # sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
