from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts202_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_ih', 'volume_ih']
        lookback_bars=2000
        super(wyc_ts202_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = ts_mean(ts_mean((sign(delta(df['volume_ih'], 5)) * (-1 * delta(df['close_ih'], 5))), 2), 10)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.88] = np.nan
        return factor