from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *

class wyc_ts38_future_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts38_future_ar, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['close' + suffix].copy()
        temp1[df['close' + suffix] > delay(df['close' + suffix], 1)] = std(df['close' + suffix],20)
        temp1[df['close' + suffix] <= delay(df['close' + suffix], 1)] = 0
        a = sma(temp1, 100, 1)
        temp1[df['close' + suffix] > delay(df['close' + suffix], 1)] = 0
        temp1[df['close' + suffix] <= delay(df['close' + suffix], 1)] = std(df['close' + suffix], 20)
        b = sma(temp1, 100, 1)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank_bk(factor, 30)
        factor = ts_mean(factor, 100)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 15)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor