from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class wyc_icif_if(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'close_if']
        lookback_bars=2000
        super(wyc_icif_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = df['close'] - df['close_if']
        factor = factor - mean(factor, 60)
        factor = mean(factor, 20)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = np.nan

        return factor