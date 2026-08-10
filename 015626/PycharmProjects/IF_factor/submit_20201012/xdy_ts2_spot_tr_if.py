from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts2_spot_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'low' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts2_spot_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        low = df['low' + suffix]
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).ewm(25).mean()

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor