from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts5_future_sc_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['volume' + suffix,'high' + suffix,'close' + suffix,'amount' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts5_future_sc_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close' + suffix], N) / N), N) / delay(df['close' + suffix], N))<=0.05,(-1 * (df['close' + suffix] - ts_min(df['close' + suffix], N))),(-1 * delta(df['close' + suffix], 3))),index=df['close' + suffix].index,columns=df['close' + suffix].columns)
        factor = ts_mean(ts_rank_bk(-1*factor, 1200),15)

        factor = factor * df['stk_index_corr' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 20)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor > 0] = 0


        return factor