from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts32_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        temp = df.close.copy()
        N = 20
        UP = temp.copy(deep = True)
        UP[df.close > delay(df.close, 1)] = std(df.close, N)
        UP[df.close <= delay(df.close, 1)] = 0
        factor = sma(UP, N, 1)
        factor = ts_rank(factor, 50)
        factor = mean(factor, 50)

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