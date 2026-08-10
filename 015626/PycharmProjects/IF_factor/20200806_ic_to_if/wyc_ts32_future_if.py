from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts32_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        temp = df.close_if.copy()
        N = 20
        UP = temp.copy(deep=True)
        UP[df.close_if > delay(df.close_if, 1)] = std(df.close_if, N)
        UP[df.close_if <= delay(df.close_if, 1)] = 0
        factor = sma(UP, 40, 1)
        factor = ts_rank_bk(factor, 100)
        factor = ts_mean(factor, 10)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor >= 0.5] = np.nan
        
        return factor