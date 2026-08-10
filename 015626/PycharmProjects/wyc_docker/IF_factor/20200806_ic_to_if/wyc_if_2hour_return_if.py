from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_if_2hour_return_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_if_2hour_return_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        ifreturn = df.close_if / df.close_if.shift(1) - 1
        factor = mean(ifreturn, 200)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor