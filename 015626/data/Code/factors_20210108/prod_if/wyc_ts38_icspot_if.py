from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts38_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 50
        stdN = 10
        temp1 = df['close_spot'].copy()
        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = std(df['close_spot'], stdN)
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = 0
        a = ts_truncated_ema(temp1, 5 * 242, 1/smaM)
        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = 0
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = std(df['close_spot'], stdN)
        b = ts_truncated_ema(temp1, 5 * 242, 1/smaM)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank(factor, 120)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)

        return factor