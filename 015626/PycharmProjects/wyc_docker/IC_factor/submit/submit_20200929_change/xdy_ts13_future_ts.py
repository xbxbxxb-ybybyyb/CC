from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts13_future_ts(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix, 'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts13_future_ts, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        factor = ts_max(delta(rolling_normalize(ts_max(high,121),3*242),15),19)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 200)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]
    
        return factor