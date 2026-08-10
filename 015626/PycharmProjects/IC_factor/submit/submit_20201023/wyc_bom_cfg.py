from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_bom_cfg(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['BidVolMean_500','BidVolMean_500']
        lookback_bars=2000
        super(wyc_bom_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = df['BidVolMean_500'] / ts_mean(df['BidVolMean_500'], 5)
        factor = factor.sum(axis=1)
        factor = ts_rank_bk(factor, 900)
        factor = ts_mean(factor, 25)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]


        return factor