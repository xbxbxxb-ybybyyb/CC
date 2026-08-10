from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_cs_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','stk_index_corr_zz500']
        lookback_bars=2000
        super(wyc_ts419_cs_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * df['stk_index_corr_zz500']
        factor = factor.sum(axis=1).to_frame()
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 5 * 242)

        return factor

from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_cs_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'stk_index_corr_zz500', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-40:]
        low = df['low_preadj'][-40:]
        high = df['high_preadj'][-40:]
        volume = df['volume_preadj'][-40:]
        
        cs = df['stk_index_corr_zz500'][-1:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-30:]
        finaldf = np.nanmean(factor, axis = 0)

        factor = finaldf * cs.values

        factor = np.nansum(factor, axis=1)
        return factor