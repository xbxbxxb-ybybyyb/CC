from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts108_future_nr_sc(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts108_future_nr_sc, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] - delay(df[key], 1) < 0, abs(df[key] - delay(df[key], 1)), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 80)

        factor = rolling_normalize(factor, 5 * 242)

        factor = factor * df['stk_index_corr' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor