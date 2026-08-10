from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_ts2_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume']
        lookback_bars=2000
        super(wyc_ts2_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = ts_mean(ts_mean((sign(delta(df['volume'], 5)) * (-1 * delta(df['close'], 5))),2),10)

        return factor