from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts32_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        temp = df['close'].copy()
        N = 20
        UP = temp.copy(deep=True)
        UP[df['close'] > delay(df['close'], 1)] = std(df['close'], N)
        UP[df['close'] <= delay(df['close'], 1)] = 0
        factor = sma(UP, 10, 1)
        factor = ts_rank(factor, 2 * 242)
        factor = ts_mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        return factor