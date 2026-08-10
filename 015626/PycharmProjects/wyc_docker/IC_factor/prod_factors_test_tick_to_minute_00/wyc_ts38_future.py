from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts38_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        temp1 = df.close.copy()
        temp1[df.close > delay(df.close, 1)] = std(df.close,20)
        temp1[df.close <= delay(df.close, 1)] = 0
        a = sma(temp1, 100, 1)
        temp1[df.close > delay(df.close, 1)] = 0
        temp1[df.close <= delay(df.close, 1)] = std(df.close, 20)
        b = sma(temp1, 100, 1)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank(factor, 30)
        factor = mean(factor, 100)

        factor = factor.to_frame()

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor