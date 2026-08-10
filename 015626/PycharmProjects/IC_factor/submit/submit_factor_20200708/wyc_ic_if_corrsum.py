from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_icihif(FactorGenerator):
    def __init__(self):
        required_columns=['close_ic','volume_if','close_if','volume_ic']
        lookback_bars=2000
        super(wyc_icihif, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 60
        factor1 = correlation(df.close_if, df.volume_ic, N)
        factor2 = correlation(df.close_ic, df.volume_if, N)
        factor = -1 * (factor1 + factor2)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor