from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_icifih_mul(FactorGenerator):
    def __init__(self):
        required_columns=['close','close_if','close_ih']
        lookback_bars=2000
        super(wyc_icifih_mul, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        factor = df.close * df.close_if / df.close_ih
        factor = factor - mean(factor, 300)
        factor = factor.to_frame()
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor