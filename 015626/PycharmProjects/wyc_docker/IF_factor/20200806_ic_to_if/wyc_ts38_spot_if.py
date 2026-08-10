from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_spot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_if']
        lookback_bars=2000
        super(wyc_ts38_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 50
        stdN = 10
        temp1 = df.close_spot_if.copy()
        temp1[df.close_spot_if > delay(df.close_spot_if, 1)] = std(df.close_spot_if, stdN)
        temp1[df.close_spot_if <= delay(df.close_spot_if, 1)] = 0
        a = sma(temp1, smaM, 1)
        temp1[df.close_spot_if > delay(df.close_spot_if, 1)] = 0
        temp1[df.close_spot_if <= delay(df.close_spot_if, 1)] = std(df.close_spot_if, stdN)
        b = sma(temp1, smaM, 1)
        factor = a / (a + b) * 100
        factor = ts_rank_bk(factor, 120)
        factor = ts_mean(factor, 5)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor