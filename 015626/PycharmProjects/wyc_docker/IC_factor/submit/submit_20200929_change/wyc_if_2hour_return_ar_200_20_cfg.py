from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_ar_200_20_cfg(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_ar_200_20_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        ifreturn = df['close' + suffix] / df['close' + suffix].shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis = 1).to_frame()

        factor = ts_rank_bk(factor, 200)
        factor = ts_mean(factor, 20)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]


        return factor