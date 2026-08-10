from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts13_future_nr_as_50_10(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts13_future_nr_as_50_10, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        # factor[factor < 0] = 0
    
        return factor