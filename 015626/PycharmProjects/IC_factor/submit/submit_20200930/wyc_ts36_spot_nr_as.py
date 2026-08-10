from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts36_spot_nr_as(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'

        required_columns=['high' + suffix,'low' + suffix,'volume' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts36_spot_nr_as, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        factor = ts_rank_bk(delta((df['high' + suffix] + df['low' + suffix] + df['amount' + suffix]/df['volume' + suffix]), 60), 60)

        factor = ts_rank_bk(factor, 242 * 2)
        factor = ts_mean(factor, 200)

        factor = rolling_normalize(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor