from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts38_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 80
        stdN = 120
        temp1 = df.close.copy()
        temp1[df.close > delay(df.close, 1)] = std(df.close, stdN)
        temp1[df.close <= delay(df.close, 1)] = 0
        a = sma(temp1, smaM, 1)
        temp1[df.close > delay(df.close, 1)] = 0
        temp1[df.close <= delay(df.close, 1)] = std(df.close, stdN)
        b = sma(temp1, smaM, 1)
        factor = a / (a + b) * 100
        factor = ts_rank_bk(factor, 30)
        factor = ts_mean(factor, 50)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor >= 0.5] = np.nan

        return factor