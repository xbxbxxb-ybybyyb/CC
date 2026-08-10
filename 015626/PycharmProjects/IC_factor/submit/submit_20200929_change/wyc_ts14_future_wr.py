from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future_wr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'weight' + suffix]
        lookback_bars=2000
        super(wyc_ts14_future_wr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        suffix = '_zz500'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 2), std(df[key], 50), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_mean(factor, 30)

        wr = (2 * df['weight' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * wr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor