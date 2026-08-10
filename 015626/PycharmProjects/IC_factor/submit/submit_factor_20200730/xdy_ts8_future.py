from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts8_future(FactorGenerator):
    def __init__(self):
        required_columns=['open']
        lookback_bars=2000
        super(xdy_ts8_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        opendf = df['open']
        factor = delta(product(opendf, 14),30)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = np.nan

        return factor