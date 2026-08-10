from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class wyc_icifih_mul_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot','close_spot_if','close_spot_ih']
        lookback_bars=2000
        super(wyc_icifih_mul_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        factor = df['close_spot'] - 2 * df['close_spot_ih'] + df['close_spot_if']
        factor = factor - mean(factor, 200)
        factor = factor.to_frame()
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = np.nan
        return factor