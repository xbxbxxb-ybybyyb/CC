from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_bigon_cfg(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['BuyUniqueOrderNum_500','BuyTradeNum_500']
        lookback_bars=2000
        super(wyc_bigon_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = 1 - df['BuyUniqueOrderNum_500'] / df['BuyTradeNum_500']

        factor = factor.sum(axis=1).to_frame()
        factor = ts_mean(factor, 15)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]


        return factor