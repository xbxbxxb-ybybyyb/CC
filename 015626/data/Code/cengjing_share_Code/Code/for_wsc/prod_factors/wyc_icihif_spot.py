from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_icihif_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot', 'close_spot_if', 'close_spot_ih']
        lookback_bars=2000
        super(wyc_icihif_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = df['close_spot'] - 2 * df['close_spot_ih'] + df['close_spot_if']
        factor = factor - mean(factor, 240)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor