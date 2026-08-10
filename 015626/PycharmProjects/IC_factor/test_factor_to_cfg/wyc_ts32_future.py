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

        temp = df['close'].copy()
        N = 20
        UP = temp.copy(deep = True)
        UP[df['close'] > delay(df['close'], 1)] = std(df['close'], N)
        UP[df['close'] <= delay(df['close'], 1)] = 0
        factor = sma(UP, N, 1)
        factor = ts_rank_bk(factor, 50)
        factor = ts_mean(factor, 50)

        return factor