from factor_generator import FactorGenerator
from operators import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_ts2_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot', 'volume_spot']
        lookback_bars=2000
        super(wyc_ts2_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = mean(mean((sign(delta(df['volume_spot'], 5)) * (-1 * delta(df['close_spot'], 5))),2),10)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor